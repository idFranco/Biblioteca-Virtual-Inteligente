using BibliotecaVirtual.Application.Commands.BookRequests;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.BookRequests.Validators;

public sealed class RejectBookRequestCommandValidator : AbstractValidator<RejectBookRequestCommand>
{
    public RejectBookRequestCommandValidator()
    {
        RuleFor(x => x.RequestId)
            .NotEmpty().WithMessage("El identificador de la solicitud es obligatorio.");

        RuleFor(x => x.AdminId)
            .NotEmpty().WithMessage("El identificador del administrador es obligatorio.");

        RuleFor(x => x.AdminNotes)
            .NotEmpty().WithMessage("La nota del administrador es obligatoria.")
            .MaximumLength(500).WithMessage("La nota del administrador no puede superar los 500 caracteres.");
    }
}
