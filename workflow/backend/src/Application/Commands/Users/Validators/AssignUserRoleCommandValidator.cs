using BibliotecaVirtual.Application.Commands.Users;
using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.Users.Validators;

public sealed class AssignUserRoleCommandValidator : AbstractValidator<AssignUserRoleCommand>
{
    private static readonly string[] AllowedRoles = ["Admin", "Bibliotecario", "Usuario"];

    public AssignUserRoleCommandValidator()
    {
        RuleFor(x => x.UserId)
            .NotEmpty().WithMessage("El usuario es obligatorio.");

        RuleFor(x => x.RoleName)
            .NotEmpty().WithMessage("El rol es obligatorio.")
            .Must(role => AllowedRoles.Contains(role))
            .WithMessage("El rol debe ser uno de: Admin, Bibliotecario, Usuario.");
    }
}