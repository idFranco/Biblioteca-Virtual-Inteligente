using BibliotecaVirtual.Application.Commands.Users;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Users;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using FluentValidation;
using Microsoft.AspNetCore.Identity;

namespace BibliotecaVirtual.Infrastructure.Handlers.Users;

public sealed class AssignUserRoleCommandHandler : ICommandHandler<AssignUserRoleCommand, AssignRoleResult>
{
    private readonly UserManager<User> _userManager;
    private readonly RoleManager<Role> _roleManager;
    private readonly IValidator<AssignUserRoleCommand> _validator;

    public AssignUserRoleCommandHandler(
        UserManager<User> userManager,
        RoleManager<Role> roleManager,
        IValidator<AssignUserRoleCommand> validator)
    {
        _userManager = userManager;
        _roleManager = roleManager;
        _validator = validator;
    }

    public async Task<AssignRoleResult> HandleAsync(
        AssignUserRoleCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var user = await _userManager.FindByIdAsync(command.UserId.ToString());
        if (user is null)
        {
            throw new KeyNotFoundException($"No se encontró el usuario con id '{command.UserId}'.");
        }

        if (!await _roleManager.RoleExistsAsync(command.RoleName))
        {
            throw new KeyNotFoundException($"No se encontró el rol '{command.RoleName}'.");
        }

        var currentRoles = await _userManager.GetRolesAsync(user);
        if (currentRoles.Contains(command.RoleName, StringComparer.Ordinal))
        {
            throw new ConflictException($"El usuario ya tiene asignado el rol '{command.RoleName}'.");
        }

        var removeResult = await _userManager.RemoveFromRolesAsync(user, currentRoles);
        if (!removeResult.Succeeded)
        {
            throw new InvalidOperationException(
                $"No se pudieron remover los roles actuales: {string.Join("; ", removeResult.Errors.Select(e => e.Description))}");
        }

        var addResult = await _userManager.AddToRoleAsync(user, command.RoleName);
        if (!addResult.Succeeded)
        {
            throw new InvalidOperationException(
                $"No se pudo asignar el rol '{command.RoleName}': {string.Join("; ", addResult.Errors.Select(e => e.Description))}");
        }

        return new AssignRoleResult(command.UserId, command.RoleName);
    }
}