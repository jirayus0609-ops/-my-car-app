import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# ตั้งค่าหน้าตาของโปรแกรม
st.set_page_config(page_title="ระบบบันทึกบริการรถ", layout="wide")
st.title("🚗🏍️🚛 ระบบบันทึกข้อมูลบริการรถและประกันภัย (เวอร์ชันอัปเกรด)")

# ชื่อไฟล์ Excel ที่ใช้เก็บข้อมูลหลักในระบบ
EXCEL_FILE = "data.xlsx"

# กำหนดรายชื่อหัวคอลัมน์ใหม่ให้ครอบคลุมข้อมูลที่อัปเดตทั้งหมด
column_headers = [
    "วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", 
    "รถยนต์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", 
    "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)", 
    "หกล้อ (คัน)", "ตรวจสภาพ(หกล้อ)", "พรบ(หกล้อ)", "ภาษี(หกล้อ)",
    "สิบล้อ (คัน)", "ตรวจสภาพ(สิบล้อ)", "พรบ(สิบล้อ)", "ภาษี(สิบล้อ)",
    "โอน", "จดใหม่", "ปรับสมุด", "ค่าบริการ", "ตรวจรวมต่อ", "เล่ม เอกสาร", "โอนย้าย", "เปลี่ยนสี", "แจ้งคอก", "ทะเบียนหกล้อ", "ทะเบียนสิบล้อ",
    "บริษัทประกัน", "ประเภทประกัน", "เบี้ยประกันภัย", "รายรับอื่นๆ", 
    "ยอดรวม", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"
]

# ฟังก์ชันสำหรับอ่านข้อมูลล่าสุดจากไฟล์ Excel หลัก
def load_data_from_excel():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
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

# แยกแท็บการกรอกข้อมูลเป็น 5 แท็บตามประเภทรถและงานบริการ
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚗 รถยนต์", "🏍️ มอเตอร์ไซค์", "🚛 หกล้อ", "🚛 สิบล้อ", "💼 ทะเบียน/ประกัน"])

with tab1:
    car_qty = st.number_input("จำนวนรถยนต์ (คัน)", min_value=0, step=1, value=None, key="car_q_" + v)
    car_check = st.number_input("ค่าตรวจสภาพรถยนต์", min_value=0.0, value=None, key="car_c_" + v)
    car_act = st.number_input("ค่า พ.ร.บ. รถยนต์", min_value=0.0, value=None, key="car_a_" + v)
    car_tax = st.number_input("ค่าภาษี รถยนต์", min_value=0.0, value=None, key="car_t_" + v)

with tab2:
    bike_qty = st.number_input("จำนวนมอเตอร์ไซค์ (คัน)", min_value=0, step=1, value=None, key="bike_q_" + v)
    bike_check = st.number_input("ค่าตรวจสภาพมอไซค์", min_value=0.0, value=None, key="bike_c_" + v)
    bike_act = st.number_input("ค่า พ.ร.บ. มอไซค์", min_value=0.0, value=None, key="bike_a_" + v)
    bike_tax = st.number_input("ค่าภาษี มอไซค์", min_value=0.0, value=None, key="bike_t_" + v)

with tab3:
    truck6_qty = st.number_input("จำนวนรถหกล้อ (คัน)", min_value=0, step=1, value=None, key="t6_q_" + v)
    truck6_check = st.number_input("ค่าตรวจสภาพหกล้อ", min_value=0.0, value=None, key="t6_c_" + v)
    truck6_act = st.number_input("ค่า พ.ร.บ. หกล้อ", min_value=0.0, value=None, key="t6_a_" + v)
    truck6_tax = st.number_input("ค่าภาษี หกล้อ", min_value=0.0, value=None, key="t6_t_" + v)

with tab4:
    truck10_qty = st.number_input("จำนวนรถสิบล้อ (คัน)", min_value=0, step=1, value=None, key="t10_q_" + v)
    truck10_check = st.number_input("ค่าตรวจสภาพสิบล้อ", min_value=0.0, value=None, key="t10_c_" + v)
    truck10_act = st.number_input("ค่า พ.ร.บ. สิบล้อ", min_value=0.0, value=None, key="t10_a_" + v)
    truck10_tax = st.number_input("ค่าภาษี สิบล้อ", min_value=0.0, value=None, key="t10_t_" + v)

with tab5:
    st.markdown("##### 📝 รายการงานทะเบียน (ระบุราคา)")
    col_reg1, col_reg2, col_reg3 = st.columns(3)
    
    fee_transfer = col_reg1.number_input("โอน (บาท)", min_value=0.0, value=None, key="reg_trans_" + v)
    fee_new_reg = col_reg2.number_input("จดใหม่ (บาท)", min_value=0.0, value=None, key="reg_new_" + v)
    fee_update_book = col_reg3.number_input("ปรับสมุด (บาท)", min_value=0.0, value=None, key="reg_book_" + v)
    
    fee_service = col_reg1.number_input("ค่าบริการ (บาท)", min_value=0.0, value=None, key="reg_srv_" + v)
    fee_total_renew = col_reg2.number_input("ตรวจรวมต่อ (บาท)", min_value=0.0, value=None, key="reg_tot_" + v)
    fee_doc_book = col_reg3.number_input("เล่ม เอกสาร (บาท)", min_value=0.0, value=None, key="reg_doc_" + v)
    
    fee_move = col_reg1.number_input("โอนย้าย (บาท)", min_value=0.0, value=None, key="reg_move_" + v)
    fee_color = col_reg2.number_input("เปลี่ยนสี (บาท)", min_value=0.0, value=None, key="reg_col_" + v)
    fee_cage = col_reg3.number_input("แจ้งคอก (บาท)", min_value=0.0, value=None, key="reg_cage_" + v)
    
    fee_truck6 = col_reg1.number_input("หกล้อ (งานทะเบียน) (บาท)", min_value=0.0, value=None, key="reg_t6_" + v)
    fee_truck10 = col_reg2.number_input("สิบล้อ (งานทะเบียน) (บาท)", min_value=0.0, value=None, key="reg_t10_" + v)
    
    st.markdown("##### 🛡️ งานประกันภัยและรายรับอื่น")
    ins_company = st.selectbox("บริษัทประกัน", ["-- เลือกบริษัทประกันภัย --", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย"], key="ins_c_" + v)
    ins_type = st.selectbox("ประเภทประกัน", ["-- เลือกประเภทประกันภัย --", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"], key="ins_t_" + v)
    ins_price = st.number_input("เบี้ยประกันภัย", min_value=0.0, value=None, key="ins_p_" + v)
    other_income = st.number_input("รายรับอื่นๆ", min_value=0.0, value=None, key="other_" + v)

# คำนวณรวมยอดเงินอัตโนมัติจากทุกฟิลด์ราคา
total_list = [
    car_check, car_act, car_tax, 
    bike_check, bike_act, bike_tax, 
    truck6_check, truck6_act, truck6_tax, 
    truck10_check, truck10_act, truck10_tax,
    fee_transfer, fee_new_reg, fee_update_book, fee_service, fee_total_renew, 
    fee_doc_book, fee_move, fee_color, fee_cage, fee_truck6, fee_truck10,
    ins_price, other_income
]
total = sum([val or 0 for val in total_list])

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
        st.error("❌ กรุณากรอก ชื่อ-นามสกุล และ ทะเบียนรถ")
    else:
        d_status = f"ค้างชำระ: {debt_amt or 0:,.2f} บ." if is_debt else "ปกติ"
        row_values = [
            date_val.strftime("%Y-%m-%d"), cust_name, cust_phone or "-", license_plate,
            car_qty or 0, car_check or "", car_act or "", car_tax or "",
            bike_qty or 0, bike_check or "", bike_act or "", bike_tax or "",
            truck6_qty or 0, truck6_check or "", truck6_act or "", truck6_tax or "",
            truck10_qty or 0, truck10_check or "", truck10_act or "", truck10_tax or "",
            fee_transfer or "", fee_new_reg or "", fee_update_book or "", fee_service or "", 
            fee_total_renew or "", fee_doc_book or "", fee_move or "", fee_color or "", fee_cage or "", 
            fee_truck6 or "", fee_truck10 or "",
            ins_company if ins_company != "-- เลือกบริษัทประกันภัย --" else "-",
            ins_type if ins_type != "-- เลือกประเภทประกันภัย --" else "-",
            ins_price or "", other_income or "",
            total, transfer_amt or 0, rem_cash, d_status
        ]
        new_df = pd.DataFrame([row_values], columns=column_headers)
        if not df_existing.empty:
            updated_df = pd.concat([new_df, df_existing], ignore_index=True)
        else:
            updated_df = new_df
        updated_df.to_excel(EXCEL_FILE, index=False)
        st.success("🎉 บันทึกข้อมูลลงไฟล์ Excel ถาวรสำเร็จ!")
        clear_form_fields()
        st.rerun()

# ==================== ส่วนแสดงตารางและระบบกรองดูรายงาน ====================
if not df_existing.empty:
    st.markdown("---")
    st.subheader("📊 ตารางรายงานสรุปยอดและสถิติข้อมูล (ฐานข้อมูล Excel)")
    
    df = df_existing.copy()
    df['dt_obj'] = pd.to_datetime(df['วันที่'], errors='coerce')

    report_type = st.radio("🔍 เลือกช่วงเวลาดูรายงาน:", ["แสดงทั้งหมด", "รายงานรายวัน (วันนี้)", "รายงานรายเดือน (เดือนนี้)", "รายงานรายปี (ปีนี้)"], horizontal=True)
    
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

    total_cars = pd.to_numeric(df_filtered['รถยนต์ (คัน)'], errors='coerce').fillna(0).sum()
    total_bikes = pd.to_numeric(df_filtered['มอเตอร์ไซค์ (คัน)'], errors='coerce').fillna(0).sum()
    total_t6 = pd.to_numeric(df_filtered['หกล้อ (คัน)'], errors='coerce').fillna(0).sum()
    total_t10 = pd.to_numeric(df_filtered['สิบล้อ (คัน)'], errors='coerce').fillna(0).sum()
    total_money = pd.to_numeric(df_filtered['ยอดรวม'], errors='coerce').fillna(0).sum()
    
    s1, s2, s3 = st.columns(3)
    s1.metric("🚗 / 🏍️ รถยนต์ & มอไซค์รวม", f"รถยนต์ {int(total_cars)} คัน | มอไซค์ {int(total_bikes)} คัน")
    s2.metric("🚛 / 🚚 หกล้อ & สิบล้อรวม", f"หกล้อ {int(total_t6)} คัน | สิบล้อ {int(total_t10)} คัน")
