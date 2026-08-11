using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.BookRequests;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.BookRequests;

public sealed class GetMyBookRequestsQueryHandler : IQueryHandler<GetMyBookRequestsQuery, PagedResult<BookRequestResponse>>
{
    private readonly BibliotecaDbContext _context;

    public GetMyBookRequestsQueryHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<PagedResult<BookRequestResponse>> HandleAsync(
        GetMyBookRequestsQuery query,
        CancellationToken cancellationToken = default)
    {
        var page = Math.Max(query.Page, 1);
        var pageSize = Math.Clamp(query.PageSize, 1, 100);

        var requests = _context.BookRequests
            .AsNoTracking()
            .Where(r => r.RequestedBy == query.UserId);

        if (query.Status.HasValue)
        {
            requests = requests.Where(r => r.Status == query.Status.Value);
        }

        var totalItems = await requests.CountAsync(cancellationToken);
        var totalPages = totalItems == 0 ? 0 : (int)Math.Ceiling(totalItems / (double)pageSize);

        var items = await requests
            .OrderByDescending(r => r.RequestedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Join(
                _context.Users,
                request => request.RequestedBy,
                user => user.Id,
                (request, user) => new { Request = request, UserEmail = user.Email ?? string.Empty })
            .ToListAsync(cancellationToken);

        var responseItems = items
            .Select(x => BookRequestMapper.ToResponse(x.Request, x.UserEmail))
            .ToList();

        return new PagedResult<BookRequestResponse>(page, pageSize, totalItems, totalPages, responseItems);
    }
}
