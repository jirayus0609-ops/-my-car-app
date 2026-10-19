import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ตั้งค่าหน้าแอป
st.set_page_config(page_title="ระบบบันทึกข้อมูลร้านตรวจสภาพรถ", layout="wide")
st.title("🚗 ระบบบันทึกข้อมูลและรายรับประจำวัน")

EXCEL_FILE = "vehicle_service_log.xlsx"

def save_to_excel(new_data):
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
        df_new = pd.DataFrame([new_data])
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_updated = pd.DataFrame([new_data])
    df_updated.to_excel(EXCEL_FILE, index=False)
    return df_updated

def load_from_excel():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    return pd.DataFrame()

# --- 1. ส่วนฟอร์มกรอกข้อมูล (Input Form) ---
st.header("📝 บันทึกรายการใหม่")
col1, col2, col3 = st.columns(3)

with col1:
    date_input = st.date_input("วันที่", datetime.now())
    car_plate = st.text_input("ทะเบียนรถ", placeholder="เช่น กข 1234")
    vehicle_type = st.radio("ประเภทรถ", ["รถยนต์", "รถมอเตอร์ไซค์"])

with col2:
    st.write("🔧 บริการที่ใช้")
    services = []
    if vehicle_type == "รถยนต์":
        if st.checkbox("ตรวจสภาพรถ (รถยนต์)"): services.append("ตรวจสภาพ (ยนต์)")
        if st.checkbox("พรบ (รถยนต์)"): services.append("พรบ (ยนต์)")
        if st.checkbox("ภาษี (รถยนต์)"): services.append("ภาษี (ยนต์)")
    else:
        if st.checkbox("ตรวจสภาพรถ (มอเตอร์ไซค์)"): services.append("ตรวจสภาพ (มอไซค์)")
        if st.checkbox("พรบ (มอเตอร์ไซค์)"): services.append("พรบ (มอไซค์)")
        if st.checkbox("ภาษี (มอเตอร์ไซค์)"): services.append("ภาษี (มอไซค์)")
        
    if st.checkbox("โอน"): services.append("โอน")
    if st.checkbox("จดใหม่"): services.append("จดใหม่")
    if st.checkbox("ปรับสมุด"): services.append("ปรับสมุด")
    
    other_income = st.number_input("รายรับอื่นๆ (บาท)", min_value=0, value=0)

with col3:
    st.write("💰 การชำระเงิน")
    total_amount = st.number_input("ยอดรวมที่ลูกค้าต้องจ่าย (บาท)", min_value=0, value=0)
    transfer_amount = st.number_input("ยอดเงินโอน (บาท)", min_value=0, value=0)
    
    cash_needed = total_amount - transfer_amount
    if cash_needed < 0:
        cash_needed = 0
        
    st.info(f"💵 ต้องจ่ายเงินสดเพิ่ม: {cash_needed:,} บาท")
    
    is_pending = st.checkbox("🛑 ลูกค้าค้างชำระยอดนี้")
    status = "ค้างชำระ" if is_pending else "จ่ายครบแล้ว"

if st.button("💾 บันทึกข้อมูลลงระบบ", type="primary"):
    if car_plate:
        new_entry = {
            "วันที่": date_input.strftime("%Y-%m-%d"),
            "ทะเบียนรถ": car_plate,
            "ประเภทรถ": vehicle_type,
            "บริการ": ", ".join(services),
            "รายรับอื่นๆ": other_income,
            "ยอดที่ต้องจ่าย": total_amount,
            "เงินโอน": transfer_amount,
            "เงินสด": cash_needed,
            "สถานะ": status
        }
        df_all = save_to_excel(new_entry)
        st.success(f"บันทึกข้อมูลรถทะเบียน {car_plate} เรียบร้อยแล้ว!")
    else:
        st.error("กรุณากรอกทะเบียนรถก่อนบันทึก")

st.divider()

# --- 2. ส่วนสรุปผลประจำวัน ---
st.header("📊 รายงานสรุปผลประจำวัน")
df = load_from_excel()

if not df.empty:
    current_date_str = date_input.strftime("%Y-%m-%d")
    df['วันที่'] = df['วันที่'].astype(str)
    df_today = df[df["วันที่"] == current_date_str]
    
    total_cars_today = len(df_today)
    pending_customers_today = len(df_today[df_today["สถานะ"] == "ค้างชำระ"])
    total_revenue_today = df_today["ยอดที่ต้องจ่าย"].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("🚗 วันนี้รถเข้าทั้งหมด", f"{total_cars_today} คัน")
    m2.metric("🛑 ลูกค้าค้างชำระวันนี้", f"{pending_customers_today} คน", delta_color="inverse")
    m3.metric("💰 ยอดรวมเงินทั้งหมดวันนี้", f"{total_revenue_today:,} บาท")
    
    st.subheader("📋 รายการบันทึกทั้งหมด")
    st.dataframe(df, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลบันทึกในระบบ เริ่มกรอกข้อมูลและกดบันทึกได้เลยครับ")
