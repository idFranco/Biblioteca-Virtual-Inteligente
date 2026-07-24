using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Interfaces;

namespace BibliotecaVirtual.Infrastructure.Services;

public sealed class Dispatcher : IDispatcher
{
    private readonly IServiceProvider _serviceProvider;

    public Dispatcher(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    public async Task<TResponse> DispatchAsync<TResponse>(
        BaseCommand<TResponse> command,
        CancellationToken cancellationToken = default)
    {
        var handlerType = typeof(ICommandHandler<,>)
            .MakeGenericType(command.GetType(), typeof(TResponse));

        var handler = _serviceProvider.GetService(handlerType)
            ?? throw new InvalidOperationException(
                $"No handler registered for command '{command.GetType().Name}'");

        var method = handlerType.GetMethod(nameof(ICommandHandler<BaseCommand<TResponse>, TResponse>.HandleAsync))
            ?? throw new InvalidOperationException("Handler method not found");

        var result = await (Task<TResponse>)method.Invoke(handler, [command, cancellationToken])!;
        return result;
    }

    public async Task<TResponse> DispatchAsync<TResponse>(
        BaseQuery<TResponse> query,
        CancellationToken cancellationToken = default)
    {
        var handlerType = typeof(IQueryHandler<,>)
            .MakeGenericType(query.GetType(), typeof(TResponse));

        var handler = _serviceProvider.GetService(handlerType)
            ?? throw new InvalidOperationException(
                $"No handler registered for query '{query.GetType().Name}'");

        var method = handlerType.GetMethod(nameof(IQueryHandler<BaseQuery<TResponse>, TResponse>.HandleAsync))
            ?? throw new InvalidOperationException("Handler method not found");

        var result = await (Task<TResponse>)method.Invoke(handler, [query, cancellationToken])!;
        return result;
    }
}
