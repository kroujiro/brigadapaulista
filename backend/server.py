from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import base64
from io import BytesIO

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = "brigada_paulista_secret_key_2025"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Thread(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    author_username: Optional[str] = None  # None for anonymous posts
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reply_count: int = 0
    image_data: Optional[str] = None  # base64 encoded image
    image_filename: Optional[str] = None

class ThreadCreate(BaseModel):
    title: str
    content: str
    author_username: Optional[str] = None
    image_data: Optional[str] = None
    image_filename: Optional[str] = None

class Reply(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str
    content: str
    author_username: Optional[str] = None  # None for anonymous posts
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    image_data: Optional[str] = None  # base64 encoded image
    image_filename: Optional[str] = None

class ReplyCreate(BaseModel):
    content: str
    author_username: Optional[str] = None
    image_data: Optional[str] = None
    image_filename: Optional[str] = None

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "username": username,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("username")
        return username
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def prepare_for_mongo(data):
    if isinstance(data, dict):
        if 'created_at' in data and isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        if 'created_at' in item and isinstance(item['created_at'], str):
            item['created_at'] = datetime.fromisoformat(item['created_at'])
    return item

# Routes
@api_router.get("/")
async def root():
    return {"message": "Brigada Paulista - Por São Paulo Livre!"}

# Authentication routes
@api_router.post("/register")
async def register(user_data: UserCreate):
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    # Create new user
    password_hash = hash_password(user_data.password)
    user = User(username=user_data.username, password_hash=password_hash)
    user_dict = prepare_for_mongo(user.dict())
    await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(user.username)
    
    return {
        "message": "Usuário criado com sucesso",
        "access_token": access_token,
        "username": user.username
    }

@api_router.post("/login")
async def login(credentials: UserLogin):
    # Find user
    user_data = await db.users.find_one({"username": credentials.username})
    if not user_data:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    user_data = parse_from_mongo(user_data)
    user = User(**user_data)
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Create access token
    access_token = create_access_token(user.username)
    
    return {
        "message": "Login realizado com sucesso",
        "access_token": access_token,
        "username": user.username
    }

@api_router.get("/me")
async def get_current_user_info(current_user: Optional[str] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return {"username": current_user}

# Forum routes
@api_router.post("/threads")
async def create_thread(thread_data: ThreadCreate, current_user: Optional[str] = Depends(get_current_user)):
    # If user is logged in, use their username, otherwise allow anonymous
    if current_user:
        thread_data.author_username = current_user
    
    thread = Thread(**thread_data.dict())
    thread_dict = prepare_for_mongo(thread.dict())
    await db.threads.insert_one(thread_dict)
    
    return {"message": "Tópico criado com sucesso", "thread_id": thread.id}

@api_router.get("/threads", response_model=List[Thread])
async def get_threads():
    threads_data = await db.threads.find().sort("created_at", -1).to_list(100)
    threads = []
    for thread_data in threads_data:
        thread_data = parse_from_mongo(thread_data)
        threads.append(Thread(**thread_data))
    return threads

@api_router.get("/threads/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str):
    thread_data = await db.threads.find_one({"id": thread_id})
    if not thread_data:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")
    
    thread_data = parse_from_mongo(thread_data)
    return Thread(**thread_data)

@api_router.post("/threads/{thread_id}/replies")
async def create_reply(thread_id: str, reply_data: ReplyCreate, current_user: Optional[str] = Depends(get_current_user)):
    # Check if thread exists
    thread_data = await db.threads.find_one({"id": thread_id})
    if not thread_data:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")
    
    # If user is logged in, use their username, otherwise allow anonymous
    if current_user:
        reply_data.author_username = current_user
    
    reply = Reply(thread_id=thread_id, **reply_data.dict())
    reply_dict = prepare_for_mongo(reply.dict())
    await db.replies.insert_one(reply_dict)
    
    # Update thread reply count
    await db.threads.update_one(
        {"id": thread_id},
        {"$inc": {"reply_count": 1}}
    )
    
    return {"message": "Resposta criada com sucesso", "reply_id": reply.id}

@api_router.get("/threads/{thread_id}/replies", response_model=List[Reply])
async def get_replies(thread_id: str):
    replies_data = await db.replies.find({"thread_id": thread_id}).sort("created_at", 1).to_list(1000)
    replies = []
    for reply_data in replies_data:
        reply_data = parse_from_mongo(reply_data)
        replies.append(Reply(**reply_data))
    return replies

# Image upload route
@api_router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Read file content
    content = await file.read()
    
    # Convert to base64
    base64_image = base64.b64encode(content).decode('utf-8')
    
    return {
        "image_data": base64_image,
        "filename": file.filename,
        "content_type": file.content_type
    }

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()