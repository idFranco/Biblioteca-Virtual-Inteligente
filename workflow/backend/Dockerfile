FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY BibliotecaVirtual.slnx ./
COPY src/Domain/BibliotecaVirtual.Domain.csproj src/Domain/
COPY src/Application/BibliotecaVirtual.Application.csproj src/Application/
COPY src/Infrastructure/BibliotecaVirtual.Infrastructure.csproj src/Infrastructure/
COPY src/WebAPI/BibliotecaVirtual.WebAPI.csproj src/WebAPI/
RUN dotnet restore

COPY . .
RUN dotnet publish src/WebAPI/BibliotecaVirtual.WebAPI.csproj -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=build /app .
EXPOSE 5000
ENV ASPNETCORE_URLS=http://+:5000
ENTRYPOINT ["dotnet", "BibliotecaVirtual.WebAPI.dll"]
