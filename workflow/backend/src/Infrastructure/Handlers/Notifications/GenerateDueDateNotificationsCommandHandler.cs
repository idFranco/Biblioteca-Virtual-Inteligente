using BibliotecaVirtual.Application.Commands.Notifications;
using BibliotecaVirtual.Application.Contracts.Notifications;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Domain.Enums;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BibliotecaVirtual.Infrastructure.Handlers.Notifications;

public sealed class GenerateDueDateNotificationsCommandHandler : ICommandHandler<GenerateDueDateNotificationsCommand, GenerateDueDateNotificationsResult>
{
    private readonly BibliotecaDbContext _context;

    public GenerateDueDateNotificationsCommandHandler(BibliotecaDbContext context)
    {
        _context = context;
    }

    public async Task<GenerateDueDateNotificationsResult> HandleAsync(
        GenerateDueDateNotificationsCommand command,
        CancellationToken cancellationToken = default)
    {
        var now = DateTime.UtcNow;
        var dueWindowEnd = now.AddDays(2);

        var existingRentalIds = await _context.Notifications
            .AsNoTracking()
            .Select(n => n.RentalId)
            .ToListAsync(cancellationToken);

        var existingSet = new HashSet<Guid>(existingRentalIds);

        var dueRentals = await _context.Rentals
            .AsNoTracking()
            .Where(r => r.Status == RentalStatus.Active
                        && r.DueDate > now
                        && r.DueDate <= dueWindowEnd)
            .Join(
                _context.Books,
                rental => rental.BookId,
                book => book.Id,
                (rental, book) => new { Rental = rental, BookTitle = book.Title })
            .ToListAsync(cancellationToken);

        var notifications = dueRentals
            .Where(x => !existingSet.Contains(x.Rental.Id))
            .Select(x => new Notification
            {
                UserId = x.Rental.UserId,
                RentalId = x.Rental.Id,
                Message = $"Tu alquiler de \"{x.BookTitle}\" vence el {x.Rental.DueDate:dd/MM/yyyy}. Devuélvelo a tiempo.",
                DueDate = x.Rental.DueDate,
                IsRead = false
            })
            .ToList();

        if (notifications.Count == 0)
        {
            return new GenerateDueDateNotificationsResult(0);
        }

        _context.Notifications.AddRange(notifications);
        await _context.SaveChangesAsync(cancellationToken);

        return new GenerateDueDateNotificationsResult(notifications.Count);
    }
}