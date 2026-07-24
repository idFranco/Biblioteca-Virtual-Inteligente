using Microsoft.AspNetCore.Identity;

namespace BibliotecaVirtual.Domain.Entities;

public sealed class Role : IdentityRole<Guid>
{
    public string? Description { get; set; }
}
