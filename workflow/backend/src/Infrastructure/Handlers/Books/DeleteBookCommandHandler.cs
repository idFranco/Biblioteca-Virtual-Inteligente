using BibliotecaVirtual.Application.Commands.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Books;

public sealed class DeleteBookCommandHandler : ICommandHandler<DeleteBookCommand, DeleteBookResult>
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<DeleteBookCommand> _validator;

    public DeleteBookCommandHandler(BibliotecaDbContext context, IValidator<DeleteBookCommand> validator)
    {
        _context = context;
        _validator = validator;
    }

    public async Task<DeleteBookResult> HandleAsync(
        DeleteBookCommand command,
        CancellationToken cancellationToken = default)
    {
        await _validator.ValidateAndThrowAsync(command, cancellationToken);

        var book = await _context.Books
            .FirstOrDefaultAsync(b => b.Id == command.BookId, cancellationToken)
            ?? throw new KeyNotFoundException($"No se encontró el libro con id '{command.BookId}'.");

        _context.Books.Remove(book);
        await _context.SaveChangesAsync(cancellationToken);

        return new DeleteBookResult(true);
    }
}