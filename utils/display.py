import html
import re
import streamlit as st

ENTITY_COLORS: dict[str, tuple[str, str]] = {
    "DATE":       ("#2980B9", "#FFFFFF"),
    "MONEY":      ("#27AE60", "#FFFFFF"),
    "ORG":        ("#E67E22", "#FFFFFF"),
    "PERSON":     ("#8E44AD", "#FFFFFF"),
    "TAX_ID":     ("#D4AC0D", "#FFFFFF"),
    "ADDRESS":    ("#C0392B", "#FFFFFF"),
    "INVOICE_NO": ("#16A085", "#FFFFFF"),
}

ENTITY_LABELS: dict[str, str] = {
    "DATE":       "วันที่",
    "MONEY":      "เงิน",
    "ORG":        "องค์กร",
    "PERSON":     "บุคคล",
    "TAX_ID":     "เลขภาษี",
    "ADDRESS":    "ที่อยู่",
    "INVOICE_NO": "เลขที่เอกสาร",
}


def highlight_entities(text: str, entities: dict[str, list[str]]) -> str:
    spans: list[tuple[int, int, str]] = []

    for entity_type, values in entities.items():
        if entity_type not in ENTITY_COLORS:
            continue
        for value in values:
            pattern = re.escape(str(value).strip())
            for m in re.finditer(pattern, text):
                spans.append((m.start(), m.end(), entity_type))

    spans.sort(key=lambda x: x[0])

    # Remove overlapping spans (keep first)
    filtered: list[tuple[int, int, str]] = []
    last_end = 0
    for span in spans:
        if span[0] >= last_end:
            filtered.append(span)
            last_end = span[1]

    result: list[str] = []
    pos = 0
    for start, end, entity_type in filtered:
        result.append(html.escape(text[pos:start]))
        bg, fg = ENTITY_COLORS[entity_type]
        label = ENTITY_LABELS.get(entity_type, entity_type)
        result.append(
            f'<mark style="background:{bg};color:{fg};padding:1px 5px;'
            f'border-radius:4px;font-weight:600;" title="{label}">'
            f'{html.escape(text[start:end])}'
            f'<sup style="font-size:0.6em;margin-left:2px;opacity:0.8">{label}</sup>'
            f"</mark>"
        )
        pos = end
    result.append(html.escape(text[pos:]))

    return "".join(result).replace("\n", "<br>")


def render_entity_table(entities: dict[str, list[str]]) -> None:
    if not any(entities.values()):
        st.info("ไม่พบ entity ในเอกสาร")
        return

    for entity_type, values in entities.items():
        if not values:
            continue
        bg, fg = ENTITY_COLORS.get(entity_type, ("#EAECEE", "#17202A"))
        label = ENTITY_LABELS.get(entity_type, entity_type)
        badge = (
            f'<span style="background:{bg};color:{fg};padding:3px 10px;'
            f'border-radius:12px;font-size:0.82em;font-weight:700">{label}</span>'
        )
        items = " &nbsp;·&nbsp; ".join(html.escape(str(v)) for v in values)
        st.markdown(f"{badge} &nbsp; {items}", unsafe_allow_html=True)
