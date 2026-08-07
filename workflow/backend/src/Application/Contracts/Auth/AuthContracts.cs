namespace BibliotecaVirtual.Application.Contracts.Auth;

public sealed record RegisterRequest(string FullName, string Email, string Password);

public sealed record LoginRequest(string Email, string Password);

public sealed record RefreshRequest(string RefreshToken);

public sealed record RevokeRequest(string RefreshToken);

public sealed record AuthUserResponse(Guid Id, string FullName, string Email, IReadOnlyList<string> Roles, IReadOnlyList<string> Permissions);

public sealed record AuthResponse(string AccessToken, DateTime AccessTokenExpiresAt, string RefreshToken, AuthUserResponse User);