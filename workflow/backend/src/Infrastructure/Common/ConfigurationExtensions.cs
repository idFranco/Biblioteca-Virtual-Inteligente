using Microsoft.Extensions.Configuration;

namespace BibliotecaVirtual.Infrastructure.Common;

public static class ConfigurationExtensions
{
    public static string GetRequiredString(this IConfiguration configuration, string key)
    {
        var value = configuration[key];
        if (string.IsNullOrWhiteSpace(value))
        {
            var envName = key.Contains(':', StringComparison.Ordinal)
                ? key.Replace(":", "__", StringComparison.Ordinal)
                : key;

            throw new InvalidOperationException(
                $"The required configuration '{key}' is missing or empty. "
                + $"Set it via the environment variable '{envName}'.");
        }

        return value;
    }

    public static string GetString(this IConfiguration configuration, string key, string defaultValue)
    {
        return configuration[key] ?? defaultValue;
    }

    public static int GetInt(this IConfiguration configuration, string key, int defaultValue)
    {
        var value = configuration[key];
        return int.TryParse(value, out var parsed) ? parsed : defaultValue;
    }

    public static int GetRequiredInt(this IConfiguration configuration, string key)
    {
        var value = GetRequiredString(configuration, key);
        if (int.TryParse(value, out var parsed))
        {
            return parsed;
        }

        var envName = key.Replace(":", "__", StringComparison.Ordinal);
        throw new InvalidOperationException(
            $"The required configuration '{key}' is not a valid integer. "
            + $"Set it via the environment variable '{envName}'.");
    }
}
