using BibliotecaVirtual.Application.Commands.Books;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Books;

public sealed class UpdateBookCommandHandler : ICommandHandler<UpdateBookCommand, BookResponse>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<UpdateBookCommand> _validator;

    public UpdateBookCommandHandler(BibliotecaDbContext context, IValidator<UpdateBookCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<BookResponse> HandleAsync(
        UpdateBookCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var book = await _context.Books
            .FirstOrDefaultAsync(b => b.Id == command.BookId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró el libro con id '{command.BookId}'.");

        book.Title = command.Title.Trim();
        book.Author = command.Author.Trim();
        book.Isbn = command.Isbn?.Trim();
        book.Genre = command.Genre?.Trim();
        book.Description = command.Description?.Trim();
        book.TotalCopies = command.TotalCopies;
        book.AvailableCopies = command.AvailableCopies;
        book.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync(cancellationToken);

        return BookMapper.ToResponse(book);
    }
}