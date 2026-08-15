using BibliotecaVirtual.Application.Contracts.Seed;

namespace BibliotecaVirtual.Application.Interfaces;

/// <summary>
/// Siembra el catálogo demo con libros de ejemplo de forma idempotente.
/// </summary>
public interface ICatalogSeeder
{
    /// <summary>
    /// Inserta libros de ejemplo si la tabla de libros está vacía.
    /// </summary>
    /// <param name="cancellationToken">Token de cancelación.</param>
    Task<CatalogSeedResult> SeedAsync(CancellationToken cancellationToken = default);
}
