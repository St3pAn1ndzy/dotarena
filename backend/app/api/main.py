import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import router as main_router
from app.core.logging import logger, setup_logging

setup_logging()

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логгирует входящие запросы и время их обработки."""
    logger.info(
        "→ {method} {path}",
        method=request.method,
        path=request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception("Ошибка при обработке {path}: {error}", path=request.url.path, error=e)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    logger.info(
        "← {method} {path} — {status}",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    )

    return response


app.include_router(main_router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)