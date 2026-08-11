using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.BookRequests;

namespace BibliotecaVirtual.Application.Commands.BookRequests;

public sealed record CreateBookRequestCommand(
    Guid UserId,
    string Title,
    string Author,
    string? Isbn,
    string? Genre,
    string? Description,
    string? OpenLibraryKey) : BaseCommand<BookRequestResponse>;
