namespace BibliotecaVirtual.Application.Contracts.Rentals;

public sealed record RentalResponse(
    Guid Id,
    Guid UserId,
    Guid BookId,
    string BookTitle,
    string UserEmail,
    DateTime RentedAt,
    DateTime DueDate,
    DateTime? ReturnedAt,
    string Status,
    bool IsOverdue);

public sealed record CreateRentalRequest(
    Guid BookId,
    DateTime? DueDate);