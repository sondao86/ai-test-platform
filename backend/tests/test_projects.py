"""Tests for project CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    response = await client.post(
        "/api/v1/projects",
        data={"name": "Test BRD Project", "description": "A test project"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test BRD Project"
    assert data["status"] == "created"
    assert data["current_phase"] == 0


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient):
    # Create a project first
    await client.post(
        "/api/v1/projects",
        data={"name": "Project 1"},
    )

    response = await client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/projects",
        data={"name": "Get Me"},
    )
    project_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Me"


@pytest.mark.asyncio
async def test_get_nonexistent_project(client: AsyncClient):
    response = await client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/projects",
        data={"name": "To Delete"},
    )
    project_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204

    # Verify it's archived
    get_resp = await client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.json()["status"] == "archived"
