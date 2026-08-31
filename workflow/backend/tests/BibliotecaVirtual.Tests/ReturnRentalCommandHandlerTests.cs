using BibliotecaVirtual.Application.Commands.Rentals;
using BibliotecaVirtual.Application.Commands.Rentals.Validators;
using BibliotecaVirtual.Application.Common;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Handlers.Rentals;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace BibliotecaVirtual.Tests;

public sealed class ReturnRentalCommandHandlerTests : IDisposable
{
    private readonly TestDatabase _db;
    private readonly ReturnRentalCommandHandler _handler;

    public ReturnRentalCommandHandlerTests()
    {
        _db = new TestDatabase();
        _handler = new ReturnRentalCommandHandler(_db.Context, new ReturnRentalCommandValidator());
    }

    public void Dispose() => _db.Dispose();

    [Fact]
    public async Task Devolver_UsuarioDevuelveSuPropioAlquiler_Permite()
    {
        var user = _db.CreateUser();
        var book = _db.CreateBook(title: "El Principito", totalCopies: 3, availableCopies: 2);
        var rental = _db.CreateRental(user.Id, book.Id, RentalStatus.Active);

        var command = new ReturnRentalCommand(rental.Id, user.Id, CanReturnAny: false);

        var result = await _handler.HandleAsync(command);

        Assert.Equal("Returned", result.Status);
    }

    [Fact]
    public async Task Devolver_UsuarioDevuelveAlquilerAjeno_LanzaKeyNotFound()
    {
        var owner = _db.CreateUser();
        var other = _db.CreateUser();
        var book = _db.CreateBook(title: "El Principito", totalCopies: 3, availableCopies: 2);
        var rental = _db.CreateRental(owner.Id, book.Id, RentalStatus.Active);

        var command = new ReturnRentalCommand(rental.Id, other.Id, CanReturnAny: false);

        await Assert.ThrowsAsync<KeyNotFoundException>(() => _handler.HandleAsync(command));
    }

    [Fact]
    public async Task Devolver_BibliotecarioDevuelveAlquilerAjeno_Permite()
    {
        var owner = _db.CreateUser();
        var staff = _db.CreateUser();
        var book = _db.CreateBook(title: "El Principito", totalCopies: 3, availableCopies: 2);
        var rental = _db.CreateRental(owner.Id, book.Id, RentalStatus.Active);

        var command = new ReturnRentalCommand(rental.Id, staff.Id, CanReturnAny: true);

        var result = await _handler.HandleAsync(command);

        Assert.Equal("Returned", result.Status);
    }

    [Fact]
    public async Task Devolver_AlquilerYaDevuelto_LanzaConflict()
    {
        var user = _db.CreateUser();
        var book = _db.CreateBook(title: "El Principito", totalCopies: 3, availableCopies: 2);
        var rental = _db.CreateRental(user.Id, book.Id, RentalStatus.Returned);

        var command = new ReturnRentalCommand(rental.Id, user.Id, CanReturnAny: false);

        var ex = await Assert.ThrowsAsync<ConflictException>(() => _handler.HandleAsync(command));

        Assert.Equal("El alquiler ya ha sido devuelto.", ex.Message);
    }

    [Fact]
    public async Task Devolver_RestauraStock()
    {
        var user = _db.CreateUser();
        var book = _db.CreateBook(title: "El Principito", totalCopies: 3, availableCopies: 2);
        var rental = _db.CreateRental(user.Id, book.Id, RentalStatus.Active);

        var command = new ReturnRentalCommand(rental.Id, user.Id, CanReturnAny: false);

        await _handler.HandleAsync(command);

        var updated = await _db.Context.Books
            .AsNoTracking()
            .SingleAsync(b => b.Id == book.Id);

        Assert.Equal(3, updated.AvailableCopies);
    }
}
