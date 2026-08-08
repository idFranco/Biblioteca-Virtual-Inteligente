using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Domain.Enums;

namespace BibliotecaVirtual.Application.Queries.Rentals;

public sealed record GetMyRentalsQuery(
    Guid UserId,
    int Page = 1,
    int PageSize = 20,
    RentalStatus? Status = null) : BaseQuery<PagedResult<RentalResponse>>;