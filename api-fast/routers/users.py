from fastapi import APIRouter, HTTPException, Depends, status, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models import User, UserLogin
from dependencies import get_db
from passlib.context import CryptContext
from jose import jwt, JWTError
import datetime
import httpx


router = APIRouter()
security = HTTPBearer()
# Configuración del hasher y del token
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "tu_clave_secreta_jwt"
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: HTTPAuthorizationCredentials = Security(security), db=Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")

    cursor = db.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE username = %s", (username,))
    user_record = cursor.fetchone()
    cursor.close()
    db.close()

    if user_record is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_id, username, email = user_record
    access_token = create_access_token(data={"sub": username})
    return {"user": {"id": user_id, "username": username, "email": email}, "access_token": access_token, "token_type": "bearer"}


@router.post("/register/")
async def register_user(user: User, db=Depends(get_db)):
    cursor = db.cursor()
    hashed_password = get_password_hash(user.password)
    try:
        query = "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)"
        cursor.execute(query, (user.username, user.email, hashed_password))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error registering user: {e}")
    finally:
        cursor.close()
        db.close()
    return {"username": user.username, "email": user.email, "message": "User registered successfully"}


@router.post("/login/")
async def login(user: UserLogin, db=Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT id, username, email, hashed_password FROM users WHERE email = %s"
    cursor.execute(query, (user.email,))
    user_record = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    user_id, username, email, hashed_password = user_record
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    access_token = create_access_token(data={"sub": username})
    return {"user": {"username": username, "email": email}, "access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/")
async def read_user_me(user: dict = Depends(get_current_user)):
    return user



@router.get("/institutions/")
async def get_institutions(user: dict = Depends(get_current_user)):
    # Obtener el token de acceso del usuario actual
    
    
    # Configurar la URL de la API de Belvo Sandbox
    belvo_sandbox_api_url = "https://sandbox.belvo.com/api/institutions/"
    
    # Configurar las credenciales de la API de Belvo Sandbox
    username = "e55216de-3b98-4132-af24-32b0ea16f932"
    password = "2l-5#fVKEw4xkSQKYqAp@v2wlnrOFOFQtRoxGx1EsfFm8MEVBRHPjiVhpqS7Cz3x"
    
    try:
        # Realizar la solicitud GET a la API de Belvo Sandbox
        async with httpx.AsyncClient(auth=(username, password)) as client:
            response = await client.get(belvo_sandbox_api_url)
            response.raise_for_status()  # Lanzar una excepción si hay un error en la solicitud

            # Convertir la respuesta JSON en un diccionario Python
            institutions_data = response.json()
            return institutions_data
    except httpx.HTTPError as e:
        # Manejar errores de solicitud HTTP
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


