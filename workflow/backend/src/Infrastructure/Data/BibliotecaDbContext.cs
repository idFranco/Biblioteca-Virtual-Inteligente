using BibliotecaVirtual.Domain.Entities;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Data;

public sealed class BibliotecaDbContext : IdentityDbContext<User, Role, Guid>
{
    public BibliotecaDbContext(DbContextOptions<BibliotecaDbContext> options)
        : base(options)
    {
    }

    public DbSet<Book> Books => Set<Book>();
    public DbSet<Rental> Rentals => Set<Rental>();

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);

        builder.Entity<Book>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Title).IsRequired().HasMaxLength(255);
            entity.Property(e => e.Author).IsRequired().HasMaxLength(255);
            entity.Property(e => e.Isbn).HasMaxLength(20);
            entity.Property(e => e.Genre).HasMaxLength(100);
            entity.Property(e => e.Description).HasMaxLength(2000);
        });

        builder.Entity<Rental>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Status)
                  .HasConversion<string>()
                  .HasMaxLength(20);
        });
    }
}
