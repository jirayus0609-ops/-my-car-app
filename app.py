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
        df_load = pd.read_excel(EXCEL_FILE)
        # แปลงคอลัมน์วันที่ให้เป็น string เสมอเพื่อความแม่นยำในการกรองข้อมูล
        df_load['วันที่'] = df_load['วันที่'].astype(str)
        return df_load
    return pd.DataFrame()

# --- 1. ส่วนฟอร์มกรอกข้อมูล (Input Form) ---
st.header("📝 บันทึกรายการใหม่")
col1, col2, col3 = st.columns(3)

with col1:
    date_input = st.date_input("วันที่", datetime.now())
    car_plate = st.text_input("ทะเบียนรถ", placeholder="เช่น กข 1234")
    vehicle_type = st.radio("ประเภทรถ", ["รถยนต์", "รถมอเตอร์ไซค์"])

with col2:
    st.write("🔧 รายการบริการและราคา (บาท)")
    
    price_inspect = 0
    price_act = 0
    price_tax = 0
    price_transfer = 0
    price_new_reg = 0
    price_book = 0
    
    services_list = []
    
    if vehicle_type == "รถยนต์":
        if st.checkbox("ตรวจสภาพรถ (รถยนต์)"):
            price_inspect = st.number_input("ราคา ตรวจสภาพ (ยนต์)", min_value=0, value=0, step=50)
            services_list.append(f"ตรวจสภาพยนต์({price_inspect})")
            
        if st.checkbox("พรบ (รถยนต์)"):
            price_act = st.number_input("ราคา พรบ (ยนต์)", min_value=0, value=0, step=50)
            services_list.append(f"พรบยนต์({price_act})")
            
        if st.checkbox("ภาษี (รถยนต์)"):
            price_tax = st.number_input("ราคา ภาษี (ยนต์)", min_value=0, value=0, step=50)
            services_list.append(f"ภาษียนต์({price_tax})")
    else:
        if st.checkbox("ตรวจสภาพรถ (มอเตอร์ไซค์)"):
            price_inspect = st.number_input("ราคา ตรวจสภาพ (มอไซค์)", min_value=0, value=0, step=50)
            services_list.append(f"ตรวจสภาพมอไซค์({price_inspect})")
            
        if st.checkbox("พรบ (มอเตอร์ไซค์)"):
            price_act = st.number_input("ราคา พรบ (มอเตอร์ไซค์)", min_value=0, value=0, step=50)
            services_list.append(f"พรบมอไซค์({price_act})")
            
        if st.checkbox("ภาษี (มอเตอร์ไซค์)"):
            price_tax = st.number_input("ราคา ภาษี (มอเตอร์ไซค์)", min_value=0, value=0, step=50)
            services_list.append(f"ภาษีมอไซค์({price_tax})")
            
    if st.checkbox("โอน"):
        price_transfer = st.number_input("ราคา โอน", min_value=0, value=0, step=50)
        services_list.append(f"โอน({price_transfer})")
        
    if st.checkbox("จดใหม่"):
        price_new_reg = st.number_input("ราคา จดใหม่", min_value=0, value=0, step=50)
        services_list.append(f"จดใหม่({price_new_reg})")
        
    if st.checkbox("ปรับสมุด"):
        price_book = st.number_input("ราคา ปรับสมุด", min_value=0, value=0, step=50)
        services_list.append(f"ปรับสมุด({price_book})")
        
    other_income = st.number_input("รายรับอื่นๆ (บาท)", min_value=0, value=0, step=50)

with col3:
    st.write("💰 คำนวณการชำระเงิน")
    
    calculated_total = price_inspect + price_act + price_tax + price_transfer + price_new_reg + price_book + other_income
    st.warning(f"📊 ยอดรวมค่าบริการทั้งหมด: {calculated_total:,} บาท")
    
    transfer_amount = st.number_input("ยอดเงินโอน (บาท)", min_value=0, value=0, step=50)
    
    cash_needed = calculated_total - transfer_amount
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
            "บริการ(ราคา)": ", ".join(services_list) if services_list else "รายรับอื่นๆ เท่านั้น",
            "รายรับอื่นๆ": other_income,
            "ยอดที่ต้องจ่าย": calculated_total,
            "เงินโอน": transfer_amount,
            "เงินสด": cash_needed,
            "สถานะ": status
        }
        df_all = save_to_excel(new_entry)
        st.success(f"บันทึกข้อมูลรถทะเบียน {car_plate} เรียบร้อยแล้ว!")
    else:
        st.error("กรุณากรอกทะเบียนรถก่อนบันทึก")

st.divider()

# --- 2. ส่วนสรุปผลและรายงานแยกตามแท็บเวลา (Dashboard) ---
st.header("📊 รายงานสรุปผลภาพรวม")
df = load_from_excel()

if not df.empty:
    # เตรียมตัวแปรวันที่ในการกรองข้อมูล
    current_date_str = date_input.strftime("%Y-%m-%d")        # เช่น "2026-10-19"
    current_month_str = date_input.strftime("%Y-%m")          # เช่น "2026-10"
    current_year_str = date_input.strftime("%Y")             # เช่น "2026"
    
    # แยกแท็บรายงาน 3 แท็บ
    tab1, tab2, tab3 = st.tabs(["📅 รายงานรายวัน", "📆 รายงานรายเดือน", "🗓️ รายงานรายปี"])
    
    # --- แท็บที่ 1: รายวัน ---
    with tab1:
        df_today = df[df["วันที่"] == current_date_str]
        st.subheader(f"ประจำวันที่ {current_date_str}")
        
        if not df_today.empty:
            total_cars_today = len(df_today)
            cars_today = len(df_today[df_today["ประเภทรถ"] == "รถยนต์"])
            bikes_today = len(df_today[df_today["ประเภทรถ"] == "รถมอเตอร์ไซค์"])
            pending_today = len(df_today[df_today["สถานะ"] == "ค้างชำระ"])
            revenue_today = df_today["ยอดที่ต้องจ่าย"].sum()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🚗 รถเข้าทั้งหมดวันนี้", f"{total_cars_today} คัน")
            m2.metric("สถิติแยกประเภท", f"ยนต์: {cars_today} | มอไซค์: {bikes_today}")
            m3.metric("🛑 ลูกค้าค้างชำระวันนี้", f"{pending_today} คน")
            m4.metric("💰 ยอดรวมรายได้วันนี้", f"{revenue_today:,} บาท")
            
            st.dataframe(df_today, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลบันทึกของวันนี้")

    # --- แท็บที่ 2: รายเดือน ---
    with tab2:
        df_month = df[df["วันที่"].str.startswith(current_month_str)]
        st.subheader(f"ประจำเดือน {current_month_str}")
        
        if not df_month.empty:
            total_cars_month = len(df_month)
            cars_month = len(df_month[df_month["ประเภทรถ"] == "รถยนต์"])
            bikes_month = len(df_month[df_month["ประเภทรถ"] == "รถมอเตอร์ไซค์"])
            pending_month = len(df_month[df_month["สถานะ"] == "ค้างชำระ"])
            revenue_month = df_month["ยอดที่ต้องจ่าย"].sum()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🚗 รถเข้าทั้งหมดเดือนนี้", f"{total_cars_month} คัน")
            m2.metric("สถิติแยกประเภท", f"ยนต์: {cars_month} | มอไซค์: {bikes_month}")
            m3.metric("🛑 ลูกค้าค้างชำระเดือนนี้", f"{pending_month} คน")
            m4.metric("💰 ยอดรวมรายได้เดือนนี้", f"{revenue_month:,} บาท")
            
            st.dataframe(df_month, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลบันทึกในเดือนนี้")

    # --- แท็บที่ 3: รายปี ---
    with tab3:
        df_year = df[df["วันที่"].str.startswith(current_year_str)]
        st.subheader(f"ประจำปี {current_year_str}")
        
        if not df_year.empty:
            total_cars_year = len(df_year)
            cars_year = len(df_year[df_year["ประเภทรถ"] == "รถยนต์"])
            bikes_year = len(df_year[df_year["ประเภทรถ"] == "รถมอเตอร์ไซค์"])
            pending_year = len(df_year[df_year["สถานะ"] == "ค้างชำระ"])
            revenue_year = df_year["ยอดที่ต้องจ่าย"].sum()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🚗 รถเข้าทั้งหมดปีนี้", f"{total_cars_year} คัน")
            m2.metric("สถิติแยกประเภท", f"ยนต์: {cars_year} | มอไซค์: {bikes_year}")
            m3.metric("🛑 ลูกค้าค้างชำระปีนี้", f"{pending_year} คน")
            m4.metric("💰 ยอดรวมรายได้ปีนี้", f"{revenue_year:,} บาท")
            
            st.dataframe(df_year, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลบันทึกในปีนี้")

else:
    st.info("ยังไม่มีข้อมูลบันทึกในระบบ เริ่มกรอกข้อมูลด้านบนและกดบันทึกได้เลยครับ")
