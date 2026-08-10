using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.BookRequests;

namespace BibliotecaVirtual.Application.Commands.BookRequests;

public sealed record ApproveBookRequestCommand(
    Guid RequestId,
    Guid AdminId,
    string? Title,
    string? Author,
    string? Isbn,
    string? Genre,
    string? Description,
    int TotalCopies) : BaseCommand<BookRequestResponse>;
