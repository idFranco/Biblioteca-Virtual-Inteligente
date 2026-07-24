from fastapi import FastAPI

app = FastAPI(title="Biblioteca Virtual Chatbot")


@app.get("/health")
def health():
    return {"status": "healthy"}
