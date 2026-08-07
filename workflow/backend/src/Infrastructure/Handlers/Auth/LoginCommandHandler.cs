using BibliotecaVirtual.Application.Commands.Auth;
using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using FluentValidation;
using Microsoft.AspNetCore.Identity;

namespace BibliotecaVirtual.Infrastructure.Handlers.Auth;

public sealed class LoginCommandHandler : ICommandHandler<LoginCommand, AuthResponse>
{
    private readonly UserManager<User> _userManager;
    private readonly ITokenService _tokenService;
    private readonly IValidator<LoginCommand> _validator;

    public LoginCommandHandler(
        UserManager<User> userManager,
        ITokenService tokenService,
        IValidator<LoginCommand> validator)
    {
        _userManager = userManager;
        _tokenService = tokenService;
        _validator = validator;
    }

    public async Task<AuthResponse> HandleAsync(LoginCommand command, CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var user = await _userManager.FindByEmailAsync(command.Email);
        if (user is null || !user.IsActive)
            throw new UnauthorizedAccessException("Credenciales inválidas.");

        var passwordValid = await _userManager.CheckPasswordAsync(user, command.Password);
        if (!passwordValid)
            throw new UnauthorizedAccessException("Credenciales inválidas.");

        return await _tokenService.CreateAuthResponseAsync(user, cancellationToken);
    }
}