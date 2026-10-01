from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get(
    "/health",
    summary="Check service health",
    description="Verifies that the API process is running and the database connection works.",
    response_description="Service and database health status.",
    responses={
        200: {
            "content": {
                "application/json": {"example": {"status": "ok", "service": "hse-delivery-service"}}
            }
        }
    },
)
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "service": "hse-delivery-service"}
