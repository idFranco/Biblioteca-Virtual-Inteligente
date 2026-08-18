using BibliotecaVirtual.Application.Contracts.Notifications;
using BibliotecaVirtual.Domain.Entities;

namespace BibliotecaVirtual.Infrastructure.Handlers.Notifications;

internal static class NotificationMapper
{
    internal static NotificationResponse ToResponse(Notification notification) => new(
        notification.Id,
        notification.UserId,
        notification.RentalId,
        notification.Message,
        notification.DueDate,
        notification.IsRead,
        notification.CreatedAt);
}