using System.Text.RegularExpressions;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.Auth;

public sealed partial class RegisterCommandValidator : AbstractValidator<RegisterCommand>
{
    public RegisterCommandValidator()
    {
        RuleFor(x => x.FullName)
            .NotEmpty().WithMessage("El nombre es obligatorio.")
            .MaximumLength(150).WithMessage("El nombre no puede superar 150 caracteres.");

        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("El email es obligatorio.")
            .MaximumLength(256).WithMessage("El email no puede superar 256 caracteres.")
            .EmailAddress().WithMessage("El email no es válido.");

        RuleFor(x => x.Password)
            .NotEmpty().WithMessage("La contraseña es obligatoria.")
            .MinimumLength(8).WithMessage("La contraseña debe tener al menos 8 caracteres.")
            .MaximumLength(128).WithMessage("La contraseña no puede superar 128 caracteres.")
            .Must(HasDigit).WithMessage("La contraseña debe contener al menos un dígito.")
            .Must(HasUpper).WithMessage("La contraseña debe contener al menos una mayúscula.")
            .Must(HasSymbolOrLower).WithMessage("La contraseña debe contener una minúscula o un símbolo.");
    }

    private static bool HasDigit(string value) => value.Any(char.IsDigit);

    private static bool HasUpper(string value) => value.Any(char.IsUpper);

    private static bool HasSymbolOrLower(string value) =>
        value.Any(char.IsLower) || SymbolRegex().IsMatch(value);

    [GeneratedRegex(@"[^a-zA-Z0-9]")]
    private static partial Regex SymbolRegex();
}