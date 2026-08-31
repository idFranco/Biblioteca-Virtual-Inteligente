using BibliotecaVirtual.Application.Commands.Rentals;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.Rentals.Validators;

public sealed class ReturnRentalCommandValidator : AbstractValidator<ReturnRentalCommand>
{
    public ReturnRentalCommandValidator()
    {
        RuleFor(x => x.RentalId)
            .NotEmpty().WithMessage("El alquiler es obligatorio.");

        RuleFor(x => x.RequesterUserId)
            .NotEmpty().WithMessage("El usuario que solicita la devolución es obligatorio.");
    }
}