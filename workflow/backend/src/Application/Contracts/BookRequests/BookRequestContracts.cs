using BibliotecaVirtual.Domain.Enums;

namespace BibliotecaVirtual.Application.Contracts.BookRequests;

public sealed record BookRequestResponse(
    Guid Id,
    string Title,
    string Author,
    string? Isbn,
    string? Genre,
    string? Description,
    string? OpenLibraryKey,
    Guid RequestedBy,
    string RequestedByEmail,
    DateTime RequestedAt,
    BookRequestStatus Status,
    string? AdminNotes,
    Guid? PromotedBookId,
    DateTime? ResolvedAt);

public sealed record CreateBookRequestRequest(
    string Title,
    string Author,
    string? Isbn,
    string? Genre,
    string? Description,
    string? OpenLibraryKey);

public sealed record ApproveBookRequestRequest(
    string? Title,
    string? Author,
    string? Isbn,
    string? Genre,
    string? Description,
    int TotalCopies = 1);

public sealed record RejectBookRequestRequest(string AdminNotes);
