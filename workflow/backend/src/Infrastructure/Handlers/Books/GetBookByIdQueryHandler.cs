using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Books;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Books;

public sealed class GetBookByIdQueryHandler : IQueryHandler<GetBookByIdQuery, BookResponse>
{
    private readonly BibliotecaDbContext _context;

    public GetBookByIdQueryHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<BookResponse> HandleAsync(
        GetBookByIdQuery query,
        CancellationToken cancellationToken = default)
    {
        var book = await _context.Books
            .AsNoTracking()
            .FirstOrDefaultAsync(b => b.Id == query.BookId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró el libro con id '{query.BookId}'.");

        return BookMapper.ToResponse(book);
    }
}