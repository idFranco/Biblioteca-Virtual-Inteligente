using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using BibliotecaVirtual.Application.Contracts.Auth;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Infrastructure.Data;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;

namespace BibliotecaVirtual.Infrastructure.Services;

public sealed class TokenService : ITokenService
{
    private readonly IConfiguration _configuration;
    private readonly UserManager<User> _userManager;
    private readonly BibliotecaDbContext _context;

    public TokenService(
        IConfiguration configuration,
        UserManager<User> userManager,
        BibliotecaDbContext context)
    {
        _configuration = configuration;
        _userManager = userManager;
        _context = context;
    }

    public async Task<AuthResponse> CreateAuthResponseAsync(User user, CancellationToken cancellationToken = default)
    {
        var roles = await _userManager.GetRolesAsync(user);
        var accessToken = GenerateAccessToken(user, roles);
        var accessTokenExpirationMinutes = _configuration.GetValue("Jwt:AccessTokenExpirationMinutes", 15);
        var refreshTokenExpirationDays = _configuration.GetValue("Jwt:RefreshTokenExpirationDays", 7);

        var refreshToken = GenerateRefreshToken();
        await StoreRefreshTokenAsync(user, refreshToken, refreshTokenExpirationDays, cancellationToken);

        return new AuthResponse(
            AccessToken: accessToken,
            AccessTokenExpiresAt: DateTime.UtcNow.AddMinutes(accessTokenExpirationMinutes),
            RefreshToken: refreshToken,
            User: new AuthUserResponse(
                user.Id,
                user.FullName ?? user.Email ?? string.Empty,
                user.Email ?? string.Empty,
                roles.ToArray()));
    }

    private string GenerateAccessToken(User user, IList<string> roles)
    {
        var jwtKey = _configuration["Jwt:Key"]
            ?? throw new InvalidOperationException("JWT Key is not configured");
        var issuer = _configuration["Jwt:Issuer"] ?? "BibliotecaVirtual";
        var audience = _configuration["Jwt:Audience"] ?? "BibliotecaVirtual";
        var expirationMinutes = _configuration.GetValue("Jwt:AccessTokenExpirationMinutes", 15);

        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new(JwtRegisteredClaimNames.Email, user.Email ?? string.Empty),
            new(JwtRegisteredClaimNames.Name, user.FullName ?? string.Empty),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new("userId", user.Id.ToString())
        };

        claims.AddRange(roles.Select(role => new Claim(ClaimTypes.Role, role)));

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: issuer,
            audience: audience,
            claims: claims,
            notBefore: DateTime.UtcNow,
            expires: DateTime.UtcNow.AddMinutes(expirationMinutes),
            signingCredentials: credentials);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    private static string GenerateRefreshToken()
    {
        var randomBytes = new byte[64];
        using var rng = RandomNumberGenerator.Create();
        rng.GetBytes(randomBytes);
        return Convert.ToBase64String(randomBytes);
    }

    private async Task StoreRefreshTokenAsync(
        User user,
        string refreshToken,
        int refreshTokenExpirationDays,
        CancellationToken cancellationToken)
    {
        _context.RefreshTokens.Add(new RefreshToken
        {
            UserId = user.Id,
            TokenHash = TokenHasher.Hash(refreshToken),
            ExpiresAt = DateTime.UtcNow.AddDays(refreshTokenExpirationDays)
        });

        await _context.SaveChangesAsync(cancellationToken);
    }
}