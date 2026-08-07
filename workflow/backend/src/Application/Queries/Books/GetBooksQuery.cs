using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Books;

namespace BibliotecaVirtual.Application.Queries.Books;

public sealed record GetBooksQuery(
    int Page = 1,
    int PageSize = 20,
    string? Search = null,
    string? Author = null,
    string? Genre = null,
    bool? AvailableOnly = null) : BaseQuery<PagedResult<BookResponse>>;