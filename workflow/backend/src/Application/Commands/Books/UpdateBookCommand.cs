using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Books;

namespace BibliotecaVirtual.Application.Commands.Books;

public sealed record UpdateBookCommand(
    Guid BookId,
    string Title,
    string Author,
    string? Isbn,
    string? Genre,
    string? Description,
    int TotalCopies,
    int AvailableCopies) : BaseCommand<BookResponse>;