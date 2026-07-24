using Microsoft.AspNetCore.Identity;

namespace BibliotecaVirtual.Domain.Entities;

public sealed class User : IdentityUser<Guid>
{
    public string? FullName { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public bool IsActive { get; set; } = true;
}
