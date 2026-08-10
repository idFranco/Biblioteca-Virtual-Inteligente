using BibliotecaVirtual.Application.Commands.BookRequests;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.BookRequests.Validators;

public sealed class CreateBookRequestCommandValidator : AbstractValidator<CreateBookRequestCommand>
{
    public CreateBookRequestCommandValidator()
    {
        RuleFor(x => x.UserId)
            .NotEmpty().WithMessage("El identificador del usuario es obligatorio.");

        RuleFor(x => x.Title)
            .NotEmpty().WithMessage("El título es obligatorio.")
            .MaximumLength(255).WithMessage("El título no puede superar los 255 caracteres.");

        RuleFor(x => x.Author)
            .NotEmpty().WithMessage("El autor es obligatorio.")
            .MaximumLength(255).WithMessage("El autor no puede superar los 255 caracteres.");

        RuleFor(x => x.Isbn)
            .MaximumLength(20).WithMessage("El ISBN no puede superar los 20 caracteres.");

        RuleFor(x => x.Genre)
            .MaximumLength(100).WithMessage("El género no puede superar los 100 caracteres.");

        RuleFor(x => x.Description)
            .MaximumLength(2000).WithMessage("La descripción no puede superar los 2000 caracteres.");

        RuleFor(x => x.OpenLibraryKey)
            .MaximumLength(64).WithMessage("La clave de Open Library no puede superar los 64 caracteres.");
    }
}
