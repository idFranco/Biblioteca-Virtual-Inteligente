using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Domain.Entities;

namespace BibliotecaVirtual.Infrastructure.Handlers.Books;

internal static class BookMapper
{
    internal static BookResponse ToResponse(Book book) => new(
        book.Id,
        book.Title,
        book.Author,
        book.Isbn,
        book.Genre,
        book.Description,
        book.TotalCopies,
        book.AvailableCopies,
        book.AvailableCopies > 0);
}