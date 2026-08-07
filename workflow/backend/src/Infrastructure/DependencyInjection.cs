using BibliotecaVirtual.Application.Commands.Auth;
using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Infrastructure.Handlers.Auth;
using BibliotecaVirtual.Infrastructure.Services;
using FluentValidation;
using Microsoft.Extensions.DependencyInjection;

namespace BibliotecaVirtual.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services)
    {
        services.AddScoped<ITokenService, TokenService>();
        services.AddScoped<IDispatcher, Dispatcher>();

        services.AddScoped<ICommandHandler<RegisterCommand, AuthResponse>, RegisterCommandHandler>();
        services.AddScoped<ICommandHandler<LoginCommand, AuthResponse>, LoginCommandHandler>();
        services.AddScoped<ICommandHandler<RefreshCommand, AuthResponse>, RefreshCommandHandler>();
        services.AddScoped<ICommandHandler<RevokeCommand, RevokeResult>, RevokeCommandHandler>();

        services.AddScoped<IValidator<RegisterCommand>, RegisterCommandValidator>();
        services.AddScoped<IValidator<LoginCommand>, LoginCommandValidator>();
        services.AddScoped<IValidator<RefreshCommand>, RefreshCommandValidator>();
        services.AddScoped<IValidator<RevokeCommand>, RevokeCommandValidator>();

        return services;
    }
}