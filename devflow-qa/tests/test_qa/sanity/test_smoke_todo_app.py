"""
Sanity / smoke tests for the Todo App.

Verifies that the application renders its key structural elements on load
without any interaction. These tests catch catastrophic regressions —
blank pages, missing headings, missing form controls — before deeper
test suites run.

Runtime verified via Playwright MCP against http://localhost:5173.
"""

import pytest
from playwright.sync_api import Page, expect


PAGE = "http://localhost:5173"


@pytest.mark.sanity
def test_app_root_renders(page: Page) -> None:
    """The <main> landmark is present immediately after load."""
    page.goto(PAGE)
    expect(page.get_by_role("main")).to_be_visible()


@pytest.mark.sanity
def test_heading_is_visible(page: Page) -> None:
    """The 'Todo' heading is always rendered regardless of list state."""
    page.goto(PAGE)
    expect(page.get_by_role("heading", name="Todo")).to_be_visible()


@pytest.mark.sanity
def test_add_todo_form_renders(page: Page) -> None:
    """The AddTodo form (role=form, aria-label='Add todo') is visible on load."""
    page.goto(PAGE)
    expect(page.get_by_role("form", name="Add todo")).to_be_visible()


@pytest.mark.sanity
def test_new_todo_input_renders(page: Page) -> None:
    """The text input with label 'New todo text' is visible and focusable."""
    page.goto(PAGE)
    expect(page.get_by_label("New todo text")).to_be_visible()


@pytest.mark.sanity
def test_add_button_renders(page: Page) -> None:
    """The 'Add' submit button is present on initial render."""
    page.goto(PAGE)
    expect(page.get_by_role("button", name="Add")).to_be_visible()


@pytest.mark.sanity
def test_empty_state_renders_on_fresh_load(page: Page) -> None:
    """With no todos, the empty-state paragraph is shown on initial load."""
    page.goto(PAGE)
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()
