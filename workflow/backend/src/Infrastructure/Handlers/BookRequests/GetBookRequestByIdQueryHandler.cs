using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.BookRequests;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.BookRequests;

public sealed class GetBookRequestByIdQueryHandler : IQueryHandler<GetBookRequestByIdQuery, BookRequestResponse>
{
    private readonly BibliotecaDbContext _context;

    public GetBookRequestByIdQueryHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<BookRequestResponse> HandleAsync(
        GetBookRequestByIdQuery query,
        CancellationToken cancellationToken = default)
    {
        var request = await _context.BookRequests
            .AsNoTracking()
            .FirstOrDefaultAsync(r => r.Id == query.RequestId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró la solicitud con id '{query.RequestId}'.");

        if (!query.CanViewAll && request.RequestedBy != query.RequesterUserId)
        {
            throw new KeyNotFoundException($"No se encontró la solicitud con id '{query.RequestId}'.");
        }

        var userEmail = await _context.Users
            .Where(u => u.Id == request.RequestedBy)
            .Select(u => u.Email ?? string.Empty)
            .FirstAsync(cancellationToken);

        return BookRequestMapper.ToResponse(request, userEmail);
    }
}
