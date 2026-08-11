namespace BibliotecaVirtual.Application.Contracts.Books;

public sealed record BookResponse(
    Guid Id,
    string Title,
    string Author,
    string? Isbn,
    string? Genre,
    string? Description,
    string? OpenLibraryKey,
    int TotalCopies,
    int AvailableCopies,
    bool IsAvailable);

public sealed record CreateBookRequest(
    string Title,
    string Author,
    string? Isbn,
    string? Genre,
    string? Description,
    string? OpenLibraryKey,
    int TotalCopies);

public sealed record UpdateBookRequest(
    string Title,
    string Author,
    string? Isbn,
    string? Genre,
    string? Description,
    string? OpenLibraryKey,
    int TotalCopies,
    int AvailableCopies);

public sealed record PagedResult<T>(int Page, int PageSize, int TotalItems, int TotalPages, IReadOnlyList<T> Items);
