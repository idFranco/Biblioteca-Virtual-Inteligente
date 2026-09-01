using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Tests;

/// <summary>
/// Base de datos SQLite en memoria compartida por los tests de handlers.
/// Cada instancia abre su propia conexión <c>:memory:</c> y crea el esquema
/// completo (incluidas las tablas de Identity) con <c>EnsureCreated</c>.
/// </summary>
internal sealed class TestDatabase : IDisposable
{
    private readonly SqliteConnection _connection;

    public BibliotecaDbContext Context { get; }

    public TestDatabase()
    {
        _connection = new SqliteConnection("Data Source=:memory:");
        _connection.Open();

        var options = new DbContextOptionsBuilder<BibliotecaDbContext>()
            .UseSqlite(_connection)
            .Options;

        Context = new BibliotecaDbContext(options);
        Context.Database.EnsureCreated();
    }

    public User CreateUser(Guid? id = null)
    {
        var userId = id ?? Guid.NewGuid();
        var email = $"user-{userId:N}@test.local";
        var user = new User
        {
            Id = userId,
            UserName = email,
            NormalizedUserName = email.ToUpperInvariant(),
            Email = email,
            NormalizedEmail = email.ToUpperInvariant(),
            FullName = "Usuario de prueba",
            IsActive = true
        };

        Context.Users.Add(user);
        Context.SaveChanges();
        return user;
    }

    public Book CreateBook(
        string title,
        string author = "Autor de prueba",
        int totalCopies = 3,
        int availableCopies = 3,
        string? content = null)
    {
        var book = new Book
        {
            Id = Guid.NewGuid(),
            Title = title,
            Author = author,
            Genre = "Novela",
            Description = "Descripción de prueba.",
            Content = content,
            TotalCopies = totalCopies,
            AvailableCopies = availableCopies,
            Status = availableCopies > 0 ? BookStatus.Available : BookStatus.Unavailable
        };

        Context.Books.Add(book);
        Context.SaveChanges();
        return book;
    }

    public Rental CreateRental(
        Guid userId,
        Guid bookId,
        RentalStatus status = RentalStatus.Active,
        DateTime? dueDate = null)
    {
        var rental = new Rental
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            BookId = bookId,
            RentedAt = DateTime.UtcNow,
            DueDate = dueDate ?? DateTime.UtcNow.AddDays(14),
            ReturnedAt = status == RentalStatus.Returned ? DateTime.UtcNow : null,
            Status = status
        };

        Context.Rentals.Add(rental);
        Context.SaveChanges();
        return rental;
    }

    public void Dispose()
    {
        Context.Dispose();
        _connection.Dispose();
    }
}