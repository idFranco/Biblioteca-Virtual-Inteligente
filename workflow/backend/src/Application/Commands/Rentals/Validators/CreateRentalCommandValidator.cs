using BibliotecaVirtual.Application.Commands.Rentals;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.Rentals.Validators;

public sealed class CreateRentalCommandValidator : AbstractValidator<CreateRentalCommand>
{
    public CreateRentalCommandValidator()
    {
        RuleFor(x => x.UserId)
            .NotEmpty().WithMessage("El usuario es obligatorio.");

        RuleFor(x => x.BookId)
            .NotEmpty().WithMessage("El libro es obligatorio.");

        When(x => x.DueDate.HasValue, () =>
        {
            RuleFor(x => x.DueDate!.Value)
                .GreaterThanOrEqualTo(DateTime.UtcNow.Date)
                .WithMessage("La fecha límite no puede ser anterior a hoy.");

            RuleFor(x => x.DueDate!.Value)
                .LessThanOrEqualTo(DateTime.UtcNow.Date.AddDays(30))
                .WithMessage("La fecha límite no puede superar los 30 días.");
        });
    }
}