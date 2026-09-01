using BibliotecaVirtual.Application.Contracts.Seed;
using FluentValidation;

namespace BibliotecaVirtual.Application.Contracts.Seed;

/// <summary>
/// Valida cada entrada del dataset de seed para que se inserte solo si es
/// coherente con el esquema del libro (mismos límites que el catálogo).
/// </summary>
public sealed class SeedBookValidator : AbstractValidator<SeedBookDto>
{
    public SeedBookValidator()
    {
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

        RuleFor(x => x.Content)
            .MaximumLength(100000).WithMessage("El contenido no puede superar los 100000 caracteres.");

        RuleFor(x => x.OpenLibraryKey)
            .MaximumLength(64).WithMessage("La clave de Open Library no puede superar los 64 caracteres.");

        RuleFor(x => x.TotalCopies)
            .GreaterThanOrEqualTo(0).WithMessage("El total de copias no puede ser negativo.");

        RuleFor(x => x.AvailableCopies)
            .GreaterThanOrEqualTo(0).WithMessage("Las copias disponibles no pueden ser negativas.")
            .LessThanOrEqualTo(x => x.TotalCopies)
            .WithMessage("Las copias disponibles no pueden superar el total.");
    }
}
