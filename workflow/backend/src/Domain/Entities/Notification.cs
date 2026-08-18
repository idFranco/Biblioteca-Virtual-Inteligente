namespace BibliotecaVirtual.Domain.Entities;

public sealed class Notification
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public Guid RentalId { get; set; }
    public string Message { get; set; } = string.Empty;
    public DateTime DueDate { get; set; }
    public bool IsRead { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public User? User { get; set; }
    public Rental? Rental { get; set; }
}