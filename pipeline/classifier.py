import json

_PROMPT = """คุณเป็นผู้เชี่ยวชาญด้านการจัดประเภทเอกสารธุรกิจภาษาไทย
จากข้อความต่อไปนี้ จงระบุประเภทของเอกสารและให้ค่าความมั่นใจระหว่าง 0.0 ถึง 1.0

ประเภทที่เป็นไปได้: ใบแจ้งหนี้, ใบเสร็จรับเงิน, สัญญา, รายงาน, อื่นๆ

ข้อความ:
{text}

ตอบในรูปแบบ JSON เท่านั้น ไม่ต้องมีคำอธิบายเพิ่มเติมหรือ markdown:
{{"type": "<ประเภท>", "confidence": <0.0-1.0>, "reason": "<เหตุผล 1 ประโยค>"}}"""


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
    return json.loads(raw)


def classify_document(text: str, client) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=_PROMPT.format(text=text[:1500]),
    )
    return _parse_json(response.text)
