using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Rentals;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Rentals;

public sealed class GetRentalsQueryHandler : IQueryHandler<GetRentalsQuery, PagedResult<RentalResponse>>
{
    private readonly BibliotecaDbContext _context;

    public GetRentalsQueryHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<PagedResult<RentalResponse>> HandleAsync(
        GetRentalsQuery query,
        CancellationToken cancellationToken = default)
    {
        var page = Math.Max(query.Page, 1);
        var pageSize = Math.Clamp(query.PageSize, 1, 100);

        var rentals = _context.Rentals.AsNoTracking();

        if (query.UserId.HasValue)
        {
            rentals = rentals.Where(r => r.UserId == query.UserId.Value);
        }

        if (query.Status.HasValue)
        {
            rentals = rentals.Where(r => r.Status == query.Status.Value);
        }

        var totalItems = await rentals.CountAsync(cancellationToken);
        var totalPages = totalItems == 0 ? 0 : (int)Math.Ceiling(totalItems / (double)pageSize);

        var items = await rentals
            .OrderByDescending(r => r.RentedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Join(
                _context.Books,
                rental => rental.BookId,
                book => book.Id,
                (rental, book) => new { Rental = rental, BookTitle = book.Title })
            .Join(
                _context.Users,
                entry => entry.Rental.UserId,
                user => user.Id,
                (entry, user) => new { entry.Rental, entry.BookTitle, UserEmail = user.Email ?? string.Empty })
            .ToListAsync(cancellationToken);

        var responseItems = items
            .Select(entry => RentalMapper.ToResponse(entry.Rental, entry.BookTitle, entry.UserEmail))
            .ToList();

        return new PagedResult<RentalResponse>(page, pageSize, totalItems, totalPages, responseItems);
    }
}