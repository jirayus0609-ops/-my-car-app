import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าตาของโปรแกรม
st.set_page_config(page_title="ระบบบันทึกข้อมูลบริการรถและประกันภัย", layout="wide")

st.title("📝 ระบบบันทึกข้อมูลบริการและประกันภัยรถ")

# สร้าง Session State สำหรับเก็บข้อมูลตารางเมื่อกดบันทึก
if "data_list" not in st.session_state:
    st.session_state.data_list = []

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

# ส่วนที่ 1: ข้อมูลลูกค้าและตัวรถ
st.subheader("1. ข้อมูลลูกค้าและตัวรถ")
col1, col2, col3 = st.columns(3)
with col1:
    date_val = st.date_input("วันที่", datetime.now())
    license_plate = st.text_input("ทะเบียนรถ", key="license_plate", placeholder="เช่น กข 1234 กรุงเทพ")
with col2:
    cust_name = st.text_input("ชื่อ-นามสกุล ลูกค้า", key="cust_name", placeholder="เช่น นายสมชาย ใจดี")
    car_qty = st.number_input("รถยนต์ (จำนวนคัน)", key="car_qty", min_value=0, step=1, value=None, placeholder="ระบุจำนวน")
with col3:
    cust_phone = st.text_input("เบอร์โทรศัพท์ลูกค้า", key="cust_phone", placeholder="เช่น 0812345678")
    bike_qty = st.number_input("มอไซค์ (จำนวนคัน)", key="bike_qty", min_value=0, step=1, value=None, placeholder="ระบุจำนวน")

# ส่วนที่ 2: ค่าบริการและงานทะเบียน
st.subheader("2. ค่าบริการและงานทะเบียน")
col4, col5, col6 = st.columns(3)
with col4:
    car_check = st.number_input("ตรวจสภาพรถ (รถยนต์)", key="car_check", min_value=0.0, value=None, placeholder="0.00")
    bike_check = st.number_input("ตรวจสภาพรถมอเตอร์ไซค์", key="bike_check", min_value=0.0, value=None, placeholder="0.00")
    reg_type = st.selectbox("ประเภทงานทะเบียน", ["-- เลือกประเภท --", "โอน", "จดใหม่", "ปรับสมุด"], key="reg_type")
with col5:
    car_act = st.number_input("พ.ร.บ. (รถยนต์)", key="car_act", min_value=0.0, value=None, placeholder="0.00")
    bike_act = st.number_input("พ.ร.บ. มอเตอร์ไซค์", key="bike_act", min_value=0.0, value=None, placeholder="0.00")
    service_fee = st.number_input("ค่าบริการงานทะเบียน", key="service_fee", min_value=0.0, value=None, placeholder="0.00")
with col6:
    car_tax = st.number_input("ภาษี (รถยนต์)", key="car_tax", min_value=0.0, value=None, placeholder="0.00")
    bike_tax = st.number_input("ภาษี มอเตอร์ไซค์", key="bike_tax", min_value=0.0, value=None, placeholder="0.00")
    other_income = st.number_input("รายรับอื่นๆ", key="other_income", min_value=0.0, value=None, placeholder="0.00")

# ส่วนที่ 3: ข้อมูลประกันภัย
st.subheader("3. ข้อมูลประกันภัยเพิ่มเติม")
col7, col8, col9 = st.columns(3)
with col7:
    ins_company = st.selectbox("บริษัทประกันภัย", ["-- เลือกบริษัทประกันภัย --", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย"], key="ins_company")
with col8:
    ins_type = st.selectbox("ประเภทประกันภัย", ["-- เลือกประเภทประกันภัย --", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"], key="ins_type")
with col9:
    ins_price = st.number_input("เบี้ยประกันภัย (ถ้ามี)", key="ins_price", min_value=0.0, value=None, placeholder="0.00")

# คำนวณยอดรวมอัตโนมัติจากทุกช่องบริการ (ถ้าช่องไหนว่างให้คิดเป็น 0)
total_amount = sum([
    car_check or 0, car_act or 0, car_tax or 0,
    bike_check or 0, bike_act or 0, bike_tax or 0,
    service_fee or 0, other_income or 0, ins_price or 0
])

# ส่วนที่ 4: สรุปยอดเงินและวิธีชำระ
st.subheader("4. สรุปยอดเงินและการชำระเงิน")
col10, col11, col12 = st.columns(3)
with col10:
    st.markdown(f"### 💰 รวมยอดเงินทั้งหมด: `{total_amount:,.2f}` บาท")
with col11:
    transfer_amt = st.number_input("เงินโอน (บาท)", key="transfer_amt", min_value=0.0, value=None, placeholder="ระบุจำนวนเงินที่โอน")
with col12:
    # คำนวณเงินสดที่ต้องจ่ายเพิ่มอัตโนมัติ
    current_transfer = transfer_amt or 0
    remaining_cash = total_amount - current_transfer
    if remaining_cash < 0: remaining_cash = 0
    st.markdown(f"### 💵 เงินสดที่ต้องจ่ายเพิ่ม: `{remaining_cash:,.2f}` บาท")

# ส่วนค้างชำระ
st.markdown("---")
is_debt = st.checkbox("⚠️ ลูกค้าค้างชำระ", key="is_debt")
debt_amt = None
if is_debt:
    debt_amt = st.number_input("จำนวนเงินที่ค้างชำระ (บาท)", key="debt_amt", min_value=0.0, value=None, placeholder="ระบุจำนวนเงินที่ค้าง")

# ปุ่มบันทึกข้อมูล
if st.button("💾 บันทึกข้อมูลข้อมูล", type="primary", use_container_width=True):
    if not cust_name or not license_plate:
        st.error("❌ กรุณากรอก ชื่อ-นามสกุล และ ทะเบียนรถ ก่อนบันทึกข้อมูลครับ")
    else:
        # เตรียมข้อมูลเพื่อจัดเก็บ
        debt_status = f"ค้างชำระ: {debt_amt or 0:,.2f} บ." if is_debt else "ปกติ"
        
        row_data = {
            "วันที่": date_val.strftime("%Y-%m-%d"),
            "ชื่อ-นามสกุล": cust_name,
            "เบอร์โทร": cust_phone if cust_phone else "-",
            "ทะเบียนรถ": license_plate,
            "รถยนต์/คัน": car_qty if car_qty is not None else "-",
            "มอไซค์/คัน": bike_qty if bike_qty is not None else "-",
            "ตรวจสภาพ(รถ)": car_check if car_check is not None else "-",
            "พรบ(รถ)": car_act if car_act is not None else "-",
            "ภาษี(รถ)": car_tax if car_tax is not None else "-",
            "ตรวจสภาพ(มอไซค์)": bike_check if bike_check is not None else "-",
            "พรบ(มอไซค์)": bike_act if bike_act is not None else "-",
            "ภาษี(มอไซค์)": bike_tax if bike_tax is not None else "-",
            "ประเภทงาน": reg_type if reg_type != "-- เลือกประเภท --" else "-",
            "ค่าบริการ": service_fee if service_fee is not None else "-",
            "รายรับอื่นๆ": other_income if other_income is not None else "-",
            "บริษัทประกัน": ins_company if ins_company != "-- เลือกบริษัทประกันภัย --" else "-",
            "ประเภทประกัน": ins_type if ins_type != "-- เลือกประเภทประกันภัย --" else "-",
            "ยอดรวม": total_amount,
            "เงินโอน": transfer_amt if transfer_amt is not None else 0,
            "เงินสด": remaining_cash,
            "สถานะการจ่ายเงิน": debt_status
        }
        
        # บันทึกลงตาราง (แทรกไว้บนสุด)
        st.session_state.data_list.insert(0, row_data)
        st.success("🎉 บันทึกข้อมูลเรียบร้อยแล้วและเคลียร์ฟอร์มให้พร้อมใช้งานต่อ!")
        
        # เรียกฟังก์ชันรีเซ็ตค่าในฟอร์มทันที โดยตัวเลขจะหายไปไม่โชว์เลข 0
        reset_form()
        st.rerun()

# ตารางแสดงผลข้อมูลด้านล่าง
st.markdown("---")
st.subheader("📊 รายการข้อมูลที่บันทึกแล้ว")
if st.session_state.data_list:
    df = pd.DataFrame(st.session_state.data_list)
    st.dataframe(df, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลที่บันทึกในระบบ")
