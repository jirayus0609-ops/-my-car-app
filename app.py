import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# ตั้งค่าหน้าตาของโปรแกรม
st.set_page_config(page_title="ระบบบันทึกบริการรถ", layout="wide")
st.title("🚗🏍️ ระบบบันทึกข้อมูลบริการรถและประกันภัย (บันทึกลงไฟล์ Excel ถาวร)")

# ชื่อไฟล์ Excel ที่ใช้เก็บข้อมูลหลักในระบบ
EXCEL_FILE = "data.xlsx"

# กำหนดรายชื่อหัวคอลัมน์ทั้งหมดของระบบให้เป็นระเบียบเรียบร้อย
column_headers = [
    "วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", 
    "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", 
    "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)", "ประเภทงาน", "ค่าบริการ", 
    "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"
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

tab1, tab2, tab3 = st.tabs(["🚗 รถยนต์", "🏍️ มอเตอร์ไซค์", "💼 ทะเบียน/ประกัน"])
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
    reg_type = st.selectbox("งานทะเบียน", ["-- เลือกประเภท --", "โอน", "จดใหม่", "ปรับสมุด"], key="reg_v_" + v)
    service_fee = st.number_input("ค่าบริการทะเบียน", min_value=0.0, value=None, key="fee_" + v)
    ins_company = st.selectbox("บริษัทประกัน", ["-- เลือกบริษัทประกันภัย --", "บริษัททิพยประกันภัย", "บริษัทเออร์โกประกันภัย", "บริษัทอินทรประกันภัย", "บริษัทไทยพัฒนาประกันภัย"], key="ins_c_" + v)
    ins_type = st.selectbox("ประเภทประกัน", ["-- เลือกประเภทประกันภัย --", "ประเภท 1", "ประเภท 2", "ประเภท 2+", "ประเภท 3", "ประเภท 3+"], key="ins_t_" + v)
    ins_price = st.number_input("เบี้ยประกันภัย", min_value=0.0, value=None, key="ins_p_" + v)
    other_income = st.number_input("รายรับอื่นๆ", min_value=0.0, value=None, key="other_" + v)

# คำนวณรวมยอดเงินอัตโนมัติ
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
        st.error("❌ กรุณากรอก ชื่อ-นามสกุล และ ทะเบียนรถ")
    else:
        d_status = f"ค้างชำระ: {debt_amt or 0:,.2f} บ." if is_debt else "ปกติ"
        
        row_values = [
            date_val.strftime("%Y-%m-%d"), cust_name, cust_phone or "-", license_plate,
            car_qty or 0, bike_qty or 0, car_check or "", car_act or "", car_tax or "",
            bike_check or "", bike_act or "", bike_tax or "",
            reg_type if reg_type != "-- เลือกประเภท --" else "-", service_fee or "", other_income or "",
            ins_company if ins_company != "-- เลือกบริษัทประกันภัย --" else "-",
            ins_type if ins_type != "-- เลือกประเภทประกันภัย --" else "-",
            total, transfer_amt or 0, rem_cash, d_status
        ]
        
        try:
            new_df = pd.DataFrame([row_values], columns=column_headers)
            updated_df = pd.concat([new_df, df_existing], ignore_index=True) if not df_existing.empty else new_df
            updated_df.to_excel(EXCEL_FILE, index=False)
            
            st.success("🎉 บันทึกข้อมูลลงไฟล์ Excel ถาวรในระบบสำเร็จ และล้างแบบฟอร์มเรียบร้อยแล้ว!")
            clear_form_fields()
            st.rerun()
        except Exception as err:
            st.error(f"❌ เกิดข้อผิดพลาดในการบันทึกข้อมูล: {err}")

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

    # สรุปสถิติจำนวนรถจากตารางที่เลือก
    total_cars = pd.to_numeric(df_filtered['รถยนต์ (คัน)'], errors='coerce').fillna(0).sum()
    total_bikes = pd.to_numeric(df_filtered['มอเตอร์ไซค์ (คัน)'], errors='coerce').fillna(0).sum()
    total_money = pd.to_numeric(df_filtered['ยอดรวม'], errors='coerce').fillna(0).sum()
    
    s1, s2, s3 = st.columns(3)
    s1.metric("🚗 จำนวนรถยนต์รวม", f"{int(total_cars)} คัน")
    s2.metric("🏍️ จำนวนมอเตอร์ไซค์รวม", f"{int(total_bikes)} คัน")
    s3.metric("💰 ยอดเงินรวมในช่วงที่เลือก", f"{total_money:,.2f} บาท")

    # แสดงตารางข้อมูลดิบ
    st.dataframe(df_filtered.drop(columns=['dt_obj'], errors='ignore'), use_container_width=True)
    
    # ระบบแปลง DataFrame เป็นรหัสไบนารีสำหรับปุ่มดาวน์โหลดไฟล์ Excel (.xlsx)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_existing.to_excel(writer, index=False, sheet_name='DataLog')
    excel_data = buffer.getvalue()
    
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลทั้งหมดเป็นไฟล์ Excel (.xlsx)",
        data=excel_data,
        file_name=f"รายงานข้อมูลร้านรถ_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    # เครื่องมือลบแถว (กรณีคีย์ผิด)
    with st.expander("🗑️ เครื่องมือลบข้อมูลแถวที่พิมพ์ผิด"):
        st.warning("คำเตือน: การลบข้อมูลตรงนี้จะลบออกจากระบบไฟล์ Excel อย่างถาวร")
        row_to_delete = st.number_input("ระบุเลขแถวซ้ายสุดที่ต้องการลบ", min_value=0, max_value=len(df)-1, step=1)
        if st.button("❌ กดเพื่อลบแถวนี้ถาวร"):
            try:
                df_dropped = df_existing.drop(index=row_to_delete).reset_index(drop=True)
                df_dropped.to_excel(EXCEL_FILE, index=False)
                st.success("ลบข้อมูลออกจากระบบไฟล์ Excel เรียบร้อยแล้ว!")
                st.rerun()
            except Exception as de:
                st.error(f"❌ ลบไม่สำเร็จ: {de}")
else:
    st.markdown("---")
    st.info("💡 ระบบไฟล์ Excel พร้อมใช้งานแล้ว! ตารางและรายงานสรุป รายวัน/รายเดือน/รายปี จะแสดงขึ้นมาทันทีเมื่อคุณเริ่มบันทึกข้อมูลลูกค้าคนแรกครับ")
