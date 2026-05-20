import fastapi
from app.api.v1.endpoints import auth,users,plants,care,gallery


api_router = fastapi.APIRouter()

@api_router.get("/health")
def health_check():
    return {"status":"ok"}


api_router.include_router(
    auth.router,
    prefix="/auth",
    tags =["Auth"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)


api_router.include_router(
    plants.router,
    prefix="/plants",
    tags= ["Plants"]
)

api_router.include_router(
    care.router,
    prefix="/care",
    tags=["Care"]
)

api_router.include_router(
    gallery.router,
    prefix="/gallery",
    tags= ["Gallery"]
)