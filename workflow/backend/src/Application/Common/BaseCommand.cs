namespace BibliotecaVirtual.Application.Common;

public abstract record BaseCommand<TResponse>
{
    public Guid CorrelationId { get; init; } = Guid.NewGuid();
}
