using BibliotecaVirtual.Application.Commands.Books;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;

namespace BibliotecaVirtual.Infrastructure.Handlers.Books;

public sealed class CreateBookCommandHandler : ICommandHandler<CreateBookCommand, BookResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<CreateBookCommand> _validator;

    public CreateBookCommandHandler(BibliotecaDbContext context, IValidator<CreateBookCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<BookResponse> HandleAsync(
        CreateBookCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var book = new Book
        {
            Title = command.Title.Trim(),
            Author = command.Author.Trim(),
            Isbn = command.Isbn?.Trim(),
            Genre = command.Genre?.Trim(),
            Description = command.Description?.Trim(),
            Content = command.Content?.Trim(),
            OpenLibraryKey = command.OpenLibraryKey?.Trim(),
            TotalCopies = command.TotalCopies,
            AvailableCopies = command.TotalCopies,
            CreatedAt = DateTime.UtcNow
        };

        _context.Books.Add(book);
        await _context.SaveChangesAsync(cancellationToken);

        return BookMapper.ToResponse(book);
    }
}
