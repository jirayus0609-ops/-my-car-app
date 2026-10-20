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
        required_cols = [
            "วันที่", "ชื่อลูกค้า", "เบอร์โทร", "ทะเบียนรถ", "ประเภทรถ", 
            "บริษัทประกัน", "ประเภทประกัน", "บริการ(ราคา)", "รายรับอื่นๆ", 
            "ยอดที่ต้องจ่าย", "เงินโอน", "เงินสด", "ยอดค้างชำระ", "สถานะ"
        ]
        for col in required_cols:
            if col not in df_load.columns:
                if col in ["รายรับอื่นๆ", "ยอดที่ต้องจ่าย", "เงินโอน", "เงินสด", "ยอดค้างชำระ"]:
                    df_load[col] = 0
                else:
                    df_load[col] = "-"
        df_load['วันที่'] = df_load['วันที่'].astype(str)
        return df_load
    return pd.DataFrame()

def update_excel_file(updated_df):
    updated_df.to_excel(EXCEL_FILE, index=False)

def delete_from_excel(index_to_delete):
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
        if index_to_delete in df_existing.index:
            df_updated = df_existing.drop(index_to_delete).reset_index(drop=True)
            df_updated.to_excel(EXCEL_FILE, index=False)
            return True
    return False

# --- 1. ส่วนฟอร์มกรอกข้อมูล (Input Form) ---
st.header("📝 บันทึกรายการใหม่")

with st.form(key="vehicle_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        date_input = st.date_input("วันที่", datetime.now())
        customer_name = st.text_input("ชื่อ - นามสกุล ลูกค้า", placeholder="ชื่อ-นามสกุล")
        customer_phone = st.text_input("เบอร์โทรศัพท์ลูกค้า", placeholder="เช่น 0812345678")
        car_plate = st.text_input("ทะเบียนรถ *", placeholder="เช่น กข 1234")
        vehicle_type = st.radio("ประเภทรถ", ["รถยนต์", "รถมอเตอร์ไซค์"])

    with col2:
        st.write("🔧 รายการบริการและราคา (บาท)")
        
        price_inspect = 0
        price_act = 0
        price_tax = 0
        price_transfer = 0
        price_new_reg = 0
        price_book = 0
        price_insurance = 0
        
        services_list = []
        
        if vehicle_type == "รถยนต์":
            if st.checkbox("ตรวจสภาพรถ (รถยนต์)"):
                val = st.number_input("ราคา ตรวจสภาพ (ยนต์)", min_value=0, value=None, step=50, placeholder="ระบุราคา")
                price_inspect = val if val is not None else 0
                services_list.append(f"ตรวจสภาพยนต์({price_inspect})")
                
            if st.checkbox("พรบ (รถยนต์)"):
                val = st.number_input("ราคา พรบ (ยนต์)", min_value=0, value=None, step=50, placeholder="ระบุราคา")
                price_act = val if val is not None else 0
                services_list.append(f"พรบยนต์({price_act})")
                
            if st.checkbox("ภาษี (รถยนต์)"):
                val = st.number_input("ราคา ภาษี (ยนต์)", min_value=0, value=None, step=50, placeholder="ระบุราคา")
                price_tax = val if val is not None else 0
                services_list.append(f"ภาษียนต์({price_tax})")
        else:
            if st.checkbox("ตรวจสภาพรถ (มอเตอร์ไซค์)"):
                val = st.number_input("ราคา ตรวจสภาพ (มอไซค์)", min_value=0, value=None, step=50, placeholder="ระบุราคา")
                price_inspect = val if val is not None else 0
                services_list.append(f"ตรวจสภาพมอไซค์({price_inspect})")
                
            if st.checkbox("พรบ (มอเตอร์ไซค์)"):
                val = st.number_input("ราคา พรบ (มอเตอร์ไซค์)", min_value=0, value=None, step=50, placeholder="ระบุราคา")
                price_act = val if val is not None else 0
                services_list.append(f"พรบมอไซค์({price_act})")
                
            if st.checkbox("ภาษี (มอเตอร์ไซค์)"):
                val = st.number_input("ราคา ภาษี (มอเตอร์ไซค์)", min_value=0, value=None, step=50, placeholder="ระบุราคา")
                price_tax = val if val is not None else 0
                services_list.append(f"ภาษีมอไซค์({price_tax})")
                
        if st.checkbox("โอน"):
            val = st.number_input("ราคา โอน", min_value=0, value=None, step=50, placeholder="ระบุราคา")
            price_transfer = val if val is not None else 0
            services_list.append(f"โอน({price_transfer})")
            
        if st.checkbox("จดใหม่"):
            val = st.number_input("ราคา จดใหม่", min_value=0, value=None, step=50, placeholder="ระบุราคา")
            price_new_reg = val if val is not None else 0
            services_list.append(f"จดใหม่({price_new_reg})")
            
        if st.checkbox("ปรับสมุด"):
            val = st.number_input("ราคา ปรับสมุด", min_value=0, value=None, step=50, placeholder="ระบุราคา")
            price_book = val if val is not None else 0
            services_list.append(f"ปรับสมุด({price_book})")

        st.divider()
        if st.checkbox("➕ ซื้อประกันภัยเพิ่ม"):
            ins_company = st.selectbox("เลือกบริษัทประกันภัย", [
                "บริษัททิพยประกันภัย", 
                "บริษัทเออร์โกประกันภัย", 
                "บริษัทอินทรประกันภัย", 
                "บริษัทไทยพัฒนาประกันภัย"
            ])
            ins_type = st.selectbox("เลือกประเภทประกันภัย", ["ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"])
            val = st.number_input("ราคา เบี้ยประกันภัย (บาท)", min_value=0, value=None, step=100, placeholder="ระบุราคาเบี้ย")
            price_insurance = val if val is not None else 0
            services_list.append(f"ประกัน-{ins_company}-{ins_type}({price_insurance})")
        else:
            ins_company = "-"
            ins_type = "-"
            
        val_other = st.number_input("รายรับอื่นๆ (บาท)", min_value=0, value=None, step=50, placeholder="ระบุราคาถ้ามี")
        other_income = val_other if val_other is not None else 0

    with col3:
        st.write("💰 คำนวณการชำระเงิน")
        
        calculated_total = price_inspect + price_act + price_tax + price_transfer + price_new_reg + price_book + price_insurance + other_income
        st.warning(f"📊 ยอดรวมค่าบริการทั้งหมด: {calculated_total:,} บาท")
        
        val_transfer = st.number_input("ยอดเงินโอน (บาท)", min_value=0, value=None, step=50, placeholder="ระบุยอดเงินโอน")
        transfer_amount = val_transfer if val_transfer is not None else 0
        
        cash_needed = calculated_total - transfer_amount
        if cash_needed < 0:
            cash_needed = 0
            
        st.info(f"💵 ต้องจ่ายเงินสดเพิ่ม: {cash_needed:,} บาท")
        
        is_pending = st.checkbox("🛑 ลูกค้าค้างชำระยอดนี้")
        pending_amount = 0
        if is_pending:
            val_pending = st.number_input("จำนวนเงินที่ค้างชำระ (บาท)", min_value=0, max_value=calculated_total, value=None, step=50, placeholder="ระบุยอดที่ค้าง")
            pending_amount = val_pending if val_pending is not None else calculated_total
            status = f"ค้างชำระ ({pending_amount:,} บ.)"
        else:
            status = "จ่ายครบแล้ว"

    submit_button = st.form_submit_button(label="💾 บันทึกข้อมูลลงระบบ", type="primary")

if submit_button:
    if car_plate:
        new_entry = {
            "วันที่": date_input.strftime("%Y-%m-%d"),
            "ชื่อลูกค้า": customer_name if customer_name else "-",
            "เบอร์โทร": customer_phone if customer_phone else "-",
            "ทะเบียนรถ": car_plate,
            "ประเภทรถ": vehicle_type,
            "บริษัทประกัน": ins_company,
            "ประเภทประกัน": ins_type,
            "บริการ(ราคา)": ", ".join(services_list) if services_list else "รายรับอื่นๆ เท่านั้น",
            "รายรับอื่นๆ": other_income,
            "ยอดที่ต้องจ่าย": calculated_total,
            "เงินโอน": transfer_amount,
            "เงินสด": cash_needed,
            "ยอดค้างชำระ": pending_amount,
            "สถานะ": status
        }
        save_to_excel(new_entry)
        st.success(f"บันทึกข้อมูลรถทะเบียน {car_plate} เรียบร้อยแล้ว!")
        st.rerun()
    else:
        st.error("กรุณากรอกทะเบียนรถก่อนบันทึก")

st.divider()

# --- 2. ส่วนสรุปผลและรายงานแยกตามแท็บเวลา (Dashboard) ---
st.header("📊 รายงานสรุปผลภาพรวม")
df = load_from_excel()

if not df.empty:
    def get_metrics(dataframe):
        total_cars = len(dataframe)
        cars = len(dataframe[dataframe["ประเภทรถ"] == "รถยนต์"])
        bikes = len(dataframe[dataframe["ประเภทรถ"] == "รถมอเตอร์ไซค์"])
        pending_count = len(dataframe[dataframe["ยอดค้างชำระ"] > 0])
        total_pending_money = dataframe["ยอดค้างชำระ"].sum()
        revenue = dataframe["ยอดที่ต้องจ่าย"].sum()
        return total_cars, cars, bikes, pending_count, total_pending_money, revenue

    all_months = sorted(list(set(df["วันที่"].str.slice(0, 7))), reverse=True)
    all_years = sorted(list(set(df["วันที่"].str.slice(0, 4))), reverse=True)
    current_date_str = datetime.now().strftime("%Y-%m-%d")

    # 🟢 แก้ไข Syntax ของการแบ่งแท็บรายงานให้สมบูรณ์และปิดวงเล็บถูกต้อง
    tab1, tab2, tab3, tab_pay, tab4 = st.tabs([
        "📅 รายงานรายวัน", 
        "📆 เลือกดูรายเดือน", 
        "🗓️ เลือกดูรายปี", 
        "💰 อัปเดตยอดค้างชำระ", 
        "🗑️ ลบข้อมูล"
    ])
    
    # --- แท็บที่ 1: รายวัน ---
    with tab1:
        df_today = df[df["วันที่"] == current_date_str]
        st.subheader(f"ประจำวันที่ {current_date_str}")
        if not df_today.empty:
            t_cars, c_cars, b_cars, p_count, p_money, rev = get_metrics(df_today)
            m1, m2, m3, m4 = st.columns(4)
