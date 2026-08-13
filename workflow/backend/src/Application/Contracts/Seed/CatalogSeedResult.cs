namespace BibliotecaVirtual.Application.Contracts.Seed;

/// <summary>
/// Resultado de la operación de seed del catálogo.
/// </summary>
public sealed record CatalogSeedResult(
    bool Executed,
    int Inserted,
    int Skipped);
