using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Books;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Books;

public sealed class GetBooksQueryHandler : IQueryHandler<GetBooksQuery, PagedResult<BookResponse>>
{
    private readonly BibliotecaDbContext _context;

    public GetBooksQueryHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<PagedResult<BookResponse>> HandleAsync(
        GetBooksQuery query,
        CancellationToken cancellationToken = default)
    {
        var page = Math.Max(query.Page, 1);
        var pageSize = Math.Clamp(query.PageSize, 1, 100);

        var books = _context.Books.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(query.Search))
        {
            var search = query.Search.Trim().ToLower();
            books = books.Where(b =>
                b.Title.ToLower().Contains(search) ||
                b.Author.ToLower().Contains(search));
        }

        if (!string.IsNullOrWhiteSpace(query.Author))
        {
            var author = query.Author.Trim().ToLower();
            books = books.Where(b => b.Author.ToLower().Contains(author));
        }

        if (!string.IsNullOrWhiteSpace(query.Genre))
        {
            var genre = query.Genre.Trim().ToLower();
            books = books.Where(b => b.Genre != null && b.Genre.ToLower().Contains(genre));
        }

        if (query.AvailableOnly == true)
        {
            books = books.Where(b => b.AvailableCopies > 0);
        }

        var totalItems = await books.CountAsync(cancellationToken);
        var totalPages = totalItems == 0 ? 0 : (int)Math.Ceiling(totalItems / (double)pageSize);

        var items = await books
            .OrderBy(b => b.Title)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(b => new BookResponse(
                b.Id,
                b.Title,
                b.Author,
                b.Isbn,
                b.Genre,
                b.Description,
                b.TotalCopies,
                b.AvailableCopies,
                b.AvailableCopies > 0))
            .ToListAsync(cancellationToken);

        return new PagedResult<BookResponse>(page, pageSize, totalItems, totalPages, items);
    }
}