"""
Regression guard: State integrity after toggle and delete operations

Source findings:
  - ui-flows.md — [NIT] No key stability guarantee for todo items
  - test-plan.md — R2 (toggle updates correct item), R3 (delete removes correct item),
    R4 (list reflects state after add/toggle/delete sequence)

These tests guard against regressions in the App state handlers (addTodo,
toggleTodo, deleteTodo) that could cause the wrong item to be mutated or
the list to desync from displayed state. All handlers use the functional
setTodos updater form, which is safe today — these tests lock that behaviour.

Selectors verified via Playwright MCP against http://localhost:5173.
"""

import pytest
from playwright.sync_api import Page, expect


PAGE = "http://localhost:5173"


@pytest.mark.regression
def test_toggle_updates_only_the_target_item(page: Page) -> None:
    """[R2] Toggling the first of two todos affects only that item, not the second."""
    page.goto(PAGE)
    for text in ["First", "Second"]:
        page.get_by_label("New todo text").fill(text)
        page.get_by_role("button", name="Add").click()

    page.get_by_role("checkbox", name='Mark "First" as done').click()

    # First item toggled
    expect(
        page.get_by_role("checkbox", name='Mark "First" as incomplete')
    ).to_be_checked()
    # Second item untouched
    expect(
        page.get_by_role("checkbox", name='Mark "Second" as done')
    ).not_to_be_checked()


@pytest.mark.regression
def test_delete_removes_only_the_target_item(page: Page) -> None:
    """[R3] Deleting the second of two todos leaves only the first."""
    page.goto(PAGE)
    for text in ["Alpha", "Beta"]:
        page.get_by_label("New todo text").fill(text)
        page.get_by_role("button", name="Add").click()

    page.get_by_role("button", name='Delete "Beta"').click()

    expect(page.get_by_text("Alpha")).to_be_visible()
    expect(page.get_by_text("Beta")).not_to_be_visible()
    expect(page.get_by_role("listitem")).to_have_count(1)


@pytest.mark.regression
def test_list_state_reflects_add_toggle_delete_sequence(page: Page) -> None:
    """[R4] List accurately reflects state after a combined add/toggle/delete sequence."""
    page.goto(PAGE)

    # Add three todos
    for text in ["Task One", "Task Two", "Task Three"]:
        page.get_by_label("New todo text").fill(text)
        page.get_by_role("button", name="Add").click()

    # Toggle the second item done
    page.get_by_role("checkbox", name='Mark "Task Two" as done').click()

    # Delete the first item
    page.get_by_role("button", name='Delete "Task One"').click()

    # Expected list: Task Two (done), Task Three (not done)
    expect(page.get_by_role("listitem")).to_have_count(2)
    expect(page.get_by_text("Task One")).not_to_be_visible()
    expect(
        page.get_by_role("checkbox", name='Mark "Task Two" as incomplete')
    ).to_be_checked()
    expect(
        page.get_by_role("checkbox", name='Mark "Task Three" as done')
    ).not_to_be_checked()


@pytest.mark.regression
def test_toggle_preserves_item_text(page: Page) -> None:
    """Toggling a todo must not alter its displayed text content."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("Stable text")
    page.get_by_role("button", name="Add").click()

    page.get_by_role("checkbox", name='Mark "Stable text" as done').click()

    # Text still visible and unchanged after toggle
    expect(page.get_by_text("Stable text")).to_be_visible()


@pytest.mark.regression
def test_list_count_is_correct_after_multiple_deletes(page: Page) -> None:
    """List item count decrements by one for each deletion."""
    page.goto("/")
    for text in ["One", "Two", "Three"]:
        page.get_by_label("New todo text").fill(text)
        page.get_by_role("button", name="Add").click()

    expect(page.get_by_role("listitem")).to_have_count(3)

    page.get_by_role("button", name='Delete "One"').click()
    expect(page.get_by_role("listitem")).to_have_count(2)

    page.get_by_role("button", name='Delete "Two"').click()
    expect(page.get_by_role("listitem")).to_have_count(1)
