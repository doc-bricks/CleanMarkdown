"""Render-Tests fuer CleanMarkdown.

Deckt die in ``Empirie_Markdown_Stichprobe_100.md`` dominanten Features ab und
zusaetzlich kritische Edge-Cases (Mathe-/Code-Schutz, Task-Lists), die im
GUI-Selbsttest nur stichprobenartig vorkommen.
"""

from __future__ import annotations

import pytest

from .conftest import render_to_body


# ---------------------------------------------------------------------------
# Hilfsfunktionen (Code-Schutz)
# ---------------------------------------------------------------------------

def test_protect_code_regions_replaces_fenced_block(render_helpers):
    text = "Vor\n\n```\n$x$\n```\n\nNach"
    masked, protected = render_helpers._protect_code_regions(text)
    assert "$x$" not in masked
    assert any("```" in value and "$x$" in value for value in protected.values())
    restored = render_helpers._restore_protected_regions(masked, protected)
    assert restored == text


def test_protect_code_regions_replaces_inline_code(render_helpers):
    text = "vor `$inline$` nach"
    masked, protected = render_helpers._protect_code_regions(text)
    assert "$inline$" not in masked
    restored = render_helpers._restore_protected_regions(masked, protected)
    assert restored == text


def test_protect_code_regions_handles_tilde_fence(render_helpers):
    text = "~~~\nA $b$ C\n~~~"
    masked, protected = render_helpers._protect_code_regions(text)
    assert "$b$" not in masked
    assert protected, "Tilden-Fence muss als geschuetzt markiert sein"


# ---------------------------------------------------------------------------
# Mathe-Markup (inline / block)
# ---------------------------------------------------------------------------

def test_inline_math_creates_span(render_helpers):
    text = "Pythagoras: $a^2 + b^2 = c^2$ in Zahlen."
    rendered = render_helpers._inject_math_markup(text)
    assert 'class="math-inline"' in rendered
    assert "a^2 + b^2 = c^2" in rendered


def test_block_math_dollar_dollar_creates_div(render_helpers):
    text = "Vorher.\n\n$$\n\\int_0^1 x\\, dx\n$$\n\nNachher."
    rendered = render_helpers._inject_math_markup(text)
    assert 'class="math-block"' in rendered
    assert "\\int_0^1" in rendered


def test_block_math_bracket_syntax(render_helpers):
    text = "Vor\n\n\\[\nE = mc^2\n\\]\n\nNach"
    rendered = render_helpers._inject_math_markup(text)
    assert 'class="math-block"' in rendered
    assert "E = mc^2" in rendered


def test_inline_math_paren_syntax(render_helpers):
    text = "Per Definition: \\(\\nabla \\cdot E = \\rho\\) gilt."
    rendered = render_helpers._inject_math_markup(text)
    assert 'class="math-inline"' in rendered


def test_pure_number_dollar_left_untouched(render_helpers):
    """Preisangaben wie ``$100`` oder ``$1.50`` sollen kein Mathe ausloesen."""

    text = "Kosten: $100$ und $1.50$ als reine Zahlen."
    rendered = render_helpers._inject_math_markup(text)
    assert 'class="math-inline"' not in rendered


def test_inline_code_dollar_does_not_trigger_math(render_helpers):
    text = "Beispiel `$variable` im Code, danach $a^2$ in Mathe."
    rendered = render_helpers._inject_math_markup(text)
    # Inline-Code wurde geschuetzt -> bleibt im Klartext erhalten
    assert "`$variable`" in rendered
    # Mathe ausserhalb wurde umgewandelt
    assert 'class="math-inline"' in rendered


def test_fenced_code_dollar_block_does_not_trigger_math(render_helpers):
    text = "```python\nprint('$total$')\n```\n\n$a^2$"
    rendered = render_helpers._inject_math_markup(text)
    assert "$total$" in rendered  # innerhalb des Code-Blocks geschuetzt
    assert 'class="math-inline"' in rendered  # ausserhalb umgewandelt


# ---------------------------------------------------------------------------
# Task-Lists
# ---------------------------------------------------------------------------

def test_task_list_open_box(render_helpers):
    body = "<ul>\n<li>[ ] Offen</li>\n</ul>"
    rendered = render_helpers._render_task_lists(body)
    assert "☐" in rendered
    assert 'class="task-list"' in rendered
    assert "[ ]" not in rendered


def test_task_list_checked_box(render_helpers):
    body = "<ul>\n<li>[x] Erledigt</li>\n</ul>"
    rendered = render_helpers._render_task_lists(body)
    assert "☑" in rendered
    assert "[x]" not in rendered


def test_task_list_uppercase_x_also_checks(render_helpers):
    body = "<ul>\n<li>[X] Erledigt mit grossem X</li>\n</ul>"
    rendered = render_helpers._render_task_lists(body)
    assert "☑" in rendered
    assert "[X]" not in rendered


# ---------------------------------------------------------------------------
# Vollstaendige Render-Pipeline
# ---------------------------------------------------------------------------

def test_pipeline_renders_atx_headings(render_helpers):
    md = "# Eins\n\n## Zwei\n\n### Drei\n"
    body = render_to_body(render_helpers, md)
    assert "<h1>Eins</h1>" in body
    assert "<h2>Zwei</h2>" in body
    assert "<h3>Drei</h3>" in body


def test_pipeline_renders_emphasis(render_helpers):
    md = "Ein **fettes** und *kursives* Wort."
    body = render_to_body(render_helpers, md)
    assert "<strong>fettes</strong>" in body
    assert "<em>kursives</em>" in body


def test_pipeline_renders_unordered_list(render_helpers):
    md = "- Apfel\n- Birne\n- Kirsche\n"
    body = render_to_body(render_helpers, md)
    assert "<ul>" in body
    assert body.count("<li>") == 3


def test_pipeline_renders_ordered_list(render_helpers):
    md = "1. Erstens\n2. Zweitens\n3. Drittens\n"
    body = render_to_body(render_helpers, md)
    assert "<ol>" in body
    assert body.count("<li>") == 3


def test_pipeline_renders_inline_code(render_helpers):
    md = "Ein `python -V` Aufruf."
    body = render_to_body(render_helpers, md)
    assert "<code>python -V</code>" in body


def test_pipeline_renders_fenced_code_block(render_helpers):
    md = "```python\nprint('hi')\n```\n"
    body = render_to_body(render_helpers, md)
    assert "<pre>" in body
    assert "print(&#39;hi&#39;)" in body or "print('hi')" in body


def test_pipeline_renders_table_with_extra_extension(render_helpers):
    md = (
        "| Spalte | Wert |\n"
        "| --- | --- |\n"
        "| Alpha | Beta |\n"
        "| Gamma | Delta |\n"
    )
    body = render_to_body(render_helpers, md)
    assert "<table>" in body
    assert "<th>Spalte</th>" in body
    assert "<td>Alpha</td>" in body


def test_pipeline_renders_blockquote(render_helpers):
    md = "> Einsicht ist der erste Schritt zur Besserung."
    body = render_to_body(render_helpers, md)
    assert "<blockquote>" in body


def test_pipeline_renders_horizontal_rule(render_helpers):
    md = "Vor\n\n---\n\nNach"
    body = render_to_body(render_helpers, md)
    assert "<hr" in body


def test_pipeline_renders_footnote(render_helpers):
    md = "Mit Fussnote.[^1]\n\n[^1]: Anmerkung"
    body = render_to_body(render_helpers, md)
    assert "footnote" in body.lower()
    assert "Anmerkung" in body


def test_pipeline_renders_image(render_helpers):
    md = "![Logo](logo.png)"
    body = render_to_body(render_helpers, md)
    assert "<img" in body
    assert 'src="logo.png"' in body
    assert 'alt="Logo"' in body


def test_pipeline_renders_link(render_helpers):
    md = "Siehe [Anthropic](https://www.anthropic.com)."
    body = render_to_body(render_helpers, md)
    assert '<a href="https://www.anthropic.com">Anthropic</a>' in body


def test_pipeline_render_combines_math_and_code_correctly(render_helpers):
    md = (
        "Inline `code mit $var$` neben echtem Mathe $a^2 + b^2$.\n\n"
        "```\nprint('$total$')\n```\n\n"
        "$$\nE = mc^2\n$$"
    )
    body = render_to_body(render_helpers, md)
    # Code bleibt original
    assert "$total$" in body
    assert "code mit $var$" in body
    # Mathe wurde umgewandelt
    assert 'class="math-inline"' in body
    assert 'class="math-block"' in body


def test_pipeline_german_umlauts_preserved(render_helpers):
    """Globale Regel: Echte Umlaute muessen erhalten bleiben."""

    md = "## Übersicht\n\nFür äußere Größen gilt die Schwäche der Lösung."
    body = render_to_body(render_helpers, md)
    assert "Übersicht" in body
    assert "äußere" in body
    assert "Größen" in body
    assert "Schwäche" in body
    assert "Lösung" in body


def test_pipeline_task_list_full_round_trip(render_helpers):
    md = "- [ ] Offen\n- [x] Erledigt\n- [X] Auch erledigt\n"
    body = render_to_body(render_helpers, md)
    assert body.count("☐") == 1
    assert body.count("☑") == 2
    assert "[ ]" not in body and "[x]" not in body and "[X]" not in body


# ---------------------------------------------------------------------------
# Regressions-Edge-Cases
# ---------------------------------------------------------------------------

def test_consecutive_inline_math_each_wrapped(render_helpers):
    text = "Erst $a$ und dann $b$ getrennt."
    rendered = render_helpers._inject_math_markup(text)
    assert rendered.count('class="math-inline"') == 2


def test_block_math_with_indentation_keeps_indent(render_helpers):
    text = "Vor\n\n  $$\n  x = y\n  $$\n\nNach"
    rendered = render_helpers._inject_math_markup(text)
    assert 'class="math-block"' in rendered


def test_escaped_dollar_is_not_math(render_helpers):
    """Mit Backslash maskierte ``\\$`` sollen kein Mathe oeffnen."""

    text = r"Preis \$5 und \$10 als Eskapaden."
    rendered = render_helpers._inject_math_markup(text)
    assert 'class="math-inline"' not in rendered


def test_empty_input_does_not_crash(render_helpers):
    rendered = render_helpers._inject_math_markup("")
    assert rendered == ""
    body = render_helpers._render_task_lists("")
    assert body == ""


def test_round_trip_protect_then_restore_preserves_text(render_helpers):
    text = "code: `a` + `b`, fenced:\n\n```\nx = 1\n```\n\nende"
    masked, protected = render_helpers._protect_code_regions(text)
    restored = render_helpers._restore_protected_regions(masked, protected)
    assert restored == text


@pytest.mark.parametrize(
    "feature,markdown,expected_substr",
    [
        ("strikethrough", "Das ist ~~weg~~ jetzt.", "<del>weg</del>"),
        ("nested_list", "- A\n    - A1\n    - A2\n- B", "<li>A1</li>"),
        ("multiple_blockquotes", "> Erst\n>\n> Zweitens", "<blockquote>"),
    ],
)
def test_pipeline_misc_features(render_helpers, feature, markdown, expected_substr):
    body = render_to_body(render_helpers, markdown)
    assert expected_substr in body, f"Feature {feature} fehlt im Output: {body!r}"


# ---------------------------------------------------------------------------
# Strikethrough (eigene GFM-Erweiterung)
# ---------------------------------------------------------------------------

def test_strikethrough_simple(render_helpers):
    body = render_helpers._render_strikethrough("Das ist <p>~~weg~~</p> hier.")
    assert "<del>weg</del>" in body


def test_strikethrough_does_not_touch_inline_code(render_helpers):
    body = "<p>Beispiel <code>~~ist Code~~</code> und ~~echt~~ daneben.</p>"
    rendered = render_helpers._render_strikethrough(body)
    assert "<code>~~ist Code~~</code>" in rendered
    assert "<del>echt</del>" in rendered


def test_strikethrough_does_not_touch_pre_block(render_helpers):
    body = "<pre><code>~~bleibt~~</code></pre>\n<p>~~geht~~</p>"
    rendered = render_helpers._render_strikethrough(body)
    assert "~~bleibt~~" in rendered
    assert "<del>geht</del>" in rendered


def test_strikethrough_full_pipeline(render_helpers):
    md = "Vor ~~text~~ nach.\n\n```\n~~code~~ bleibt\n```"
    body = render_to_body(render_helpers, md)
    assert "<del>text</del>" in body
    assert "~~code~~ bleibt" in body
