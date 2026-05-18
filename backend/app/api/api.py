import fastapi

api_router = fastapi.APIRouter()

@api_router.get("/health")
def health_check():
    return {"status":"ok"}