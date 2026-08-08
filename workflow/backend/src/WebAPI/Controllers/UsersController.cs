using BibliotecaVirtual.Application.Commands.Users;
using BibliotecaVirtual.Application.Contracts.Users;
using BibliotecaVirtual.Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BibliotecaVirtual.WebAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public sealed class UsersController : ControllerBase
{
    private readonly IDispatcher _dispatcher;

    public UsersController(IDispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    [HttpPut("{userId:guid}/role")]
    [Authorize(Policy = "roles.manage")]
    public Task<AssignRoleResult> AssignRole(Guid userId, AssignRoleRequest request, CancellationToken cancellationToken)
    {
        return _dispatcher.DispatchAsync<AssignRoleResult>(
            new AssignUserRoleCommand(userId, request.RoleName),
            cancellationToken);
    }
}