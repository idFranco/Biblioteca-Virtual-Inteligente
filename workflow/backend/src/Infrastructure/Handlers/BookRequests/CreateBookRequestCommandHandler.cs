using BibliotecaVirtual.Application.Commands.BookRequests;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.BookRequests;

public sealed class CreateBookRequestCommandHandler : ICommandHandler<CreateBookRequestCommand, BookRequestResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<CreateBookRequestCommand> _validator;

    public CreateBookRequestCommandHandler(BibliotecaDbContext context, IValidator<CreateBookRequestCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<BookRequestResponse> HandleAsync(
        CreateBookRequestCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var normalizedTitle = command.Title.Trim();
        var normalizedAuthor = command.Author.Trim();

        var hasPendingDuplicate = await _context.BookRequests.AnyAsync(
            r => r.RequestedBy == command.UserId &&
                 r.Status == BookRequestStatus.Pending &&
                 r.Title.ToLower() == normalizedTitle.ToLower() &&
                 r.Author.ToLower() == normalizedAuthor.ToLower(),
            cancellationToken);

        if (hasPendingDuplicate)
        {
            throw new ConflictException("Ya tienes una solicitud pendiente para este libro.");
        }

        var request = new BookRequest
        {
            Title = normalizedTitle,
            Author = normalizedAuthor,
            Isbn = command.Isbn?.Trim(),
            Genre = command.Genre?.Trim(),
            Description = command.Description?.Trim(),
            OpenLibraryKey = command.OpenLibraryKey?.Trim(),
            RequestedBy = command.UserId,
            RequestedAt = DateTime.UtcNow,
            Status = BookRequestStatus.Pending
        };

        _context.BookRequests.Add(request);
        await _context.SaveChangesAsync(cancellationToken);

        var userEmail = await _context.Users
            .Where(u => u.Id == command.UserId)
            .Select(u => u.Email ?? string.Empty)
            .FirstOrDefaultAsync(cancellationToken) ?? string.Empty;

        return BookRequestMapper.ToResponse(request, userEmail);
    }
}
