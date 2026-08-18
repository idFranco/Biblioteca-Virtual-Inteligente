using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Notifications;

namespace BibliotecaVirtual.Application.Commands.Notifications;

public sealed record GenerateDueDateNotificationsCommand : BaseCommand<GenerateDueDateNotificationsResult>;