using BibliotecaVirtual.Application.Commands.Books;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Books;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace BibliotecaVirtual.WebAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public sealed class BooksController : ControllerBase
{
    private readonly IDispatcher _dispatcher;

    public BooksController(IDispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    private Guid UserId =>
        Guid.Parse(User.FindFirstValue("userId")
            ?? throw new UnauthorizedAccessException("El token no contiene el identificador del usuario."));

    [HttpGet]
    [Authorize(Policy = "books.read")]
    public Task<PagedResult<BookResponse>> GetBooks(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        [FromQuery] string? search = null,
        [FromQuery] string? author = null,
        [FromQuery] string? genre = null,
        [FromQuery] bool? availableOnly = null,
        CancellationToken cancellationToken = default)
    {
        var query = new GetBooksQuery(page, pageSize, search, author, genre, availableOnly);
        return _dispatcher.DispatchAsync<PagedResult<BookResponse>>(query, cancellationToken);
    }

    [HttpGet("{bookId:guid}")]
    [Authorize(Policy = "books.read")]
    public Task<BookResponse> GetBookById(Guid bookId, CancellationToken cancellationToken)
    {
        return _dispatcher.DispatchAsync<BookResponse>(new GetBookByIdQuery(bookId), cancellationToken);
    }

    [HttpGet("{bookId:guid}/reading")]
    [Authorize(Policy = "books.read")]
    public Task<BookForReadingResponse> GetBookForReading(Guid bookId, CancellationToken cancellationToken)
    {
        return _dispatcher.DispatchAsync<BookForReadingResponse>(
            new GetBookForReadingQuery(bookId, UserId),
            cancellationToken);
    }

    [HttpPost]
    [Authorize(Policy = "books.create")]
    public async Task<IActionResult> Create(CreateBookRequest request, CancellationToken cancellationToken)
    {
        var command = new CreateBookCommand(
            request.Title,
            request.Author,
            request.Isbn,
            request.Genre,
            request.Description,
            request.OpenLibraryKey,
            request.TotalCopies);

        var result = await _dispatcher.DispatchAsync<BookResponse>(command, cancellationToken);
        return CreatedAtAction(nameof(GetBookById), new { bookId = result.Id }, result);
    }

    [HttpPut("{bookId:guid}")]
    [Authorize(Policy = "books.update")]
    public async Task<BookResponse> Update(Guid bookId, UpdateBookRequest request, CancellationToken cancellationToken)
    {
        var command = new UpdateBookCommand(
            bookId,
            request.Title,
            request.Author,
            request.Isbn,
            request.Genre,
            request.Description,
            request.OpenLibraryKey,
            request.TotalCopies,
            request.AvailableCopies);

        return await _dispatcher.DispatchAsync<BookResponse>(command, cancellationToken);
    }

    [HttpDelete("{bookId:guid}")]
    [Authorize(Policy = "books.delete")]
    public async Task<IActionResult> Delete(Guid bookId, CancellationToken cancellationToken)
    {
        var result = await _dispatcher.DispatchAsync<DeleteBookResult>(
            new DeleteBookCommand(bookId),
            cancellationToken);

        return result.Deleted ? NoContent() : NotFound();
    }
}