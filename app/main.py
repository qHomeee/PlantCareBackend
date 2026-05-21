import fastapi
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from fastapi.staticfiles import StaticFiles
from app.models import Plant, User, UserPlant, WateringEvent
from app.core.database import Base,engine


Base.metadata.create_all(bind= engine)

app = fastapi.FastAPI(
    title=settings.APP_NAME,
    version = settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
app.include_router(api_router,prefix=settings.API_V1_PREFIX)



@app.get("/")
def root():
    return{
        "message": "PlantCare API is running",
        "docs": "/docs",
    }