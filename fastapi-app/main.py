import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
TODO_FILE = BASE_DIR / "todo.json"
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app = FastAPI(title="Todo List")


class TodoIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    completed: bool = False


class TodoItem(TodoIn):
    id: int


def ensure_todo_file() -> None:
    if not TODO_FILE.exists():
        TODO_FILE.write_text("[]", encoding="utf-8")


def read_todos() -> list[dict]:
    ensure_todo_file()
    try:
        data = json.loads(TODO_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=500, detail="todo.json 파일 형식이 올바르지 않습니다.") from error
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="todo.json은 배열 형식이어야 합니다.")
    return data


def write_todos(todos: list[dict]) -> None:
    TODO_FILE.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/todos", response_model=list[TodoItem])
def list_todos():
    # 이전 버전의 데이터에 description이 없어도 화면에서 정상 표시한다.
    return [{"description": "", **item} for item in read_todos()]


@app.post("/todos", response_model=TodoItem, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoIn):
    todos = read_todos()
    next_id = max((item.get("id", 0) for item in todos), default=0) + 1
    new_todo = {"id": next_id, **todo.model_dump()}
    todos.append(new_todo)
    write_todos(todos)
    return new_todo


@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo: TodoIn):
    todos = read_todos()
    for index, item in enumerate(todos):
        if item.get("id") == todo_id:
            updated_todo = {"id": todo_id, **todo.model_dump()}
            todos[index] = updated_todo
            write_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다.")


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    todos = read_todos()
    remaining_todos = [item for item in todos if item.get("id") != todo_id]
    if len(remaining_todos) == len(todos):
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다.")
    write_todos(remaining_todos)
