using BibliotecaVirtual.Application.Commands.BookRequests;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.BookRequests.Validators;

public sealed class ApproveBookRequestCommandValidator : AbstractValidator<ApproveBookRequestCommand>
{
    public ApproveBookRequestCommandValidator()
    {
        RuleFor(x => x.RequestId)
            .NotEmpty().WithMessage("El identificador de la solicitud es obligatorio.");

        RuleFor(x => x.AdminId)
            .NotEmpty().WithMessage("El identificador del administrador es obligatorio.");

        RuleFor(x => x.Title)
            .MaximumLength(255).WithMessage("El título no puede superar los 255 caracteres.");

        RuleFor(x => x.Author)
            .MaximumLength(255).WithMessage("El autor no puede superar los 255 caracteres.");

        RuleFor(x => x.Isbn)
            .MaximumLength(20).WithMessage("El ISBN no puede superar los 20 caracteres.");

        RuleFor(x => x.Genre)
            .MaximumLength(100).WithMessage("El género no puede superar los 100 caracteres.");

        RuleFor(x => x.Description)
            .MaximumLength(2000).WithMessage("La descripción no puede superar los 2000 caracteres.");

        RuleFor(x => x.TotalCopies)
            .GreaterThanOrEqualTo(1).WithMessage("El total de copias debe ser al menos 1.");
    }
}
