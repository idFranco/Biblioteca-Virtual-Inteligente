using BibliotecaVirtual.Application.Commands.Auth;
using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;

namespace BibliotecaVirtual.WebAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[EnableRateLimiting("auth")]
public sealed class AuthController : ControllerBase
{
    private readonly IDispatcher _dispatcher;

    public AuthController(IDispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    [HttpPost("register")]
    public Task<AuthResponse> Register(RegisterRequest request, CancellationToken cancellationToken)
    {
        var command = new RegisterCommand(request.FullName, request.Email, request.Password);
        return _dispatcher.DispatchAsync<AuthResponse>(command, cancellationToken);
    }

    [HttpPost("login")]
    public Task<AuthResponse> Login(LoginRequest request, CancellationToken cancellationToken)
    {
        var command = new LoginCommand(request.Email, request.Password);
        return _dispatcher.DispatchAsync<AuthResponse>(command, cancellationToken);
    }

    [HttpPost("refresh")]
    public Task<AuthResponse> Refresh(RefreshRequest request, CancellationToken cancellationToken)
    {
        var command = new RefreshCommand(request.RefreshToken);
        return _dispatcher.DispatchAsync<AuthResponse>(command, cancellationToken);
    }

    [HttpPost("revoke")]
    public Task<RevokeResult> Revoke(RevokeRequest request, CancellationToken cancellationToken)
    {
        var command = new RevokeCommand(request.RefreshToken);
        return _dispatcher.DispatchAsync<RevokeResult>(command, cancellationToken);
    }
}