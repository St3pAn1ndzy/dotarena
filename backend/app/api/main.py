import uuid

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import router as main_router
from app.core.exceptions import BattleError
from app.core.logging import logger, set_request_id, setup_logging

setup_logging()

app = FastAPI()


@app.exception_handler(BattleError)
async def battle_error_handler(request, exc: BattleError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логгирует входящие запросы и время их обработки."""
    request_id = str(uuid.uuid4())[:8]
    set_request_id(request_id)

    logger.info(
        "→ {method} {path}",
        method=request.method,
        path=request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(
            "Ошибка при обработке {path}: {error}",
            path=request.url.path,
            error=e,
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    response.headers["X-Request-ID"] = request_id

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
