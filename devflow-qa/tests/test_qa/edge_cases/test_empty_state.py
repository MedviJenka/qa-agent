"""
Edge case: Empty state visibility

Verifies that the empty-state paragraph appears and disappears at the correct
moments. Because there is no async data fetching in this app, all state
transitions are synchronous — no route mocking is needed.

Test plan coverage: E1 (empty state after delete last), E2 (single item
add/toggle/delete cycle), S3 (initial empty state on fresh load).

Selectors verified via Playwright MCP against http://localhost:5173.
"""

import pytest
from playwright.sync_api import Page, expect


PAGE = "http://localhost:5173"


@pytest.mark.edge_case
def test_empty_state_visible_on_initial_load(page: Page) -> None:
    """[E1 / S3] Empty-state text is shown when no todos exist on fresh page load."""
    page.goto(PAGE)
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()
    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()


@pytest.mark.edge_case
def test_empty_state_disappears_after_add(page: Page) -> None:
    """Empty state must hide as soon as the first todo is added."""
    page.goto(PAGE)
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()

    page.get_by_label("New todo text").fill("First todo")
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_text("No todos yet. Add one above.")).not_to_be_visible()
    expect(page.get_by_role("list", name="Todo list")).to_be_visible()


@pytest.mark.edge_case
def test_empty_state_returns_after_deleting_last_todo(page: Page) -> None:
    """[E1] Deleting the last remaining todo must restore the empty-state paragraph."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("Only todo")
    page.get_by_role("button", name="Add").click()
    expect(page.get_by_text("No todos yet. Add one above.")).not_to_be_visible()

    page.get_by_role("button", name='Delete "Only todo"').click()

    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()
    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()


@pytest.mark.edge_case
def test_single_item_full_lifecycle(page: Page) -> None:
    """[E2] Add one todo, toggle it, then delete it — app must end in empty state with no errors."""
    page.goto(PAGE)

    # Add
    page.get_by_label("New todo text").fill("Lifecycle task")
    page.get_by_role("button", name="Add").click()
    expect(page.get_by_text("Lifecycle task")).to_be_visible()

    # Toggle done
    page.get_by_role("checkbox", name='Mark "Lifecycle task" as done').click()
    expect(
        page.get_by_role("checkbox", name='Mark "Lifecycle task" as incomplete')
    ).to_be_checked()

    # Delete
    page.get_by_role("button", name='Delete "Lifecycle task"').click()

    # Empty state restored; no crash
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()
    expect(page.get_by_role("heading", name="Todo")).to_be_visible()
    expect(page.get_by_role("form", name="Add todo")).to_be_visible()
