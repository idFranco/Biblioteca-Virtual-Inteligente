using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.Rentals;

namespace BibliotecaVirtual.Application.Commands.Rentals;

public sealed record ReturnRentalCommand(Guid RentalId) : BaseCommand<RentalResponse>;