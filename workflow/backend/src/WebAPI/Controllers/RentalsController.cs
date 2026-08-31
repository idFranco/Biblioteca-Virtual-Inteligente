using System.Security.Claims;
using BibliotecaVirtual.Application.Commands.Rentals;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.Rentals;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Rentals;
using BibliotecaVirtual.Domain.Enums;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BibliotecaVirtual.WebAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public sealed class RentalsController : ControllerBase
{
    private readonly IDispatcher _dispatcher;

    public RentalsController(IDispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    private Guid UserId =>
        Guid.Parse(User.FindFirstValue("userId")
            ?? throw new UnauthorizedAccessException("El token no contiene el identificador del usuario."));

    private bool CanViewAll => User.HasClaim("permission", "rentals.view_all");

    [HttpPost]
    [Authorize(Policy = "rentals.create")]
    public async Task<IActionResult> Create(CreateRentalRequest request, CancellationToken cancellationToken)
    {
        var command = new CreateRentalCommand(UserId, request.BookId, request.DueDate);
        var result = await _dispatcher.DispatchAsync<RentalResponse>(command, cancellationToken);
        return CreatedAtAction(nameof(GetRentalById), new { rentalId = result.Id }, result);
    }

    [HttpPost("{rentalId:guid}/return")]
    [Authorize(Policy = "rentals.return_own")]
    public Task<RentalResponse> Return(Guid rentalId, CancellationToken cancellationToken)
    {
        var command = new ReturnRentalCommand(
            rentalId,
            UserId,
            User.HasClaim("permission", "rentals.return"));
        return _dispatcher.DispatchAsync<RentalResponse>(command, cancellationToken);
    }

    [HttpGet("mine")]
    [Authorize(Policy = "rentals.view_own")]
    public Task<PagedResult<RentalResponse>> GetMine(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        [FromQuery] RentalStatus? status = null,
        CancellationToken cancellationToken = default)
    {
        return _dispatcher.DispatchAsync<PagedResult<RentalResponse>>(
            new GetMyRentalsQuery(UserId, page, pageSize, status),
            cancellationToken);
    }

    [HttpGet]
    [Authorize(Policy = "rentals.view_all")]
    public Task<PagedResult<RentalResponse>> GetAll(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        [FromQuery] Guid? userId = null,
        [FromQuery] RentalStatus? status = null,
        CancellationToken cancellationToken = default)
    {
        return _dispatcher.DispatchAsync<PagedResult<RentalResponse>>(
            new GetRentalsQuery(page, pageSize, userId, status),
            cancellationToken);
    }

    [HttpGet("{rentalId:guid}")]
    [Authorize(Policy = "rentals.view")]
    public Task<RentalResponse> GetRentalById(Guid rentalId, CancellationToken cancellationToken)
    {
        return _dispatcher.DispatchAsync<RentalResponse>(
            new GetRentalByIdQuery(rentalId, UserId, CanViewAll),
            cancellationToken);
    }
}