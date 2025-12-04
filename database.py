"""
โมดูลจัดการฐานข้อมูล SQLite สำหรับบันทึกผลการคำนวณภาษี
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


DB_NAME = 'tax.db'


def get_connection():
    """สร้าง connection กับฐานข้อมูล"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """สร้างตารางฐานข้อมูลถ้ายังไม่มี"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            income REAL NOT NULL,
            total_deductions REAL NOT NULL,
            net_income REAL NOT NULL,
            tax REAL NOT NULL,
            deduction_details TEXT,
            tax_details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ตารางสำหรับเก็บข้อมูลผู้ใช้
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            income_data TEXT NOT NULL,
            deductions_data TEXT NOT NULL,
            withholding_tax REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[DEBUG] Database initialized: {DB_NAME}")


def save_calculation(name: str, calculation_result: Dict) -> int:
    """
    บันทึกผลการคำนวณภาษี
    
    Args:
        name: ชื่อผู้ใช้
        calculation_result: ผลการคำนวณจาก calculate_tax_complete()
    
    Returns:
        calculation_id: ID ของการคำนวณที่บันทึก
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # แปลง dictionary เป็น JSON string
    deduction_details_json = json.dumps(calculation_result.get('deduction_details', {}), ensure_ascii=False)
    tax_details_json = json.dumps([
        {
            'range': detail['range'],
            'taxable_amount': detail['taxable_amount'],
            'rate': detail['rate'],
            'tax': detail['tax']
        }
        for detail in calculation_result.get('tax_details', [])
    ], ensure_ascii=False)
    
    cursor.execute('''
        INSERT INTO calculations 
        (name, income, total_deductions, net_income, tax, deduction_details, tax_details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        calculation_result['income'],
        calculation_result['total_deductions'],
        calculation_result['net_income'],
        calculation_result['tax'],
        deduction_details_json,
        tax_details_json
    ))
    
    calculation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"[DEBUG] Calculation saved: ID={calculation_id}, Name={name}, Tax={calculation_result['tax']:,.2f}")
    return calculation_id


def get_calculations(limit: Optional[int] = None) -> List[Dict]:
    """
    ดึงประวัติการคำนวณทั้งหมด
    
    Args:
        limit: จำนวนรายการที่ต้องการดึง (None = ทั้งหมด)
    
    Returns:
        List of calculation records
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM calculations ORDER BY created_at DESC'
    if limit:
        query += f' LIMIT {limit}'
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    calculations = []
    for row in rows:
        calculation = {
            'id': row['id'],
            'name': row['name'],
            'income': row['income'],
            'total_deductions': row['total_deductions'],
            'net_income': row['net_income'],
            'tax': row['tax'],
            'deduction_details': json.loads(row['deduction_details']) if row['deduction_details'] else {},
            'tax_details': json.loads(row['tax_details']) if row['tax_details'] else [],
            'created_at': row['created_at']
        }
        calculations.append(calculation)
    
    conn.close()
    print(f"[DEBUG] Retrieved {len(calculations)} calculations")
    return calculations


def get_calculation_by_id(calculation_id: int) -> Optional[Dict]:
    """
    ดึงข้อมูลการคำนวณตาม ID
    
    Args:
        calculation_id: ID ของการคำนวณ
    
    Returns:
        Calculation record or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM calculations WHERE id = ?', (calculation_id,))
    row = cursor.fetchone()
    
    if row:
        calculation = {
            'id': row['id'],
            'name': row['name'],
            'income': row['income'],
            'total_deductions': row['total_deductions'],
            'net_income': row['net_income'],
            'tax': row['tax'],
            'deduction_details': json.loads(row['deduction_details']) if row['deduction_details'] else {},
            'tax_details': json.loads(row['tax_details']) if row['tax_details'] else [],
            'created_at': row['created_at']
        }
        conn.close()
        return calculation
    
    conn.close()
    return None


def delete_calculation(calculation_id: int) -> bool:
    """
    ลบข้อมูลการคำนวณ
    
    Args:
        calculation_id: ID ของการคำนวณที่ต้องการลบ
    
    Returns:
        True if deleted, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM calculations WHERE id = ?', (calculation_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    if deleted:
        print(f"[DEBUG] Calculation deleted: ID={calculation_id}")
    else:
        print(f"[DEBUG] Calculation not found: ID={calculation_id}")
    
    return deleted


def get_statistics() -> Dict:
    """
    ดึงสถิติการคำนวณ
    
    Returns:
        Dictionary with statistics
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM calculations')
    total = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(tax) as total_tax FROM calculations')
    total_tax = cursor.fetchone()['total_tax'] or 0
    
    cursor.execute('SELECT AVG(tax) as avg_tax FROM calculations')
    avg_tax = cursor.fetchone()['avg_tax'] or 0
    
    cursor.execute('SELECT AVG(income) as avg_income FROM calculations')
    avg_income = cursor.fetchone()['avg_income'] or 0
    
    conn.close()
    
    return {
        'total_calculations': total,
        'total_tax': total_tax,
        'avg_tax': avg_tax,
        'avg_income': avg_income
    }


# ฟังก์ชันจัดการข้อมูลผู้ใช้
def save_user_profile(name: str, income_data: Dict, deductions_data: Dict, withholding_tax: float = 0) -> int:
    """
    บันทึกหรืออัปเดตข้อมูลผู้ใช้
    
    Args:
        name: ชื่อผู้ใช้
        income_data: ข้อมูลเงินได้
        deductions_data: ข้อมูลค่าลดหย่อน
        withholding_tax: ภาษีหัก ณ ที่จ่าย
    
    Returns:
        user_id: ID ของผู้ใช้
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    income_data_json = json.dumps(income_data, ensure_ascii=False)
    deductions_data_json = json.dumps(deductions_data, ensure_ascii=False)
    
    # Debug: แสดงข้อมูลที่บันทึก
    print(f"[DEBUG] Saving user profile: Name={name}")
    print(f"[DEBUG] Income data keys: {list(income_data.keys())}")
    print(f"[DEBUG] Deductions data keys: {list(deductions_data.keys())}")
    print(f"[DEBUG] Withholding tax: {withholding_tax}")
    
    # ตรวจสอบว่ามีผู้ใช้อยู่แล้วหรือไม่
    cursor.execute('SELECT id FROM user_profiles WHERE name = ?', (name,))
    existing = cursor.fetchone()
    
    if existing:
        # อัปเดตข้อมูล
        cursor.execute('''
            UPDATE user_profiles 
            SET income_data = ?, deductions_data = ?, withholding_tax = ?, updated_at = CURRENT_TIMESTAMP
            WHERE name = ?
        ''', (income_data_json, deductions_data_json, withholding_tax, name))
        user_id = existing['id']
        print(f"[DEBUG] User profile updated: ID={user_id}, Name={name}")
    else:
        # สร้างใหม่
        cursor.execute('''
            INSERT INTO user_profiles (name, income_data, deductions_data, withholding_tax)
            VALUES (?, ?, ?, ?)
        ''', (name, income_data_json, deductions_data_json, withholding_tax))
        user_id = cursor.lastrowid
        print(f"[DEBUG] User profile saved: ID={user_id}, Name={name}")
    
    conn.commit()
    conn.close()
    return user_id


def get_user_profiles() -> List[Dict]:
    """
    ดึงรายชื่อผู้ใช้ทั้งหมด
    
    Returns:
        List of user profiles
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, updated_at, created_at FROM user_profiles ORDER BY name')
    rows = cursor.fetchall()
    
    profiles = []
    for row in rows:
        profiles.append({
            'id': row['id'],
            'name': row['name'],
            'updated_at': row['updated_at'],
            'created_at': row['created_at']
        })
    
    conn.close()
    return profiles


def get_user_profile_by_name(name: str) -> Optional[Dict]:
    """
    ดึงข้อมูลผู้ใช้ตามชื่อ
    
    Args:
        name: ชื่อผู้ใช้
    
    Returns:
        User profile or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user_profiles WHERE name = ?', (name,))
    row = cursor.fetchone()
    
    if row:
        income_data = json.loads(row['income_data']) if row['income_data'] else {}
        deductions_data = json.loads(row['deductions_data']) if row['deductions_data'] else {}
        
        # Debug: แสดงข้อมูลที่โหลด
        print(f"[DEBUG] Loading user profile: Name={name}")
        print(f"[DEBUG] Income data keys: {list(income_data.keys())}")
        print(f"[DEBUG] Deductions data keys: {list(deductions_data.keys())}")
        print(f"[DEBUG] Withholding tax: {row['withholding_tax']}")
        
        profile = {
            'id': row['id'],
            'name': row['name'],
            'income_data': income_data,
            'deductions_data': deductions_data,
            'withholding_tax': row['withholding_tax'],
            'updated_at': row['updated_at'],
            'created_at': row['created_at']
        }
        conn.close()
        return profile
    
    conn.close()
    return None


def delete_user_profile(name: str) -> bool:
    """
    ลบข้อมูลผู้ใช้
    
    Args:
        name: ชื่อผู้ใช้ที่ต้องการลบ
    
    Returns:
        True if deleted, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM user_profiles WHERE name = ?', (name,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    if deleted:
        print(f"[DEBUG] User profile deleted: Name={name}")
    else:
        print(f"[DEBUG] User profile not found: Name={name}")
    
    return deleted

