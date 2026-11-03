import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Integer, String, Boolean, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL environment variable is required')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

class Base(DeclarativeBase):
    pass

class Todo(Base):
    __tablename__ = 'todos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    completed: bool | None = None

class TodoOut(BaseModel):
    id: int
    title: str
    completed: bool
    model_config = {'from_attributes': True}

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title='Simple TODO API', lifespan=lifespan)
origins = [s.strip() for s in os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',') if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET','POST','PATCH','DELETE'], allow_headers=['Content-Type'])

@app.get('/api/health')
def health():
    return {'status': 'ok'}

@app.get('/api/todos', response_model=list[TodoOut])
def list_todos():
    with Session(engine) as session:
        return session.scalars(select(Todo).order_by(Todo.id.desc())).all()

@app.post('/api/todos', response_model=TodoOut, status_code=201)
def create_todo(data: TodoCreate):
    with Session(engine) as session:
        todo = Todo(title=data.title.strip())
        if not todo.title:
            raise HTTPException(422, 'Title must not be blank')
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

@app.patch('/api/todos/{todo_id}', response_model=TodoOut)
def update_todo(todo_id: int, data: TodoUpdate):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(404, 'Todo not found')
        if data.title is not None:
            todo.title = data.title.strip()
            if not todo.title:
                raise HTTPException(422, 'Title must not be blank')
        if data.completed is not None:
            todo.completed = data.completed
        session.commit()
        session.refresh(todo)
        return todo

@app.delete('/api/todos/{todo_id}', status_code=204)
def delete_todo(todo_id: int):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(404, 'Todo not found')
        session.delete(todo)
        session.commit()
