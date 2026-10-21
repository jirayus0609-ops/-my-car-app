
import io
import os
import sqlite3
import shutil
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_FILE = APP_DIR / "vehicle_service.db"
BACKUP_DIR = APP_DIR / "backups"
LEGACY_EXCEL = APP_DIR / "data.xlsx"
BACKUP_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="ระบบบริการรถและประกันภัย",
    page_icon="🚗",
    layout="wide"
)

COLUMNS = [
    "id", "วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ",
    "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)", "หกล้อ (คัน)", "สิบล้อ (คัน)",
    "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)",
    "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)",
    "ตรวจสภาพ(หกล้อ)", "พรบ(หกล้อ)", "ภาษี(หกล้อ)",
    "ตรวจสภาพ(สิบล้อ)", "พรบ(สิบล้อ)", "ภาษี(สิบล้อ)",
    "ประเภทงาน", "ค่าบริการ", "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน",
    "เบี้ยประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "ยอดชำระสะสม",
    "ยอดค้างคงเหลือ", "สถานะการจ่ายเงิน", "บันทึกล่าสุด"
]

MONEY_FIELDS = [
    "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)",
    "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)",
    "ตรวจสภาพ(หกล้อ)", "พรบ(หกล้อ)", "ภาษี(หกล้อ)",
    "ตรวจสภาพ(สิบล้อ)", "พรบ(สิบล้อ)", "ภาษี(สิบล้อ)",
    "ค่าบริการ", "รายรับอื่นๆ", "เบี้ยประกัน"
]


def connect():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            customer TEXT NOT NULL,
            phone TEXT DEFAULT '',
            plate TEXT NOT NULL,
            car_qty INTEGER DEFAULT 0,
            bike_qty INTEGER DEFAULT 0,
            sixwheel_qty INTEGER DEFAULT 0,
            tenwheel_qty INTEGER DEFAULT 0,
            car_check REAL DEFAULT 0,
            car_act REAL DEFAULT 0,
            car_tax REAL DEFAULT 0,
            bike_check REAL DEFAULT 0,
            bike_act REAL DEFAULT 0,
            bike_tax REAL DEFAULT 0,
            job_type TEXT DEFAULT '-',
            service_fee REAL DEFAULT 0,
            other_income REAL DEFAULT 0,
            ins_company TEXT DEFAULT '-',
            ins_type TEXT DEFAULT '-',
            ins_price REAL DEFAULT 0,
            total REAL DEFAULT 0,
            transfer REAL DEFAULT 0,
            cash REAL DEFAULT 0,
            paid_total REAL DEFAULT 0,
            balance REAL DEFAULT 0,
            status TEXT DEFAULT 'ปกติ',
            updated_at TEXT NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            paid_date TEXT NOT NULL,
            method TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT DEFAULT '',
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """)

        existing_cols = {
            r[1] for r in conn.execute(
                "PRAGMA table_info(jobs)"
            ).fetchall()
        }

        new_cols = {
            "sixwheel_qty": "INTEGER DEFAULT 0",
            "tenwheel_qty": "INTEGER DEFAULT 0",
            "sixwheel_check": "REAL DEFAULT 0",
            "sixwheel_act": "REAL DEFAULT 0",
            "sixwheel_tax": "REAL DEFAULT 0",
            "tenwheel_check": "REAL DEFAULT 0",
            "tenwheel_act": "REAL DEFAULT 0",
            "tenwheel_tax": "REAL DEFAULT 0"
        }

        for col, definition in new_cols.items():
            if col not in existing_cols:
                conn.execute(
                    f"ALTER TABLE jobs ADD COLUMN {col} {definition}"
                )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_date ON jobs(date)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_plate ON jobs(plate)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_customer ON jobs(customer)"
        )

    migrate_legacy_excel()


def migrate_legacy_excel():
    if not LEGACY_EXCEL.exists():
        return

    with connect() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM jobs"
        ).fetchone()[0]
        if count:
            return

    try:
        old = pd.read_excel(LEGACY_EXCEL).fillna("")
    except Exception:
        return

    if old.empty:
        return

    with connect() as conn:
        for _, r in old.iterrows():

            def val(col, default=0):
                x = r.get(col, default)
                return default if x == "" or pd.isna(x) else x

            d = str(val("วันที่", date.today().isoformat()))[:10]

            if d and d != "NaT":
                try:
                    d = pd.to_datetime(d).strftime("%Y-%m-%d")
                except Exception:
                    d = date.today().isoformat()

            fields = {
                "date": d,
                "customer": str(val("ชื่อ-นามสกุล", "ไม่ระบุ")),
                "phone": str(val("เบอร์โทร", "")),
                "plate": str(val("ทะเบียนรถ", "-")),
                "car_qty": int(float(val("รถยนต์ (คัน)", 0) or 0)),
                "bike_qty": int(float(val("มอเตอร์ไซค์ (คัน)", 0) or 0)),
                "sixwheel_qty": int(float(val("หกล้อ (คัน)", 0) or 0)),
                "tenwheel_qty": int(float(val("สิบล้อ (คัน)", 0) or 0)),
                "car_check": float(val("ตรวจสภาพ(รถ)", 0) or 0),
                "car_act": float(val("พรบ(รถ)", 0) or 0),
                "car_tax": float(val("ภาษี(รถ)", 0) or 0),
                "bike_check": float(val("ตรวจสภาพ(มอไซค์)", 0) or 0),
                "bike_act": float(val("พรบ(มอไซค์)", 0) or 0),
                "bike_tax": float(val("ภาษี(มอไซค์)", 0) or 0),
                "sixwheel_check": float(val("ตรวจสภาพ(หกล้อ)", 0) or 0),
                "sixwheel_act": float(val("พรบ(หกล้อ)", 0) or 0),
                "sixwheel_tax": float(val("ภาษี(หกล้อ)", 0) or 0),
                "tenwheel_check": float(val("ตรวจสภาพ(สิบล้อ)", 0) or 0),
                "tenwheel_act": float(val("พรบ(สิบล้อ)", 0) or 0),
                "tenwheel_tax": float(val("ภาษี(สิบล้อ)", 0) or 0),
                "job_type": str(val("ประเภทงาน", "-")),
                "service_fee": float(val("ค่าบริการ", 0) or 0),
                "other_income": float(val("รายรับอื่นๆ", 0) or 0),
                "ins_company": str(val("บริษัทประกัน", "-")),
                "ins_type": str(val("ประเภทประกัน", "-")),
                "ins_price": float(val("เบี้ยประกัน", 0) or 0),
                "total": float(val("ยอดรวม", 0) or 0),
                "transfer": float(val("เงินโอน", 0) or 0),
                "cash": float(val("เงินสด", 0) or 0),
                "paid_total": (
                    float(val("เงินโอน", 0) or 0)
                    + float(val("เงินสด", 0) or 0)
                ),
                "balance": max(
                    0,
                    float(val("ยอดรวม", 0) or 0)
                    - float(val("เงินโอน", 0) or 0)
                    - float(val("เงินสด", 0) or 0)
                ),
                "status": str(val("สถานะการจ่ายเงิน", "ปกติ")),
                "updated_at": datetime.now().isoformat(timespec="seconds")
            }

            if fields["balance"] <= 0:
                fields["status"] = "ชำระแล้ว"

            keys = list(fields)

            conn.execute(
                f"INSERT INTO jobs ({','.join(keys)}) "
                f"VALUES ({','.join(['?'] * len(keys))})",
                [fields[k] for k in keys]
            )
# ==============================
# ส่วนที่ 2: ระบบจัดการข้อมูล
# ==============================

DB_FIELDS = {
    "วันที่": "date",
    "ชื่อ-นามสกุล": "customer",
    "เบอร์โทร": "phone",
    "ทะเบียนรถ": "plate",
    "รถยนต์ (คัน)": "car_qty",
    "มอเตอร์ไซค์ (คัน)": "bike_qty",
    "หกล้อ (คัน)": "sixwheel_qty",
    "สิบล้อ (คัน)": "tenwheel_qty",
    "ตรวจสภาพ(รถ)": "car_check",
    "พรบ(รถ)": "car_act",
    "ภาษี(รถ)": "car_tax",
    "ตรวจสภาพ(มอไซค์)": "bike_check",
    "พรบ(มอไซค์)": "bike_act",
    "ภาษี(มอไซค์)": "bike_tax",
    "ตรวจสภาพ(หกล้อ)": "sixwheel_check",
    "พรบ(หกล้อ)": "sixwheel_act",
    "ภาษี(หกล้อ)": "sixwheel_tax",
    "ตรวจสภาพ(สิบล้อ)": "tenwheel_check",
    "พรบ(สิบล้อ)": "tenwheel_act",
    "ภาษี(สิบล้อ)": "tenwheel_tax",
    "ประเภทงาน": "job_type",
    "ค่าบริการ": "service_fee",
    "รายรับอื่นๆ": "other_income",
    "บริษัทประกัน": "ins_company",
    "ประเภทประกัน": "ins_type",
    "เบี้ยประกัน": "ins_price",
    "ยอดรวม": "total",
    "เงินโอน": "transfer",
    "เงินสด": "cash",
    "ยอดชำระสะสม": "paid_total",
    "ยอดค้างคงเหลือ": "balance",
    "สถานะการจ่ายเงิน": "status",
    "บันทึกล่าสุด": "updated_at"
}

JOB_TYPES = [
    "ตรวจสภาพ",
    "ตรวจรวมต่อ",
    "เล่ม",
    "เอกสาร",
    "โอนย้าย",
    "เปลี่ยนสี",
    "แจ้งคอก",
    "พ.ร.บ.",
    "ต่อภาษี",
    "ประกันภัย",
    "อื่นๆ"
]


def money(value):
    try:
        return float(value or 0)
    except (ValueError, TypeError):
        return 0.0


def calculate_total(data):
    return round(
        sum(money(data.get(k, 0)) for k in MONEY_FIELDS),
        2
    )


def get_jobs():
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY date DESC, id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_job(job_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (int(job_id),)
        ).fetchone()
    return dict(row) if row else None


def save_job(data, job_id=None):
    """บันทึกหรือแก้ไขรายการ โดยคำนวณยอดรวมและยอดค้างใหม่"""

    values = dict(data)

    # คำนวณยอดรวมจากค่าตรวจ พ.ร.บ. ภาษี ค่าบริการ และเบี้ยประกัน
    total = calculate_total(values)

    transfer = money(values.get("transfer", 0))
    cash = money(values.get("cash", 0))
    paid = transfer + cash
    balance = max(0, round(total - paid, 2))

    values["total"] = total
    values["paid_total"] = paid
    values["balance"] = balance
    values["status"] = "ชำระแล้ว" if balance <= 0 else (
        "ยังไม่ชำระ" if paid <= 0 else "ชำระบางส่วน"
    )
    values["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    # แปลงชื่อช่องในหน้าจอเป็นชื่อคอลัมน์ฐานข้อมูล
    db_data = {}
    for label, column in DB_FIELDS.items():
        if label in values:
            db_data[column] = values[label]

    # รองรับข้อมูลที่ใช้ชื่อคอลัมน์ฐานข้อมูลอยู่แล้ว
    for key in [
        "date", "customer", "phone", "plate",
        "car_qty", "bike_qty", "sixwheel_qty", "tenwheel_qty",
        "car_check", "car_act", "car_tax",
        "bike_check", "bike_act", "bike_tax",
        "sixwheel_check", "sixwheel_act", "sixwheel_tax",
        "tenwheel_check", "tenwheel_act", "tenwheel_tax",
        "job_type", "service_fee", "other_income",
        "ins_company", "ins_type", "ins_price",
        "total", "transfer", "cash", "paid_total",
        "balance", "status", "updated_at"
    ]:
        if key in values:
            db_data[key] = values[key]

    required = ["date", "customer", "plate"]
    for key in required:
        if not db_data.get(key):
            raise ValueError(f"กรุณาระบุข้อมูล {key}")

    with connect() as conn:
        if job_id is None:
            keys = list(db_data.keys())
            sql = (
                f"INSERT INTO jobs ({','.join(keys)}) "
                f"VALUES ({','.join(['?'] * len(keys))})"
            )
            cur = conn.execute(
                sql, [db_data[k] for k in keys]
            )
            return cur.lastrowid

        keys = list(db_data.keys())
        assignments = ",".join(f"{k} = ?" for k in keys)
        conn.execute(
            f"UPDATE jobs SET {assignments} WHERE id = ?",
            [db_data[k] for k in keys] + [int(job_id)]
        )
        return int(job_id)


def delete_job(job_id):
    with connect() as conn:
        conn.execute(
            "DELETE FROM payments WHERE job_id = ?",
            (int(job_id),)
        )
        conn.execute(
            "DELETE FROM jobs WHERE id = ?",
            (int(job_id),)
        )


def record_payment(job_id, amount, method, paid_date, note=""):
    """บันทึกรับชำระเพิ่มเติม และเก็บประวัติการชำระ"""

    amount = money(amount)

    if amount <= 0:
        raise ValueError("จำนวนเงินต้องมากกว่า 0")

    if method not in ("เงินสด", "เงินโอน"):
        raise ValueError("กรุณาเลือกเงินสดหรือเงินโอน")

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (int(job_id),)
        ).fetchone()

        if row is None:
            raise ValueError("ไม่พบรายการที่ต้องการรับชำระ")

        job = dict(row)
        balance = money(job["balance"])

        if amount > balance + 0.001:
            raise ValueError(
                f"ยอดรับชำระเกินยอดค้าง "
                f"ยอดค้างปัจจุบัน {balance:,.2f} บาท"
            )

        conn.execute(
            """
            INSERT INTO payments
            (job_id, paid_date, method, amount, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (int(job_id), str(paid_date), method, amount, note)
        )

        if method == "เงินสด":
            job["cash"] = money(job["cash"]) + amount
        else:
            job["transfer"] = money(job["transfer"]) + amount

        paid = money(job["paid_total"]) + amount
        new_balance = max(
            0, round(money(job["total"]) - paid, 2)
        )

        status = (
            "ชำระแล้ว" if new_balance <= 0
            else "ชำระบางส่วน"
        )

        conn.execute(
            """
            UPDATE jobs
            SET cash = ?, transfer = ?, paid_total = ?,
                balance = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                job["cash"],
                job["transfer"],
                paid,
                new_balance,
                status,
                datetime.now().isoformat(timespec="seconds"),
                int(job_id)
            )
        )


def payment_history(job_id):
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT paid_date AS วันที่,
                   method AS วิธีชำระ,
                   amount AS จำนวนเงิน,
                   note AS หมายเหตุ
            FROM payments
            WHERE job_id = ?
            ORDER BY paid_date DESC, id DESC
            """,
            (int(job_id),)
        ).fetchall()
    return pd.DataFrame([dict(r) for r in rows])


def export_excel():
    """ส่งออกข้อมูลรายการและประวัติรับชำระเป็น Excel"""

    jobs = get_jobs()

    job_df = pd.DataFrame(jobs)
    if not job_df.empty:
        job_df = job_df.rename(
            columns={
                v: k for k, v in DB_FIELDS.items()
            }
        )

    with connect() as conn:
        payments = pd.read_sql_query(
            """
            SELECT p.id AS เลขที่,
                   p.job_id AS เลขที่รายการ,
                   j.customer AS ลูกค้า,
                   j.plate AS ทะเบียนรถ,
                   p.paid_date AS วันที่รับชำระ,
                   p.method AS วิธีชำระ,
                   p.amount AS จำนวนเงิน,
                   p.note AS หมายเหตุ
            FROM payments p
            LEFT JOIN jobs j ON j.id = p.job_id
            ORDER BY p.paid_date DESC, p.id DESC
            """,
            conn
        )

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        job_df.to_excel(
            writer, index=False, sheet_name="รายการบริการรถ"
        )
        payments.to_excel(
            writer, index=False, sheet_name="ประวัติรับชำระ"
        )

    output.seek(0)
    return output.getvalue()


def make_backup():
    """สำรองฐานข้อมูล SQLite"""

    if not DB_FILE.exists():
        raise FileNotFoundError("ยังไม่มีไฟล์ฐานข้อมูล")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = BACKUP_DIR / f"vehicle_service_{stamp}.db"

    # ใช้ SQLite backup API เพื่อให้สำรองได้ปลอดภัยกว่า
    with connect() as source:
        backup_conn = sqlite3.connect(destination)
        try:
            source.backup(backup_conn)
        finally:
            backup_conn.close()

    return destination
# ==============================
# ส่วนที่ 3: หน้าจอโปรแกรม
# ==============================

def render_dashboard():
    st.subheader("ภาพรวมรายรับและบริการรถ")

    jobs = get_jobs()
    if not jobs:
        st.info("ยังไม่มีข้อมูล กรุณาเริ่มบันทึกรายการใหม่")
        return

    df = pd.DataFrame(jobs)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    today = pd.Timestamp(date.today())

    daily = df[df["date"].dt.date == date.today()]
    monthly = df[
        (df["date"].dt.year == today.year)
        & (df["date"].dt.month == today.month)
    ]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("รายการวันนี้", f"{len(daily):,} รายการ")
    c2.metric("รายรับวันนี้", f"{daily['total'].sum():,.2f} บาท")
    c3.metric("รายรับเดือนนี้", f"{monthly['total'].sum():,.2f} บาท")
    c4.metric("ยอดค้างทั้งหมด", f"{df['balance'].sum():,.2f} บาท")

    st.markdown("### สรุปเงินรับชำระ")
    a, b, c = st.columns(3)
    a.metric("เงินโอนสะสม", f"{df['transfer'].sum():,.2f} บาท")
    b.metric("เงินสดสะสม", f"{df['cash'].sum():,.2f} บาท")
    c.metric("ยอดชำระสะสม", f"{df['paid_total'].sum():,.2f} บาท")

    st.markdown("### จำนวนรถที่ให้บริการ")
    x, y, z, w = st.columns(4)
    x.metric("รถยนต์", f"{df['car_qty'].sum():,.0f} คัน")
    y.metric("มอเตอร์ไซค์", f"{df['bike_qty'].sum():,.0f} คัน")
    z.metric("รถหกล้อ", f"{df['sixwheel_qty'].sum():,.0f} คัน")
    w.metric("รถสิบล้อ", f"{df['tenwheel_qty'].sum():,.0f} คัน")

    st.markdown("### รายการล่าสุด")
    display = df.sort_values(
        "date", ascending=False
    ).head(20).copy()

    display["date"] = display["date"].dt.strftime("%Y-%m-%d")
    display = display.rename(columns={
        "date": "วันที่",
        "customer": "ลูกค้า",
        "plate": "ทะเบียนรถ",
        "job_type": "ประเภทงาน",
        "total": "ยอดรวม",
        "paid_total": "ชำระแล้ว",
        "balance": "ยอดค้าง",
        "status": "สถานะ"
    })

    show_cols = [
        "วันที่", "customer", "ทะเบียนรถ",
        "ประเภทงาน", "ยอดรวม", "ชำระแล้ว",
        "ยอดค้าง", "สถานะ"
    ]
    show_cols = [c for c in show_cols if c in display.columns]
    st.dataframe(display[show_cols], use_container_width=True)


def render_new_job():
    st.subheader("บันทึกรายการบริการรถใหม่")

    with st.form("new_job_form"):
        left, right = st.columns(2)

        with left:
            job_date = st.date_input("วันที่", value=date.today())
            customer = st.text_input("ชื่อลูกค้า *")
            phone = st.text_input("เบอร์โทรศัพท์")
            plate = st.text_input("ทะเบียนรถ *")
            job_type = st.selectbox("ประเภทงาน", JOB_TYPES)

        with right:
            ins_company = st.text_input("บริษัทประกัน")
            ins_type = st.selectbox(
                "ประเภทประกัน",
                ["-", "พ.ร.บ.", "ประกันชั้น 1", "ประกันชั้น 2+",
                 "ประกันชั้น 3+", "ประกันชั้น 3", "อื่นๆ"]
            )
            ins_price = st.number_input(
                "เบี้ยประกัน (บาท)", min_value=0.0, step=100.0
            )
            service_fee = st.number_input(
                "ค่าบริการ (บาท)", min_value=0.0, step=10.0
            )
            other_income = st.number_input(
                "รายรับอื่นๆ (บาท)", min_value=0.0, step=10.0
            )

        st.markdown("### จำนวนรถ")
        q1, q2, q3, q4 = st.columns(4)
        car_qty = q1.number_input("รถยนต์ (คัน)", min_value=0, step=1)
        bike_qty = q2.number_input("มอเตอร์ไซค์ (คัน)", min_value=0, step=1)
        sixwheel_qty = q3.number_input("หกล้อ (คัน)", min_value=0, step=1)
        tenwheel_qty = q4.number_input("สิบล้อ (คัน)", min_value=0, step=1)

        st.markdown("### รถยนต์")
        a, b, c = st.columns(3)
        car_check = a.number_input("ค่าตรวจสภาพรถยนต์", min_value=0.0, step=10.0)
        car_act = b.number_input("พ.ร.บ. รถยนต์", min_value=0.0, step=10.0)
        car_tax = c.number_input("ภาษีรถยนต์", min_value=0.0, step=10.0)

        st.markdown("### มอเตอร์ไซค์")
        a, b, c = st.columns(3)
        bike_check = a.number_input("ค่าตรวจสภาพมอเตอร์ไซค์", min_value=0.0, step=10.0)
        bike_act = b.number_input("พ.ร.บ. มอเตอร์ไซค์", min_value=0.0, step=10.0)
        bike_tax = c.number_input("ภาษีมอเตอร์ไซค์", min_value=0.0, step=10.0)

        st.markdown("### รถหกล้อ")
        a, b, c = st.columns(3)
        sixwheel_check = a.number_input("ค่าตรวจสภาพหกล้อ", min_value=0.0, step=10.0)
        sixwheel_act = b.number_input("พ.ร.บ. หกล้อ", min_value=0.0, step=10.0)
        sixwheel_tax = c.number_input("ภาษีหกล้อ", min_value=0.0, step=10.0)

        st.markdown("### รถสิบล้อ")
        a, b, c = st.columns(3)
        tenwheel_check = a.number_input("ค่าตรวจสภาพสิบล้อ", min_value=0.0, step=10.0)
        tenwheel_act = b.number_input("พ.ร.บ. สิบล้อ", min_value=0.0, step=10.0)
        tenwheel_tax = c.number_input("ภาษีสิบล้อ", min_value=0.0, step=10.0)

        total = (
            car_check + car_act + car_tax
            + bike_check + bike_act + bike_tax
            + sixwheel_check + sixwheel_act + sixwheel_tax
            + tenwheel_check + tenwheel_act + tenwheel_tax
            + service_fee + other_income + ins_price
        )

        st.markdown(f"### ยอดรวมก่อนรับชำระ: {total:,.2f} บาท")

        st.markdown("### รับเงินครั้งแรก")
        p1, p2 = st.columns(2)
        transfer = p1.number_input("เงินโอน (บาท)", min_value=0.0, step=10.0)
        cash = p2.number_input("เงินสด (บาท)", min_value=0.0, step=10.0)

        st.caption(
            f"ยอดรับชำระ {transfer + cash:,.2f} บาท | "
            f"ยอดคงเหลือ {max(0, total - transfer - cash):,.2f} บาท"
        )

        submitted = st.form_submit_button(
            "บันทึกรายการ", type="primary", use_container_width=True
        )

    if submitted:
        if not customer.strip() or not plate.strip():
            st.error("กรุณากรอกชื่อลูกค้าและทะเบียนรถ")
            return

        if transfer + cash > total + 0.001:
            st.error("ยอดเงินรับชำระเกินยอดรวม กรุณาตรวจสอบ")
            return

        data = {
            "วันที่": job_date.isoformat(),
            "ชื่อ-นามสกุล": customer.strip(),
            "เบอร์โทร": phone.strip(),
            "ทะเบียนรถ": plate.strip(),
            "รถยนต์ (คัน)": car_qty,
            "มอเตอร์ไซค์ (คัน)": bike_qty,
            "หกล้อ (คัน)": sixwheel_qty,
            "สิบล้อ (คัน)": tenwheel_qty,
            "ตรวจสภาพ(รถ)": car_check,
            "พรบ(รถ)": car_act,
            "ภาษี(รถ)": car_tax,
            "ตรวจสภาพ(มอไซค์)": bike_check,
            "พรบ(มอไซค์)": bike_act,
            "ภาษี(มอไซค์)": bike_tax,
            "ตรวจสภาพ(หกล้อ)": sixwheel_check,
            "พรบ(หกล้อ)": sixwheel_act,
            "ภาษี(หกล้อ)": sixwheel_tax,
            "ตรวจสภาพ(สิบล้อ)": tenwheel_check,
            "พรบ(สิบล้อ)": tenwheel_act,
            "ภาษี(สิบล้อ)": tenwheel_tax,
            "ประเภทงาน": job_type,
            "ค่าบริการ": service_fee,
            "รายรับอื่นๆ": other_income,
            "บริษัทประกัน": ins_company,
            "ประเภทประกัน": ins_type,
            "เบี้ยประกัน": ins_price,
            "เงินโอน": transfer,
            "เงินสด": cash
        }

        try:
            new_id = save_job(data)
            st.success(f"บันทึกรายการสำเร็จ เลขที่ {new_id}")
            st.rerun()
        except Exception as e:
            st.error(f"บันทึกไม่สำเร็จ: {e}")


def render_search():
    st.subheader("ค้นหา แก้ไข และลบรายการ")

    jobs = get_jobs()
    if not jobs:
        st.info("ยังไม่มีรายการให้ค้นหา")
        return

    df = pd.DataFrame(jobs)
    keyword = st.text_input("ค้นหาด้วยชื่อลูกค้า ทะเบียนรถ หรือเบอร์โทร")

    if keyword.strip():
        mask = (
            df["customer"].astype(str).str.contains(keyword, case=False, na=False, regex=False)
            | df["plate"].astype(str).str.contains(keyword, case=False, na=False, regex=False)
            | df["phone"].astype(str).str.contains(keyword, case=False, na=False, regex=False)
        )
        df = df[mask]

    if df.empty:
        st.warning("ไม่พบข้อมูลที่ค้นหา")
        return

    df = df.sort_values(["date", "id"], ascending=False)

    st.dataframe(
        df[[
            "id", "date", "customer", "phone", "plate",
            "job_type", "total", "paid_total", "balance", "status"
        ]].rename(columns={
            "id": "เลขที่",
            "date": "วันที่",
            "customer": "ลูกค้า",
            "phone": "โทรศัพท์",
            "plate": "ทะเบียนรถ",
            "job_type": "ประเภทงาน",
            "total": "ยอดรวม",
            "paid_total": "ชำระแล้ว",
            "balance": "ยอดค้าง",
            "status": "สถานะ"
        }),
        use_container_width=True
    )

    ids = [int(i) for i in df["id"].tolist()]
    selected_id = st.selectbox("เลือกรายการที่ต้องการจัดการ", ids)
    job = get_job(selected_id)

    if not job:
        return

    st.markdown(f"### รายการเลขที่ {selected_id}")
    st.write(
        f"ลูกค้า: {job['customer']} | ทะเบียน: {job['plate']} | "
        f"ยอดรวม: {job['total']:,.2f} บาท | "
        f"ยอดค้าง: {job['balance']:,.2f} บาท"
    )

    action = st.radio(
        "เลือกการทำงาน",
        ["ดูรายละเอียด", "แก้ไขข้อมูล", "ลบรายการ"],
        horizontal=True,
        key=f"action_{selected_id}"
    )

    if action == "ดูรายละเอียด":
        st.json(job)
        hist = payment_history(selected_id)
        st.markdown("#### ประวัติการรับชำระ")
        if hist.empty:
            st.info("ยังไม่มีประวัติการรับชำระแยก")
        else:
            st.dataframe(hist, use_container_width=True)

    elif action == "แก้ไขข้อมูล":
        st.warning(
            "การแก้ไขยอดเงินจะคำนวณยอดค้างใหม่ "
            "โปรดตรวจสอบข้อมูลก่อนบันทึก"
        )

        with st.form(f"edit_{selected_id}"):
            customer = st.text_input("ชื่อลูกค้า", value=job["customer"])
            phone = st.text_input("เบอร์โทร", value=job["phone"] or "")
            plate = st.text_input("ทะเบียนรถ", value=job["plate"])
            job_date = st.date_input(
                "วันที่",
                value=date.fromisoformat(job["date"])
            )
            job_type = st.selectbox(
                "ประเภทงาน",
                JOB_TYPES,
                index=JOB_TYPES.index(job["job_type"])
                if job["job_type"] in JOB_TYPES else 0
            )

            st.markdown("#### จำนวนรถ")
            car_qty = st.number_input(
                "รถยนต์ (คัน)", min_value=0,
                value=int(job["car_qty"] or 0), step=1
            )
            bike_qty = st.number_input(
                "มอเตอร์ไซค์ (คัน)", min_value=0,
                value=int(job["bike_qty"] or 0), step=1
            )
            sixwheel_qty = st.number_input(
                "หกล้อ (คัน)", min_value=0,
                value=int(job["sixwheel_qty"] or 0), step=1
            )
            tenwheel_qty = st.number_input(
                "สิบล้อ (คัน)", min_value=0,
                value=int(job["tenwheel_qty"] or 0), step=1
            )

            st.markdown("#### ค่าบริการรถยนต์")
            car_check = st.number_input(
                "ค่าตรวจรถยนต์", min_value=0.0,
                value=money(job["car_check"]), step=10.0
            )
            car_act = st.number_input(
                "พ.ร.บ. รถยนต์", min_value=0.0,
                value=money(job["car_act"]), step=10.0
            )
            car_tax = st.number_input(
                "ภาษีรถยนต์", min_value=0.0,
                value=money(job["car_tax"]), step=10.0
            )

            st.markdown("#### ค่าบริการมอเตอร์ไซค์")
            bike_check = st.number_input(
                "ค่าตรวจมอเตอร์ไซค์", min_value=0.0,
                value=money(job["bike_check"]), step=10.0
            )
            bike_act = st.number_input(
                "พ.ร.บ. มอเตอร์ไซค์", min_value=0.0,
                value=money(job["bike_act"]), step=10.0
            )
            bike_tax = st.number_input(
                "ภาษีมอเตอร์ไซค์", min_value=0.0,
                value=money(job["bike_tax"]), step=10.0
            )

            st.markdown("#### ค่าบริการหกล้อ")
            sixwheel_check = st.number_input(
                "ค่าตรวจหกล้อ", min_value=0.0,
                value=money(job["sixwheel_check"]), step=10.0
            )
            sixwheel_act = st.number_input(
                "พ.ร.บ. หกล้อ", min_value=0.0,
                value=money(job["sixwheel_act"]), step=10.0
            )
            sixwheel_tax = st.number_input(
                "ภาษีหกล้อ", min_value=0.0,
                value=money(job["sixwheel_tax"]), step=10.0
            )

            st.markdown("#### ค่าบริการสิบล้อ")
            tenwheel_check = st.number_input(
                "ค่าตรวจสิบล้อ", min_value=0.0,
                value=money(job["tenwheel_check"]), step=10.0
            )
            tenwheel_act = st.number_input(
                "พ.ร.บ. สิบล้อ", min_value=0.0,
                value=money(job["tenwheel_act"]), step=10.0
            )
            tenwheel_tax = st.number_input(
                "ภาษีสิบล้อ", min_value=0.0,
                value=money(job["tenwheel_tax"]), step=10.0
            )

            service_fee = st.number_input(
                "ค่าบริการ", min_value=0.0,
                value=money(job["service_fee"]), step=10.0
            )
            other_income = st.number_input(
                "รายรับอื่นๆ", min_value=0.0,
                value=money(job["other_income"]), step=10.0
            )
            ins_company = st.text_input(
                "บริษัทประกัน", value=job["ins_company"] or ""
            )
            ins_type = st.text_input(
                "ประเภทประกัน", value=job["ins_type"] or ""
            )
            ins_price = st.number_input(
                "เบี้ยประกัน", min_value=0.0,
                value=money(job["ins_price"]), step=100.0
            )

            st.caption(
                "ช่องเงินโอนและเงินสดเดิมจะไม่ถูกแก้ไขจากแบบฟอร์มนี้"
            )

            save_edit = st.form_submit_button(
                "บันทึกการแก้ไข", type="primary"
            )

        if save_edit:
            data = {
                "วันที่": job_date.isoformat(),
                "ชื่อ-นามสกุล": customer.strip(),
                "เบอร์โทร": phone.strip(),
                "ทะเบียนรถ": plate.strip(),
                "รถยนต์ (คัน)": car_qty,
                "มอเตอร์ไซค์ (คัน)": bike_qty,
                "หกล้อ (คัน)": sixwheel_qty,
                "สิบล้อ (คัน)": tenwheel_qty,
                "ตรวจสภาพ(รถ)": car_check,
                "พรบ(รถ)": car_act,
                "ภาษี(รถ)": car_tax,
                "ตรวจสภาพ(มอไซค์)": bike_check,
                "พรบ(มอไซค์)": bike_act,
                "ภาษี(มอไซค์)": bike_tax,
                "ตรวจสภาพ(หกล้อ)": sixwheel_check,
                "พรบ(หกล้อ)": sixwheel_act,
                "ภาษี(หกล้อ)": sixwheel_tax,
                "ตรวจสภาพ(สิบล้อ)": tenwheel_check,
                "พรบ(สิบล้อ)": tenwheel_act,
                "ภาษี(สิบล้อ)": tenwheel_tax,
                "ประเภทงาน": job_type,
                "ค่าบริการ": service_fee,
                "รายรับอื่นๆ": other_income,
                "บริษัทประกัน": ins_company,
                "ประเภทประกัน": ins_type,
                "เบี้ยประกัน": ins_price,
                "เงินโอน": money(job["transfer"]),
                "เงินสด": money(job["cash"])
            }

            if not customer.strip() or not plate.strip():
                st.error("กรุณากรอกชื่อลูกค้าและทะเบียนรถ")
            else:
                try:
                    save_job(data, job_id=selected_id)
                    st.success("แก้ไขข้อมูลเรียบร้อย")
                    st.rerun()
                except Exception as e:
                    st.error(f"แก้ไขไม่สำเร็จ: {e}")

    elif action == "ลบรายการ":
        st.error("การลบรายการไม่สามารถย้อนกลับได้")
        confirm = st.checkbox(
            f"ยืนยันลบรายการเลขที่ {selected_id}",
            key=f"confirm_delete_{selected_id}"
        )

        if st.button(
            "ยืนยันลบรายการ",
            type="primary",
            disabled=not confirm
        ):
            delete_job(selected_id)
            st.success("ลบรายการเรียบร้อย")
            st.rerun()


def render_payments():
    st.subheader("รับชำระยอดค้าง")

    jobs = get_jobs()
    outstanding = [j for j in jobs if money(j["balance"]) > 0]

    if not outstanding:
        st.success("ไม่มีรายการค้างชำระ")
        return

    df = pd.DataFrame(outstanding)
    st.dataframe(
        df[[
            "id", "date", "customer", "plate",
            "total", "paid_total", "balance"
        ]].rename(columns={
            "id": "เลขที่",
            "date": "วันที่",
            "customer": "ลูกค้า",
            "plate": "ทะเบียน",
            "total": "ยอดรวม",
            "paid_total": "ชำระสะสม",
            "balance": "ยอดค้าง"
        }),
        use_container_width=True
    )

    options = {
        f"#{j['id']} | {j['customer']} | {j['plate']} | "
        f"ค้าง {money(j['balance']):,.2f} บาท": j["id"]
        for j in outstanding
    }

    selected = st.selectbox(
        "เลือกรายการรับชำระ",
        list(options.keys())
    )
    job_id = options[selected]
    job = get_job(job_id)

    st.metric("ยอดค้างปัจจุบัน", f"{money(job['balance']):,.2f} บาท")

    with st.form("payment_form"):
        paid_date = st.date_input("วันที่รับชำระ", value=date.today())
        method = st.radio(
            "วิธีรับชำระ",
            ["เงินสด", "เงินโอน"],
            horizontal=True
        )
        amount = st.number_input(
            "จำนวนเงินที่รับ (บาท)",
            min_value=0.01,
            max_value=max(0.01, money(job["balance"])),
            value=min(100.0, money(job["balance"])),
            step=10.0
        )
        note = st.text_input("หมายเหตุ")
        submit = st.form_submit_button(
            "บันทึกรับชำระ", type="primary"
        )

    if submit:
        try:
            record_payment(
                job_id,
                amount,
                method,
                paid_date.isoformat(),
                note
            )
            st.success("บันทึกรับชำระเรียบร้อย")
            st.rerun()
        except Exception as e:
            st.error(f"บันทึกไม่สำเร็จ: {e}")

    st.markdown("### ประวัติรับชำระของรายการนี้")
    hist = payment_history(job_id)
    if hist.empty:
        st.info("ยังไม่มีประวัติการรับชำระเพิ่มเติม")
    else:
        st.dataframe(hist, use_container_width=True)


def render_reports():
    st.subheader("รายงานรายรับ")

    jobs = get_jobs()
    if not jobs:
        st.info("ยังไม่มีข้อมูลสำหรับรายงาน")
        return

    df = pd.DataFrame(jobs)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    mode = st.radio(
        "ช่วงเวลารายงาน",
        ["รายวัน", "รายเดือน", "รายปี", "ทั้งหมด"],
        horizontal=True
    )

    if mode == "รายวัน":
        chosen = st.date_input("เลือกวันที่", value=date.today())
        df = df[df["date"].dt.date == chosen]

    elif mode == "รายเดือน":
        today = date.today()
        chosen_month = st.selectbox(
            "เดือน",
            list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda x: f"{x:02d}"
        )
        chosen_year = st.number_input(
            "ปี ค.ศ.",
            min_value=2000,
            max_value=2100,
            value=today.year,
            step=1
        )
        df = df[
            (df["date"].dt.month == chosen_month)
            & (df["date"].dt.year == chosen_year)
        ]

    elif mode == "รายปี":
        years = sorted(
            df["date"].dropna().dt.year.unique().tolist()
        )
        if years:
            year = st.selectbox("เลือกปี ค.ศ.", years, index=len(years)-1)
            df = df[df["date"].dt.year == year]

    if df.empty:
        st.warning("ไม่พบรายการในช่วงเวลาที่เลือก")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("จำนวนรายการ", f"{len(df):,}")
    c2.metric("ยอดรวม", f"{df['total'].sum():,.2f} บาท")
    c3.metric("เงินโอน", f"{df['transfer'].sum():,.2f} บาท")
    c4.metric("เงินสด", f"{df['cash'].sum():,.2f} บาท")

    st.metric("ยอดค้างในรายการ", f"{df['balance'].sum():,.2f} บาท")

    summary = df.groupby("date", dropna=False).agg(
        จำนวนรายการ=("id", "count"),
        ยอดรวม=("total", "sum"),
        เงินโอน=("transfer", "sum"),
        เงินสด=("cash", "sum"),
        ยอดค้าง=("balance", "sum")
    ).reset_index()

    summary["date"] = summary["date"].dt.strftime("%Y-%m-%d")
    st.markdown("### สรุปแยกตามวันที่")
    st.dataframe(summary, use_container_width=True)

    st.markdown("### รายการในช่วงเวลาที่เลือก")
    st.dataframe(
        df[[
            "id", "date", "customer", "plate", "job_type",
            "total", "transfer", "cash", "paid_total",
            "balance", "status"
        ]].rename(columns={
            "id": "เลขที่",
            "date": "วันที่",
            "customer": "ลูกค้า",
            "plate": "ทะเบียน",
            "job_type": "ประเภทงาน",
            "total": "ยอดรวม",
            "transfer": "เงินโอน",
            "cash": "เงินสด",
            "paid_total": "ชำระสะสม",
            "balance": "ยอดค้าง",
            "status": "สถานะ"
        }),
        use_container_width=True
    )


def render_backup():
    st.subheader("ส่งออกและสำรองข้อมูล")

    st.write(
        "ส่งออกข้อมูลรายการและประวัติรับชำระเป็น Excel "
        "หรือสร้างไฟล์สำรองฐานข้อมูล SQLite"
    )

    a, b = st.columns(2)

    with a:
        try:
            excel_data = export_excel()
            st.download_button(
                "ดาวน์โหลดรายงาน Excel",
                data=excel_data,
                file_name=f"รายงานบริการรถ_{date.today().isoformat()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"สร้าง Excel ไม่สำเร็จ: {e}")

    with b:
        if st.button("สร้างไฟล์สำรองฐานข้อมูล", use_container_width=True):
            try:
                backup_path = make_backup()
                st.success(f"สร้างไฟล์สำรองแล้ว: {backup_path.name}")
                st.download_button(
                    "ดาวน์โหลดไฟล์สำรอง",
                    data=backup_path.read_bytes(),
                    file_name=backup_path.name,
                    mime="application/octet-stream"
                )
            except Exception as e:
                st.error(f"สำรองข้อมูลไม่สำเร็จ: {e}")


# ==============================
# เริ่มโปรแกรม
# ==============================

init_db()

st.title("🚗 ระบบจัดการบริการรถและประกันภัย")
st.caption("บันทึกรายการ | ตรวจสภาพ | พ.ร.บ. | ภาษี | ประกัน | รับชำระ")

menu = st.sidebar.radio(
    "เมนูหลัก",
    [
        "ภาพรวม",
        "บันทึกรายการใหม่",
        "ค้นหา / แก้ไข / ลบ",
        "รับชำระยอดค้าง",
        "รายงานรายรับ",
        "ส่งออก / สำรองข้อมูล"
    ]
)

if menu == "ภาพรวม":
    render_dashboard()
elif menu == "บันทึกรายการใหม่":
    render_new_job()
elif menu == "ค้นหา / แก้ไข / ลบ":
    render_search()
elif menu == "รับชำระยอดค้าง":
    render_payments()
elif menu == "รายงานรายรับ":
    render_reports()
elif menu == "ส่งออก / สำรองข้อมูล":
    render_backup()
