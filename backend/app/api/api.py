import fastapi
from app.api.v1.endpoints import auth


api_router = fastapi.APIRouter()

@api_router.get("/health")
def health_check():
    return {"status":"ok"}


api_router.include_router(
    auth.router,
    prefix="/auth",
    tags =["Auth"]
)


