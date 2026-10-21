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

st.set_page_config(page_title="ระบบบริการรถและประกันภัย", page_icon="🚗", layout="wide")

COLUMNS = [
    "id", "วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ",
    "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)",
    "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)",
    "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)",
    "ประเภทงาน", "ค่าบริการ", "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน",
    "เบี้ยประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "ยอดชำระสะสม",
    "ยอดค้างคงเหลือ", "สถานะการจ่ายเงิน", "บันทึกล่าสุด"
]
MONEY_FIELDS = [
    "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", "ตรวจสภาพ(มอไซค์)",
    "พรบ(มอไซค์)", "ภาษี(มอไซค์)", "ค่าบริการ", "รายรับอื่นๆ", "เบี้ยประกัน"
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
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_date ON jobs(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_plate ON jobs(plate)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_customer ON jobs(customer)")
    migrate_legacy_excel()

def migrate_legacy_excel():
    # Import legacy data.xlsx only when the new database is empty.
    if not LEGACY_EXCEL.exists():
        return
    with connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
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
                "date": d, "customer": str(val("ชื่อ-นามสกุล", "ไม่ระบุ")),
                "phone": str(val("เบอร์โทร", "")), "plate": str(val("ทะเบียนรถ", "-")),
                "car_qty": int(float(val("รถยนต์ (คัน)", 0) or 0)),
                "bike_qty": int(float(val("มอเตอร์ไซค์ (คัน)", 0) or 0)),
                "car_check": float(val("ตรวจสภาพ(รถ)", 0) or 0),
                "car_act": float(val("พรบ(รถ)", 0) or 0),
                "car_tax": float(val("ภาษี(รถ)", 0) or 0),
                "bike_check": float(val("ตรวจสภาพ(มอไซค์)", 0) or 0),
                "bike_act": float(val("พรบ(มอไซค์)", 0) or 0),
                "bike_tax": float(val("ภาษี(มอไซค์)", 0) or 0),
                "job_type": str(val("ประเภทงาน", "-")),
                "service_fee": float(val("ค่าบริการ", 0) or 0),
                "other_income": float(val("รายรับอื่นๆ", 0) or 0),
                "ins_company": str(val("บริษัทประกัน", "-")),
                "ins_type": str(val("ประเภทประกัน", "-")),
                "ins_price": float(val("เบี้ยประกัน", 0) or 0),
                "total": float(val("ยอดรวม", 0) or 0),
                "transfer": float(val("เงินโอน", 0) or 0),
                "cash": float(val("เงินสด", 0) or 0),
                "paid_total": float(val("เงินโอน", 0) or 0) + float(val("เงินสด", 0) or 0),
                "balance": max(0, float(val("ยอดรวม", 0) or 0) - float(val("เงินโอน", 0) or 0) - float(val("เงินสด", 0) or 0)),
                "status": str(val("สถานะการจ่ายเงิน", "ปกติ")),
                "updated_at": datetime.now().isoformat(timespec="seconds")
            }
            if fields["balance"] <= 0:
                fields["status"] = "ชำระแล้ว"
            keys = list(fields)
            conn.execute(f"INSERT INTO jobs ({','.join(keys)}) VALUES ({','.join(['?']*len(keys))})",
                         [fields[k] for k in keys])

def get_jobs():
    with connect() as conn:
        return pd.read_sql_query("SELECT * FROM jobs ORDER BY date DESC, id DESC", conn)

def fmt_money(x):
    return f"{float(x or 0):,.2f}"

def save_job(data, job_id=None):
    data["total"] = round(sum(float(data.get(k, 0) or 0) for k in MONEY_FIELDS), 2)
    data["transfer"] = float(data.get("transfer", 0) or 0)
    data["cash"] = float(data.get("cash", 0) or 0)
    data["paid_total"] = data["transfer"] + data["cash"]
    data["balance"] = max(0, round(data["total"] - data["paid_total"], 2))
    data["status"] = "ชำระแล้ว" if data["balance"] <= 0 else ("ค้างชำระ" if data["paid_total"] <= 0 else "ชำระบางส่วน")
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        if job_id is None:
            keys = list(data)
            cur = conn.execute(f"INSERT INTO jobs ({','.join(keys)}) VALUES ({','.join(['?']*len(keys))})",
                               [data[k] for k in keys])
            return cur.lastrowid
        keys = list(data)
        conn.execute(f"UPDATE jobs SET {','.join([k+'=?' for k in keys])} WHERE id=?",
                     [data[k] for k in keys] + [job_id])
        return job_id

def delete_job(job_id):
    with connect() as conn:
        conn.execute("DELETE FROM payments WHERE job_id=?", (int(job_id),))
        conn.execute("DELETE FROM jobs WHERE id=?", (int(job_id),))

def add_payment(job_id, paid_date, method, amount, note):
    with connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (int(job_id),)).fetchone()
        if row is None:
            raise ValueError("ไม่พบรายการ")
        amount = float(amount)
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        if amount > float(row["balance"]) + 0.001:
            raise ValueError("ยอดชำระเกินยอดค้างคงเหลือ")
        conn.execute("INSERT INTO payments(job_id, paid_date, method, amount, note) VALUES(?,?,?,?,?)",
                     (int(job_id), paid_date.isoformat(), method, amount, note))
        paid_total = float(row["paid_total"]) + amount
        transfer = float(row["transfer"]) + (amount if method == "เงินโอน" else 0)
        cash = float(row["cash"]) + (amount if method == "เงินสด" else 0)
        balance = max(0, round(float(row["total"]) - paid_total, 2))
        status = "ชำระแล้ว" if balance <= 0 else "ชำระบางส่วน"
        conn.execute("""UPDATE jobs SET transfer=?, cash=?, paid_total=?, balance=?, status=?, updated_at=? WHERE id=?""",
                     (transfer, cash, paid_total, balance, status, datetime.now().isoformat(timespec="seconds"), int(job_id)))

def jobs_to_excel(df):
    out = io.BytesIO()
    export = df.copy()
    rename = {
        "id":"เลขที่", "date":"วันที่", "customer":"ชื่อ-นามสกุล", "phone":"เบอร์โทร",
        "plate":"ทะเบียนรถ", "car_qty":"รถยนต์ (คัน)", "bike_qty":"มอเตอร์ไซค์ (คัน)",
        "car_check":"ตรวจสภาพ(รถ)", "car_act":"พรบ(รถ)", "car_tax":"ภาษี(รถ)",
        "bike_check":"ตรวจสภาพ(มอไซค์)", "bike_act":"พรบ(มอไซค์)", "bike_tax":"ภาษี(มอไซค์)",
        "job_type":"ประเภทงาน", "service_fee":"ค่าบริการ", "other_income":"รายรับอื่นๆ",
        "ins_company":"บริษัทประกัน", "ins_type":"ประเภทประกัน", "ins_price":"เบี้ยประกัน",
        "total":"ยอดรวม", "transfer":"เงินโอนสะสม", "cash":"เงินสดสะสม",
        "paid_total":"ยอดชำระสะสม", "balance":"ยอดค้างคงเหลือ", "status":"สถานะการจ่ายเงิน",
        "updated_at":"บันทึกล่าสุด"
    }
    export = export.rename(columns=rename)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        export.to_excel(writer, index=False, sheet_name="รายการบริการ")
        with connect() as conn:
            pay = pd.read_sql_query("""SELECT p.id AS 'เลขที่รับชำระ', p.job_id AS 'เลขที่รายการ',
                j.customer AS 'ลูกค้า', j.plate AS 'ทะเบียนรถ', p.paid_date AS 'วันที่รับชำระ',
                p.method AS 'วิธีชำระ', p.amount AS 'จำนวนเงิน', p.note AS 'หมายเหตุ'
                FROM payments p LEFT JOIN jobs j ON j.id=p.job_id ORDER BY p.paid_date DESC, p.id DESC""", conn)
        pay.to_excel(writer, index=False, sheet_name="ประวัติรับชำระ")
    return out.getvalue()

init_db()

st.title("🚗🏍️ ระบบจัดการงานบริการรถและประกันภัย")
st.caption("บันทึกรายการ • ติดตามยอดชำระ • รายงาน • ส่งออก Excel • สำรองข้อมูล")

jobs = get_jobs()
menu = st.sidebar.radio("เมนูหลัก", ["ภาพรวมและรายงาน", "บันทึกรายการใหม่", "ค้นหา / แก้ไข / ลบ", "รับชำระหนี้", "ส่งออกและสำรองข้อมูล"])
st.sidebar.caption("ข้อมูลเก็บในไฟล์ vehicle_service.db ภายในโฟลเดอร์โปรแกรม")

if menu == "ภาพรวมและรายงาน":
    st.subheader("📊 ภาพรวมและรายงาน")
    today = date.today()
    period = st.radio("ช่วงรายงาน", ["รายวัน", "รายเดือน", "รายปี", "ทั้งหมด"], horizontal=True)
    if period == "รายวัน":
        chosen = st.date_input("เลือกวันที่", today)
        filtered = jobs[jobs["date"] == chosen.isoformat()] if not jobs.empty else jobs
    elif period == "รายเดือน":
        chosen_month = st.date_input("เลือกเดือน (เลือกวันใดก็ได้ในเดือน)", today, key="report_month")
        filtered = jobs[pd.to_datetime(jobs["date"], errors="coerce").dt.to_period("M") == pd.Period(chosen_month, freq="M")] if not jobs.empty else jobs
    elif period == "รายปี":
        year = st.number_input("เลือกปี ค.ศ.", min_value=2000, max_value=2100, value=today.year, step=1)
        filtered = jobs[pd.to_datetime(jobs["date"], errors="coerce").dt.year == int(year)] if not jobs.empty else jobs
    else:
        filtered = jobs.copy()
    if filtered.empty:
        st.info("ยังไม่มีข้อมูลในช่วงเวลาที่เลือก")
    else:
        total = pd.to_numeric(filtered["total"], errors="coerce").fillna(0).sum()
        transfer = pd.to_numeric(filtered["transfer"], errors="coerce").fillna(0).sum()
        cash = pd.to_numeric(filtered["cash"], errors="coerce").fillna(0).sum()
        balance = pd.to_numeric(filtered["balance"], errors="coerce").fillna(0).sum()
        a,b,c,d,e = st.columns(5)
        a.metric("รายการ", f"{len(filtered):,}")
        b.metric("รถยนต์", f"{int(filtered['car_qty'].sum()):,} คัน")
        c.metric("มอเตอร์ไซค์", f"{int(filtered['bike_qty'].sum()):,} คัน")
        d.metric("ยอดรวมค่าบริการ", f"{fmt_money(total)} บ.")
        e.metric("ยอดค้าง", f"{fmt_money(balance)} บ.")
        f,g,h = st.columns(3)
        f.metric("รับเงินโอนสะสม", f"{fmt_money(transfer)} บ.")
        g.metric("รับเงินสดสะสม", f"{fmt_money(cash)} บ.")
        h.metric("รับชำระสะสม", f"{fmt_money(transfer+cash)} บ.")
        st.dataframe(filtered.rename(columns={"id":"เลขที่","date":"วันที่","customer":"ชื่อ-นามสกุล","phone":"เบอร์โทร","plate":"ทะเบียนรถ","total":"ยอดรวม","transfer":"เงินโอน","cash":"เงินสด","paid_total":"ยอดชำระสะสม","balance":"ยอดค้างคงเหลือ","status":"สถานะ"}), use_container_width=True, hide_index=True)
        st.download_button("📥 ดาวน์โหลดรายงานช่วงที่เลือก (Excel)", jobs_to_excel(filtered), f"รายงานบริการ_{datetime.now():%Y%m%d_%H%M}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.markdown("#### รายการค้างชำระ")
    if not jobs.empty:
        due = jobs[pd.to_numeric(jobs["balance"], errors="coerce").fillna(0) > 0]
        if due.empty:
            st.success("ไม่มีรายการค้างชำระ")
        else:
            st.dataframe(due[["id","date","customer","plate","total","paid_total","balance","status"]].rename(columns={"id":"เลขที่","date":"วันที่","customer":"ลูกค้า","plate":"ทะเบียน","total":"ยอดรวม","paid_total":"ชำระแล้ว","balance":"ค้าง","status":"สถานะ"}), use_container_width=True, hide_index=True)

elif menu == "บันทึกรายการใหม่":
    st.subheader("📝 บันทึกรายการบริการ")
    with st.form("new_job_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        d = c1.date_input("วันที่", date.today())
        customer = c2.text_input("ชื่อ-นามสกุล *")
        phone = c3.text_input("เบอร์โทรศัพท์")
        plate = c1.text_input("ทะเบียนรถ *")
        car_qty = c2.number_input("จำนวนรถยนต์ (คัน)", min_value=0, value=0, step=1)
        bike_qty = c3.number_input("จำนวนมอเตอร์ไซค์ (คัน)", min_value=0, value=0, step=1)
        st.markdown("**รถยนต์**")
        x1,x2,x3 = st.columns(3)
        car_check = x1.number_input("ค่าตรวจสภาพรถยนต์", min_value=0.0, value=0.0, step=10.0)
        car_act = x2.number_input("ค่า พ.ร.บ. รถยนต์", min_value=0.0, value=0.0, step=10.0)
        car_tax = x3.number_input("ค่าภาษีรถยนต์", min_value=0.0, value=0.0, step=10.0)
        st.markdown("**มอเตอร์ไซค์**")
        y1,y2,y3 = st.columns(3)
        bike_check = y1.number_input("ค่าตรวจสภาพมอเตอร์ไซค์", min_value=0.0, value=0.0, step=10.0)
        bike_act = y2.number_input("ค่า พ.ร.บ. มอเตอร์ไซค์", min_value=0.0, value=0.0, step=10.0)
        bike_tax = y3.number_input("ค่าภาษีมอเตอร์ไซค์", min_value=0.0, value=0.0, step=10.0)
        st.markdown("**งานทะเบียนและประกันภัย**")
        z1,z2,z3 = st.columns(3)
        job_type = z1.selectbox("ประเภทงาน", ["-", "โอน", "จดใหม่", "ปรับสมุด", "ต่อภาษี", "อื่นๆ"])
        service_fee = z2.number_input("ค่าบริการทะเบียน", min_value=0.0, value=0.0, step=10.0)
        other_income = z3.number_input("รายรับอื่นๆ", min_value=0.0, value=0.0, step=10.0)
        ins_company = st.selectbox("บริษัทประกัน", ["-", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย", "อื่นๆ"])
        ins_type = st.selectbox("ประเภทประกัน", ["-", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"])
        ins_price = st.number_input("เบี้ยประกันภัย", min_value=0.0, value=0.0, step=100.0)
        total_preview = car_check+car_act+car_tax+bike_check+bike_act+bike_tax+service_fee+other_income+ins_price
        st.info(f"ยอดรวมอัตโนมัติ: {total_preview:,.2f} บาท")
        st.markdown("**รับเงิน ณ วันที่บันทึก**")
        p1,p2 = st.columns(2)
        transfer = p1.number_input("เงินโอน (บาท)", min_value=0.0, value=0.0, step=10.0)
        cash = p2.number_input("เงินสด (บาท)", min_value=0.0, value=0.0, step=10.0)
        st.caption(f"ยอดค้างคงเหลือโดยประมาณ: {max(0,total_preview-transfer-cash):,.2f} บาท")
        submitted = st.form_submit_button("💾 บันทึกรายการ", type="primary", use_container_width=True)
    if submitted:
        if not customer.strip() or not plate.strip():
            st.error("กรุณากรอกชื่อ-นามสกุลและทะเบียนรถ")
        elif transfer + cash > total_preview + 0.001:
            st.error("ยอดเงินโอนรวมเงินสดต้องไม่เกินยอดรวม")
        else:
            data = {
                "date": d.isoformat(), "customer": customer.strip(), "phone": phone.strip(),
                "plate": plate.strip().upper(), "car_qty": car_qty, "bike_qty": bike_qty,
                "car_check": car_check, "car_act": car_act, "car_tax": car_tax,
                "bike_check": bike_check, "bike_act": bike_act, "bike_tax": bike_tax,
                "job_type": job_type, "service_fee": service_fee, "other_income": other_income,
                "ins_company": ins_company, "ins_type": ins_type, "ins_price": ins_price,
                "transfer": transfer, "cash": cash
            }
            jid = save_job(data)
            st.success(f"บันทึกสำเร็จ เลขที่รายการ {jid}")

elif menu == "ค้นหา / แก้ไข / ลบ":
    st.subheader("🔎 ค้นหา แก้ไข และลบรายการ")
    query = st.text_input("ค้นหาจากชื่อลูกค้า ทะเบียนรถ หรือเบอร์โทร", placeholder="พิมพ์ชื่อ ทะเบียน หรือเบอร์โทร")
    results = jobs.copy()
    if query.strip() and not results.empty:
        q = query.strip().casefold()
        mask = results[["customer","plate","phone"]].astype(str).apply(lambda col: col.str.casefold().str.contains(q, regex=False)).any(axis=1)
        results = results[mask]
    if results.empty:
        st.info("ไม่พบรายการที่ตรงกับคำค้นหา")
    else:
        labels = {int(r.id): f"#{int(r.id)} | {r.date} | {r.customer} | {r.plate} | ยอด {float(r.total):,.2f} | ค้าง {float(r.balance):,.2f}" for r in results.itertuples()}
        selected = st.selectbox("เลือกรายการ", list(labels.keys()), format_func=lambda x: labels[x])
        row = results[results["id"] == selected].iloc[0]
        with st.expander("ดูรายละเอียดรายการ", expanded=True):
            st.json({k: (v.item() if hasattr(v, "item") else v) for k,v in row.to_dict().items()}, expanded=False)
        st.warning("การแก้ไขยอดรายการจะคำนวณยอดรวมและยอดค้างใหม่จากเงินสด/เงินโอนที่บันทึกไว้")
        with st.form(f"edit_{selected}"):
            c1,c2,c3 = st.columns(3)
            ed_date = c1.date_input("วันที่", pd.to_datetime(row["date"]).date())
            ed_customer = c2.text_input("ชื่อ-นามสกุล", str(row["customer"]))
            ed_phone = c3.text_input("เบอร์โทร", str(row["phone"]))
            ed_plate = c1.text_input("ทะเบียนรถ", str(row["plate"]))
            ed_car_qty = c2.number_input("จำนวนรถยนต์", min_value=0, value=int(row["car_qty"] or 0))
            ed_bike_qty = c3.number_input("จำนวนมอเตอร์ไซค์", min_value=0, value=int(row["bike_qty"] or 0))
            values = {}
            labels_money = [
                ("car_check","ตรวจสภาพรถยนต์"),("car_act","พ.ร.บ. รถยนต์"),("car_tax","ภาษีรถยนต์"),
                ("bike_check","ตรวจสภาพมอเตอร์ไซค์"),("bike_act","พ.ร.บ. มอเตอร์ไซค์"),("bike_tax","ภาษีมอเตอร์ไซค์"),
                ("service_fee","ค่าบริการ"),("other_income","รายรับอื่นๆ"),("ins_price","เบี้ยประกัน")
            ]
            cols = st.columns(3)
            for i,(key,label) in enumerate(labels_money):
                values[key] = cols[i%3].number_input(label, min_value=0.0, value=float(row[key] or 0), key=f"edit_{selected}_{key}")
            ed_job_type = st.selectbox("ประเภทงาน", ["-", "โอน", "จดใหม่", "ปรับสมุด", "ต่อภาษี", "อื่นๆ"], index=(["-", "โอน", "จดใหม่", "ปรับสมุด", "ต่อภาษี", "อื่นๆ"].index(row["job_type"]) if row["job_type"] in ["-", "โอน", "จดใหม่", "ปรับสมุด", "ต่อภาษี", "อื่นๆ"] else 0))
            ed_ins_company = st.text_input("บริษัทประกัน", str(row["ins_company"]))
            ed_ins_type = st.text_input("ประเภทประกัน", str(row["ins_type"]))
            ed_transfer = st.number_input("เงินโอนสะสม", min_value=0.0, value=float(row["transfer"] or 0))
            ed_cash = st.number_input("เงินสดสะสม", min_value=0.0, value=float(row["cash"] or 0))
            save_edit = st.form_submit_button("บันทึกการแก้ไข", type="primary", use_container_width=True)
        if save_edit:
            ed_total = sum(values.values())
            if not ed_customer.strip() or not ed_plate.strip():
                st.error("กรุณากรอกชื่อลูกค้าและทะเบียนรถ")
            elif ed_transfer + ed_cash > ed_total + 0.001:
                st.error("ยอดรับชำระรวมมากกว่ายอดรวม กรุณาตรวจสอบ")
            else:
                data = {
                    "date": ed_date.isoformat(), "customer": ed_customer.strip(), "phone": ed_phone.strip(),
                    "plate": ed_plate.strip().upper(), "car_qty": ed_car_qty, "bike_qty": ed_bike_qty,
                    **values, "job_type": ed_job_type, "ins_company": ed_ins_company.strip() or "-",
                    "ins_type": ed_ins_type.strip() or "-", "transfer": ed_transfer, "cash": ed_cash
                }
                save_job(data, int(selected))
                st.success("แก้ไขรายการเรียบร้อย")
                st.rerun()
        with st.expander("ลบรายการนี้ถาวร"):
            confirm = st.checkbox(f"ยืนยันลบรายการ #{selected} ของ {row['customer']} ({row['plate']})")
            if st.button("🗑️ ลบรายการที่เลือก", type="secondary", disabled=not confirm):
                delete_job(int(selected))
                st.success("ลบรายการและประวัติรับชำระที่เกี่ยวข้องแล้ว")
                st.rerun()

elif menu == "รับชำระหนี้":
    st.subheader("💵 รับชำระหนี้เพิ่มเติม")
    due = jobs[pd.to_numeric(jobs["balance"], errors="coerce").fillna(0) > 0] if not jobs.empty else jobs
    if due.empty:
        st.success("ไม่มีรายการค้างชำระ")
    else:
        labels = {int(r.id): f"#{int(r.id)} | {r.customer} | {r.plate} | ค้าง {float(r.balance):,.2f} บาท" for r in due.itertuples()}
        selected = st.selectbox("เลือกรายการค้างชำระ", list(labels.keys()), format_func=lambda x: labels[x])
        row = due[due["id"] == selected].iloc[0]
        st.info(f"ยอดรวม {float(row.total):,.2f} บาท | ชำระแล้ว {float(row.paid_total):,.2f} บาท | คงเหลือ {float(row.balance):,.2f} บาท")
        with st.form("payment_form"):
            paid_date = st.date_input("วันที่รับชำระ", date.today())
            method = st.radio("ช่องทางรับเงิน", ["เงินสด", "เงินโอน"], horizontal=True)
            amount = st.number_input("จำนวนเงินที่รับชำระ", min_value=0.01, max_value=max(0.01,float(row.balance)), value=min(100.0,float(row.balance)), step=10.0)
            note = st.text_input("หมายเหตุ (ไม่บังคับ)")
            submit_payment = st.form_submit_button("บันทึกรับชำระ", type="primary", use_container_width=True)
        if submit_payment:
            if amount > float(row.balance) + 0.001:
                st.error("ยอดรับชำระเกินยอดค้าง")
            else:
                add_payment(int(selected), paid_date, method, amount, note)
                st.success("บันทึกการรับชำระและปรับยอดคงเหลือแล้ว")
                st.rerun()
        with st.expander("ประวัติรับชำระของรายการนี้"):
            with connect() as conn:
                history = pd.read_sql_query("SELECT paid_date AS วันที่, method AS ช่องทาง, amount AS จำนวนเงิน, note AS หมายเหตุ FROM payments WHERE job_id=? ORDER BY paid_date DESC, id DESC", conn, params=(int(selected),))
            if history.empty:
                st.caption("ยังไม่มีประวัติรับชำระเพิ่มเติม")
            else:
                st.dataframe(history, use_container_width=True, hide_index=True)

elif menu == "ส่งออกและสำรองข้อมูล":
    st.subheader("📦 ส่งออกและสำรองข้อมูล")
    jobs = get_jobs()
    st.download_button("📥 ดาวน์โหลดข้อมูลทั้งหมดเป็น Excel", jobs_to_excel(jobs),
                       f"ข้อมูลบริการรถ_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)
    st.markdown("#### สำรองฐานข้อมูล")
    st.write("สำรองไฟล์ฐานข้อมูลและประวัติรับชำระ เพื่อเก็บไว้ก่อนแก้ไขข้อมูลหรือย้ายเครื่อง")
    if st.button("สร้างไฟล์สำรองตอนนี้", type="primary", use_container_width=True):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"vehicle_service_backup_{stamp}.db"
        with connect() as conn:
            with sqlite3.connect(backup_path) as backup_conn:
                conn.backup(backup_conn)
        st.session_state["latest_backup"] = str(backup_path)
        st.success(f"สร้างไฟล์สำรองแล้ว: {backup_path.name}")
    if st.session_state.get("latest_backup") and Path(st.session_state["latest_backup"]).exists():
        p = Path(st.session_state["latest_backup"])
        st.download_button("⬇️ ดาวน์โหลดไฟล์สำรองฐานข้อมูล (.db)", p.read_bytes(), p.name, "application/octet-stream", use_container_width=True)
    st.markdown("#### นำเข้าข้อมูลจาก Excel")
    st.warning("การนำเข้าเพิ่มข้อมูลใหม่ ไม่ได้แทนที่ข้อมูลเดิม ควรสำรองข้อมูลก่อนเสมอ")
    upload = st.file_uploader("เลือกไฟล์ Excel ที่มีคอลัมน์จากระบบเดิม", type=["xlsx"])
    if upload is not None and st.button("นำเข้าไฟล์ Excel", use_container_width=True):
        try:
            imported = pd.read_excel(upload).fillna("")
            required = {"วันที่", "ชื่อ-นามสกุล", "ทะเบียนรถ"}
            if not required.issubset(set(imported.columns)):
                st.error("ไฟล์ต้องมีคอลัมน์ วันที่, ชื่อ-นามสกุล และ ทะเบียนรถ")
            else:
                added = 0
                with connect() as conn:
                    for _, r in imported.iterrows():
                        def num(col):
                            v = r.get(col, 0)
                            return 0.0 if v == "" or pd.isna(v) else float(v)
                        def txt(col, default="-"):
                            v = r.get(col, default)
                            return default if v == "" or pd.isna(v) else str(v)
                        try:
                            d = pd.to_datetime(txt("วันที่", date.today().isoformat())).date().isoformat()
                        except Exception:
                            d = date.today().isoformat()
                        vals = {
                            "date": d, "customer": txt("ชื่อ-นามสกุล","ไม่ระบุ"), "phone": txt("เบอร์โทร",""),
                            "plate": txt("ทะเบียนรถ","-"), "car_qty": int(num("รถยนต์ (คัน)")),
                            "bike_qty": int(num("มอเตอร์ไซค์ (คัน)")), "car_check": num("ตรวจสภาพ(รถ)"),
                            "car_act": num("พรบ(รถ)"), "car_tax": num("ภาษี(รถ)"),
                            "bike_check": num("ตรวจสภาพ(มอไซค์)"), "bike_act": num("พรบ(มอไซค์)"),
                            "bike_tax": num("ภาษี(มอไซค์)"), "job_type": txt("ประเภทงาน"),
                            "service_fee": num("ค่าบริการ"), "other_income": num("รายรับอื่นๆ"),
                            "ins_company": txt("บริษัทประกัน"), "ins_type": txt("ประเภทประกัน"),
                            "ins_price": num("เบี้ยประกัน"), "transfer": num("เงินโอน"), "cash": num("เงินสด")
                        }
                        vals["total"] = sum(vals[k] for k in MONEY_FIELDS)
                        vals["paid_total"] = vals["transfer"] + vals["cash"]
                        vals["balance"] = max(0, vals["total"] - vals["paid_total"])
                        vals["status"] = "ชำระแล้ว" if vals["balance"] <= 0 else ("ค้างชำระ" if vals["paid_total"] <= 0 else "ชำระบางส่วน")
                        vals["updated_at"] = datetime.now().isoformat(timespec="seconds")
                        keys = list(vals)
                        conn.execute(f"INSERT INTO jobs ({','.join(keys)}) VALUES ({','.join(['?']*len(keys))})", [vals[k] for k in keys])
                        added += 1
                st.success(f"นำเข้าข้อมูลสำเร็จ {added} รายการ")
                st.rerun()
        except Exception as exc:
            st.error(f"นำเข้าไม่สำเร็จ กรุณาตรวจสอบรูปแบบไฟล์: {exc}")

st.sidebar.markdown("---")
st.sidebar.caption("คำแนะนำ: หากใช้งานหลายคนพร้อมกันหรือข้อมูลมีความสำคัญสูง ควรใช้ฐานข้อมูลบนเซิร์ฟเวอร์และตั้งเวลาสำรองข้อมูลอัตโนมัติ")
