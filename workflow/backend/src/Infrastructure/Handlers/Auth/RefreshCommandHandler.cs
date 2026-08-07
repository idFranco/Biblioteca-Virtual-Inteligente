using BibliotecaVirtual.Application.Commands.Auth;
using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Infrastructure.Data;
using BibliotecaVirtual.Infrastructure.Services;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Auth;

public sealed class RefreshCommandHandler : ICommandHandler<RefreshCommand, AuthResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly ITokenService _tokenService;
    private readonly IValidator<RefreshCommand> _validator;

    public RefreshCommandHandler(
        BibliotecaDbContext context,
        ITokenService tokenService,
        IValidator<RefreshCommand> validator)
    {
        _context = context;
        _tokenService = tokenService;
        _validator = validator;
    }

    public async Task<AuthResponse> HandleAsync(RefreshCommand command, CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var tokenHash = TokenHasher.Hash(command.RefreshToken);
        var stored = await _context.RefreshTokens
            .Include(t => t.User)
            .FirstOrDefaultAsync(t => t.TokenHash == tokenHash, cancellationToken);

        if (stored is null || !stored.IsActive)
            throw new UnauthorizedAccessException("El refresh token es inválido o ha expirado.");

        stored.RevokedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync(cancellationToken);

        return await _tokenService.CreateAuthResponseAsync(stored.User!, cancellationToken);
    }
}