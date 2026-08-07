using FluentValidation;

namespace BibliotecaVirtual.Application.Commands.Auth;

public sealed class RevokeCommandValidator : AbstractValidator<RevokeCommand>
{
    public RevokeCommandValidator()
    {
        RuleFor(x => x.RefreshToken)
            .NotEmpty().WithMessage("El refresh token es obligatorio.");
    }
}