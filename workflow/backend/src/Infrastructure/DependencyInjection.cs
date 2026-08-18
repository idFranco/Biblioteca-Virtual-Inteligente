using BibliotecaVirtual.Application.Commands.Auth;
using BibliotecaVirtual.Application.Commands.BookRequests;
using BibliotecaVirtual.Application.Commands.BookRequests.Validators;
using BibliotecaVirtual.Application.Commands.Books;
using BibliotecaVirtual.Application.Commands.Books.Validators;
using BibliotecaVirtual.Application.Commands.Notifications;
using BibliotecaVirtual.Application.Commands.Notifications.Validators;
using BibliotecaVirtual.Application.Commands.Rentals;
using BibliotecaVirtual.Application.Commands.Rentals.Validators;
using BibliotecaVirtual.Application.Commands.Users;
using BibliotecaVirtual.Application.Commands.Users.Validators;
using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Application.Contracts.Notifications;
using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Application.Contracts.Seed;
using BibliotecaVirtual.Application.Contracts.Users;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Books;
using BibliotecaVirtual.Application.Queries.BookRequests;
using BibliotecaVirtual.Application.Queries.Notifications;
using BibliotecaVirtual.Application.Queries.Rentals;
using BibliotecaVirtual.Infrastructure.Data.Seed;
using BibliotecaVirtual.Infrastructure.Handlers.Auth;
using BibliotecaVirtual.Infrastructure.Handlers.BookRequests;
using BibliotecaVirtual.Infrastructure.Handlers.Books;
using BibliotecaVirtual.Infrastructure.Handlers.Notifications;
using BibliotecaVirtual.Infrastructure.Handlers.Rentals;
using BibliotecaVirtual.Infrastructure.Handlers.Users;
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

        services.AddScoped<ICommandHandler<CreateRentalCommand, RentalResponse>, CreateRentalCommandHandler>();
        services.AddScoped<ICommandHandler<ReturnRentalCommand, RentalResponse>, ReturnRentalCommandHandler>();

        services.AddScoped<ICommandHandler<CreateBookRequestCommand, BookRequestResponse>, CreateBookRequestCommandHandler>();
        services.AddScoped<ICommandHandler<ApproveBookRequestCommand, BookRequestResponse>, ApproveBookRequestCommandHandler>();
        services.AddScoped<ICommandHandler<RejectBookRequestCommand, BookRequestResponse>, RejectBookRequestCommandHandler>();

        services.AddScoped<ICommandHandler<AssignUserRoleCommand, AssignRoleResult>, AssignUserRoleCommandHandler>();

        services.AddScoped<IQueryHandler<GetBooksQuery, PagedResult<BookResponse>>, GetBooksQueryHandler>();
        services.AddScoped<IQueryHandler<GetBookByIdQuery, BookResponse>, GetBookByIdQueryHandler>();
        services.AddScoped<IQueryHandler<GetBookForReadingQuery, BookForReadingResponse>, GetBookForReadingQueryHandler>();

        services.AddScoped<IQueryHandler<GetMyRentalsQuery, PagedResult<RentalResponse>>, GetMyRentalsQueryHandler>();
        services.AddScoped<IQueryHandler<GetRentalsQuery, PagedResult<RentalResponse>>, GetRentalsQueryHandler>();
        services.AddScoped<IQueryHandler<GetRentalByIdQuery, RentalResponse>, GetRentalByIdQueryHandler>();

        services.AddScoped<IQueryHandler<GetMyBookRequestsQuery, PagedResult<BookRequestResponse>>, GetMyBookRequestsQueryHandler>();
        services.AddScoped<IQueryHandler<GetBookRequestsQuery, PagedResult<BookRequestResponse>>, GetBookRequestsQueryHandler>();
        services.AddScoped<IQueryHandler<GetBookRequestByIdQuery, BookRequestResponse>, GetBookRequestByIdQueryHandler>();

        services.AddScoped<ICommandHandler<GenerateDueDateNotificationsCommand, GenerateDueDateNotificationsResult>, GenerateDueDateNotificationsCommandHandler>();
        services.AddScoped<ICommandHandler<MarkNotificationReadCommand, bool>, MarkNotificationReadCommandHandler>();
        services.AddScoped<IQueryHandler<GetMyNotificationsQuery, PagedResult<NotificationResponse>>, GetMyNotificationsQueryHandler>();

        services.AddScoped<IValidator<RegisterCommand>, RegisterCommandValidator>();
        services.AddScoped<IValidator<LoginCommand>, LoginCommandValidator>();
        services.AddScoped<IValidator<RefreshCommand>, RefreshCommandValidator>();
        services.AddScoped<IValidator<RevokeCommand>, RevokeCommandValidator>();

        services.AddScoped<IValidator<CreateBookCommand>, CreateBookCommandValidator>();
        services.AddScoped<IValidator<UpdateBookCommand>, UpdateBookCommandValidator>();
        services.AddScoped<IValidator<DeleteBookCommand>, DeleteBookCommandValidator>();

        services.AddScoped<IValidator<CreateRentalCommand>, CreateRentalCommandValidator>();
        services.AddScoped<IValidator<ReturnRentalCommand>, ReturnRentalCommandValidator>();

        services.AddScoped<IValidator<AssignUserRoleCommand>, AssignUserRoleCommandValidator>();

        services.AddScoped<IValidator<CreateBookRequestCommand>, CreateBookRequestCommandValidator>();
        services.AddScoped<IValidator<ApproveBookRequestCommand>, ApproveBookRequestCommandValidator>();
        services.AddScoped<IValidator<RejectBookRequestCommand>, RejectBookRequestCommandValidator>();

        services.AddScoped<IValidator<MarkNotificationReadCommand>, MarkNotificationReadCommandValidator>();

        services.AddHostedService<RentalDueNotificationService>();

        services.AddScoped<IValidator<SeedBookDto>, SeedBookValidator>();
        services.AddScoped<ICatalogSeeder, CatalogSeeder>();

        return services;
    }
}