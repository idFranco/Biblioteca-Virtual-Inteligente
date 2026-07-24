using BibliotecaVirtual.Application.Common;

namespace BibliotecaVirtual.Application.Interfaces;

public interface ICommandHandler<TCommand, TResponse>
    where TCommand : BaseCommand<TResponse>
{
    Task<TResponse> HandleAsync(TCommand command, CancellationToken cancellationToken = default);
}
