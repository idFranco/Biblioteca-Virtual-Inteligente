namespace BibliotecaVirtual.Application.Common;

public sealed class ResourceAlreadyExistsException : Exception
{
    public ResourceAlreadyExistsException(string message) : base(message)
    {
    }
}