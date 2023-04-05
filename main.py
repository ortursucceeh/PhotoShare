import uvicorn
from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from src.database.connect_db import get_db
from src.routes.auth import router as auth_router
from src.routes.posts import router as post_router
from src.routes.transform_post import router as trans_router
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello PhotoShare"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth_router, prefix='/api')
app.include_router(post_router, prefix='/api')
app.include_router(trans_router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='localhost', port=8000)
