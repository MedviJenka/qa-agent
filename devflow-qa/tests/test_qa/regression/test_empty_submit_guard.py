"""
Regression guard: Empty and whitespace-only submit (SHOULD-FIX)

Source finding: ui-regression-risks.md — [SHOULD-FIX]
  "Submit button unconditionally enabled — todo-app/src/components/AddTodo.tsx:25"

The Add button has no disabled condition. When clicked with empty or
whitespace-only input the parent App.addTodo guard silently swallows the
call, but the user receives zero feedback. These tests document that guard
behaviour and will catch any regression where empty input results in a
phantom todo being appended to the list.

Selectors verified via Playwright MCP against http://localhost:5173.
"""

import pytest
from playwright.sync_api import Page, expect


PAGE = "http://localhost:5173"


@pytest.mark.regression
def test_empty_submit_does_not_add_item(page: Page) -> None:
    """[R1] Clicking Add with an empty input must not create a todo item.

    Guards the App.addTodo early-return: `if (!text.trim()) return`.
    """
    page.goto(PAGE)
    # Input is empty on fresh load — click Add directly
    page.get_by_role("button", name="Add").click()

    # The list must not appear; empty state must remain
    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()


@pytest.mark.regression
def test_whitespace_only_submit_does_not_add_item(page: Page) -> None:
    """[R1] Submitting whitespace-only text must not create a todo item.

    Guards both the trim-before-store path in App.addTodo and the
    missing trim in AddTodo.handleSubmit (NIT finding in ui-flows.md).
    """
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("     ")
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()


@pytest.mark.regression
def test_whitespace_only_submit_via_enter_does_not_add_item(page: Page) -> None:
    """[R1] Pressing Enter on whitespace-only input must not create a todo item."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("   ")
    page.get_by_label("New todo text").press("Enter")

    expect(page.get_by_role("list", name="Todo list")).not_to_be_visible()
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()


@pytest.mark.regression
def test_empty_submit_does_not_crash_app(page: Page) -> None:
    """[R1] Repeated empty submits must not crash or corrupt app state."""
    page.goto(PAGE)
    add_button = page.get_by_role("button", name="Add")

    # Click Add three times with no input
    add_button.click()
    add_button.click()
    add_button.click()

    # App must still be functional: heading and form remain visible
    expect(page.get_by_role("heading", name="Todo")).to_be_visible()
    expect(page.get_by_role("form", name="Add todo")).to_be_visible()
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()


@pytest.mark.regression
def test_valid_add_after_empty_submit_still_works(page: Page) -> None:
    """[R1] After an empty submit the form must still accept a valid todo."""
    page.goto("/")
    # First attempt: empty
    page.get_by_role("button", name="Add").click()
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()

    # Second attempt: valid
    page.get_by_label("New todo text").fill("Valid task")
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_text("Valid task")).to_be_visible()
    expect(page.get_by_role("listitem")).to_have_count(1)
