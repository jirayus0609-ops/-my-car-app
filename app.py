import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# ตั้งค่าหน้าตาของโปรแกรม
st.set_page_config(page_title="ระบบบันทึกบริการรถ", layout="wide")
st.title("🚗 ระบบบันทึกข้อมูลบริการรถ ประกันภัย และสรุปสถิติ (Excel ถาวร)")

# ชื่อไฟล์ Excel ที่ใช้เก็บข้อมูลหลักในระบบ
EXCEL_FILE = "data.xlsx"

# กำหนดรายชื่อหัวคอลัมน์ทั้งหมดของระบบ (36 คอลัมน์)
column_headers = [
    "วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", 
    "รถยนต์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)",
    "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)",
    "หกล้อ (คัน)", "ตรวจสภาพ(หกล้อ)", "พรบ(หกล้อ)", "ภาษี(หกล้อ)",
    "สิบล้อ (คัน)", "ตรวจสภาพ(สิบล้อ)", "พรบ(สิบล้อ)", "ภาษี(สิบล้อ)",
    "บริษัทประกัน", "ประเภทประกัน", "เบี้ยประกันภัย", 
    "โอน", "จดใหม่", "ปรับสมุด", "ค่าบริการ", "ตรวจรวมต่อ", "เล่ม เอกสาร", "โอนย้าย", "เปลี่ยนสี", "แจ้งคอก", "รายรับอื่นๆ", 
    "ยอดรวมทั้งหมด", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"
]

# ฟังก์ชันอ่านข้อมูลแบบปลอดภัยสูงสุด (หากไฟล์เดิมมีปัญหาหรือบั๊ก จะเคลียร์ทำใหม่ให้ทันที)
def load_data_from_excel():
    if os.path.exists(EXCEL_FILE):
        try:
            df_read = pd.read_excel(EXCEL_FILE)
            # ล้างคอลัมน์ที่เป็นค่าขยะค้างในระบบทิ้งออกไปทั้งหมด
            df_read = df_read[[c for c in df_read.columns if c in column_headers]]
            # เพิ่มคอลัมน์ที่ขาดหายไปให้ครบโครงสร้าง 36 คอลัมน์เป๊ะๆ
            for col in column_headers:
                if col not in df_read.columns:
                    df_read[col] = ""
            return df_read[column_headers]
        except Exception:
            pass
    return pd.DataFrame(columns=column_headers)

# โหลดข้อมูลเริ่มใช้งานใหม่
df_existing = load_data_from_excel()

if "form_version" not in st.session_state:
    st.session_state.form_version = 0

def clear_form_fields():
    st.session_state.form_version += 1

v = str(st.session_state.form_version)

# ==================== ฟอร์มกรอกข้อมูล ====================
st.markdown("---")
st.subheader("📋 ฟอร์มบันทึกข้อมูลใหม่")
c_a, c_b, c_c = st.columns(3)
date_val = c_a.date_input("วันที่", datetime.now(), key="date_" + v)
cust_name = c_b.text_input("ชื่อ-นามสกุล ลูกค้า", key="name_" + v)
cust_phone = c_c.text_input("เบอร์โทรศัพท์", key="phone_" + v)
license_plate = c_a.text_input("ทะเบียนรถ", key="plate_" + v)

# แท็บแบ่งประเภทรถทั้ง 4 ประเภท
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚗 รถยนต์", "🏍️ มอเตอร์ไซค์", "🚛 รถหกล้อ", "🚚 รถสิบล้อ", "💼 ทะเบียน/ประกัน/ค่าบริการ"])

with tab1:
    st.markdown("#### 🚗 ข้อมูลบริการรถยนต์")
    car_qty = st.number_input("จำนวนรถยนต์ (คัน)", min_value=0, step=1, value=None, key="car_q_" + v)
    car_check = st.number_input("ค่าตรวจสภาพรถยนต์ (บาท)", min_value=0.0, value=None, key="car_c_" + v)
    car_act = st.number_input("ค่า พ.ร.บ. รถยนต์ (บาท)", min_value=0.0, value=None, key="car_a_" + v)
    car_tax = st.number_input("ค่าภาษี รถยนต์ (บาท)", min_value=0.0, value=None, key="car_t_" + v)

with tab2:
    st.markdown("#### 🏍️ ข้อมูลบริการมอเตอร์ไซค์")
    bike_qty = st.number_input("จำนวนมอเตอร์ไซค์ (คัน)", min_value=0, step=1, value=None, key="bike_q_" + v)
    bike_check = st.number_input("ค่าตรวจสภาพมอไซค์ (บาท)", min_value=0.0, value=None, key="bike_c_" + v)
    bike_act = st.number_input("ค่า พ.ร.บ. มอไซค์ (บาท)", min_value=0.0, value=None, key="bike_a_" + v)
    bike_tax = st.number_input("ค่าภาษี มอไซค์ (บาท)", min_value=0.0, value=None, key="bike_t_" + v)

with tab3:
    st.markdown("#### 🚛 ข้อมูลบริการรถหกล้อ")
    w6_qty = st.number_input("จำนวนรถหกล้อ (คัน)", min_value=0, step=1, value=None, key="w6_q_" + v)
    w6_check = st.number_input("ค่าตรวจสภาพรถหกล้อ (บาท)", min_value=0.0, value=None, key="w6_c_" + v)
    w6_act = st.number_input("ค่า พ.ร.บ. รถหกล้อ (บาท)", min_value=0.0, value=None, key="w6_a_" + v)
    w6_tax = st.number_input("ค่าภาษี รถหกล้อ (บาท)", min_value=0.0, value=None, key="w6_t_" + v)

with tab4:
    st.markdown("#### 🚚 ข้อมูลบริการรถสิบล้อ")
    w10_qty = st.number_input("จำนวนรถสิบล้อ (คัน)", min_value=0, step=1, value=None, key="w10_q_" + v)
    w10_check = st.number_input("ค่าตรวจสภาพรถสิบล้อ (บาท)", min_value=0.0, value=None, key="w10_c_" + v)
    w10_act = st.number_input("ค่า พ.ร.บ. รถสิบล้อ (บาท)", min_value=0.0, value=None, key="w10_a_" + v)
    w10_tax = st.number_input("ค่าภาษี รถสิบล้อ (บาท)", min_value=0.0, value=None, key="w10_t_" + v)

with tab5:
    st.markdown("#### 💼 งานประกันภัย")
    ins_company = st.selectbox("บริษัทประกัน", ["-- เลือกบริษัทประกันภัย --", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย"], key="ins_c_" + v)
    ins_type = st.selectbox("ประเภทประกัน", ["-- เลือกประเภทประกันภัย --", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"], key="ins_t_" + v)
    ins_price = st.number_input("เบี้ยประกันภัย (บาท)", min_value=0.0, value=None, key="ins_p_" + v)
    
    st.markdown("#### 📁 งานทะเบียนและค่าบริการ")
    col_new1, col_new2 = st.columns(2)
    with col_new1:
        p_transfer_owner = col_new1.number_input("โอน (บาท)", min_value=0.0, value=None, key="p_to_" + v)
        p_new_reg = col_new1.number_input("จดใหม่ (บาท)", min_value=0.0, value=None, key="p_nr_" + v)
        p_update_book = col_new1.number_input("ปรับสมุด (บาท)", min_value=0.0, value=None, key="p_ub_" + v)
        p_service = col_new1.number_input("ค่าบริการ (บาท)", min_value=0.0, value=None, key="p_serv_" + v)
    with col_new2:
        p_check_ext = col_new2.number_input("ตรวจรวมต่อ (บาท)", min_value=0.0, value=None, key="p_chext_" + v)
        p_book = col_new2.number_input("เล่ม เอกสาร (บาท)", min_value=0.0, value=None, key="p_book_" + v)
        p_transfer = col_new2.number_input("โอนย้าย (บาท)", min_value=0.0, value=None, key="p_trans_" + v)
        p_color = col_new2.number_input("เปลี่ยนสี (บาท)", min_value=0.0, value=None, key="p_color_" + v)
        p_cage = col_new2.number_input("แจ้งคอก (บาท)", min_value=0.0, value=None, key="p_cage_" + v)
        
    other_income = st.number_input("รายรับอื่นๆ (บาท)", min_value=0.0, value=None, key="other_" + v)

# คำนวณยอดเงินอัตโนมัติ
total = sum([
    car_check or 0, car_act or 0, car_tax or 0, 
    bike_check or 0, bike_act or 0, bike_tax or 0, 
    w6_check or 0, w6_act or 0, w6_tax or 0,
    w10_check or 0, w10_act or 0, w10_tax or 0,
    ins_price or 0, p_transfer_owner or 0, p_new_reg or 0, p_update_book or 0,
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
if st.button("💾 บันทึกข้อมูลลงตาราง", type="primary", use_container_width=True):
    if not cust_name or not license_plate:
        st.error("❌ กรุณากรอก ชื่อ-นามสกุล และ ทะเบียนรถ ก่อนบันทึกข้อมูล")
    else:
        d_status = f"ค้างชำระ: {debt_amt or 0:,.2f} บ." if is_debt else "ปกติ"
        
        row_values = [
            date_val.strftime("%Y-%m-%d"), cust_name, cust_phone or "-", license_plate,
            car_qty or 0, car_check or 0, car_act or 0, car_tax or 0,
            bike_qty or 0, bike_check or 0, bike_act or 0, bike_tax or 0,
            w6_qty or 0, w6_check or 0, w6_act or 0, w6_tax or 0,
            w10_qty or 0, w10_check or 0, w10_act or 0, w10_tax or 0,
            ins_company if ins_company != "-- เลือกบริษัทประกันภัย --" else "-", 
            ins_type if ins_type != "-- เลือกประเภทประกันภัย --" else "-", ins_price or 0,
            p_transfer_owner or 0, p_new_reg or 0, p_update_book or 0, p_service or 0,
            p_check_ext or 0, p_book or 0, p_transfer or 0, p_color or 0, p_cage or 0,
            other_income or 0, total, transfer_amt or 0, rem_cash, d_status
        ]
        
        try:
            new_row_df = pd.DataFrame([row_values], columns=column_headers)
            df_updated = pd.concat([df_existing, new_row_df], ignore_index=True)
            df_updated.to_excel(EXCEL_FILE, index=False)
            st.success("✅ บันทึกข้อมูลลงระบบเรียบร้อยแล้ว!")
            clear_form_fields()
            st.rerun()
        except Exception as e:
            st.error(f"❌ ไม่สามารถบันทึกข้อมูลได้เนื่องจาก: {e}")

# ==================== ส่วนระบบสถิติและเครื่องมือการจัดการแบบใหม่แกะกล่องความปลอดภัย 100% ====================
st.markdown("---")
st.subheader("📊 ระบบรายงานข้อมูลสรุปแยกช่วงเวลา (ดึงข้อมูลตรงแสดงผลสำเร็จ)")

now_d = datetime.now().strftime("%Y-%m-%d")
now_m = datetime.now().strftime("%Y-%m")
now_y = datetime.now().strftime("%Y")

# ตัวแปรสำหรับนับจำนวนคันรถ
d_car, d_bike, d_w6, d_w10 = 0, 0, 0, 0
m_car, m_bike, m_w6, m_w10 = 0, 0, 0, 0
y_car, y_bike, y_w6, y_w10 = 0, 0, 0, 0

if not df_existing.empty:
    try:
        # แปลงวันที่เป็นข้อความ String เพื่อใช้คำนวณแบบไม่ค้างลูป
        dates_str = df_existing["วันที่"].astype(str)
        
        # 1. ยอดรายวัน (วันนี้)
        df_d = df_existing[dates_str == now_d]
        d_car = int(pd.to_numeric(df_d["รถยนต์ (คัน)"], errors='coerce').sum())
        d_bike = int(pd.to_numeric(df_d["มอเตอร์ไซค์ (คัน)"], errors='coerce').sum())
        d_w6 = int(pd.to_numeric(df_d["หกล้อ (คัน)"], errors='coerce').sum())
        d_w10 = int(pd.to_numeric(df_d["สิบล้อ (คัน)"], errors='coerce').sum())
        
        # 2. ยอดรายเดือน (เดือนนี้)
        df_m = df_existing[dates_str.str.startswith(now_m)]
        m_car = int(pd.to_numeric(df_m["รถยนต์ (คัน)"], errors='coerce').sum())
        m_bike = int(pd.to_numeric(df_m["มอเตอร์ไซค์ (คัน)"], errors='coerce').sum())
