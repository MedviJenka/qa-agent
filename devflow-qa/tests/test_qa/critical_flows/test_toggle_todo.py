"""
Critical flow: Toggle todo

Covers toggling a todo item between done and incomplete states, including:
- Checkbox becomes checked and text gains line-through after first toggle
- Checkbox becomes unchecked and line-through is removed after second toggle
- Toggling one item does not affect sibling items

Selectors and style values verified via Playwright MCP against http://localhost:5173:
  - Checkbox label before toggle: 'Mark "<text>" as done'
  - Checkbox label after toggle:  'Mark "<text>" as incomplete'
  - text-decoration before toggle: 'none'
  - text-decoration after toggle:  'line-through'
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.critical_flow
def test_toggle_marks_todo_as_done(page: Page) -> None:
    """Clicking the checkbox on an incomplete todo checks it and sets line-through."""
    page.goto("/")
    page.get_by_label("New todo text").fill("Buy groceries")
    page.get_by_role("button", name="Add").click()

    checkbox = page.get_by_role("checkbox", name='Mark "Buy groceries" as done')
    expect(checkbox).not_to_be_checked()
    checkbox.click()
    expect(checkbox).to_be_checked()


@pytest.mark.critical_flow
def test_toggle_applies_line_through_style(page: Page) -> None:
    """After toggling done, the todo text element has text-decoration: line-through."""
    page.goto("/")
    page.get_by_label("New todo text").fill("Read a book")
    page.get_by_role("button", name="Add").click()

    page.get_by_role("checkbox", name='Mark "Read a book" as done').click()

    text_span = page.get_by_text("Read a book")
    text_decoration = text_span.evaluate(
        "el => window.getComputedStyle(el).textDecoration"
    )
    assert "line-through" in text_decoration


@pytest.mark.critical_flow
def test_toggle_twice_returns_to_incomplete(page: Page) -> None:
    """Toggling a done todo a second time unchecks it and removes line-through."""
    page.goto("/")
    page.get_by_label("New todo text").fill("Walk the dog")
    page.get_by_role("button", name="Add").click()

    # First toggle: mark done
    page.get_by_role("checkbox", name='Mark "Walk the dog" as done').click()
    expect(
        page.get_by_role("checkbox", name='Mark "Walk the dog" as incomplete')
    ).to_be_checked()

    # Second toggle: mark incomplete
    page.get_by_role("checkbox", name='Mark "Walk the dog" as incomplete').click()
    checkbox = page.get_by_role("checkbox", name='Mark "Walk the dog" as done')
    expect(checkbox).not_to_be_checked()

    text_decoration = page.get_by_text("Walk the dog").evaluate(
        "el => window.getComputedStyle(el).textDecoration"
    )
    assert "line-through" not in text_decoration


@pytest.mark.critical_flow
def test_toggle_aria_label_changes_after_click(page: Page) -> None:
    """The checkbox aria-label switches between 'as done' and 'as incomplete'."""
    page.goto("/")
    page.get_by_label("New todo text").fill("Call dentist")
    page.get_by_role("button", name="Add").click()

    # Before toggle: label contains "as done"
    expect(
        page.get_by_role("checkbox", name='Mark "Call dentist" as done')
    ).to_be_visible()

    page.get_by_role("checkbox", name='Mark "Call dentist" as done').click()

    # After toggle: label contains "as incomplete"
    expect(
        page.get_by_role("checkbox", name='Mark "Call dentist" as incomplete')
    ).to_be_visible()


@pytest.mark.critical_flow
def test_toggle_does_not_affect_sibling_todo(page: Page) -> None:
    """Toggling one todo leaves all other todos unchanged."""
    page.goto("/")
    for text in ["First task", "Second task"]:
        page.get_by_label("New todo text").fill(text)
        page.get_by_role("button", name="Add").click()

    # Toggle only the first item
    page.get_by_role("checkbox", name='Mark "First task" as done').click()

    # First item is now checked
    expect(
        page.get_by_role("checkbox", name='Mark "First task" as incomplete')
    ).to_be_checked()

    # Second item is still unchecked
    expect(
        page.get_by_role("checkbox", name='Mark "Second task" as done')
    ).not_to_be_checked()
