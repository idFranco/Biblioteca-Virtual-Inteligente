using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.BookRequests;

namespace BibliotecaVirtual.Application.Queries.BookRequests;

public sealed record GetBookRequestByIdQuery(
    Guid RequestId,
    Guid RequesterUserId,
    bool CanViewAll) : BaseQuery<BookRequestResponse>;
