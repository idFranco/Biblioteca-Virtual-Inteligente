using BibliotecaVirtual.Application.Commands.Rentals;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Rentals;

public sealed class ReturnRentalCommandHandler : ICommandHandler<ReturnRentalCommand, RentalResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<ReturnRentalCommand> _validator;

    public ReturnRentalCommandHandler(BibliotecaDbContext context, IValidator<ReturnRentalCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<RentalResponse> HandleAsync(
        ReturnRentalCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var rental = await _context.Rentals
            .FirstOrDefaultAsync(r => r.Id == command.RentalId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró el alquiler con id '{command.RentalId}'.");

        if (rental.Status == RentalStatus.Returned)
        {
            throw new ConflictException("El alquiler ya ha sido devuelto.");
        }

        var returnedAt = DateTime.UtcNow;

        await using var transaction = await _context.Database.BeginTransactionAsync(cancellationToken);

        var affected = await _context.Books
            .Where(b => b.Id == rental.BookId && b.AvailableCopies < b.TotalCopies)
            .ExecuteUpdateAsync(
                setters => setters.SetProperty(b => b.AvailableCopies, b => b.AvailableCopies + 1),
                cancellationToken);

        if (affected == 0)
        {
            await transaction.RollbackAsync(cancellationToken);
            throw new ConflictException("No se pudo liberar el stock del libro.");
        }

        rental.ReturnedAt = returnedAt;
        rental.Status = returnedAt > rental.DueDate ? RentalStatus.Overdue : RentalStatus.Returned;

        await _context.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);

        var bookTitle = await _context.Books
            .Where(b => b.Id == rental.BookId)
            .Select(b => b.Title)
            .FirstAsync(cancellationToken);

        var userEmail = await _context.Users
            .Where(u => u.Id == rental.UserId)
            .Select(u => u.Email ?? string.Empty)
            .FirstAsync(cancellationToken);

        return RentalMapper.ToResponse(rental, bookTitle, userEmail);
    }
}