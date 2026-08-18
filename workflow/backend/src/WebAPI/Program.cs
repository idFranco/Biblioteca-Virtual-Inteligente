using System.Text;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Infrastructure;
using BibliotecaVirtual.Infrastructure.Common;
using BibliotecaVirtual.Infrastructure.Data;
using BibliotecaVirtual.Infrastructure.Services;
using BibliotecaVirtual.WebAPI.Middleware;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Data Source=../database/BibliotecaVirtual.db";

connectionString = ResolveLocalSqlitePath(builder.Configuration, connectionString);

builder.Services.AddDbContext<BibliotecaDbContext>(options =>
    options.UseSqlite(connectionString, sqlite =>
            sqlite.CommandTimeout(30))
        .AddInterceptors(new SqlitePragmaInterceptor()));

builder.Services.AddIdentity<User, Role>(options =>
{
    options.Password.RequireDigit = true;
    options.Password.RequiredLength = 8;
    options.Password.RequireNonAlphanumeric = false;
    options.Password.RequireUppercase = true;
    options.Lockout.MaxFailedAccessAttempts = 5;
})
.AddEntityFrameworkStores<BibliotecaDbContext>()
.AddDefaultTokenProviders();

var jwtKey = builder.Configuration.GetRequiredString("Jwt:Key");

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = builder.Configuration.GetString("Jwt:Issuer", "BibliotecaVirtual"),
        ValidAudience = builder.Configuration.GetString("Jwt:Audience", "BibliotecaVirtual"),
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
    };
});

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("books.read", policy =>
        policy.RequireClaim("permission", "books.read"));
    options.AddPolicy("books.create", policy =>
        policy.RequireClaim("permission", "books.create"));
    options.AddPolicy("books.update", policy =>
        policy.RequireClaim("permission", "books.update"));
    options.AddPolicy("books.delete", policy =>
        policy.RequireClaim("permission", "books.delete"));

    options.AddPolicy("rentals.create", policy =>
        policy.RequireClaim("permission", "rentals.create"));
    options.AddPolicy("rentals.return", policy =>
        policy.RequireClaim("permission", "rentals.return"));
    options.AddPolicy("rentals.view_own", policy =>
        policy.RequireClaim("permission", "rentals.view_own"));
    options.AddPolicy("rentals.view_all", policy =>
        policy.RequireClaim("permission", "rentals.view_all"));
    options.AddPolicy("rentals.view", policy =>
        policy.RequireAssertion(context =>
            context.User.HasClaim("permission", "rentals.view_own") ||
            context.User.HasClaim("permission", "rentals.view_all")));

    options.AddPolicy("bookrequests.create", policy =>
        policy.RequireClaim("permission", "books.request"));
    options.AddPolicy("bookrequests.view_own", policy =>
        policy.RequireClaim("permission", "books.request"));
    options.AddPolicy("bookrequests.manage", policy =>
        policy.RequireClaim("permission", "books.manage"));

    options.AddPolicy("roles.manage", policy =>
        policy.RequireClaim("permission", "roles.manage"));

    options.AddPolicy("notifications.read", policy =>
        policy.RequireClaim("permission", "notifications.read"));
});

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins(builder.Configuration.GetString("Cors:Origins", "http://localhost:5173"))
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

builder.Services.AddHealthChecks()
    .AddDbContextCheck<BibliotecaDbContext>();

builder.Services.AddRateLimiter(options =>
{
    var authPermitLimit = builder.Configuration.GetInt("AUTH_RATE_LIMIT_PER_MINUTE", 10);

    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddFixedWindowLimiter("auth", limiter =>
    {
        limiter.PermitLimit = authPermitLimit;
        limiter.Window = TimeSpan.FromMinutes(1);
        limiter.QueueLimit = 0;
    });
});

builder.Services.AddInfrastructure();

var app = builder.Build();

app.UseMiddleware<GlobalExceptionHandler>();
app.UseCors("AllowFrontend");
app.UseRateLimiter();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.MapHealthChecks("/health");

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<BibliotecaDbContext>();
    db.Database.EnsureCreated();
    await SeedRolesAsync(scope.ServiceProvider);
    await SeedAdministratorAsync(scope.ServiceProvider, builder.Configuration);

    var catalogSeeder = scope.ServiceProvider.GetRequiredService<ICatalogSeeder>();
    await catalogSeeder.SeedAsync();
}

app.Run();

static async Task SeedRolesAsync(IServiceProvider serviceProvider)
{
    var roleManager = serviceProvider.GetRequiredService<RoleManager<Role>>();

    var rolePermissions = new Dictionary<string, string[]>
    {
        ["Admin"] = [
            "books.read", "books.create", "books.update", "books.delete",
            "rentals.create", "rentals.return", "rentals.view_own", "rentals.view_all",
            "books.request", "books.manage",
            "roles.manage", "notifications.read"],
        ["Bibliotecario"] = [
            "books.read", "books.create", "books.update", "books.delete",
            "rentals.return", "rentals.view_all",
            "books.request", "books.manage", "notifications.read"],
        ["Usuario"] = [
            "books.read", "rentals.create", "rentals.view_own",
            "books.request", "notifications.read"]
    };

    foreach (var (roleName, permissions) in rolePermissions)
    {
        if (!await roleManager.RoleExistsAsync(roleName))
        {
            await roleManager.CreateAsync(new Role { Name = roleName });
        }

        var role = await roleManager.FindByNameAsync(roleName)
            ?? throw new InvalidOperationException($"No se pudo recuperar el rol '{roleName}'.");

        var existingClaims = await roleManager.GetClaimsAsync(role);
        foreach (var permission in permissions)
        {
            if (existingClaims.All(c => c.Type != "permission" || c.Value != permission))
            {
                await roleManager.AddClaimAsync(role, new System.Security.Claims.Claim("permission", permission));
            }
        }
    }
}

static async Task SeedAdministratorAsync(IServiceProvider serviceProvider, IConfiguration configuration)
{
    var adminEmail = configuration["ADMIN_EMAIL"];
    var adminPassword = configuration["ADMIN_PASSWORD"];
    if (string.IsNullOrWhiteSpace(adminEmail) || string.IsNullOrWhiteSpace(adminPassword))
    {
        return;
    }

    var userManager = serviceProvider.GetRequiredService<UserManager<User>>();
    var existing = await userManager.FindByEmailAsync(adminEmail);
    if (existing is not null)
    {
        return;
    }

    var admin = new User
    {
        UserName = adminEmail,
        Email = adminEmail,
        FullName = "Administrador",
        IsActive = true
    };

    var result = await userManager.CreateAsync(admin, adminPassword);
    if (!result.Succeeded)
    {
        throw new InvalidOperationException(
            $"No se pudo crear el usuario administrador inicial: {string.Join("; ", result.Errors.Select(e => e.Description))}");
    }

    await userManager.AddToRoleAsync(admin, "Admin");
}

static string ResolveLocalSqlitePath(IConfiguration configuration, string connectionString)
{
    if (configuration["SQLITE_DATA_SOURCE"] is { Length: > 0 } envSource)
        return envSource;

    var connectionBuilder = new Microsoft.Data.Sqlite.SqliteConnectionStringBuilder(connectionString);
    if (Path.IsPathRooted(connectionBuilder.DataSource))
        return connectionString;

    var databaseDirectory = FindWorkflowDatabaseDirectory()
        ?? Path.Combine(Directory.GetCurrentDirectory(), "database");

    var resolved = Path.Combine(databaseDirectory, Path.GetFileName(connectionBuilder.DataSource));
    Directory.CreateDirectory(databaseDirectory);
    connectionBuilder.DataSource = resolved;
    return connectionBuilder.ToString();
}

static string? FindWorkflowDatabaseDirectory()
{
    var directory = new DirectoryInfo(Directory.GetCurrentDirectory());
    while (directory is not null)
    {
        var workflow = Path.Combine(directory.FullName, "workflow");
        if (Directory.Exists(workflow))
            return Path.Combine(workflow, "database");

        if (File.Exists(Path.Combine(directory.FullName, "docker-compose.yml")))
            return Path.Combine(directory.FullName, "workflow", "database");

        directory = directory.Parent;
    }

    return null;
}