import re

THAI_MONTHS = (
    r"มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|"
    r"กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม|"
    r"ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\."
)

REGEX_PATTERNS: dict[str, list[str]] = {
    "DATE": [
        rf"\d{{1,2}}\s*(?:{THAI_MONTHS})\s*\d{{4}}",
        r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}",
        r"\d{4}-\d{2}-\d{2}",
    ],
    "MONEY": [
        r"[\d,]+(?:\.\d{1,2})?\s*(?:บาท|THB|฿)",
        r"(?:THB|฿)\s*[\d,]+(?:\.\d{1,2})?",
        r"(?:จำนวน|มูลค่า|ราคา|รวม)\s*[\d,]+(?:\.\d{1,2})?",
    ],
    "TAX_ID": [
        r"\b\d{13}\b",
        r"\b\d-\d{4}-\d{5}-\d{2}-\d\b",
    ],
    "INVOICE_NO": [
        r"(?:INV|IV|เลขที่|เอกสารเลขที่)[- _#]*[\w\d/\-]+",
        r"(?:Invoice\s*No\.?|Inv\.?\s*No\.?)\s*:?\s*[\w\d/\-]+",
    ],
}


def _extract_regex(text: str) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    for entity_type, patterns in REGEX_PATTERNS.items():
        found: list[str] = []
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            found.extend(m.strip() for m in matches)
        if found:
            results[entity_type] = list(dict.fromkeys(found))
    return results


def _extract_thai_ner(text: str) -> dict[str, list[str]]:
    try:
        from pythainlp.tag import NER  # type: ignore

        ner = NER(engine="thainer")
        tagged: list[tuple[str, str]] = ner.get_ner(text)

        label_map = {
            "PERSON": "PERSON",
            "ORGANIZATION": "ORG",
            "LOCATION": "ADDRESS",
        }
        bucket: dict[str, list[str]] = {v: [] for v in label_map.values()}

        current_label: str | None = None
        current_tokens: list[str] = []

        def flush():
            if current_label and current_tokens:
                mapped = label_map.get(current_label)
                if mapped:
                    entity = "".join(current_tokens).strip()
                    if entity:
                        bucket[mapped].append(entity)

        for token, tag in tagged:
            if tag.startswith("B-"):
                flush()
                current_label = tag[2:]
                current_tokens = [token]
            elif tag.startswith("I-") and current_label:
                current_tokens.append(token)
            else:
                flush()
                current_label = None
                current_tokens = []
        flush()

        return {k: list(dict.fromkeys(v)) for k, v in bucket.items() if v}
    except Exception:
        return {}


def extract_entities(text: str) -> dict[str, list[str]]:
    entities = _extract_regex(text)
    thai_entities = _extract_thai_ner(text)
    for k, v in thai_entities.items():
        entities.setdefault(k, [])
        entities[k] = list(dict.fromkeys(entities[k] + v))
    return entities
