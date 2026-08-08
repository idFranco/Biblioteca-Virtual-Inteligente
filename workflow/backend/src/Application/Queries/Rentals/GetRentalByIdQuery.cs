using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Rentals;

namespace BibliotecaVirtual.Application.Queries.Rentals;

public sealed record GetRentalByIdQuery(
    Guid RentalId,
    Guid RequesterUserId,
    bool CanViewAll) : BaseQuery<RentalResponse>;