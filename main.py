from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from sqlmodel import SQLModel, Field, Session, select, col
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import date, datetime
from enum import Enum
import time
import jwt
import os
from database import get_session, create_db_and_tables

# -------------------------------------------
# DATA MODELS (The "Cookie Cutters") RE
# -------------------------------------------

# Enums: Restricting values to a specific set
class ListStatus(str, Enum):
    ACTIVE = "Active"
    DEFERRED = "Deferred"
    DELETED = "Deleted"

class TaskStatus(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In-Progress"
    COMPLETED = "Completed"
    DEFERRED = "Deferred"
    DELETED = "Deleted"

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

# Schemas: Defining the shape of our data objects

class ToDoList(SQLModel, table=True):
    # System fields (readOnly in YAML) are Optional here so we don't have to send them when creating
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[str] = Field(default=None, index=True)
    title: str
    description: Optional[str] = None
    status: ListStatus = Field(default=ListStatus.ACTIVE)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        # This tells Pydantic to treat Enums as strings
        use_enum_values = True

class ToDoListUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ListStatus] = None

    class Config:
        use_enum_values = True

class Task(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    list_id: Optional[UUID] = Field(default=None, foreign_key="todolist.id", index=True)
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.NEW)
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None

    class Config:
        use_enum_values = True

class Client(SQLModel, table=True):
    client_id: str = Field(primary_key=True)
    client_secret: str # In a real production app, this should be hashed!
    name: str

class Error(SQLModel):
    code: int
    message: str
    details: Optional[List] = None

# 1. Initialize the API
# This creates the application instance.

class TokenRequest(SQLModel):
    client_id: str
    client_secret: str

class TokenResponse(SQLModel):
    access_token: str
    token_type: str
    expires_in: int

app = FastAPI(
    title="To-Do List API (Cloud)",
    description="A simple API for managing task lists",
    version="1.1.0"
)

# CORS Configuration (Allows the world to talk to your API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello World", "status": "System is Online"}

@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    try:
        create_db_and_tables()
    except Exception as e:
        print("\n\n" + "="*60)
        print("❌ DATABASE CONNECTION FAILED")
        print("="*60)
        print(f"Error Details: {e}")
        print("\n💡 COMMON FIXES:")
        print("1. Check Supabase Dashboard: Is your project PAUSED?")
        print("2. Check .env: Is the DATABASE_URL correct?")
        print("3. Check Network: Are you on a VPN blocking the connection?")
        print("="*60 + "\n")
        raise e

# -------------------------------------------
# EXCEPTION HANDLERS
# -------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"code": 400, "message": "Validation Error", "details": exc.errors()}),
    )

# -------------------------------------------
# MIDDLEWARE
# -------------------------------------------

# Rate Limiting Configuration
RATE_LIMIT_DURATION = 60  # seconds
RATE_LIMIT_REQUESTS = 100
request_counts = {}  # Stores request timestamps per IP

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Initialize if new client
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    
    # Clean up old timestamps (keep only those within the window)
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < RATE_LIMIT_DURATION]
    
    # Check if limit exceeded
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"code": 429, "message": "Too Many Requests", "details": "Rate limit exceeded"},
            headers={"Retry-After": str(RATE_LIMIT_DURATION)}
        )
    
    # Record current request
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

# -------------------------------------------
# DEPENDENCIES (Reusable Logic)
# -------------------------------------------

# Security Scheme
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extracts the Bearer Token and treats it as the User ID."""
    token = credentials.credentials
    secret = os.getenv("SUPABASE_JWT_SECRET")
    
    try:
        # Decode and verify the JWT signature using Supabase's secret
        # options={"verify_aud": False} allows us to skip audience check for simplicity
        payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_aud": False})
        return payload.get("sub") # 'sub' is the User ID in Supabase
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_valid_list(list_id: UUID, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)) -> ToDoList:
    """Dependency to find and validate a parent list."""
    parent_list = session.get(ToDoList, list_id)

    if not parent_list or parent_list.status == ListStatus.DELETED:
        raise HTTPException(status_code=404, detail="Parent List not found")
    
    # Authorization Check
    if parent_list.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    return parent_list

# -------------------------------------------
# ENDPOINTS
# -------------------------------------------

@app.post("/v1/auth/token", response_model=TokenResponse, tags=["Auth"])
def login_for_access_token(request: TokenRequest, session: Session = Depends(get_session)):
    """
    Standard Client Credentials Flow.
    Exchanges Client ID + Secret for a short-lived Access Token.
    """
    # 1. Find Client
    client = session.get(Client, request.client_id)
    if not client or client.client_secret != request.client_secret:
        raise HTTPException(status_code=401, detail="Invalid client_id or client_secret")
    
    # 2. Generate Token
    now = int(time.time())
    expires_in = 3600 * 24 # 1 day validity
    
    payload = {
        "sub": client.client_id,
        "role": "authenticated",
        "exp": now + expires_in
    }
    
    secret = os.getenv("SUPABASE_JWT_SECRET")
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    return {"access_token": token, "token_type": "bearer", "expires_in": expires_in}

@app.post("/v1/auth/clients", response_model=Client, tags=["Auth"])
def register_client(client: Client, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    """Register a new third-party client (Protected by your Master Token)."""
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@app.post("/v1/lists", response_model=ToDoList, status_code=201, tags=["Lists"])
def create_list(todo_list: ToDoList, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    # 1. Set system fields
    todo_list.user_id = user_id
    
    # 2. Save to Database
    session.add(todo_list)
    session.commit()
    session.refresh(todo_list)
    
    return todo_list

@app.get("/v1/lists", response_model=List[ToDoList], tags=["Lists"])
def get_lists(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Query: Select * From ToDoList Where user_id = X AND status != Deleted
    query = select(ToDoList).where(
        ToDoList.user_id == user_id, 
        ToDoList.status != ListStatus.DELETED
    )
    start = (page - 1) * limit
    results = session.exec(query.offset(start).limit(limit)).all()
    return results

@app.get("/v1/lists/{id}", response_model=ToDoList, tags=["Lists"])
def get_list(id: UUID, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    # We use get_valid_list logic here manually or just query directly
    todo_list = session.get(ToDoList, id)
    
    if not todo_list or todo_list.status == ListStatus.DELETED:
        raise HTTPException(status_code=404, detail="List not found")
        
    if todo_list.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
        
    return todo_list

@app.patch("/v1/lists/{id}", response_model=ToDoList, tags=["Lists"])
def update_list(id: UUID, list_update: ToDoListUpdate, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    # 1. Fetch existing list
    db_list = session.get(ToDoList, id)
    if not db_list or db_list.status == ListStatus.DELETED:
        raise HTTPException(status_code=404, detail="List not found")
    
    if db_list.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    # 2. Business Rule: Cannot defer a list with In-Progress tasks.
    if list_update.status == ListStatus.DEFERRED:
        # Query: Select * From Task Where list_id = X AND status = 'In-Progress'
        active_task = session.exec(select(Task).where(
            Task.list_id == id, 
            Task.status == TaskStatus.IN_PROGRESS
        )).first()
        
        if active_task:
            raise HTTPException(status_code=409, detail="Cannot defer list with 'In-Progress' tasks")

    # 3. Update fields
    try:
        update_data = list_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_list, key, value)
        db_list.updated_at = datetime.now()
        
        session.add(db_list)
        session.commit()
        session.refresh(db_list)
        return db_list
    except Exception as e:
        session.rollback()
        print(f"❌ Database Error: {e}")
        raise HTTPException(status_code=500, detail=f"Database Update Failed: {str(e)}")

@app.delete("/v1/lists/{id}", status_code=204, tags=["Lists"])
def delete_list(id: UUID, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    db_list = session.get(ToDoList, id)
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
        
    if db_list.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    if db_list.status != ListStatus.DELETED:
        # Business Rule: Cannot delete list with active tasks.
        active_task = session.exec(select(Task).where(
            Task.list_id == id,
            col(Task.status).in_([TaskStatus.NEW, TaskStatus.IN_PROGRESS])
        )).first()
        
        if active_task:
            raise HTTPException(status_code=409, detail="Cannot delete list with active tasks")

        db_list.status = ListStatus.DELETED
        db_list.updated_at = datetime.now()
        session.add(db_list)
        session.commit()
    
    return

@app.post("/v1/lists/{list_id}/tasks", response_model=Task, status_code=201, tags=["Tasks"])
def create_task(task: Task, parent_list: ToDoList = Depends(get_valid_list), session: Session = Depends(get_session)):
    # 1. Validate Parent List (Handled by dependency)
    if parent_list.status == ListStatus.DEFERRED:
        raise HTTPException(status_code=409, detail="Cannot add tasks to a Deferred list")

    # 2. Set system fields
    task.list_id = parent_list.id  # Link the task to the parent list
    
    # 3. Save to Database
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return task

@app.get("/v1/lists/{list_id}/tasks", response_model=List[Task], tags=["Tasks"])
def get_tasks(
    parent_list: ToDoList = Depends(get_valid_list),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session)
):
    # Query: Select * From Task Where list_id = X AND status != Deleted
    query = select(Task).where(
        Task.list_id == parent_list.id,
        Task.status != TaskStatus.DELETED
    )
    start = (page - 1) * limit
    return session.exec(query.offset(start).limit(limit)).all()

@app.get("/v1/lists/{list_id}/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def get_task(task_id: UUID, parent_list: ToDoList = Depends(get_valid_list), session: Session = Depends(get_session)):
    # Parent list is already validated by dependency
    task = session.get(Task, task_id)
    
    if not task or task.list_id != parent_list.id or task.status == TaskStatus.DELETED:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task

@app.patch("/v1/lists/{list_id}/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def update_task(task_id: UUID, task_update: TaskUpdate, parent_list: ToDoList = Depends(get_valid_list), session: Session = Depends(get_session)):
    # 1. Validate Parent List (Handled by dependency)
    if parent_list.status == ListStatus.DEFERRED:
        raise HTTPException(status_code=409, detail="Cannot update tasks in a Deferred list")

    # 2. Find and Update Task
    task = session.get(Task, task_id)
    if not task or task.list_id != parent_list.id or task.status in [TaskStatus.DELETED, TaskStatus.DEFERRED]:
        raise HTTPException(status_code=404, detail="Task not found")

    # 3. Get update data and validate business rules
    update_data = task_update.dict(exclude_unset=True)

    # Business Rule: Cannot revert task status to 'New' (Story 10)
    if "status" in update_data and update_data["status"] == TaskStatus.NEW:
        raise HTTPException(status_code=400, detail="Cannot revert task status to 'New'")
    
    # 4. Apply updates
    try:
        for key, value in update_data.items():
            setattr(task, key, value)
        task.updated_at = datetime.now()

        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception as e:
        session.rollback()
        print(f"❌ Database Error: {e}")
        raise HTTPException(status_code=500, detail=f"Database Update Failed: {str(e)}")

@app.delete("/v1/lists/{list_id}/tasks/{task_id}", status_code=204, tags=["Tasks"])
def delete_task(task_id: UUID, parent_list: ToDoList = Depends(get_valid_list), session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    
    if not task or task.list_id != parent_list.id:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status != TaskStatus.DELETED:
        task.status = TaskStatus.DELETED
        task.updated_at = datetime.now()
        session.add(task)
        session.commit()
    
    return