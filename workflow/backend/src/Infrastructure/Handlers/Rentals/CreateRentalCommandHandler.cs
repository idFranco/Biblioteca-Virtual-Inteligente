using BibliotecaVirtual.Application.Commands.Rentals;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Common;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;

namespace BibliotecaVirtual.Infrastructure.Handlers.Rentals;

public sealed class CreateRentalCommandHandler : ICommandHandler<CreateRentalCommand, RentalResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<CreateRentalCommand> _validator;
    private readonly IConfiguration _configuration;

    public CreateRentalCommandHandler(
        BibliotecaDbContext context,
        IValidator<CreateRentalCommand> validator,
        IConfiguration configuration)
    {
        _context = context;
        _validator = validator;
        _configuration = configuration;
    }

    public async Task<RentalResponse> HandleAsync(
        CreateRentalCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var book = await _context.Books
            .FirstOrDefaultAsync(b => b.Id == command.BookId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró el libro con id '{command.BookId}'.");

        var normalizedTitle = book.Title.ToLower();

        var hasActiveDuplicateTitle = await (
            from activeRental in _context.Rentals
            join candidate in _context.Books on activeRental.BookId equals candidate.Id
            where activeRental.UserId == command.UserId
                  && activeRental.Status == RentalStatus.Active
                  && candidate.Title.ToLower() == normalizedTitle
            select activeRental.Id)
            .AnyAsync(cancellationToken);

        if (hasActiveDuplicateTitle)
        {
            throw new ConflictException("Ya tienes un alquiler activo de este libro.");
        }

        var maxActivePerUser = _configuration.GetInt("Rentals:MaxActivePerUser", 5);

        var activeCount = await _context.Rentals.CountAsync(
            r => r.UserId == command.UserId && r.Status == RentalStatus.Active,
            cancellationToken);

        if (activeCount >= maxActivePerUser)
        {
            throw new ConflictException($"Has alcanzado el máximo de {maxActivePerUser} alquileres activos.");
        }

        var dueDate = command.DueDate ?? DateTime.UtcNow.AddDays(14);

        await using var transaction = await _context.Database.BeginTransactionAsync(cancellationToken);

        var affected = await _context.Books
            .Where(b => b.Id == command.BookId && b.AvailableCopies > 0)
            .ExecuteUpdateAsync(
                setters => setters.SetProperty(b => b.AvailableCopies, b => b.AvailableCopies - 1),
                cancellationToken);

        if (affected == 0)
        {
            await transaction.RollbackAsync(cancellationToken);
            throw new ConflictException("No hay copias disponibles de este libro.");
        }

        var rental = new Rental
        {
            UserId = command.UserId,
            BookId = command.BookId,
            RentedAt = DateTime.UtcNow,
            DueDate = dueDate,
            Status = RentalStatus.Active
        };

        _context.Rentals.Add(rental);
        await _context.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);

        var userEmail = await _context.Users
            .Where(u => u.Id == command.UserId)
            .Select(u => u.Email ?? string.Empty)
            .FirstAsync(cancellationToken);

        return RentalMapper.ToResponse(rental, book.Title, userEmail);
    }
}