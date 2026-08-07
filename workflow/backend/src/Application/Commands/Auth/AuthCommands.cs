using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Auth;

namespace BibliotecaVirtual.Application.Commands.Auth;

public sealed record RegisterCommand(
    string FullName,
    string Email,
    string Password) : BaseCommand<AuthResponse>;

public sealed record LoginCommand(
    string Email,
    string Password) : BaseCommand<AuthResponse>;

public sealed record RefreshCommand(
    string RefreshToken) : BaseCommand<AuthResponse>;

public sealed record RevokeCommand(
    string RefreshToken) : BaseCommand<RevokeResult>;

public sealed record RevokeResult(bool Revoked);