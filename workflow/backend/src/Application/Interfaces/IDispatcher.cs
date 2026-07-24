using BibliotecaVirtual.Application.Common;

namespace BibliotecaVirtual.Application.Interfaces;

public interface IDispatcher
{
    Task<TResponse> DispatchAsync<TResponse>(
        BaseCommand<TResponse> command,
        CancellationToken cancellationToken = default);

    Task<TResponse> DispatchAsync<TResponse>(
        BaseQuery<TResponse> query,
        CancellationToken cancellationToken = default);
}
