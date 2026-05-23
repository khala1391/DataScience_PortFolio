import io
import json

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

st.set_page_config(
    page_title="Document Intelligence Pipeline",
    page_icon="📄",
    layout="wide",
)


_EXAMPLES: dict[str, dict] = {
    "invoice": {
        "filename": "ใบแจ้งหนี้_ตัวอย่าง.pdf",
        "is_example": True,
        "ocr_text": (
            "ใบแจ้งหนี้\n"
            "บริษัท เอบีซี จำกัด\n"
            "123/45 ถนนสุขุมวิท แขวงคลองเตย เขตคลองเตย กรุงเทพฯ 10110\n"
            "เลขที่ผู้เสียภาษี: 0105566012345\n\n"
            "เรียน: บริษัท เอ็กซ์วายแซด จำกัด\n"
            "วันที่: 15 มกราคม 2567\n"
            "เลขที่ใบแจ้งหนี้: INV-2024-0042\n\n"
            "รายการ:\n"
            "1. บริการพัฒนาซอฟต์แวร์   150,000 บาท\n"
            "2. ค่าบำรุงรักษาระบบ       25,000 บาท\n"
            "3. ค่าอบรมพนักงาน          30,000 บาท\n\n"
            "ยอดรวม: 205,000 บาท\n"
            "ภาษีมูลค่าเพิ่ม 7%: 14,350 บาท\n"
            "ยอดสุทธิ: 219,350 บาท\n\n"
            "กำหนดชำระ: 15 กุมภาพันธ์ 2567"
        ),
        "entities": {
            "DATE": ["15 มกราคม 2567", "15 กุมภาพันธ์ 2567"],
            "MONEY": ["150,000 บาท", "25,000 บาท", "30,000 บาท", "219,350 บาท"],
            "ORG": ["บริษัท เอบีซี จำกัด", "บริษัท เอ็กซ์วายแซด จำกัด"],
            "PERSON": [],
            "TAX_ID": ["0105566012345"],
            "ADDRESS": ["123/45 ถนนสุขุมวิท แขวงคลองเตย เขตคลองเตย กรุงเทพฯ 10110"],
            "INVOICE_NO": ["INV-2024-0042"],
        },
        "classification": {
            "type": "ใบแจ้งหนี้",
            "confidence": 0.97,
            "reason": "พบเลขที่ใบแจ้งหนี้ รายการบริการ และยอดเงินรวมพร้อมภาษีมูลค่าเพิ่ม",
        },
        "summary": {
            "คู่สัญญา": [
                "บริษัท เอบีซี จำกัด (ผู้ออกใบแจ้งหนี้)",
                "บริษัท เอ็กซ์วายแซด จำกัด (ผู้รับ)",
            ],
            "วันที่สำคัญ": ["วันที่ออก: 15 มกราคม 2567", "กำหนดชำระ: 15 กุมภาพันธ์ 2567"],
            "มูลค่า": [
                "ยอดก่อนภาษี: 205,000 บาท",
                "ภาษีมูลค่าเพิ่ม (7%): 14,350 บาท",
                "ยอดสุทธิ: 219,350 บาท",
            ],
            "สาระสำคัญ": (
                "ใบแจ้งหนี้จาก บริษัท เอบีซี จำกัด ถึง บริษัท เอ็กซ์วายแซด จำกัด "
                "สำหรับบริการพัฒนาซอฟต์แวร์และบริการที่เกี่ยวข้อง มูลค่ารวม 219,350 บาท "
                "กำหนดชำระภายใน 15 กุมภาพันธ์ 2567"
            ),
            "ข้อสังเกต": "ควรตรวจสอบเลขที่ผู้เสียภาษีและยืนยันกำหนดชำระเงินกับฝ่ายบัญชี",
        },
    },
    "contract": {
        "filename": "สัญญาจ้างงาน_ตัวอย่าง.pdf",
        "is_example": True,
        "ocr_text": (
            "สัญญาจ้างงาน\n"
            "ทำขึ้น ณ บริษัท เทคโนโลยี ไทย จำกัด\n"
            "456 ถนนวิภาวดีรังสิต เขตหลักสี่ กรุงเทพฯ 10210\n\n"
            "สัญญานี้ทำขึ้นระหว่าง\n"
            "นายจ้าง: บริษัท เทคโนโลยี ไทย จำกัด\n"
            "ลูกจ้าง: นายสมชาย ใจดี\n\n"
            "ตำแหน่ง: วิศวกรซอฟต์แวร์อาวุโส\n"
            "วันที่เริ่มงาน: 1 มีนาคม 2567\n"
            "วันสิ้นสุดสัญญา: 28 กุมภาพันธ์ 2568\n"
            "อัตราเงินเดือน: 85,000 บาท ต่อเดือน\n"
            "สวัสดิการ: ประกันสุขภาพ, กองทุนสำรองเลี้ยงชีพ 5%\n\n"
            "ลงนาม ณ วันที่ 20 กุมภาพันธ์ 2567\n"
            "ผู้มีอำนาจลงนาม: นางสาววิภา รักดี ตำแหน่ง ผู้อำนวยการฝ่าย HR"
        ),
        "entities": {
            "DATE": ["1 มีนาคม 2567", "28 กุมภาพันธ์ 2568", "20 กุมภาพันธ์ 2567"],
            "MONEY": ["85,000 บาท"],
            "ORG": ["บริษัท เทคโนโลยี ไทย จำกัด"],
            "PERSON": ["นายสมชาย ใจดี", "นางสาววิภา รักดี"],
            "TAX_ID": [],
            "ADDRESS": ["456 ถนนวิภาวดีรังสิต เขตหลักสี่ กรุงเทพฯ 10210"],
            "INVOICE_NO": [],
        },
        "classification": {
            "type": "สัญญา",
            "confidence": 0.95,
            "reason": "พบข้อความสัญญาระหว่างนายจ้างและลูกจ้าง ระบุตำแหน่งงานและเงินเดือน",
        },
        "summary": {
            "คู่สัญญา": [
                "บริษัท เทคโนโลยี ไทย จำกัด (นายจ้าง)",
                "นายสมชาย ใจดี (ลูกจ้าง)",
            ],
            "วันที่สำคัญ": [
                "วันเริ่มงาน: 1 มีนาคม 2567",
                "วันสิ้นสุด: 28 กุมภาพันธ์ 2568",
                "วันลงนาม: 20 กุมภาพันธ์ 2567",
            ],
            "มูลค่า": ["เงินเดือน: 85,000 บาท/เดือน"],
            "สาระสำคัญ": (
                "สัญญาจ้างงาน 1 ปีระหว่าง บริษัท เทคโนโลยี ไทย จำกัด กับ นายสมชาย ใจดี "
                "ในตำแหน่งวิศวกรซอฟต์แวร์อาวุโส อัตราเงินเดือน 85,000 บาทต่อเดือน "
                "มีผลตั้งแต่ 1 มีนาคม 2567 ถึง 28 กุมภาพันธ์ 2568"
            ),
            "ข้อสังเกต": "ควรตรวจสอบเงื่อนไขการต่อสัญญาและสวัสดิการเพิ่มเติมก่อนลงนาม",
        },
    },
    "report": {
        "filename": "รายงานผลดำเนินงาน_ตัวอย่าง.pdf",
        "is_example": True,
        "ocr_text": (
            "รายงานสรุปผลการดำเนินงาน ไตรมาสที่ 1/2567\n"
            "บริษัท กรีน เอนเนอร์จี จำกัด (มหาชน)\n\n"
            "ประจำวันที่ 31 มีนาคม 2567\n\n"
            "ภาพรวมผลการดำเนินงาน:\n"
            "รายได้รวม: 125,000,000 บาท (เพิ่มขึ้น 12% จากปีที่แล้ว)\n"
            "ต้นทุนรวม: 98,500,000 บาท\n"
            "กำไรสุทธิ: 18,500,000 บาท\n"
            "จำนวนพนักงาน: 1,250 คน\n\n"
            "โครงการสำคัญในไตรมาสนี้:\n"
            "- ติดตั้งโซลาร์เซลล์ จังหวัดนครราชสีมา แล้วเสร็จ 15 กุมภาพันธ์ 2567\n"
            "- ขยายเครือข่ายพลังงานลม อยู่ระหว่างดำเนินการ\n\n"
            "ผู้รับรองรายงาน: นายวิชัย สุขใจ ตำแหน่ง กรรมการผู้จัดการ\n"
            "วันที่จัดทำ: 10 เมษายน 2567"
        ),
        "entities": {
            "DATE": ["31 มีนาคม 2567", "15 กุมภาพันธ์ 2567", "10 เมษายน 2567"],
            "MONEY": ["125,000,000 บาท", "98,500,000 บาท", "18,500,000 บาท"],
            "ORG": ["บริษัท กรีน เอนเนอร์จี จำกัด (มหาชน)"],
            "PERSON": ["นายวิชัย สุขใจ"],
            "TAX_ID": [],
            "ADDRESS": ["จังหวัดนครราชสีมา"],
            "INVOICE_NO": [],
        },
        "classification": {
            "type": "รายงาน",
            "confidence": 0.92,
            "reason": "พบรายงานสรุปผลการดำเนินงานรายไตรมาส ระบุรายได้ ต้นทุน และกำไรสุทธิ",
        },
        "summary": {
            "คู่สัญญา": ["บริษัท กรีน เอนเนอร์จี จำกัด (มหาชน)"],
            "วันที่สำคัญ": [
                "ปิดงบไตรมาส: 31 มีนาคม 2567",
                "จัดทำรายงาน: 10 เมษายน 2567",
            ],
            "มูลค่า": [
                "รายได้รวม: 125,000,000 บาท",
                "ต้นทุนรวม: 98,500,000 บาท",
                "กำไรสุทธิ: 18,500,000 บาท",
            ],
            "สาระสำคัญ": (
                "รายงานผลการดำเนินงานไตรมาส 1/2567 ของ บริษัท กรีน เอนเนอร์จี จำกัด (มหาชน) "
                "มีรายได้รวม 125 ล้านบาท เพิ่มขึ้น 12% จากปีก่อน กำไรสุทธิ 18.5 ล้านบาท "
                "มีโครงการโซลาร์เซลล์แล้วเสร็จและโครงการพลังงานลมอยู่ระหว่างดำเนินการ"
            ),
            "ข้อสังเกต": "ควรติดตามความคืบหน้าโครงการพลังงานลมและแนวโน้มรายได้ไตรมาสถัดไป",
        },
    },
}


@st.cache_resource(show_spinner="โหลดโมเดล OCR (ครั้งแรกอาจใช้เวลา)...")
def _get_ocr_reader():
    import easyocr  # type: ignore

    return easyocr.Reader(["th", "en"], gpu=False)


def _run_pipeline(file_bytes: bytes, file_type: str, api_key: str) -> dict:
    from google import genai

    from pipeline.classifier import classify_document
    from pipeline.ner import extract_entities
    from pipeline.ocr import run_ocr
    from pipeline.summarizer import summarize_document
    from utils.pdf_utils import (
        extract_text_from_pdf,
        is_scanned_pdf,
        pdf_to_images,
    )

    client = genai.Client(api_key=api_key)

    # Stage 2: OCR
    with st.status("OCR — ดึงข้อความจากเอกสาร...", expanded=True) as s:
        if file_type == "application/pdf":
            if not is_scanned_pdf(file_bytes):
                st.write("พบ text layer — ดึงข้อความโดยตรง (ไม่ต้องใช้ OCR)")
                raw = extract_text_from_pdf(file_bytes)
                ocr_text = raw.split("--- หน้าถัดไป ---")[0].strip()
            else:
                st.write("PDF เป็น scanned image — ใช้ EasyOCR")
                images = pdf_to_images(file_bytes)
                reader = _get_ocr_reader()
                ocr_text = run_ocr(images[0], reader)
        else:
            st.write("ประมวลผลรูปภาพด้วย EasyOCR")
            image = Image.open(io.BytesIO(file_bytes))
            reader = _get_ocr_reader()
            ocr_text = run_ocr(image, reader)
        s.update(label="OCR เสร็จสิ้น", state="complete")

    # Stage 3: NER
    with st.status("NER — ดึง entity จากข้อความ...", expanded=False) as s:
        entities = extract_entities(ocr_text)
        count = sum(len(v) for v in entities.values())
        s.update(label=f"NER เสร็จสิ้น — พบ {count} entities", state="complete")

    # Stage 4: Classification
    with st.status("Classification — จำแนกประเภทเอกสาร...", expanded=False) as s:
        classification = classify_document(ocr_text, client)
        s.update(
            label=f"ประเภท: {classification.get('type', '?')} "
            f"({int(classification.get('confidence', 0) * 100)}%)",
            state="complete",
        )

    # Stage 5: Summarization
    with st.status("Summarization — สรุปเนื้อหา...", expanded=False) as s:
        summary = summarize_document(ocr_text, entities, client)
        s.update(label="สรุปเสร็จสิ้น", state="complete")

    return {
        "ocr_text": ocr_text,
        "entities": entities,
        "classification": classification,
        "summary": summary,
    }


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("📄 Document Intelligence")
    st.caption("OCR → NER → Classification → Summarization")
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Contact-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yuttapong-m/)",
        unsafe_allow_html=True,
    )
    st.divider()

    api_key = st.text_input(
        "Google Gemini API Key",
        value="",
        type="password",
        help="สมัครและรับ key ได้ที่ aistudio.google.com",
    )

    st.divider()

    uploaded = st.file_uploader(
        "อัปโหลดเอกสาร",
        type=["pdf", "png", "jpg", "jpeg"],
        help="รองรับ PDF, PNG, JPG — ประมวลผลเพียง 1 หน้าแรก",
    )

    if uploaded:
        if uploaded.type.startswith("image"):
            st.image(uploaded, caption="Preview", width=280)
        else:
            st.info(f"📎 {uploaded.name}")

    st.divider()

    process_btn = st.button(
        "ประมวลผล",
        type="primary",
        disabled=not (uploaded and api_key),
        use_container_width=True,
    )

    if not api_key:
        st.caption("กรุณาใส่ Gemini API Key ก่อน")
    elif not uploaded:
        st.caption("กรุณาอัปโหลดเอกสารก่อน")

    st.divider()

    if st.button("ดูตัวอย่างผลลัพธ์", use_container_width=True):
        st.session_state["show_examples"] = not st.session_state.get("show_examples", False)

    if st.session_state.get("show_examples"):
        st.caption("เลือกประเภทเอกสาร:")
        if st.button("📄 ใบแจ้งหนี้", use_container_width=True):
            st.session_state["result"] = _EXAMPLES["invoice"]
            st.session_state["show_examples"] = False
            st.rerun()
        if st.button("📝 สัญญาจ้างงาน", use_container_width=True):
            st.session_state["result"] = _EXAMPLES["contract"]
            st.session_state["show_examples"] = False
            st.rerun()
        if st.button("📊 รายงานผลดำเนินงาน", use_container_width=True):
            st.session_state["result"] = _EXAMPLES["report"]
            st.session_state["show_examples"] = False
            st.rerun()

# ── Main Area ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* Tab bar background */
div[data-baseweb="tab-list"] {
    gap: 8px !important;
    background: #CBD5E1 !important;
    padding: 10px 10px 0 10px !important;
    border-radius: 12px 12px 0 0 !important;
}
/* Hide default underline indicator */
div[data-baseweb="tab-highlight"],
div[data-baseweb="tab-border"] {
    display: none !important;
}
/* Inactive tab — Streamlit 1.3x uses <button> */
button[data-baseweb="tab"] {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    padding: 14px 40px !important;
    border-radius: 10px 10px 0 0 !important;
    border: none !important;
    background: #94A3B8 !important;
    color: #F1F5F9 !important;
    letter-spacing: 0.02em !important;
    min-width: 120px !important;
}
button[data-baseweb="tab"]:hover {
    background: #6B7FA8 !important;
    color: #FFFFFF !important;
}
/* Active tab */
button[aria-selected="true"][data-baseweb="tab"] {
    background: #FFFFFF !important;
    color: #1E3A5F !important;
    margin-bottom: -2px !important;
}
/* Tab content panel */
div[data-baseweb="tab-panel"] {
    border-radius: 0 0 12px 12px !important;
    padding: 24px 20px !important;
    background: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Document Intelligence Pipeline")

if not uploaded and "result" not in st.session_state:
    st.markdown(
        "**Document Intelligence Pipeline** วิเคราะห์และสกัดข้อมูลจากเอกสารภาษาไทยอัตโนมัติ "
        "รองรับเอกสารหลากหลายประเภท เช่น ใบแจ้งหนี้ สัญญา รายงาน หนังสือราชการ และเอกสารทั่วไป"
    )
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 1. ใส่ API Key")
        st.markdown(
            "กรอก **Google Gemini API Key** ในแถบด้านซ้าย "
            "รับได้ฟรีที่ Google AI Studio"
        )
    with col2:
        st.markdown("#### 2. อัปโหลดเอกสาร")
        st.markdown(
            "รองรับ **PDF, PNG, JPG, JPEG** "
            "ทั้งเอกสาร text-based และ scanned image "
            "ระบบประมวลผลหน้าแรกของเอกสาร"
        )
    with col3:
        st.markdown("#### 3. กดประมวลผล")
        st.markdown(
            "ระบบจะดึงข้อความ จำแนก entity "
            "ระบุประเภทเอกสาร และสรุปประเด็นสำคัญโดยอัตโนมัติ"
        )

    st.divider()
    st.markdown("##### ผลลัพธ์ที่ได้จากการประมวลผล")

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.info("**OCR**\nดึงข้อความจาก PDF หรือรูปภาพ รองรับทั้งภาษาไทยและอังกฤษ")
    with r2:
        st.info("**NER**\nระบุ entity สำคัญ เช่น วันที่ มูลค่า องค์กร บุคคล ที่อยู่")
    with r3:
        st.info("**Classification**\nจำแนกประเภทเอกสาร เช่น ใบแจ้งหนี้ สัญญา รายงาน")
    with r4:
        st.info("**Summary**\nสรุปสาระสำคัญ คู่สัญญา วันที่ และมูลค่าที่เกี่ยวข้อง")

    st.divider()
    st.caption(
        "ยังไม่มีเอกสาร? กดปุ่ม **ดูตัวอย่างผลลัพธ์** ในแถบด้านซ้าย "
        "เพื่อดูตัวอย่างจากใบแจ้งหนี้ สัญญาจ้างงาน หรือรายงานผลดำเนินงาน"
    )
    st.stop()

if process_btn and uploaded:
    uploaded.seek(0)
    file_bytes = uploaded.read()
    try:
        result = _run_pipeline(file_bytes, uploaded.type, api_key)
        result["filename"] = uploaded.name
        st.session_state["result"] = result
    except Exception as exc:
        st.error(f"เกิดข้อผิดพลาด: {exc}")
        st.stop()

if "result" not in st.session_state:
    st.stop()

r = st.session_state["result"]
ocr_text: str = r["ocr_text"]
entities: dict = r["entities"]
classification: dict = r["classification"]
summary: dict = r["summary"]

from utils.display import highlight_entities, render_entity_table  # noqa: E402

if r.get("is_example"):
    st.info("นี่คือข้อมูลตัวอย่าง — อัปโหลดเอกสารจริงและกด **ประมวลผล** เพื่อวิเคราะห์เอกสารของคุณ")

# ── Shared computed values ────────────────────────────────────────────────────
doc_type = classification.get("type", "ไม่ทราบ")
confidence = float(classification.get("confidence", 0))
reason = classification.get("reason", "")
conf_pct = int(confidence * 100)

full_result = {
    "file": r.get("filename", ""),
    "ocr_text": ocr_text,
    "entities": entities,
    "classification": classification,
    "summary": summary,
}
txt_lines = [
    "Document Intelligence Pipeline — ผลลัพธ์",
    f"ไฟล์: {r.get('filename', '')}",
    "",
    "=== ข้อความ OCR ===",
    ocr_text,
    "",
    "=== Entity ที่พบ ===",
    json.dumps(entities, ensure_ascii=False, indent=2),
    "",
    "=== ประเภทเอกสาร ===",
    f"{doc_type} (ความมั่นใจ {conf_pct}%)",
    f"เหตุผล: {reason}",
    "",
    "=== สรุปเนื้อหา ===",
    json.dumps(summary, ensure_ascii=False, indent=2),
]

# ── Header: filename + download buttons ──────────────────────────────────────
hcol1, hcol2, hcol3 = st.columns([3, 1, 1])
with hcol1:
    st.markdown(f"**ไฟล์:** {r.get('filename', '')}")
with hcol2:
    st.download_button(
        "⬇ JSON",
        data=json.dumps(full_result, ensure_ascii=False, indent=2),
        file_name=f"result_{r.get('filename', 'doc')}.json",
        mime="application/json",
        use_container_width=True,
    )
with hcol3:
    st.download_button(
        "⬇ TXT",
        data="\n".join(txt_lines),
        file_name=f"result_{r.get('filename', 'doc')}.txt",
        mime="text/plain; charset=utf-8",
        use_container_width=True,
    )

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_ocr, tab_ner, tab_cls, tab_sum = st.tabs(["OCR", "NER", "Classification", "Summary"])

with tab_ocr:
    st.text_area(
        "raw",
        value=ocr_text,
        height=340,
        disabled=True,
        label_visibility="collapsed",
    )

with tab_ner:
    highlighted_html = highlight_entities(ocr_text[:1500], entities)
    st.markdown(
        f'<div style="font-family:\'Sarabun\',\'Noto Sans Thai\',sans-serif;'
        f"line-height:2.2;padding:14px;background:#FAFAFA;color:#1A1A1A;"
        f'border-radius:8px;border:1px solid #E5E7EB">'
        f"{highlighted_html}</div>",
        unsafe_allow_html=True,
    )
    st.caption("สรุป entity ที่พบ:")
    render_entity_table(entities)

with tab_cls:
    color = "#27AE60" if conf_pct >= 80 else "#F39C12" if conf_pct >= 60 else "#E74C3C"
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(
            f'<div style="text-align:center;padding:18px 10px;background:{color}18;'
            f"border:2px solid {color};border-radius:12px\">"
            f'<div style="font-size:1.35em;font-weight:700;color:{color}">{doc_type}</div>'
            f'<div style="color:{color};font-size:0.88em;margin-top:4px">ความมั่นใจ {conf_pct}%</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with col2:
        if reason:
            st.info(f"เหตุผล: {reason}")

with tab_sum:
    main_point: str = summary.get("สาระสำคัญ", "")
    if main_point:
        st.markdown(f"> {main_point}")
        st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        parties: list = summary.get("คู่สัญญา", [])
        if parties:
            st.markdown("**คู่สัญญา**")
            for p in parties:
                st.markdown(f"- {p}")
    with col2:
        dates: list = summary.get("วันที่สำคัญ", [])
        if dates:
            st.markdown("**วันที่สำคัญ**")
            for d in dates:
                st.markdown(f"- {d}")
    with col3:
        amounts: list = summary.get("มูลค่า", [])
        if amounts:
            st.markdown("**มูลค่า**")
            for a in amounts:
                st.markdown(f"- {a}")

    note: str = summary.get("ข้อสังเกต", "")
    if note and note != "-":
        st.warning(f"ข้อสังเกต: {note}")
