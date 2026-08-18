using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.Notifications;

namespace BibliotecaVirtual.Application.Queries.Notifications;

public sealed record GetMyNotificationsQuery(
    Guid UserId,
    int Page = 1,
    int PageSize = 20,
    bool? UnreadOnly = null) : BaseQuery<PagedResult<NotificationResponse>>;