import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from io import StringIO

# إعدادات الصفحة والشكل العام للنظام المحاسبي المتطور (Oracle Style)
st.set_page_config(page_title="نظام البربوه المحاسبي - Oracle ERP Edition", layout="wide")

# أسماء ملفات البيانات (الدفاتر والحسابات القائمة على القيد المزدوج)
INVENTORY_FILE = "inventory_data.csv"
USERS_FILE = "users_data.csv"
SALES_FILE = "sales_data.csv"
PURCHASES_FILE = "purchases_data.csv"
EXPENSES_FILE = "expenses_data.csv"
ATTENDANCE_FILE = "attendance_data.csv"
CONTACTS_FILE = "contacts_data.csv"
PERMISSIONS_FILE = "permissions_config.csv"
SETTINGS_FILE = "system_settings.csv"
RETURNS_FILE = "returns_data.csv"  
COLLECTIONS_FILE = "collections_data.csv"

# ملفات المحاسبة المتقدمة ونظام Oracle ERP
COA_FILE = "chart_of_accounts.csv"      # شجرة الحسابات (Chart of Accounts)
GL_JOURNAL_FILE = "gl_journals.csv"     # دفتر القيود اليومية General Ledger Entries

# دالة إيجاد كود الحساب من شجرة الحسابات
def get_account_code(account_name):
    if os.path.exists(COA_FILE):
        coa_df = pd.read_csv(COA_FILE)
        match = coa_df[coa_df['اسم الحساب'] == account_name]
        if not match.empty:
            return match.iloc[0]['رقم الحساب']
    return "0000"

# دالة إنشاء قيد محاسبي آلي بقواعد القيد المزدوج (Double-Entry Engine)
def post_gl_journal_entry(batch_id, ref_no, description, debit_acc, credit_acc, amount, user):
    if amount <= 0:
        return
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    debit_code = get_account_code(debit_acc)
    credit_code = get_account_code(credit_acc)
    
    # الطرف المدين (Debit)
    entry_debit = {
        "رقم الحركة": batch_id,
        "التاريخ": current_time,
        "رقم المرجع": ref_no,
        "البيان والتفاصيل": description,
        "رقم الحساب": debit_code,
        "اسم الحساب": debit_acc,
        "مدين (Debit)": amount,
        "دائن (Credit)": 0.0,
        "المسؤول": user
    }
    
    # الطرف الدائن (Credit)
    entry_credit = {
        "رقم الحركة": batch_id,
        "التاريخ": current_time,
        "رقم المرجع": ref_no,
        "البيان والتفاصيل": description,
        "رقم الحساب": credit_code,
        "اسم الحساب": credit_acc,
        "مدين (Debit)": 0.0,
        "دائن (Credit)": amount,
        "المسؤول": user
    }
    
    gl_df = pd.read_csv(GL_JOURNAL_FILE) if os.path.exists(GL_JOURNAL_FILE) else pd.DataFrame()
    new_entries = pd.DataFrame([entry_debit, entry_credit])
    gl_df = pd.concat([gl_df, new_entries], ignore_index=True)
    gl_df.to_csv(GL_JOURNAL_FILE, index=False, encoding='utf-8-sig')

# دالة توليد رقم فاتورة تسلسلي
def generate_sequential_invoice_id(sales_df):
    if sales_df.empty or "رقم الفاتورة" not in sales_df.columns:
        return "INV-0001"
    inv_numbers = []
    for inv_id in sales_df["رقم الفاتورة"].dropna().unique():
        inv_str = str(inv_id)
        if "INV-" in inv_str:
            num_part = inv_str.replace("INV-", "")
            if num_part.isdigit():
                inv_numbers.append(int(num_part))
    if not inv_numbers:
        return "INV-0001"
    return f"INV-{(max(inv_numbers) + 1):04d}"

# التفقيط العربي
def number_to_arabic_words(number):
    try:
        num = int(float(number))
        if num == 0: return "صفر جنيهاً مصرياً لا غير"
        units = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"]
        tens = ["", "عشرة", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
        hundreds = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعون", "ثمانمائة", "تسعمائة"]
        words = []
        if num >= 1000:
            thousands = num // 1000
            if thousands == 1: words.append("ألف")
            elif thousands == 2: words.append("ألفين")
            elif 3 <= thousands <= 10: words.append(f"{units[thousands]} آلاف")
            else: words.append(f"{thousands} ألف")
            num %= 1000
        if num >= 100:
            words.append(hundreds[num // 100])
            num %= 100
        if num > 0:
            if len(words) > 0: words.append("و")
            if num < 10: words.append(units[num])
            elif num < 20:
                special = ["عشرة", "أحد عشر", "إثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
                words.append(special[num - 10])
            else:
                unit_part = num % 10
                tens_part = num // 10
                if unit_part > 0: words.append(f"{units[unit_part]} و{tens[tens_part]}")
                else: words.append(tens[tens_part])
        return "فقط " + " و ".join([w for w in words if w != "و"]) + " جنيهاً مصرياً لا غير"
    except:
        return ""

# تهيئة الملفات وبناء شجرة حسابات Oracle الأساسية
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([
            {"username": "admin", "password": "123", "role": "مدير"},
            {"username": "sharaf", "password": "456", "role": "مشرف"},
            {"username": "user1", "password": "111", "role": "موظف"}
        ]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')

    # إنشاء شجرة الحسابات المحاسبية Standard Chart of Accounts (Oracle-based)
    if not os.path.exists(COA_FILE):
        default_coa = [
            {"رقم الحساب": "1101", "اسم الحساب": "النقدية بالخزينة Main Cash", "نوع الحساب": "أصول متداولة", "النوع الرئيسي": "أصول"},
            {"رقم الحساب": "1102", "اسم الحساب": "العملاء والذمم المدينة Accounts Receivable", "نوع الحساب": "أصول متداولة", "النوع الرئيسي": "أصول"},
            {"رقم الحساب": "1103", "اسم الحساب": "مخزون البضائع Inventory", "نوع الحساب": "أصول متداولة", "النوع الرئيسي": "أصول"},
            {"رقم الحساب": "2101", "اسم الحساب": "الموردين والذمم الدائنة Accounts Payable", "نوع الحساب": "التزامات متداولة", "النوع الرئيسي": "التزامات"},
            {"رقم الحساب": "3101", "اسم الحساب": "رأس المال Owner's Equity", "نوع الحساب": "حقوق ملكية", "النوع الرئيسي": "حقوق ملكية"},
            {"رقم الحساب": "4101", "اسم الحساب": "إيرادات المبيعات Sales Revenue", "نوع الحساب": "إيرادات", "النوع الرئيسي": "إيرادات"},
            {"رقم الحساب": "5101", "اسم الحساب": "تكلفة البضاعة المباعة Cost of Goods Sold", "نوع الحساب": "مصروفات تشغيلية", "النوع الرئيسي": "مصروفات"},
            {"رقم الحساب": "5201", "اسم الحساب": "المصاريف العمومية والإدارية General Expenses", "نوع الحساب": "مصروفات إدارية", "النوع الرئيسي": "مصروفات"},
            {"رقم الحساب": "4201", "اسم الحساب": "مردودات ومسموحات المبيعات Sales Returns", "نوع الحساب": "إيرادات عكسية", "النوع الرئيسي": "إيرادات"}
        ]
        pd.DataFrame(default_coa).to_csv(COA_FILE, index=False, encoding='utf-8-sig')

    if not os.path.exists(GL_JOURNAL_FILE):
        pd.DataFrame(columns=["رقم الحركة", "التاريخ", "رقم المرجع", "البيان والتفاصيل", "رقم الحساب", "اسم الحساب", "مدين (Debit)", "دائن (Credit)", "المسؤول"]).to_csv(GL_JOURNAL_FILE, index=False, encoding='utf-8-sig')

    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "تصنيف الصنف", "نوع الوحدة", "موقع المخزن", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "هاتف العميل", "العنوان", "نوع البيع", "نظام التحصيل", "تاريخ التحصيل", "المدفوع مقدم", "المتبقي", "كود الصنف", "الصنف", "تصنيف الصنف", "نوع الوحدة", "موقع المخزن", "الكمية", "سعر الوحدة", "الخصم %", "خصم نقدي ثابت", "إجمالي البيع", "تكلفة الشراء الإجمالية", "صافي ربح الفاتورة", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(RETURNS_FILE):
        pd.DataFrame(columns=["رقم الإرجاع", "رقم الفاتورة الأصلية", "التاريخ", "اسم العميل", "كود الصنف", "الصنف", "الكمية المرجعة", "المبلغ المردود", "المسؤول"]).to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')

    if not os.path.exists(PURCHASES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "المورد", "كود الصنف", "الصنف", "تصنيف الصنف", "نوع الوحدة", "موقع المخزن", "سعر الشراء المعتمد", "الكمية", "إجمالي الشراء", "المسؤول"]).to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(EXPENSES_FILE):
        pd.DataFrame(columns=["التاريخ", "البيان", "المبلغ", "المسؤول"]).to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(ATTENDANCE_FILE):
        pd.DataFrame(columns=["الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف"]).to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(CONTACTS_FILE):
        pd.DataFrame(columns=["النوع", "الاسم", "الهاتف", "العنوان"]).to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')
     
    if not os.path.exists(COLLECTIONS_FILE):
        pd.DataFrame(columns=["رقم السند", "التاريخ", "اسم العميل", "المبلغ المحصل", "طريقة السداد", "ملاحظات", "المسؤول"]).to_csv(COLLECTIONS_FILE, index=False, encoding='utf-8-sig')

    if not os.path.exists(SETTINGS_FILE):
        pd.DataFrame([{"اسم المعرض": "شركة البربوه المحاسبية", "العنوان": "المركز الرئيسي - أوراكل ERP", "رقم الدعم": "0100XXXXXXX"}]).to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')

    all_pages = [
        "🏛️ الدفتر العام وشجرة الحسابات (Oracle COA)", "📦 إدارة الأصناف والمخزن", "📊 رصيد أول المدة Excel", "🔍 حالة المخزن", 
        "🤝 العملاء والموردين", "📥 حركة فواتير الشراء والتعديل", "📤 حركة فواتير البيع", 
        "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "📈 ميزان المراجع والتقارير المالية (Oracle Reports)", "💸 المصاريف", 
        "⏰ الحضور والانصراف", "⚙️ إدارة وتعديل الصلاحيات والحسابات", "⚙️ إعدادات بيانات الفاتورة والدعم"
    ]
    
    if not os.path.exists(PERMISSIONS_FILE):
        default_perms = []
        for page in all_pages:
            default_perms.append({
                "اسم الصفحة": page, 
                "مدير": True, 
                "مشرف": True if page in ["🏛️ الدفتر العام وشجرة الحسابات (Oracle COA)", "🔍 حالة المخزن", "📥 حركة فواتير الشراء والتعديل", "📤 حركة فواتير البيع", "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "📈 ميزان المراجع والتقارير المالية (Oracle Reports)", "⏰ الحضور والانصراف"] else False, 
                "موظف": True if page in ["🔍 حالة المخزن", "📤 حركة فواتير البيع", "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"] else False
            })
        pd.DataFrame(default_perms).to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')

init_files()

def load_data_into_session():
    if 'data_loaded' not in st.session_state or st.sidebar.button("🔄 تحديث شامل للبيانات", key="global_refresh"):
        st.session_state.inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
        for col in ["تصنيف الصنف", "نوع الوحدة", "موقع المخزن"]:
            if col not in st.session_state.inv_df.columns:
                st.session_state.inv_df[col] = "غير محدد"
                
        st.session_state.inv_df["الكمية"] = pd.to_numeric(st.session_state.inv_df["الكمية"], errors='coerce').fillna(0).astype(int)
        st.session_state.inv_df["سعر الشراء"] = pd.to_numeric(st.session_state.inv_df["سعر الشراء"], errors='coerce').fillna(0.0)
        st.session_state.inv_df["سعر البيع"] = pd.to_numeric(st.session_state.inv_df["سعر البيع"], errors='coerce').fillna(0.0)

        st.session_state.sales_df = pd.read_csv(SALES_FILE, dtype={"رقم الفاتورة": str, "كود الصنف": str})
        st.session_state.returns_df = pd.read_csv(RETURNS_FILE, dtype={"رقم الإرجاع": str, "رقم الفاتورة الأصلية": str, "كود الصنف": str})
        st.session_state.purchases_df = pd.read_csv(PURCHASES_FILE, dtype={"رقم الفاتورة": str, "كود الصنف": str})
        st.session_state.exp_df = pd.read_csv(EXPENSES_FILE)
        st.session_state.att_df = pd.read_csv(ATTENDANCE_FILE)
        st.session_state.contacts_df = pd.read_csv(CONTACTS_FILE, dtype=str)
        st.session_state.collections_df = pd.read_csv(COLLECTIONS_FILE)
        st.session_state.coa_df = pd.read_csv(COA_FILE)
        st.session_state.gl_df = pd.read_csv(GL_JOURNAL_FILE)
        st.session_state.data_loaded = True

load_data_into_session()

settings_df = pd.read_csv(SETTINGS_FILE)
SHOWROOM_NAME = settings_df.iloc[0]["اسم المعرض"]
SHOWROOM_ADDRESS = settings_df.iloc[0]["العنوان"]
INQUIRY_NUMBER = settings_df.iloc[0]["رقم الدعم"]

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "موظف"
if 'cart' not in st.session_state: st.session_state.cart = []
if 'edit_invoice_cart' not in st.session_state: st.session_state.edit_invoice_cart = []

if 'form_sale_cust_type' not in st.session_state: st.session_state.form_sale_cust_type = "عميل سريع (كاش)"
if 'form_sale_selected_cust' not in st.session_state: st.session_state.form_sale_selected_cust = ""
if 'form_sale_cust_name' not in st.session_state: st.session_state.form_sale_cust_name = ""
if 'form_sale_cust_phone' not in st.session_state: st.session_state.form_sale_cust_phone = ""
if 'form_sale_cust_address' not in st.session_state: st.session_state.form_sale_cust_address = ""
if 'form_purchase_qty' not in st.session_state: st.session_state.form_purchase_qty = 1
if 'system_page_choice' not in st.session_state: st.session_state.system_page_choice = "🔍 حالة المخزن"

def generate_triple_invoice_html(inv_id, datetime_str, client_name, phone, address, pay_type, collect_system, collect_date, paid_advance, remaining_bal, user, cart_items, sh_name, sh_address, sh_phone, discount_fixed=0.0):
    collect_info = ""
    if pay_type == "آجل (على الحساب)":
        collect_info = f"""
        <tr><td><b>نظام التحصيل:</b> {collect_system}</td><td><b>تاريخ الاستحقاق:</b> {collect_date}</td></tr>
        <tr><td><b>المدفوع مقدماً:</b> <span style='color:green; font-weight:bold;'>{paid_advance} جنيه</span></td><td><b>المتبقي بالذمة (آجل):</b> <span style='color:red; font-weight:bold;'>{remaining_bal} جنيه</span></td></tr>
        """
    subtotal_before_discount = sum(item['final_total'] for item in cart_items)
    total_invoice_amount = max(0.0, subtotal_before_discount - discount_fixed)
    arabic_total_words = number_to_arabic_words(total_invoice_amount)
    
    standard_table_th = "<tr><th>الصنف والبيان</th><th>الوحدة</th><th>الكمية</th><th>سعر المفرد</th><th>الصافي الإجمالي</th></tr>"
    standard_table_td = ""
    for item in cart_items:
        standard_table_td += f"<tr><td>{item['item_name']}</td><td>{item.get('unit', 'قطعة')}</td><td>{item['qty']}</td><td>{item['price']} جنيه</td><td style='font-weight: bold;'>{item['final_total']} جنيه</td></tr>"
    if discount_fixed > 0:
        standard_table_td += f"<tr style='background:#f9f9f9; font-weight:bold;'><td colspan='4' style='text-align:left;'>الخصم النقدي المباشر:</td><td>{discount_fixed} جنيه</td></tr>"
    standard_table_td += f"<tr style='background:#f2f2f2; font-weight:bold; font-size:1.1em;'><td colspan='4' style='text-align:left;'>الصافي الإجمالي المطلوب سداده:</td><td style='color:#d9534f;'>{total_invoice_amount} جنيه</td></tr>"
    standard_table_td += f"<tr style='background:#fafafa;'><td colspan='5' style='text-align:right; font-size:0.95em;'><b>التفقيط المالي للصافي:</b> {arabic_total_words}</td></tr>"
    
    print_style_setting = """
    <style>
        @media print {
            @page { size: A5 portrait; margin: 8mm 8mm 8mm 8mm; }
            body { background: #fff; color: #000; direction: rtl; }
            .invoice-card-print { border: 1px solid #000 !important; box-shadow: none !important; padding: 10px !important; margin: 0 !important; page-break-after: always; }
            .no-print { display: none !important; }
        }
        .items-table th { background:#f2f2f2 !important; color:#333 !important; padding:6px; border:1px solid #ddd; font-weight:bold; }
        .items-table td { padding:6px; border:1px solid #ddd; }
    </style>
    """
    full_triple_block = print_style_setting
    receipt_titles = ["نسخة الحسابات والإدارة العامة", "نسخة العميل والمستلم", "نسخة بوابات وأمن المخازن"]
    for title in receipt_titles:
        full_triple_block += f"""
        <div class='invoice-card-print' style='direction: rtl; text-align: right; font-family: "Segoe UI", Tahoma; border: 2px dashed #bbb; padding: 18px; margin-bottom: 30px; background: #fff; border-radius: 8px;'>
            <table style='width:100%; border-collapse:collapse; margin-bottom:8px;'>
                <tr>
                    <td style='text-align:right; vertical-align:middle;'>
                        <h3 style='margin:0; color:#2c3e50; font-size:1.3em;'>{sh_name}</h3>
                        <p style='margin:4px 0; font-size:0.85em; color:#7f8c8d;'>{sh_address} | تليفون: {sh_phone}</p>
                    </td>
                    <td style='text-align:left; vertical-align:middle;'>
                        <span style='background:#34495e; color:#fff; padding:4px 10px; font-size:0.85em; font-weight:bold; border-radius:4px;'>{title}</span>
                        <h5 style='margin:8px 0 0 0; color:#e74c3c; font-size:0.95em;'>رقم الفاتورة: {inv_id}</h5>
                    </td>
                </tr>
            </table>
            <hr style='border:0; border-top:1px solid #eee; margin:8px 0;'>
            <table style='width:100%; font-size:0.85em; background:#fafafa; padding:6px; border-radius:4px; margin-bottom:12px; border:1px solid #eaeaea;'>
                <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>تاريخ ووقـت الإصدار:</b> {datetime_str}</td></tr>
                <tr><td><b>رقم الهاتف:</b> {phone}</td><td><b>طبيعة السداد الفوري:</b> <span style='font-weight:bold; color:#2980b9;'>{pay_type}</span></td></tr>
                <tr><td><b>عنوان العميل:</b> {address}</td><td><b>المسؤول المصدر:</b> {user}</td></tr>
                {collect_info}
            </table>
            <table class='items-table' style='width:100%; border-collapse:collapse; text-align:center; font-size:0.85em;'>
                <thead>{standard_table_th}</thead>
                <tbody>{standard_table_td}</tbody>
            </table>
            <table style='width:100%; margin-top:15px; font-size:0.8em; text-align:center; color:#7f8c8d;'>
                <tr>
                    <td><b>توقيع المستلم البائع</b><br><br>........................</td>
                    <td><b>توقيع أمن البوابة</b><br><br>........................</td>
                    <td><b>توقيع العميل المستلم</b><br><br>........................</td>
                </tr>
            </table>
        </div>
        """
    return full_triple_block

def get_download_link(html_content, filename="invoice.html"):
    b64 = base64.b64encode(html_content.encode('utf-8-sig')).decode()
    return f'<div class="download-btn-area"><a href="data:text/html;base64,{b64}" download="{filename}" style="display: block; padding: 12px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px; font-weight: bold; text-align: center; margin: 15px auto; max-width:400px;">📥 اضغط هنا لتنزيل وحفظ ملف الفاتورة في التحميلات فوراً</a></div>'

if not st.session_state.auth:
    st.title(f"🏢 نظام {SHOWROOM_NAME} (Oracle Financials ERP)")
    user_input = st.text_input("اسم المستخدم", key="login_user").strip()
    pw_input = st.text_input("كلمة المرور", type="password", key="login_pw").strip()
    
    if st.button("دخول للنظام المحاسبي", use_container_width=True):
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        match = u_df[(u_df['username'] == user_input) & (u_df['password'] == pw_input)]
        if not match.empty:
            st.session_state.auth = True
            st.session_state.user = user_input
            st.session_state.role = match.iloc[0]['role']
            st.success(f"مرحباً بك يا {user_input} ({st.session_state.role})")
            st.rerun()
        else: st.error("بيانات الدخول خاطئة.")
else:
    perms_df = pd.read_csv(PERMISSIONS_FILE)
    current_role = st.session_state.role
    
    allowed_actions = perms_df[perms_df[current_role] == True]["اسم الصفحة"].tolist()
    sidebar_pages = [p for p in allowed_actions]
    
    if not sidebar_pages: sidebar_pages = ["🔍 حالة المخزن"]
        
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.write(f"الرتبة المحاسبية: **{st.session_state.role}**")
    
    if st.session_state.system_page_choice not in sidebar_pages:
        st.session_state.system_page_choice = sidebar_pages[0]
        
    choice = st.sidebar.radio("📋 القائمة المحاسبية لنظام Oracle ERP:", sidebar_pages, index=sidebar_pages.index(st.session_state.system_page_choice))
    st.session_state.system_page_choice = choice
    
    inv_df = st.session_state.inv_df
    sales_df = st.session_state.sales_df
    returns_df = st.session_state.returns_df
    purchases_df = st.session_state.purchases_df
    exp_df = st.session_state.exp_df
    att_df = st.session_state.att_df
    contacts_df = st.session_state.contacts_df
    collections_df = st.session_state.collections_df
    coa_df = st.session_state.coa_df
    gl_df = pd.read_csv(GL_JOURNAL_FILE)

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.session_state.cart = []
        st.rerun()

    def safe_item_format(x):
        if inv_df.empty: return str(x)
        match = inv_df[inv_df['كود الصنف'] == x]['اسم الصنف'].values
        return f"{x} - {match[0]}" if len(match) > 0 else f"{x} - (صنف غير معروف)"

    # --- 0. شجرة الحسابات والقيود المحاسبية (Oracle Chart of Accounts & GL) ---
    if "شجرة الحسابات" in choice:
        st.header("🏛️ دليل الحسابات العام ودفتر اليومية (Oracle Chart of Accounts & GL)")
        t_coa, t_gl, t_add_acc = st.tabs(["📊 شجرة الحسابات (COA)", "📖 دفتر القيود اليومية (General Ledger)", "➕ إضافة حساب جديد"])
        
        with t_coa:
            st.subheader("دليل شجرة الحسابات المحاسبية المعتمدة")
            st.dataframe(coa_df, use_container_width=True)
            
        with t_gl:
            st.subheader("دفتر قيود اليومية الآلية القياسية (Double-Entry Log)")
            st.dataframe(gl_df, use_container_width=True)
            
            # التحقق التلقائي من توازن القيود المحاسبية
            total_debit = pd.to_numeric(gl_df["مدين (Debit)"], errors='coerce').sum()
            total_credit = pd.to_numeric(gl_df["دائن (Credit)"], errors='coerce').sum()
            c_d, c_c, c_bal = st.columns(3)
            c_d.metric("إجمالي الطرف المدين (Total Debit)", f"{total_debit:,.2f} جنيه")
            c_c.metric("إجمالي الطرف الدائن (Total Credit)", f"{total_credit:,.2f} جنيه")
            diff = total_debit - total_credit
            if abs(diff) < 0.01:
                c_bal.success("⚖️ جميع القيود اليومية متوازنة تماماً (Balanced)")
            else:
                c_bal.error(f"🚨 غير متوازن بفرق: {diff:,.2f} جنيه")

        with t_add_acc:
            st.subheader("إضافة حساب محاسبي جديد للدليل")
            ac1, ac2, ac3, ac4 = st.columns(4)
            acc_num = ac1.text_input("رقم الحساب (الكود المحاسبي)").strip()
            acc_name = ac2.text_input("اسم الحساب").strip()
            acc_type = ac3.selectbox("نوع الحساب الفرعي", ["أصول متداولة", "أصول ثابتة", "التزامات متداولة", "حقوق ملكية", "إيرادات", "مصروفات تشغيلية", "مصروفات إدارية"])
            acc_main = ac4.selectbox("النوع الرئيسي", ["أصول", "التزامات", "حقوق ملكية", "إيرادات", "مصروفات"])
            
            if st.button("حفظ الحساب في شجرة الحسابات"):
                if acc_num and acc_name:
                    if acc_num in coa_df["رقم الحساب"].astype(str).values:
                        st.warning("⚠️ رقم الحساب موجود بالفعل!")
                    else:
                        new_acc = pd.DataFrame([{"رقم الحساب": acc_num, "اسم الحساب": acc_name, "نوع الحساب": acc_type, "النوع الرئيسي": acc_main}])
                        st.session_state.coa_df = pd.concat([coa_df, new_acc], ignore_index=True)
                        st.session_state.coa_df.to_csv(COA_FILE, index=False, encoding='utf-8-sig')
                        st.success("✅ تم إضافة الحساب لشجرة الحسابات بنجاح!")
                        st.rerun()

    # --- 1. صفحة إدارة الأصناف ---
    elif "إدارة الأصناف والمخزن" in choice:
        st.header("📦 إدارة وتكويد أصناف المخزن المتطورة")
        t_view, t_add, t_edit, t_delete = st.tabs(["📋 استعراض المنتجات", "➕ تكويد صنف جديد", "✏️ تعديل أسعار صنف", "❌ حذف صنف من النظام"])
        
        with t_view:
            st.dataframe(inv_df, use_container_width=True)
            
        with t_add:
            st.subheader("إضافة منتج جديد بالتفاصيل الجديدة")
            c1, c2, c3, c4 = st.columns(4)
            iid = c1.text_input("كود الصنف (الباركود)").strip()
            iname = c2.text_input("اسم المنتج").strip()
            icat = c3.selectbox("تصنيف الصنف", ["كهربي", "منزلي", "بلاستيك", "صيني ومطابخ", "منظفات", "عام أخري"])
            iunit = c4.selectbox("نوع الوحدة", ["قطعة", "طقم", "كرتونة", "دسته", "كيلو"])
            
            c5, c6, c7 = st.columns(3)
            iwh = c5.text_input("موقع المخزن / الرف", value="المخزن الرئيسي").strip()
            ipurchase = c6.number_input("سعر الشراء الافتراضي", min_value=0.0, step=1.0)
            isale = c7.number_input("سعر البيع الافتراضي", min_value=0.0, step=1.0)
            
            if st.button("تكويد وحفظ البند"):
                if iid and iname:
                    if iid in inv_df["كود الصنف"].values: st.warning("⚠️ هذا الكود مسجل مسبقاً!")
                    else:
                        new_item = pd.DataFrame([{"كود الصنف": iid, "اسم الصنف": iname, "تصنيف الصنف": icat, "نوع الوحدة": iunit, "موقع المخزن": iwh, "الكمية": 0, "سعر الشراء": ipurchase, "سعر البيع": isale}])
                        st.session_state.inv_df = pd.concat([inv_df, new_item], ignore_index=True)
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        st.success("🎉 تم تكويد المنتج بنجاح وحفظه!")
                        st.rerun()

        with t_edit:
            st.subheader("تعديل تفاصيل وأسعار صنف حالي")
            if inv_df.empty: 
                st.info("لا توجد أصناف مسجلة لتعديلها.")
            else:
                selected_edit_code = st.selectbox("اختر الصنف المراد تعديله", inv_df["كود الصنف"].values, format_func=safe_item_format)
                matching_rows = inv_df[inv_df["كود الصنف"] == selected_edit_code]
                if matching_rows.empty:
                    st.warning("⚠️ الصنف المحدد غير متوفر أو تم حذفه.")
                else:
                    row_idx = matching_rows.index[0]
                    ec1, ec2, ec3 = st.columns(3)
                    updated_cat = ec1.selectbox("تعديل التصنيف", ["كهربي", "منزلي", "بلاستيك", "صيني ومطابخ", "منظفات", "عام أخري"], index=["كهربي", "منزلي", "بلاستيك", "صيني ومطابخ", "منظفات", "عام أخري"].index(inv_df.at[row_idx, "تصنيف الصنف"]) if inv_df.at[row_idx, "تصنيف الصنف"] in ["كهربي", "منزلي", "بلاستيك", "صيني ومطابخ", "منظفات", "عام أخري"] else 0)
                    updated_unit = ec2.selectbox("تعديل الوحدة", ["قطعة", "طقم", "كرتونة", "دسته", "كيلو"], index=["قطعة", "طقم", "كرتونة", "دسته", "كيلو"].index(inv_df.at[row_idx, "نوع الوحدة"]) if inv_df.at[row_idx, "نوع الوحدة"] in ["قطعة", "طقم", "كرتونة", "دسته", "كيلو"] else 0)
                    updated_wh = ec3.text_input("تعديل موقع المخزن", value=str(inv_df.at[row_idx, "موقع المخزن"]))
                    
                    ec4, ec5 = st.columns(2)
                    updated_purchase = ec4.number_input("سعر الشراء الجديد", value=float(inv_df.at[row_idx, "سعر الشراء"]), min_value=0.0)
                    updated_sale = ec5.number_input("سعر البيع الجديد", value=float(inv_df.at[row_idx, "سعر البيع"]), min_value=0.0)
                    
                    if st.button("💾 حفظ الأسعار والتفاصيل الجديدة"):
                        st.session_state.inv_df.at[row_idx, "تصنيف الصنف"] = updated_cat
                        st.session_state.inv_df.at[row_idx, "نوع الوحدة"] = updated_unit
                        st.session_state.inv_df.at[row_idx, "موقع المخزن"] = updated_wh
                        st.session_state.inv_df.at[row_idx, "سعر الشراء"] = updated_purchase
                        st.session_state.inv_df.at[row_idx, "سعر البيع"] = updated_sale
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        st.success("✅ تم تحديث بيانات البند بنجاح!")
                        st.rerun()

        with t_delete:
            st.subheader("❌ حذف صنف نهائياً")
            if inv_df.empty: 
                st.info("لا توجد أصناف بالمخزن.")
            else:
                selected_del_code = st.selectbox("اختر الصنف المراد حذفه تماماً", inv_df["كود الصنف"].values, format_func=safe_item_format, key="del_box")
                st.warning("⚠️ انتبه! حذف الصنف سيؤدي لإزالته كلياً من جرد المخزن الحركي.")
                if st.button("🔥 تأكيد الحذف النهائي للصنف"):
                    st.session_state.inv_df = inv_df[inv_df["كود الصنف"] != selected_del_code]
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("🗑️ تم حذف المنتج من النظام بنجاح!")
                    st.rerun()

    # --- 2. صفحة رفع رصيد أول المدة ---
    elif "رصيد أول المدة" in choice:
        st.header("📊 رفع وتثبيت رصيد أول المدة ومخزون البضائع")
        t_paste, t_file = st.tabs(["📋 خاصية اللصق السريع المباشر", "📥 رفع ملف Excel"])
        
        def process_and_merge_data(imported_df):
            try:
                imported_df.columns = imported_df.columns.str.strip()
                if "كود الصنف" in imported_df.columns:
                    imported_df["كود الصنف"] = imported_df["كود الصنف"].astype(str)
                    combined = pd.concat([st.session_state.inv_df, imported_df]).drop_duplicates(subset=['كود الصنف'], keep='last')
                    st.session_state.inv_df = combined
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    # إنشاء قيد افتتاح رصيد أول المدة المحاسبي في أوراكل
                    total_inv_val = (pd.to_numeric(imported_df["الكمية"], errors='coerce') * pd.to_numeric(imported_df["سعر الشراء"], errors='coerce')).sum()
                    batch_id = "OB-" + str(int(datetime.now().timestamp()))
                    post_gl_journal_entry(batch_id, "OB-INIT", "رصيد المخزون الافتتاحي - أول المدة", "مخزون البضائع Inventory", "رأس المال Owner's Equity", total_inv_val, st.session_state.user)
                    
                    st.success("🚀 تم دمج وحفظ البيانات وإنشاء القيد المحاسبي الافتتاحي بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ فشل الدمج: تأكد من احتواء العناوين على حقل 'كود الصنف'.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء ترحيل البيانات: {e}")

        with t_paste:
            pasted_input = st.text_area("قم باللصق هنا (Ctrl + V)", height=250)
            if pasted_input.strip():
                try:
                    paste_df = pd.read_csv(StringIO(pasted_input), sep="\t")
                    st.dataframe(paste_df, use_container_width=True)
                    if st.button("🚀 ترحيل وحفظ البيانات الملصوقة فوراً"):
                        process_and_merge_data(paste_df)
                except Exception as ex:
                    st.error(f"🚨 تعذر تحليل النص: {ex}")

        with t_file:
            uploaded_file = st.file_uploader("اختر شيت الاكسل الخاص بالبضائع", type=["xlsx", "xls"])
            if uploaded_file is not None:
                try:
                    excel_df = pd.read_excel(uploaded_file, dtype={"كود الصنف": str})
                    st.dataframe(excel_df)
                    if st.button("تأكيد ودمج الملف في رصيد أول المدة"):
                        process_and_merge_data(excel_df)
                except Exception as e: st.error(f"❌ خطأ قراءة الملف: {e}")

    # --- 3. صفحة حالة المخزن ---
    elif "حالة المخزن" in choice:
        st.header("🔍 جرد بضائع المخزن الحالية ومواقع تواجدها")
        st.dataframe(inv_df, use_container_width=True)

    # --- 4. العملاء والموردين وسندات القبض ---
    elif "العملاء والموردين" in choice:
        st.header("🤝 إدارة بيانات العملاء والموردين وكشوفات الحساب")
        t_contacts, t_statement = st.tabs(["👥 تسجيل وعرض الجهات", "📊 كشف حساب عميل مفصل"])
        with t_contacts:
            st.dataframe(contacts_df, use_container_width=True)
            c1, c2, c3, c4 = st.columns(4)
            ctype = c1.selectbox("النوع", ["عميل", "مورد"])
            cname = c2.text_input("الاسم")
            cphone = c3.text_input("الهاتف")
            caddress = c4.text_input("العنوان")
            if st.button("حفظ الجهة"):
                if cname:
                    new_c = pd.DataFrame([{"النوع": ctype, "الاسم": cname, "الهاتف": cphone, "العنوان": caddress}])
                    st.session_state.contacts_df = pd.concat([contacts_df, new_c], ignore_index=True)
                    st.session_state.contacts_df.to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم حفظ الجهة بنجاح!")
                    st.rerun()
        with t_statement:
            all_custs = contacts_df[contacts_df["النوع"] == "عميل"]["الاسم"].unique()
            if len(all_custs) == 0:
                st.info("لم يتم تسجيل أي عملاء في النظام حتى الآن.")
            else:
                selected_cust = st.selectbox("اختر العميل لاستعراض ماليته:", all_custs)
                cust_info = contacts_df[(contacts_df["الاسم"] == selected_cust) & (contacts_df["النوع"] == "عميل")]
                cust_phone = str(cust_info.iloc[0]["الهاتف"]).strip() if not cust_info.empty else ""
                
                cust_sales = sales_df[sales_df["اسم العميل"] == selected_cust]
                cust_returns = returns_df[returns_df["اسم العميل"] == selected_cust] if not returns_df.empty else pd.DataFrame()
                cust_colls = collections_df[collections_df["اسم العميل"] == selected_cust] if not collections_df.empty else pd.DataFrame()
                
                total_invoiced = pd.to_numeric(cust_sales["إجمالي البيع"], errors='coerce').sum()
                total_paid_at_invoice = 0.0
                if not cust_sales.empty:
                    for _, s_row in cust_sales.drop_duplicates("رقم الفاتورة").iterrows():
                        if s_row["نوع البيع"] == "نقدي (كاش)":
                            total_paid_at_invoice += pd.to_numeric(cust_sales[cust_sales["رقم الفاتورة"] == s_row["رقم الفاتورة"]]["إجمالي البيع"], errors='coerce').sum()
                        else:
                            total_paid_at_invoice += pd.to_numeric(s_row.get("المدفوع مقدم", 0), errors='coerce')
                total_subsequent_payments = pd.to_numeric(cust_colls["المبلغ المحصل"], errors='coerce').sum() if not cust_colls.empty else 0.0
                total_returned = pd.to_numeric(cust_returns["المبلغ المردود"], errors='coerce').sum() if not cust_returns.empty else 0.0
                grand_total_paid = total_paid_at_invoice + total_subsequent_payments
                current_debt = total_invoiced - grand_total_paid - total_returned
                
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("🛒 إجمالي المبيعات", f"{total_invoiced:,.2f} جنيه")
                k2.metric("🟢 إجمالي المدفوعات والتحصيلات", f"{grand_total_paid:,.2f} جنيه")
                k3.metric("↩️ إجمالي المردودات له", f"{total_returned:,.2f} جنيه")
                k4.metric("🚨 المديونية الحالية بالذمة", f"{current_debt:,.2f} جنيه", delta_color="inverse")
                st.markdown("---")
                col_pay1, col_pay2, col_pay3 = st.columns(3)
                pay_amt = col_pay1.number_input("المبلغ المدفوع (جنيه)", min_value=0.0, step=50.0)
                pay_method = col_pay2.selectbox("طريقة السداد", ["نقدي خزينة", "حوالة فودافون كاش", "فيزا / شبكة", "شيك بنكي"])
                pay_notes = col_pay3.text_input("ملاحظات السداد", placeholder="سداد دفعة آجل")
                
                if st.button("💵 تأكيد وترحيل السند وقيد اليومية للعميل", use_container_width=True):
                    if pay_amt <= 0: st.error("يرجى إدخال مبلغ صحيح.")
                    else:
                        coll_id = "REC-" + str(int(datetime.now().timestamp()))
                        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_coll = pd.DataFrame([{ "رقم السند": coll_id, "التاريخ": current_time_str, "اسم العميل": selected_cust, "المبلغ المحصل": pay_amt, "طريقة السداد": pay_method, "ملاحظات": pay_notes, "المسؤول": st.session_state.user }])
                        st.session_state.collections_df = pd.concat([collections_df, new_coll], ignore_index=True)
                        st.session_state.collections_df.to_csv(COLLECTIONS_FILE, index=False, encoding='utf-8-sig')
                        
                        # إنشاء القيد المحاسبي المزدوج في أوراكل: من حـ/ الخزينة إلى حـ/ العملاء والذمم المدينة
                        post_gl_journal_entry(coll_id, coll_id, f"سند تحصيل دفعة من العميل: {selected_cust}", "النقدية بالخزينة Main Cash", "العملاء والذمم المدينة Accounts Receivable", pay_amt, st.session_state.user)
                        
                        st.success(f"🎉 تم تسجيل السند وترحيل القيد المحاسبي بنجاح!")

    # --- 5. صفحة حركة فواتير الشراء المطور (Oracle AP Procurement) ---
    elif "حركة فواتير الشراء" in choice:
        st.header("📥 تسجيل وإدارة فواتير المشتريات والوارد (Oracle AP Procurement)")
        t_new, t_manage = st.tabs(["📥 تسجيل فاتورة شراء جديدة", "✏️ مراجعة وحذف الفواتير القديمة"])
        
        with t_new:
            if inv_df.empty: st.warning("⚠️ قم بتكويد بضائع أولاً.")
            else:
                m_list = contacts_df[contacts_df['النوع'] == 'مورد']['الاسم'].unique()
                if len(m_list) == 0: m_list = ["مورد عام"]
                c1, c2, c3, c4 = st.columns(4)
                vendor = c1.selectbox("المورد", m_list)
                
                selected_item_code = c2.selectbox("الصنف المشترى", inv_df['كود الصنف'].values, format_func=safe_item_format)
                matching_items = inv_df[inv_df['كود الصنف'] == selected_item_code]
                if not matching_items.empty:
                    item_row = matching_items.iloc[0]
                    default_pur_price = float(item_row['سعر الشراء']) if 'سعر الشراء' in item_row else 0.0
                    actual_purchase_price = c3.number_input("سعر الشراء المعتمد", value=default_pur_price, min_value=0.0)
                    qty = c4.number_input("الكمية المشتراة", min_value=1, step=1, value=st.session_state.form_purchase_qty)
                    st.session_state.form_purchase_qty = qty
                    total = actual_purchase_price * qty
                    
                    if st.button("حفظ المشتريات وإنشـاء القيد المحاسبي المزدوج"):
                        idx = inv_df[inv_df['كود الصنف'] == selected_item_code].index[0]
                        st.session_state.inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) + qty
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        
                        pur_id = "PUR-" + str(int(datetime.now().timestamp()))
                        new_p = pd.DataFrame([{"رقم الفاتورة": pur_id, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "المورد": vendor, "كود الصنف": selected_item_code, "الصنف": item_row['اسم الصنف'], "تصنيف الصنف": item_row['تصنيف الصنف'], "نوع الوحدة": item_row['نوع الوحدة'], "موقع المخزن": item_row['موقع المخزن'], "سعر الشراء المعتمد": str(actual_purchase_price), "الكمية": str(qty), "إجمالي الشراء": str(total), "المسؤول": st.session_state.user}])
                        st.session_state.purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                        st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                        
                        # إنشاء قيد المشتريات المزدوج (Oracle Double Entry): من حـ/ المخزون إلى حـ/ الموردين والذمم الدائنة
                        post_gl_journal_entry(pur_id, pur_id, f"فاتورة شراء بضاعة من المورد: {vendor}", "مخزون البضائع Inventory", "الموردين والذمم الدائنة Accounts Payable", total, st.session_state.user)
                        
                        st.session_state.form_purchase_qty = 1  
                        st.success("✅ تم تسجيل الوارد وإدراج القيود المحاسبية بنجاح!")
                        st.rerun()

        with t_manage:
            st.dataframe(purchases_df, use_container_width=True)

    # --- 6. صفحة حركة فواتير البيع وإصدار الفواتير (Oracle AR Order Management) ---
    elif "📤 حركة فواتير البيع" in choice:
        st.header("📤 لوحة حركة فواتير البيع وإصدار الفواتير المتطورة")
        tab1, tab2 = st.tabs(["🆕 إصدار فاتورة جديدة", "🔍 البحث وتعديل فاتورة قديمة"])
        
        with tab1:
            cust_type_select = st.radio("نوع العميل للفاتورة الحالية:", ["عميل سريع (كاش)", "عميل مكود ومسجل مسبقاً"], horizontal=True)
            sale_cust, sale_phone, sale_address = "", "", ""
            
            if cust_type_select == "عميل سريع (كاش)":
                c1, c2, c3 = st.columns(3)
                sale_cust = c1.text_input("اسم العميل السريع", value=st.session_state.form_sale_cust_name)
                sale_phone = c2.text_input("رقم الهاتف (اختياري)", value=st.session_state.form_sale_cust_phone)
                sale_address = c3.text_input("العنوان (اختياري)", value=st.session_state.form_sale_cust_address)
            else:
                all_saved_customers = contacts_df[contacts_df["النوع"] == "عميل"]["الاسم"].unique() if not contacts_df.empty else []
                if len(all_saved_customers) > 0:
                    selected_c_name = st.selectbox("اختر العميل المكود من النظام:", all_saved_customers)
                    cust_data_row = contacts_df[(contacts_df["الاسم"] == selected_c_name) & (contacts_df["النوع"] == "عميل")].iloc[0]
                    sale_cust = str(selected_c_name)
                    sale_phone = str(cust_data_row["الهاتف"])
                    sale_address = str(cust_data_row["العنوان"])

            sc1, sc2, sc3, sc4, sc5 = st.columns(5)
            if not inv_df.empty:
                selected_sale_code = sc1.selectbox("اختر الصنف للبيع", inv_df["كود الصنف"].values, format_func=safe_item_format)
                match_s = inv_df[inv_df["كود الصنف"] == selected_sale_code].iloc[0]
                sale_qty = sc2.number_input(f"الكمية (المتاحة: {match_s['الكمية']})", min_value=1, max_value=int(match_s['الكمية']) if int(match_s['الكمية']) > 0 else 1, step=1)
                custom_sale_price = sc3.number_input("سعر البيع المعتمد", value=float(match_s['سعر البيع']), min_value=0.0)
                custom_purchase_cost = sc4.number_input("سعر الشراء المعتمد", value=float(match_s['سعر الشراء']), min_value=0.0)
                sale_disc = sc5.number_input("نسبة الخصم %", min_value=0.0, max_value=100.0, step=1.0, value=0.0)
                
                if st.button("➕ إضافة المنتج المختار إلى سلة الفاتورة الحالية", use_container_width=True):
                    if match_s['الكمية'] > 0:
                        tot_b = sale_qty * custom_sale_price
                        final_tot_p = tot_b - (tot_b * (sale_disc / 100))
                        st.session_state.cart.append({
                            "item_code": selected_sale_code, "item_name": match_s['اسم الصنف'],
                            "category": match_s['تصنيف الصنف'], "unit": match_s['نوع الوحدة'],
                            "warehouse_loc": match_s['موقع المخزن'], "qty": int(sale_qty),
                            "price": float(custom_sale_price), "discount": float(sale_disc),
                            "final_total": float(final_tot_p), "purchase_cost": float(custom_purchase_cost)
                        })
                        st.success("تم الإضافة للسلة!")
                        st.rerun()

            if st.session_state.cart:
                st.write("🧾 الأصناف المدرجة بالسلة:")
                st.dataframe(pd.DataFrame(st.session_state.cart))
                subtotal_before_discount = sum(item['final_total'] for item in st.session_state.cart)
                discount_fixed = st.number_input("💵 خصم نقدي مباشر", min_value=0.0, value=0.0)
                total_invoice_amount = max(0.0, subtotal_before_discount - discount_fixed)
                
                pay_type = st.radio("نوع عملية البيع", ["نقدي (كاش)", "آجل (على الحساب)"], horizontal=True)
                collect_system, collect_date, paid_advance, remaining_bal = "غير محدد", "غير محدد", 0.0, 0.0
                
                if pay_type == "آجل (على الحساب)":
                    ac1, ac2, ac3 = st.columns(3)
                    collect_system = ac1.selectbox("نظام التحصيل", ["أسبوعي", "شهري", "دفعات مرنة"])
                    collect_date = ac2.text_input("تاريخ الاستحقاق", value=datetime.now().strftime("%Y-%m-%d"))
                    paid_advance = ac3.number_input("المدفوع مقدم", min_value=0.0, max_value=float(total_invoice_amount))
                    remaining_bal = total_invoice_amount - paid_advance

                if st.button("🚀 ترحيل الفاتورة نهائياً وإنشاء قيود أوراكل اليومية", use_container_width=True):
                    if sale_cust:
                        inv_id = generate_sequential_invoice_id(sales_df)
                        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        total_cogs_amount = 0.0
                        sales_rows = []
                        
                        for item in st.session_state.cart:
                            item_tot_cost = item['qty'] * item['purchase_cost']
                            total_cogs_amount += item_tot_cost
                            item_net_profit = item['final_total'] - item_tot_cost
                            
                            sales_rows.append({
                                "رقم الفاتورة": inv_id, "التاريخ": datetime_str, "اسم العميل": sale_cust,
                                "هاتف العميل": sale_phone, "العنوان": sale_address, "نوع البيع": pay_type,
                                "نظام التحصيل": collect_system, "تاريخ التحصيل": collect_date,
                                "المدفوع مقدم": paid_advance, "المتبقي": remaining_bal,
                                "كود الصنف": item['item_code'], "الصنف": item['item_name'],
                                "تصنيف الصنف": item['category'], "نوع الوحدة": item['unit'],
                                "موقع المخزن": item['warehouse_loc'], "الكمية": item['qty'],
                                "سعر الوحدة": item['price'], "الخصم %": item['discount'],
                                "خصم نقدي ثابت": discount_fixed,
                                "إجمالي البيع": item['final_total'], "تكلفة الشراء الإجمالية": item_tot_cost,
                                "صافي ربح الفاتورة": item_net_profit, "المسؤول": st.session_state.user
                            })
                            
                            idx = inv_df[inv_df["كود الصنف"] == item['item_code']].index[0]
                            st.session_state.inv_df.at[idx, "الكمية"] -= int(item['qty'])
                            
                        new_sales_df = pd.DataFrame(sales_rows)
                        st.session_state.sales_df = pd.concat([sales_df, new_sales_df], ignore_index=True)
                        st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        
                        # --- القيود المحاسبية الآلية المزدوجة وفق معايير أوراكل Oracle GL Posting ---
                        if pay_type == "نقدي (كاش)":
                            # قيد المبيعات النقدي: من حـ/ الخزينة إلى حـ/ إيرادات المبيعات
                            post_gl_journal_entry(inv_id, inv_id, f"إيراد فاتورة مبيعات نقدية للعميل: {sale_cust}", "النقدية بالخزينة Main Cash", "إيرادات المبيعات Sales Revenue", total_invoice_amount, st.session_state.user)
                        else:
                            # قيد المبيعات الآجلة: من حـ/ النقدية بالخزينة (بالمقدم) وحـ/ العملاء والذمم المدينة (بالمتبقي) إلى حـ/ إيرادات المبيعات
                            if paid_advance > 0:
                                post_gl_journal_entry(inv_id, inv_id, f"المقدم النقدي لفاتورة آجل: {sale_cust}", "النقدية بالخزينة Main Cash", "إيرادات المبيعات Sales Revenue", paid_advance, st.session_state.user)
                            if remaining_bal > 0:
                                post_gl_journal_entry(inv_id, inv_id, f"المديونية الآجلة لفاتورة العميل: {sale_cust}", "العملاء والذمم المدينة Accounts Receivable", "إيرادات المبيعات Sales Revenue", remaining_bal, st.session_state.user)
                        
                        # قيد إخراج المخزون وتكلفة المبيعات (COGS Entry): من حـ/ تكلفة البضاعة المباعة إلى حـ/ مخزون البضائع
                        post_gl_journal_entry(inv_id, inv_id, f"إثبات تكلفة البضاعة المباعة للفاتورة {inv_id}", "تكلفة البضاعة المباعة Cost of Goods Sold", "مخزون البضائع Inventory", total_cogs_amount, st.session_state.user)
                        
                        st.success(f"🎉 تم ترحيل الفاتورة وإدراج جميع القيود المحاسبية المزدوجة بنجاح برقم {inv_id}!")
                        
                        html_invoice = generate_triple_invoice_html(inv_id, datetime_str, sale_cust, sale_phone, sale_address, pay_type, collect_system, collect_date, paid_advance, remaining_bal, st.session_state.user, st.session_state.cart, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, discount_fixed=discount_fixed)
                        st.markdown(html_invoice, unsafe_allow_html=True)
                        st.session_state.cart = []
                        st.rerun()

        with tab2:
            st.dataframe(sales_df, use_container_width=True)

    # --- 7. ارتجاع المبيعات مع القيود العكسية ---
    elif "ارتجاع فواتير البيع" in choice:
        st.header("↩️ ارتجاع فواتير البيع والقيود المحاسبية العكسية")
        if sales_df.empty:
            st.info("لا توجد فواتير مبيعات مسجلة.")
        else:
            invoice_list = sales_df["رقم الفاتورة"].unique().tolist()
            selected_inv = st.selectbox("اختر رقم الفاتورة المراد إرجاعها:", options=[""] + invoice_list)
            
            if selected_inv:
                inv_items = sales_df[sales_df["رقم الفاتورة"] == selected_inv]
                client_name = inv_items.iloc[0]["اسم العميل"]
                st.dataframe(inv_items[["كود الصنف", "الصنف", "الكمية", "إجمالي البيع"]], use_container_width=True)
                
                if st.button("🔴 تأكيد إرجاع الفاتورة وإنشاء قيد التسوية المحاسبي العكسي", use_container_width=True):
                    ret_id = f"RET-{int(datetime.now().timestamp())}"
                    ret_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    total_refund = 0.0
                    total_cost_returned = 0.0
                    return_rows = []
                    
                    for _, row in inv_items.iterrows():
                        p_code = str(row["كود الصنف"])
                        qty_to_return = int(row["الكمية"])
                        refund_amt = float(row["إجمالي البيع"])
                        cost_amt = float(row.get("تكلفة الشراء الإجمالية", 0))
                        
                        total_refund += refund_amt
                        total_cost_returned += cost_amt
                        
                        if p_code in st.session_state.inv_df["كود الصنف"].values:
                            idx = st.session_state.inv_df[st.session_state.inv_df["كود الصنف"] == p_code].index[0]
                            st.session_state.inv_df.at[idx, "الكمية"] += qty_to_return
                        
                        return_rows.append({
                            "رقم الإرجاع": ret_id, "رقم الفاتورة الأصلية": selected_inv,
                            "التاريخ": ret_date, "اسم العميل": client_name,
                            "كود الصنف": p_code, "الصنف": row["الصنف"],
                            "الكمية المرجعة": qty_to_return, "المبلغ المردود": refund_amt,
                            "المسؤول": st.session_state.user
                        })
                    
                    new_returns_df = pd.DataFrame(return_rows)
                    st.session_state.returns_df = pd.concat([returns_df, new_returns_df], ignore_index=True)
                    st.session_state.returns_df.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
                    
                    st.session_state.sales_df = sales_df[sales_df["رقم الفاتورة"] != selected_inv]
                    st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    # إنشاء قيود الارتجاع العكسية أوراكل (Reversing Journal Entries)
                    post_gl_journal_entry(ret_id, selected_inv, f"قيد مردودات مبيعات للعميل: {client_name}", "مردودات ومسموحات المبيعات Sales Returns", "النقدية بالخزينة Main Cash", total_refund, st.session_state.user)
                    post_gl_journal_entry(ret_id, selected_inv, f"قيد إرجاع البضاعة للمخزن للفاتورة {selected_inv}", "مخزون البضائع Inventory", "تكلفة البضاعة المباعة Cost of Goods Sold", total_cost_returned, st.session_state.user)
                    
                    st.success("✅ تم تسجيل الارتجاع وخصم القيود المحاسبية العكسية بنجاح!")
                    st.rerun()

    # --- 8. البحث والطباعة ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 البحث الذكي، معاينة الفواتير، وطباعتها")
        if not sales_df.empty:
            invoice_list = sales_df["رقم الفاتورة"].unique()
            selected_inv_id = st.selectbox("🎯 اختر رقم الفاتورة:", invoice_list)
            inv_items = sales_df[sales_df["رقم الفاتورة"] == selected_inv_id].copy()
            first_row = inv_items.iloc[0]
            
            preview_cart = []
            for _, r in inv_items.iterrows():
                preview_cart.append({
                    "item_name": r["الصنف"], "unit": r.get("نوع الوحدة", "قطعة"),
                    "qty": r["الكمية"], "price": r["سعر الوحدة"], "final_total": r["إجمالي البيع"]
                })
            
            invoice_html_content = generate_triple_invoice_html(
                inv_id=selected_inv_id, datetime_str=first_row["التاريخ"],
                client_name=first_row["اسم العميل"], phone=first_row["هاتف العميل"],
                address=first_row["العنوان"], pay_type=first_row["نوع البيع"],
                collect_system=first_row.get("نظام التحصيل", "فوري"),
                collect_date=first_row.get("تاريخ التحصيل", "-"),
                paid_advance=first_row.get("المدفوع مقدم", 0),
                remaining_bal=first_row.get("المتبقي", 0),
                user=first_row.get("المسؤول", st.session_state.user),
                cart_items=preview_cart, sh_name=SHOWROOM_NAME,
                sh_address=SHOWROOM_ADDRESS, sh_phone=INQUIRY_NUMBER,
                discount_fixed=float(first_row.get("خصم نقدي ثابت", 0))
            )
            st.components.v1.html(invoice_html_content, height=500, scrolling=True)

    # --- 9. المصاريف والقيود ---
    elif "المصاريف" in choice:
        st.header("💸 تسجيل المصاريف والعموميات")
        c1, c2 = st.columns(2)
        exp_desc = c1.text_input("بيان المصروف")
        exp_amount = c2.number_input("المبلغ", min_value=0.0)
        
        if st.button("حفظ المصروف وترحيل القيد المحاسبي"):
            if exp_desc and exp_amount > 0:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_e = pd.DataFrame([{"التاريخ": current_time, "البيان": exp_desc, "المبلغ": exp_amount, "المسؤول": st.session_state.user}])
                st.session_state.exp_df = pd.concat([exp_df, new_e], ignore_index=True)
                st.session_state.exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                
                exp_id = "EXP-" + str(int(datetime.now().timestamp()))
                # قيد المصروفات: من حـ/ المصاريف العمومية إلى حـ/ النقدية بالخزينة
                post_gl_journal_entry(exp_id, exp_id, f"مصروف: {exp_desc}", "المصاريف العمومية والإدارية General Expenses", "النقدية بالخزينة Main Cash", exp_amount, st.session_state.user)
                
                st.success("✅ تم تسجيل المصروف وإدراج قيده المحاسبي بنجاح!")
                st.rerun()

    # --- 10. تقارير وميزان المراجعة المحاسبي (Oracle Trial Balance & Financial Reports) ---
    elif "ميزان المراجع والتقارير المالية" in choice:
        st.header("📈 ميزان المراجعة والتقارير المالية المتقدمة (Oracle Financial Reports)")
        
        tab_tb, tab_pl = st.tabs(["⚖️ ميزان المراجعة (Trial Balance)", "📜 قائمة الدخل والأرباح (Income Statement)"])
        
        with tab_tb:
            st.subheader("ميزان المراجعة بالأرصدة والجامع المحاسبي")
            if not gl_df.empty:
                tb_df = gl_df.groupby(["رقم الحساب", "اسم الحساب"]).agg({
                    "مدين (Debit)": "sum",
                    "دائن (Credit)": "sum"
                }).reset_index()
                
                tb_df["الرصيد الصافي (Net Balance)"] = tb_df["مدين (Debit)"] - tb_df["دائن (Credit)"]
                st.dataframe(tb_df, use_container_width=True)
                
                tot_d = tb_df["مدين (Debit)"].sum()
                tot_c = tb_df["دائن (Credit)"].sum()
                st.info(f"⚖️ مجموع الأطراف المدينة: **{tot_d:,.2f} جنيه** | مجموع الأطراف الدائنة: **{tot_c:,.2f} جنيه**")
            else:
                st.info("لا توجد حركات محاسبية لإنشاء ميزان المراجعة.")

        with tab_pl:
            st.subheader("قائمة الدخل الشاملة (Profit and Loss Statement)")
            
            rev = pd.to_numeric(gl_df[gl_df["اسم الحساب"] == "إيرادات المبيعات Sales Revenue"]["دائن (Credit)"], errors='coerce').sum()
            cogs = pd.to_numeric(gl_df[gl_df["اسم الحساب"] == "تكلفة البضاعة المباعة Cost of Goods Sold"]["مدين (Debit)"], errors='coerce').sum()
            returns = pd.to_numeric(gl_df[gl_df["اسم الحساب"] == "مردودات ومسموحات المبيعات Sales Returns"]["مدين (Debit)"], errors='coerce').sum()
            expenses = pd.to_numeric(gl_df[gl_df["اسم الحساب"] == "المصاريف العمومية والإدارية General Expenses"]["مدين (Debit)"], errors='coerce').sum()
            
            net_sales = rev - returns
            gross_profit = net_sales - cogs
            net_income = gross_profit - expenses
            
            c_r1, c_r2, c_r3, c_r4 = st.columns(4)
            c_r1.metric("صافي الإيرادات", f"{net_sales:,.2f} جنيه")
            c_r2.metric("تكلفة البضاعة المباعة (COGS)", f"{cogs:,.2f} جنيه")
            c_r3.metric("مجمل الربح (Gross Profit)", f"{gross_profit:,.2f} جنيه")
            c_r4.metric("صافي الربح النهائي (Net Income)", f"{net_income:,.2f} جنيه", delta_color="normal" if net_income >= 0 else "inverse")
