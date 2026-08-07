using BibliotecaVirtual.Application.Commands.Auth;
using BibliotecaVirtual.Application.Commands.Books;
using BibliotecaVirtual.Application.Commands.Books.Validators;
using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Books;
using BibliotecaVirtual.Infrastructure.Handlers.Auth;
using BibliotecaVirtual.Infrastructure.Handlers.Books;
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

        services.AddScoped<ICommandHandler<CreateBookCommand, BookResponse>, CreateBookCommandHandler>();
        services.AddScoped<ICommandHandler<UpdateBookCommand, BookResponse>, UpdateBookCommandHandler>();
        services.AddScoped<ICommandHandler<DeleteBookCommand, DeleteBookResult>, DeleteBookCommandHandler>();

        services.AddScoped<IQueryHandler<GetBooksQuery, PagedResult<BookResponse>>, GetBooksQueryHandler>();
        services.AddScoped<IQueryHandler<GetBookByIdQuery, BookResponse>, GetBookByIdQueryHandler>();

        services.AddScoped<IValidator<RegisterCommand>, RegisterCommandValidator>();
        services.AddScoped<IValidator<LoginCommand>, LoginCommandValidator>();
        services.AddScoped<IValidator<RefreshCommand>, RefreshCommandValidator>();
        services.AddScoped<IValidator<RevokeCommand>, RevokeCommandValidator>();

        services.AddScoped<IValidator<CreateBookCommand>, CreateBookCommandValidator>();
        services.AddScoped<IValidator<UpdateBookCommand>, UpdateBookCommandValidator>();
        services.AddScoped<IValidator<DeleteBookCommand>, DeleteBookCommandValidator>();

        return services;
    }
}