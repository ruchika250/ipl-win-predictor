from api import app, MatchData, predict_win_probability
from db import SessionLocal, User

from fastapi.security import HTTPBearer
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from datetime import timedelta, datetime
from typing import Optional
from jose import jwt

import hashlib
from passlib.context import CryptContext

# =========================
# Configurations
# =========================
SECRET_KEY = "sample key"  # change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# =========================
# Password Hashing (bcrypt-safe)
# =========================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

def _prehash(password: str) -> str:
    # Pre-hash to avoid bcrypt 72-byte limit
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash(password))

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_prehash(plain), hashed)

# =========================
# User Models
# =========================
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# =========================
# JWT Helpers
# =========================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

# =========================
# Auth Logic
# =========================
def auth_user(username: str, password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user
    finally:
        db.close()

# =========================
# Auth Endpoints
# =========================
@app.post("/register", response_model=TokenResponse)
async def register_user(user: UserRegister):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == user.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        new_user = User(
            username=user.username,
            password_hash=hash_password(user.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    finally:
        db.close()

    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expire
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/login", response_model=TokenResponse)
async def user_login(user_cred: UserLogin):
    user = auth_user(user_cred.username, user_cred.password)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_cred.username},
        expires_delta=access_token_expire
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# =========================
# Prediction Models
# =========================
class PredictionResponse(BaseModel):
    batting_team: str
    bowling_team: str
    win_probability: float
    loss_probability: float

class AuthenticatedPredictionRequest(BaseModel):
    customer: MatchData

# =========================
# Protected Prediction Endpoint
# =========================
@app.post("/predict/auth", response_model=PredictionResponse, dependencies=[Depends(security)])
async def predict_auth(
    request: AuthenticatedPredictionRequest,
    credentials=Depends(security)
):
    username = verify_token(credentials.credentials)
    print(f"User {username} accessed the prediction endpoint")

    result = predict_win_probability(request.customer)

    return {
        "batting_team": request.customer.batting_team,
        "bowling_team": request.customer.bowling_team,
        "win_probability": result["win_probability"],
        "loss_probability": result["loss_probability"],
    }
