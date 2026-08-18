using BibliotecaVirtual.Application.Commands.Notifications;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Notifications;

public sealed class MarkNotificationReadCommandHandler : ICommandHandler<MarkNotificationReadCommand, bool>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<MarkNotificationReadCommand> _validator;

    public MarkNotificationReadCommandHandler(BibliotecaDbContext context, IValidator<MarkNotificationReadCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<bool> HandleAsync(
        MarkNotificationReadCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var notification = await _context.Notifications
            .FirstOrDefaultAsync(n => n.Id == command.NotificationId, cancellationToken);

        if (notification is null || notification.UserId != command.UserId)
        {
            return false;
        }

        if (notification.IsRead)
        {
            return true;
        }

        notification.IsRead = true;
        await _context.SaveChangesAsync(cancellationToken);

        return true;
    }
}