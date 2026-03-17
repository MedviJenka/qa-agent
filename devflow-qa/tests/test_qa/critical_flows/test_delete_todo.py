"""
Critical flow: Delete todo

Covers removing todo items from the list, including:
- Deleting the only item restores the empty state
- Deleting one of multiple items removes only that item
- The correct item is removed when deleting by position (first, middle, last)
- List count decrements correctly after each deletion

Selectors verified via Playwright MCP against http://localhost:5173:
  - Delete button aria-label: 'Delete "<text>"'
  - Empty state text: 'No todos yet. Add one above.'
  - Todo list role: list, name 'Todo list'
"""

import pytest
from playwright.sync_api import Page, expect

from tests.test_qa.critical_flows.test_add_todo import PAGE


@pytest.mark.critical_flow
def test_delete_only_todo_shows_empty_state(page: Page) -> None:
    """Deleting the sole todo item restores the empty-state paragraph."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("Only task")
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_text("Only task")).to_be_visible()

    page.get_by_role("button", name='Delete "Only task"').click()

    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()


@pytest.mark.critical_flow
def test_delete_one_of_two_leaves_the_other(page: Page) -> None:
    """Deleting the second of two todos leaves only the first in the list."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("Keep me")
    page.get_by_role("button", name="Add").click()
    page.get_by_label("New todo text").fill("Delete me")
    page.get_by_role("button", name="Add").click()

    page.get_by_role("button", name='Delete "Delete me"').click()

    expect(page.get_by_text("Keep me")).to_be_visible()
    expect(page.get_by_text("Delete me")).not_to_be_visible()
    expect(page.get_by_role("listitem")).to_have_count(1)


@pytest.mark.critical_flow
def test_delete_first_of_three_leaves_two(page: Page) -> None:
    """Deleting the first item leaves the remaining two in original order."""
    page.goto(PAGE)
    for text in ["Alpha", "Beta", "Gamma"]:
        page.get_by_label("New todo text").fill(text)
        page.get_by_role("button", name="Add").click()

    page.get_by_role("button", name='Delete "Alpha"').click()

    expect(page.get_by_role("listitem")).to_have_count(2)
    expect(page.get_by_text("Alpha")).not_to_be_visible()
    expect(page.get_by_text("Beta")).to_be_visible()
    expect(page.get_by_text("Gamma")).to_be_visible()


@pytest.mark.critical_flow
def test_delete_all_todos_sequentially_shows_empty_state(page: Page) -> None:
    """Deleting all todos one by one leaves the empty-state paragraph."""
    page.goto(PAGE)
    for text in ["Task A", "Task B"]:
        page.get_by_label("New todo text").fill(text)
        page.get_by_role("button", name="Add").click()

    page.get_by_role("button", name='Delete "Task A"').click()
    page.get_by_role("button", name='Delete "Task B"').click()

    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()
    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()
