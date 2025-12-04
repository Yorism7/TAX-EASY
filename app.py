"""
เว็บแอพคำนวณภาษีเงินได้บุคคลธรรมดา ปี 2568
พัฒนาโดยใช้ Streamlit
"""

import streamlit as st
import pandas as pd
from tax_calculator import calculate_tax_complete
from database import (
    init_db, save_calculation, get_calculations, delete_calculation, get_statistics,
    save_user_profile, get_user_profiles, get_user_profile_by_name, delete_user_profile
)

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="คำนวณภาษีเงินได้บุคคลธรรมดา 2568",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# กำหนด CSS สำหรับ responsive design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Sidebar navigation
st.sidebar.title("📋 เมนู")
page = st.sidebar.radio(
    "เลือกหน้า",
    ["คำนวณภาษี", "จัดการข้อมูลผู้ใช้", "ประวัติการคำนวณ", "สถิติ"]
)

# หน้าคำนวณภาษี
if page == "คำนวณภาษี":
    st.markdown('<div class="main-header">💰 คำนวณภาษีเงินได้บุคคลธรรมดา ปี 2568</div>', unsafe_allow_html=True)
    
    # ตรวจสอบว่ามีการอัปเดตข้อมูลผู้ใช้หรือไม่
    if st.session_state.get('profile_updated', False):
        st.session_state['profile_updated'] = False
        st.rerun()
    
    # ส่วนเลือกผู้ใช้ที่บันทึกไว้
    user_profiles = get_user_profiles()
    if user_profiles:
        st.markdown("### 👤 เลือกผู้ใช้ที่บันทึกไว้")
        profile_names = [p['name'] for p in user_profiles]
        profile_names.insert(0, "--- สร้างใหม่ ---")
        
        # ตรวจสอบว่ามีผู้ใช้ที่โหลดอยู่แล้วหรือไม่
        current_loaded_name = st.session_state.get('loaded_profile', {}).get('name', '') if 'loaded_profile' in st.session_state else ''
        default_index = 0
        if current_loaded_name in profile_names:
            default_index = profile_names.index(current_loaded_name)
        
        selected_profile = st.selectbox("เลือกผู้ใช้", profile_names, index=default_index, key="profile_selector")
        
        # โหลดข้อมูลอัตโนมัติเมื่อเลือกผู้ใช้
        if selected_profile != "--- สร้างใหม่ ---":
            # ตรวจสอบว่าผู้ใช้ที่เลือกเปลี่ยนไปหรือไม่
            if 'loaded_profile' not in st.session_state or st.session_state.get('loaded_profile', {}).get('name', '') != selected_profile:
                profile = get_user_profile_by_name(selected_profile)
                if profile:
                    st.session_state['loaded_profile'] = profile
                    st.session_state['last_name'] = profile['name']  # เก็บชื่อไว้ด้วย
                    st.success(f"✅ โหลดข้อมูล {selected_profile} อัตโนมัติ")
                    st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ ลบข้อมูลผู้ใช้", key="delete_profile", type="secondary", use_container_width=True):
                    if delete_user_profile(selected_profile):
                        # ลบข้อมูลที่โหลดอยู่ถ้าเป็นผู้ใช้คนเดียวกัน
                        if 'loaded_profile' in st.session_state and st.session_state['loaded_profile'].get('name') == selected_profile:
                            del st.session_state['loaded_profile']
                        st.success(f"✅ ลบข้อมูล {selected_profile} สำเร็จ")
                        st.rerun()
                    else:
                        st.error("❌ ไม่สามารถลบข้อมูลได้")
            with col2:
                if 'loaded_profile' in st.session_state and st.session_state['loaded_profile'].get('name') == selected_profile:
                    if st.button("🔄 ล้างข้อมูล", key="clear_profile", use_container_width=True):
                        del st.session_state['loaded_profile']
                        st.success("✅ ล้างข้อมูลสำเร็จ")
                        st.rerun()
        else:
            # ถ้าเลือก "--- สร้างใหม่ ---" ให้ล้างข้อมูลที่โหลดอยู่
            if 'loaded_profile' in st.session_state:
                del st.session_state['loaded_profile']
    
    # โหลดข้อมูลผู้ใช้ที่เลือก
    if 'loaded_profile' in st.session_state:
        profile = st.session_state['loaded_profile']
        income_data_loaded = profile['income_data']
        deductions_data_loaded = profile['deductions_data']
        withholding_tax_loaded = profile['withholding_tax']
        
        # แสดงข้อมูลที่โหลดมา
        with st.expander("📥 ข้อมูลที่โหลดมา", expanded=False):
            st.write(f"**ชื่อ:** {profile['name']}")
            st.write(f"**ข้อมูลเงินได้ ({len(income_data_loaded)} รายการ):**")
            st.json(income_data_loaded)
            st.write(f"**ข้อมูลค่าลดหย่อน ({len(deductions_data_loaded)} รายการ):**")
            st.json(deductions_data_loaded)
            st.write(f"**ภาษีหัก ณ ที่จ่าย:** {withholding_tax_loaded:,.2f} บาท")
        
        # รองรับรูปแบบเก่า (income_40_1_2) และรูปแบบใหม่ (salary_per_month, bonus)
        if 'salary_per_month' not in income_data_loaded and 'income_40_1_2' in income_data_loaded:
            # แปลงรูปแบบเก่าเป็นรูปแบบใหม่ (ประมาณค่า)
            income_data_loaded['salary_per_month'] = income_data_loaded.get('income_40_1_2', 0) / 12
            income_data_loaded['salary_months'] = 12
            income_data_loaded['bonus'] = 0
    else:
        income_data_loaded = {}
        deductions_data_loaded = {}
        withholding_tax_loaded = 0.0
    
    with st.form("tax_calculation_form"):
        st.markdown('<div class="section-header">📝 ข้อมูลรายได้ตามมาตรา 40</div>', unsafe_allow_html=True)
        
        # ข้อมูลพื้นฐาน
        # ใช้ชื่อจาก loaded_profile หรือ session state หรือค่าว่าง
        if 'loaded_profile' in st.session_state:
            default_name = st.session_state['loaded_profile'].get('name', '')
        elif 'last_name' in st.session_state:
            default_name = st.session_state['last_name']
        else:
            default_name = ''
        
        name = st.text_input("ชื่อ-นามสกุล *", value=default_name, placeholder="กรุณากรอกชื่อ", key="name_input")
        
        # ประเภทเงินได้ตามมาตรา 40
        with st.expander("💰 ประเภทเงินได้", expanded=True):
            st.markdown("**40(1)(2) เงินเดือน/โบนัส**")
            col_salary, col_bonus = st.columns(2)
            with col_salary:
                salary_per_month = st.number_input("เงินเดือนต่อเดือน (บาท)", min_value=0.0, 
                                                  value=income_data_loaded.get('salary_per_month', 0.0), step=1000.0, format="%.2f",
                                                  key="salary_per_month")
                salary_months = st.number_input("จำนวนเดือน", min_value=0, max_value=12, value=income_data_loaded.get('salary_months', 12), step=1,
                                               key="salary_months")
                salary_total = salary_per_month * salary_months
                st.info(f"💰 เงินเดือนรวม: {salary_total:,.2f} บาท")
            with col_bonus:
                bonus = st.number_input("โบนัส (บาท)", min_value=0.0, 
                                       value=income_data_loaded.get('bonus', 0.0), step=1000.0, format="%.2f",
                                       key="bonus")
                income_40_1_2 = salary_total + bonus
                st.info(f"💰 เงินเดือน + โบนัสรวม: {income_40_1_2:,.2f} บาท")
            
            expense_40_1_2 = st.number_input("ค่าใช้จ่าย 40(1)(2) (ถ้าไม่ระบุจะใช้ 100,000)", min_value=0.0, 
                                            value=income_data_loaded.get('expense_40_1_2', 100000.0), step=1000.0, format="%.2f",
                                            help="สูงสุด 100,000 บาท", key="expense_40_1_2")
            
            col1, col2 = st.columns(2)
            with col1:
                income_40_4 = st.number_input("40(4) ดอกเบี้ย/เงินปันผล", min_value=0.0, 
                                             value=income_data_loaded.get('income_40_4', 0.0), step=1000.0, format="%.2f",
                                             help="หักค่าใช้จ่าย 10%", key="income_40_4")
            with col2:
                income_40_5 = st.number_input("40(5) ค่าเช่าทรัพย์สิน", min_value=0.0, 
                                             value=income_data_loaded.get('income_40_5', 0.0), step=1000.0, format="%.2f",
                                             help="หักค่าใช้จ่าย 30%", key="income_40_5")
                income_40_6 = st.number_input("40(6) เงินได้วิชาชีพอิสระ", min_value=0.0, 
                                             value=income_data_loaded.get('income_40_6', 0.0), step=1000.0, format="%.2f",
                                             help="หักค่าใช้จ่าย 60%", key="income_40_6")
                income_40_7 = st.number_input("40(7) เงินได้จากการรับเหมา", min_value=0.0, 
                                             value=income_data_loaded.get('income_40_7', 0.0), step=1000.0, format="%.2f",
                                             help="หักค่าใช้จ่าย 70%", key="income_40_7")
                income_40_8 = st.number_input("40(8) เงินได้อื่นๆ", min_value=0.0, 
                                             value=income_data_loaded.get('income_40_8', 0.0), step=1000.0, format="%.2f",
                                             help="หักค่าใช้จ่าย 92%", key="income_40_8")
        
        st.markdown('<div class="section-header">📋 ค่าลดหย่อน</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("👨‍👩‍👧‍👦 ส่วนตัวและครอบครัว", expanded=True):
                personal = st.number_input("ค่าลดหย่อนส่วนตัว", min_value=0.0, 
                                         value=deductions_data_loaded.get('personal', 60000.0), step=1000.0, format="%.2f", key="personal")
                spouse = st.checkbox("มีคู่สมรส (ไม่มีรายได้)", 
                                    value=deductions_data_loaded.get('spouse', False), key="spouse")
                children = st.number_input("จำนวนบุตร", min_value=0, 
                                         value=deductions_data_loaded.get('children', 0), step=1, key="children")
                children_2nd = st.number_input("จำนวนบุตรคนที่ 2 เกิดหลังปี 2561", min_value=0, 
                                             value=deductions_data_loaded.get('children_2nd', 0), step=1, 
                                             help="บุตรคนที่ 2 ที่เกิดหลังปี 2561 จะได้ค่าลดหย่อนคนละ 60,000 บาท", key="children_2nd")
                parents = st.number_input("จำนวนบิดามารดา (อายุ 60+ ปี)", min_value=0, 
                                         value=deductions_data_loaded.get('parents', 0), step=1, key="parents")
            
            with st.expander("🛡️ ประกัน", expanded=True):
                life_insurance = st.number_input("เบี้ยประกันชีวิต", min_value=0.0, 
                                               value=deductions_data_loaded.get('life_insurance', 0.0), step=1000.0, format="%.2f",
                                               help="สูงสุด 100,000 บาท", key="life_insurance")
                health_insurance_self = st.number_input("เบี้ยประกันสุขภาพตนเอง", min_value=0.0, 
                                                      value=deductions_data_loaded.get('health_insurance_self', 0.0), step=1000.0, format="%.2f",
                                                      help="สูงสุด 25,000 บาท", key="health_insurance_self")
                health_insurance_parent = st.number_input("เบี้ยประกันสุขภาพบิดามารดา", min_value=0.0, 
                                                          value=deductions_data_loaded.get('health_insurance_parent', 0.0), step=1000.0, format="%.2f",
                                                          help="สูงสุด 15,000 บาท", key="health_insurance_parent")
        
        with col2:
            with st.expander("📈 การลงทุน", expanded=True):
                rmf = st.number_input("กองทุน RMF", min_value=0.0, 
                                    value=deductions_data_loaded.get('rmf', 0.0), step=1000.0, format="%.2f",
                                    help="30% ของเงินได้ สูงสุด 500,000 บาท", key="rmf")
                ssf = st.number_input("กองทุน SSF", min_value=0.0, 
                                    value=deductions_data_loaded.get('ssf', 0.0), step=1000.0, format="%.2f",
                                    help="30% ของเงินได้ สูงสุด 200,000 บาท", key="ssf")
                pvd = st.number_input("กองทุนสำรองเลี้ยงชีพ (PVD)", min_value=0.0, 
                                    value=deductions_data_loaded.get('pvd', 0.0), step=1000.0, format="%.2f",
                                    help="15% ของเงินได้ สูงสุด 500,000 บาท", key="pvd")
                thai_esg = st.number_input("กองทุน Thai ESG", min_value=0.0, 
                                         value=deductions_data_loaded.get('thai_esg', 0.0), step=1000.0, format="%.2f",
                                         help="30% ของเงินได้ สูงสุด 300,000 บาท", key="thai_esg")
                nssf = st.number_input("กองทุนการออมแห่งชาติ (กอช.)", min_value=0.0, 
                                      value=deductions_data_loaded.get('nssf', 0.0), step=1000.0, format="%.2f",
                                      help="สูงสุด 30,000 บาท", key="nssf")
                social_security = st.number_input("เงินสมทบกองทุนประกันสังคม", min_value=0.0, 
                                                value=deductions_data_loaded.get('social_security', 0.0), step=1000.0, format="%.2f",
                                                help="สูงสุด 9,000 บาท", key="social_security")
            
            with st.expander("💼 อื่นๆ", expanded=True):
                easy_e_receipt = st.checkbox("Easy E-Receipt 2568 (50,000 บาท)", 
                                           value=deductions_data_loaded.get('easy_e_receipt', False), key="easy_e_receipt",
                                           help="ระหว่างวันที่ 16 ม.ค. - 28 ก.พ. 2568")
                solar_cell = st.number_input("ค่าติดตั้งโซลาร์เซลล์", min_value=0.0, 
                                            value=deductions_data_loaded.get('solar_cell', 0.0), step=1000.0, format="%.2f",
                                            help="สูงสุด 200,000 บาท (ถึง 31 ธ.ค. 2570)", key="solar_cell")
                home_construction = st.number_input("ค่าก่อสร้างบ้านใหม่", min_value=0.0, 
                                                  value=deductions_data_loaded.get('home_construction', 0.0), step=1000.0, format="%.2f",
                                                  help="สูงสุด 100,000 บาท (9 เม.ย. 2567 - 31 ธ.ค. 2568)", key="home_construction")
                home_interest = st.number_input("ดอกเบี้ยที่อยู่อาศัย", min_value=0.0, 
                                              value=deductions_data_loaded.get('home_interest', 0.0), step=1000.0, format="%.2f",
                                              help="สูงสุด 100,000 บาท", key="home_interest")
                donation = st.number_input("เงินบริจาคทั่วไป", min_value=0.0, 
                                         value=deductions_data_loaded.get('donation', 0.0), step=1000.0, format="%.2f",
                                         help="สูงสุด 10% ของเงินได้หลังหักค่าลดหย่อน", key="donation")
                education_donation = st.number_input("เงินบริจาคเพื่อการศึกษา", min_value=0.0, 
                                                    value=deductions_data_loaded.get('education_donation', 0.0), step=1000.0, format="%.2f",
                                                    help="2 เท่าของเงินบริจาค แต่ไม่เกิน 10% ของเงินได้หลังหักค่าลดหย่อน", key="education_donation")
                political_donation = st.number_input("เงินบริจาคพรรคการเมือง", min_value=0.0, 
                                                    value=deductions_data_loaded.get('political_donation', 0.0), step=1000.0, format="%.2f",
                                                    help="สูงสุด 10,000 บาท", key="political_donation")
                social_enterprise = st.number_input("เงินลงทุนในธุรกิจวิสาหกิจเพื่อสังคม", min_value=0.0, 
                                                   value=deductions_data_loaded.get('social_enterprise', 0.0), step=1000.0, format="%.2f",
                                                   help="สูงสุด 100,000 บาท", key="social_enterprise")
        
        withholding_tax = st.number_input("ภาษีหัก ณ ที่จ่าย", min_value=0.0, value=withholding_tax_loaded, step=100.0, format="%.2f",
                                         help="ภาษีที่หักไว้แล้ว", key="withholding_tax")
        
        submitted = st.form_submit_button("🔢 คำนวณภาษี", use_container_width=True)
        
        if submitted:
            # เก็บชื่อไว้ใน session state
            if name and name.strip():
                st.session_state['last_name'] = name.strip()
            
            # ล้างข้อมูลที่โหลดไว้เมื่อกดคำนวณใหม่ (แต่เก็บชื่อไว้)
            if 'loaded_profile' in st.session_state:
                del st.session_state['loaded_profile']
            
            if not name or name.strip() == "":
                st.error("⚠️ กรุณากรอกชื่อ-นามสกุล")
            else:
                # คำนวณเงินเดือนรวม
                salary_total = salary_per_month * salary_months
                income_40_1_2 = salary_total + bonus
                
                # เตรียมข้อมูลเงินได้
                income_data = {
                    'salary_per_month': salary_per_month,
                    'salary_months': salary_months,
                    'bonus': bonus,
                    'income_40_1_2': income_40_1_2,
                    'expense_40_1_2': expense_40_1_2,
                    'income_40_4': income_40_4,
                    'income_40_5': income_40_5,
                    'income_40_6': income_40_6,
                    'income_40_7': income_40_7,
                    'income_40_8': income_40_8
                }
                
                # เตรียมข้อมูลค่าลดหย่อน
                deductions_data = {
                    'personal': personal,
                    'spouse': spouse,
                    'children': children,
                    'children_2nd': children_2nd,
                    'parents': parents,
                    'life_insurance': life_insurance,
                    'health_insurance_self': health_insurance_self,
                    'health_insurance_parent': health_insurance_parent,
                    'rmf': rmf,
                    'ssf': ssf,
                    'pvd': pvd,
                    'thai_esg': thai_esg,
                    'nssf': nssf,
                    'social_security': social_security,
                    'easy_e_receipt': easy_e_receipt,
                    'solar_cell': solar_cell,
                    'home_construction': home_construction,
                    'home_interest': home_interest,
                    'donation': donation,
                    'education_donation': education_donation,
                    'political_donation': political_donation,
                    'social_enterprise': social_enterprise
                }
                
                # คำนวณภาษี
                result = calculate_tax_complete(income_data, deductions_data, withholding_tax)
                
                # แสดงผลการคำนวณ
                st.success("✅ คำนวณสำเร็จ!")
                
                # แสดงสรุปผลการคำนวณตามรูปภาพ
                st.markdown("### 📊 สรุปผลการคำนวณภาษี")
                
                # ตารางสรุป
                summary_data = [
                    ["เงินได้", f"{result['total_income']:,.2f}"],
                    ["หักค่าใช้จ่าย", f"{result['total_expenses']:,.2f}"],
                    ["เงินได้หลังหักค่าใช้จ่าย", f"{result['income_after_expenses']:,.2f}"],
                    ["หักค่าลดหย่อน", f"{result['total_deductions']:,.2f}"],
                    ["เงินได้หลังหักค่าลดหย่อน", f"{result['net_income'] + result['total_donation']:,.2f}"],
                    ["หัก เงินบริจาค", f"{result['total_donation']:,.2f}"],
                    ["เงินได้สุทธิ", f"{result['net_income']:,.2f}"],
                    ["ภาษีที่ประเมิน", f"{result['tax']:,.2f}"],
                    ["% ของเงินได้ทั้งปี", f"{result['tax_percent_of_income']:.2f}%"],
                    ["% ของเงินได้สุทธิ", f"{result['tax_percent_of_net']:.2f}%"],
                ]
                
                summary_df = pd.DataFrame(summary_data, columns=["รายการ", "จำนวนเงิน (บาท)"])
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # เงินคืน/เงินเพิ่ม
                st.markdown("### 💰 เงินคืน/เงินเพิ่ม")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("ภาษีหัก ณ ที่จ่าย", f"{result['withholding_tax']:,.2f} บาท")
                with col2:
                    if result['tax_refund'] > 0:
                        st.metric("เงินคืน", f"{result['tax_refund']:,.2f} บาท", delta="เงินคืน")
                    elif result['tax_additional'] > 0:
                        st.metric("เงินเพิ่ม", f"{result['tax_additional']:,.2f} บาท", delta="ต้องจ่ายเพิ่ม")
                    else:
                        st.metric("เงินคืน/เงินเพิ่ม", "0.00 บาท")
                
                # รายละเอียดเงินได้
                with st.expander("📋 รายละเอียดเงินได้ตามมาตรา 40", expanded=False):
                    income_detail_data = []
                    for key, detail in result['income_details'].items():
                        income_detail_data.append({
                            "ประเภท": key,
                            "เงินได้": f"{detail['income']:,.2f}",
                            "หักค่าใช้จ่าย": f"{detail['expense']:,.2f}",
                            "เงินได้หลังหักค่าใช้จ่าย": f"{detail['net']:,.2f}"
                        })
                    if income_detail_data:
                        income_detail_df = pd.DataFrame(income_detail_data)
                        st.dataframe(income_detail_df, use_container_width=True, hide_index=True)
                
                # รายละเอียดค่าลดหย่อน
                with st.expander("📊 รายละเอียดค่าลดหย่อน", expanded=False):
                    deduction_detail_data = []
                    for key, value in result['deduction_details'].items():
                        if value > 0:
                            deduction_detail_data.append({
                                "ประเภท": key,
                                "จำนวนเงิน (บาท)": f"{value:,.2f}"
                            })
                    if deduction_detail_data:
                        deduction_detail_df = pd.DataFrame(deduction_detail_data)
                        st.dataframe(deduction_detail_df, use_container_width=True, hide_index=True)
                
                # รายละเอียดการคำนวณภาษี
                if result['tax_details']:
                    with st.expander("📈 รายละเอียดการคำนวณภาษี (ขั้นบันได)", expanded=False):
                        tax_df = pd.DataFrame(result['tax_details'])
                        tax_df['ช่วงรายได้'] = tax_df['range']
                        tax_df['จำนวนเงินที่ต้องเสียภาษี (บาท)'] = tax_df['taxable_amount'].apply(lambda x: f"{x:,.2f}")
                        tax_df['อัตราภาษี (%)'] = tax_df['rate']
                        tax_df['ภาษี (บาท)'] = tax_df['tax'].apply(lambda x: f"{x:,.2f}")
                        tax_df = tax_df[['ช่วงรายได้', 'จำนวนเงินที่ต้องเสียภาษี (บาท)', 'อัตราภาษี (%)', 'ภาษี (บาท)']]
                        st.dataframe(tax_df, use_container_width=True, hide_index=True)
                
                # บันทึกข้อมูลผู้ใช้อัตโนมัติเมื่อกดคำนวณ
                if name and name.strip():
                    try:
                        # ตรวจสอบข้อมูลก่อนบันทึก
                        income_keys_count = len(income_data)
                        deductions_keys_count = len(deductions_data)
                        
                        user_id = save_user_profile(
                            name.strip(),
                            income_data,
                            deductions_data,
                            withholding_tax
                        )
                        
                        st.success(f"💾 บันทึกข้อมูลผู้ใช้อัตโนมัติแล้ว (ID: {user_id})")
                        st.caption(f"บันทึกข้อมูลเงินได้ {income_keys_count} รายการ, ค่าลดหย่อน {deductions_keys_count} รายการ")
                        
                        # อัปเดต loaded_profile เพื่อให้ข้อมูลใหม่แสดงใน dropdown
                        st.session_state['loaded_profile'] = {
                            'name': name.strip(),
                            'income_data': income_data,
                            'deductions_data': deductions_data,
                            'withholding_tax': withholding_tax
                        }
                        
                        # ตั้งค่า flag เพื่อให้ dropdown อัปเดตในรอบถัดไป
                        st.session_state['profile_updated'] = True
                    except Exception as e:
                        import traceback
                        error_msg = str(e)
                        error_trace = traceback.format_exc()
                        st.error(f"❌ ไม่สามารถบันทึกข้อมูลผู้ใช้อัตโนมัติได้: {error_msg}")
                        with st.expander("รายละเอียดข้อผิดพลาด", expanded=False):
                            st.code(error_trace)
                
                # เก็บผลการคำนวณใน session state สำหรับปุ่มบันทึกประวัติ
                st.session_state['last_calculation'] = {
                    'name': name,
                    'result': result,
                    'income_data': income_data,
                    'deductions_data': deductions_data,
                    'withholding_tax': withholding_tax
                }
    
    # ปุ่มบันทึกประวัติการคำนวณ (ถ้าต้องการ)
    if 'last_calculation' in st.session_state:
        st.markdown("---")
        if st.button("💾 บันทึกประวัติการคำนวณ", use_container_width=True):
            try:
                calc_data = st.session_state['last_calculation']
                # ปรับข้อมูลให้เข้ากับ database
                save_result = {
                    'income': calc_data['result']['total_income'],
                    'total_deductions': calc_data['result']['total_deductions'],
                    'net_income': calc_data['result']['net_income'],
                    'tax': calc_data['result']['tax'],
                    'deduction_details': calc_data['result']['deduction_details'],
                    'tax_details': calc_data['result']['tax_details']
                }
                calculation_id = save_calculation(calc_data['name'], save_result)
                st.success(f"✅ บันทึกประวัติการคำนวณสำเร็จ! (ID: {calculation_id})")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการบันทึก: {str(e)}")

# หน้าจัดการข้อมูลผู้ใช้
elif page == "จัดการข้อมูลผู้ใช้":
    st.title("👤 จัดการข้อมูลผู้ใช้")
    
    user_profiles = get_user_profiles()
    
    if not user_profiles:
        st.info("ยังไม่มีข้อมูลผู้ใช้")
    else:
        st.write(f"**จำนวนผู้ใช้ทั้งหมด: {len(user_profiles)} คน**")
        
        # แสดงตารางผู้ใช้
        df_data = []
        for profile in user_profiles:
            df_data.append({
                "ID": profile['id'],
                "ชื่อ": profile['name'],
                "อัปเดตล่าสุด": profile['updated_at'],
                "สร้างเมื่อ": profile['created_at']
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # ส่วนลบข้อมูล
        st.subheader("🗑️ ลบข้อมูลผู้ใช้")
        profile_names = [p['name'] for p in user_profiles]
        selected_name = st.selectbox("เลือกผู้ใช้ที่ต้องการลบ", profile_names, key="delete_user_selector")
        
        if st.button("ลบข้อมูลผู้ใช้", type="primary", key="delete_user_btn"):
            if delete_user_profile(selected_name):
                st.success(f"✅ ลบข้อมูล {selected_name} สำเร็จ")
                st.rerun()
            else:
                st.error("❌ ไม่สามารถลบข้อมูลได้")

# หน้าประวัติการคำนวณ
elif page == "ประวัติการคำนวณ":
    st.title("📚 ประวัติการคำนวณ")
    
    calculations = get_calculations()
    
    if not calculations:
        st.info("ยังไม่มีประวัติการคำนวณ")
    else:
        st.write(f"**จำนวนรายการทั้งหมด: {len(calculations)} รายการ**")
        
        # แสดงตาราง
        df_data = []
        for calc in calculations:
            df_data.append({
                "ID": calc['id'],
                "ชื่อ": calc['name'],
                "รายได้รวม": f"{calc['income']:,.2f}",
                "ค่าลดหย่อน": f"{calc['total_deductions']:,.2f}",
                "รายได้สุทธิ": f"{calc['net_income']:,.2f}",
                "ภาษี": f"{calc['tax']:,.2f}",
                "วันที่": calc['created_at']
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # ส่วนลบข้อมูล
        st.subheader("🗑️ ลบข้อมูล")
        calc_ids = [calc['id'] for calc in calculations]
        selected_id = st.selectbox("เลือก ID ที่ต้องการลบ", calc_ids)
        
        if st.button("ลบข้อมูล", type="primary"):
            if delete_calculation(selected_id):
                st.success(f"✅ ลบข้อมูล ID {selected_id} สำเร็จ")
                st.rerun()
            else:
                st.error("❌ ไม่สามารถลบข้อมูลได้")

# หน้าสถิติ
elif page == "สถิติ":
    st.title("📊 สถิติการคำนวณ")
    
    stats = get_statistics()
    
    if stats['total_calculations'] == 0:
        st.info("ยังไม่มีข้อมูลสถิติ")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("จำนวนการคำนวณ", f"{stats['total_calculations']}")
            st.metric("ภาษีรวมทั้งหมด", f"{stats['total_tax']:,.2f} บาท")
        with col2:
            st.metric("ภาษีเฉลี่ย", f"{stats['avg_tax']:,.2f} บาท")
            st.metric("รายได้เฉลี่ย", f"{stats['avg_income']:,.2f} บาท")
