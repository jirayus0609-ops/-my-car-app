import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ตั้งค่าหน้าตาของโปรแกรม
st.set_page_config(page_title="ระบบบันทึกข้อมูลและสรุปยอดบริการรถ", layout="wide")

st.title("🚗🏍️ ระบบบันทึกข้อมูลบริการรถ ประกันภัย และสรุปสถิติ")

# เชื่อมต่อกับ Google Sheets ผ่าน st.connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # อ่านข้อมูลที่มีอยู่เดิมจาก Google Sheets
    df_existing = conn.read(ttl=0)
except Exception as e:
    st.error("⚠️ ยังไม่ได้ตั้งค่าการเชื่อมต่อกับ Google Sheets หรือข้อมูลในระบบ Sheets ว่างเปล่า")
    df_existing = pd.DataFrame()

# ฟังก์ชันสำหรับรีเซ็ตค่าในฟอร์ม (เคลียร์เป็นค่าว่าง ไม่ให้มีเลข 0 ค้าง)
def reset_form():
    st.session_state.cust_name = ""
    st.session_state.cust_phone = ""
    st.session_state.license_plate = ""
    st.session_state.car_qty = None
    st.session_state.bike_qty = None
    st.session_state.car_check = None
    st.session_state.car_act = None
    st.session_state.car_tax = None
    st.session_state.bike_check = None
    st.session_state.bike_act = None
    st.session_state.bike_tax = None
    st.session_state.reg_type = "-- เลือกประเภท --"
    st.session_state.service_fee = None
    st.session_state.other_income = None
    st.session_state.ins_company = "-- เลือกบริษัทประกันภัย --"
    st.session_state.ins_type = "-- เลือกประเภทประกันภัย --"
    st.session_state.ins_price = None
    st.session_state.transfer_amt = None
    st.session_state.is_debt = False
    st.session_state.debt_amt = None

# =========================================================================
# ส่วนสรุปสถิติจำนวนรถ เข้ากี่คันต่อวัน ต่อเดือน ต่อปี (Dashboard)
# =========================================================================
st.markdown("---")
st.subheader("📊 สรุปยอดจำนวนรถที่เข้าใช้บริการ (คำนวณจากฐานข้อมูลถาวร)")

if not df_existing.empty and "วันที่" in df_existing.columns:
    df_stats = df_existing.copy()
    df_stats['date_dt'] = pd.to_datetime(df_stats['วันที่'], errors='coerce')
    
    df_stats['car_count'] = df_stats['รถยนต์ (คัน)'].apply(lambda x: int(x) if str(x).isdigit() else 0)
    df_stats['bike_count'] = df_stats['มอเตอร์ไซค์ (คัน)'].apply(lambda x: int(x) if str(x).isdigit() else 0)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    df_today = df_stats[df_stats['วันที่'] == today_str]
    today_cars = df_today['car_count'].sum()
    today_bikes = df_today['bike_count'].sum()
    
    df_month = df_stats[df_stats['date_dt'].dt.month == current_month]
    month_cars = df_month['car_count'].sum()
    month_bikes = df_month['bike_count'].sum()
    
    df_year = df_stats[df_stats['date_dt'].dt.year == current_year]
    year_cars = df_year['car_count'].sum()
    year_bikes = df_year['bike_count'].sum()
    
    dash_col1, dash_col2, dash_col3 = st.columns(3)
    with dash_col1:
        st.info(f"📅 **ยอดวันนี้ ({datetime.now().strftime('%d/%m/%Y')})**")
        st.metric("รถยนต์เข้าวันนี้", f"{today_cars} คัน")
        st.metric("มอเตอร์ไซค์เข้าวันนี้", f"{today_bikes} คัน")
        
    with dash_col2:
        st.success(f"📆 **ยอดเดือนนี้ ({datetime.now().strftime('%m/%Y')})**")
        st.metric("รถยนต์รวมเดือนนี้", f"{month_cars} คัน")
        st.metric("มอเตอร์ไซค์รวมเดือนนี้", f"{month_bikes} คัน")
        
    with dash_col3:
        st.warning(f"🗓️ **ยอดปีนี้ (ปี {current_year+543})**")
        st.metric("รถยนต์รวมปีนี้", f"{year_cars} คัน")
        st.metric("มอเตอร์ไซค์รวมปีนี้", f"{year_bikes} คัน")
else:
    st.info("💡 ระบบจะแสดงสถิติรายวัน/รายเดือน/รายปีตรงนี้โดยอัตโนมัติเมื่อทำการเชื่อมโยง Google Sheets เรียบร้อยและเริ่มบันทึกข้อมูลครับ")

st.markdown("---")

# =========================================================================
# ส่วนฟอร์มกรอกข้อมูล (แยกหมวดหมู่ รถยนต์ / มอเตอร์ไซค์ ชัดเจน)
# =========================================================================
st.subheader("📋 ฟอร์มบันทึกข้อมูล")

with st.expander("👤 ข้อมูลลูกค้าและยานพาหนะ", expanded=True):
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        date_val = st.date_input("วันที่ทำรายการ", datetime.now())
        license_plate = st.text_input("ทะเบียนรถ", key="license_plate", placeholder="เช่น กข 1234 กรุงเทพ")
    with col_c2:
        cust_name = st.text_input("ชื่อ-นามสกุล ลูกค้า", key="cust_name", placeholder="เช่น นายสมชาย ใจดี")
    with col_c3:
        cust_phone = st.text_input("เบอร์โทรศัพท์ลูกค้า", key="cust_phone", placeholder="เช่น 0812345678")

tab1, tab2, tab3 = st.tabs(["🚗 หมวดหมู่ รถยนต์", "🏍️ หมวดหมู่ มอเตอร์ไซค์", "💼 งานทะเบียนและรายรับอื่นๆ"])

with tab1:
    st.markdown("#### ข้อมูลและการบริการสำหรับรถยนต์")
    col_car1, col_car2 = st.columns(2)
    with col_car1:
        car_qty = st.number_input("จำนวนรถยนต์ (คัน)", key="car_qty", min_value=0, step=1, value=None, placeholder="กรอกจำนวนคัน เช่น 1")
        car_check = st.number_input("ค่าตรวจสภาพรถยนต์", key="car_check", min_value=0.0, value=None, placeholder="0.00")
    with col_car2:
        car_act = st.number_input("ค่า พ.ร.บ. รถยนต์", key="car_act", min_value=0.0, value=None, placeholder="0.00")
        car_tax = st.number_input("ค่าภาษี รถยนต์", key="car_tax", min_value=0.0, value=None, placeholder="0.00")

with tab2:
    st.markdown("#### ข้อมูลและการบริการสำหรับมอเตอร์ไซค์")
    col_bike1, col_bike2 = st.columns(2)
    with col_bike1:
        bike_qty = st.number_input("จำนวนมอเตอร์ไซค์ (คัน)", key="bike_qty", min_value=0, step=1, value=None, placeholder="กรอกจำนวนคัน เช่น 1")
        bike_check = st.number_input("ค่าตรวจสภาพรถมอเตอร์ไซค์", key="bike_check", min_value=0.0, value=None, placeholder="0.00")
    with col_bike2:
        bike_act = st.number_input("ค่า พ.ร.บ. มอเตอร์ไซค์", key="bike_act", min_value=0.0, value=None, placeholder="0.00")
        bike_tax = st.number_input("ค่าภาษี มอเตอร์ไซค์", key="bike_tax", min_value=0.0, value=None, placeholder="0.00")

with tab3:
    st.markdown("#### งานทะเบียน ประกันภัย และรายรับอื่นๆ")
    col_other1, col_other2, col_other3 = st.columns(3)
    with col_other1:
        reg_type = st.selectbox("ประเภทงานทะเบียน", ["-- เลือกประเภท --", "โอน", "จดใหม่", "ปรับสมุด"], key="reg_type")
        service_fee = st.number_input("ค่าบริการงานทะเบียน", key="service_fee", min_value=0.0, value=None, placeholder="0.00")
    with col_other2:
        ins_company = st.selectbox("บริษัทประกันภัย", ["-- เลือกบริษัทประกันภัย --", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย"], key="ins_company")
        ins_type = st.selectbox("ประเภทประกันภัย", ["-- เลือกประเภทประกันภัย --", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"], key="ins_type")
    with col_other3:
        ins_price = st.number_input("เบี้ยประกันภัย (ถ้ามี)", key="ins_price", min_value=0.0, value=None, placeholder="0.00")
        other_income = st.number_input("รายรับอื่นๆ", key="other_income", min_value=0.0, value=None, placeholder="0.00")

# คำนวณรวมยอดเงินอัตโนมัติ
total_amount = sum([
    car_check or 0, car_act or 0, car_tax or 0,
    bike_check or 0, bike_act or 0, bike_tax or 0,
    service_fee or 0, other_income or 0, ins_price or 0
])

st.markdown("### 💰 สรุปยอดเงินและการชำระเงิน")
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    st.markdown(f"#### ยอดรวมทั้งหมด: <span style='color:#2b6cb0;'>{total_amount:,.2f}</span> บาท", unsafe_allow_html=True)
with col_p2:
    transfer_amt = st.number_input("เงินโอน (บาท)", key="transfer_amt", min_value=0.0, value=None, placeholder="ระบุจำนวนเงินที่โอน")
with col_p3:
    current_transfer = transfer_amt or 0
    remaining_cash = total_amount - current_transfer
    if remaining_cash < 0: remaining_cash = 0
    cash_display = f"{remaining_cash:,.2f}" if total_amount > 0 else ""
    st.markdown(f"#### เงินสดที่ต้องจ่ายเพิ่ม: <span style='color:#27ae60;'>{cash_display}</span> บาท", unsafe_allow_html=True)

# ส่วนค้างชำระ
st.markdown("---")
is_debt = st.checkbox("⚠️ ลูกค้าค้างชำระ", key="is_debt")
debt_amt = None
if is_debt:
    debt_amt = st.number_input("จำนวนเงินที่ค้างชำระ (บาท)", key="debt_amt", min_value=0.0, value=None, placeholder="ระบุจำนวนเงินที่ค้าง")

# =========================================================================
# ปุ่มกดบันทึกข้อมูลและอัปเดตลง Google Sheets ทันที (ไม่มีสัญลักษณ์ปีกกา {})
# =========================================================================
if st.button("💾 บันทึกข้อมูล", type="primary", use_container_width=True):
    if not cust_name or not license_plate:
        st.error("❌ กรุณากรอก ชื่อ-นามสกุล และ ทะเบียนรถ ก่อนบันทึกข้อมูลครับ")
    else:
        debt_status = f"ค้างชำระ: {debt_amt or 0:,.2f} บ." if is_debt else "ปกติ"
        
        # กำหนดชื่อหัวคอลัมน์ให้ตรงกัน
        column_headers = [
            "วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", 
            "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", 
            "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)", "ประเภทงาน", "ค่าบริการ", 
            "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"
        ]
        
        # ใส่ข้อมูลดิบเรียงตามลำดับคอลัมน์แบบใช้ก้ามปู [ ] ธรรมดา
        row_values = [
            date_val.strftime("%Y-%m-%d"),
            cust_name,
            cust_phone if cust_phone else "-",
            license_plate,
            str(car_qty) if car_qty is not None else "",
            str(bike_qty) if bike_qty is not None else "",
            car_check if car_check is not None else "",
            car_act if car_act is not None else "",
            car_tax if car_tax is not None else "",
            bike_check if bike_check is not None else "",
            bike_act if bike_act is not None else "",
            bike_tax if bike_tax is not None else "",
            reg_type if reg_type != "-- เลือกประเภท --" else "-",
