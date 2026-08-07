using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Domain.Entities;

namespace BibliotecaVirtual.Application.Interfaces;

public interface ITokenService
{
    Task<AuthResponse> CreateAuthResponseAsync(User user, CancellationToken cancellationToken = default);
}