from fastapi import FastAPI

app = FastAPI(title="SlideGen AI")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
