using System.Text.Json;
using BibliotecaVirtual.Application.Contracts.Seed;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Infrastructure.Common;
using BibliotecaVirtual.Infrastructure.Data;
using FluentValidation;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace BibliotecaVirtual.Infrastructure.Data.Seed;

/// <summary>
/// Seeder idempotente del catálogo demo. Lee el dataset de <c>seed-books.json</c>
/// (fuente única de verdad) e inserta los libros solo si la tabla <c>Books</c>
/// está vacía. Cada entrada inválida se omite con un warning sin abortar el arranque.
/// </summary>
public sealed class CatalogSeeder : ICatalogSeeder
{
    private readonly BibliotecaDbContext _context;
    private readonly IValidator<SeedBookDto> _validator;
    private readonly IConfiguration _configuration;
    private readonly ILogger<CatalogSeeder> _logger;

    public CatalogSeeder(
        BibliotecaDbContext context,
        IValidator<SeedBookDto> validator,
        IConfiguration configuration,
        ILogger<CatalogSeeder> logger)
    {
        _context = context;
        _validator = validator;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<CatalogSeedResult> SeedAsync(CancellationToken cancellationToken = default)
    {
        var enabled = _configuration.GetValue<bool?>("CatalogSeed:Enabled");
        if (enabled is null)
        {
            throw new InvalidOperationException(
                "The required configuration 'CatalogSeed:Enabled' is missing. Set it via the environment variable 'CatalogSeed__Enabled'.");
        }

        if (!enabled.Value)
        {
            _logger.LogInformation("Seed de catálogo deshabilitado por configuración.");
            return new CatalogSeedResult(Executed: false, Inserted: 0, Skipped: 0);
        }

        if (await _context.Books.AnyAsync(cancellationToken))
        {
            _logger.LogInformation("La tabla de libros ya contiene datos; seed omitido.");
            return new CatalogSeedResult(Executed: false, Inserted: 0, Skipped: 0);
        }

        var entries = await LoadEntriesAsync(cancellationToken);
        if (entries.Count == 0)
        {
            _logger.LogWarning("No se encontró contenido de seed en el dataset.");
            return new CatalogSeedResult(Executed: true, Inserted: 0, Skipped: 0);
        }

        var inserted = 0;
        var skipped = 0;

        foreach (var entry in entries)
        {
            var validation = _validator.Validate(entry);
            if (!validation.IsValid)
            {
                skipped++;
                _logger.LogWarning(
                    "Entrada de seed omitida (\"{Title}\"): {Errors}",
                    entry.Title,
                    string.Join("; ", validation.Errors.Select(e => e.ErrorMessage)));
                continue;
            }

            _context.Books.Add(MapEntity(entry));
            inserted++;
        }

        await _context.SaveChangesAsync(cancellationToken);
        _logger.LogInformation("Seed de catálogo completado: {Inserted} insertados, {Skipped} omitidos.", inserted, skipped);

        return new CatalogSeedResult(Executed: true, Inserted: inserted, Skipped: skipped);
    }

    private async Task<List<SeedBookDto>> LoadEntriesAsync(CancellationToken cancellationToken)
    {
        var filePath = ResolveFilePath();
        if (!File.Exists(filePath))
        {
            _logger.LogWarning("No se encontró el dataset de seed en {Path}.", filePath);
            return [];
        }

        await using var stream = File.OpenRead(filePath);
        var container = await JsonSerializer.DeserializeAsync<SeedFileContainer>(
            stream,
            new JsonSerializerOptions(JsonSerializerDefaults.Web),
            cancellationToken);

        return container?.Books ?? [];
    }

    private string ResolveFilePath()
    {
        var configured = _configuration.GetRequiredString("CatalogSeed:FilePath");
        return Path.IsPathRooted(configured)
            ? configured
            : Path.Combine(AppContext.BaseDirectory, configured);
    }

    private static Book MapEntity(SeedBookDto dto) => new()
    {
        Title = dto.Title,
        Author = dto.Author,
        Isbn = dto.Isbn,
        Genre = dto.Genre,
        Description = dto.Description,
        OpenLibraryKey = dto.OpenLibraryKey,
        TotalCopies = dto.TotalCopies,
        AvailableCopies = dto.AvailableCopies,
        Status = dto.AvailableCopies > 0 ? Domain.Enums.BookStatus.Available : Domain.Enums.BookStatus.Unavailable,
        CreatedAt = DateTime.UtcNow,
    };

    private sealed class SeedFileContainer
    {
        public List<SeedBookDto> Books { get; set; } = [];
    }
}
