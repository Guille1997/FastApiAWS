from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import users
app = FastAPI()

origins = [
    "http://localhost:3000",  # Suponiendo que el frontend corre en localhost puerto 3000
    "https://cosmic-cat-b91a36.netlify.app",
    "https://6631b57134aa6973b162dd4b--cosmic-cat-b91a36.netlify.app",
    "https://sensational-maamoul-6b9ca1.netlify.app"
]


app.include_router(users.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Dominios/origenes que pueden hacer solicitudes
    allow_credentials=True,  # Permite cookies
    allow_methods=["*"],  # Métodos permitidos
    allow_headers=["*"],  # Encabezados permitidos
)