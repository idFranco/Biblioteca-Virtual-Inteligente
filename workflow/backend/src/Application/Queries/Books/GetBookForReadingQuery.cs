using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Books;

namespace BibliotecaVirtual.Application.Queries.Books;

public sealed record GetBookForReadingQuery(Guid BookId, Guid UserId) : BaseQuery<BookForReadingResponse>;