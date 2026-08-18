using BibliotecaVirtual.Application.Common;

namespace BibliotecaVirtual.Application.Commands.Notifications;

public sealed record MarkNotificationReadCommand(Guid NotificationId, Guid UserId) : BaseCommand<bool>;