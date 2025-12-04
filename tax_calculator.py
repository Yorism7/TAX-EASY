"""
โมดูลคำนวณภาษีเงินได้บุคคลธรรมดา ปี 2568
"""

# อัตราภาษีขั้นบันไดปี 2568
TAX_BRACKETS = [
    (0, 150000, 0.0),
    (150001, 300000, 0.05),
    (300001, 500000, 0.10),
    (500001, 750000, 0.15),
    (750001, 1000000, 0.20),
    (1000001, 2000000, 0.25),
    (2000001, 5000000, 0.30),
    (5000001, float('inf'), 0.35),
]

# ค่าลดหย่อนพื้นฐาน
PERSONAL_DEDUCTION = 60000
SPOUSE_DEDUCTION = 60000
CHILD_DEDUCTION = 30000
CHILD_DEDUCTION_2ND = 60000  # บุตรคนที่ 2 เกิดหลังปี 2561
PARENT_DEDUCTION = 30000

# วงเงินค่าลดหย่อนสูงสุด ปี 2568
MAX_LIFE_INSURANCE = 100000
MAX_HEALTH_INSURANCE_SELF = 25000
MAX_HEALTH_INSURANCE_PARENT = 15000
MAX_SOCIAL_SECURITY = 9000

# กองทุนการออมและการลงทุน
MAX_RMF_PERCENT = 0.30  # 30% ของเงินได้
MAX_RMF_AMOUNT = 500000
MAX_SSF_PERCENT = 0.30  # 30% ของเงินได้
MAX_SSF_AMOUNT = 200000
MAX_PVD_PERCENT = 0.15  # 15% ของเงินได้
MAX_PVD_AMOUNT = 500000
MAX_RMF_SSF_PVD_COMBINED = 500000  # รวม RMF + SSF + PVD ไม่เกิน 500,000
MAX_THAI_ESG_PERCENT = 0.30  # 30% ของเงินได้
MAX_THAI_ESG_AMOUNT = 300000  # ปรับเป็น 300,000 ตามปี 2568
MAX_NSSF = 30000  # กองทุนการออมแห่งชาติ (กอช.)

# ค่าลดหย่อนเพื่อกระตุ้นเศรษฐกิจ
EASY_E_RECEIPT = 50000  # Easy E-Receipt 2568
MAX_SOLAR_CELL = 200000  # ค่าติดตั้งโซลาร์เซลล์
MAX_HOME_CONSTRUCTION = 100000  # ค่าก่อสร้างบ้านใหม่
MAX_HOME_INTEREST = 100000  # ดอกเบี้ยที่อยู่อาศัย

# ค่าลดหย่อนจากการบริจาค
MAX_DONATION_PERCENT = 0.10  # 10% ของเงินได้หลังหักค่าลดหย่อน
EDUCATION_DONATION_MULTIPLIER = 2  # 2 เท่าของเงินบริจาค
MAX_POLITICAL_DONATION = 10000  # เงินบริจาคพรรคการเมือง
MAX_SOCIAL_ENTERPRISE = 100000  # เงินลงทุนในธุรกิจวิสาหกิจเพื่อสังคม

# อัตราหักค่าใช้จ่ายตามประเภทเงินได้มาตรา 40
EXPENSE_RATES = {
    '40_1_2': 100000,  # 40(1)(2) เงินเดือน/โบนัส - หัก 100,000 หรือตามจริง
    '40_4': 0.10,  # 40(4) ดอกเบี้ย/เงินปันผล - หัก 10%
    '40_5': 0.30,  # 40(5) ค่าเช่าทรัพย์สิน - หัก 30%
    '40_6': 0.60,  # 40(6) เงินได้วิชาชีพอิสระ - หัก 60%
    '40_7': 0.70,  # 40(7) เงินได้จากการรับเหมา - หัก 70%
    '40_8': 0.92,  # 40(8) เงินได้อื่นๆ - หัก 92%
}


def calculate_income_expenses(income_data):
    """
    คำนวณหักค่าใช้จ่ายตามประเภทเงินได้มาตรา 40
    
    Args:
        income_data: dictionary ประกอบด้วย:
            - income_40_1_2: เงินเดือน/โบนัส 40(1)(2)
            - expense_40_1_2: ค่าใช้จ่าย 40(1)(2) (ถ้าไม่ระบุจะใช้ 100,000)
            - income_40_4: ดอกเบี้ย/เงินปันผล 40(4)
            - income_40_5: ค่าเช่าทรัพย์สิน 40(5)
            - income_40_6: เงินได้วิชาชีพอิสระ 40(6)
            - income_40_7: เงินได้จากการรับเหมา 40(7)
            - income_40_8: เงินได้อื่นๆ 40(8)
    
    Returns:
        total_income: เงินได้รวม
        total_expenses: ค่าใช้จ่ายรวม
        income_after_expenses: เงินได้หลังหักค่าใช้จ่าย
        income_details: รายละเอียดเงินได้แต่ละประเภท
    """
    income_details = {}
    total_income = 0
    total_expenses = 0
    
    # 40(1)(2) เงินเดือน/โบนัส
    income_40_1_2 = income_data.get('income_40_1_2', 0)
    if income_40_1_2 > 0:
        expense_40_1_2 = income_data.get('expense_40_1_2', EXPENSE_RATES['40_1_2'])
        expense_40_1_2 = min(expense_40_1_2, EXPENSE_RATES['40_1_2'])  # ไม่เกิน 100,000
        income_details['40_1_2'] = {
            'income': income_40_1_2,
            'expense': expense_40_1_2,
            'net': income_40_1_2 - expense_40_1_2
        }
        total_income += income_40_1_2
        total_expenses += expense_40_1_2
    
    # 40(4) ดอกเบี้ย/เงินปันผล
    income_40_4 = income_data.get('income_40_4', 0)
    if income_40_4 > 0:
        expense_40_4 = income_40_4 * EXPENSE_RATES['40_4']
        income_details['40_4'] = {
            'income': income_40_4,
            'expense': expense_40_4,
            'net': income_40_4 - expense_40_4
        }
        total_income += income_40_4
        total_expenses += expense_40_4
    
    # 40(5) ค่าเช่าทรัพย์สิน
    income_40_5 = income_data.get('income_40_5', 0)
    if income_40_5 > 0:
        expense_40_5 = income_40_5 * EXPENSE_RATES['40_5']
        income_details['40_5'] = {
            'income': income_40_5,
            'expense': expense_40_5,
            'net': income_40_5 - expense_40_5
        }
        total_income += income_40_5
        total_expenses += expense_40_5
    
    # 40(6) เงินได้วิชาชีพอิสระ
    income_40_6 = income_data.get('income_40_6', 0)
    if income_40_6 > 0:
        expense_40_6 = income_40_6 * EXPENSE_RATES['40_6']
        income_details['40_6'] = {
            'income': income_40_6,
            'expense': expense_40_6,
            'net': income_40_6 - expense_40_6
        }
        total_income += income_40_6
        total_expenses += expense_40_6
    
    # 40(7) เงินได้จากการรับเหมา
    income_40_7 = income_data.get('income_40_7', 0)
    if income_40_7 > 0:
        expense_40_7 = income_40_7 * EXPENSE_RATES['40_7']
        income_details['40_7'] = {
            'income': income_40_7,
            'expense': expense_40_7,
            'net': income_40_7 - expense_40_7
        }
        total_income += income_40_7
        total_expenses += expense_40_7
    
    # 40(8) เงินได้อื่นๆ
    income_40_8 = income_data.get('income_40_8', 0)
    if income_40_8 > 0:
        expense_40_8 = income_40_8 * EXPENSE_RATES['40_8']
        income_details['40_8'] = {
            'income': income_40_8,
            'expense': expense_40_8,
            'net': income_40_8 - expense_40_8
        }
        total_income += income_40_8
        total_expenses += expense_40_8
    
    income_after_expenses = max(0, total_income - total_expenses)
    
    return total_income, total_expenses, income_after_expenses, income_details


def calculate_deductions(income, deductions_data):
    """
    คำนวณค่าลดหย่อนทั้งหมด
    
    Args:
        income: รายได้รวม
        deductions_data: dictionary ประกอบด้วย:
            - personal: ค่าลดหย่อนส่วนตัว (default: 60000)
            - spouse: มีคู่สมรส (boolean)
            - children: จำนวนบุตร
            - children_2nd: จำนวนบุตรคนที่ 2 เกิดหลังปี 2561
            - parents: จำนวนบิดามารดา
            - life_insurance: เบี้ยประกันชีวิต
            - health_insurance_self: เบี้ยประกันสุขภาพตนเอง
            - health_insurance_parent: เบี้ยประกันสุขภาพบิดามารดา
            - rmf_ssf: กองทุน RMF/SSF
            - thai_esg: กองทุน Thai ESG
            - pvd: กองทุนสำรองเลี้ยงชีพ
            - easy_e_receipt: Easy E-Receipt
            - home_interest: ดอกเบี้ยที่อยู่อาศัย
            - donation: เงินบริจาคทั่วไป
            - education_donation: เงินบริจาคเพื่อการศึกษา
    
    Returns:
        total_deductions: ค่าลดหย่อนรวม
        deduction_details: รายละเอียดค่าลดหย่อนแต่ละประเภท
    """
    deduction_details = {}
    
    # ค่าลดหย่อนส่วนตัว
    personal = deductions_data.get('personal', PERSONAL_DEDUCTION)
    deduction_details['personal'] = personal
    
    # ค่าลดหย่อนคู่สมรส
    spouse_deduction = SPOUSE_DEDUCTION if deductions_data.get('spouse', False) else 0
    deduction_details['spouse'] = spouse_deduction
    
    # ค่าลดหย่อนบุตร
    children = deductions_data.get('children', 0)
    children_2nd = deductions_data.get('children_2nd', 0)
    child_deduction = (children - children_2nd) * CHILD_DEDUCTION + children_2nd * CHILD_DEDUCTION_2ND
    deduction_details['children'] = child_deduction
    
    # ค่าลดหย่อนบิดามารดา
    parents = deductions_data.get('parents', 0)
    parent_deduction = parents * PARENT_DEDUCTION
    deduction_details['parents'] = parent_deduction
    
    # เบี้ยประกันชีวิต
    life_insurance = min(deductions_data.get('life_insurance', 0), MAX_LIFE_INSURANCE)
    deduction_details['life_insurance'] = life_insurance
    
    # เบี้ยประกันสุขภาพตนเอง
    health_insurance_self = min(deductions_data.get('health_insurance_self', 0), MAX_HEALTH_INSURANCE_SELF)
    deduction_details['health_insurance_self'] = health_insurance_self
    
    # เบี้ยประกันสุขภาพบิดามารดา
    health_insurance_parent = min(deductions_data.get('health_insurance_parent', 0), MAX_HEALTH_INSURANCE_PARENT)
    deduction_details['health_insurance_parent'] = health_insurance_parent
    
    # กองทุน RMF (30% ของเงินได้ สูงสุด 500,000)
    rmf_amount = deductions_data.get('rmf', 0)
    rmf_limit_by_percent = income * MAX_RMF_PERCENT
    rmf = min(rmf_amount, rmf_limit_by_percent, MAX_RMF_AMOUNT)
    deduction_details['rmf'] = rmf
    
    # กองทุน SSF (30% ของเงินได้ สูงสุด 200,000)
    ssf_amount = deductions_data.get('ssf', 0)
    ssf_limit_by_percent = income * MAX_SSF_PERCENT
    ssf = min(ssf_amount, ssf_limit_by_percent, MAX_SSF_AMOUNT)
    deduction_details['ssf'] = ssf
    
    # กองทุนสำรองเลี้ยงชีพ (PVD) (15% ของเงินได้ สูงสุด 500,000)
    pvd_amount = deductions_data.get('pvd', 0)
    pvd_limit_by_percent = income * MAX_PVD_PERCENT
    pvd = min(pvd_amount, pvd_limit_by_percent, MAX_PVD_AMOUNT)
    deduction_details['pvd'] = pvd
    
    # รวม RMF + SSF + PVD ไม่เกิน 500,000
    rmf_ssf_pvd_total = rmf + ssf + pvd
    if rmf_ssf_pvd_total > MAX_RMF_SSF_PVD_COMBINED:
        # ปรับสัดส่วน
        ratio = MAX_RMF_SSF_PVD_COMBINED / rmf_ssf_pvd_total
        rmf = rmf * ratio
        ssf = ssf * ratio
        pvd = pvd * ratio
        deduction_details['rmf'] = rmf
        deduction_details['ssf'] = ssf
        deduction_details['pvd'] = pvd
    
    # กองทุน Thai ESG (30% ของเงินได้ สูงสุด 300,000)
    thai_esg_amount = deductions_data.get('thai_esg', 0)
    thai_esg_limit_by_percent = income * MAX_THAI_ESG_PERCENT
    thai_esg = min(thai_esg_amount, thai_esg_limit_by_percent, MAX_THAI_ESG_AMOUNT)
    deduction_details['thai_esg'] = thai_esg
    
    # กองทุนการออมแห่งชาติ (กอช.)
    nssf = min(deductions_data.get('nssf', 0), MAX_NSSF)
    deduction_details['nssf'] = nssf
    
    # เงินสมทบกองทุนประกันสังคม
    social_security = min(deductions_data.get('social_security', 0), MAX_SOCIAL_SECURITY)
    deduction_details['social_security'] = social_security
    
    # Easy E-Receipt 2568
    easy_e_receipt = EASY_E_RECEIPT if deductions_data.get('easy_e_receipt', False) else 0
    deduction_details['easy_e_receipt'] = easy_e_receipt
    
    # ค่าติดตั้งโซลาร์เซลล์
    solar_cell = min(deductions_data.get('solar_cell', 0), MAX_SOLAR_CELL)
    deduction_details['solar_cell'] = solar_cell
    
    # ค่าก่อสร้างบ้านใหม่
    home_construction = min(deductions_data.get('home_construction', 0), MAX_HOME_CONSTRUCTION)
    deduction_details['home_construction'] = home_construction
    
    # ดอกเบี้ยที่อยู่อาศัย
    home_interest = min(deductions_data.get('home_interest', 0), MAX_HOME_INTEREST)
    deduction_details['home_interest'] = home_interest
    
    # คำนวณค่าลดหย่อนพื้นฐานก่อน (ไม่รวมเงินบริจาค)
    basic_deductions = sum([
        personal, spouse_deduction, child_deduction, parent_deduction,
        life_insurance, health_insurance_self, health_insurance_parent,
        rmf, ssf, pvd, thai_esg, nssf, social_security, 
        easy_e_receipt, solar_cell, home_construction, home_interest
    ])
    
    # เงินได้หลังหักค่าลดหย่อนพื้นฐาน
    income_after_basic = max(0, income - basic_deductions)
    
    # เงินบริจาคทั่วไป (ไม่เกิน 10% ของเงินได้หลังหักค่าลดหย่อน)
    donation = deductions_data.get('donation', 0)
    max_donation = income_after_basic * MAX_DONATION_PERCENT
    donation = min(donation, max_donation)
    deduction_details['donation'] = donation
    
    # เงินบริจาคเพื่อการศึกษา (2 เท่า แต่ไม่เกิน 10% ของเงินได้หลังหักค่าลดหย่อน)
    education_donation = deductions_data.get('education_donation', 0)
    education_donation_deduction = education_donation * EDUCATION_DONATION_MULTIPLIER
    max_education_donation = income_after_basic * MAX_DONATION_PERCENT
    education_donation_deduction = min(education_donation_deduction, max_education_donation)
    deduction_details['education_donation'] = education_donation_deduction
    
    # เงินบริจาคพรรคการเมือง
    political_donation = min(deductions_data.get('political_donation', 0), MAX_POLITICAL_DONATION)
    deduction_details['political_donation'] = political_donation
    
    # เงินลงทุนในธุรกิจวิสาหกิจเพื่อสังคม
    social_enterprise = min(deductions_data.get('social_enterprise', 0), MAX_SOCIAL_ENTERPRISE)
    deduction_details['social_enterprise'] = social_enterprise
    
    # ค่าลดหย่อนรวม
    total_deductions = basic_deductions + donation + education_donation_deduction + political_donation + social_enterprise
    
    return total_deductions, deduction_details


def calculate_net_income(income_after_expenses, deductions_data):
    """
    คำนวณรายได้สุทธิ
    
    Args:
        income_after_expenses: เงินได้หลังหักค่าใช้จ่าย
        deductions_data: ข้อมูลค่าลดหย่อน
    
    Returns:
        net_income: รายได้สุทธิ
        total_deductions: ค่าลดหย่อนรวม
        deduction_details: รายละเอียดค่าลดหย่อน
    """
    total_deductions, deduction_details = calculate_deductions(income_after_expenses, deductions_data)
    net_income = max(0, income_after_expenses - total_deductions)
    return net_income, total_deductions, deduction_details


def calculate_tax(net_income):
    """
    คำนวณภาษีตามขั้นบันได (Progressive Tax)
    
    วิธีคำนวณ:
    - แต่ละขั้นจะคำนวณเฉพาะส่วนที่อยู่ในช่วงนั้น
    - ตัวอย่าง: รายได้สุทธิ 275,852.19 บาท
      - 0-150,000: ยกเว้น (ไม่ต้องคำนวณ)
      - 150,001-300,000: (275,852.19 - 150,000) = 125,852.19 × 5% = 6,292.61
    
    Args:
        net_income: รายได้สุทธิ
    
    Returns:
        tax: ภาษีที่ต้องจ่าย
        tax_details: รายละเอียดการคำนวณภาษีแต่ละขั้น
    """
    if net_income <= 0:
        return 0, []
    
    tax = 0
    tax_details = []
    
    for min_income, max_income, rate in TAX_BRACKETS:
        # ข้ามขั้นที่รายได้ไม่ถึง
        if net_income <= min_income:
            continue
        
        # คำนวณจำนวนเงินที่ต้องเสียภาษีในขั้นนี้
        # ใช้ min เพื่อหาว่ารายได้อยู่ในขั้นไหน
        if max_income == float('inf'):
            # ขั้นสุดท้าย
            taxable_amount = net_income - (min_income - 1)  # ลบ 1 เพราะ min_income คือจุดเริ่มต้นของขั้น
        else:
            # ขั้นอื่นๆ
            bracket_max = min(net_income, max_income)
            # taxable_amount = bracket_max - (min_income - 1) เพราะ min_income คือจุดเริ่มต้นของขั้น
            # ตัวอย่าง: 150,001-300,000 หมายความว่า 150,001 เป็นจุดเริ่มต้น
            # แต่ในการคำนวณ ต้องหัก 150,000 (ไม่ใช่ 150,001)
            taxable_amount = bracket_max - (min_income - 1)
        
        # ตรวจสอบว่ามีเงินที่ต้องเสียภาษีในขั้นนี้หรือไม่
        if taxable_amount > 0 and rate > 0:  # แสดงเฉพาะขั้นที่มีอัตราภาษี > 0
            bracket_tax = taxable_amount * rate
            tax += bracket_tax
            
            tax_details.append({
                'range': f'{min_income:,.0f} - {max_income if max_income != float("inf") else "∞":,}',
                'taxable_amount': taxable_amount,
                'rate': rate * 100,
                'tax': bracket_tax
            })
            
            # ถ้ารายได้อยู่ในขั้นนี้แล้ว ให้หยุด
            if net_income <= max_income:
                break
    
    return tax, tax_details


def calculate_tax_complete(income_data, deductions_data, withholding_tax=0):
    """
    คำนวณภาษีแบบครบถ้วน
    
    Args:
        income_data: ข้อมูลเงินได้ตามมาตรา 40
        deductions_data: ข้อมูลค่าลดหย่อน
        withholding_tax: ภาษีหัก ณ ที่จ่าย
    
    Returns:
        dict: ข้อมูลการคำนวณภาษีทั้งหมด
    """
    # คำนวณเงินได้และค่าใช้จ่าย
    total_income, total_expenses, income_after_expenses, income_details = calculate_income_expenses(income_data)
    
    # คำนวณค่าลดหย่อนและรายได้สุทธิ
    net_income, total_deductions, deduction_details = calculate_net_income(income_after_expenses, deductions_data)
    
    # คำนวณภาษี
    tax, tax_details = calculate_tax(net_income)
    
    # คำนวณเงินบริจาค
    donation = deduction_details.get('donation', 0)
    education_donation = deduction_details.get('education_donation', 0)
    total_donation = donation + education_donation
    
    # เงินได้สุทธิหลังหักเงินบริจาค
    net_income_after_donation = net_income - total_donation
    
    # คำนวณภาษีใหม่หลังหักเงินบริจาค
    tax_after_donation, _ = calculate_tax(net_income_after_donation)
    
    # เงินคืน/เงินเพิ่ม
    tax_refund = max(0, withholding_tax - tax_after_donation)
    tax_additional = max(0, tax_after_donation - withholding_tax)
    
    # คำนวณเปอร์เซ็นต์
    tax_percent_of_income = (tax_after_donation / total_income * 100) if total_income > 0 else 0
    tax_percent_of_net = (tax_after_donation / net_income_after_donation * 100) if net_income_after_donation > 0 else 0
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'income_after_expenses': income_after_expenses,
        'income_details': income_details,
        'total_deductions': total_deductions,
        'deduction_details': deduction_details,
        'donation': donation,
        'education_donation': education_donation,
        'total_donation': total_donation,
        'net_income': net_income_after_donation,
        'tax': tax_after_donation,
        'tax_details': tax_details,
        'withholding_tax': withholding_tax,
        'tax_refund': tax_refund,
        'tax_additional': tax_additional,
        'tax_percent_of_income': tax_percent_of_income,
        'tax_percent_of_net': tax_percent_of_net,
        'net_income_after_tax': net_income_after_donation - tax_after_donation
    }

