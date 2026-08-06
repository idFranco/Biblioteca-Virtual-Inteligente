using System.Text;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Infrastructure.Data;
using BibliotecaVirtual.Infrastructure.Services;
using BibliotecaVirtual.WebAPI.Middleware;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Identity;
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

var jwtKey = builder.Configuration["Jwt:Key"]
    ?? throw new InvalidOperationException("JWT Key is not configured");

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
        ValidIssuer = builder.Configuration["Jwt:Issuer"] ?? "BibliotecaVirtual",
        ValidAudience = builder.Configuration["Jwt:Audience"] ?? "BibliotecaVirtual",
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
    };
});

builder.Services.AddAuthorization();

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins(builder.Configuration["Cors:Origins"] ?? "http://localhost:5173")
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

builder.Services.AddHealthChecks()
    .AddDbContextCheck<BibliotecaDbContext>();

builder.Services.AddScoped<IDispatcher, Dispatcher>();

var app = builder.Build();

app.UseMiddleware<GlobalExceptionHandler>();
app.UseCors("AllowFrontend");
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.MapHealthChecks("/health");

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<BibliotecaDbContext>();
    db.Database.EnsureCreated();
}

app.Run();

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
