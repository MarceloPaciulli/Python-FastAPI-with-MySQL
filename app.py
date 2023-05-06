from fastapi import FastAPI
from routes.user import user
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title = "Python FastAPI and MySQL",
    description = "Upload to GitHub - Renaiss AI",
    openapi_tags= [{
         "name": "users",
         "description": "users routes with chats" 
    }]
)

# Configurar los dominios permitidos para las solicitudes CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

# Agregar los encabezados CORS a las respuestas
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(user)