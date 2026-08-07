using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Books;

namespace BibliotecaVirtual.Application.Queries.Books;

public sealed record GetBookByIdQuery(Guid BookId) : BaseQuery<BookResponse>;