import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าตาของโปรแกรม
st.set_page_config(page_title="ระบบบันทึกบริการรถ", layout="wide")
st.title("🚗🏍️ ระบบบันทึกข้อมูลบริการรถและประกันภัย")

# สร้างระบบเก็บข้อมูลภายในตัวโปรแกรมและเวอร์ชันของฟอร์ม
if "data_list" not in st.session_state:
    st.session_state.data_list = []
if "form_version" not in st.session_state:
    st.session_state.form_version = 0

# อัปเดตเวอร์ชันเพื่อล้างข้อมูลในฟอร์มทั้งหมดแบบไร้เลขศูนย์ค้าง
def clear_form_fields():
    st.session_state.form_version += 1

# ดึงรหัสเวอร์ชันมาผูกกับช่องกรอกเพื่อบังคับรีเซ็ตค่า
v = str(st.session_state.form_version)

# ==================== ฟอร์มกรอกข้อมูล ====================
st.markdown("---")
st.subheader("📋 ฟอร์มบันทึกข้อมูล")
c_a, c_b, c_c = st.columns(3)
date_val = c_a.date_input("วันที่", datetime.now(), key="date_" + v)
cust_name = c_b.text_input("ชื่อ-นามสกุล ลูกค้า", key="name_" + v)
cust_phone = c_c.text_input("เบอร์โทรศัพท์", key="phone_" + v)
license_plate = c_a.text_input("ทะเบียนรถ", key="plate_" + v)

t1, t2, t3 = st.tabs(["🚗 รถยนต์", "🏍️ มอเตอร์ไซค์", "💼 ทะเบียน/ประกัน"])
with t1:
    car_qty = st.number_input("จำนวนรถยนต์ (คัน)", min_value=0, step=1, value=None, key="car_q_" + v)
    car_check = st.number_input("ค่าตรวจสภาพรถยนต์", min_value=0.0, value=None, key="car_c_" + v)
    car_act = st.number_input("ค่า พ.ร.บ. รถยนต์", min_value=0.0, value=None, key="car_a_" + v)
    car_tax = st.number_input("ค่าภาษี รถยนต์", min_value=0.0, value=None, key="car_t_" + v)
with t2:
    bike_qty = st.number_input("จำนวนมอเตอร์ไซค์ (คัน)", min_value=0, step=1, value=None, key="bike_q_" + v)
    bike_check = st.number_input("ค่าตรวจสภาพมอไซค์", min_value=0.0, value=None, key="bike_c_" + v)
    bike_act = st.number_input("ค่า พ.ร.บ. มอไซค์", min_value=0.0, value=None, key="bike_a_" + v)
    bike_tax = st.number_input("ค่าภาษี มอไซค์", min_value=0.0, value=None, key="bike_t_" + v)
with t3:
    reg_type = st.selectbox("งานทะเบียน", ["-- เลือกประเภท --", "โอน", "จดใหม่", "ปรับสมุด"], key="reg_v_" + v)
    service_fee = st.number_input("ค่าบริการทะเบียน", min_value=0.0, value=None, key="fee_" + v)
    ins_company = st.selectbox("บริษัทประกัน", ["-- เลือกบริษัทประกันภัย --", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย"], key="ins_c_" + v)
    ins_type = st.selectbox("ประเภทประกัน", ["-- เลือกประเภทประกันภัย --", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"], key="ins_t_" + v)
    ins_price = st.number_input("เบี้ยประกันภัย", min_value=0.0, value=None, key="ins_p_" + v)
    other_income = st.number_input("รายรับอื่นๆ", min_value=0.0, value=None, key="other_" + v)

# คำนวณยอดเงินและเงินสดอัตโนมัติ
total = sum([car_check or 0, car_act or 0, car_tax or 0, bike_check or 0, bike_act or 0, bike_tax or 0, service_fee or 0, other_income or 0, ins_price or 0])

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
        cols = ["วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)", "ประเภทงาน", "ค่าบริการ", "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"]
        vals = [date_val.strftime("%Y-%m-%d"), cust_name, cust_phone or "-", license_plate, car_qty or 0, bike_qty or 0, car_check or "", car_act or "", car_tax or "", bike_check or "", bike_act or "", bike_tax or "", reg_type if reg_type != "-- เลือกประเภท --" else "-", service_fee or "", other_income or "", ins_company if ins_company != "-- เลือกบริษัทประกันภัย --" else "-", ins_type if ins_type != "-- เลือกประเภทประกันภัย --" else "-", total, transfer_amt or 0, rem_cash, d_status]
        
        # บันทึกข้อมูลเข้า List ในระบบ
        st.session_state.data_list.insert(0, vals)
        st.toast("🎉 บันทึกข้อมูลเข้าตารางสรุปสำเร็จ และเคลียร์ฟอร์มแล้ว!")
        
        # เรียกฟังก์ชันสลับเวอร์ชันเพื่อเคลียร์ข้อมูลทั้งหมดทันทีอย่างปลอดภัย
        clear_form_fields()
        st.rerun()

# ==================== ส่วนแสดงตารางและระบบกรองดูรายงาน ====================
if st.session_state.data_list:
    st.markdown("---")
    st.subheader("📊 ตารางรายงานสรุปยอดและสถิติข้อมูล")
    
    cols = ["วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)", "ประเภทงาน", "ค่าบริการ", "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"]
    df = pd.DataFrame(st.session_state.data_list, columns=cols)
    df['dt_obj'] = pd.to_datetime(df['วันที่'])

    # แถบเลือกดูรายงาน วัน / เดือน / ปี ตามสั่ง
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

    # สรุปสถิติจำนวนรถจากตารางที่ถูกฟิลเตอร์
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
