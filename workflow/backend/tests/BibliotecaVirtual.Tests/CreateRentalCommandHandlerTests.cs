using BibliotecaVirtual.Application.Commands.Rentals;
using BibliotecaVirtual.Application.Commands.Rentals.Validators;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Infrastructure.Handlers.Rentals;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Xunit;

namespace BibliotecaVirtual.Tests;

public sealed class CreateRentalCommandHandlerTests : IDisposable
{
    private readonly TestDatabase _db;
    private readonly CreateRentalCommandHandler _handler;

    public CreateRentalCommandHandlerTests()
    {
        _db = new TestDatabase();

        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["Rentals:MaxActivePerUser"] = "5"
            })
            .Build();

        _handler = new CreateRentalCommandHandler(_db.Context, new CreateRentalCommandValidator(), configuration);
    }

    public void Dispose() => _db.Dispose();

    [Fact]
    public async Task CreateRental_RejectsDuplicateActiveRental_SameBook()
    {
        var user = _db.CreateUser();
        var book = _db.CreateBook(title: "Cien años de soledad", availableCopies: 3);
        _db.CreateRental(user.Id, book.Id);

        var command = new CreateRentalCommand(user.Id, book.Id, null);

        var ex = await Assert.ThrowsAsync<ConflictException>(() => _handler.HandleAsync(command));

        Assert.Equal("Ya tienes un alquiler activo de este libro.", ex.Message);
    }

    [Fact]
    public async Task CreateRental_RejectsDuplicateActiveRental_SameTitle_DifferentBookId()
    {
        var user = _db.CreateUser();
        var firstCopy = _db.CreateBook(title: "Cien años de soledad", availableCopies: 2);
        var secondCopy = _db.CreateBook(title: "Cien años de soledad", availableCopies: 2);
        _db.CreateRental(user.Id, firstCopy.Id);

        var command = new CreateRentalCommand(user.Id, secondCopy.Id, null);

        var ex = await Assert.ThrowsAsync<ConflictException>(() => _handler.HandleAsync(command));

        Assert.Equal("Ya tienes un alquiler activo de este libro.", ex.Message);
    }

    [Fact]
    public async Task CreateRental_AllowsDifferentTitle()
    {
        var user = _db.CreateUser();
        var firstBook = _db.CreateBook(title: "Cien años de soledad", availableCopies: 1);
        _db.CreateRental(user.Id, firstBook.Id);
        var secondBook = _db.CreateBook(title: "Don Quijote de la Mancha", availableCopies: 2);

        var command = new CreateRentalCommand(user.Id, secondBook.Id, null);

        var result = await _handler.HandleAsync(command);

        Assert.NotNull(result);
        Assert.Equal(secondBook.Id, result.BookId);
    }

    [Fact]
    public async Task CreateRental_RejectsWhenMaxConcurrentReached()
    {
        var user = _db.CreateUser();
        for (var i = 0; i < 5; i++)
        {
            var book = _db.CreateBook(title: $"Libro activo {i}", availableCopies: 1);
            _db.CreateRental(user.Id, book.Id);
        }

        var sixthBook = _db.CreateBook(title: "Sexto libro", availableCopies: 1);
        var command = new CreateRentalCommand(user.Id, sixthBook.Id, null);

        var ex = await Assert.ThrowsAsync<ConflictException>(() => _handler.HandleAsync(command));

        Assert.Contains("máximo de 5 alquileres activos", ex.Message);
    }

    [Fact]
    public async Task CreateRental_AllowsBelowMaxConcurrent()
    {
        var user = _db.CreateUser();
        for (var i = 0; i < 4; i++)
        {
            var book = _db.CreateBook(title: $"Libro activo {i}", availableCopies: 1);
            _db.CreateRental(user.Id, book.Id);
        }

        var fifthBook = _db.CreateBook(title: "Quinto libro", availableCopies: 1);
        var command = new CreateRentalCommand(user.Id, fifthBook.Id, null);

        var result = await _handler.HandleAsync(command);

        Assert.NotNull(result);
        Assert.Equal(fifthBook.Id, result.BookId);
    }

    [Fact]
    public async Task CreateRental_DecrementsStock()
    {
        var user = _db.CreateUser();
        var book = _db.CreateBook(title: "Moby Dick", totalCopies: 3, availableCopies: 3);

        var command = new CreateRentalCommand(user.Id, book.Id, null);

        await _handler.HandleAsync(command);

        var updated = await _db.Context.Books
            .AsNoTracking()
            .SingleAsync(b => b.Id == book.Id);

        Assert.Equal(2, updated.AvailableCopies);
    }
}