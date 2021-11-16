from fastapi import FastAPI
from routes.user import user

app = FastAPI(
    title = "Python FastAPI and MySQL",
    description = "Uploaded to GitHub",
    openapi_tags= [{
         "name": "users",
         "description": "users routes" 
    }]
)

app.include_router(user)