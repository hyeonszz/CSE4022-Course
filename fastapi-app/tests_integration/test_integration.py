import os

import httpx2

# Jenkins가 Deploy 단계 직후 API_BASE_URL="http://호스트:포트" 로 지정해서 실행한다.
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_crud_flow():
    create_resp = httpx2.post(
        f"{BASE_URL}/todos",
        json={"title": "통합테스트", "description": "e2e", "completed": False},
    )
    assert create_resp.status_code == 201
    todo_id = create_resp.json()["id"]

    list_resp = httpx2.get(f"{BASE_URL}/todos")
    assert list_resp.status_code == 200
    assert any(item["id"] == todo_id for item in list_resp.json())

    update_resp = httpx2.put(
        f"{BASE_URL}/todos/{todo_id}",
        json={"title": "수정됨", "description": "e2e", "completed": True},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "수정됨"

    delete_resp = httpx2.delete(f"{BASE_URL}/todos/{todo_id}")
    assert delete_resp.status_code == 204


def test_create_todo_invalid():
    response = httpx2.post(f"{BASE_URL}/todos", json={"description": "title 없음"})
    assert response.status_code == 422


def test_delete_todo_not_found():
    response = httpx2.delete(f"{BASE_URL}/todos/999999")
    assert response.status_code == 404
