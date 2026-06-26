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
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "هاتف العميل", "العنوان", "نوع البيع", "نظام التحصيل", "تاريخ التحصيل", "المدفوع مقدم", "المتبقي", "كود الصنف", "الصنف", "تصنيف الصنف", "نوع الوحدة", "موقع المخزن", "الكمية", "سعر الوحدة", "الخصم %", "إجمالي البيع", "تكلفة الشراء الإجمالية", "صافي ربح الفاتورة", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
        
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

# تهيئة متغيرات حفظ الحالة للتنقل بدون فقدان البيانات
if 'form_sale_cust_name' not in st.session_state: st.session_state.form_sale_cust_name = ""
if 'form_sale_cust_phone' not in st.session_state: st.session_state.form_sale_cust_phone = ""
if 'form_sale_cust_address' not in st.session_state: st.session_state.form_sale_cust_address = ""
if 'form_purchase_qty' not in st.session_state: st.session_state.form_purchase_qty = 1

# تم تحديث الدالة لمنع تداخل الصفحات في الطباعة نهائياً
def generate_triple_invoice_html(inv_id, datetime_str, client_name, phone, address, pay_type, collect_system, collect_date, paid_advance, remaining_bal, user, cart_items, sh_name, sh_address, sh_phone):
    collect_info = ""
    if pay_type == "آجل (على الحساب)":
        collect_info = f"""
        <tr><td><b>نظام التحصيل:</b> {collect_system}</td><td><b>تاريخ الاستحقاق:</b> {collect_date}</td></tr>
        <tr><td><b>المدفوع مقدماً:</b> <span style='color:green; font-weight:bold;'>{paid_advance} جنيه</span></td><td><b>المتبقي بالذمة (آجل):</b> <span style='color:red; font-weight:bold;'>{remaining_bal} جنيه</span></td></tr>
        """
    
    total_invoice_amount = sum(item['final_total'] for item in cart_items)
    arabic_total_words = number_to_arabic_words(total_invoice_amount)
    
    standard_table_th = "<tr><th>الصنف والبيان</th><th>التصنيف</th><th>الوحدة</th><th>الكمية</th><th>سعر المفرد</th><th>الخصم</th><th>الصافي الإجمالي</th></tr>"
    standard_table_td = ""
    for item in cart_items:
        standard_table_td += f"<tr><td>{item['item_name']}</td><td>{item.get('category', 'عام')}</td><td>{item.get('unit', 'قطعة')}</td><td>{item['qty']}</td><td>{item['price']} جنيه</td><td>{item['discount']}%</td><td style='font-weight: bold;'>{item['final_total']} جنيه</td></tr>"
    
    store_table_th = "<tr><th>الصنف والبيان</th><th>موقع المخزن</th><th>الكمية المطلوبة للصرف</th></tr>"
    store_table_td = ""
    for item in cart_items:
        store_table_td += f"<tr><td style='font-size: 15px; font-weight: bold;'>{item['item_name']} ({item.get('unit', 'قطعة')})</td><td>{item.get('warehouse_loc', 'الرئيسي')}</td><td style='font-size: 16px; font-weight: bold;'>{item['qty']}</td></tr>"

    html_content = f"""
    <div class="triple-print-wrapper">
        <style>
            @page {{ size: A5 portrait; margin: 5mm; }}
            @media print {{
                body {{ direction: rtl; background: #fff; color: #000; padding: 0; margin: 0; }}
                header, [data-testid="stSidebar"], [data-testid="stHeader"], .no-print-zone, .stButton, .download-btn-area {{ display: none !important; }}
                .invoice-page {{ width: 148mm; height: auto; min-height: 200mm; box-sizing: border-box; padding: 8mm !important; margin: 0 0 10mm 0 !important; page-break-after: always; border: none !important; box-shadow: none !important; }}
                tr {{ page-break-inside: avoid; }}
            }}
            .triple-print-wrapper {{ direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; }}
            .invoice-page {{ width: 148mm; max-width: 100%; border: 2px solid #000; padding: 20px; margin: 20px auto; background: #fff; color: #000; box-sizing: border-box; page-break-after: always; position: relative; }}
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
                        msg_text = f"عزيزي العميل: {selected_cust}\nتم استلام مبلغ: {pay_amt} جنيهاً مصرياً بحسابكم بطريقة ({pay_method}).\nرقم الحركة: {coll_id}\nالتاريخ: {current_time_str}\nالمديونية المتبقية بذمتكم هي: {new_debt_after_pay:,.2f} جنيه.\nشكراً لتعاملكم مع {SHOWROOM_NAME}."
                        st.info(f"📨 تم إرسال رسالة نصية تفصيلية إلى رقم هاتف العميل ({cust_phone if cust_phone else 'غير مسجل'}):\n\n \"{msg_text}\"")
                        
                        if cust_phone and cust_phone != "nan" and cust_phone != "":
                            clean_phone = cust_phone
                            if clean_phone.startswith("0"): clean_phone = "2" + clean_phone
                            encoded_msg = urllib.parse.quote(msg_text)
                            whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
                            st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display: block; width: 100%; text-align: center; background-color: #25D366; color: white; padding: 12px; font-weight: bold; text-decoration: none; border-radius: 5px; margin-top: 10px;">🟢 اضغط هنا لفتح وتأكيد إرسال رسالة الـ WhatsApp للعميل فوراً</a>', unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ لم يتم تفعيل واتساب لعدم وجود رقم هاتف صحيح.")
                        st.rerun()

    # --- 5. حركة فواتير الشراء ---
    elif "حركة فواتير الشراء" in choice:
        st.header("📥 تسجيل وإدخال فواتير شراء بضائع جديدة")
        if inv_df.empty:
            st.info("يرجى إضافة أو رفع تكويد الأصناف أولاً في صفحة إدارة المخزن قبل تسجيل فواتير المشتريات.")
        else:
            with st.form("purchase_form"):
                p_inv_id = st.text_input("رقم فاتورة الشراء (من المورد)", value=str(int(datetime.now().timestamp())))
                p_supplier = st.text_input("اسم المورد / الشركة", value="مورد عام")
                p_code = st.selectbox("اختر الصنف المراد شراؤه", inv_df["كود الصنف"].values, format_func=safe_item_format)
                p_qty = st.number_input("الكمية المشتراة", min_value=1, step=1, value=st.session_state.form_purchase_qty)
                p_price = st.number_input("سعر شراء الوحدة المعتمد", min_value=0.0, step=1.0)
                
                if st.form_submit_button("📥 ترحيل الفاتورة وزيادة رصيد المخزن فوراً"):
                    match_inv = inv_df[inv_df["كود الصنف"] == p_code]
                    p_name = match_inv.iloc[0]["اسم الصنف"]
                    p_cat = match_inv.iloc[0]["تصنيف الصنف"]
                    p_unit = match_inv.iloc[0]["نوع الوحدة"]
                    p_wh = match_inv.iloc[0]["موقع المخزن"]
                    
                    total_p = p_qty * p_price
                    current_date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    new_p_row = pd.DataFrame([{
                        "رقم الفاتورة": p_inv_id, "التاريخ": current_date_str, "المورد": p_supplier, "كود الصنف": p_code,
                        "الصنف": p_name, "تصنيف الصنف": p_cat, "نوع الوحدة": p_unit, "موقع المخزن": p_wh,
                        "سعر الشراء المعتمد": p_price, "الكمية": p_qty, "إجمالي الشراء": total_p, "المسؤول": st.session_state.user
                    }])
                    
                    st.session_state.purchases_df = pd.concat([purchases_df, new_p_row], ignore_index=True)
                    st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                    
                    row_idx = inv_df[inv_df["كود الصنف"] == p_code].index[0]
                    st.session_state.inv_df.at[row_idx, "الكمية"] += int(p_qty)
                    st.session_state.inv_df.at[row_idx, "سعر الشراء"] = float(p_price)
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success(f"🎉 تم ترحيل فاتورة الشراء بنجاح وزيادة كمية الصنف ({p_name}) بمقدار {p_qty} قطعة!")
                    st.rerun()

    # --- 6. صفحة حركة فواتير البيع (تتضمن الآن ميزة التعديل وإدارة أسعار الشراء) ---
    elif "حركة فواتير البيع" in choice:
        st.header("📤 نظام مبيعات وعمليات فواتير البيع")
        
        # إنشاء التبويبين (إنشاء / تعديل)
        t_create_sale, t_edit_sale = st.tabs(["📤 إنشاء فاتورة بيع جديدة", "✏️ تعديل فاتورة بيع سابقة"])
        
        with t_create_sale:
            if inv_df.empty:
                st.info("المخزن فارغ! يرجى إضافة سلع أولاً.")
            else:
                st.subheader("🛒 سلة مبيعات الفاتورة الحالية")
                
                col_item1, col_item2, col_item3, col_item4 = st.columns([3, 1, 1, 1])
                sale_code = col_item1.selectbox("اختر المنتج للبيع", inv_df["كود الصنف"].values, format_func=safe_item_format, key="sale_item_box")
                
                match_row = inv_df[inv_df["كود الصنف"] == sale_code].iloc[0]
                available_qty = int(match_row["الكمية"])
                default_sale_price = float(match_row["سعر البيع"])
                default_purchase_price = float(match_row["سعر الشراء"])
                
                st.caption(f"💡 الكمية المتوفرة بالمخزن حالياً لهذا الصنف: **{available_qty} قطعة**")
                
                sale_qty = col_item2.number_input("الكمية المطلوبة", min_value=1, step=1, value=1, key="sale_qty_box")
                sale_price = col_item3.number_input("سعر البيع المعتمد", min_value=0.0, value=default_sale_price, key="sale_price_box")
                sale_disc = col_item4.number_input("خصم % للصنف", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="sale_disc_box")
                
                if st.button("➕ إضافة البند للسلة الحالية", use_container_width=True):
                    if sale_qty > available_qty:
                        st.error(f"🚨 لا يمكن إضافة البند! الكمية المتاحة بالمخازن ({available_qty}) أقل من كمية الطلب.")
                    else:
                        sub_tot = sale_qty * sale_price
                        f_tot = sub_tot - (sub_tot * (sale_disc / 100))
                        total_purchase_cost = sale_qty * default_purchase_price
                        item_profit = f_tot - total_purchase_cost
                        
                        st.session_state.cart.append({
                            "code": sale_code, "item_name": match_row["اسم الصنف"], "category": match_row["تصنيف الصنف"],
                            "unit": match_row["نوع الوحدة"], "warehouse_loc": match_row["موقع المخزن"], "qty": sale_qty,
                            "price": sale_price, "discount": sale_disc, "final_total": f_tot, "purchase_cost_total": total_purchase_cost, "profit": item_profit
                        })
                        st.success(f"✅ تم إدراج الصنف {match_row['اسم الصنف']} بالسلة.")
                        st.rerun()
                
                if st.session_state.cart:
                    st.markdown("### 📋 الأصناف المدرجة بالسلة حالياً")
                    cart_df = pd.DataFrame(st.session_state.cart)
                    st.dataframe(cart_df[["code", "item_name", "qty", "price", "discount", "final_total"]], use_container_width=True)
                    
                    if st.button("❌ تفريغ وإلغاء السلة تماماً"):
                        st.session_state.cart = []
                        st.rerun()
                        
                    st.markdown("---")
                    st.subheader("👤 بيانات العميل ونظام ترحيل واستحقاق الفاتورة")
                    
                    fc1, fc2, fc3 = st.columns(3)
                    cust_name = fc1.text_input("اسم العميل الثلاثي", value=st.session_state.form_sale_cust_name).strip()
                    cust_phone = fc2.text_input("رقم هاتف العميل", value=st.session_state.form_sale_cust_phone).strip()
                    cust_address = fc3.text_input("عنوان العميل بالتفصيل", value=st.session_state.form_sale_cust_address).strip()
                    
                    fc4, fc5, fc6 = st.columns(3)
                    payment_type = fc4.selectbox("نوع وعقد البيع", ["نقدي (كاش)", "آجل (على الحساب)"])
                    
                    collect_system = "غير محدد"
                    collect_date = "غير محدد"
                    paid_advance = 0.0
                    remaining_bal = 0.0
                    
                    total_cart_sum = sum(x["final_total"] for x in st.session_state.cart)
                    
                    if payment_type == "آجل (على الحساب)":
                        collect_system = fc5.selectbox("جدولة ونظام التحصيل", ["قسط أسبوعي", "قسط شهري", "دفعات مرنة", "دفعة واحدة مؤجلة"])
                        collect_date = fc6.text_input("تاريخ استحقاق المديونية", value=datetime.now().strftime("%Y-%m-%d"))
                        
                        cc1, cc2 = st.columns(2)
                        paid_advance = cc1.number_input("المدفوع مقدماً (جدية حجز / كاش)", min_value=0.0, max_value=float(total_cart_sum), value=0.0)
                        remaining_bal = total_cart_sum - paid_advance
                        cc2.metric("⚠️ المتبقي في ذمة العميل (آجل)", f"{remaining_bal:,.2f} جنيه")
                    else:
                        paid_advance = total_cart_sum
                        remaining_bal = 0.0
                        
                    st.markdown(f"### 💰 إجمالي قيمة الفاتورة النهائي: <span style='color:blue; font-weight:bold;'>{total_cart_sum:,.2f} جنيه</span>", unsafe_allow_html=True)
                    
                    if st.button("🚀 إصدار، ترحيل، وحفظ الفاتورة نهائياً وتحديث المخازن", use_container_width=True):
                        if not cust_name:
                            st.error("يرجى إدخال اسم العميل أولاً لإتمام الفاتورة.")
                        else:
                            new_invoice_id = "INV-" + str(int(datetime.now().timestamp()))
                            current_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            new_sales_entries = []
                            for cart_item in st.session_state.cart:
                                new_sales_entries.append({
                                    "رقم الفاتورة": new_invoice_id, "التاريخ": current_datetime_str, "اسم العميل": cust_name,
                                    "هاتف العميل": cust_phone, "العنوان": cust_address, "نوع البيع": payment_type,
                                    "نظام التحصيل": collect_system, "تاريخ التحصيل": collect_date, "المدفوع مقدم": paid_advance,
                                    "المتبقي": remaining_bal, "كود الصنف": cart_item["code"], "الصنف": cart_item["item_name"],
                                    "تصنيف الصنف": cart_item["category"], "نوع الوحدة": cart_item["unit"], "موقع المخزن": cart_item["warehouse_loc"],
                                    "الكمية": cart_item["qty"], "سعر الوحدة": cart_item["price"], "الخصم %": cart_item["discount"],
                                    "إجمالي البيع": cart_item["final_total"], "تكلفة الشراء الإجمالية": cart_item["purchase_cost_total"],
                                    "صافي ربح الفاتورة": cart_item["profit"], "المسؤول": st.session_state.user
                                })
                                
                                row_idx = inv_df[inv_df["كود الصنف"] == cart_item["code"]].index[0]
                                st.session_state.inv_df.at[row_idx, "الكمية"] -= int(cart_item["qty"])
                                
                            st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                            
                            updated_sales_df = pd.concat([sales_df, pd.DataFrame(new_sales_entries)], ignore_index=True)
                            st.session_state.sales_df = updated_sales_df
                            st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                            
                            st.success(f"🚀 تم ترحيل الفاتورة {new_invoice_id} وحفظ القيود المالية وتحديث الجرد الحركي للمخازن!")
                            
                            html_invoice = generate_triple_invoice_html(
                                new_invoice_id, current_datetime_str, cust_name, cust_phone, cust_address,
                                payment_type, collect_system, collect_date, paid_advance, remaining_bal,
                                st.session_state.user, st.session_state.cart, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER
                            )
                            st.markdown(html_invoice, unsafe_allow_html=True)
                            st.markdown(get_download_link(html_invoice, f"invoice_{new_invoice_id}.html"), unsafe_allow_html=True)
                            
                            st.session_state.cart = []
                            st.session_state.form_sale_cust_name = ""
                            st.session_state.form_sale_cust_phone = ""
                            st.session_state.form_sale_cust_address = ""
                else:
                    st.info("سلة المبيعات فارغة، قم باختيار الأصناف من الأعلى لإدراجها هنا.")

        with t_edit_sale:
            st.subheader("🛠️ بند تعديل فواتير البيع وإدارة أسعار الشراء")
            if sales_df.empty:
                st.info("لا توجد فواتير بيع مسجلة لتعديلها.")
            else:
                # اختيار رقم الفاتورة المراد تعديلها
                invoice_list = sales_df["رقم الفاتورة"].unique()
                selected_inv_id = st.selectbox("اختر رقم الفاتورة للبدء بالتعديل عليها:", invoice_list, key="edit_sale_select")
                
                # جلب البنود الخاصة بهذه الفاتورة
                invoice_items = sales_df[sales_df["رقم الفاتورة"] == selected_inv_id].copy()
                
                st.write("📋 **جدول التعديل التفاعلي:** (عدل أسعار الشراء، البيع، أو الكميات مباشرة)")
                
                # الأعمدة المحددة التي تشمل أسعار وتكلفة الشراء
                columns_to_show = [
                    "كود الصنف", "الصنف", "الكمية", "سعر الوحدة", 
                    "الخصم %", "تكلفة الشراء الإجمالية", "إجمالي البيع", "صافي ربح الفاتورة"
                ]
                
                # تفعيل محرر البيانات وتحديد الحقول المفتوحة للتعديل والحقول المغلقة
                edited_items_df = st.data_editor(
                    invoice_items[columns_to_show], 
                    use_container_width=True, 
                    disabled=["كود الصنف", "الصنف", "إجمالي البيع", "صافي ربح الفاتورة"],
                    key="sales_data_editor"
                )
                
                if st.button("💾 حفظ وتحديث الفاتورة وإعادة احتساب الأرباح حركياً"):
                    # إعادة معالجة القيود والحسابات والأرباح بناءً على تعديل المستخدم
                    for idx, row in edited_items_df.iterrows():
                        orig_idx = invoice_items.index[idx]
                        
                        qty = float(row["الكمية"])
                        price = float(row["سعر الوحدة"])
                        disc = float(row["الخصم %"])
                        purchase_cost = float(row["تكلفة الشراء الإجمالية"]) # يظهر للتحكم وتعديل سعر الشراء
                        
                        # حساب المعادلة المالية الجديدة للبيع والأرباح
                        sub_total = qty * price
                        final_sale = sub_total - (sub_total * (disc / 100))
                        net_profit = final_sale - purchase_cost
                        
                        # التحديث الفوري في Session State
                        st.session_state.sales_df.at[orig_idx, "الكمية"] = qty
                        st.session_state.sales_df.at[orig_idx, "سعر الوحدة"] = price
                        st.session_state.sales_df.at[orig_idx, "الخصم %"] = disc
                        st.session_state.sales_df.at[orig_idx, "تكلفة الشراء الإجمالية"] = purchase_cost
                        st.session_state.sales_df.at[orig_idx, "إجمالي البيع"] = final_sale
                        st.session_state.sales_df.at[orig_idx, "صافي ربح الفاتورة"] = net_profit
                    
                    # حفظ التحديثات النهائية في ملف قاعدة البيانات CSV المعتمد
                    st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    st.success(f"🚀 تم تحديث الفاتورة رقم {selected_inv_id} وإعادة احتساب الأرباح حركياً بنجاح!")
                    st.rerun()

    # --- 7. صفحة ارتجاع فواتير البيع ---
    elif "ارتجاع فواتير البيع" in choice:
        st.header("↩️ نظام إدارة وإصدار مرتجعات فواتير البيع")
        if sales_df.empty:
            st.info("لا توجد مبيعات مسجلة للارتجاع.")
        else:
            with st.form("return_form"):
                r_inv_id = st.selectbox("اختر رقم الفاتورة المراد الارتجاع منها", sales_df["رقم الفاتورة"].unique())
                matched_sales = sales_df[sales_df["رقم الفاتورة"] == r_inv_id]
                r_code = st.selectbox("اختر الصنف المراد إرجاعه", matched_sales["كود الصنف"].values, format_func=safe_item_format)
                
                sale_row = matched_sales[matched_sales["كود الصنف"] == r_code].iloc[0]
                max_returnable = int(sale_row["الكمية"])
                item_unit_price = float(sale_row["سعر الوحدة"])
                item_discount = float(sale_row["الخصم %"])
                
                r_qty = st.number_input(f"الكمية المرجعة (الحد الأقصى المسموح به: {max_returnable})", min_value=1, max_value=max_returnable, value=1, step=1)
                
                if st.form_submit_button("↩️ تأكيد وإصدار إذن الارتجاع"):
                    current_date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    r_id = "RET-" + str(int(datetime.now().timestamp()))
                    
                    sub_t = r_qty * item_unit_price
                    refund_amt = sub_t - (sub_t * (item_discount / 100))
                    
                    new_r_row = pd.DataFrame([{
                        "رقم الإرجاع": r_id, "رقم الفاتورة الأصلية": r_inv_id, "التاريخ": current_date_str,
                        "اسم العميل": sale_row["اسم العميل"], "كود الصنف": r_code, "الصنف": sale_row["الصنف"],
                        "الكمية المرجعة": r_qty, "المبلغ المردود": refund_amt, "المسؤول": st.session_state.user
                    }])
                    
                    st.session_state.returns_df = pd.concat([returns_df, new_r_row], ignore_index=True)
                    st.session_state.returns_df.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
                    
                    if r_code in inv_df["كود الصنف"].values:
                        inv_idx = inv_df[inv_df["كود الصنف"] == r_code].index[0]
                        st.session_state.inv_df.at[inv_idx, "الكمية"] += int(r_qty)
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    sales_row_idx = sales_df[(sales_df["رقم الفاتورة"] == r_inv_id) & (sales_df["كود الصنف"] == r_code)].index[0]
                    st.session_state.sales_df.at[sales_row_idx, "الكمية"] -= int(r_qty)
                    
                    old_item_sale_total = float(st.session_state.sales_df.at[sales_row_idx, "إجمالي البيع"])
                    st.session_state.sales_df.at[sales_row_idx, "إجمالي البيع"] = old_item_sale_total - refund_amt
                    
                    old_item_purchase_cost = float(st.session_state.sales_df.at[sales_row_idx, "تكلفة الشراء الإجمالية"])
                    single_item_purchase_cost = old_item_purchase_cost / max_returnable if max_returnable > 0 else 0
                    new_item_purchase_cost = old_item_purchase_cost - (single_item_purchase_cost * r_qty)
                    st.session_state.sales_df.at[sales_row_idx, "تكلفة الشراء الإجمالية"] = new_item_purchase_cost
                    
                    st.session_state.sales_df.at[sales_row_idx, "صافي ربح الفاتورة"] = (old_item_sale_total - refund_amt) - new_item_purchase_cost
                    
                    st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success(f"🎉 تم تسجيل المرتجع بنجاح برقم {r_id} وإعادة السلع إلى المخازن!")
                    st.rerun()

    # --- 8. صفحة البحث عن الفواتير وطباعتها ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 محرك البحث عن الفواتير وطباعتها الذكية (A5)")
        if sales_df.empty:
            st.info("لا توجد فواتير مبيعات مسجلة للبحث عنها.")
        else:
            search_inv_id = st.selectbox("اختر أو ابحث برقم الفاتورة لطباعتها:", sales_df["رقم الفاتورة"].unique())
            
            matched_records = sales_df[sales_df["رقم الفاتورة"] == search_inv_id]
            if matched_records.empty:
                st.warning("لم يتم العثور على أي قيود لهذه الفاتورة.")
            else:
                first_row = matched_records.iloc[0]
                
                st.markdown(f"**📄 تفاصيل أساسية للفاتورة:**")
                st.write(f"العميل: **{first_row['اسم العميل']}** | التاريخ: **{first_row['التاريخ']}** | المسؤول: **{first_row['المسؤول']}** | نوع الدفع: **{first_row['نوع البيع']}**")
                
                st.dataframe(matched_records[["كود الصنف", "الصنف", "الكمية", "سعر الوحدة", "الخصم %", "إجمالي البيع"]], use_container_width=True)
                
                reconstructed_cart = []
                for _, r in matched_records.iterrows():
                    reconstructed_cart.append({
                        "item_name": r["الصنف"], "category": r.get("تصنيف الصنف", "عام"), "unit": r.get("نوع الوحدة", "قطعة"),
                        "warehouse_loc": r.get("موقع المخزن", "الرئيسي"), "qty": int(r["الكمية"]), "price": float(r["سعر الوحدة"]),
                        "discount": float(r["الخصم %"]), "final_total": float(r["إجمالي البيع"])
                    })
                
                if st.button("🖨️ تجهيز وعرض معاينة الفاتورة للطباعة المستقلة"):
                    html_invoice = generate_triple_invoice_html(
                        search_inv_id, first_row['التاريخ'], first_row['اسم العميل'], first_row.get('هاتف العميل', ''),
                        first_row.get('العنوان', ''), first_row['نوع البيع'], first_row.get('نظام التحصيل', 'غير محدد'),
                        first_row.get('تاريخ التحصيل', 'غير محدد'), float(first_row.get('المدفوع مقدم', 0)),
                        float(first_row.get('المتبقي', 0)), first_row['المسؤول'], reconstructed_cart, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER
                    )
                    st.markdown(html_invoice, unsafe_allow_html=True)
                    st.markdown(get_download_link(html_invoice, f"invoice_{search_inv_id}.html"), unsafe_allow_html=True)

    # --- 9. صفحة التقارير والأرباح ---
    elif "تقارير البيع والشراء والأرباح" in choice:
        st.header("📈 لوحة تقارير الأرباح والخسائر وحركات المال")
        
        rep_sales_total = pd.to_numeric(sales_df["إجمالي البيع"], errors='coerce').sum() if not sales_df.empty else 0.0
        rep_purchases_total = pd.to_numeric(purchases_df["إجمالي الشراء"], errors='coerce').sum() if not purchases_df.empty else 0.0
        rep_expenses_total = pd.to_numeric(exp_df["المبلغ"], errors='coerce').sum() if not exp_df.empty else 0.0
        
        gross_profit = pd.to_numeric(sales_df["صافي ربح الفاتورة"], errors='coerce').sum() if not sales_df.empty else 0.0
        net_profit_total = gross_profit - rep_expenses_total
        
        m1, m2, m3 = st.columns(3)
        m1.metric("📊 إجمالي المبيعات (حركة البيع)", f"{rep_sales_total:,.2f} جنيه")
        m2.metric("📥 إجمالي المشتريات البضاعة", f"{rep_purchases_total:,.2f} جنيه")
        m3.metric("💸 إجمالي مصاريف التشغيل والنثرية", f"{rep_expenses_total:,.2f} جنيه")
        
        p1, p2 = st.columns(2)
        p1.metric("💰 مجمل أرباح مبيعات البضائع", f"{gross_profit:,.2f} جنيه")
        p2.metric("🚀 صافي الأرباح النهائية للمؤسسة", f"{net_profit_total:,.2f} جنيه")
        
        st.markdown("---")
        st.subheader("📋 تفاصيل السجلات المالية لحركات المبيعات")
        st.dataframe(sales_df, use_container_width=True)

    # --- 10. صفحة المصاريف ---
    elif "المصاريف" in choice:
        st.header("💸 دفتر قيد حساب المصاريف والنشاط")
        st.dataframe(exp_df, use_container_width=True)
        
        with st.form("exp_form"):
            exp_desc = st.text_input("بيان وجدولة المصروف").strip()
            exp_val = st.number_input("المبلغ المدفوع (جنيه)", min_value=0.0, step=10.0)
            if st.form_submit_button("💾 قيد وحفظ المصروف فوراً"):
                if exp_desc and exp_val > 0:
                    current_date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_exp = pd.DataFrame([{"التاريخ": current_date_str, "البيان": exp_desc, "المبلغ": exp_val, "المسؤول": st.session_state.user}])
                    st.session_state.exp_df = pd.concat([exp_df, new_exp], ignore_index=True)
                    st.session_state.exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم قيد بند المصروف بنجاح!")
                    st.rerun()

    # --- 11. صفحة الحضور والانصراف ---
    elif "الحضور والانصراف" in choice:
        st.header("⏰ نظام الحضور والانصراف الإلكتروني للموظفين")
        st.dataframe(att_df, use_container_width=True)
        
        current_date_today = datetime.now().strftime("%Y-%m-%d")
        current_time_now = datetime.now().strftime("%H:%M:%S")
        
        ac1, ac2 = st.columns(2)
        if ac1.button("🟢 تسجيل إثبات الحضور الآن", use_container_width=True):
            match_att = att_df[(att_df["الموظف"] == st.session_state.user) & (att_df["التاريخ"] == current_date_today)]
            if not match_att.empty:
                st.warning("⚠️ أنت مسجل حضور بالفعل لهذا اليوم!")
            else:
                new_att = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": current_date_today, "وقت الحضور": current_time_now, "وقت الانصراف": "لم ينصرف"}])
                st.session_state.att_df = pd.concat([att_df, new_att], ignore_index=True)
                st.session_state.att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"🌅 تم تسجيل حضورك بنجاح في تمام الساعة {current_time_now}")
                st.rerun()
                
        if ac2.button("🔴 تسجيل إثبات الانصراف الآن", use_container_width=True):
            match_att = att_df[(att_df["الموظف"] == st.session_state.user) & (att_df["التاريخ"] == current_date_today)]
            if match_att.empty:
                st.error("❌ لم تقم بتسجيل الحضور أولاً لتقوم بالانصراف!")
            else:
                idx = match_att.index[0]
                st.session_state.att_df.at[idx, "وقت الانصراف"] = current_time_now
                st.session_state.att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"🌌 تم تسجيل انصرافك بنجاح في تمام الساعة {current_time_now}")
                st.rerun()

    # --- 12. صفحة إدارة وتعديل الصلاحيات والحسابات ---
    elif "إدارة وتعديل الصلاحيات والحسابات" in choice:
        st.header("⚙️ لوحة تحكم الحسابات والصلاحيات والأدوار")
        
        tab_users, tab_roles = st.tabs(["👥 الحسابات الحالية بالنظام", "🔑 لوحة الصلاحيات للأقسام"])
        
        with tab_users:
            u_data = pd.read_csv(USERS_FILE)
            st.dataframe(u_data, use_container_width=True)
            
            st.subheader("➕ إضافة حساب موظف جديد")
            with st.form("add_user_form"):
                new_username = st.text_input("اسم المستخدم الجديد").strip()
                new_password = st.text_input("كلمة المرور الخاصة به").strip()
                new_role = st.selectbox("الرتبة والدور", ["مدير", "مشرف", "موظف"])
                
                if st.form_submit_button("🚀 حفظ الحساب وتفعيل صلاحياته"):
                    if new_username and new_password:
                        if new_username in u_data["username"].values:
                            st.warning("⚠️ اسم المستخدم هذا موجود مسبقاً!")
                        else:
                            updated_u = pd.concat([u_data, pd.DataFrame([{"username": new_username, "password": new_password, "role": new_role}])], ignore_index=True)
                            updated_u.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                            st.success(f"🎉 تم إنشاء حساب الموظف {new_username} بنجاح!")
                            st.rerun()
            
            st.subheader("❌ حذف حساب مستخدم")
            user_to_delete = st.selectbox("اختر الحساب المراد حذفه نهائياً:", u_data["username"].values)
            if user_to_delete == "admin":
                st.error("لا يمكن حذف حساب الأدمن الأساسي لحماية النظام.")
            else:
                if st.button("🔥 تأكيد حذف هذا الحساب فوراً"):
                    updated_u = u_data[u_data["username"] != user_to_delete]
                    updated_u.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
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
                st.success("🚀 تم تحديث وحفظ بيانات الفواتير والدعم بنجاح!")
                st.rerun()
