import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from io import BytesIO
from io import StringIO
import urllib.parse

# إعدادات الصفحة والشكل العام
st.set_page_config(page_title="نظام معرض الكبير لإدارة المخازن المتطور", layout="wide")

# أسماء ملفات البيانات (CSV المعتمدة)
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
COLLECTIONS_FILE = "collections_data.csv" # ملف التحصيلات وسدادات الآجل

# دالة تحويل الأرقام إلى كلمات عربية (التفقيط)
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
            elif thousands >= 3 and thousands <= 10: words.append(f"{units[thousands]} آلاف")
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
                if unit_part > 0:
                    words.append(f"{units[unit_part]} و{tens[tens_part]}")
                else:
                    words.append(tens[tens_part])
                    
        return "فقط " + " و ".join([w for w in words if w != "و"]) + " جنيهاً مصرياً لا غير"
    except:
        return ""

# دالة تهيئة الملفات وإنشائها في حال عدم وجودها
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([
            {"username": "admin", "password": "123", "role": "مدير"},
            {"username": "sharaf", "password": "456", "role": "مشرف"},
            {"username": "user1", "password": "111", "role": "موظف"}
        ]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "تصنيف الصنف", "نوع الوحدة", "موقع المخزن", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "هاتف العميل", "العنوان", "نوع البيع", "نظام التحصيل", "تاريخ التحصيل", "المدفوع مقدم", "المتبقي", "كود الصنف", "الصنف", "تصنيف الصنف", "نوع الوحدة", "موقع المخزن", "الكمية", "سعر الوحدة", "الخصم %", "إجمالي البيع", "تكلفة الشراء الإجمالية", "صافي ربح الفاتورة", "المسؤول", "الخصم النقدي"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
        
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
        pd.DataFrame([{"اسم المعرض": "معرض الكبير", "العنوان": "ابوحماد - قرية العراقي - بجوار مدرسة الشهيد صلاح فتحي", "رقم الدعم": "0100XXXXXXX"}]).to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')

    all_pages = [
        "📦 إدارة الأصناف والمخزن", "📊 رصيد أول المدة Excel", "🔍 حالة المخزن", 
        "🤝 العملاء والموردين", "📥 حركة فواتير الشراء", "📤 حركة فواتير البيع", 
        "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "📈 تقارير البيع والشراء والأرباح", "💸 المصاريف", 
        "⏰ الحضور والانصراف", "⚙️ إدارة وتعديل الصلاحيات والحسابات", "⚙️ إعدادات بيانات الفاتورة والدعم"
    ]
    
    if not os.path.exists(PERMISSIONS_FILE):
        default_perms = []
        for page in all_pages:
            default_perms.append({
                "اسم الصفحة": page, 
                "مدير": True, 
                "مشرف": True if page in ["🔍 حالة المخزن", "📥 حركة فواتير الشراء", "📤 حركة فواتير البيع", "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"] else False, 
                "موظف": True if page in ["🔍 حالة المخزن", "📤 حركة فواتير البيع", "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"] else False
            })
        pd.DataFrame(default_perms).to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')

init_files()

# دالة لتحميل جميع البيانات في الـ Session State
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
        if "الخصم النقدي" not in st.session_state.sales_df.columns:
            st.session_state.sales_df["الخصم النقدي"] = 0.0
            
        st.session_state.returns_df = pd.read_csv(RETURNS_FILE, dtype={"رقم الإرجاع": str, "رقم الفاتورة الأصلية": str, "كود الصنف": str})
        st.session_state.purchases_df = pd.read_csv(PURCHASES_FILE, dtype={"رقم الفاتورة": str, "كود الصنف": str})
        st.session_state.exp_df = pd.read_csv(EXPENSES_FILE)
        st.session_state.att_df = pd.read_csv(ATTENDANCE_FILE)
        st.session_state.contacts_df = pd.read_csv(CONTACTS_FILE, dtype=str)
        st.session_state.collections_df = pd.read_csv(COLLECTIONS_FILE)
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

if 'form_sale_cust_name' not in st.session_state: st.session_state.form_sale_cust_name = ""
if 'form_sale_cust_phone' not in st.session_state: st.session_state.form_sale_cust_phone = ""
if 'form_sale_cust_address' not in st.session_state: st.session_state.form_sale_cust_address = ""
if 'form_purchase_qty' not in st.session_state: st.session_state.form_purchase_qty = 1

# تحديث دالة الطباعة بالـ CSS الجديد لمعالجة مشكلة التداخل وضبط الخصم بالجنيه
def generate_triple_invoice_html(inv_id, datetime_str, client_name, phone, address, pay_type, collect_system, collect_date, paid_advance, remaining_bal, user, cart_items, sh_name, sh_address, sh_phone, cash_discount=0.0):
    collect_info = ""
    if pay_type == "آجل (على الحساب)":
        collect_info = f"""
        <tr><td><b>نظام التحصيل:</b> {collect_system}</td><td><b>تاريخ الاستحقاق:</b> {collect_date}</td></tr>
        <tr><td><b>المدفوع مقدماً:</b> <span style='color:green; font-weight:bold;'>{paid_advance} جنيه</span></td><td><b>المتبقي بالذمة (آجل):</b> <span style='color:red; font-weight:bold;'>{remaining_bal} جنيه</span></td></tr>
        """
    
    subtotal_amount = sum(item['final_total'] for item in cart_items)
    total_invoice_amount = max(0.0, subtotal_amount - cash_discount)
    arabic_total_words = number_to_arabic_words(total_invoice_amount)
    
    standard_table_th = "<thead><tr><th>الصنف والبيان</th><th>التصنيف</th><th>الوحدة</th><th>الكمية</th><th>سعر المفرد</th><th>الخصم</th><th>الصافي</th></tr></thead>"
    standard_table_td = "<tbody>"
    for item in cart_items:
        standard_table_td += f"<tr><td>{item['item_name']}</td><td>{item.get('category', 'عام')}</td><td>{item.get('unit', 'قطعة')}</td><td>{item['qty']}</td><td>{item['price']} جنيه</td><td>{item['discount']}%</td><td style='font-weight: bold;'>{item['final_total']} جنيه</td></tr>"
    standard_table_td += "</tbody>"
    
    store_table_th = "<thead><tr><th>الصنف والبيان</th><th>موقع المخزن</th><th>الكمية المطلوبة للصرف</th></tr></thead>"
    store_table_td = "<tbody>"
    for item in cart_items:
        store_table_td += f"<tr><td style='font-size: 15px; font-weight: bold;'>{item['item_name']} ({item.get('unit', 'قطعة')})</td><td>{item.get('warehouse_loc', 'الرئيسي')}</td><td style='font-size: 16px; font-weight: bold;'>{item['qty']}</td></tr>"
    store_table_td += "</tbody>"

    html_content = f"""
    <div class="triple-print-wrapper">
        <style>
            @page {{ size: A5 portrait; margin: 5mm; }}
            @media print {{
                body {{ direction: rtl; background: #fff; color: #000; padding: 0; margin: 0; font-size: 12px; }}
                header, [data-testid="stSidebar"], [data-testid="stHeader"], .no-print-zone, .stButton, .download-btn-area {{ display: none !important; }}
                .invoice-page {{ width: 100%; height: auto; box-sizing: border-box; padding: 5mm !important; margin: 0 0 15mm 0 !important; page-break-after: always; page-break-inside: avoid; border: 2px solid #000 !important; box-shadow: none !important; }}
                table {{ page-break-inside: auto; }}
                tr {{ page-break-inside: avoid; page-break-after: auto; }}
                thead {{ display: table-header-group; }}
                tfoot {{ display: table-footer-group; }}
            }}
            .triple-print-wrapper {{ direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; }}
            .invoice-page {{ width: 148mm; max-width: 100%; border: 2px solid #000; padding: 20px; margin: 20px auto; background: #fff; color: #000; box-sizing: border-box; page-break-after: always; }}
            .invoice-header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 10px; page-break-inside: avoid; }}
            .invoice-header h3 {{ margin: 0; background: #000; color: #fff; padding: 4px 12px; display: inline-block; font-size: 14px; border-radius: 4px; }}
            .invoice-header h1 {{ margin: 6px 0; font-size: 24px; color: #000; font-weight: 700; }}
            .invoice-header p {{ font-size: 12px; margin: 2px 0; color: #000; }}
            .invoice-details-table {{ width: 100%; font-size: 13px; margin-top: 5px; border-bottom: 1px solid #000; padding-bottom: 8px; page-break-inside: avoid; }}
            .invoice-details-table td {{ padding: 4px 0; width: 50%; }}
            .invoice-items-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; border: 2px solid black; font-size: 13px; text-align: center; }}
            .invoice-items-table th {{ background: #f2f2f2; border: 1px solid black; padding: 8px; font-weight: bold; color: #000; }}
            .invoice-items-table td {{ border: 1px solid black; padding: 8px; }}
            .total-words-area {{ margin-top: 15px; background: #fff; border: 1px dashed #000; padding: 8px; font-size: 14px; font-weight: bold; text-align: right; page-break-inside: avoid; }}
            .invoice-footer-alert {{ margin-top: 15px; font-size: 11px; font-weight: bold; text-align: center; border: 1px solid #000; padding: 6px; background: #fff; page-break-inside: avoid; }}
            .print-trigger-btn {{ background-color: #28a745; color: white; padding: 12px 24px; margin: 10px auto; border: none; border-radius: 5px; cursor: pointer; font-size: 15px; font-weight: bold; display: block; text-align: center; }}
        </style>
        
        <div class="no-print-zone" style="text-align:center; margin-bottom:20px;">
            <button class="print-trigger-btn" onclick="window.print()">🖨️ إصدار وطباعة الفاتورة الثلاثية فوراً (A5)</button>
        </div>

        <div class="invoice-page">
            <div class="invoice-header">
                <h3>📋 نسخة العميل (أصل الفاتورة)</h3>
                <h1>🏢 {sh_name}</h1>
                <p>العنوان: {sh_address}</p>
                <p style="font-size: 12px; font-weight: bold;">📞 رقم الاستعلام والدعم: {sh_phone}</p>
            </div>
            <table class="invoice-details-table">
                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
                <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>الهاتف:</b> {phone if phone else 'غير محدد'}</td></tr>
                <tr><td><b>العنوان:</b> {address if address else 'غير محدد'}</td><td><b>المسؤول:</b> {user}</td></tr>
                <tr><td><b>نوع الدفع:</b> {pay_type}</td><td><b>إجمالي البنود:</b> {subtotal_amount} جنيه</td></tr>
                <tr><td><b>الخصم النقدي المباشر:</b> <span style="color:red; font-weight:bold;">{cash_discount} جنيه</span></td><td><b>الصافي النهائي المطلوب:</b> <span style="color:blue; font-weight:bold;">{total_invoice_amount} جنيه</span></td></tr>
                {collect_info}
            </table>
            <table class="invoice-items-table">
                {standard_table_th}
                {standard_table_td}
            </table>
            <div class="total-words-area">💰 إجمالي المبلغ باللغة العربية: <span style="color:#000;">{arabic_total_words}</span></div>
            <div class="invoice-footer-alert">⚠️ تنبيه: مدة الاستبدال والارتجاع 15 يوماً من تاريخ الفاتورة بشرط سلامة الغلاف الأصلي.</div>
        </div>

        <div class="invoice-page">
            <div class="invoice-header">
                <h3>📋 نسخة الإدارة المالية والحسابات</h3>
                <h1>🏢 {sh_name}</h1>
                <p>العنوان: {sh_address}</p>
            </div>
            <table class="invoice-details-table">
                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
                <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>الهاتف:</b> {phone if phone else 'غير محدد'}</td></tr>
                <tr><td><b>نوع الدفع:</b> {pay_type}</td><td><b>المسؤول:</b> {user}</td></tr>
                <tr><td><b>الخصم النقدي:</b> {cash_discount} جنيه</td><td><b>الصافي النهائي:</b> {total_invoice_amount} جنيه</td></tr>
                {collect_info}
            </table>
            <table class="invoice-items-table">
                {standard_table_th}
                {standard_table_td}
            </table>
            <div class="total-words-area">💰 إجمالي المبلغ باللغة العربية: <span style="color:#000;">{arabic_total_words}</span></div>
        </div>

        <div class="invoice-page">
            <div class="invoice-header">
                <h3>📦 نسخة مسؤول المخازن والصرف</h3>
                <h1>🏢 {sh_name}</h1>
                <p>التوجيه: يرجى صرف الأصناف المبينة أدناه لمستلم الفاتورة</p>
            </div>
            <table class="invoice-details-table">
                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
                <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>المسؤول المصدر:</b> {user}</td></tr>
                <tr><td><b>نوع الدفع:</b> {pay_type}</td><td><b>حالة الإذن:</b> جاهز للصرف</td></tr>
            </table>
            <table class="invoice-items-table">
                {store_table_th}
                {store_table_td}
            </table>
            <div class="invoice-footer-alert" style="margin-top:40px;">توقيع أمين المخزن: ............................ | توقيع المستلم: ............................</div>
        </div>
    </div>
    """
    return html_content

def get_download_link(html_content, filename="invoice.html"):
    b64 = base64.b64encode(html_content.encode('utf-8-sig')).decode()
    return f'<div class="download-btn-area"><a href="data:text/html;base64,{b64}" download="{filename}" style="display: block; padding: 12px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px; font-weight: bold; text-align: center; margin: 15px auto; max-width:400px;">📥 اضغط هنا لتنزيل وحفظ ملف الفاتورة في التحميلات فوراً</a></div>'

if not st.session_state.auth:
    st.title(f"🏢 نظام {SHOWROOM_NAME} - تسجيل الدخول")
    user_input = st.text_input("اسم المستخدم", key="login_user").strip()
    pw_input = st.text_input("كلمة المرور", type="password", key="login_pw").strip()
    
    if st.button("دخول للنظام", use_container_width=True):
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
    st.sidebar.write(f"الرتبة: **{st.session_state.role}**")
    
    choice = st.sidebar.radio("📋 الأقسام الرئيسية للنظام:", sidebar_pages)
    
    inv_df = st.session_state.inv_df
    sales_df = st.session_state.sales_df
    returns_df = st.session_state.returns_df
    purchases_df = st.session_state.purchases_df
    exp_df = st.session_state.exp_df
    att_df = st.session_state.att_df
    contacts_df = st.session_state.contacts_df
    collections_df = st.session_state.collections_df

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.session_state.cart = []
        st.rerun()

    def safe_item_format(x):
        if inv_df.empty: return str(x)
        match = inv_df[inv_df['كود الصنف'] == x]['اسم الصنف'].values
        return f"{x} - {match[0]}" if len(match) > 0 else f"{x} - (صنف غير معروف)"

    # --- 1. صفحة إدارة الأصناف ---
    if "إدارة الأصناف والمخزن" in choice:
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
                    st.success("🚀 تم دمج وحفظ البيانات في رصيد أول المدة بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ فشل الدمج: تأكد من احتواء العناوين الملصوقة أو المرفوعة على حقل 'كود الصنف'.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء ترحيل البيانات: {e}")

        with t_paste:
            st.markdown("💡 **انسخ البيانات من جداول الـ Excel بالكامل (بما فيها صف العناوين الرئيسي) ثم الصقها بالأسفل:**")
            pasted_input = st.text_area("قم باللصق هنا (Ctrl + V)", height=250, placeholder="كود الصنف\tاسم الصنف\tتصنيف الصنف...")
            if pasted_input.strip():
                try:
                    paste_df = pd.read_csv(StringIO(pasted_input), sep="\t")
                    st.write("🔍 **معاينة حية للبيانات التي قمت بلصقها:**")
                    st.dataframe(paste_df, use_container_width=True)
                    if st.button("🚀 ترحيل وحفظ البيانات الملصوقة فوراً بالقاعدة"):
                        process_and_merge_data(paste_df)
                except Exception as ex:
                    st.error(f"🚨 عذراً، لم نتمكن من تحليل النص الملصوق. تأكد من نسخ جدول Excel كامل بالعناوين بشكل صحيح: {ex}")

        with t_file:
            st.info("💡 تأكد أن ملف الـ Excel يحتوي على الأعمدة التالية ليعمل بشكل سليم: (كود الصنف، اسم الصنف، تصنيف الصنف، نوع الوحدة، موقع المخزن، الكمية، سعر الشراء، سعر البيع)")
            uploaded_file = st.file_uploader("اختر شيت الاكسل الخاص بالبضائع", type=["xlsx", "xls"])
            if uploaded_file is not None:
                try:
                    excel_df = pd.read_excel(uploaded_file, dtype={"كود الصنف": str})
                    st.dataframe(excel_df)
                    if st.button("تأكيد ودمج الملف في رصيد أول المدة"):
                        process_and_merge_data(excel_df)
                except Exception as e: st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")

    # --- 3. صفحة حالة المخزن ---
    elif "حالة المخزن" in choice:
        st.header("🔍 جرد بضائع المخزن الحالية ومواقع تواجدها")
        st.dataframe(inv_df, use_container_width=True)

    # --- 4. صفحة العملاء والموردين و كشف الحساب المتطور ---
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
            st.subheader("🔍 استخراج كشف الحساب وسندات السداد للعملاء")
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
                
                st.subheader("💳 تسجيل سند تحصيل / دفعة سداد جديدة للعميل")
                col_pay1, col_pay2, col_pay3 = st.columns(3)
                pay_amt = col_pay1.number_input("المبلغ المدفوع (جنيه)", min_value=0.0, step=50.0)
                pay_method = col_pay2.selectbox("طريقة السداد", ["نقدي خزينة", "حوالة فودافون كاش", "فيزا / شبكة", "شيك بنكي"])
                pay_notes = col_pay3.text_input("ملاحظات السداد", placeholder="مثال: سداد قسط أسبوعي")
                
                if st.button("💵 تأكيد وترحيل السند لحساب العميل", use_container_width=True):
                    if pay_amt <= 0:
                        st.error("يرجى إدخال مبلغ تحصيل صحيح أكبر من الصفر.")
                    else:
                        coll_id = "REC-" + str(int(datetime.now().timestamp()))
                        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_coll = pd.DataFrame([{
                            "رقم السند": coll_id, "التاريخ": current_time_str, "اسم العميل": selected_cust,
                            "المبلغ المحصل": pay_amt, "طريقة السداد": pay_method, "ملاحظات": pay_notes, "المسؤول": st.session_state.user
                        }])
                        st.session_state.collections_df = pd.concat([collections_df, new_coll], ignore_index=True)
                        st.session_state.collections_df.to_csv(COLLECTIONS_FILE, index=False, encoding='utf-8-sig')
                        st.success(f"🎉 تم تسجيل السند {coll_id} بنجاح وخصمه من حساب العميل!")
                        
                        new_debt_after_pay = current_debt - pay_amt
                        msg_text = f"عزيزي العميل: {selected_cust}\n" \
                                   f"تم استلام مبلغ: {pay_amt} جنيهاً مصرياً بحسابكم بطريقة ({pay_method}).\n" \
                                   f"رقم الحركة: {coll_id}\n" \
                                   f"التاريخ: {current_time_str}\n" \
                                   f"المديونية المتبقية بذمتكم هي: {new_debt_after_pay:,.2f} جنيه.\n" \
                                   f"شكراً لتعاملكم مع {SHOWROOM_NAME}."
                        
                        st.info(f"📨 تم إرسال رسالة نصية تفصيلية إلى رقم هاتف العميل ({cust_phone if cust_phone else 'غير مسجل'}):\n\n \"{msg_text}\"")
                        if cust_phone and cust_phone != "nan" and cust_phone != "":
                            clean_phone = cust_phone
                            if clean_phone.startswith("0"): clean_phone = "2" + clean_phone
                            encoded_msg = urllib.parse.quote(msg_text)
                            whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
                            st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display: block; width: 100%; text-align: center; background-color: #25D366; color: white; padding: 12px; font-weight: bold; text-decoration: none; border-radius: 5px; margin-top: 10px;">🟢 اضغط هنا لفتح وتأكيد إرسال رسالة الـ WhatsApp للعميل فوراً</a>', unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ لم يتم توليد رابط واتساب لعدم وجود رقم هاتف صحيح مسجل بملف العميل.")
                        if st.button("🔄 تحديث الصفحة بعد إرسال الرسالة"):
                            st.rerun()

    # --- 5. صفحة فواتير الشراء ---
    elif "حركة فواتير الشراء" in choice:
        st.header("📥 حركة فواتير الشراء وتوريد البضائع للمخازن")
        c1, c2, c3 = st.columns(3)
        p_id = c1.text_input("رقم فاتورة الشراء / المورد").strip()
        p_sup = c2.text_input("اسم المورد / الشركة المصنعة").strip()
        p_code = c3.selectbox("اختر الصنف الوارد لتوريده للمخزن", inv_df["كود الصنف"].values if not inv_df.empty else [], format_func=safe_item_format)
        
        c4, c5 = st.columns(2)
        p_qty = c4.number_input("الكمية الموردة", min_value=1, step=1)
        p_cost = c5.number_input("سعر الشراء الفعلي المعتمد لهذه الشحنة (للوحدة)", min_value=0.0, step=10.0)
        
        if st.button("📥 ترحيل الفاتورة وزيادة كميات جرد المخزن فوراً"):
            if p_id and p_sup and p_code:
                match_idx = inv_df[inv_df["كود الصنف"] == p_code].index[0]
                st.session_state.inv_df.at[match_idx, "الكمية"] += int(p_qty)
                st.session_state.inv_df.at[match_idx, "سعر الشراء"] = float(p_cost)
                st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                
                new_p = pd.DataFrame([{
                    "رقم الفاتورة": p_id, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "المورد": p_sup, "كود الصنف": p_code, "الصنف": inv_df.at[match_idx, "اسم الصنف"],
                    "تصنيف الصنف": inv_df.at[match_idx, "تصنيف الصنف"], "نوع الوحدة": inv_df.at[match_idx, "نوع الوحدة"],
                    "موقع المخزن": inv_df.at[match_idx, "موقع المخزن"], "سعر الشراء المعتمد": p_cost,
                    "الكمية": p_qty, "إجمالي الشراء": p_qty * p_cost, "المسؤول": st.session_state.user
                }])
                st.session_state.purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                st.success("🎉 تم تسجيل فاتورة الشراء وزيادة بضائع المخزن وتعديل سعر الشراء الافتراضي بنجاح!")
                st.rerun()

    # --- 6. صفحة حركة فواتير البيع وتعديل إدخال بند الخصم بالجنيه ---
    elif "حركة فواتير البيع" in choice:
        st.header("📤 شاشة كاشير المبيعات المتطورة وإصدار الفواتير الثلاثية")
        
        st.subheader("👤 أولاً: بيانات العميل ونظام الفاتورة")
        sc1, sc2, sc3 = st.columns(3)
        c_name = sc1.text_input("اسم العميل الثلاثي", value=st.session_state.form_sale_cust_name).strip()
        c_phone = sc2.text_input("رقم الهاتف", value=st.session_state.form_sale_cust_phone).strip()
        c_address = sc3.text_input("العنوان بالتفصيل", value=st.session_state.form_sale_cust_address).strip()
        
        sc4, sc5, sc6 = st.columns(3)
        pay_type = sc4.selectbox("نوع البيع وسياسة الدفع", ["نقدي (كاش)", "آجل (على الحساب)"])
        collect_system = sc5.selectbox("نظام تحصيل الآجل (في حال تم اختيار نظام آجل فقط)", ["أسبوعي", "شهري", "دفعات غير منتظمة", "كاش بالكامل لاحقاً"])
        collect_date = sc6.date_input("تاريخ استحقاق وتحصيل القسط / المبلغ")
        
        st.markdown("---")
        st.subheader("🛒 ثانياً: إضافة البضائع لسلة المبيعات الحالية")
        
        cc1, cc2, cc3 = st.columns(3)
        sale_code = cc1.selectbox("اختر المنتج من الجرد الحركي المتاح", inv_df["كود الصنف"].values if not inv_df.empty else [], format_func=safe_item_format)
        
        if sale_code:
            match_row = inv_df[inv_df["كود الصنف"] == sale_code].iloc[0]
            max_qty = int(match_row["الكمية"])
            default_price = float(match_row["سعر البيع"])
            st.info(f"📦 المخزون الحالي المتاح لهذا المنتج: {max_qty} {match_row['نوع الوحدة']} | سعر البيع الافتراضي المقترح: {default_price} جنيه")
            
            sale_qty = cc2.number_input("الكمية المطلوبة للبيع", min_value=1, max_value=max_qty if max_qty > 0 else 1, step=1)
            custom_price = cc3.number_input("سعر وحدة البيع الفعلي المقترح والمعدل", value=default_price, min_value=0.0)
            
            cc4 = st.columns(1)[0]
            item_discount = cc4.number_input("نسبة الخصم الممنوحة على هذا الصنف فقط (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            
            if st.button("➕ إضافة البند المحدد للسلة"):
                if max_qty <= 0:
                    st.error("❌ عذراً، لا يمكن إتمام إضافة البند لعدم توفر رصيد حركي كافٍ بالمخازن لهذا الصنف.")
                else:
                    g_total = sale_qty * custom_price
                    f_total = g_total * (1 - (item_discount / 100.0))
                    
                    st.session_state.cart.append({
                        "item_code": sale_code, "item_name": match_row["اسم الصنف"],
                        "category": match_row["تصنيف الصنف"], "unit": match_row["نوع الوحدة"],
                        "warehouse_loc": match_row["موقع المخزن"], "qty": sale_qty,
                        "price": custom_price, "discount": item_discount,
                        "gross_total": g_total, "final_total": f_total, "purchase_price": match_row["سعر الشراء"]
                    })
                    st.success(f"تم إدراج الصنف [{match_row['اسم الصنف']}] بنجاح داخل السلة الحالية!")
                    st.rerun()

        if st.session_state.cart:
            st.markdown("---")
            st.subheader("📋 البنود الحالية المدرجة في سلة الفاتورة")
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df[["item_code", "item_name", "qty", "price", "discount", "final_total"]], use_container_width=True)
            
            if st.button("🗑️ تفريغ وإلغاء كافة بنود السلة"):
                st.session_state.cart = []
                st.rerun()
                
            st.markdown("---")
            st.subheader("💰 ثالثاً: الحسابات الختامية والخصم المباشر")
            subtotal_cart = cart_df["final_total"].sum()
            st.metric("إجمالي البنود قبل الخصم النقدي", f"{subtotal_cart:,.2f} جنيه")
            
            # بند الخصم الجديد بالأرقام بالجنيه على إجمالي الفاتورة
            cash_discount = st.number_input("💸 إضافة قيمة خصم نقدي مباشرة بالجنيه على الفاتورة ككل", min_value=0.0, max_value=float(subtotal_cart), value=0.0, step=5.0)
            
            final_invoice_total = max(0.0, subtotal_cart - cash_discount)
            st.subheader(f"الصافي النهائي المطلوب سداده: {final_invoice_total:,.2f} جنيه")
            
            sc_paid, sc_rem = 0.0, 0.0
            if pay_type == "آجل (على الحساب)":
                cx1, cx2 = st.columns(2)
                sc_paid = cx1.number_input("المبلغ المدفوع كـ مقدم تعاقد (جنيه)", min_value=0.0, max_value=float(final_invoice_total), value=0.0)
                sc_rem = final_invoice_total - sc_paid
                cx2.metric("المتبقي بالذمة كـ دين آجل للعميل", f"{sc_rem:,.2f} جنيه")
                
            if st.button("🚀 ترحيل وحفظ وبناء الفاتورة الثلاثية الفورية المتطورة", use_container_width=True):
                if not c_name:
                    st.error("يرجى ملء حقل اسم العميل لإصدار الفاتورة بشكل صحيح وقانوني.")
                else:
                    inv_id = "INV-" + str(int(datetime.now().timestamp()))
                    dt_now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    sales_records = []
                    for item in st.session_state.cart:
                        match_idx = inv_df[inv_df["كود الصنف"] == item["item_code"]].index[0]
                        st.session_state.inv_df.at[match_idx, "الكمية"] -= int(item["qty"])
                        
                        cost_all = item["qty"] * item["purchase_price"]
                        # توزيع الخصم النقدي بنسبة وتناسب على الأصناف للحفاظ على دقة الأرباح
                        item_ratio = item["final_total"] / subtotal_cart if subtotal_cart > 0 else 0
                        allocated_discount = cash_discount * item_ratio
                        item_net_sale = item["final_total"] - allocated_discount
                        net_profit = item_net_sale - cost_all
                        
                        sales_records.append({
                            "رقم الفاتورة": inv_id, "التاريخ": dt_now_str, "اسم العميل": c_name,
                            "هاتف العميل": c_phone, "العنوان": c_address, "نوع البيع": pay_type,
                            "نظام التحصيل": collect_system if pay_type == "آجل (على الحساب)" else "نقدي",
                            "تاريخ التحصيل": str(collect_date) if pay_type == "آجل (على الحساب)" else "نقدي",
                            "المدفوع مقدم": sc_paid, "المتبقي": sc_rem, "كود الصنف": item["item_code"],
                            "الصنف": item["item_name"], "تصنيف الصنف": item["category"], "نوع الوحدة": item["unit"],
                            "موقع المخزن": item["warehouse_loc"], "الكمية": item["qty"], "سعر الوحدة": item["price"],
                            "الخصم %": item["discount"], "إجمالي البيع": item_net_sale, "تكلفة الشراء الإجمالية": cost_all,
                            "صافي ربح الفاتورة": net_profit, "المسؤول": st.session_state.user, "الخصم النقدي": allocated_discount
                        })
                        
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    new_sales_df = pd.DataFrame(sales_records)
                    st.session_state.sales_df = pd.concat([sales_df, new_sales_df], ignore_index=True)
                    st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success(f"🎉 تم ترحيل وحفظ وتثبيت الفاتورة بنجاح بالرقم الفوري: {inv_id}")
                    
                    invoice_html = generate_triple_invoice_html(
                        inv_id, dt_now_str, c_name, c_phone, c_address, pay_type,
                        collect_system, str(collect_date), sc_paid, sc_rem,
                        st.session_state.user, st.session_state.cart,
                        SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, cash_discount
                    )
                    
                    st.components.v1.html(invoice_html, height=1400, scrolling=True)
                    st.markdown(get_download_link(invoice_html, f"invoice_{inv_id}.html"), unsafe_allow_html=True)
                    
                    st.session_state.cart = []
                    st.session_state.form_sale_cust_name = ""
                    st.session_state.form_sale_cust_phone = ""
                    st.session_state.form_sale_cust_address = ""

    # --- 7. صفحة ارتجاع فواتير البيع مضافاً إليها بند تعديل الصنف وتغيير سعر الشراء ---
    elif "ارتجاع فواتير البيع" in choice:
        st.header("↩️ شاشة إدارة المرتجعات وتعديل أسعار شراء البضائع")
        
        rc1, rc2 = st.columns(2)
        r_invoice_id = rc1.text_input("ادخل رقم فاتورة البيع الأصلية المراد الإرجاع منها").strip()
        r_cust_name = rc2.text_input("اسم العميل الحالي للتوثيق ماليًا").strip()
        
        if r_invoice_id:
            matched_sales = sales_df[sales_df["رقم الفاتورة"] == r_invoice_id]
            if matched_sales.empty:
                st.warning("⚠️ رقم هذه الفاتورة غير مدرج في سجلات البيع المعتمدة بالنظام.")
            else:
                st.subheader("📦 الأصناف والكميات المباعة في الفاتورة المحددة")
                st.dataframe(matched_sales[["كود الصنف", "الصنف", "الكمية", "سعر الوحدة", "إجمالي البيع"]], use_container_width=True)
                
                st.markdown("---")
                st.subheader("🔄 تحديد البيانات المرتجعة وتحديث مواصفات البند")
                
                rx1, rx2 = st.columns(2)
                r_code = rx1.selectbox("اختر البند المرتجع لتعديله وإعادته للمخزن", matched_sales["كود الصنف"].values, format_func=lambda x: f"{x} - {matched_sales[matched_sales['كود الصنف']==x]['الصنف'].values[0]}")
                
                item_sale_row = matched_sales[matched_sales["كود الصنف"] == r_code].iloc[0]
                max_ret_qty = int(item_sale_row["الكمية"])
                
                r_qty = rx2.number_input(f"الكمية المرتجعة الفعلية (الحد الأقصى المسموح به {max_ret_qty})", min_value=1, max_value=max_ret_qty, step=1)
                
                # بند إضافي جديد لتحديث الصنف وتغيير سعر الشراء فورياً
                match_inv_row = inv_df[inv_df["كود الصنف"] == r_code].iloc[0]
                st.info(f"💡 سعر الشراء الحالي الافتراضي المسجل للمنتج بالمخزن هو: {match_inv_row['سعر الشراء']} جنيه.")
                
                new_purchase_price = st.number_input("✏️ تعديل وتغيير سعر الشراء المعتمد لهذا الصنف بالمخازن (جنيه)", min_value=0.0, value=float(match_inv_row['سعر الشراء']), step=1.0)
                
                unit_refund = float(item_sale_row["سعر الوحدة"]) * (1 - (float(item_sale_row["الخصم %"]) / 100.0))
                total_refund_amt = r_qty * unit_refund
                
                st.subheader(f"💵 المبلغ المستحق رده للعميل فوراً: {total_refund_amt:,.2f} جنيه")
                
                if st.button("↩️ تأكيد الارتجاع النهائي وتحديث أسعار الشراء للأصناف"):
                    # 1. إرجاع الكمية للمخزن وتحديث سعر الشراء المدخل
                    inv_match_idx = inv_df[inv_df["كود الصنف"] == r_code].index[0]
                    st.session_state.inv_df.at[inv_match_idx, "الكمية"] += int(r_qty)
                    st.session_state.inv_df.at[inv_match_idx, "سعر الشراء"] = float(new_purchase_price)
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    # 2. تسجيل الفاتورة في المردودات
                    ret_id = "RET-" + str(int(datetime.now().timestamp()))
                    new_ret = pd.DataFrame([{
                        "رقم الإرجاع": ret_id, "رقم الفاتورة الأصلية": r_invoice_id,
                        "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "اسم العميل": r_cust_name if r_cust_name else item_sale_row["اسم العميل"],
                        "كود الصنف": r_code, "الصنف": item_sale_row["الصنف"], "الكمية المرجعة": r_qty,
                        "المبلغ المردود": total_refund_amt, "المسؤول": st.session_state.user
                    }])
                    st.session_state.returns_df = pd.concat([returns_df, new_ret], ignore_index=True)
                    st.session_state.returns_df.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success("🎉 تم تسجيل عملية المردودات بنجاح، وإعادة الكمية للمخزن، وتحديث وتثبيت سعر الشراء الجديد للصنف كلياً!")
                    st.rerun()

    # --- 8. صفحة البحث وطباعة الفواتير ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 البحث عن الفواتير القديمة وإعادة طباعتها فوراً")
        search_id = st.text_input("ادخل رقم الفاتورة للبحث عنها (INV-XXXX)").strip()
        if search_id:
            f_sales = sales_df[sales_df["رقم الفاتورة"] == search_id]
            if f_sales.empty: st.warning("لا توجد فاتورة مسجلة بهذا الرقم.")
            else:
                first_row = f_sales.iloc[0]
                st.write(f"**اسم العميل:** {first_row['اسم العميل']} | **التاريخ:** {first_row['التاريخ']} | **المسؤول:** {first_row['المسؤول']}")
                st.dataframe(f_sales[["كود الصنف", "الصنف", "الكمية", "سعر الوحدة", "إجمالي البيع"]])
                
                re_cart = []
                for _, r in f_sales.iterrows():
                    re_cart.append({
                        "item_name": r["الصنف"], "category": r.get("تصنيف الصنف", "عام"), "unit": r.get("نوع الوحدة", "قطعة"),
                        "warehouse_loc": r.get("موقع المخزن", "الرئيسي"), "qty": int(r["الكمية"]), "price": float(r["سعر الوحدة"]),
                        "discount": float(r["الخصم %"]), "final_total": float(r["إجمالي البيع"])
                    })
                
                cash_discount_val = float(first_row.get("الخصم النقدي", 0.0))
                
                if st.button("🖨️ توليد وإصدار أمر طباعة جديد للفاتورة"):
                    invoice_html = generate_triple_invoice_html(
                        search_id, first_row['التاريخ'], first_row['اسم العميل'], first_row['هاتف العميل'], first_row['العنوان'],
                        first_row['نوع البيع'], first_row['نظام التحصيل'], first_row['تاريخ التحصيل'], first_row['المدفوع مقدم'],
                        first_row['المتبقي'], first_row['المسؤول'], re_cart, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, cash_discount_val
                    )
                    st.components.v1.html(invoice_html, height=1400, scrolling=True)

    # --- 9. صفحة التقارير والأرباح ---
    elif "تقارير البيع والشراء والأرباح" in choice:
        st.header("📈 التقارير المالية التفصيلية وحسابات الأرباح والخسائر المعرض")
        s_total = pd.to_numeric(sales_df["إجمالي البيع"], errors='coerce').sum()
        p_total = pd.to_numeric(purchases_df["إجمالي الشراء"], errors='coerce').sum()
        e_total = pd.to_numeric(exp_df["المبلغ"], errors='coerce').sum()
        r_total = pd.to_numeric(returns_df["المبلغ المردود"], errors='coerce').sum() if not returns_df.empty else 0.0
        
        gross_profit = pd.to_numeric(sales_df["صافي ربح الفاتورة"], errors='coerce').sum()
        net_profit_total = gross_profit - e_total - r_total
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🛒 صافي المبيعات الإجمالي", f"{s_total:,.2f} جنيه")
        c2.metric("📥 مشتريات وتوريدات البضائع", f"{p_total:,.2f} جنيه")
        c3.metric("💸 مصاريف ونثريات التشغيل", f"{e_total:,.2f} جنيه")
        c4.metric("↩️ إجمالي قيم المردودات", f"{r_total:,.2f} جنيه")
        
        d1, d2 = st.columns(2)
        d1.metric("📊 مجمل الربح التجاري للبضاعة", f"{gross_profit:,.2f} جنيه")
        d2.metric("🏁 صافي الأرباح النهائي للمعرض", f"{net_profit_total:,.2f} جنيه")

    # --- 10. صفحة المصاريف ---
    elif "المصاريف" in choice:
        st.header("💸 إدارة وتقييد المصاريف اليومية والنثريات الخزينة")
        st.dataframe(exp_df, use_container_width=True)
        c1, c2 = st.columns(2)
        ex_label = c1.text_input("بيان المنصرف / وجهة الصرف").strip()
        ex_val = c2.number_input("المبلغ المنصرف (جنيه)", min_value=0.0, step=10.0)
        if st.button("💾 ترحيل البند للمصاريف"):
            if ex_label and ex_val > 0:
                new_ex = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "البيان": ex_label, "المبلغ": ex_val, "المسؤول": st.session_state.user}])
                st.session_state.exp_df = pd.concat([exp_df, new_ex], ignore_index=True)
                st.session_state.exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم حفظ البند وخصمه من مجمل الأرباح بنجاح!")
                st.rerun()

    # --- 11. صفحة الحضور والانصراف ---
    elif "الحضور والانصراف" in choice:
        st.header("⏰ نظام تسجيل حضور وانصراف موظفي وعمال المعرض")
        st.dataframe(att_df, use_container_width=True)
        c1, c2 = st.columns(2)
        if c1.button("⏰ تسجيل بصمة حضور الآن", use_container_width=True):
            new_att = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "وقت الحضور": datetime.now().strftime("%H:%M:%S"), "وقت الانصراف": "لم ينصرف بعد"}])
            st.session_state.att_df = pd.concat([att_df, new_att], ignore_index=True)
            st.session_state.att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
            st.success("🎉 تم تسجيل حضورك بنجاح! يوم سعيد عمل موفق.")
            st.rerun()
        if c2.button("⏰ تسجيل بصمة انصراف الآن", use_container_width=True):
            today_str = datetime.now().strftime("%Y-%m-%d")
            match = att_df[(att_df["الموظف"] == st.session_state.user) & (att_df["التاريخ"] == today_str)]
            if not match.empty:
                last_idx = match.index[-1]
                st.session_state.att_df.at[last_idx, "وقت الانصراف"] = datetime.now().strftime("%H:%M:%S")
                st.session_state.att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم تسجيل انصرافك بنجاح! في رعاية الله.")
                st.rerun()
            else: st.error("عذراً، لم يتم العثور على حركة حضور مسجلة لك اليوم لإتمام الانصراف عليها.")

    # --- 12. صفحة الصلاحيات والمستخدمين ---
    elif "إدارة وتعديل الصلاحيات والحسابات" in choice:
        st.header("⚙️ لوحة التحكم بالحسابات والقواعد التفصيلية")
        tab_users, tab_roles = st.tabs(["👥 حسابات الموظفين", "🔑 الصلاحيات والموقع"])
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        
        with tab_users:
            st.dataframe(u_df, use_container_width=True)
            with st.form("add_user_form"):
                st.subheader("➕ إنشاء حساب مستخدم جديد")
                new_u = st.text_input("اسم المستخدم الجديد").strip()
                new_p = st.text_input("كلمة المرور السرية").strip()
                new_r = st.selectbox("الرتبة الممنوحة له", ["مدير", "مشرف", "موظف"])
                if st.form_submit_button("💾 تكويد الحساب"):
                    if new_u and new_p:
                        if new_u in u_df["username"].values: st.error("المستخدم موجود مسبقاً.")
                        else:
                            added_u = pd.DataFrame([{"username": new_u, "password": new_p, "role": new_r}])
                            pd.concat([u_df, added_u]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                            st.success("🚀 تم الحفظ!")
                            st.rerun()
            st.markdown("---")
            st.subheader("🗑️ حذف حساب من القاعدة")
            del_user_target = st.selectbox("اختر الحساب المراد إزالته", u_df["username"].values)
            if st.button("🔥 حذف الحساب المختار نهائياً"):
                if del_user_target == "admin":
                    st.error("❌ لا يمكن حذف الحساب الرئيسي للمدير الأساسي للنظام (admin)!")
                else:
                    updated_users = u_df[u_df["username"] != del_user_target]
                    updated_users.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                    st.success("🗑️ تم حذف الحساب من السجلات بنجاح!")
                    st.rerun()

        with tab_roles:
            st.subheader("🔑 جدول التحكم التفاعلي بالصفحات")
            edited_perms_df = st.data_editor(perms_df, use_container_width=True, disabled=["اسم الصفحة"])
            if st.button("💾 حفظ الصلاحيات والتعديلات الجديدة"):
                edited_perms_df.to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')
                st.success("🚀 تم تحديث قواعد الصلاحيات!")
                st.rerun()

    # --- 13. صفحة إعدادات بيانات الفاتورة والدعم ---
    elif "⚙️ إعدادات بيانات الفاتورة والدعم" in choice:
        st.header("⚙️ تحديث وإعداد بيانات طباعة الفاتورة والدعم")
        with st.form("settings_form_updated"):
            new_showroom_name = st.text_input("اسم المعرض / الشركة بالفاتورة", value=SHOWROOM_NAME)
            new_showroom_address = st.text_input("العنوان بالتفصيل بالفاتورة", value=SHOWROOM_ADDRESS)
            new_inquiry_number = st.text_input("رقم الدعم الفني للفواتير", value=INQUIRY_NUMBER)
            if st.form_submit_button("💾 حفظ وتحديث الإعدادات"):
                updated_settings = pd.DataFrame([{"اسم المعرض": new_showroom_name, "العنوان": new_showroom_address, "رقم الدعم": new_inquiry_number}])
                updated_settings.to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم تحديث بيانات لوحة الفاتورة والاتصال!")
                st.rerun()
