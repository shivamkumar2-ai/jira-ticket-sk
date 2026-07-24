import pytest
from pydantic import ValidationError

from app.schemas import ProjectCreate


def test_project_create_accepts_camel_case_resource_url():
    project = ProjectCreate.model_validate(
        {
            "title": "Valid",
            "description": "Valid description",
            "category": "bug",
            "status": "in_progress",
            "priority": "medium",
            "progress": 25,
            "tags": "bug, board",
            "resourceUrl": "https://example.com",
            "notes": "",
        }
    )
    assert project.resource_url == "https://example.com"
    assert project.tags == ["bug", "board"]


def test_project_create_rejects_invalid_url():
    with pytest.raises(ValidationError):
        ProjectCreate.model_validate(
            {
                "title": "Valid",
                "description": "Valid description",
                "category": "bug",
                "status": "in_progress",
                "priority": "medium",
                "progress": 25,
                "resourceUrl": "not-a-url",
            }
        )
