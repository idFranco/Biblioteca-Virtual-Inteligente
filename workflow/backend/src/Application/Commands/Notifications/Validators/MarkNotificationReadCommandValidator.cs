using BibliotecaVirtual.Application.Commands.Notifications;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.Notifications.Validators;

public sealed class MarkNotificationReadCommandValidator : AbstractValidator<MarkNotificationReadCommand>
{
    public MarkNotificationReadCommandValidator()
    {
        RuleFor(x => x.NotificationId)
            .NotEmpty().WithMessage("La notificación es obligatoria.");
        RuleFor(x => x.UserId)
            .NotEmpty().WithMessage("El usuario es obligatorio.");
    }
}