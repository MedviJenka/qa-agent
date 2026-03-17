"""
Edge case: Input value edge cases

Covers unusual but plausible todo text values including very long strings,
leading/trailing whitespace trimming, and text with special characters.
These guard the trim logic split between AddTodo and App (NIT finding in
ui-flows.md and ui-regression-risks.md).

Test plan coverage: E3 (long text), E4 (whitespace trimmed on add).

Selectors verified via Playwright MCP against http://localhost:5173.
"""

import pytest
from playwright.sync_api import Page, expect


PAGE = "http://localhost:5173"


@pytest.mark.edge_case
def test_long_text_is_displayed(page: Page) -> None:
    """[E3] A very long todo text is added and visible (truncation or wrap is acceptable)."""
    page.goto(PAGE)
    long_text = "A" * 200
    page.get_by_label("New todo text").fill(long_text)
    page.get_by_role("button", name="Add").click()

    # The text element must be in the DOM; visual overflow handling is acceptable
    expect(page.get_by_text(long_text)).to_be_visible()
    expect(page.get_by_role("listitem")).to_have_count(1)


@pytest.mark.edge_case
def test_whitespace_trimmed_on_add(page: Page) -> None:
    """[E4] Leading and trailing whitespace is stripped from added todos.

    App.addTodo stores text.trim(), so '  hello  ' must appear as 'hello'.
    """
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("  hello  ")
    page.get_by_role("button", name="Add").click()

    # Trimmed text must be present
    expect(page.get_by_text("hello")).to_be_visible()
    # Full untrimmed string must NOT appear as its own text node
    # (we check the checkbox label which uses the stored, trimmed value)
    expect(
        page.get_by_role("checkbox", name='Mark "hello" as done')
    ).to_be_visible()


@pytest.mark.edge_case
def test_todo_with_special_characters(page: Page) -> None:
    """A todo containing special characters is stored and displayed correctly."""
    page.goto(PAGE)
    special_text = 'Buy "milk" & bread <today>'
    page.get_by_label("New todo text").fill(special_text)
    page.get_by_role("button", name="Add").click()

    expect(page.get_by_text(special_text)).to_be_visible()


@pytest.mark.edge_case
def test_numeric_text_todo(page: Page) -> None:
    """A todo that is purely numeric is added and displayed without falsy-render issues."""
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("42")
    page.get_by_role("button", name="Add").click()

    # Guards against falsy short-circuit renders (e.g. {count && <Component />})
    expect(page.get_by_text("42")).to_be_visible()
    expect(page.get_by_role("listitem")).to_have_count(1)


@pytest.mark.edge_case
def test_input_cleared_after_whitespace_only_submit(page: Page) -> None:
    """After a whitespace-only submit the input value behaviour is consistent.

    The current implementation clears the input even on a rejected submit
    (handleSubmit always calls setInput('')). This test documents that
    behaviour so any change is caught.
    """
    page.goto(PAGE)
    page.get_by_label("New todo text").fill("   ")
    page.get_by_role("button", name="Add").click()

    # No todo added
    expect(page.get_by_text("No todos yet. Add one above.")).to_be_visible()
    # Input is cleared (current documented behaviour)
    expect(page.get_by_label("New todo text")).to_have_value("")
