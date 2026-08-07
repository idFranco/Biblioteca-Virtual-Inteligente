using BibliotecaVirtual.Application.Commands.Auth;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Infrastructure.Data;
using BibliotecaVirtual.Infrastructure.Services;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Auth;

public sealed class RevokeCommandHandler : ICommandHandler<RevokeCommand, RevokeResult>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<RevokeCommand> _validator;

    public RevokeCommandHandler(BibliotecaDbContext context, IValidator<RevokeCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<RevokeResult> HandleAsync(RevokeCommand command, CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var tokenHash = TokenHasher.Hash(command.RefreshToken);
        var stored = await _context.RefreshTokens
            .FirstOrDefaultAsync(t => t.TokenHash == tokenHash, cancellationToken);

        if (stored is null || !stored.IsActive)
            throw new UnauthorizedAccessException("El refresh token es inválido o ya fue revocado.");

        stored.RevokedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync(cancellationToken);

        return new RevokeResult(true);
    }
}