namespace BibliotecaVirtual.Application.Contracts.Seed;

/// <summary>
/// Modelo de un libro proveniente del dataset de seed (<c>seed-books.json</c>).
/// </summary>
public sealed record SeedBookDto(
    string Title,
    string Author,
    string? Isbn,
    string? Genre,
    string? Description,
    string? OpenLibraryKey,
    string? Content,
    int TotalCopies,
    int AvailableCopies);
