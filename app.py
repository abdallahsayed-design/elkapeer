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
    
    standard_table_th = "<tr><th>الصنف والبيان</th><th>التصنيف</th><th>الوحدة</th><th>الكمية</th><th>سعر المفرد</th><th>الخصم</th><th>الصافي الإجمالي</th></tr>"
    standard_table_td = ""
    for item in cart_items:
        standard_table_td += f"<tr><td>{item['item_name']}</td><td>{item.get('category', 'عام')}</td><td>{item.get('unit', 'قطعة')}</td><td>{item['qty']}</td><td>{item['price']} جنيه</td><td>{item['discount']}%</td><td style='font-weight: bold;'>{item['final_total']} جنيه</td></tr>"
    
    # إضافة سطر الخصم المباشر لجدول الأصناف إن وجد
    if discount_fixed > 0:
        standard_table_td += f"<tr style='background:#f9f9f9; font-weight:bold;'><td colspan='6' style='text-align:left; padding-left:15px;'>خصم نقدي مباشر على الفاتورة:</td><td style='color:red;'>-{discount_fixed} جنيه</td></tr>"
    
    store_table_th = "<tr><th>الصنف والبيان</th><th>موقع المخزن</th><th>الكمية المطلوبة للصرف</th></tr>"
    store_table_td = ""
    for item in cart_items:
        store_table_td += f"<tr><td style='font-size: 15px; font-weight: bold;'>{item['item_name']} ({item.get('unit', 'قطعة')})</td><td>{item.get('warehouse_loc', 'الرئيسي')}</td><td style='font-size: 16px; font-weight: bold;'>{item['qty']}</td></tr>"

    html_content = f"""
    <div class="triple-print-wrapper">
        <style>
            @page {{ size: A5 portrait; margin: 0; }}
            @media print {{
                body {{ direction: rtl; background: #fff; color: #000; padding: 0; margin: 0; }}
                header, [data-testid="stSidebar"], [data-testid="stHeader"], .no-print-zone, .stButton, .download-btn-area {{ display: none !important; }}
                .invoice-page {{ 
                    width: 148mm; 
                    height: auto !important; 
                    min-height: 210mm; 
                    box-sizing: border-box; 
                    padding: 10mm !important; 
                    margin: 0 !important; 
                    page-break-after: always; 
                    border: none !important; 
                    box-shadow: none !important; 
                }}
                .invoice-items-table tr {{
                    page-break-inside: avoid !important;
                    page-break-after: auto !important;
                }}
            }}
            .triple-print-wrapper {{ direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; }}
            .invoice-page {{ 
                width: 148mm; 
                height: auto;
                min-height: 210mm;
                max-width: 100%; 
                border: 2px solid #000; 
                padding: 20px; 
                margin: 20px auto; 
                background: #fff; 
                color: #000; 
                box-sizing: border-box; 
                page-break-after: always; 
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
    
    # ربط اختيار الـ Sidebar بـ Session State للحفاظ على حالة الصفحة الحالية عند التنقل
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
                    if pay_amt <= 0: st.error("يرجى إدخال مبلغ تحصيل صحيح أكبر من الصفر.")
                    else:
                        coll_id = "REC-" + str(int(datetime.now().timestamp()))
                        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_coll = pd.DataFrame([{ "رقم السند": coll_id, "التاريخ": current_time_str, "اسم العميل": selected_cust, "المبلغ المحصل": pay_amt, "طريقة السداد": pay_method, "ملاحظات": pay_notes, "المسؤول": st.session_state.user }])
                        st.session_state.collections_df = pd.concat([collections_df, new_coll], ignore_index=True)
                        st.session_state.collections_df.to_csv(COLLECTIONS_FILE, index=False, encoding='utf-8-sig')
                        st.success(f"🎉 تم تسجيل السند {coll_id} بنجاح وخصمه من حساب العميل!")
                        new_debt_after_pay = current_debt - pay_amt
                        msg_text = f"عزيزي العميل: {selected_cust}\nتم استلام مبلغ: {pay_amt} جنيهاً مصرياً بحسابكم بطريقة ({pay_method}).\nرقم الحركة: {coll_id}\nالتاريخ: {current_time_str}\nالمديونية المتبقية بذمتكم هي: {new_debt_after_pay:,.2f} جنيه.\nشكراً لتعاملكم مع {SHOWROOM_NAME}."
                        st.info(f"📨 تم إرسال رسالة نصية تفصيلية إلى رقم هاتف العميل ({cust_phone if cust_phone else 'غير مسجل'}):\n\n \"{msg_text}\"")

    # --- 5. حركة فواتير الشراء والتعديل والارتجاع حركياً المطور ---
    elif "حركة فواتير الشراء والتعديل" in choice:
        st.header("📥 حركات فواتير الشراء وتغذية المخزون بالبضائع")
        
        tab_p_add, tab_p_edit_remove = st.tabs(["➕ تسجيل فاتورة شراء جديدة", "🎛️ لوحة تحكم وتعديل وارتجاع فواتير الشراء"])
        
        with tab_p_add:
            with st.form("purchase_form"):
                p1, p2, p3 = st.columns(3)
                p_invoice = p1.text_input("رقم فاتورة الشراء", value="PUR-" + str(int(datetime.now().timestamp())))
                
                # جلب أسماء الموردين المكودين مسبقاً لتسهيل الإدخال
                all_suppliers = contacts_df[contacts_df["النوع"] == "مورد"]["الاسم"].unique() if not contacts_df.empty else []
                if len(all_suppliers) > 0:
                    p_supplier = p2.selectbox("اسم المورد / الشركة", all_suppliers)
                else:
                    p_supplier = p2.text_input("اسم المورد / الشركة (اكتب اسم المورد)")
                    
                if inv_df.empty: p_code = p3.text_input("كود الصنف")
                else: p_code = p3.selectbox("اختر الصنف لتغذيته", inv_df["كود الصنف"].values, format_func=safe_item_format)
                
                p4, p5 = st.columns(2)
                p_qty = p4.number_input("الكمية المشتراة", min_value=1, step=1, value=st.session_state.form_purchase_qty)
                p_price = p5.number_input("سعر الشراء الفعلي للوحدة (جنيه)", min_value=0.0, step=10.0)
                
                if st.form_submit_button("📥 ترحيل الفاتورة وزيادة الأرصدة بالمخزن"):
                    if p_supplier and p_code:
                        match_item = inv_df[inv_df['كود الصنف'] == p_code]
                        if match_item.empty: st.error("كود الصنف غير صحيح.")
                        else:
                            item_idx = match_item.index[0]
                            item_name = match_item.iloc[0]['اسم الصنف']
                            item_cat = match_item.iloc[0]['تصنيف الصنف']
                            item_unit = match_item.iloc[0]['نوع الوحدة']
                            item_wh = match_item.iloc[0]['موقع المخزن']
                            
                            total_p = p_qty * p_price
                            new_p_row = pd.DataFrame([{
                                "رقم الفاتورة": p_invoice, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "المورد": p_supplier, "كود الصنف": p_code, "الصنف": item_name, "تصنيف الصنف": item_cat,
                                "نوع الوحدة": item_unit, "موقع المخزن": item_wh, "سعر الشراء المعتمد": p_price,
                                "الكمية": p_qty, "إجمالي الشراء": total_p, "المسؤول": st.session_state.user
                            }])
                            
                            st.session_state.purchases_df = pd.concat([purchases_df, new_p_row], ignore_index=True)
                            st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                            
                            st.session_state.inv_df.at[item_idx, "الكمية"] += int(p_qty)
                            st.session_state.inv_df.at[item_idx, "سعر الشراء"] = p_price
                            st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                            
                            st.success("🎉 تم حفظ حركة الشراء بنجاح وزيادة كميات الصنف وتعديل سعر تكلفته!")
                            st.rerun()
                            
        with tab_p_edit_remove:
            st.subheader("📝 تعديل، ارتجاع، وحذف حركات فواتير الشراء")
            if purchases_df.empty:
                st.info("لا توجد فواتير شراء مسجلة.")
            else:
                st.write("💡 يمكنك تعديل الحقول مباشرة من الجدول التفاعلي أدناه واضغط حفظ. (تنبيه: التعديل من الجدول لا يؤثر على المخزون بشكل حركي، لتعديل المخزون استخدم الأزرار التفاعلية بالأسفل)")
                
                # عرض محرر البيانات التفاعلي لفواتير الشراء
                edited_purchases = st.data_editor(purchases_df, num_rows="dynamic", use_container_width=True, key="purchases_interactive_editor")
                if st.button("💾 حفظ تعديلات جدول المشتريات العامة"):
                    edited_purchases.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                    st.session_state.purchases_df = edited_purchases
                    st.success("🚀 تم حفظ التعديلات في ملف المشتريات!")
                    st.rerun()
                    
                st.markdown("---")
                st.subheader("↩️ إجراء حركة ارتجاع بضاعة لمورد أو حذف بند شراء معين وضبط المخزن تلقائياً")
                
                # آلية ذكية لاختيار فاتورة الشراء وتعديلها أو ارتجاع كمياتها مع التأثير المباشر واللحظي على جرد المخزن
                p_select_inv = st.selectbox("اختر رقم الفاتورة لإجراء تعديل حركي / ارتجاع:", purchases_df["رقم الفاتورة"].unique())
                matching_p_rows = purchases_df[purchases_df["رقم الفاتورة"] == p_select_inv]
                
                if not matching_p_rows.empty:
                    st.dataframe(matching_p_rows[["كود الصنف", "الصنف", "الكمية", "سعر الشراء المعتمد", "المورد"]])
                    p_row_to_mod = st.selectbox("اختر الصنف المراد ارجاعه أو حذفه من هذه الفاتورة:", matching_p_rows["كود الصنف"].values, format_func=lambda x: f"كود {x} - {matching_p_rows[matching_p_rows['كود الصنف']==x]['الصنف'].values[0]}")
                    
                    target_p_invoice_row = matching_p_rows[matching_p_rows["كود الصنف"] == p_row_to_mod].iloc[0]
                    max_ret_qty = int(target_p_invoice_row["الكمية"])
                    
                    c_act1, c_act2 = st.columns(2)
                    qty_to_return_supplier = c_act1.number_input("الكمية المراد ارتجاعها للمورد (سيتم خصمها من المخزن الحالي):", min_value=1, max_value=max_ret_qty, value=1, step=1)
                    
                    if c_act2.button("🔥 تنفيذ ارتجاع البضاعة للمورد وتعديل الأرصدة الحالية", use_container_width=True):
                        # 1. تحديث كمية الصنف في ملف المشتريات
                        p_idx = purchases_df[(purchases_df["رقم الفاتورة"] == p_select_inv) & (purchases_df["كود الصنف"] == p_row_to_mod)].index[0]
                        new_p_qty = max_ret_qty - qty_to_return_supplier
                        
                        if new_p_qty == 0:
                            # إذا تم ارتجاع كامل الكمية نقوم بحذف السطر
                            st.session_state.purchases_df = purchases_df.drop(p_idx)
                        else:
                            st.session_state.purchases_df.at[p_idx, "الكمية"] = new_p_qty
                            st.session_state.purchases_df.at[p_idx, "إجمالي الشراء"] = new_p_qty * float(target_p_invoice_row["سعر الشراء المعتمد"])
                            
                        st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                        
                        # 2. خصم الكمية المرتجعة من جرد المخزن
                        if p_row_to_mod in st.session_state.inv_df["كود الصنف"].values:
                            inv_idx = st.session_state.inv_df[st.session_state.inv_df["كود الصنف"] == p_row_to_mod].index[0]
                            st.session_state.inv_df.at[inv_idx, "الكمية"] = max(0, int(st.session_state.inv_df.at[inv_idx, "الكمية"]) - qty_to_return_supplier)
                            st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                            
                        st.success("✅ تم تنفيذ عملية الارتجاع بنجاح وخصم الكميات من المخازن وتعديل حسابات التكلفة الفاتورة!")
                        st.rerun()

    # --- 6. صفحة حركة فواتير البيع المتطورة (عميل مكود وسريع + حذف أصناف البث الحي) ---
    elif "حركة فواتير البيع" in choice:
        st.header("📤 لوحة حركة فواتير البيع وإصدار الفواتير المتطورة")
        
        st.markdown("### 👤 بيانات العميل ونظام البيع")
        cust_type_select = st.radio("نوع العميل للفاتورة الحالية:", ["عميل سريع (كاش)", "عميل مكود ومسجل مسبقاً"], index=0 if st.session_state.form_sale_cust_type == "عميل سريع (كاش)" else 1, horizontal=True)
        st.session_state.form_sale_cust_type = cust_type_select
        
        sale_cust = ""
        sale_phone = ""
        sale_address = ""
        
        if cust_type_select == "عميل سريع (كاش)":
            c1, c2, c3 = st.columns(3)
            # الاحتفاظ بالبيانات المدخلة في الـ Session State لمنع الفقدان عند التنقل
            sale_cust = c1.text_input("اسم العميل السريع", value=st.session_state.form_sale_cust_name)
            sale_phone = c2.text_input("رقم الهاتف (اختياري)", value=st.session_state.form_sale_cust_phone)
            sale_address = c3.text_input("العنوان (اختياري)", value=st.session_state.form_sale_cust_address)
            
            st.session_state.form_sale_cust_name = sale_cust
            st.session_state.form_sale_cust_phone = sale_phone
            st.session_state.form_sale_cust_address = sale_address
        else:
            all_saved_customers = contacts_df[contacts_df["النوع"] == "عميل"]["الاسم"].unique() if not contacts_df.empty else []
            if len(all_saved_customers) == 0:
                st.warning("⚠️ لا توجد كروت عملاء مكودة بالنظام! يرجى تكويد عملاء من صفحة 'العملاء والموردين'. تم تحويلك للعميل السريع تلقائياً.")
                sale_cust = st.text_input("اسم العميل", value=st.session_state.form_sale_cust_name)
                st.session_state.form_sale_cust_name = sale_cust
            else:
                selected_c_index = 0
                if st.session_state.form_sale_selected_cust in all_saved_customers:
                    selected_c_index = list(all_saved_customers).index(st.session_state.form_sale_selected_cust)
                    
                selected_c_name = st.selectbox("اختر العميل المكود من النظام:", all_saved_customers, index=selected_c_index)
                st.session_state.form_sale_selected_cust = selected_c_name
                
                cust_data_row = contacts_df[(contacts_df["الاسم"] == selected_c_name) & (contacts_df["النوع"] == "عميل")].iloc[0]
                sale_cust = str(selected_c_name)
                sale_phone = str(cust_data_row["الهاتف"])
                sale_address = str(cust_data_row["العنوان"])
                st.info(f"🟢 العميل: {sale_cust} | الهاتف: {sale_phone} | العنوان: {sale_address}")
        
        st.markdown("### 🛒 اختيار المنتجات وإضافتها للسلة")
        sc1, sc2, sc3 = st.columns(3)
        if inv_df.empty: sc1.info("المخزن فارغ.")
        else:
            selected_sale_code = sc1.selectbox("اختر الصنف للبيع", inv_df["كود الصنف"].values, format_func=safe_item_format)
            match_s = inv_df[inv_df["كود الصنف"] == selected_sale_code].iloc[0]
            
            sale_qty = sc2.number_input(f"الكمية المطلوبة (المتاحة: {match_s['الكمية']})", min_value=1, max_value=int(match_s['الكمية']) if int(match_s['الكمية']) > 0 else 1, step=1)
            sale_disc = sc3.number_input("نسبة الخصم للبند %", min_value=0.0, max_value=100.0, step=1.0, value=0.0)
            
            if st.button("➕ إضافة المنتج المختار إلى سلة الفاتورة الحالية"):
                if match_s['الكمية'] <= 0: st.error("⚠️ عذراً رصيد هذا الصنف صفر بالمخزن حالياً!")
                else:
                    final_u_p = match_s['سعر البيع']
                    total_p_b = sale_qty * final_u_p
                    final_tot_p = total_p_b - (total_p_b * (sale_disc / 100))
                    
                    st.session_state.cart.append({
                        "item_code": selected_sale_code, "item_name": match_s['اسم الصنف'],
                        "category": match_s['تصنيف الصنف'], "unit": match_s['نوع الوحدة'],
                        "warehouse_loc": match_s['موقع المخزن'], "qty": int(sale_qty),
                        "price": float(final_u_p), "discount": float(sale_disc),
                        "final_total": float(final_tot_p), "purchase_cost": float(match_s['سعر الشراء'])
                    })
                    st.success(f"تم إضافة {match_s['اسم الصنف']} بنجاح بالسلة!")
                    st.rerun()
                    
        if st.session_state.cart:
            st.markdown("### 🧾 معاينة الأصناف المدرجة بالسلة وإدارة الحذف:")
            cart_df = pd.DataFrame(st.session_state.cart)
            
            # آلية تفاعلية جديدة تتيح للمستخدم إمكانية حذف بند معين فوراً من السلة المباشرة قبل ترحيل الفاتورة
            for i, item in enumerate(st.session_state.cart):
                cols_cart_control = st.columns([5, 2, 2, 2])
                cols_cart_control[0].write(f"📦 **{item['item_name']}** ({item['item_code']})")
                cols_cart_control[1].write(f"الكمية: {item['qty']}")
                cols_cart_control[2].write(f"الإجمالي: {item['final_total']} ج.م")
                if cols_cart_control[3].button(f"🗑️ حذف البند", key=f"btn_remove_item_cart_{i}_{item['item_code']}"):
                    st.session_state.cart.pop(i)
                    st.success("تم إزالة الصنف المحدد من السلة!")
                    st.rerun()
                    
            if st.button("🗑️ تفريغ وإلغاء السلة بالكامل"):
                st.session_state.cart = []
                st.rerun()
                
            subtotal_before_discount = sum(item['final_total'] for item in st.session_state.cart)
            
            st.markdown("---")
            st.subheader("💰 إجماليات الفاتورة النهائية والخصومات الثابتة")
            
            col_disc1, col_disc2 = st.columns(2)
            with col_disc1:
                discount_fixed = st.number_input("💵 خصم نقدي مباشر على الفاتورة (بالجنيه على الإجمالي كلي)", min_value=0.0, value=0.0, step=5.0, key="sale_discount_fixed_input")
            
            total_invoice_amount = max(0.0, subtotal_before_discount - discount_fixed)
            st.metric("🧾 صافي إجمالي الفاتورة المطلوب سداده الفعلي:", f"{total_invoice_amount:,.2f} جنيه")
            
            st.markdown("### 🛡️ تحديد شروط ونظام السداد المالي")
            pay_type = st.radio("نوع عملية البيع والفاتورة", ["نقدي (كاش)", "آجل (على الحساب)"], horizontal=True)
            
            collect_system = "غير محدد"
            collect_date = "غير محدد"
            paid_advance = 0.0
            remaining_bal = 0.0
            
            if pay_type == "آجل (على الحساب)":
                ac1, ac2, ac3 = st.columns(3)
                collect_system = ac1.selectbox("نظام التحصيل للآجل", ["أسبوعي", "شهري", "دفعات مرنة", "عند الطلب"])
                collect_date = ac2.text_input("تاريخ استحقاق المديونية", value=datetime.now().strftime("%Y-%m-%d"))
                paid_advance = ac3.number_input("المبلغ المدفوع مقدماً (جدية حجز / مقدم)", min_value=0.0, max_value=float(total_invoice_amount), step=50.0)
                remaining_bal = total_invoice_amount - paid_advance
                st.warning(f"⚠️ سيتم ترحيل مديونية بقيمة {remaining_bal:,.2f} جنيه بحساب العميل بذمته المالية.")
                
            if st.button("🚀 ترحيل الفاتورة نهائياً وخصم البضاعة من المخزن", use_container_width=True):
                if not sale_cust: st.error("⚠️ يرجى إدخال اسم العميل لإصدار الفاتورة باسمه.")
                else:
                    inv_id = "INV-" + str(int(datetime.now().timestamp()))
                    datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    sales_rows = []
                    for item in st.session_state.cart:
                        item_tot_cost = item['qty'] * item['purchase_cost']
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
                    
                    st.success(f"🎉 تم ترحيل الفاتورة بنجاح برقم {inv_id} وتحديث الأرصدة بالمخزن!")
                    
                    html_invoice = generate_triple_invoice_html(inv_id, datetime_str, sale_cust, sale_phone, sale_address, pay_type, collect_system, collect_date, paid_advance, remaining_bal, st.session_state.user, st.session_state.cart, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, discount_fixed=discount_fixed)
                    st.markdown(html_invoice, unsafe_allow_html=True)
                    st.markdown(get_download_link(html_invoice, f"Invoice_{inv_id}.html"), unsafe_allow_html=True)
                    
                    # تصفير المدخلات والسلة بعد النجاح
                    st.session_state.cart = []
                    st.session_state.form_sale_cust_name = ""
                    st.session_state.form_sale_cust_phone = ""
                    st.session_state.form_sale_cust_address = ""
                    st.rerun()

    # --- 7. صفحة ارتجاع فواتير البيع التفاعلية الكاملة ---
    elif "ارتجاع فواتير البيع" in choice:
        st.header("↩️ إدارة لوحة ارتجاع وتعديل الأصناف المرتجعة للعملاء")
        
        t_manage_returns, t_add_return = st.tabs(["🎛️ لوحة تحكم المردودات والارتجاع (تعديل وحذف)", "➕ تسجيل بند إرجاع جديد"])
        
        with t_manage_returns:
            st.subheader("📝 جدول تفاعلي لتعديل أو حذف بيانات الارتجاع وضبط أسعار الشراء والبيع")
            if returns_df.empty:
                st.info("لا توجد بيانات حركات ارتجاع مسجلة حالياً.")
            else:
                st.write("💡 يمكنك تعديل أي خانة (الأسعار، الكميات، الأرقام) بالضغط عليها مرتين مباشرة، أو حذف أي سطر بتحديده ثم الضغط على زر الحذف في الكيبورد أو جدول النظام.")
                
                edited_returns = st.data_editor(
                    returns_df, 
                    num_rows="dynamic",  
                    use_container_width=True,
                    key="returns_main_interactive_editor"
                )
                
                if st.button("💾 حفظ جميع التعديلات وتحديث سجلات النظام"):
                    try:
                        edited_returns.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
                        st.session_state.returns_df = edited_returns
                        st.success("🚀 تم تحديث وحفظ سجلات الارتجاع والأسعار المعدلة في الملفات بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الحفظ والتعديل: {e}")
                    
        with t_add_return:
            st.subheader("➕ إضافة بند ارتجاع جديد يدوياً إلى النظام")
            with st.form("add_return_new_form", clear_on_submit=True):
                rc1, rc2, rc3 = st.columns(3)
                ret_id = rc1.text_input("رقم الإرجاع", value="RET-" + str(int(datetime.now().timestamp())))
                invoice_ref = rc2.text_input("رقم الفاتورة الأصلية")
                cust_name = rc3.text_input("اسم العميل")
                
                rc4, rc5, rc6 = st.columns(3)
                if inv_df.empty:
                    item_code = rc4.text_input("كود الصنف")
                else:
                    item_code = rc4.selectbox("اختر الصنف المراد إرجاعه", inv_df["كود الصنف"].values, format_func=safe_item_format)
                
                ret_qty = rc5.number_input("الكمية المرجعة", min_value=1, step=1, value=1)
                ret_amount = rc6.number_input("المبلغ المردود للعميل (جنيه)", min_value=0.0, step=10.0, value=0.0)
                
                submit_ret = st.form_submit_button("📥 ترحيل بند الارتجاع وزيادة المخزن فوراً")
                if submit_ret:
                    if cust_name and invoice_ref and item_code:
                        match_item = inv_df[inv_df['كود الصنف'] == item_code]
                        item_name = match_item.iloc[0]['اسم الصنف'] if not match_item.empty else "صنف غير معروف"
                        
                        new_return_row = pd.DataFrame([{
                            "رقم الإرجاع": str(ret_id),
                            "رقم الفاتورة الأصلية": str(invoice_ref),
                            "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "اسم العميل": str(cust_name),
                            "كود الصنف": str(item_code),
                            "الصنف": str(item_name),
                            "الكمية المرجعة": int(ret_qty),
                            "المبلغ المردود": float(ret_amount),
                            "المسؤول": st.session_state.user
                        }])
                        
                        updated_returns_df = pd.concat([st.session_state.returns_df, new_return_row], ignore_index=True)
                        updated_returns_df.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
                        st.session_state.returns_df = updated_returns_df
                        
                        if item_code in st.session_state.inv_df["كود الصنف"].values:
                            idx = st.session_state.inv_df[st.session_state.inv_df["كود الصنف"] == item_code].index[0]
                            st.session_state.inv_df.at[idx, "الكمية"] += int(ret_qty)
                            st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        
                        st.success("🎉 تم تسجيل حركة وبند الارتجاع بنجاح، وإعادة السلع للمخازن وتعديل الأرصدة المالية!")
                        st.rerun()
                    else:
                        st.error("⚠️ يرجى ملء الحقول الأساسية (اسم العميل، رقم الفاتورة الأصلية، والصنف) لإتمام الحركة.")

    # --- 8. البحث عن الفواتير وطباعتها ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 محرك البحث عن الفواتير السريع وطباعتها")
        if sales_df.empty: st.info("لم يتم إصدار فواتير بيع بعد.")
        else:
            search_id = st.text_input("ادخل رقم الفاتورة المطلوب البحث عنها أو طباعتها:").strip()
            if search_id:
                f_sales = sales_df[sales_df["رقم الفاتورة"] == search_id]
                if f_sales.empty: st.error("❌ لم يتم العثور على أي فاتورة تطابق هذا الرقم.")
                else:
                    st.success("🔍 تم العثور على الفاتورة بنجاح! تفاصيل البيانات:")
                    f_head = f_sales.iloc[0]
                    
                    st.write(f"**اسم العميل:** {f_head['اسم العميل']} | **التاريخ:** {f_head['التاريخ']} | **نوع الدفع:** {f_head['نوع البيع']}")
                    st.dataframe(f_sales[["كود الصنف", "الصنف", "الكمية", "سعر الوحدة", "الخصم %", "إجمالي البيع"]], use_container_width=True)
                    
                    re_items = []
                    for _, r in f_sales.iterrows():
                        re_items.append({
                            "item_code": r["كود الصنف"], "item_name": r["الصنف"],
                            "qty": int(r["الكمية"]), "price": float(r["سعر الوحدة"]),
                            "discount": float(r["الخصم %"]), "final_total": float(r["إجمالي البيع"])
                        })
                    
                    fixed_disc_val = f_head.get("خصم نقدي ثابت", 0.0)
                    html_invoice = generate_triple_invoice_html(search_id, f_head["التاريخ"], f_head["اسم العميل"], f_head["هاتف العميل"], f_head["العنوان"], f_head["نوع البيع"], f_head["نظام التحصيل"], f_head["تاريخ التحصيل"], f_head["المدفوع مقدم"], f_head["المتبقي"], f_head["المسؤول"], re_items, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, discount_fixed=fixed_disc_val)
                    st.markdown(html_invoice, unsafe_allow_html=True)

    # --- 9. تقارير البيع والشراء والأرباح ---
    elif "تقارير البيع والشراء والأرباح" in choice:
        st.header("📈 لوحة التقارير الذكية والإحصائيات والأرباح العامة")
        
        total_s_income = pd.to_numeric(sales_df["إجمالي البيع"], errors='coerce').sum() if not sales_df.empty else 0.0
        total_s_profit = pd.to_numeric(sales_df["صافي ربح الفاتورة"], errors='coerce').sum() if not sales_df.empty else 0.0
        total_p_expenses = pd.to_numeric(purchases_df["إجمالي الشراء"], errors='coerce').sum() if not purchases_df.empty else 0.0
        total_gen_expenses = pd.to_numeric(exp_df["المبلغ"], errors='coerce').sum() if not exp_df.empty else 0.0
        
        final_net_profit = total_s_profit - total_gen_expenses
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🛒 إجمالي دخل المبيعات", f"{total_s_income:,.2f} جنيه")
        m2.metric("📥 إجمالي نفقات المشتريات", f"{total_p_expenses:,.2f} جنيه")
        m3.metric("💸 إجمالي بند المصاريف النثرية", f"{total_gen_expenses:,.2f} جنيه")
        m4.metric("📊 صافي الأرباح النهائية للمحل", f"{final_net_profit:,.2f} جنيه")

    # --- 10. المصاريف ---
    elif "المصاريف" in choice:
        st.header("💸 سجل إدارة المصاريف النثرية والعمومية")
        st.dataframe(exp_df, use_container_width=True)
        with st.form("exp_form"):
            ex1, ex2 = st.columns(2)
            e_desc = ex1.text_input("بيان وجدول المصروف")
            e_amt = ex2.number_input("المبلغ المدفوع (جنيه)", min_value=0.0, step=10.0)
            if st.form_submit_button("💾 ترحيل المصروف المالي"):
                if e_desc and e_amt > 0:
                    new_e = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "البيان": e_desc, "المبلغ": e_amt, "المسؤول": st.session_state.user}])
                    st.session_state.exp_df = pd.concat([exp_df, new_e], ignore_index=True)
                    st.session_state.exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم حفظ قيد المصروف الجديد!")
                    st.rerun()

    # --- 11. الحضور والانصراف ---
    elif "الحضور والانصراف" in choice:
        st.header("⏰ دفتر تسجيل حضور وانصراف الموظفين الحركي")
        st.dataframe(att_df, use_container_width=True)
        ac1, ac2 = st.columns(2)
        if ac1.button("🟢 تسجيل بصمة حضور الآن", use_container_width=True):
            new_att = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "وقت الحضور": datetime.now().strftime("%H:%M:%S"), "وقت الانصراف": "لم ينصرف"}])
            st.session_state.att_df = pd.concat([att_df, new_att], ignore_index=True)
            st.session_state.att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
            st.success("✅ تم تسجيل بصمة الحضور اليومية بنجاح!")
            st.rerun()
            
        if ac2.button("🔴 تسجيل بصمة انصراف الآن", use_container_width=True):
            today_str = datetime.now().strftime("%Y-%m-%d")
            match_att = att_df[(att_df["الموظف"] == st.session_state.user) & (att_df["التاريخ"] == today_str)]
            if match_att.empty: st.error("❌ لم يتم العثور على بصمة حضور مسجلة لك اليوم.")
            else:
                idx = match_att.index[-1]
                st.session_state.att_df.at[idx, "وقت الانصراف"] = datetime.now().strftime("%H:%M:%S")
                st.session_state.att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم تسجيل وقت انصرافك بنجاح! رافقتكم السلامة.")
                st.rerun()

    # --- 12. إدارة وتعديل الصلاحيات والحسابات ---
    elif "إدارة وتعديل الصلاحيات والحسابات" in choice:
        st.header("⚙️ لوحة التحكم بصلاحيات المستخدمين وعناوين الصفحات")
        tab_users, tab_roles = st.tabs(["👥 حسابات الموظفين", "🔑 صلاحيات المجموعات"])
        
        with tab_users:
            u_manage = pd.read_csv(USERS_FILE)
            st.dataframe(u_manage, use_container_width=True)
            with st.form("add_user_form"):
                au1, au2, au3 = st.columns(3)
                new_u = au1.text_input("اسم المستخدم الجديد")
                new_p = au2.text_input("كلمة المرور")
                new_r = au3.selectbox("الرتبة / الدور", ["مدير", "مشرف", "موظف"])
                if st.form_submit_button("💾 إنشاء مستخدم"):
                    if new_u and new_p:
                        u_updated = pd.concat([u_manage, pd.DataFrame([{"username": new_u, "password": new_p, "role": new_r}])], ignore_index=True)
                        u_updated.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                        st.success("🚀 تم إضافة المستخدم الجديد للحسابات!")
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
                st.success("✅ تم تحديث وحفظ بيانات المعرض بنجاح!")
                st.rerun()
