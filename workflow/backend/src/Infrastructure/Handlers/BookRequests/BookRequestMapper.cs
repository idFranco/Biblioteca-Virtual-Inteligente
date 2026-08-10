using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Domain.Entities;

namespace BibliotecaVirtual.Infrastructure.Handlers.BookRequests;

internal static class BookRequestMapper
{
    internal static BookRequestResponse ToResponse(BookRequest request, string requestedByEmail) => new(
        request.Id,
        request.Title,
        request.Author,
        request.Isbn,
        request.Genre,
        request.Description,
        request.OpenLibraryKey,
        request.RequestedBy,
        requestedByEmail,
        request.RequestedAt,
        request.Status,
        request.AdminNotes,
        request.PromotedBookId,
        request.ResolvedAt);
}
