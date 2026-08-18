namespace BibliotecaVirtual.Application.Contracts.Notifications;

public sealed record NotificationResponse(
    Guid Id,
    Guid UserId,
    Guid RentalId,
    string Message,
    DateTime DueDate,
    bool IsRead,
    DateTime CreatedAt);

public sealed record GenerateDueDateNotificationsResult(int CreatedCount);