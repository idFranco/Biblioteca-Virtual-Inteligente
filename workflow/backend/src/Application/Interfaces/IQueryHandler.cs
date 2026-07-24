using BibliotecaVirtual.Application.Common;

namespace BibliotecaVirtual.Application.Interfaces;

public interface IQueryHandler<TQuery, TResponse>
    where TQuery : BaseQuery<TResponse>
{
    Task<TResponse> HandleAsync(TQuery query, CancellationToken cancellationToken = default);
}
