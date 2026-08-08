using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Rentals;

namespace BibliotecaVirtual.Application.Commands.Rentals;

public sealed record CreateRentalCommand(
    Guid UserId,
    Guid BookId,
    DateTime? DueDate) : BaseCommand<RentalResponse>;