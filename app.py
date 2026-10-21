import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# ตั้งค่าหน้าตาของโปรแกรม
st.set_page_config(page_title="ระบบบันทึกบริการรถ", layout="wide")
st.title("🚗🏍️🚛 ระบบบันทึกข้อมูลบริการรถ ประกันภัย และสรุปสถิติ (Excel ถาวร)")

# ชื่อไฟล์ Excel ที่ใช้เก็บข้อมูลหลักในระบบ
EXCEL_FILE = "data.xlsx"

# กำหนดรายชื่อหัวคอลัมน์ทั้งหมดของระบบหลังจากแยกประเภทรถครบถ้วน
column_headers = [
    "วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", 
    "รถยนต์ (คัน)", "ราคาตรวจสภาพ(รถ)", "ราคา พรบ(รถ)", "ราคาภาษี(รถ)",
    "มอเตอร์ไซค์ (คัน)", "ราคาตรวจสภาพ(มอไซค์)", "ราคา พรบ(มอไซค์)", "ราคาภาษี(มอไซค์)",
    "หกล้อ (คัน)", "ราคาค่าบริการ(หกล้อ)",
    "สิบล้อ (คัน)", "ราคาค่าบริการ(สิบล้อ)",
    "ประเภทงานทะเบียน", "ค่าบริการทะเบียน", "บริษัทประกัน", "ประเภทประกัน", "เบี้ยประกันภัย", 
    "ค่าบริการอื่นๆ", "ตรวจรวมต่อ", "เล่ม เอกสาร", "โอนย้าย", "เปลี่ยนสี", "แจ้งคอก", "รายรับอื่นๆ", 
    "ยอดรวมทั้งหมด", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"
]

# ฟังก์ชันสำหรับอ่านข้อมูลล่าสุดจากไฟล์ Excel หลัก
def load_data_from_excel():
    if os.path.exists(EXCEL_FILE):
        try:
            return pd.read_excel(EXCEL_FILE)
        except Exception:
            return pd.DataFrame(columns=column_headers)
    else:
        return pd.DataFrame(columns=column_headers)

# โหลดข้อมูลเก่าจาก Excel มารอแสดงผลในระบบ
df_existing = load_data_from_excel()

if "form_version" not in st.session_state:
    st.session_state.form_version = 0

def clear_form_fields():
    st.session_state.form_version += 1

v = str(st.session_state.form_version)

# ==================== ฟอร์มกรอกข้อมูล ====================
st.markdown("---")
st.subheader("📋 ฟอร์มบันทึกข้อมูล")
c_a, c_b, c_c = st.columns(3)
date_val = c_a.date_input("วันที่", datetime.now(), key="date_" + v)
cust_name = c_b.text_input("ชื่อ-นามสกุล ลูกค้า", key="name_" + v)
cust_phone = c_c.text_input("เบอร์โทรศัพท์", key="phone_" + v)
license_plate = c_a.text_input("ทะเบียนรถ", key="plate_" + v)

# แยกหมวดหมู่รถ 4 ประเภท และงานทะเบียน/ประกันภัย ชัดเจนด้วยระบบแท็บ
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚗 รถยนต์", "🏍️ มอเตอร์ไซค์", "🚛 รถหกล้อ", "🚚 รถสิบล้อ", "💼 ทะเบียน/ประกัน/อื่นๆ"])

with tab1:
    st.markdown("#### 🚗 ข้อมูลและราคาบริการรถยนต์")
    car_qty = st.number_input("จำนวนรถยนต์ (คัน)", min_value=0, step=1, value=None, key="car_q_" + v)
    car_check = st.number_input("ราคาค่าตรวจสภาพรถยนต์ (บาท)", min_value=0.0, value=None, key="car_c_" + v)
    car_act = st.number_input("ราคาค่า พ.ร.บ. รถยนต์ (บาท)", min_value=0.0, value=None, key="car_a_" + v)
    car_tax = st.number_input("ราคาค่าภาษี รถยนต์ (บาท)", min_value=0.0, value=None, key="car_t_" + v)

with tab2:
    st.markdown("#### 🏍️ ข้อมูลและราคาบริการมอเตอร์ไซค์")
    bike_qty = st.number_input("จำนวนมอเตอร์ไซค์ (คัน)", min_value=0, step=1, value=None, key="bike_q_" + v)
    bike_check = st.number_input("ราคาค่าตรวจสภาพมอไซค์ (บาท)", min_value=0.0, value=None, key="bike_c_" + v)
    bike_act = st.number_input("ราคาค่า พ.ร.บ. มอไซค์ (บาท)", min_value=0.0, value=None, key="bike_a_" + v)
    bike_tax = st.number_input("ราคาค่าภาษี มอไซค์ (บาท)", min_value=0.0, value=None, key="bike_t_" + v)

with tab3:
    st.markdown("#### 🚛 ข้อมูลและราคาบริการรถหกล้อ")
    w6_qty = st.number_input("จำนวนรถหกล้อ (คัน)", min_value=0, step=1, value=None, key="w6_q_" + v)
    w6_price = st.number_input("ราคาค่าบริการรถหกล้อ (บาท)", min_value=0.0, value=None, key="w6_p_" + v)

with tab4:
    st.markdown("#### 🚚 ข้อมูลและราคาบริการรถสิบล้อ")
    w10_qty = st.number_input("จำนวนรถสิบล้อ (คัน)", min_value=0, step=1, value=None, key="w10_q_" + v)
    w10_price = st.number_input("ราคาค่าบริการรถสิบล้อ (บาท)", min_value=0.0, value=None, key="w10_p_" + v)

with tab5:
    st.markdown("#### 💼 งานทะเบียนและประกันภัย")
    reg_type = st.selectbox("งานทะเบียน", ["-- เลือกประเภท --", "โอน", "จดใหม่", "ปรับสมุด"], key="reg_v_" + v)
    service_fee = st.number_input("ราคาค่าบริการงานทะเบียน (บาท)", min_value=0.0, value=None, key="fee_" + v)
    ins_company = st.selectbox("บริษัทประกัน", ["-- เลือกบริษัทประกันภัย --", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย"], key="ins_c_" + v)
    ins_type = st.selectbox("ประเภทประกัน", ["-- เลือกประเภทประกันภัย --", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"], key="ins_t_" + v)
    ins_price = st.number_input("ราคาเบี้ยประกันภัย (บาท)", min_value=0.0, value=None, key="ins_p_" + v)
    
    st.markdown("#### 🛠️ ค่าบริการและช่องเอกสารอื่นๆ")
    p_service = st.number_input("ราคา ค่าบริการอื่นๆ (บาท)", min_value=0.0, value=None, key="p_serv_" + v)
    p_check_ext = st.number_input("ราคา ตรวจรวมต่อ (บาท)", min_value=0.0, value=None, key="p_chext_" + v)
    p_book = st.number_input("ราคา เล่ม เอกสาร (บาท)", min_value=0.0, value=None, key="p_book_" + v)
    p_transfer = st.number_input("ราคา โอนย้าย (บาท)", min_value=0.0, value=None, key="p_trans_" + v)
    p_color = st.number_input("ราคา เปลี่ยนสี (บาท)", min_value=0.0, value=None, key="p_color_" + v)
    p_cage = st.number_input("ราคา แจ้งคอก (บาท)", min_value=0.0, value=None, key="p_cage_" + v)
    other_income = st.number_input("ราคาสำหรับรายรับอื่นๆ (บาท)", min_value=0.0, value=None, key="other_" + v)

# คำนวณรวมยอดเงินอัตโนมัติจากทุกช่อง
total = sum([
    car_check or 0, car_act or 0, car_tax or 0, 
    bike_check or 0, bike_act or 0, bike_tax or 0, 
    w6_price or 0, w10_price or 0,
    service_fee or 0, ins_price or 0,
    p_service or 0, p_check_ext or 0, p_book or 0, p_transfer or 0,
    p_color or 0, p_cage or 0, other_income or 0
])

st.markdown("### 💰 สรุปยอดเงิน")
p1, p2, p3 = st.columns(3)
p1.markdown(f"#### ยอดรวมทั้งหมด: `{total:,.2f}` บาท")
transfer_amt = p2.number_input("เงินโอน (บาท)", min_value=0.0, value=None, key="trans_" + v)
rem_cash = max(0.0, total - (transfer_amt or 0.0))
p3.markdown(f"#### เงินสดต้องจ่ายเพิ่ม: `{rem_cash:,.2f}` บาท" if total > 0 else "#### เงินสดต้องจ่ายเพิ่ม:")

is_debt = st.checkbox("⚠️ ลูกค้าค้างชำระ", key="debt_chk_" + v)
debt_amt = st.number_input("เงินที่ค้างชำระ (บาท)", min_value=0.0, value=None, key="debt_a_" + v) if is_debt else None

# ปุ่มบันทึกข้อมูล
if st.button("💾 บันทึกข้อมูล", type="primary", use_container_width=True):
    if not cust_name or not license_plate:
        st.error("❌ กรุณากรอก ชื่อ-นามสกุล และ ทะเบียนรถ ก่อนบันทึกข้อมูล")
    else:
        d_status = f"ค้างชำระ: {debt_amt or 0:,.2f} บ." if is_debt else "ปกติ"
        row_values = [
            date_val.strftime("%Y-%m-%d"), cust_name, cust_phone or "-", license_plate,
            car_qty or 0, car_check or "", car_act or "", car_tax or "",
            bike_qty or 0, bike_check or "", bike_act or "", bike_tax or "",
            w6_qty or 0, w6_price or "",
            w10_qty or 0, w10_price or "",
            reg_type if reg_type != "-- เลือกประเภท --" else "-", service_fee or "", 
            ins_company if ins_company != "-- เลือกบริษัทประกันภัย --" else "-", 
            ins_type if ins_type != "-- เลือกประเภทประกันภัย --" else "-", ins_price or "",
            p_service or "", p_check_ext or "", p_book or "", p_transfer or "",
            p_color or "", p_cage or "", other_income or "", total, transfer_amt or 0, rem_cash, d_status
        ]
        new_df = pd.DataFrame([row_values], columns=column_headers)
        updated_df = pd.concat([new_df, df_existing], ignore_index=True) if not df_existing.empty else new_df
        updated_df.to_excel(EXCEL_FILE, index=False)
        st.success("🎉 บันทึกข้อมูลลงไฟล์ Excel ถาวรสำเร็จ!")
        clear_form_fields()
        st.rerun()

# ==================== ส่วนแสดงตารางและระบบกรองดูรายงาน วัน เดือน ปี ====================
if not df_existing.empty:
    st.markdown("---")
    st.subheader("📊 ตารางรายงานสรุปยอดและสถิติข้อมูล (ฐานข้อมูล Excel)")
    
    df = df_existing.copy()
    df['dt_obj'] = pd.to_datetime(df['วันที่'], errors='coerce')

    report_type = st.radio("🔍 เลือกช่วงเวลาดูรายงานสถิติคันรถและรายรับ:", ["แสดงทั้งหมด", "รายงานรายวัน (วันนี้)", "รายงานรายเดือน (เดือนนี้)", "รายงานรายปี (ปีนี้)"], horizontal=True)
    
    t_str = datetime.now().strftime("%Y-%m-%d")
    c_m, c_y = datetime.now().month, datetime.now().year
    
    if report_type == "รายงานรายวัน (วันนี้)":
        df_filtered = df[df['วันที่'] == t_str]
    elif report_type == "รายงานรายเดือน (เดือนนี้)":
        df_filtered = df[df['dt_obj'].dt.month == c_m]
    elif report_type == "รายงานรายปี (ปีนี้)":
        df_filtered = df[df['dt_obj'].dt.year == c_y]
    else:
        df_filtered = df.copy()

    # ระบบคำนวณสถิติจำนวนคันรถแยกประเภทแบบละเอียดยิบตามช่วงเวลาที่กดเลือก (วัน/เดือน/ปี)
    t_cars = pd.to_numeric(df_filtered['รถยนต์ (คัน)'], errors='coerce').fillna(0).sum()
    t_bikes = pd.to_numeric(df_filtered['มอเตอร์ไซค์ (คัน)'], errors='coerce').fillna(0).sum()
    t_w6 = pd.to_numeric(df_filtered['หกล้อ (คัน)'], errors='coerce').fillna(0).sum()
    t_w10 = pd.to_numeric(df_filtered['สิบล้อ (คัน)'], errors='coerce').fillna(0).sum()
    t_money = pd.to_numeric(df_filtered['ยอดรวมทั้งหมด'], errors='coerce').fillna(0).sum()
    
    # หน้าจอสรุปยอดจำนวนรถและเงินเด่นชัด แยกประเภทครบถ้วน
    st.markdown(f"#### 📈 ยอดสรุปจำนวนรถสะสมของช่วงเวลา: `{report_type}`")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("🚗 รถยนต์รวม", f"{int(t_cars)} คัน")
    s2.metric("🏍️ มอเตอร์ไซค์รวม", f"{int(t_bikes)} คัน")
    s3.metric("🚛 รถหกล้อรวม", f"{int(t_w6)} คัน")
    s4.metric("🚚 รถสิบล้อรวม", f"{int(t_w10)} คัน")
    
    st.markdown(f"### 💰 ยอดเงินหมุนเวียนรวมในช่วงเวลาที่เลือก: <span style='color:#2b6cb0;'>{t_money:,.2f}</span> บาท", unsafe_allow_html=True)

    # แสดงตารางข้อมูลดิบ
    st.dataframe(df_filtered.drop(columns=['dt_obj'], errors='ignore'), use_container_width=True)
    
    # ระบบส่งออกไฟล์ Excel (.xlsx) ทันใจ
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_existing.to_excel(writer, index=False, sheet_name='DataLog')
