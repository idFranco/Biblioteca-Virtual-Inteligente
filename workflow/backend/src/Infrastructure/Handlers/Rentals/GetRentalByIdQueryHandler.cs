using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Rentals;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Rentals;

public sealed class GetRentalByIdQueryHandler : IQueryHandler<GetRentalByIdQuery, RentalResponse>
{
    private readonly BibliotecaDbContext _context;

    public GetRentalByIdQueryHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<RentalResponse> HandleAsync(
        GetRentalByIdQuery query,
        CancellationToken cancellationToken = default)
    {
        var rental = await _context.Rentals
            .AsNoTracking()
            .FirstOrDefaultAsync(r => r.Id == query.RentalId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró el alquiler con id '{query.RentalId}'.");

        if (!query.CanViewAll && rental.UserId != query.RequesterUserId)
        {
            throw new KeyNotFoundException($"No se encontró el alquiler con id '{query.RentalId}'.");
        }

        var bookTitle = await _context.Books
            .Where(b => b.Id == rental.BookId)
            .Select(b => b.Title)
            .FirstAsync(cancellationToken);

        var userEmail = await _context.Users
            .Where(u => u.Id == rental.UserId)
            .Select(u => u.Email ?? string.Empty)
            .FirstAsync(cancellationToken);

        return RentalMapper.ToResponse(rental, bookTitle, userEmail);
    }
}