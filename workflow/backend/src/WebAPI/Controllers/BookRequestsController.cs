using System.Security.Claims;
using BibliotecaVirtual.Application.Commands.BookRequests;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.BookRequests;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.BookRequests;
using BibliotecaVirtual.Domain.Enums;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BibliotecaVirtual.WebAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public sealed class BookRequestsController : ControllerBase
{
    private readonly IDispatcher _dispatcher;

    public BookRequestsController(IDispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    private Guid UserId =>
        Guid.Parse(User.FindFirstValue("userId")
            ?? throw new UnauthorizedAccessException("El token no contiene el identificador del usuario."));

    private bool CanViewAll => User.HasClaim("permission", "books.manage");

    [HttpPost]
    [Authorize(Policy = "bookrequests.create")]
    public async Task<IActionResult> Create(CreateBookRequestRequest request, CancellationToken cancellationToken)
    {
        var command = new CreateBookRequestCommand(
            UserId,
            request.Title,
            request.Author,
            request.Isbn,
            request.Genre,
            request.Description,
            request.OpenLibraryKey);

        var result = await _dispatcher.DispatchAsync<BookRequestResponse>(command, cancellationToken);
        return CreatedAtAction(nameof(GetById), new { requestId = result.Id }, result);
    }

    [HttpGet("mine")]
    [Authorize(Policy = "bookrequests.view_own")]
    public Task<PagedResult<BookRequestResponse>> GetMine(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        [FromQuery] BookRequestStatus? status = null,
        CancellationToken cancellationToken = default)
    {
        return _dispatcher.DispatchAsync<PagedResult<BookRequestResponse>>(
            new GetMyBookRequestsQuery(UserId, page, pageSize, status),
            cancellationToken);
    }

    [HttpGet]
    [Authorize(Policy = "bookrequests.manage")]
    public Task<PagedResult<BookRequestResponse>> GetAll(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        [FromQuery] BookRequestStatus? status = null,
        [FromQuery] string? search = null,
        CancellationToken cancellationToken = default)
    {
        return _dispatcher.DispatchAsync<PagedResult<BookRequestResponse>>(
            new GetBookRequestsQuery(page, pageSize, status, search),
            cancellationToken);
    }

    [HttpGet("{requestId:guid}")]
    [Authorize(Policy = "bookrequests.create")]
    public Task<BookRequestResponse> GetById(Guid requestId, CancellationToken cancellationToken)
    {
        return _dispatcher.DispatchAsync<BookRequestResponse>(
            new GetBookRequestByIdQuery(requestId, UserId, CanViewAll),
            cancellationToken);
    }

    [HttpPost("{requestId:guid}/approve")]
    [Authorize(Policy = "bookrequests.manage")]
    public Task<BookRequestResponse> Approve(
        Guid requestId,
        ApproveBookRequestRequest request,
        CancellationToken cancellationToken)
    {
        var command = new ApproveBookRequestCommand(
            requestId,
            UserId,
            request.Title,
            request.Author,
            request.Isbn,
            request.Genre,
            request.Description,
            request.TotalCopies);

        return _dispatcher.DispatchAsync<BookRequestResponse>(command, cancellationToken);
    }

    [HttpPost("{requestId:guid}/reject")]
    [Authorize(Policy = "bookrequests.manage")]
    public Task<BookRequestResponse> Reject(
        Guid requestId,
        RejectBookRequestRequest request,
        CancellationToken cancellationToken)
    {
        var command = new RejectBookRequestCommand(requestId, UserId, request.AdminNotes);
        return _dispatcher.DispatchAsync<BookRequestResponse>(command, cancellationToken);
    }
}
