import uvicorn
from fastapi import FastAPI

from app.api.router import router as main_router

app = FastAPI()

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
