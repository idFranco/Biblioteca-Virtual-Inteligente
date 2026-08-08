using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Domain.Enums;

namespace BibliotecaVirtual.Infrastructure.Handlers.Rentals;

internal static class RentalMapper
{
    internal static RentalResponse ToResponse(Rental rental, string bookTitle, string userEmail) => new(
        rental.Id,
        rental.UserId,
        rental.BookId,
        bookTitle,
        userEmail,
        rental.RentedAt,
        rental.DueDate,
        rental.ReturnedAt,
        rental.Status.ToString(),
        rental.Status == RentalStatus.Active && rental.DueDate < DateTime.UtcNow);
}