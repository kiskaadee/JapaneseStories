from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from config.database import
from config.system import settings


def create_app():
    app = FastAPI(title=settings.PROJECT_NAME,
                  version=settings.PROJECT_VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    # routers

    return app


app = create_app()


@app.get("/")
async def root():
    return {"message": "Server is running"}
