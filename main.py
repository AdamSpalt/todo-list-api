from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import date, datetime
from enum import Enum
import time

# -------------------------------------------
# DATA MODELS (The "Cookie Cutters")
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

class ToDoList(BaseModel):
    # System fields (readOnly in YAML) are Optional here so we don't have to send them when creating
    id: Optional[UUID] = None
    user_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: ListStatus = ListStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        # This tells Pydantic to treat Enums as strings
        use_enum_values = True

class Task(BaseModel):
    id: Optional[UUID] = None
    list_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.NEW
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True

class Error(BaseModel):
    code: int
    message: str
    details: Optional[List] = None

# 1. Initialize the API
# This creates the application instance.
app = FastAPI(
    title="To-Do List API",
    description="A simple API for managing task lists",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Hello World", "status": "System is Online"}

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
        status_code=422,
        content={"code": 422, "message": "Validation Error", "details": exc.errors()},
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
# FAKE DATABASE
# -------------------------------------------
db_lists = []
db_tasks = []

# -------------------------------------------
# DEPENDENCIES (Reusable Logic)
# -------------------------------------------

# Security Scheme
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extracts the Bearer Token and treats it as the User ID."""
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return token

def get_valid_list(list_id: UUID, user_id: str = Depends(get_current_user)) -> ToDoList:
    """Dependency to find and validate a parent list."""
    parent_list = None
    for l in db_lists:
        if l.id == list_id:
            parent_list = l
            break
            
    if not parent_list or parent_list.status == ListStatus.DELETED:
        raise HTTPException(status_code=404, detail="Parent List not found")
    
    # Authorization Check
    if parent_list.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    return parent_list

# -------------------------------------------
# ENDPOINTS
# -------------------------------------------
@app.post("/v1/lists", response_model=ToDoList, status_code=201, tags=["Lists"])
def create_list(todo_list: ToDoList, user_id: str = Depends(get_current_user)):
    # 1. Generate system fields
    todo_list.id = uuid4()
    todo_list.user_id = user_id
    todo_list.created_at = datetime.now()
    todo_list.updated_at = datetime.now()
    
    # 2. Save to "Database"
    db_lists.append(todo_list)
    
    return todo_list

@app.get("/v1/lists", response_model=List[ToDoList], tags=["Lists"])
def get_lists(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user)
):
    # Return all lists that are NOT marked as 'Deleted'
    active_lists = [l for l in db_lists if l.status != ListStatus.DELETED and l.user_id == user_id]
    start = (page - 1) * limit
    return active_lists[start : start + limit]

@app.get("/v1/lists/{id}", response_model=ToDoList, tags=["Lists"])
def get_list(id: UUID, user_id: str = Depends(get_current_user)):
    # Find the list with the matching ID
    for l in db_lists:
        if l.id == id and l.status != ListStatus.DELETED:
            if l.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to access this resource")
            return l
    
    # If we finish the loop and find nothing, throw a 404 error
    raise HTTPException(status_code=404, detail="List not found")

@app.patch("/v1/lists/{id}", response_model=ToDoList, tags=["Lists"])
def update_list(id: UUID, list_update: ToDoList, user_id: str = Depends(get_current_user)):
    for l in db_lists:
        if l.id == id and l.status != ListStatus.DELETED:
            if l.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to access this resource")

            # Business Rule: Cannot defer a list with In-Progress tasks.
            if list_update.status == ListStatus.DEFERRED:
                for task in db_tasks:
                    if task.list_id == id and task.status == TaskStatus.IN_PROGRESS:
                        raise HTTPException(
                            status_code=409, 
                            detail="Cannot defer list with 'In-Progress' tasks"
                        )

            l.title = list_update.title
            l.description = list_update.description
            l.status = list_update.status
            l.updated_at = datetime.now()
            return l
            
    raise HTTPException(status_code=404, detail="List not found")

@app.delete("/v1/lists/{id}", status_code=204, tags=["Lists"])
def delete_list(id: UUID, user_id: str = Depends(get_current_user)):
    for l in db_lists:
        if l.id == id:
            if l.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to access this resource")

            # If the list is found, we will return success (idempotency).
            # Only update it if it's not already deleted.
            if l.status != ListStatus.DELETED:
                # Business Rule: Cannot delete list with active tasks.
                for t in db_tasks:
                    if t.list_id == id and t.status in [TaskStatus.NEW, TaskStatus.IN_PROGRESS]:
                        raise HTTPException(
                            status_code=409, 
                            detail="Cannot delete list with active tasks"
                        )

                l.status = ListStatus.DELETED
                l.updated_at = datetime.now()
            return
            
    raise HTTPException(status_code=404, detail="List not found")

@app.post("/v1/lists/{list_id}/tasks", response_model=Task, status_code=201, tags=["Tasks"])
def create_task(task: Task, parent_list: ToDoList = Depends(get_valid_list)):
    # 1. Validate Parent List (Handled by dependency)
    # If list is Deferred, we cannot add new tasks (Business Rule)
    if parent_list.status == ListStatus.DEFERRED:
        raise HTTPException(status_code=409, detail="Cannot add tasks to a Deferred list")

    # 2. Generate system fields
    task.id = uuid4()
    task.list_id = parent_list.id  # Link the task to the parent list
    task.created_at = datetime.now()
    task.updated_at = datetime.now()
    
    # 3. Save to "Database"
    db_tasks.append(task)
    
    return task

@app.get("/v1/lists/{list_id}/tasks", response_model=List[Task], tags=["Tasks"])
def get_tasks(
    parent_list: ToDoList = Depends(get_valid_list),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    # 1. Validate Parent List (Handled by dependency)
    # 2. Return tasks for this list
    list_tasks = [t for t in db_tasks if t.list_id == parent_list.id and t.status != TaskStatus.DELETED]
    start = (page - 1) * limit
    return list_tasks[start : start + limit]

@app.get("/v1/lists/{list_id}/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def get_task(task_id: UUID, parent_list: ToDoList = Depends(get_valid_list)):
    # 1. Validate Parent List (Handled by dependency)
    # 2. Find the Task
    for t in db_tasks:
        if t.id == task_id and t.list_id == parent_list.id and t.status != TaskStatus.DELETED:
            return t
            
    raise HTTPException(status_code=404, detail="Task not found")

@app.patch("/v1/lists/{list_id}/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def update_task(task_id: UUID, task_update: Task, parent_list: ToDoList = Depends(get_valid_list)):
    # 1. Validate Parent List (Handled by dependency)
    if parent_list.status == ListStatus.DEFERRED:
        raise HTTPException(status_code=409, detail="Cannot update tasks in a Deferred list")

    # 2. Find and Update Task
    for t in db_tasks:
        if t.id == task_id and t.list_id == parent_list.id:
            if t.status == TaskStatus.DELETED:
                break
            
            # Business Rule: Cannot revert task status to 'New'
            if task_update.status == TaskStatus.NEW and t.status != TaskStatus.NEW:
                raise HTTPException(status_code=400, detail="Cannot revert task status to 'New'")
            
            t.title = task_update.title
            t.description = task_update.description
            t.status = task_update.status
            t.priority = task_update.priority
            t.due_date = task_update.due_date
            t.updated_at = datetime.now()
            return t
            
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/v1/lists/{list_id}/tasks/{task_id}", status_code=204, tags=["Tasks"])
def delete_task(task_id: UUID, parent_list: ToDoList = Depends(get_valid_list)):
    # 1. Validate Parent List (Handled by dependency)
    # 2. Find and Soft-Delete Task
    for t in db_tasks:
        if t.id == task_id and t.list_id == parent_list.id:
            # If the task is found, we will return success (idempotency).
            # Only update it if it's not already deleted.
            if t.status != TaskStatus.DELETED:
                t.status = TaskStatus.DELETED
                t.updated_at = datetime.now()
            return
            
    raise HTTPException(status_code=404, detail="Task not found")