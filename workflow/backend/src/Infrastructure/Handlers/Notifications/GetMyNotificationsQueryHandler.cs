using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.Notifications;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Notifications;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Notifications;

public sealed class GetMyNotificationsQueryHandler : IQueryHandler<GetMyNotificationsQuery, PagedResult<NotificationResponse>>
{
    private readonly BibliotecaDbContext _context;

    public GetMyNotificationsQueryHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<PagedResult<NotificationResponse>> HandleAsync(
        GetMyNotificationsQuery query,
        CancellationToken cancellationToken = default)
    {
        var page = Math.Max(query.Page, 1);
        var pageSize = Math.Clamp(query.PageSize, 1, 100);

        var notifications = _context.Notifications
            .AsNoTracking()
            .Where(n => n.UserId == query.UserId);

        if (query.UnreadOnly == true)
        {
            notifications = notifications.Where(n => !n.IsRead);
        }

        var totalItems = await notifications.CountAsync(cancellationToken);
        var totalPages = totalItems == 0 ? 0 : (int)Math.Ceiling(totalItems / (double)pageSize);

        var items = await notifications
            .OrderByDescending(n => n.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(n => NotificationMapper.ToResponse(n))
            .ToListAsync(cancellationToken);

        return new PagedResult<NotificationResponse>(page, pageSize, totalItems, totalPages, items);
    }
}