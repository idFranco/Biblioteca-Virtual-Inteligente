using BibliotecaVirtual.Application.Commands.BookRequests;
using BibliotecaVirtual.Application.Commands.Books;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.BookRequests;

public sealed class ApproveBookRequestCommandHandler : ICommandHandler<ApproveBookRequestCommand, BookRequestResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<ApproveBookRequestCommand> _validator;
    private readonly IDispatcher _dispatcher;

    public ApproveBookRequestCommandHandler(
        BibliotecaDbContext context,
        IValidator<ApproveBookRequestCommand> validator,
        IDispatcher dispatcher)
    {
        _context = context;
        _validator = validator;
        _dispatcher = dispatcher;
    }

    public async Task<BookRequestResponse> HandleAsync(
        ApproveBookRequestCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var request = await _context.BookRequests
            .FirstOrDefaultAsync(r => r.Id == command.RequestId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró la solicitud con id '{command.RequestId}'.");

        if (request.Status != BookRequestStatus.Pending)
        {
            throw new ConflictException("La solicitud ya fue resuelta.");
        }

        await using var transaction = await _context.Database.BeginTransactionAsync(cancellationToken);

        var createBookCommand = new CreateBookCommand(
            (command.Title ?? request.Title).Trim(),
            (command.Author ?? request.Author).Trim(),
            command.Isbn ?? request.Isbn,
            command.Genre ?? request.Genre,
            command.Description ?? request.Description,
            request.OpenLibraryKey,
            Content: null,
            command.TotalCopies);

        var createdBook = await _dispatcher.DispatchAsync<BookResponse>(createBookCommand, cancellationToken);

        request.Status = BookRequestStatus.Approved;
        request.PromotedBookId = createdBook.Id;
        request.ResolvedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);

        var userEmail = await _context.Users
            .Where(u => u.Id == request.RequestedBy)
            .Select(u => u.Email ?? string.Empty)
            .FirstOrDefaultAsync(cancellationToken) ?? string.Empty;

        return BookRequestMapper.ToResponse(request, userEmail);
    }
}
