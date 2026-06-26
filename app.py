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
        pd.DataFrame([{"اسم المعرض": "معرض الكبير", "العنوان": "ابوحماد - قرية العراقي - بجوار مدرسة الشهيد صلاح فتحي", "رقم الدعم": "0100XXXXXXX"}]).to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')

    all_pages = [
        "📦 إدارة الأصناف والمخزن", "📊 رصيد أول المدة Excel", "🔍 حالة المخزن", 
        "🤝 العملاء والموردين", "📥 حركة فواتير الشراء والتعديل", "📤 حركة فواتير البيع", 
        "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "📈 تقارير البيع والشراء والأرباح", "💸 المصاريف", 
        "⏰ الحضور والانصراف", "⚙️ إدارة وتعديل الصلاحيات والحسابات", "⚙️ إعدادات بيانات الفاتورة والدعم"
    ]
    
    if not os.path.exists(PERMISSIONS_FILE):
        default_perms = []
        for page in all_pages:
            default_perms.append({
                "اسم الصفحة": page, 
                "مدير": True, 
                "مشرف": True if page in ["🔍 حالة المخزن", "📥 حركة فواتير الشراء والتعديل", "📤 حركة فواتير البيع", "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"] else False, 
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

# تهيئة متغيرات حفظ الحالة للتنقل بدون فقدان البيانات وتثبيتها في الـ Session State
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
    
    standard_table_th = "<thead><tr><th>الصنف والبيان</th><th>التصنيف</th><th>الوحدة</th><th>الكمية</th><th>سعر المفرد</th><th>الخصم</th><th>الصافي الإجمالي</th></tr></thead>"
    standard_table_td = "<tbody>"
    for item in cart_items:
        standard_table_td += f"<tr><td>{item['item_name']}</td><td>{item.get('category', 'عام')}</td><td>{item.get('unit', 'قطعة')}</td><td>{item['qty']}</td><td>{item['price']} جنيه</td><td>{item['discount']}%</td><td style='font-weight: bold;'>{item['final_total']} جنيه</td></tr>"
    
    if discount_fixed > 0:
        standard_table_td += f"<tr style='background:#f9f9f9; font-weight:bold;'><td colspan='6' style='text-align:left; padding-left:15px;'>خصم نقدي مباشر على الفاتورة:</td><td style='color:red;'>-{discount_fixed} جنيه</td></tr>"
    standard_table_td += "</tbody>"
    
    store_table_th = "<thead><tr><th>الصنف والبيان</th><th>موقع المخزن</th><th>الكمية المطلوبة للصرف</th></tr></thead>"
    store_table_td = "<tbody>"
    for item in cart_items:
        store_table_td += f"<tr><td style='font-size: 15px; font-weight: bold;'>{item['item_name']} ({item.get('unit', 'قطعة')})</td><td>{item.get('warehouse_loc', 'الرئيسي')}</td><td style='font-size: 16px; font-weight: bold;'>{item['qty']}</td></tr>"
    store_table_td += "</tbody>"

    html_content = f"""
    <div class="triple-print-wrapper">
    
   <style>
    @media print {{
        body {{ 
            direction: rtl !important; 
            background: #fff !important; 
            color: #000 !important; 
            padding: 0 !important; 
            margin: 0 !important; 
        }}
        header, [data-testid="stSidebar"], [data-testid="stHeader"], .no-print-zone, .stButton, .download-btn-area {{ 
            display: none !important; 
        }}
        .triple-print-wrapper {{ 
            display: block !important; 
        }}
        
        .invoice-page {{ 
            width: 100% !important;
            max-width: 100% !important;
            height: auto !important; 
            page-break-after: always !important; 
            page-break-inside: auto !important; 
            border: 2px solid #000 !important;
            margin: 0 0 40px 0 !important;
            padding: 20px !important;
            box-shadow: none !important;
            display: block !important;
        }}

        .invoice-items-table tr {{
            page-break-inside: avoid !important;
            page-break-after: auto !important;
        }}
        
        .invoice-items-table thead {{
            display: table-header-group !important;
        }}
        
        .total-words-area, .invoice-footer-alert {{
            page-break-inside: avoid !important;
        }}
    }}

    .triple-print-wrapper {{ direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; }}
    .invoice-page {{ 
        max-width: 800px; 
        border: 2px solid #000; 
        padding: 20px; 
        margin: 20px auto; 
        background: #fff; 
        color: #000; 
        box-sizing: border-box; 
    }}
    .invoice-header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 10px; }}
    .invoice-header h3 {{ margin: 0; background: #000; color: #fff; padding: 4px 12px; display: inline-block; font-size: 14px; border-radius: 4px; }}
    .invoice-header h1 {{ margin: 6px 0; font-size: 24px; color: #000; font-weight: 700; }}
    .invoice-header p {{ font-size: 12px; margin: 2px 0; color: #000; }}
    .invoice-details-table {{ width: 100%; font-size: 13px; margin-top: 5px; border-bottom: 1px solid #000; padding-bottom: 8px; }}
    .invoice-details-table td {{ padding: 4px 0; width: 50%; }}
    .invoice-items-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; border: 2px solid black; font-size: 13px; text-align: center; }}
    .invoice-items-table th {{ background: #f2f2f2; border: 1px solid black; padding: 8px; font-weight: bold; color: #000; }}
    .invoice-items-table td {{ border: 1px solid black; padding: 8px; }}
    .total-words-area {{ margin-top: 15px; background: #fff; border: 1px dashed #000; padding: 8px; font-size: 14px; font-weight: bold; text-align: right; }}
    .invoice-footer-alert {{ margin-top: 15px; font-size: 11px; font-weight: bold; text-align: center; border: 1px solid #000; padding: 6px; background: #fff; }}
    .print-trigger-btn { background-color: #28a745; color: white; padding: 12px 24px; margin: 10px auto; border: none; border-radius: 5px; cursor: pointer; font-size: 15px; font-weight: bold; display: block; text-align: center; }
</style>
        
        <div class="no-print-zone" style="text-align:center; margin-bottom:20px;">
            <button class="print-trigger-btn" onclick="window.print()">🖨️ إصدار وطباعة الفاتورة الثلاثية فوراً</button>
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
                <tr><td><b>نوع الدفع:</b> {pay_type}</td><td><b>الإجمالي الكلي:</b> {total_invoice_amount} جنيه</td></tr>
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
                <tr><td><b>الإجمالي الكلي:</b> {total_invoice_amount} جنيه</td><td></td></tr>
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
    
    if st.session_state.system_page_choice not in sidebar_pages:
        st.session_state.system_page_choice = sidebar_pages[0]
        
    choice = st.sidebar.radio("📋 الأقسام الرئيسية للنظام:", sidebar_pages, index=sidebar_pages.index(st.session_state.system_page_choice))
    st.session_state.system_page_choice = choice
    
    inv_df = st.session_state.inv_df
    sales_df = st.session_state.sales_df
    returns_df = st.session_state.returns_df
    purchases_df = st.session_state.purchases_df
    exp_df = st.session_state.exp_df
    att_df = st.session_state.att_df
    contacts_df = st.session_state.contacts_df
    collections_df = st.session_state.collections_df

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
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")

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
            all_custs = contacts_df[contacts_df["النوع"] == "عميل"]["الاسم"].unique() if not contacts_df.empty else []
            if len(all_custs) == 0:
                st.info("لم يتم تسجيل أي عملاء في النظام حتى الآن.")
            else:
                selected_cust = st.selectbox("اختر العميل لاستعراض ماليته:", all_custs)
                cust_info = contacts_df[(contacts_df["الاسم"] == selected_cust) & (contacts_df["النوع"] == "عميل")]
                cust_phone = str(cust_info.iloc[0]["الهاتف"]).strip() if not cust_info.empty else ""
                
                cust_sales = sales_df[sales_df["اسم العميل"] == selected_cust] if not sales_df.empty else pd.DataFrame()
                cust_returns = returns_df[returns_df["اسم العميل"] == selected_cust] if not returns_df.empty else pd.DataFrame()
                cust_colls = collections_df[collections_df["اسم العميل"] == selected_cust] if not collections_df.empty else pd.DataFrame()
                
                total_invoiced = pd.to_numeric(cust_sales["إجمالي البيع"], errors='coerce').sum() if not cust_sales.empty else 0.0
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
                with st.form("collection_form"):
                    col_amount = st.number_input("المبلغ المحصل نقداً", min_value=1.0, step=50.0)
                    col_method = st.selectbox("طريقة السداد", ["نقدي خزينة", "تحويل بنكي", "فودافون كاش", "شيك الدفع"])
                    col_notes = st.text_input("ملاحظات / بيان السند")
                    if st.form_submit_button("💾 ترحيل وحفظ سند السداد"):
                        new_slip_id = str(int(datetime.now().timestamp()))
                        new_coll_row = pd.DataFrame([{
                            "رقم السند": new_slip_id,
                            "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "اسم العميل": selected_cust,
                            "المبلغ المحصل": col_amount,
                            "طريقة السداد": col_method,
                            "ملاحظات": col_notes,
                            "المسؤول": st.session_state.user
                        }])
                        st.session_state.collections_df = pd.concat([collections_df, new_coll_row], ignore_index=True)
                        st.session_state.collections_df.to_csv(COLLECTIONS_FILE, index=False, encoding='utf-8-sig')
                        st.success("🎉 تم حفظ وتوثيق سند السداد وجاري تحديث ميزان الحساب!")
                        st.rerun()
                
                if not cust_colls.empty:
                    st.write("📋 **سجل المقبوضات والسندات السابقة للعميل:**")
                    st.dataframe(cust_colls, use_container_width=True)

    # --- 5. حركة فواتير الشراء ---
    elif "حركة فواتير الشراء والتعديل" in choice:
        st.header("📥 تسجيل فواتير وتوريدات الشراء لزيادة المخزون")
        all_suppliers = contacts_df[contacts_df["النوع"] == "مورد"]["الاسم"].unique() if not contacts_df.empty else []
        if len(all_suppliers) == 0:
            st.warning("⚠️ يرجى إضافة مورد واحد على الأقل من قسم 'العملاء والموردين' أولاً.")
        else:
            with st.form("purchase_form"):
                p_id = st.text_input("رقم فاتورة الشراء / إذن الوارد", value=str(int(datetime.now().timestamp())))
                p_sup = st.selectbox("اختر المورد المعني", all_suppliers)
                p_code = st.selectbox("اختر الصنف المراد زيادة كميته", inv_df["كود الصنف"].values, format_func=safe_item_format)
                p_qty = st.number_input("الكمية المشتراة", min_value=1, value=1)
                p_price = st.number_input("سعر شراء الوحدة الفعلي", min_value=0.0, step=1.0)
                
                if st.form_submit_button("📥 ترحيل الفاتورة للمخازن"):
                    idx = inv_df[inv_df["كود الصنف"] == p_code].index[0]
                    st.session_state.inv_df.at[idx, "الكمية"] += int(p_qty)
                    st.session_state.inv_df.at[idx, "سعر الشراء"] = float(p_price)
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    new_p = pd.DataFrame([{
                        "رقم الفاتورة": p_id, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"), "المورد": p_sup,
                        "كود الصنف": p_code, "الصنف": inv_df.at[idx, "اسم الصنف"], "تصنيف الصنف": inv_df.at[idx, "تصنيف الصنف"],
                        "نوع الوحدة": inv_df.at[idx, "نوع الوحدة"], "موقع المخزن": inv_df.at[idx, "موقع المخزن"],
                        "سعر الشراء المعتمد": p_price, "الكمية": p_qty, "إجمالي الشراء": p_qty * p_price, "المسؤول": st.session_state.user
                    }])
                    st.session_state.purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                    st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                    st.success("🎉 تم ترحيل الشراء وزيادة كميات المخزن بنجاح!")
                    st.rerun()

    # --- 6. صفحة حركة فواتير البيع الكاش والآجل ---
    elif "حركة فواتير البيع" in choice:
        st.header("📤 وحدة كاشير إصدار مبيعات وفواتير جديدة")
        
        # اختيار العميل ونظام التنسيق
        c_mode = st.radio("شكل الفاتورة والعميل:", ["عميل سريع (كاش)", "عميل مسجل بالدليل"], horizontal=True)
        c_name, c_phone, c_address = "عميل نقدي سريع", "غير محدد", "غير محدد"
        
        if c_mode == "عميل مسجل بالدليل":
            all_c = contacts_df[contacts_df["النوع"] == "عميل"]["الاسم"].unique() if not contacts_df.empty else []
            if len(all_c) > 0:
                c_name = st.selectbox("اختر العميل المسجل:", all_c)
                c_row = contacts_df[contacts_df["الاسم"] == c_name]
                c_phone = c_row.iloc[0]["الهاتف"] if not c_row.empty else "غير محدد"
                c_address = c_row.iloc[0]["العنوان"] if not c_row.empty else "غير محدد"
            else:
                st.info("لا يوجد عملاء مسجلين، تم إرجاعك للعميل السريع.")
        else:
            cx1, cx2 = st.columns(2)
            c_name = cx1.text_input("اسم العميل السريع", value="عميل نقدي سريع")
            c_phone = cx2.text_input("رقم هاتف العميل")
            
        pay_type = st.selectbox("طبيعة ونظام الفاتورة المالية", ["نقدي (كاش)", "آجل (على الحساب)"])
        coll_sys, coll_date, p_advance, r_bal = "كاش كامل", "فوراً", 0.0, 0.0
        
        if pay_type == "آجل (على الحساب)":
            cx3, cx4 = st.columns(2)
            coll_sys = cx3.text_input("نظام وملاحظات التحصيل", value="أقساط شهرية / دفعات حرة")
            coll_date = cx4.text_input("تاريخ استحقاق المديونية الكاملة", value=datetime.now().strftime("%Y-%m-%d"))
            
        st.markdown("---")
        st.subheader("🛒 سلة المبيعات الحالية والأصناف")
        
        cc1, cc2, cc3, cc4 = st.columns([3, 1, 1, 1])
        b_code = cc1.selectbox("اختر صنف لإضافته للسلة", inv_df["كود الصنف"].values, format_func=safe_item_format)
        match_inv = inv_df[inv_df["كود الصنف"] == b_code]
        
        max_qty = int(match_inv.iloc[0]["الكمية"]) if not match_inv.empty else 0
        st.info(f"الكمية المتوفرة حالياً في المخزن لهذا الصنف: {max_qty}")
        
        b_qty = cc2.number_input("الكمية المطلوبة", min_value=1, max_value=max(1, max_qty), value=1)
        b_disc = cc3.number_input("خصم الوحدة %", min_value=0.0, max_value=100.0, value=0.0)
        
        if cc4.button("➕ إضافة الصنف للسلة", use_container_width=True):
            if max_qty >= b_qty:
                row = match_inv.iloc[0]
                total_one = b_qty * float(row["سعر البيع"])
                final_total = total_one - (total_one * (b_disc / 100.0))
                
                st.session_state.cart.append({
                    "code": b_code, "item_name": row["اسم الصنف"], "category": row["تصنيف الصنف"],
                    "unit": row["نوع الوحدة"], "warehouse_loc": row["موقع المخزن"], "qty": int(b_qty),
                    "price": float(row["سعر البيع"]), "discount": b_disc, "final_total": final_total,
                    "cost": float(row["سعر الشراء"]) * int(b_qty)
                })
                st.success("تم إدراج الصنف بنجاح داخل سلة المبيعات!")
                st.rerun()
            else:
                st.error("🚨 الكمية المتاحة في المخزن غير كافية لإتمام البيع!")
                
        if st.session_state.cart:
            st.write("📋 **محتويات سلة الكاشير الحالية:**")
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df, use_container_width=True)
            
            if st.button("🗑️ تفريغ ومسح السلة بالكامل"):
                st.session_state.cart = []
                st.rerun()
                
            st.markdown("---")
            disc_fixed = st.number_input("خصم نقدي إضافي مباشر على إجمالي الفاتورة (جنيه)", min_value=0.0, value=0.0)
            
            sub_total = cart_df["final_total"].sum()
            grand_total = max(0.0, sub_total - disc_fixed)
            
            if pay_type == "آجل (على الحساب)":
                p_advance = st.number_input("المبلغ المدفوع مقدماً الآن من العميل", min_value=0.0, max_value=float(grand_total), value=0.0)
                r_bal = grand_total - p_advance
                
            st.write(f"💰 **صافي القيمة الإجمالية المطلوبة للفاتورة:** {grand_total:,.2f} جنيهاً مصرياً.")
            
            if st.button("🚀 تأكيد وترحيل الفاتورة وإصدار أمر الطباعة الثلاثي", use_container_width=True):
                inv_number = str(int(datetime.now().timestamp()))
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                new_sales_rows = []
                for item in st.session_state.cart:
                    idx = inv_df[inv_df["كود الصنف"] == item["code"]].index[0]
                    st.session_state.inv_df.at[idx, "الكمية"] -= int(item["qty"])
                    
                    net_profit = item["final_total"] - item["cost"]
                    new_sales_rows.append({
                        "رقم الفاتورة": inv_number, "التاريخ": date_str, "اسم العميل": c_name, "هاتف العميل": c_phone,
                        "العنوان": c_address, "نوع البيع": pay_type, "نظام التحصيل": coll_sys, "تاريخ التحصيل": coll_date,
                        "المدفوع مقدم": p_advance, "المتبقي": r_bal, "كود الصنف": item["code"], "الصنف": item["item_name"],
                        "تصنيف الصنف": item["category"], "نوع الوحدة": item["unit"], "موقع المخزن": item["warehouse_loc"],
                        "الكمية": item["qty"], "سعر الوحدة": item["price"], "الخصم %": item["discount"],
                        "خصم نقدي ثابت": disc_fixed, "إجمالي البيع": grand_total, "تكلفة الشراء الإجمالية": item["cost"],
                        "صافي ربح الفاتورة": net_profit, "المسؤول": st.session_state.user
                    })
                    
                st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                
                updated_sales = pd.concat([sales_df, pd.DataFrame(new_sales_rows)], ignore_index=True)
                st.session_state.sales_df = updated_sales
                st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                
                # توليد كود الطباعة والتحميل
                html_res = generate_triple_invoice_html(inv_number, date_str, c_name, c_phone, c_address, pay_type, coll_sys, coll_date, p_advance, r_bal, st.session_state.user, st.session_state.cart, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, disc_fixed)
                st.markdown(html_res, unsafe_allow_html=True)
                st.markdown(get_download_link(html_res, f"Invoice_{inv_number}.html"), unsafe_allow_html=True)
                
                st.session_state.cart = []
                st.success("🎉 تم تسجيل عملية البيع وخصم الكميات من المخزن!")

    # --- 7. ارتجاع فواتير البيع ---
    elif "ارتجاع فواتير البيع" in choice:
        st.header("↩️ إدارة مرتجعات المبيعات واسترداد البضائع")
        if sales_df.empty:
            st.info("لا توجد مبيعات مسجلة للارتجاع منها.")
        else:
            ret_inv_id = st.selectbox("اختر رقم الفاتورة الأصلية لعمل المرتجع منها:", sales_df["رقم الفاتورة"].unique())
            matching_sales = sales_df[sales_df["رقم الفاتورة"] == ret_inv_id]
            st.write("الأصناف المتواجدة داخل هذه الفاتورة:")
            st.dataframe(matching_sales[["كود الصنف", "الصنف", "الكمية", "إجمالي البيع"]], use_container_width=True)
            
            ret_code = st.selectbox("اختر الصنف المراد إرجاعه للمخزن:", matching_sales["كود الصنف"].unique(), format_func=lambda x: f"{x} - {matching_sales[matching_sales['كود الصنف'] == x]['الصنف'].values[0]}")
            ret_row = matching_sales[matching_sales["كود الصنف"] == ret_code].iloc[0]
            
            ret_qty = st.number_input("الكمية المراد إرجاعها:", min_value=1, max_value=int(ret_row["الكمية"]), value=1)
            refund_amount = st.number_input("المبلغ المالي المردود للعميل:", min_value=0.0, value=float(ret_qty * float(ret_row["سعر الوحدة"])))
            
            if st.button("↩️ تأكيد وحفظ إذن الارتجاع"):
                if ret_code in inv_df["كود الصنف"].values:
                    i_idx = inv_df[inv_df["كود الصنف"] == ret_code].index[0]
                    st.session_state.inv_df.at[i_idx, "الكمية"] += int(ret_qty)
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                new_ret_id = str(int(datetime.now().timestamp()))
                new_ret_row = pd.DataFrame([{
                    "رقم الإرجاع": new_ret_id, "رقم الفاتورة الأصلية": ret_inv_id, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "اسم العميل": ret_row["اسم العميل"], "كود الصنف": ret_code, "الصنف": ret_row["الصنف"],
                    "الكمية المرجعة": ret_qty, "المبلغ المردود": refund_amount, "المسؤول": st.session_state.user
                }])
                st.session_state.returns_df = pd.concat([returns_df, new_ret_row], ignore_index=True)
                st.session_state.returns_df.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
                st.success("🎉 تم قبول المرتجع وإعادة إدخال البضاعة للمخزن وتحديث الحساب المالي!")
                st.rerun()

    # --- 8. البحث وطباعة الفواتير القديمة ---
    elif "البحث عن الفواتيروطباعتها" in choice or "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 محرك البحث وطباعة الفواتير الثلاثية المسجلة مسبقاً")
        if sales_df.empty:
            st.info("لا توجد فواتير مبيعات مسجلة في قاعدة البيانات.")
        else:
            search_id = st.selectbox("اختر أو ابحث برقم الفاتورة لاستخراجها:", sales_df["رقم الفاتورة"].unique())
            f_rows = sales_df[sales_df["رقم الفاتورة"] == search_id]
            f_init = f_rows.iloc[0]
            
            st.write("📋 **تفاصيل الأصناف المسجلة بالفاتورة الحالية:**")
            st.dataframe(f_rows[["كود الصنف", "الصنف", "الكمية", "سعر الوحدة", "الخصم %", "المسؤول"]], use_container_width=True)
            
            re_cart_items = []
            for _, r_item in f_rows.iterrows():
                re_cart_items.append({
                    "item_name": r_item["الصنف"], "category": r_item["تصنيف الصنف"], "unit": r_item["نوع الوحدة"],
                    "qty": r_item["الكمية"], "price": r_item["سعر الوحدة"], "discount": r_item["الخصم %"],
                    "final_total": r_item["الكمية"] * r_item["سعر الوحدة"] - (r_item["الكمية"] * r_item["سعر الوحدة"] * (r_item["الخصم %"] / 100.0)),
                    "warehouse_loc": r_item["موقع المخزن"]
                })
                
            if st.button("🖨️ إعادة بناء وإصدار الفاتورة الثلاثية للطباعة"):
                html_res = generate_triple_invoice_html(search_id, f_init["التاريخ"], f_init["اسم العميل"], f_init["هاتف العميل"], f_init["العنوان"], f_init["نوع البيع"], f_init["نظام التحصيل"], f_init["تاريخ التحصيل"], f_init.get("المدفوع مقدم", 0.0), f_init.get("المتبقي", 0.0), f_init["المسؤول"], re_cart_items, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, float(f_init.get("خصم نقدي ثابت", 0.0)))
                st.markdown(html_res, unsafe_allow_html=True)
                st.markdown(get_download_link(html_res, f"Invoice_{search_id}.html"), unsafe_allow_html=True)

    # --- 9. تقارير الأرباح والمبيعات ---
    elif "تقارير البيع والشراء والأرباح" in choice:
        st.header("📈 لوحة التقارير والمؤشرات المالية العامة للأرباح والمبيعات")
        
        sum_sales = pd.to_numeric(sales_df["إجمالي البيع"], errors='coerce').sum() if not sales_df.empty else 0.0
        sum_purchases = pd.to_numeric(purchases_df["إجمالي الشراء"], errors='coerce').sum() if not purchases_df.empty else 0.0
        sum_expenses = pd.to_numeric(exp_df["المبلغ"], errors='coerce').sum() if not exp_df.empty else 0.0
        sum_profits = pd.to_numeric(sales_df["صافي ربح الفاتورة"], errors='coerce').sum() if not sales_df.empty else 0.0
        net_wallet = sum_profits - sum_expenses
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💰 إجمالي المبيعات", f"{sum_sales:,.2f} ج")
        m2.metric("📥 إجمالي المشتريات", f"{sum_purchases:,.2f} ج")
        m3.metric("💸 إجمالي المصاريف", f"{sum_expenses:,.2f} ج")
        m4.metric("📈 أرباح المبيعات الإجمالية", f"{sum_profits:,.2f} ج")
        m5.metric("⚖️ صافي الربح الحقيقي", f"{net_wallet:,.2f} ج")

    # --- 10. صفحة إدارة بند المصاريف ---
    elif "المصاريف" in choice:
        st.header("💸 دفتر قيد وإدارة المصاريف النقدية والإدارية")
        st.dataframe(exp_df, use_container_width=True)
        with st.form("expenses_form"):
            e_desc = st.text_input("البيان / وجه الصرف للمبلغ مالي")
            e_val = st.number_input("المبلغ المنصرف بالجنيه", min_value=1.0, step=10.0)
            if st.form_submit_button("💾 قيد وإثبات المصروف"):
                if e_desc:
                    new_exp = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d"), "البيان": e_desc, "المبلغ": e_val, "المسؤول": st.session_state.user}])
                    st.session_state.exp_df = pd.concat([exp_df, new_exp], ignore_index=True)
                    st.session_state.exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم توثيق المصروف في الدفتر اليومي الحسابي!")
                    st.rerun()

    # --- 11. الحضور والانصراف ---
    elif "الحضور والانصراف" in choice:
        st.header("⏰ سجل حركات الحضور والانصراف الإلكتروني اليومي للموظفين")
        st.dataframe(att_df, use_container_width=True)
        c1, c2 = st.columns(2)
        if c1.button("🟢 إثبات بصمة حضور الآن للمستخدم الحالي", use_container_width=True):
            new_att = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "وقت الحضور": datetime.now().strftime("%H:%M:%S"), "وقت الانصراف": "لم ينصرف"}])
            st.session_state.att_df = pd.concat([att_df, new_att], ignore_index=True)
            st.session_state.att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
            st.success("🎉 تم قيد وبصم وقت حضورك للنظام بنجاح!")
            st.rerun()
            
        if c2.button("🔴 إثبات بصمة انصراف الآن وغلق العمل", use_container_width=True):
            today_str = datetime.now().strftime("%Y-%m-%d")
            idx = att_df[(att_df["الموظف"] == st.session_state.user) & (att_df["التاريخ"] == today_str)].index
            if not idx.empty:
                st.session_state.att_df.at[idx[-1], "وقت الانصراف"] = datetime.now().strftime("%H:%M:%S")
                st.session_state.att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success("🎉 تم توثيق وبصم وقت انصرافك بنجاح. رافقتك السلامة!")
                st.rerun()
            else: st.warning("⚠️ عذراً، لم يتم العثور على حركة تسجيل حضور مسجلة لك اليوم أولاً!")

    # --- 12. صفحة إدارة الصلاحيات والحسابات ---
    elif "إدارة وتعديل الصلاحيات والحسابات" in choice:
        st.header("⚙️ لوحة الإدارة الشاملة للحسابات والتحكم بالصلاحيات")
        tab_users, tab_roles = st.tabs(["👥 الحسابات والمسؤولين", "🔑 إدارة الصلاحيات للمجموعات"])
        
        with tab_users:
            u_data = pd.read_csv(USERS_FILE)
            st.dataframe(u_data, use_container_width=True)
            with st.form("add_user_form"):
                new_un = st.text_input("اسم حساب المستخدم الجديد").strip()
                new_pw = st.text_input("كلمة مرور الحساب").strip()
                new_rl = st.selectbox("الرتبة والدرجة الصلاحية", ["مدير", "مشرف", "موظف"])
                if st.form_submit_button("➕ إنشاء وتثبيت حساب المستخدم الجديد"):
                    if new_un and new_pw:
                        new_u_row = pd.DataFrame([{"username": new_un, "password": new_pw, "role": new_rl}])
                        pd.concat([u_data, new_u_row], ignore_index=True).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                        st.success("🚀 تم إضافة المستخدم الجديد لحسابات!")
                        st.rerun()
                        
        with tab_roles:
            st.subheader("🔑 جدول التحكم التفاعلي بالصفحات")
            edited_perms_df = st.data_editor(perms_df, use_container_width=True, disabled=["اسم الصفحة"])
            if st.button("💾 حفظ الصلاحيات والتعديلات الجديدة"):
                edited_perms_df.to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')
                st.success("🚀 تم تحديث قواعد الصلاحيات!")
                st.rerun()

    # --- 13. صفحة إعدادات بيانات الفاتورة والدعم ---
    elif "إعدادات بيانات الفاتورة والدعم" in choice:
        st.header("⚙️ تحديث وإعداد بيانات طباعة الفاتورة والدعم")
        with st.form("settings_form_updated"):
            new_showroom_name = st.text_input("اسم المعرض / الشركة بالفاتورة", value=SHOWROOM_NAME)
            new_showroom_address = st.text_input("العنوان بالتفصيل بالفاتورة", value=SHOWROOM_ADDRESS)
            new_inquiry_number = st.text_input("رقم الدعم الفني للفواتير", value=INQUIRY_NUMBER)
            if st.form_submit_button("💾 حفظ وتحديث الإعدادات"):
                updated_settings = pd.DataFrame([{"اسم المعرض": new_showroom_name, "العنوان": new_showroom_address, "رقم الدعم": new_inquiry_number}])
                updated_settings.to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم حفظ الإعدادات وتطبيقها على ترويسة الفواتير والمستندات بنجاح!")
                st.rerun()
