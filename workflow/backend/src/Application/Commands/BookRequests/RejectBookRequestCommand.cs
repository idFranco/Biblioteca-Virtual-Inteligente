using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Application.Contracts.BookRequests;

namespace BibliotecaVirtual.Application.Commands.BookRequests;

public sealed record RejectBookRequestCommand(
    Guid RequestId,
    Guid AdminId,
    string AdminNotes) : BaseCommand<BookRequestResponse>;
