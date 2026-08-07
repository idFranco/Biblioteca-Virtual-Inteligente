using BibliotecaVirtual.Application.Common;

namespace BibliotecaVirtual.Application.Commands.Books;

public sealed record DeleteBookCommand(Guid BookId) : BaseCommand<DeleteBookResult>;

public sealed record DeleteBookResult(bool Deleted);