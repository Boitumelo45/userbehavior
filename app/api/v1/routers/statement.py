from fastapi import APIRouter
from app.db.database import conn

router = APIRouter()

@router.get("/statement/")
async def get_statement():
    result = conn.execute("SELECT * FROM statements").fetchall()
    return {"statement": result}
