using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Domain.Enums;

namespace BibliotecaVirtual.Application.Queries.BookRequests;

public sealed record GetBookRequestsQuery(
    int Page = 1,
    int PageSize = 20,
    BookRequestStatus? Status = null,
    string? Search = null) : BaseQuery<PagedResult<BookRequestResponse>>;
