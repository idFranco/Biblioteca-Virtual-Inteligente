using BibliotecaVirtual.Application.Commands.Books;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.Books.Validators;

public sealed class DeleteBookCommandValidator : AbstractValidator<DeleteBookCommand>
{
    public DeleteBookCommandValidator()
    {
        RuleFor(x => x.BookId)
            .NotEmpty().WithMessage("El identificador del libro es obligatorio.");
    }
}