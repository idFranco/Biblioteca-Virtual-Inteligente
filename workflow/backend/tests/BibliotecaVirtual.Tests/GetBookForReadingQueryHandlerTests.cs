using BibliotecaVirtual.Application.Queries.Books;
using BibliotecaVirtual.Infrastructure.Handlers.Books;
using Xunit;

namespace BibliotecaVirtual.Tests;

public sealed class GetBookForReadingQueryHandlerTests : IDisposable
{
    private readonly TestDatabase _db;
    private readonly GetBookForReadingQueryHandler _handler;

    public GetBookForReadingQueryHandlerTests()
    {
        _db = new TestDatabase();
        _handler = new GetBookForReadingQueryHandler(_db.Context);
    }

    public void Dispose() => _db.Dispose();

    [Fact]
    public async Task Leer_SinAlquilerActivo_LanzaKeyNotFound()
    {
        var user = _db.CreateUser();
        var book = _db.CreateBook(title: "Crimen y castigo", content: "Contenido de prueba.");

        var query = new GetBookForReadingQuery(book.Id, user.Id);

        await Assert.ThrowsAsync<KeyNotFoundException>(() => _handler.HandleAsync(query));
    }

    [Fact]
    public async Task Leer_ConAlquilerActivo_DevuelveContenido()
    {
        var user = _db.CreateUser();
        var book = _db.CreateBook(title: "Crimen y castigo", content: "Contenido de prueba.");
        _db.CreateRental(user.Id, book.Id);

        var query = new GetBookForReadingQuery(book.Id, user.Id);

        var result = await _handler.HandleAsync(query);

        Assert.NotNull(result);
        Assert.Equal("Contenido de prueba.", result.Content);
    }
}
