# backend/app.py
import os, uuid, json, datetime, logging, traceback
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field, conint, confloat
from jose import jwt, JWTError
from passlib.hash import pbkdf2_sha256          # ⟵ dùng PBKDF2-SHA256, bỏ bcrypt
from sqlalchemy import create_engine, text
import pandas as pd, joblib

from personalize import personalize_recommendations

# ---------- Config ----------
SECRET = os.getenv("SECRET", "change_me")
ALGO = "HS256"
ACCESS_EXPIRE_MIN = int(os.getenv("ACCESS_EXPIRE_MIN", "60"))
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
MODEL_PATH = os.getenv("MODEL_PATH", "models/best_model_calibrated.pkl")
META_PATH = os.getenv("META_PATH", "models/meta.json")
DEFAULT_THRESHOLD = float(os.getenv("DEFAULT_THRESHOLD", "0.5"))
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

# App
app = FastAPI(title="Heart Risk API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
)

with engine.begin() as conn:
    conn.execute(text("""
      CREATE TABLE IF NOT EXISTS users(
        id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, name TEXT, created_at TEXT
      )
    """))
    conn.execute(text("""
      CREATE TABLE IF NOT EXISTS history(
        id TEXT PRIMARY KEY, user_id TEXT, timestamp TEXT,
        model_name TEXT, model_version TEXT, probability REAL, pred_label INTEGER,
        features_json TEXT, top_features_json TEXT, recommendations_json TEXT
      )
    """))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_hist_user_time ON history(user_id, timestamp)"))

# Model loading 
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Model file not found: {MODEL_PATH}")
pipe = joblib.load(MODEL_PATH)
if os.path.exists(META_PATH):
    meta = json.load(open(META_PATH))
    THRESH = float(meta.get("threshold", DEFAULT_THRESHOLD))
    MODEL_NAME = str(meta.get("model_name", "best_calibrated"))
else:
    THRESH = DEFAULT_THRESHOLD
    MODEL_NAME = "best_calibrated"
logger.info("Model loaded name=%s version=%s threshold=%.3f", MODEL_NAME, MODEL_VERSION, THRESH)

#  Auth helpers 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_pw(p: str) -> str:           
    return pbkdf2_sha256.hash(p)

def verify_pw(p: str, h: str) -> bool:
    return pbkdf2_sha256.verify(p, h)

def create_access_token(user_id: str, minutes: int = ACCESS_EXPIRE_MIN) -> str:
    payload = {"sub": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def get_user_by_email(email: str):
    with engine.begin() as c:
        return c.execute(text("SELECT * FROM users WHERE email=:e"), {"e": email}).first()

def get_user_by_id(uid: str):
    with engine.begin() as c:
        return c.execute(text("SELECT * FROM users WHERE id=:i"), {"i": uid}).first()

def current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        uid = payload.get("sub")
        if not uid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    u = get_user_by_id(uid)
    if not u:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return u

#  Schemas 
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=256)
    name: Optional[str] = None

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class FeaturesIn(BaseModel):
    age: conint(ge=1, le=120) # type: ignore
    sex: conint(ge=0, le=1) # type: ignore
    cp: conint(ge=0, le=3) # type: ignore
    trestbps: conint(ge=60, le=300) # type: ignore
    chol: conint(ge=50, le=800) # type: ignore
    fbs: conint(ge=0, le=1) # type: ignore
    restecg: conint(ge=0, le=2) # type: ignore
    thalach: conint(ge=50, le=250) # type: ignore
    exang: conint(ge=0, le=1) # type: ignore
    oldpeak: confloat(ge=0.0, le=10.0) # type: ignore
    slope: conint(ge=0, le=2) # type: ignore
    ca: conint(ge=0, le=3) # type: ignore
    thal: conint(ge=0, le=7) # type: ignore

class PredictIn(BaseModel):
    features: FeaturesIn

#  Routes 
@app.get("/", response_class=HTMLResponse)
def root():
    return "<h3>Heart Risk API</h3><p>>. Xem <a href='/docs'>/docs</a>.</p>"

@app.get("/healthz")
def healthz():
    return {"status": "ok", "time": datetime.datetime.utcnow().isoformat()}

@app.post("/auth/register")
def register(body: RegisterIn):
    try:
        if get_user_by_email(body.email):
            raise HTTPException(400, "Email đã tồn tại")
        uid = str(uuid.uuid4())
        with engine.begin() as c:
            c.execute(text("""
                INSERT INTO users VALUES(:i,:e,:p,:n,:t)
            """), {
                "i": uid, "e": body.email, "p": hash_pw(body.password),
                "n": body.name, "t": datetime.datetime.utcnow().isoformat()
            })
        return {"access_token": create_access_token(uid), "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Register failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(500, "Internal Server Error")

@app.post("/auth/login")
def login(body: LoginIn):
    try:
        u = get_user_by_email(body.email)
        if not u or not verify_pw(body.password, u.password_hash):
            raise HTTPException(401, "Sai thông tin đăng nhập")
        return {"access_token": create_access_token(u.id), "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(500, "Internal Server Error")

@app.post("/predict")
def predict(body: PredictIn, user = Depends(current_user)):
    try:
        x = body.features.dict()
        df = pd.DataFrame([x])
        proba = float(pipe.predict_proba(df)[:, 1][0])
        pred  = int(proba >= THRESH)
        tier  = "cao" if proba >= 0.66 else ("trung_binh" if proba >= 0.33 else "thấp")
        recs  = personalize_recommendations(x, p=proba, shap_top=None)

        with engine.begin() as c:
            c.execute(text("""
                INSERT INTO history VALUES(:id,:uid,:ts,:mn,:mv,:pb,:pl,:fj,:tj,:rj)
            """),{
                "id": str(uuid.uuid4()), "uid": user.id, "ts": datetime.datetime.utcnow().isoformat(),
                "mn": MODEL_NAME, "mv": MODEL_VERSION,
                "pb": proba, "pl": pred,
                "fj": json.dumps(x, ensure_ascii=False),
                "tj": json.dumps([], ensure_ascii=False),
                "rj": json.dumps(recs, ensure_ascii=False)
            })
        return {"probability": proba, "risk_tier": tier, "label": pred,
                "recommendations": recs, "model_version": MODEL_VERSION}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Predict failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(500, "Internal Server Error")

@app.get("/history")
def history(limit: int = 100, user = Depends(current_user)):
    try:
        with engine.begin() as c:
            rows = c.execute(text("""
                SELECT * FROM history WHERE user_id=:u
                ORDER BY timestamp DESC LIMIT :l
            """), {"u": user.id, "l": limit}).mappings().all()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("History failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(500, "Internal Server Error")
