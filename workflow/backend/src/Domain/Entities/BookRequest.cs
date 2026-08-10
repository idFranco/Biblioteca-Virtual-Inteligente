using BibliotecaVirtual.Domain.Enums;

namespace BibliotecaVirtual.Domain.Entities;

public sealed class BookRequest
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Title { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string? Isbn { get; set; }
    public string? Genre { get; set; }
    public string? Description { get; set; }
    public string? OpenLibraryKey { get; set; }
    public Guid RequestedBy { get; set; }
    public DateTime RequestedAt { get; set; } = DateTime.UtcNow;
    public BookRequestStatus Status { get; set; } = BookRequestStatus.Pending;
    public string? AdminNotes { get; set; }
    public Guid? PromotedBookId { get; set; }
    public DateTime? ResolvedAt { get; set; }

    public User? RequestedByUser { get; set; }
    public Book? PromotedBook { get; set; }
}
