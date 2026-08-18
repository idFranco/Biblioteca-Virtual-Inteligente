using BibliotecaVirtual.Application.Commands.Notifications;
using BibliotecaVirtual.Application.Contracts.Notifications;
using BibliotecaVirtual.Application.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace BibliotecaVirtual.Infrastructure.Services;

public sealed class RentalDueNotificationService : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly IConfiguration _configuration;
    private readonly ILogger<RentalDueNotificationService> _logger;

    public RentalDueNotificationService(
        IServiceScopeFactory scopeFactory,
        IConfiguration configuration,
        ILogger<RentalDueNotificationService> logger)
    {
        _scopeFactory = scopeFactory;
        _configuration = configuration;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var intervalSeconds = _configuration.GetValue<int?>("Notifications:CheckIntervalSeconds") ?? 3600;
        var interval = TimeSpan.FromSeconds(Math.Max(intervalSeconds, 30));

        _logger.LogInformation("RentalDueNotificationService iniciado. Comprobación cada {Interval} segundos.", interval.TotalSeconds);

        using var timer = new PeriodicTimer(interval);

        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            await RunOnceAsync(stoppingToken);
        }
    }

    private async Task RunOnceAsync(CancellationToken stoppingToken)
    {
        try
        {
            await using var scope = _scopeFactory.CreateAsyncScope();
            var dispatcher = scope.ServiceProvider.GetRequiredService<IDispatcher>();

            var result = await dispatcher.DispatchAsync<GenerateDueDateNotificationsResult>(
                new GenerateDueDateNotificationsCommand(),
                stoppingToken);

            _logger.LogInformation("Notificaciones de vencimiento generadas: {CreatedCount}.", result.CreatedCount);
        }
        catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
        {
            _logger.LogInformation("RentalDueNotificationService cancelado.");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error al generar notificaciones de vencimiento.");
        }
    }
}