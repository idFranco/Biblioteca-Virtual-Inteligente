using BibliotecaVirtual.Domain.Enums;

namespace BibliotecaVirtual.Domain.Entities;

public sealed class Book
{
    public Guid Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string? Isbn { get; set; }
    public string? Genre { get; set; }
    public string? Description { get; set; }
    public int TotalCopies { get; set; }
    public int AvailableCopies { get; set; }
    public BookStatus Status { get; set; } = BookStatus.Available;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? UpdatedAt { get; set; }
}
