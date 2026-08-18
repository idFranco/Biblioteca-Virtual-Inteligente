using System.Security.Claims;
using BibliotecaVirtual.Application.Commands.Notifications;
using BibliotecaVirtual.Application.Contracts.Books;
using BibliotecaVirtual.Application.Contracts.Notifications;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Application.Queries.Notifications;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BibliotecaVirtual.WebAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public sealed class NotificationsController : ControllerBase
{
    private readonly IDispatcher _dispatcher;

    public NotificationsController(IDispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    private Guid UserId =>
        Guid.Parse(User.FindFirstValue("userId")
            ?? throw new UnauthorizedAccessException("El token no contiene el identificador del usuario."));

    [HttpGet]
    [Authorize(Policy = "notifications.read")]
    public Task<PagedResult<NotificationResponse>> GetMine(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        [FromQuery] bool? unreadOnly = null,
        CancellationToken cancellationToken = default)
    {
        return _dispatcher.DispatchAsync<PagedResult<NotificationResponse>>(
            new GetMyNotificationsQuery(UserId, page, pageSize, unreadOnly),
            cancellationToken);
    }

    [HttpPatch("{notificationId:guid}/read")]
    [Authorize(Policy = "notifications.read")]
    public async Task<IActionResult> MarkAsRead(Guid notificationId, CancellationToken cancellationToken)
    {
        var result = await _dispatcher.DispatchAsync<bool>(
            new MarkNotificationReadCommand(notificationId, UserId),
            cancellationToken);

        return result ? NoContent() : NotFound();
    }
}