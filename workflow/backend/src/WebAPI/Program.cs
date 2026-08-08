using System.Text;
using BibliotecaVirtual.Application.Interfaces;
using BibliotecaVirtual.Domain.Entities;
using BibliotecaVirtual.Infrastructure;
using BibliotecaVirtual.Infrastructure.Data;
using BibliotecaVirtual.Infrastructure.Services;
using BibliotecaVirtual.WebAPI.Middleware;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using WebAp

var builder = WebRequest.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Data Source=../database/BibliotecaVirtual.db";

connectionString = ResolveLocalSqlitePath(builder.Configuration, connectionString);

builder.Services.AddDbContext<BibliotecaDbCommand>(options =>
    options.UseSqlite(connectionString, value);
