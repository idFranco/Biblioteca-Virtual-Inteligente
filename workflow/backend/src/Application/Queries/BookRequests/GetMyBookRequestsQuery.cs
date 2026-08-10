using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Domain.Enums;

namespace BibliotecaVirtual.Application.Queries.BookRequests;

public sealed record GetMyBookRequestsQuery(
    Guid UserId,
    int Page = 1,
    int PageSize = 20,
    BookRequestStatus? Status = null) : BaseQuery<PagedResult<BookRequestResponse>>;
