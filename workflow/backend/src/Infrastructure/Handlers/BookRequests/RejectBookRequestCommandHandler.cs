using BibliotecaVirtual.Application.Commands.BookRequests;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.BookRequests;

public sealed class RejectBookRequestCommandHandler : ICommandHandler<RejectBookRequestCommand, BookRequestResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<RejectBookRequestCommand> _validator;

    public RejectBookRequestCommandHandler(BibliotecaDbContext context, IValidator<RejectBookRequestCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<BookRequestResponse> HandleAsync(
        RejectBookRequestCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var request = await _context.BookRequests
            .FirstOrDefaultAsync(r => r.Id == command.RequestId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró la solicitud con id '{command.RequestId}'.");

        if (request.Status != BookRequestStatus.Pending)
        {
            throw new ConflictException("La solicitud ya fue resuelta.");
        }

        request.Status = BookRequestStatus.Rejected;
        request.AdminNotes = command.AdminNotes.Trim();
        request.ResolvedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync(cancellationToken);

        var userEmail = await _context.Users
            .Where(u => u.Id == request.RequestedBy)
            .Select(u => u.Email ?? string.Empty)
            .FirstOrDefaultAsync(cancellationToken) ?? string.Empty;

        return BookRequestMapper.ToResponse(request, userEmail);
    }
}
