from fastapi import FastAPI, Depends, Form, Request, status

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("index.html", {"request": request, "todos": db.query(models.Todo).all()})


@app.post("/add")
async def add_todo(request: Request, title: str = Form(...), db: Session = Depends(get_db)):
    todo = models.Todo(title=title)
    db.add(todo)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/update/{todo_id}")
async def update_todo(todo_id: int, request: Request, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.done = not todo.done
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/delete/{todo_id}")
async def delete_todo(todo_id: int, request: Request, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
