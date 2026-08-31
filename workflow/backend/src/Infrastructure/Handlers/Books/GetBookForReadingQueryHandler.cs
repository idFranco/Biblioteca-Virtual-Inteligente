using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Books;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Books;

public sealed class GetBookForReadingQueryHandler : IQueryHandler<GetBookForReadingQuery, BookForReadingResponse>
{
    private readonly BibliotecaDbContext _context;

    public GetBookForReadingQueryHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<BookForReadingResponse> HandleAsync(
        GetBookForReadingQuery query,
        CancellationToken cancellationToken = default)
    {
        var entry = await _context.Rentals
            .AsNoTracking()
            .Where(r => r.BookId == query.BookId
                        && r.UserId == query.UserId
                        && r.ReturnedAt == null)
            .Join(
                _context.Books,
                rental => rental.BookId,
                book => book.Id,
                (rental, book) => new { Rental = rental, Book = book })
            .OrderByDescending(x => x.Rental.RentedAt)
            .FirstOrDefaultAsync(cancellationToken);

        if (entry is null)
        {
            throw new KeyNotFoundException($"No tienes un alquiler activo del libro con id '{query.BookId}'.");
        }

        var book = entry.Book;
        return new BookForReadingResponse(
            book.Id,
            book.Title,
            book.Author,
            book.Isbn,
            book.Genre,
            book.Description,
            book.OpenLibraryKey,
            book.TotalCopies,
            book.AvailableCopies,
            book.AvailableCopies > 0,
            book.Content,
            entry.Rental.RentedAt,
            entry.Rental.DueDate);
    }
}