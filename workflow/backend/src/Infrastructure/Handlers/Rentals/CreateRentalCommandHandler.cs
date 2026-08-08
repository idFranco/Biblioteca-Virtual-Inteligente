using BibliotecaVirtual.Application.Commands.Rentals;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Rentals;

public sealed class CreateRentalCommandHandler : ICommandHandler<CreateRentalCommand, RentalResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<CreateRentalCommand> _validator;

    public CreateRentalCommandHandler(BibliotecaDbContext context, IValidator<CreateRentalCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<RentalResponse> HandleAsync(
        CreateRentalCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var book = await _context.Books
            .FirstOrDefaultAsync(b => b.Id == command.BookId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró el libro con id '{command.BookId}'.");

        var hasActiveDuplicate = await _context.Rentals.AnyAsync(
            r => r.BookId == command.BookId &&
                 r.UserId == command.UserId &&
                 r.Status == RentalStatus.Active,
            cancellationToken);

        if (hasActiveDuplicate)
        {
            throw new ConflictException("Ya tienes un alquiler activo de este libro.");
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