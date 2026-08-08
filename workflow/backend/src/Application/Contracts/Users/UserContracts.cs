namespace BibliotecaVirtual.Application.Contracts.Users;

public sealed record AssignRoleResult(Guid UserId, string RoleName);

public sealed record AssignRoleRequest(string RoleName);