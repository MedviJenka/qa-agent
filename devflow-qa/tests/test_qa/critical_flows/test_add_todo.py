"""
Critical flow: Add todo

Covers the primary user flow for creating new todo items, including:
- Successful add via button click
- Successful add via Enter key
- Input cleared after successful add
- Multiple todos accumulate in the list
- Empty / whitespace-only input guard (no item added)

Selectors verified via Playwright MCP against http://localhost:5173.
"""

import pytest
from playwright.sync_api import Page, expect


PAGE = 'http://localhost:5173'


@pytest.mark.critical_flow
def test_add_todo_via_button_click(page: Page) -> None:
    """Typing text and clicking Add appends a new item to the list."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("Buy groceries")
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_role("list", name="Todo list")).to_be_visible()
    expect(page.get_by_text("Buy groceries")).to_be_visible()


@pytest.mark.critical_flow
def test_input_is_cleared_after_add(page: Page) -> None:
    """After a successful add the text input is reset to empty."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("Walk the dog")
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_label("New todo text")).to_have_value("")


@pytest.mark.critical_flow
def test_add_todo_via_enter_key(page: Page) -> None:
    """Pressing Enter while the input is focused submits the form."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("Read a book")
    page.get_by_label("New todo text").press("Enter")

    expect(page.get_by_text("Read a book")).to_be_visible()


@pytest.mark.critical_flow
def test_empty_state_hides_after_first_add(page: Page) -> None:
    """The empty-state paragraph disappears once a todo is added."""
    page.goto(PAGE)
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()

    page.get_by_label("New todo text").fill("First task")
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_text("No todos yet. Add one above.")).not_to_be_visible()


@pytest.mark.critical_flow
def test_multiple_todos_accumulate(page: Page) -> None:
    """Adding multiple todos results in multiple list items."""
    page.goto(PAGE)

    todos = ["Task one", "Task two", "Task three"]
    for text in todos:
        page.get_by_label("New todo text").fill(text)
        page.get_by_role("button", name="Add").click()

    list_items = page.get_by_role("listitem")
    expect(list_items).to_have_count(3)


@pytest.mark.critical_flow
def test_empty_input_does_not_add_todo(page: Page) -> None:
    """Clicking Add with an empty input adds nothing to the list."""
    page.goto(PAGE)
    page.get_by_role("button", name="Add").click()

    # List should not appear — empty state remains
    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()


@pytest.mark.critical_flow
def test_whitespace_only_input_does_not_add_todo(page: Page) -> None:
    """Clicking Add with whitespace-only input adds nothing to the list."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("   ")
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()
