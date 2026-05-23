import json

_PROMPT = """คุณเป็นผู้ช่วยสรุปเอกสารธุรกิจภาษาไทย
จากข้อความและ entity ที่ดึงออกมา จงสรุปประเด็นสำคัญของเอกสาร

ข้อความ:
{text}

Entity ที่พบ:
{entities}

ตอบในรูปแบบ JSON เท่านั้น ไม่ต้องมี markdown:
{{
  "คู่สัญญา": [],
  "วันที่สำคัญ": [],
  "มูลค่า": [],
  "สาระสำคัญ": "<สรุป 2-3 ประโยค>",
  "ข้อสังเกต": "<สิ่งที่ควรตรวจสอบเพิ่มเติม หรือ '-' ถ้าไม่มี>"
}}"""


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
    return json.loads(raw)


def summarize_document(text: str, entities: dict, client) -> dict:
    entities_str = json.dumps(entities, ensure_ascii=False, indent=2)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=_PROMPT.format(text=text[:2000], entities=entities_str),
    )
    return _parse_json(response.text)
