using BibliotecaVirtual.Application.Commands.Auth;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using FluentValidation;
using Microsoft.AspNetCore.Identity;

namespace BibliotecaVirtual.Infrastructure.Handlers.Auth;

public sealed class RegisterCommandHandler : ICommandHandler<RegisterCommand, AuthResponse>
{
    private readonly UserManager<User> _userManager;
    private readonly ITokenService _tokenService;
    private readonly IValidator<RegisterCommand> _validator;

    public RegisterCommandHandler(
        UserManager<User> userManager,
        ITokenService tokenService,
        IValidator<RegisterCommand> validator)
    {
        _userManager = userManager;
        _tokenService = tokenService;
        _validator = validator;
    }

    public async Task<AuthResponse> HandleAsync(RegisterCommand command, CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var existing = await _userManager.FindByEmailAsync(command.Email);
        if (existing is not null)
            throw new ResourceAlreadyExistsException($"Ya existe un usuario con el email '{command.Email}'.");

        var user = new User
        {
            UserName = command.Email,
            Email = command.Email,
            FullName = command.FullName,
            IsActive = true
        };

        var result = await _userManager.CreateAsync(user, command.Password);
        if (!result.Succeeded)
            throw new InvalidOperationException(FormatErrors(result));

        var roleResult = await _userManager.AddToRoleAsync(user, "Usuario");
        if (!roleResult.Succeeded)
            throw new InvalidOperationException("No se pudo asignar el rol 'Usuario'.");

        return await _tokenService.CreateAuthResponseAsync(user, cancellationToken);
    }

    private static string FormatErrors(IdentityResult result) =>
        string.Join(" ", result.Errors.Select(e => e.Description));
}