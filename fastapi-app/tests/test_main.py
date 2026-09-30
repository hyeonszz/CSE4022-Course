import pytest
from fastapi.testclient import TestClient

import main
from main import app, read_todos, write_todos, TodoItem

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown(tmp_path, monkeypatch):
    # 실제 todo.json 대신 테스트마다 새 임시 파일 사용 (본인 데이터 보호 + 테스트 간 격리)
    monkeypatch.setattr(main, "TODO_FILE", tmp_path / "todo.json")
    write_todos([])  # 테스트 전 초기화
    yield
    # 테스트 후 정리: tmp_path 와 monkeypatch 가 자동으로 원상 복구


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200


def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_get_todos_with_items():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    write_todos([todo.model_dump()])
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test"


def test_create_todo():
    todo = {"title": "Test", "description": "Test description", "completed": False}  # id 는 보내지 않음
    response = client.post("/todos", json=todo)
    assert response.status_code == 201            # 생성 성공 = 201 Created
    assert response.json()["title"] == "Test"
    assert response.json()["id"] == 1             # id 는 서버가 부여
    assert len(read_todos()) == 1                  # 파일에도 저장됐는지 확인


def test_create_todo_invalid():
    todo = {"description": "Test description"}    # 필수 필드 title 누락
    response = client.post("/todos", json=todo)
    assert response.status_code == 422


def test_update_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    write_todos([todo.model_dump()])
    updated_todo = {"title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_update_todo_not_found():
    updated_todo = {"title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 404


def test_delete_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    write_todos([todo.model_dump()])
    response = client.delete("/todos/1")
    assert response.status_code == 204             # 삭제 성공 = 204 No Content (응답 본문 없음)
    assert read_todos() == []


def test_delete_todo_not_found():
    response = client.delete("/todos/1")
    assert response.status_code == 404
