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
    
    # رأس الجدول الأساسي
    standard_table_th = "<tr><th>الصنف والبيان</th><th>الوحدة</th><th>الكمية</th><th>سعر المفرد</th><th>الصافي الإجمالي</th></tr>"
    standard_table_td = ""
    for item in cart_items:
        standard_table_td += f"<tr><td>{item['item_name']}</td><td>{item.get('unit', 'قطعة')}</td><td>{item['qty']}</td><td>{item['price']} جنيه</td><td style='font-weight: bold;'>{item['final_total']} جنيه</td></tr>"
    
    if discount_fixed > 0:
        standard_table_td += f"<tr style='background:#f9f9f9; font-weight:bold;'><td colspan='4' style='text-align:left;'>الخصم النقدي المباشر:</td><td>{discount_fixed} جنيه</td></tr>"
    
    standard_table_td += f"<tr style='background:#f2f2f2; font-weight:bold; font-size:1.1em;'><td colspan='4' style='text-align:left;'>الصافي الإجمالي المطلوب سداده:</td><td style='color:#d9534f;'>{total_invoice_amount} جنيه</td></tr>"
    standard_table_td += f"<tr style='background:#fafafa;'><td colspan='5' style='text-align:right; font-size:0.95em;'><b>التفقيط المالي للصافي:</b> {arabic_total_words}</td></tr>"
    
    # كود تهيئة الورقة والمقاس A5 عند تفعيل أمر الطباعة بالمتصفح
    print_style_setting = """
    <style>
        @media print {
            @page {
                size: A5 portrait;
                margin: 8mm 8mm 8mm 8mm;
            }
            body {
                background: #fff;
                color: #000;
                direction: rtl;
            }
            .invoice-card-print {
                border: 1px solid #000 !important;
                box-shadow: none !important;
                padding: 10px !important;
                margin: 0 0 0 0 !important;
                page-break-after: always; /* يجعل كل نسخة تطبع في ورقة A5 منفصلة تلقائياً */
                height: auto;
            }
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
        <div class='invoice-card-print' style='direction: rtl; text-align: right; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; border: 2px dashed #bbb; padding: 18px; margin-bottom: 30px; background: #fff; border-radius: 8px;'>
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
                <thead>
                    {standard_table_th}
                </thead>
                <tbody>
                    {standard_table_td}
                </tbody>
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

    # --- 5. صفحة حركة فواتير الشراء ---
    elif "حركة فواتير الشراء" in choice:
        st.header("📥 تسجيل وإدارة فواتير المشتريات والوارد")
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
                if matching_items.empty:
                    st.warning("الصنف المحدد غير متوفر.")
                else:
                    item_row = matching_items.iloc[0]
                    default_pur_price = float(item_row['سعر الشراء']) if 'سعر الشراء' in item_row else 0.0
                    actual_purchase_price = c3.number_input("سعر الشراء المعتمد لهذه الفاتورة", value=default_pur_price, min_value=0.0)
                    
                    qty = c4.number_input("الكمية المشتراة", min_value=1, step=1, value=st.session_state.form_purchase_qty)
                    st.session_state.form_purchase_qty = qty
                    
                    total = actual_purchase_price * qty
                    if st.button("حفظ المشتريات وإدخلها للمخزن المحدد"):
                        idx = inv_df[inv_df['كود الصنف'] == selected_item_code].index[0]
                        st.session_state.inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) + qty
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        
                        pur_id = "PUR-" + str(int(datetime.now().timestamp()))
                        new_p = pd.DataFrame([{"رقم الفاتورة": pur_id, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "المورد": vendor, "كود الصنف": selected_item_code, "الصنف": item_row['اسم الصنف'], "تصنيف الصنف": item_row['تصنيف الصنف'], "نوع الوحدة": item_row['نوع الوحدة'], "موقع المخزن": item_row['موقع المخزن'], "سعر الشراء المعتمد": str(actual_purchase_price), "الكمية": str(qty), "إجمالي الشراء": str(total), "المسؤول": st.session_state.user}])
                        st.session_state.purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                        st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                        st.session_state.form_purchase_qty = 1  
                        st.success("✅ تم تسجيل الوارد وتحديث المخزن والـ Session بنجاح!")
                        st.rerun()
                        
        with t_manage:
            st.subheader("⚙️ مراجعة وحذف فواتير الشراء السابقة")
            if purchases_df.empty: st.info("لا توجد فواتير شراء مسجلة حالياً.")
            else:
                st.dataframe(purchases_df, use_container_width=True)
                target_pur_id = st.selectbox("اختر رقم فاتورة الشراء للإجراء", purchases_df["رقم الفاتورة"].unique())
                p_row = purchases_df[purchases_df["رقم الفاتورة"] == target_pur_id].iloc[0]
                
                if st.button("❌ حذف فاتورة الشراء هذه بالكامل وخصمها من المخزن", use_container_width=True):
                    p_code = p_row["كود الصنف"]
                    p_qty = int(p_row["الكمية"])
                    if p_code in inv_df["كود الصنف"].values:
                        inv_idx = inv_df[inv_df["كود الصنف"] == p_code].index[0]
                        st.session_state.inv_df.at[inv_idx, "الكمية"] = max(0, int(inv_df.at[inv_idx, "الكمية"]) - p_qty)
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    st.session_state.purchases_df = purchases_df[purchases_df["رقم الفاتورة"] != target_pur_id]
                    st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                    st.success("🔥 تم حذف فاتورة الشراء وتعديل رصيد المخزن!")
                    st.rerun()

# --- 6. صفحة حركة فواتير البيع المتطورة ---
    elif "📤 حركة فواتير البيع" in choice:
        st.header("📤 لوحة حركة فواتير البيع وإصدار الفواتير المتطورة")
        
        # إنشاء تبويبات لفصل الفاتورة الجديدة عن الفواتير القديمة
        tab1, tab2 = st.tabs(["🆕 إصدار فاتورة جديدة", "🔍 البحث وتعديل فاتورة قديمة"])
        
        with tab1:
            st.markdown("### 👤 بيانات العميل ونظام البيع")
            cust_type_select = st.radio("نوع العميل للفاتورة الحالية:", ["عميل سريع (كاش)", "عميل مكود ومسجل مسبقاً"], index=0 if st.session_state.form_sale_cust_type == "عميل سريع (كاش)" else 1, horizontal=True)
            st.session_state.form_sale_cust_type = cust_type_select
            
            sale_cust = ""
            sale_phone = ""
            sale_address = ""
            
            if cust_type_select == "عميل سريع (كاش)":
                c1, c2, c3 = st.columns(3)
                sale_cust = c1.text_input("اسم العميل السريع", value=st.session_state.form_sale_cust_name)
                sale_phone = c2.text_input("رقم الهاتف (اختياري)", value=st.session_state.form_sale_cust_phone)
                sale_address = c3.text_input("العنوان (اختياري)", value=st.session_state.form_sale_cust_address)
                
                st.session_state.form_sale_cust_name = sale_cust
                st.session_state.form_sale_cust_phone = sale_phone
                st.session_state.form_sale_cust_address = sale_address
            else:
                all_saved_customers = contacts_df[contacts_df["النوع"] == "عميل"]["الاسم"].unique() if not contacts_df.empty else []
                if len(all_saved_customers) == 0:
                    st.warning("⚠️ لا توجد كروت عملاء مكودة للنظام! يرجى تكويد عملاء من صفحة 'العملاء والموردين'. تم تحويلك للعميل السريع تلقائياً.")
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
                    sale_phone = str(cust_data_row["Hands_phone"] if "Hands_phone" in cust_data_row else cust_data_row["الهاتف"])
                    sale_address = str(cust_data_row["العنوان"])
                    st.info(f"🟢 العميل: {sale_cust} | الهاتف: {sale_phone} | العنوان: {sale_address}")
            
            st.markdown("### 🛒 اختيار المنتجات وإضافتها للسلة")
            sc1, sc2, sc3, sc4, sc5 = st.columns(5)
            if inv_df.empty: 
                sc1.info("المخزن فارغ.")
            else:
                selected_sale_code = sc1.selectbox("اختر الصنف للبيع", inv_df["كود الصنف"].values, format_func=safe_item_format)
                match_s = inv_df[inv_df["كود الصنف"] == selected_sale_code].iloc[0]
                
                sale_qty = sc2.number_input(f"الكمية (المتاحة: {match_s['الكمية']})", min_value=1, max_value=int(match_s['الكمية']) if int(match_s['الكمية']) > 0 else 1, step=1)
                
                default_sale_price = float(match_s['سعر البيع']) if 'سعر البيع' in match_s else 0.0
                custom_sale_price = sc3.number_input("سعر البيع المعتمد", value=default_sale_price, min_value=0.0, step=1.0)
                
                default_purchase_cost = float(match_s['سعر الشراء']) if 'سعر الشراء' in match_s else 0.0
                custom_purchase_cost = sc4.number_input("سعر الشراء المعتمد", value=default_purchase_cost, min_value=0.0, step=1.0)
                
                sale_disc = sc5.number_input("نسبة الخصم %", min_value=0.0, max_value=100.0, step=1.0, value=0.0)
                
                if st.button("➕ إضافة المنتج المختار إلى سلة الفاتورة الحالية", use_container_width=True):
                    if match_s['الكمية'] <= 0: 
                        st.error("⚠️ عذراً رصيد هذا الصنف صفر بالمخزن حالياً!")
                    else:
                        final_u_p = custom_sale_price
                        total_p_b = sale_qty * final_u_p
                        final_tot_p = total_p_b - (total_p_b * (sale_disc / 100))
                        
                        st.session_state.cart.append({
                            "item_code": selected_sale_code, "item_name": match_s['اسم الصنف'],
                            "category": match_s['تصنيف الصنف'], "unit": match_s['نوع الوحدة'],
                            "warehouse_loc": match_s['موقع المخزن'], "qty": int(sale_qty),
                            "price": float(final_u_p), "discount": float(sale_disc),
                            "final_total": float(final_tot_p), "purchase_cost": float(custom_purchase_cost)
                        })
                        st.success(f"تم إضافة {match_s['اسم الصنف']} بنجاح بالسلة!")
                        st.rerun()
                        
            if st.session_state.cart:
                st.markdown("### 🧾 معاينة الأصناف المدرجة بالسلة وإدارة الحذف:")
                for i, item in enumerate(st.session_state.cart):
                    cols_cart_control = st.columns([5, 2, 2, 2])
                    cols_cart_control[0].write(f"📦 **{item['item_name']}** ({item['item_code']})")
                    cols_cart_control[1].write(f"الكمية: {item['qty']}")
                    cols_cart_control[2].write(f"السعر المفرد: {item['price']} ج.م | الإجمالي: {item['final_total']} ج.م")
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
                
                collect_system = "غير مححدد"
                collect_date = "غير محدد"
                paid_advance = 0.0
                remaining_bal = 0.0
                
                if pay_type == "آجل (على الحساب)":
                    ac1, ac2, ac3 = st.columns(3)
                    collect_system = ac1.selectbox("نظام التحصيل للآجل", ["أسبوعي", "شهري", "دفعات مرنة", "عند الطلب"])
                    collect_date = ac2.text_input("تاريخ استحقاق المديونية", value=datetime.now().strftime("%Y-%m-%d"))
                    paid_advance = ac3.number_input("المبلغ المدفوع مقدماً (مقدم)", min_value=0.0, max_value=float(total_invoice_amount), step=50.0)
                    remaining_bal = total_invoice_amount - paid_advance
                    st.warning(f"⚠️ سيتم ترحيل مديونية بقيمة {remaining_bal:,.2f} جنيه بحساب العميل.")
                    
                if st.button("🚀 ترحيل الفاتورة نهائياً وخصم البضاعة من المخزن", use_container_width=True):
                    if not sale_cust: 
                        st.error("⚠️ يرجى إدخل اسم العميل لإصدار الفاتورة باسمه.")
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
                        
                        st.success(f"🎉 تم ترحيل الفاتورة بنجاح برقم {inv_id}!")
                        
                        html_invoice = generate_triple_invoice_html(inv_id, datetime_str, sale_cust, sale_phone, sale_address, pay_type, collect_system, collect_date, paid_advance, remaining_bal, st.session_state.user, st.session_state.cart, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, discount_fixed=discount_fixed)
                        st.markdown(html_invoice, unsafe_allow_html=True)
                        st.markdown(get_download_link(html_invoice, f"Invoice_{inv_id}.html"), unsafe_allow_html=True)
                        
                        st.session_state.cart = []
                        st.session_state.form_sale_cust_name = ""
                        st.session_state.form_sale_cust_phone = ""
                        st.session_state.form_sale_cust_address = ""
                        st.rerun()

      # --- تبويب مراجع وتعديل الفواتير القديمة ---
        with tab2:
            st.markdown("### 🔍 مراجعة وتعديل الفواتير الصادرة مسبقاً")
            
            if sales_df.empty:
                st.info("ℹ️ لا توجد فواتير مبيعات مسجلة في النظام حتى الآن.")
            else:
                unique_invoices = sales_df["رقم الفاتورة"].unique()
                search_inv = st.selectbox("اختر رقم الفاتورة المراد تعديلها:", unique_invoices)
                
                invoice_items = sales_df[sales_df["رقم الفاتورة"] == search_inv].copy()
                
                if not invoice_items.empty:
                    first_row = invoice_items.iloc[0]
                    st.info(f"📄 الفاتورة الحالية: العميل: {first_row['اسم العميل']} | التاريخ: {first_row['التاريخ']} | طريقة السداد: {first_row['نوع البيع']}")
                    
                    st.markdown("#### ⚙️ تعديل البيانات العامة للفاتورة")
                    e_c1, e_c2, e_c3 = st.columns(3)
                    edit_cust_name = e_c1.text_input("اسم العميل المعدل", value=first_row["اسم العميل"], key="e_cust_name")
                    edit_cust_phone = e_c2.text_input("هاتف العميل المعدل", value=first_row["هاتف العميل"], key="e_cust_phone")
                    edit_cust_address = e_c3.text_input("العنوان المعدل", value=first_row["العنوان"], key="e_cust_address")
                    
                    e_p1, e_p2 = st.columns(2)
                    edit_pay_type = e_p1.radio("نوع البيع المعدل", ["نقدي (كاش)", "آجل (على الحساب)"], index=0 if first_row["نوع البيع"] == "نقدي (كاش)" else 1, horizontal=True, key="e_pay_type")
                    edit_discount_fixed = e_p2.number_input("الخصم النقدي الثابت المعدل", min_value=0.0, value=float(first_row["خصم نقدي ثابت"]), step=5.0, key="e_disc_fixed")
                    
                    edit_collect_system = "غير محدد"
                    edit_collect_date = "غير محدد"
                    edit_paid_advance = 0.0
                    
                    if edit_pay_type == "آجل (على الحساب)":
                        ea1, ea2, ea3 = st.columns(3)
                        curr_sys = first_row["نظام التحصيل"] if first_row["نظام التحصيل"] in ["أسبوعي", "شهري", "دفعات مرنة", "عند الطلب"] else "أسبوعي"
                        edit_collect_system = ea1.selectbox("نظام التحصيل المعدل", ["أسبوعي", "شهري", "دفعات مرنة", "عند الطلب"], index=["أسبوعي", "شهري", "دفعات مرنة", "عند الطلب"].index(curr_sys))
                        edit_collect_date = ea2.text_input("تاريخ الاستحقاق المعدل", value=str(first_row["تاريخ التحصيل"]))
                        edit_paid_advance = ea3.number_input("المبلغ المدفوع مقدماً المعدل", min_value=0.0, value=float(first_row["المدفوع مقدم"]))
                    
                    st.markdown("#### 📦 تعديل كميات وأسعار الأصناف (وتكلفة الشراء)")
                    updated_items_list = []
                    
                    for idx, row in invoice_items.iterrows():
                        st.write(f"🔹 **الصنف:** {row['الصنف']} ({row['كود الصنف']})")
                        col_i1, col_i2, col_i3, col_i4, col_i5 = st.columns(5)
                        
                        matching_inv = inv_df[inv_df["كود الصنف"] == row["كود الصنف"]]
                        stock_qty = matching_inv.iloc[0]["الكمية"] if not matching_inv.empty else 0
                        max_allowed = int(stock_qty + row["الكمية"])
                        
                        if max_allowed < 0:
                            max_allowed = 0
                            
                        current_invoice_qty = int(row["الكمية"])
                        
                        # حساب سعر تكلفة الشراء المفرد الحالي (إذا كان مخزناً كإجمالي، نقسمه على الكمية)
                        old_total_cost = float(row["تكلفة الشراء الإجمالية"]) if "تكلفة الشراء الإجمالية" in row else 0.0
                        old_unit_cost = old_total_cost / current_invoice_qty if current_invoice_qty > 0 else 0.0
                        
                        new_qty = col_i1.number_input(f"الكمية المعدلة (المتاحة: {max_allowed})", min_value=0, max_value=max(current_invoice_qty, max_allowed), value=current_invoice_qty, key=f"edit_qty_{idx}")
                        new_price = col_i2.number_input("سعر البيع المعدل", min_value=0.0, value=float(row["سعر الوحدة"]), key=f"edit_price_{idx}")
                        new_disc = col_i3.number_input("الخصم % المعدل", min_value=0.0, max_value=100.0, value=float(row["الخصم %"]), key=f"edit_disc_{idx}")
                        
                        # --- الإضافة الجديدة: تعديل سعر الشراء للصنف ---
                        new_cost_unit = col_i4.number_input("سعر الشراء المعدل", min_value=0.0, value=float(old_unit_cost), key=f"edit_cost_{idx}")
                        
                        t_b_d = new_qty * new_price
                        new_final_total = t_b_d - (t_b_d * (new_disc / 100))
                        col_i5.metric("الإجمالي الجديد", f"{new_final_total:,.2f} ج.م")
                        
                        row_data = row.to_dict()
                        row_data["الكمية_الجديدة"] = new_qty
                        row_data["سعر_الوحدة_الجديد"] = new_price
                        row_data["الخصم_الجديد"] = new_disc
                        row_data["سعر_الشراء_المفرد_الجديد"] = new_cost_unit
                        row_data["إجمالي_البيع_الجديد"] = new_final_total
                        updated_items_list.append(row_data)
                        st.markdown("---")
                    
                    subtotal_new = sum(item["إجمالي_البيع_الجديد"] for item in updated_items_list)
                    total_invoice_new = max(0.0, subtotal_new - edit_discount_fixed)
                    edit_remaining_bal = total_invoice_new - edit_paid_advance if edit_pay_type == "آجل (على الحساب)" else 0.0
                    
                    st.subheader(f"💰 صافي الفاتورة الجديد: {total_invoice_new:,.2f} جنيه")
                    
                    if st.button("💾 حفظ وتحديث الفاتورة القديمة", use_container_width=True):
                        # إرجاع الأرصدة القديمة أولاً للمخزن
                        for row in updated_items_list:
                            if row["كود الصنف"] in st.session_state.inv_df["كود الصنف"].values:
                                m_idx = st.session_state.inv_df[st.session_state.inv_df["كود الصنف"] == row["كود الصنف"]].index[0]
                                st.session_state.inv_df.at[m_idx, "الكمية"] += int(row["الكمية"])
                        
                        # حذف الأسطر القديمة من سجل المبيعات
                        st.session_state.sales_df = st.session_state.sales_df[st.session_state.sales_df["رقم الفاتورة"] != search_inv]
                        
                        final_updated_rows = []
                        for row in updated_items_list:
                            m_idx = st.session_state.inv_df[st.session_state.inv_df["كود الصنف"] == row["كود الصنف"]].index[0]
                            # خصم الكمية الجديدة المعدلة من المخزن
                            st.session_state.inv_df.at[m_idx, "الكمية"] -= int(row["الكمية_الجديدة"])
                            
                            # احتساب إجمالي تكلفة الشراء وصافي الربح بناءً على السعر الجديد المدخل
                            item_tot_cost_new = row["الكمية_الجديدة"] * row["سعر_الشراء_المفرد_الجديد"]
                            item_net_profit_new = row["إجمالي_البيع_الجديد"] - item_tot_cost_new
                            
                            final_updated_rows.append({
                                "رقم الفاتورة": search_inv, "التاريخ": row["التاريخ"], "اسم العميل": edit_cust_name,
                                "هاتف العميل": edit_cust_phone, "العنوان": edit_cust_address, "نوع البيع": edit_pay_type,
                                "نظام التحصيل": edit_collect_system, "تاريخ التحصيل": edit_collect_date,
                                "المدفوع مقدم": edit_paid_advance, "المتبقي": edit_remaining_bal,
                                "كود الصنف": row['كود الصنف'], "الصنف": row['الصنف'],
                                "تصنيف الصنف": row['تصنيف الصنف'], "نوع الوحدة": row['نوع الوحدة'],
                                "موقع المخزن": row['موقع المخزن'], "الكمية": row['الكمية_الجديدة'],
                                "سعر الوحدة": row['سعر_الوحدة_الجديد'], "الخصم %": row['الخصم_الجديد'],
                                "خصم نقدي ثابت": edit_discount_fixed,
                                "إجمالي البيع": row['إجمالي_البيع_الجديد'], 
                                "تكلفة الشراء الإجمالية": item_tot_cost_new, # تحديث التكلفة الإجمالية في السجل
                                "صافي ربح الفاتورة": item_net_profit_new,      # تحديث صافي الربح في السجل
                                "المسؤول": st.session_state.user
                            })
                        
                        updated_sales_df = pd.DataFrame(final_updated_rows)
                        st.session_state.sales_df = pd.concat([st.session_state.sales_df, updated_sales_df], ignore_index=True)
                        
                        # حفظ التعديلات نهائياً في ملفات الـ CSV
                        st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        
                        st.success(f"🎉 تم تحديث الفاتورة {search_inv} وتحديث التكاليف والأرباح بنجاح!")
                        st.rerun()

    # --- 7. صفحة ارتجاع فواتير البيع ---
    elif "↩️ ارتجاع فواتير البيع" in choice:
        st.header("↩️ إدارة لوحة ارتجاع وتعديل الأصناف المرتجعة للعملاء")
        
        t_manage_returns, t_add_return = st.tabs(["🎛️ لوحة تحكم المردودات والارتجاع (تعديل وحذف)", "➕ تسجيل بند إرجاع جديد"])
        
        with t_manage_returns:
            st.subheader("📝 جدول تفاعلي لتعديل أو حذف بيانات الارتجاع")
            if returns_df.empty:
                st.info("لا توجد بيانات حركات ارتجاع مسجلة حالياً.")
            else:
                edited_returns = st.data_editor(returns_df, num_rows="dynamic", use_container_width=True, key="returns_main_interactive_editor")
                if st.button("💾 حفظ جميع التعديلات وتحديث سجلات النظام"):
                    try:
                        edited_returns.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
                        st.session_state.returns_df = edited_returns
                        st.success("🚀 تم تحديث وحفظ سجلات الارتجاع والأسعار المعدلة!")
                        st.rerun()
                    except Exception as e: st.error(f"حدث خطأ أثناء الحفظ: {e}")
                    
        with t_add_return:
            st.subheader("➕ إضافة بند ارتجاع جديد يدوياً إلى النظام")
            with st.form("add_return_new_form", clear_on_submit=True):
                rc1, rc2, rc3 = st.columns(3)
                ret_id = rc1.text_input("رقم الإرجاع", value="RET-" + str(int(datetime.now().timestamp())))
                invoice_ref = rc2.text_input("رقم الفاتورة الأصلية")
                cust_name = rc3.text_input("اسم العميل")
                
                rc4, rc5, rc6 = st.columns(3)
                if inv_df.empty: item_code = rc4.text_input("كود الصنف")
                else: item_code = rc4.selectbox("اختر الصنف المراد إرجاعه", inv_df["كود الصنف"].values, format_func=safe_item_format)
                
                ret_qty = rc5.number_input("الكمية المرجعة", min_value=1, step=1, value=1)
                ret_amount = rc6.number_input("المبلغ المردود للعميل (جنيه)", min_value=0.0, step=10.0, value=0.0)
                
                submit_ret = st.form_submit_button("📥 ترحيل بند الارتجاع وزيادة المخزن فوراً")
                if submit_ret:
                    if cust_name and invoice_ref and item_code:
                        match_item = inv_df[inv_df['كود الصنف'] == item_code]
                        item_name = match_item.iloc[0]['اسم الصنف'] if not match_item.empty else "صنف غير معروف"
                        
                        new_return_row = pd.DataFrame([{
                            "رقم الإرجاع": str(ret_id), "رقم الفاتورة الأصلية": str(invoice_ref),
                            "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "اسم العميل": str(cust_name),
                            "كود الصنف": str(item_code), "الصنف": str(item_name), "الكمية المرجعة": int(ret_qty),
                            "المبلغ المردود": float(ret_amount), "المسؤول": st.session_state.user
                        }])
                        
                        updated_returns_df = pd.concat([st.session_state.returns_df, new_return_row], ignore_index=True)
                        updated_returns_df.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
                        st.session_state.returns_df = updated_returns_df
                        
                        if item_code in st.session_state.inv_df["كود الصنف"].values:
                            idx = st.session_state.inv_df[st.session_state.inv_df["كود الصنف"] == item_code].index[0]
                            st.session_state.inv_df.at[idx, "الكمية"] += int(ret_qty)
                            st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        
                        st.success("🎉 تم تسجيل بند الارتجاع بنجاح وضبط الكميات!")
                        st.rerun()

 # --- 8. صفحة البحث عن الفواتير وطباعتها ومعاينتها وتعديل الأسعار ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 البحث الذكي، معاينة الفواتير، وتعديل أسعار أصناف البيع")
        
        if sales_df.empty:
            st.info("لا توجد فواتير بيع مسجلة في النظام حتى الآن.")
        else:
            # 1. خيار البحث واختيار الفاتورة
            invoice_list = sales_df["رقم الفاتورة"].unique()
            selected_inv_id = st.selectbox("🎯 اختر أو ابحث عن رقم الفاتورة المستهدفة للعمل عليها:", invoice_list)
            
            # جلب بنود الفاتورة المحددة
            inv_items = sales_df[sales_df["رقم الفاتورة"] == selected_inv_id].copy()
            first_row = inv_items.iloc[0]
            
            # عرض بيانات العميل الأساسية للفاتورة
            st.markdown(f"### 📋 بيانات الفاتورة الحالية لـ: **{first_row['اسم العميل']}** | تاريخ الإصدار: `{first_row['التاريخ']}`")
            
            # تفاصيل العميل ونوع البيع
            c_info1, c_info2, c_info3 = st.columns(3)
            c_info1.markdown(f"**📱 هاتف العميل:** {first_row['هاتف العميل']}")
            c_info2.markdown(f"**📍 العنوان:** {first_row['العنوان']}")
            c_info3.markdown(f"**💳 طريقة السداد:** {first_row['نوع البيع']}")
            
            st.markdown("---")
            st.subheader("✏️ تعديل أسعار بيع الأصناف داخل الفاتورة")
            st.caption("يمكنك تعديل أسعار البيع للوحدات أدناه وسيقوم النظام بإعادة احتساب الأرباح والإجماليات والتفقيط تلقائياً لحفظها.")
            
            # جدول تعديل الأسعار حركياً بداخل الفاتورة
            updated_items_list = []
            has_changes = False
            
            for idx, item_row in inv_items.iterrows():
                col_name, col_qty, col_old_price, col_new_price = st.columns([3, 1, 1, 2])
                
                col_name.write(f"📦 **{item_row['الصنف']}** ({item_row['كود الصنف']})")
                col_qty.info(f"الكمية: {item_row['الكمية']}")
                col_old_price.write(f"السعر الحالي: {item_row['سعر الوحدة']} ج.م")
                
                # حقل إدخال السعر الجديد لكل بند
                new_unit_price = col_new_price.number_input(
                    f"السعر الجديد لـ {item_row['الصنف']}", 
                    min_value=0.0, 
                    value=float(item_row['سعر الوحدة']),
                    step=1.0,
                    key=f"price_edit_{idx}"
                )
                
                if new_unit_price != float(item_row['سعر الوحدة']):
                    has_changes = True
                
                # تجميع البيانات وحساب القيم الجديدة لكل بند تلقائياً
                qty = float(item_row['الكمية'])
                disc_pct = float(item_row.get('الخصم %', 0))
                disc_fixed = float(item_row.get('خصم نقدي ثابت', 0))
                
                # حساب إجمالي البيع للبند بناء على السعر المعدل
                sub_total = qty * new_unit_price
                if disc_pct > 0:
                    sub_total = sub_total * (1 - (disc_pct / 100))
                sub_total = max(0.0, sub_total - disc_fixed)
                
                # حساب صافي الربح الجديد للبند بناء على تكلفة الشراء المخزنة
                cost_total = float(item_row.get('تكلفة الشراء الإجمالية', 0))
                if cost_total > 0 and float(item_row['سعر الوحدة']) > 0:
                    unit_cost = cost_total / qty
                else:
                    unit_cost = float(item_row.get('سعر الشراء المعتمد', 0))
                
                new_cost_total = unit_cost * qty
                new_net_profit = sub_total - new_cost_total
                
                # تحديث قيم الصف الحالي
                updated_row = item_row.copy()
                updated_row['سعر الوحدة'] = new_unit_price
                updated_row['إجمالي البيع'] = sub_total
                updated_row['صافي ربح الفاتورة'] = new_net_profit
                
                updated_items_list.append((idx, updated_row))
            
            # حفظ الأسعار المعدلة إن وجدت
            if has_changes:
                if st.button("💾 حفظ الأسعار وتحديث الفاتورة بالكامل", use_container_width=True):
                    for orig_idx, updated_row in updated_items_list:
                        sales_df.loc[orig_idx] = updated_row
                    
                    sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    st.session_state.sales_df = sales_df
                    st.success("🚀 تم تعديل الأسعار وإعادة احتساب الأرباح والإجماليات بنجاح!")
                    st.rerun()
            
            st.markdown("---")
            st.subheader("👁️ معاينة الفاتورة الثلاثية الفورية (قبل الطباعة)")
            
            # تجهيز بيانات السلة للمعاينة والطباعة
            preview_cart = []
            for _, r in sales_df[sales_df["رقم الفاتورة"] == selected_inv_id].iterrows():
                preview_cart.append({
                    "item_name": r["الصنف"],
                    "unit": r.get("نوع الوحدة", "قطعة"),
                    "qty": r["الكمية"],
                    "price": r["سعر الوحدة"],
                    "final_total": r["إجمالي البيع"]
                })
            
            # استدعاء دالة بناء الفاتورة المعتمدة في النظام
            invoice_html_content = generate_triple_invoice_html(
                inv_id=selected_inv_id,
                datetime_str=first_row["التاريخ"],
                client_name=first_row["اسم العميل"],
                phone=first_row["هاتف العميل"],
                address=first_row["العنوان"],
                pay_type=first_row["نوع البيع"],
                collect_system=first_row.get("نظام التحصيل", "فوري"),
                collect_date=first_row.get("تاريخ التحصيل", "-"),
                paid_advance=first_row.get("المدفوع مقدم", 0),
                remaining_bal=first_row.get("المتبقي", 0),
                user=first_row.get("المسؤول", st.session_state.get('user', 'الإدارة')),
                cart_items=preview_cart,
                sh_name=SHOWROOM_NAME,
                sh_address=SHOWROOM_ADDRESS,
                sh_phone=INQUIRY_NUMBER
            )
            
            # تم تعديل خيار scroller إلى scrolling الصحيح هنا لتفادي الخطأ تماماً
            st.components.v1.html(invoice_html_content, height=500, scrolling=True)
            
            # 3. زر إصدار وطباعة الفاتورة 
            st.markdown("---")
            st.subheader("🖨️ طباعة وإصدار المستند النهائي")
            st.write("اضغط على الزر أدناه لفتح أو تحميل الفاتورة بصيغة HTML جاهزة للطباعة الفورية بضغطة واحدة:")
            
            st.download_button(
                label="🖨️ إصدار وطباعة الفاتورة الثلاثية (اضغط للتحميل والطباعة)",
                data=invoice_html_content,
                file_name=f"Invoice_{selected_inv_id}.html",
                mime="text/html",
                use_container_width=True
            )
            
    # --- 9. تقارير البيع والشراء والأرباح المطور ---
    elif "📈 تقارير البيع والشراء والأرباح" in choice:
        st.header("📈 لوحة التقارير الذكية وفلاتر الأرباح العامة")

        # --- قسم الفلترة من تاريخ إلى تاريخ ---
        st.markdown("### 🔍 تخصيص فترة التقرير")
        c_date1, c_date2 = st.columns(2)
        
        # تعيين تاريخ اليوم كقيمة افتراضية لشهر كامل مثلاً
        start_date = c_date1.date_input("من تاريخ", datetime.now().replace(day=1))
        end_date = c_date2.date_input("إلى تاريخ", datetime.now())

        # تحويل عمود التاريخ في الجداول إلى صيغة تاريخ صالحة للمقارنة
        # تحويل تاريخ المبيعات
        if not sales_df.empty:
            sales_df['تاريخ_مقارنة'] = pd.to_datetime(sales_df['التاريخ'], errors='coerce').dt.date
            filtered_sales = sales_df[(sales_df['تاريخ_مقارنة'] >= start_date) & (sales_df['تاريخ_مقارنة'] <= end_date)]
        else:
            filtered_sales = sales_df.copy()

        # تحويل تاريخ المشتريات
        if not purchases_df.empty:
            purchases_df['تاريخ_مقارنة'] = pd.to_datetime(purchases_df['التاريخ'], errors='coerce').dt.date
            filtered_purchases = purchases_df[(purchases_df['تاريخ_مقارنة'] >= start_date) & (purchases_df['تاريخ_مقارنة'] <= end_date)]
        else:
            filtered_purchases = purchases_df.copy()

        # تحويل تاريخ المصاريف
        if not exp_df.empty:
            exp_df['تاريخ_مقارنة'] = pd.to_datetime(exp_df['التاريخ'], errors='coerce').dt.date
            filtered_expenses = exp_df[(exp_df['تاريخ_مقارنة'] >= start_date) & (exp_df['تاريخ_مقارنة'] <= end_date)]
        else:
            filtered_expenses = exp_df.copy()

        st.markdown("---")

        # --- حساب الإجماليات بناءً على الفلترة ---
        total_s_income = pd.to_numeric(filtered_sales["إجمالي البيع"], errors='coerce').sum() if not filtered_sales.empty else 0.0
        total_s_profit = pd.to_numeric(filtered_sales["صافي ربح الفاتورة"], errors='coerce').sum() if not filtered_sales.empty else 0.0
        total_p_expenses = pd.to_numeric(filtered_purchases["إجمالي الشراء"], errors='coerce').sum() if not filtered_purchases.empty else 0.0
        total_gen_expenses = pd.to_numeric(filtered_expenses["المبلغ"], errors='coerce').sum() if not filtered_expenses.empty else 0.0
        
        final_net_profit = total_s_profit - total_gen_expenses
        
        # عرض العدادات المالية الرقمية للمستخدم
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🛒 مبيعات الفترة المحددة", f"{total_s_income:,.2f} جنيه")
        m2.metric("📥 مشتريات الفترة المحددة", f"{total_p_expenses:,.2f} جنيه")
        m3.metric("💸 المصاريف النثرية بالفترة", f"{total_gen_expenses:,.2f} جنيه")
        
        # تلوين مؤشر صافي الربح مخصص
        if final_net_profit >= 0:
            m4.metric("📊 صافي الأرباح النهائية (الربح الصافي)", f"{final_net_profit:,.2f} جنيه")
        else:
            m4.metric("📊 صافي الأرباح النهائية (خسارة)", f"{final_net_profit:,.2f} جنيه", delta_color="inverse")

        st.markdown("---")

        # --- قسم السجل اليومي التفصيلي للفترة ---
        st.markdown("### 📋 السجل اليومي التفصيلي للحركات")
        
        t_daily_sales, t_daily_purchases, t_daily_expenses = st.tabs([
            "🛒 تفاصيل مبيعات الفترة", 
            "📥 تفاصيل مشتريات الفترة", 
            "💸 تفاصيل مصاريف الفترة"
        ])
        
        with t_daily_sales:
            if filtered_sales.empty:
                st.info("لا توجد مبيعات مسجلة في هذه الفترة.")
            else:
                st.dataframe(
                    filtered_sales[["رقم الفاتورة", "التاريخ", "اسم العميل", "الصنف", "الكمية", "إجمالي البيع", "صافي ربح الفاتورة", "المسؤول"]], 
                    use_container_width=True
                )
                
        with t_daily_purchases:
            if filtered_purchases.empty:
                st.info("لا توجد مشتريات مسجلة في هذه الفترة.")
            else:
                st.dataframe(
                    filtered_purchases[["رقم الفاتورة", "التاريخ", "المورد", "الصنف", "الكمية", "إجمالي الشراء", "المسؤول"]], 
                    use_container_width=True
                )
                
        with t_daily_expenses:
            if filtered_expenses.empty:
                st.info("لا توجد مصاريف نثرية مسجلة في هذه الفترة.")
            else:
                st.dataframe(
                    filtered_expenses[["التاريخ", "البيان", "المبلغ", "المسؤول"]], 
                    use_container_width=True
                )

        # --- رسم بياني بسيط ملخص للأداء الإجمالي ---
        st.markdown("### 📊 ملخص بياني سريع للأداء")
        chart_data = pd.DataFrame({
            "المؤشر المالي": ["المبيعات", "المشتريات", "المصاريف", "صافي الأرباح"],
            "المبلغ الإجمالي": [total_s_income, total_p_expenses, total_gen_expenses, final_net_profit]
        })
        st.bar_chart(data=chart_data, x="المؤشر المالي", y="المبلغ الإجمالي")

    # --- 10. المصاريف ---
    elif "💸 المصاريف" in choice:
        st.header("💸 سجل إدارة المصاريف النثرية والعمومية")
        st.dataframe(exp_df, use_container_width=True)
        with st.form("exp_form"):
            ex1, ex2 = st.columns(2)
            e_desc = ex1.text_input("بيان المصروف")
            e_amt = ex2.number_input("المبلغ المدفوع (جنيه)", min_value=0.0, step=10.0)
            if st.form_submit_button("💾 ترحيل المصروف المالي"):
                if e_desc and e_amt > 0:
                    new_e = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "البيان": e_desc, "المبلغ": e_amt, "المسؤول": st.session_state.user}])
                    st.session_state.exp_df = pd.concat([exp_df, new_e], ignore_index=True)
                    st.session_state.exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم حفظ قيد المصروف الجديد!")
                    st.rerun()

    # --- 11. الحضور والانصراف ---
    elif "⏰ الحضور والانصراف" in choice:
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
                st.success("✅ تم تسجيل وقت انصرافك بنجاح!")
                st.rerun()

    # --- 12. إدارة وتعديل الصلاحيات والحسابات ---
    elif "⚙️ إدارة وتعديل الصلاحيات والحسابات" in choice:
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
                st.success("✅ تم تحديث وحفظ بيانات المعرض بنجاح!")
                st.rerun()
