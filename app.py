import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าตาของโปรแกรม
st.set_page_config(page_title="ระบบบันทึกบริการรถ", layout="wide")
st.title("🚗🏍️ ระบบบันทึกข้อมูลบริการรถและประกันภัย")

# สร้างระบบเก็บข้อมูลภายในตัวโปรแกรม
if "data_list" not in st.session_state:
    st.session_state.data_list = []

# ฟังก์ชันรีเซ็ตค่ากลับเป็นค่าว่างอย่างปลอดภัย (เคลียร์ช่องพิมพ์แบบล้างเลขศูนย์)
def reset_form():
    st.session_state.cust_name = ""
    st.session_state.cust_phone = ""
    st.session_state.license_plate = ""
    st.session_state.car_qty = None
    st.session_state.car_check = None
    st.session_state.car_act = None
    st.session_state.car_tax = None
    st.session_state.bike_qty = None
    st.session_state.bike_check = None
    st.session_state.bike_act = None
    st.session_state.bike_tax = None
    st.session_state.reg_type = "-- เลือกประเภท --"
    st.session_state.service_fee = None
    st.session_state.ins_company = "-- เลือกบริษัทประกันภัย --"
    st.session_state.ins_type = "-- เลือกประเภทประกันภัย --"
    st.session_state.ins_price = None
    st.session_state.other_income = None
    st.session_state.transfer_amt = None
    st.session_state.is_debt = False
    st.session_state.debt_amt = None

# ==================== ฟอร์มกรอกข้อมูล ====================
st.markdown("---")
st.subheader("📋 ฟอร์มบันทึกข้อมูล")
c_a, c_b, c_c = st.columns(3)
date_val = c_a.date_input("วันที่", datetime.now())
cust_name = c_b.text_input("ชื่อ-นามสกุล ลูกค้า", key="cust_name")
cust_phone = c_c.text_input("เบอร์โทรศัพท์", key="cust_phone")
license_plate = c_a.text_input("ทะเบียนรถ", key="license_plate")

t1, t2, t3 = st.tabs(["🚗 รถยนต์", "🏍️ มอเตอร์ไซค์", "💼 ทะเบียน/ประกัน"])
with t1:
    car_qty = st.number_input("จำนวนรถยนต์ (คัน)", key="car_qty", min_value=0, step=1, value=None)
    car_check = st.number_input("ค่าตรวจสภาพรถยนต์", key="car_check", min_value=0.0, value=None)
    car_act = st.number_input("ค่า พ.ร.บ. รถยนต์", key="car_act", min_value=0.0, value=None)
    car_tax = st.number_input("ค่าภาษี รถยนต์", key="car_tax", min_value=0.0, value=None)
with t2:
    bike_qty = st.number_input("จำนวนมอเตอร์ไซค์ (คัน)", key="bike_qty", min_value=0, step=1, value=None)
    bike_check = st.number_input("ค่าตรวจสภาพมอไซค์", key="bike_check", min_value=0.0, value=None)
    bike_act = st.number_input("ค่า พ.ร.บ. มอไซค์", key="bike_act", min_value=0.0, value=None)
    bike_tax = st.number_input("ค่าภาษี มอไซค์", key="bike_tax", min_value=0.0, value=None)
with t3:
    reg_type = st.selectbox("งานทะเบียน", ["-- เลือกประเภท --", "โอน", "จดใหม่", "ปรับสมุด"], key="reg_type")
    service_fee = st.number_input("ค่าบริการทะเบียน", key="service_fee", min_value=0.0, value=None)
    ins_company = st.selectbox("บริษัทประกัน", ["-- เลือกบริษัทประกันภัย --", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย"], key="ins_company")
    ins_type = st.selectbox("ประเภทประกัน", ["-- เลือกประเภทประกันภัย --", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"], key="ins_type")
    ins_price = st.number_input("เบี้ยประกันภัย", key="ins_price", min_value=0.0, value=None)
    other_income = st.number_input("รายรับอื่นๆ", key="other_income", min_value=0.0, value=None)

# คำนวณยอดเงินและเงินสดอัตโนมัติ
total = sum([car_check or 0, car_act or 0, car_tax or 0, bike_check or 0, bike_act or 0, bike_tax or 0, service_fee or 0, other_income or 0, ins_price or 0])

st.markdown("### 💰 สรุปยอดเงิน")
p1, p2, p3 = st.columns(3)
p1.markdown(f"#### ยอดรวมทั้งหมด: `{total:,.2f}` บาท")
transfer_amt = p2.number_input("เงินโอน (บาท)", key="transfer_amt", min_value=0.0, value=None)
rem_cash = max(0.0, total - (transfer_amt or 0.0))
p3.markdown(f"#### เงินสดต้องจ่ายเพิ่ม: `{rem_cash:,.2f}` บาท" if total > 0 else "#### เงินสดต้องจ่ายเพิ่ม:")

is_debt = st.checkbox("⚠️ ลูกค้าค้างชำระ", key="is_debt")
debt_amt = st.number_input("เงินที่ค้างชำระ (บาท)", key="debt_amt", min_value=0.0, value=None) if is_debt else None

# ปุ่มบันทึกข้อมูล
if st.button("💾 บันทึกข้อมูล", type="primary", use_container_width=True):
    if not cust_name or not license_plate:
        st.error("❌ กรุณากรอก ชื่อ-นามสกุล และ ทะเบียนรถ")
    else:
        d_status = f"ค้างชำระ: {debt_amt or 0:,.2f} บ." if is_debt else "ปกติ"
        cols = ["วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)", "ประเภทงาน", "ค่าบริการ", "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"]
        vals = [date_val.strftime("%Y-%m-%d"), cust_name, cust_phone or "-", license_plate, car_qty or 0, bike_qty or 0, car_check or "", car_act or "", car_tax or "", bike_check or "", bike_act or "", bike_tax or "", reg_type if reg_type != "-- เลือกประเภท --" else "-", service_fee or "", other_income or "", ins_company if ins_company != "-- เลือกบริษัทประกันภัย --" else "-", ins_type if ins_type != "-- เลือกประเภทประกันภัย --" else "-", total, transfer_amt or 0, rem_cash, d_status]
        
        # บันทึกข้อมูลเข้า List
        st.session_state.data_list.insert(0, vals)
        st.success("🎉 บันทึกข้อมูลเข้าตารางสรุปด้านล่างสำเร็จ และเคลียร์เลขศูนย์แล้ว!")
        reset_form()
        st.rerun()

# ==================== ส่วนแสดงตารางและระบบกรองดูรายงาน ====================
if st.session_state.data_list:
    st.markdown("---")
    st.subheader("📊 ตารางรายงานสรุปยอดและสถิติข้อมูล")
    
    cols = ["วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)", "ประเภทงาน", "ค่าบริการ", "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"]
    df = pd.DataFrame(st.session_state.data_list, columns=cols)
    df['dt_obj'] = pd.to_datetime(df['วันที่'])

    # แถบเลือกดูรายงาน วัน / เดือน / ปี
    report_type = st.radio("🔍 เลือกช่วงเวลาที่ต้องการดูรายงานคันรถและยอดเงิน:", ["แสดงทั้งหมด", "รายงานรายวัน (วันนี้)", "รายงานรายเดือน (เดือนนี้)", "รายงานรายปี (ปีนี้)"], horizontal=True)
    
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

    # สรุปสถิติจำนวนรถจากตารางที่กรอง
    total_cars = df_filtered['รถยนต์ (คัน)'].sum()
    total_bikes = df_filtered['มอเตอร์ไซค์ (คัน)'].sum()
    total_money = df_filtered['ยอดรวม'].sum()
    
    s1, s2, s3 = st.columns(3)
    s1.metric("🚗 จำนวนรถยนต์รวม", f"{total_cars} คัน")
    s2.metric("🏍️ จำนวนมอเตอร์ไซค์รวม", f"{total_bikes} คัน")
    s3.metric("💰 ยอดเงินรวมในช่วงที่เลือก", f"{total_money:,.2f} บาท")

    # แสดงตารางข้อมูลดิบ
    st.dataframe(df_filtered.drop(columns=['dt_obj']), use_container_width=True)
    
    # เครื่องมือลบแถว (กรณีคีย์ผิด)
    with st.expander("🗑️ เครื่องมือลบข้อมูลแถวที่พิมพ์ผิด"):
        r_del = st.number_input("ระบุเลขแถวซ้ายสุดที่ต้องการลบ", min_value=0, max_value=len(df)-1, step=1)
        if st.button("❌ กดเพื่อลบแถวนี้ทันที"):
            st.session_state.data_list.pop(r_del)
            st.success("ลบข้อมูลแถวที่เลือกเรียบร้อยแล้ว!")
            st.rerun()
else:
    st.markdown("---")
    st.info("💡 ตารางและรายงานสรุป รายวัน/รายเดือน/รายปี จะแสดงขึ้นมาทันทีเมื่อคุณเริ่มกดบันทึกข้อมูลของลูกค้าคนแรกครับ")
