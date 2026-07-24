namespace BibliotecaVirtual.Application.Common;

public abstract record BaseQuery<TResponse>
{
    public Guid CorrelationId { get; init; } = Guid.NewGuid();
}
