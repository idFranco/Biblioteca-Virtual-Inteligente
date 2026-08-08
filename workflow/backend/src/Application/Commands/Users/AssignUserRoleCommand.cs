using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Users;

namespace BibliotecaVirtual.Application.Commands.Users;

public sealed record AssignUserRoleCommand(Guid UserId, string RoleName) : BaseCommand<AssignRoleResult>;