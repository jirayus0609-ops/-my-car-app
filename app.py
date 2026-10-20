import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ระบบบันทึกบริการรถ", layout="wide")
st.title("🚗🏍️ ระบบบันทึกข้อมูลบริการรถและประกันภัย")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existing = conn.read(ttl=0)
except Exception as e:
    st.error("⚠️ ยังไม่ได้ตั้งค่าเชื่อมต่อกับ Google Sheets")
    df_existing = pd.DataFrame()

def reset_form():
    for k in st.session_state.keys():
        if k not in ["data_list"]: st.session_state[k] = None if "qty" in k or "price" in k or "amt" in k or "fee" in k or "check" in k or "act" in k or "tax" in k else ""
    st.session_state.reg_type = "-- เลือกประเภท --"
    st.session_state.ins_company = "-- เลือกบริษัทประกันภัย --"
    st.session_state.ins_type = "-- เลือกประเภทประกันภัย --"
    st.session_state.is_debt = False

# ==================== ส่วนสถิติรายวัน/เดือน/ปี ====================
st.markdown("---")
st.subheader("📊 สรุปยอดจำนวนรถที่เข้าใช้บริการ")
if not df_existing.empty and "วันที่" in df_existing.columns:
    df_s = df_existing.copy()
    df_s['dt'] = pd.to_datetime(df_s['วันที่'], errors='coerce')
    df_s['c_count'] = df_s['รถยนต์ (คัน)'].apply(lambda x: int(x) if str(x).isdigit() else 0)
    df_s['b_count'] = df_s['มอเตอร์ไซค์ (คัน)'].apply(lambda x: int(x) if str(x).isdigit() else 0)
    
    t_str = datetime.now().strftime("%Y-%m-%d")
    c_m, c_y = datetime.now().month, datetime.now().year
    
    d1, d2, d3 = st.columns(3)
    d1.metric("วันนี้ (ยนต์/มอไซค์)", f"{df_s[df_s['วันที่']==t_str]['c_count'].sum()} / {df_s[df_s['วันที่']==t_str]['b_count'].sum()} คัน")
    d2.metric("เดือนนี้ (ยนต์/มอไซค์)", f"{df_s[df_s['dt'].dt.month==c_m]['c_count'].sum()} / {df_s[df_s['dt'].dt.month==c_m]['b_count'].sum()} คัน")
    d3.metric("ปีนี้ (ยนต์/มอไซค์)", f"{df_s[df_s['dt'].dt.year==c_y]['c_count'].sum()} / {df_s[df_s['dt'].dt.year==c_y]['b_count'].sum()} คัน")
else:
    st.info("💡 เริ่มแสดงสถิติเมื่อเชื่อมต่อฐานข้อมูลสำเร็จ")

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

# ==================== คำนวณเงินโอน/เงินสด ====================
total = sum([car_check or 0, car_act or 0, car_tax or 0, bike_check or 0, bike_act or 0, bike_tax or 0, service_fee or 0, other_income or 0, ins_price or 0])

st.markdown("### 💰 สรุปยอดเงิน")
p1, p2, p3 = st.columns(3)
p1.markdown(f"#### ยอดรวมทั้งหมด: `{total:,.2f}` บาท")
transfer_amt = p2.number_input("เงินโอน (บาท)", key="transfer_amt", min_value=0.0, value=None)
rem_cash = max(0.0, total - (transfer_amt or 0.0))
p3.markdown(f"#### เงินสดต้องจ่ายเพิ่ม: `{rem_cash:,.2f}` บาท" if total > 0 else "#### เงินสดต้องจ่ายเพิ่ม:")

is_debt = st.checkbox("⚠️ ลูกค้าค้างชำระ", key="is_debt")
debt_amt = st.number_input("เงินที่ค้างชำระ (บาท)", key="debt_amt", min_value=0.0, value=None) if is_debt else None

# ==================== บันทึกและลบข้อมูล ====================
if st.button("💾 บันทึกข้อมูล", type="primary", use_container_width=True):
    if not cust_name or not license_plate:
        st.error("❌ กรุณากรอก ชื่อ-นามสกุล และ ทะเบียนรถ")
    else:
        d_status = f"ค้างชำระ: {debt_amt or 0:,.2f} บ." if is_debt else "ปกติ"
        cols = ["วันที่", "ชื่อ-นามสกุล", "เบอร์โทร", "ทะเบียนรถ", "รถยนต์ (คัน)", "มอเตอร์ไซค์ (คัน)", "ตรวจสภาพ(รถ)", "พรบ(รถ)", "ภาษี(รถ)", "ตรวจสภาพ(มอไซค์)", "พรบ(มอไซค์)", "ภาษี(มอไซค์)", "ประเภทงาน", "ค่าบริการ", "รายรับอื่นๆ", "บริษัทประกัน", "ประเภทประกัน", "ยอดรวม", "เงินโอน", "เงินสด", "สถานะการจ่ายเงิน"]
        vals = [date_val.strftime("%Y-%m-%d"), cust_name, cust_phone or "-", license_plate, str(car_qty or ""), str(bike_qty or ""), car_check or "", car_act or "", car_tax or "", bike_check or "", bike_act or "", bike_tax or "", reg_type if reg_type != "-- เลือกประเภท --" else "-", service_fee or "", other_income or "", ins_company if ins_company != "-- เลือกบริษัทประกันภัย --" else "-", ins_type if ins_type != "-- เลือกประเภทประกันภัย --" else "-", total, transfer_amt or "", rem_cash if rem_cash > 0 else "", d_status]
        try:
            new_df = pd.DataFrame([vals], columns=cols)
            up_df = pd.concat([new_df, df_existing], ignore_index=True) if not df_existing.empty else new_df
            conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=up_df)
            st.success("🎉 บันทึกข้อมูลสำเร็จ!")
            reset_form()
            st.rerun()
        except Exception as err:
            st.error(f"❌ บันทึกไม่สำเร็จ: {err}")

if not df_existing.empty:
    with st.expander("🗑️ เครื่องมือลบข้อมูล (คีย์ผิด)"):
        r_del = st.number_input("ระบุเลขแถวที่ต้องการลบ", min_value=0, max_value=len(df_existing)-1, step=1)
        if st.button("❌ ลบข้อมูลแถวนี้ถาวร"):
            try:
                df_dr = df_existing.drop(index=r_del).reset_index(drop=True)
                conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_dr)
                st.success("🗑️ ลบข้อมูลเรียบร้อย!")
                st.rerun()
            except Exception as de:
                st.error(f"❌ ลบไม่สำเร็จ: {de}")

st.markdown("---")
st.subheader("📊 ตารางรายการข้อมูลทั้งหมดล่าสุด")
if not df_existing.empty:
    st.dataframe(df_existing, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลในระบบ")
