import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from io import StringIO

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
PURCHASE_RETURNS_FILE = "purchase_returns_data.csv" # ملف ارتجاع فواتير الشراء الجديد
COLLECTIONS_FILE = "collections_data.csv" 

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
                if unit_part > 0: words.append(f"{units[unit_part]} و{tens[tens_part]}")
                else: words.append(tens[tens_part])
        return "فقط " + " و ".join([w for w in words if w != "و"]) + " جنيهاً مصرياً لا غير"
    except: return ""

# دالة تهيئة الملفات
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([{"username": "admin", "password": "123", "role": "مدير"}, {"username": "sharaf", "password": "456", "role": "مشرف"}]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "تصنيف الصنف", "نوع الوحدة", "موقع المخزن", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "هاتف العميل", "العنوان", "نوع البيع", "نظام التحصيل", "تاريخ التحصيل", "المدفوع مقدم", "المتبقي", "كود الصنف", "الصنف", "تصنيف الصنف", "نوع الوحدة", "موقع المخزن", "الكمية", "سعر الوحدة", "الخصم %", "خصم نقدي ثابت", "إجمالي البيع", "تكلفة الشراء الإجمالية", "صافي ربح الفاتورة", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(RETURNS_FILE):
        pd.DataFrame(columns=["رقم الإرجاع", "رقم الفاتورة الأصلية", "التاريخ", "اسم العميل", "كود الصنف", "الصنف", "الكمية المرجعة", "المبلغ المردود", "المسؤول"]).to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(PURCHASE_RETURNS_FILE):
        pd.DataFrame(columns=["رقم الإرجاع", "رقم فاتورة الشراء", "التاريخ", "اسم المورد", "كود الصنف", "الصنف", "الكمية المرجعة", "المبلغ المسترد", "المسؤول"]).to_csv(PURCHASE_RETURNS_FILE, index=False, encoding='utf-8-sig')
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

    all_pages = ["📦 إدارة الأصناف والمخزن", "📊 رصيد أول المدة Excel", "🔍 حالة المخزن", "🤝 العملاء والموردين", "📥 حركة فواتير الشراء وارتجاعها", "📤 حركة فواتير البيع", "↩️ ارتجاع فواتير البيع", "🔎 البحث عن الفواتير وطباعتها", "📈 تقارير البيع والشراء والأرباح", "💸 المصاريف", "⏰ الحضور والانصراف", "⚙️ إدارة وتعديل الصلاحيات والحسابات", "⚙️ إعدادات بيانات الفاتورة والدعم"]
    if not os.path.exists(PERMISSIONS_FILE):
        default_perms = [{"اسم الصفحة": page, "مدير": True, "مشرف": True if page in ["🔍 حالة المخزن", "📥 حركة فواتير الشراء وارتجاعها", "📤 حركة فواتير البيع", "🔎 البحث عن الفواتير وطباعتها"] else False, "موظف": True if page in ["🔍 حالة المخزن", "📤 حركة فواتير البيع"] else False} for page in all_pages]
        pd.DataFrame(default_perms).to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')

init_files()

def load_data_into_session():
    if 'data_loaded' not in st.session_state or st.sidebar.button("🔄 تحديث شامل للبيانات", key="global_refresh"):
        st.session_state.inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
        st.session_state.inv_df["الكمية"] = pd.to_numeric(st.session_state.inv_df["الكمية"], errors='coerce').fillna(0).astype(int)
        st.session_state.inv_df["سعر الشراء"] = pd.to_numeric(st.session_state.inv_df["سعر الشراء"], errors='coerce').fillna(0.0)
        st.session_state.inv_df["سعر البيع"] = pd.to_numeric(st.session_state.inv_df["سعر البيع"], errors='coerce').fillna(0.0)
        st.session_state.sales_df = pd.read_csv(SALES_FILE, dtype={"رقم الفاتورة": str, "كود الصنف": str})
        st.session_state.returns_df = pd.read_csv(RETURNS_FILE, dtype={"رقم الإرجاع": str, "كود الصنف": str})
        st.session_state.p_returns_df = pd.read_csv(PURCHASE_RETURNS_FILE, dtype={"رقم الإرجاع": str, "كود الصنف": str})
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

# الحفاظ على حالة المدخلات عند التنقل بين الصفحات ومنع مسحها
if 'state_sale_cust_type' not in st.session_state: st.session_state.state_sale_cust_type = "عميل سريع (جديد)"
if 'state_sale_cust_name_input' not in st.session_state: st.session_state.state_sale_cust_name_input = ""
if 'state_sale_cust_phone' not in st.session_state: st.session_state.state_sale_cust_phone = ""
if 'state_sale_cust_address' not in st.session_state: st.session_state.state_sale_cust_address = ""
if 'state_sale_discount_fixed' not in st.session_state: st.session_state.state_sale_discount_fixed = 0.0
if 'state_purchase_invoice' not in st.session_state: st.session_state.state_purchase_invoice = "PUR-" + str(int(datetime.now().timestamp()))
if 'state_purchase_supplier' not in st.session_state: st.session_state.state_purchase_supplier = ""

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
    if discount_fixed > 0:
        standard_table_td += f"<tr style='background:#f9f9f9; font-weight:bold;'><td colspan='6' style='text-align:left;'>خصم نقدي مباشر على الفاتورة:</td><td style='color:red;'>-{discount_fixed} جنيه</td></tr>"
    
    store_table_th = "<tr><th>الصنف والبيان</th><th>موقع المخزن</th><th>الكمية المطلوبة للصرف</th></tr>"
    store_table_td = ""
    for item in cart_items:
        store_table_td += f"<tr><td>{item['item_name']}</td><td>{item.get('warehouse_loc', 'الرئيسي')}</td><td style='font-size: 16px; font-weight: bold;'>{item['qty']}</td></tr>"

    return f"""
    <div class="triple-print-wrapper">
        <style>
            @page {{ size: A5 portrait; margin: 0; }}
            @media print {{
                body {{ direction: rtl; background: #fff; color: #000; padding: 0; margin: 0; }}
                header, [data-testid="stSidebar"], [data-testid="stHeader"], .no-print-zone, .stButton, .download-btn-area {{ display: none !important; }}
                .invoice-page {{ width: 148mm; height: auto !important; min-height: 210mm; box-sizing: border-box; padding: 10mm !important; margin: 0 !important; page-break-after: always; border: none !important; box-shadow: none !important; }}
                .invoice-items-table tr {{ page-break-inside: avoid !important; page-break-after: auto !important; }}
            }}
            .invoice-page {{ width: 148mm; height: auto; min-height: 210mm; border: 2px solid #000; padding: 20px; margin: 20px auto; background: #fff; color: #000; box-sizing: border-box; page-break-after: always; }}
            .invoice-header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; }}
            .invoice-header h1 {{ margin: 6px 0; font-size: 24px; }}
            .invoice-items-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; border: 2px solid black; text-align: center; }}
            .invoice-items-table th, .invoice-items-table td {{ border: 1px solid black; padding: 6px; }}
            .total-words-area {{ margin-top: 15px; border: 1px dashed #000; padding: 8px; font-weight: bold; }}
            .print-trigger-btn {{ background-color: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 15px; font-weight: bold; display: block; margin: 20px auto; }}
        </style>
        <div class="no-print-zone"><button class="print-trigger-btn" onclick="window.print()">🖨️ إصدار وطباعة الفاتورة الثلاثية (A5)</button></div>
        <div class="invoice-page">
            <div class="invoice-header"><h3> أصل الفاتورة (نسخة العميل)</h3><h1>{sh_name}</h1><p>{sh_address} | {sh_phone}</p></div>
            <table style="width:100%; font-size:13px;">
                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ:</b> {datetime_str}</td></tr>
                <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>المسؤول:</b> {user}</td></tr>
                <tr><td><b>نوع الدفع:</b> {pay_type}</td><td><b>صافي المطلوب:</b> {total_invoice_amount} جنيه</td></tr> {collect_info}
            </table>
            <table class="invoice-items-table">{standard_table_th}{standard_table_td}</table>
            <div class="total-words-area">{arabic_total_words}</div>
        </div>
        <div class="invoice-page">
            <div class="invoice-header"><h3> نسخة الحسابات والإدارة</h3><h1>{sh_name}</h1></div>
            <table class="invoice-items-table">{standard_table_th}{standard_table_td}</table>
        </div>
        <div class="invoice-page">
            <div class="invoice-header"><h3> إذن الصرف (نسخة المخزن)</h3><h1>{sh_name}</h1></div>
            <table class="invoice-items-table">{store_table_th}{store_table_td}</table>
        </div>
    </div>
    """

if not st.session_state.auth:
    st.title(f"🏢 نظام {SHOWROOM_NAME} - تسجيل الدخول")
    user_input = st.text_input("اسم المستخدم").strip()
    pw_input = st.text_input("كلمة المرور", type="password").strip()
    if st.button("دخول للنظام", use_container_width=True):
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        match = u_df[(u_df['username'] == user_input) & (u_df['password'] == pw_input)]
        if not match.empty:
            st.session_state.auth = True
            st.session_state.user = user_input
            st.session_state.role = match.iloc[0]['role']
            st.rerun()
        else: st.error("بيانات الدخول خاطئة.")
else:
    perms_df = pd.read_csv(PERMISSIONS_FILE)
    allowed_actions = perms_df[perms_df[st.session_state.role] == True]["اسم الصفحة"].tolist()
    choice = st.sidebar.radio("📋 الأقسام الرئيسية للنظام:", allowed_actions)
    
    inv_df = st.session_state.inv_df
    sales_df = st.session_state.sales_df
    returns_df = st.session_state.returns_df
    p_returns_df = st.session_state.p_returns_df
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
        return f"{x} - {match[0]}" if len(match) > 0 else f"{x}"

    # --- 1. صفحة إدارة الأصناف ---
    if "إدارة الأصناف والمخزن" in choice:
        st.header("📦 إدارة وتكويد أصناف المخزن المتطورة")
        t_view, t_add, t_edit, t_delete = st.tabs(["📋 استعراض المنتجات", "➕ تكويد صنف جديد", "✏️ تعديل صنف", "❌ حذف صنف نهائياً"])
        with t_view: st.dataframe(inv_df, use_container_width=True)
        with t_add:
            c1, c2, c3, c4 = st.columns(4)
            iid = c1.text_input("كود الصنف").strip()
            iname = c2.text_input("اسم المنتج").strip()
            icat = c3.selectbox("تصنيف الصنف", ["كهربي", "منزلي", "بلاستيك", "صيني ومطابخ", "منظفات", "عام"])
            iunit = c4.selectbox("نوع الوحدة", ["قطعة", "طقم", "كرتونة"])
            if st.button("تكويد وحفظ البند"):
                if iid and iname:
                    if iid in inv_df["كود الصنف"].values: st.warning("الكود مسجل مسبقاً")
                    else:
                        new_item = pd.DataFrame([{"كود الصنف": iid, "اسم الصنف": iname, "تصنيف الصنف": icat, "نوع الوحدة": iunit, "موقع المخزن": "المخزن الرئيسي", "الكمية": 0, "سعر الشراء": 0.0, "سعر البيع": 0.0}])
                        st.session_state.inv_df = pd.concat([inv_df, new_item], ignore_index=True)
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        st.success("تم التكويد")
                        st.rerun()
        with t_delete:
            selected_del_code = st.selectbox("اختر صنف لحذفه", inv_df["كود الصنف"].values, format_func=safe_item_format)
            if st.button("تأكيد الحذف الكلي"):
                st.session_state.inv_df = inv_df[inv_df["كود الصنف"] != selected_del_code]
                st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                st.success("تم الحذف")
                st.rerun()

    # --- 2. رصيد أول المدة ---
    elif "رصيد أول المدة" in choice:
        st.header("📊 رفع رصيد أول المدة Excel أو اللصق السريع")
        pasted_input = st.text_area("الصق جدول إكسيل هنا مباشرة")
        if st.button("دمج وترحيل البيانات"):
            if pasted_input.strip():
                try:
                    df = pd.read_csv(StringIO(pasted_input), sep="\t", dtype={"كود الصنف": str})
                    df["كود الصنف"] = df["كود الصنف"].astype(str).str.strip()
                    combined = pd.concat([inv_df, df]).drop_duplicates(subset=['كود الصنف'], keep='last')
                    st.session_state.inv_df = combined
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("تم دمج رصيد أول المدة بنجاح!")
                    st.rerun()
                except Exception as e: st.error(f"خطأ: {e}")

    # --- 3. حالة المخزن ---
    elif "حالة المخزن" in choice:
        st.header("🔍 جرد بضائع المخزن الحالية")
        st.dataframe(inv_df, use_container_width=True)

    # --- 4. العملاء والموردين ---
    elif "العملاء والموردين" in choice:
        st.header("🤝 إدارة بيانات العملاء والموردين")
        st.dataframe(contacts_df, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        ctype = c1.selectbox("النوع", ["عميل", "مورد"])
        cname = c2.text_input("الاسم")
        cphone = c3.text_input("الهاتف")
        if st.button("حفظ الجهة"):
            if cname:
                new_c = pd.DataFrame([{"النوع": ctype, "الاسم": cname, "الهاتف": cphone, "العنوان": "عام"}])
                st.session_state.contacts_df = pd.concat([contacts_df, new_c], ignore_index=True)
                st.session_state.contacts_df.to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')
                st.success("تم الحفظ")
                st.rerun()

    # --- 5. حركة فواتير الشراء وارتجاعها ---
    elif "حركة فواتير الشراء وارتجاعها" in choice:
        st.header("📥 حركات فواتير الشراء وإرجاع المشتريات للموردين")
        t_buy, t_buy_return = st.tabs(["📥 تسجيل فاتورة شراء جديدة", "↩️ تسجيل فاتورة ارتجاع مشتريات (لمورد)"])
        
        with t_buy:
            p_invoice = st.text_input("رقم فاتورة الشراء", value=st.session_state.state_purchase_invoice)
            st.session_state.state_purchase_invoice = p_invoice
            
            p_supplier = st.text_input("اسم المورد / الشركة", value=st.session_state.state_purchase_supplier)
            st.session_state.state_purchase_supplier = p_supplier
            
            pc1, pc2, pc3 = st.columns(3)
            p_code = pc1.selectbox("اختر الصنف لتوريده", inv_df["كود الصنف"].values, format_func=safe_item_format, key="p_code_box")
            p_qty = pc2.number_input("الكمية المشتراة", min_value=1, step=1, value=1)
            p_price = pc3.number_input("سعر الشراء للوحدة (جنيه)", min_value=0.0, step=10.0)
            
            if st.button("📥 ترحيل فاتورة الشراء للمخزن"):
                if p_supplier and p_code:
                    idx = inv_df[inv_df['كود الصنف'] == p_code].index[0]
                    item_name = inv_df.at[idx, 'اسم الصنف']
                    total_p = p_qty * p_price
                    new_p = pd.DataFrame([{"رقم الفاتورة": p_invoice, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "المورد": p_supplier, "كود الصنف": p_code, "الصنف": item_name, "تصنيف الصنف": "عام", "نوع الوحدة": "قطعة", "موقع المخزن": "الرئيسي", "سعر الشراء المعتمد": p_price, "الكمية": p_qty, "إجمالي الشراء": total_p, "المسؤول": st.session_state.user}])
                    st.session_state.purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                    st.session_state.purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                    
                    st.session_state.inv_df.at[idx, "الكمية"] += int(p_qty)
                    st.session_state.inv_df.at[idx, "سعر الشراء"] = p_price
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("تم تسجيل المشتريات بنجاح وزيادة المخزن!")
                    st.rerun()
                    
        with t_buy_return:
            st.subheader("↩️ ارتجاع بضاعة مشتراة إلى مورد (خصم من المخزن)")
            prc1, prc2 = st.columns(2)
            pret_invoice = prc1.text_input("رقم فاتورة الشراء الأصلية")
            pret_supplier = prc2.text_input("اسم المورد المستلم للمردودات")
            
            prc3, prc4, prc5 = st.columns(3)
            pret_code = prc3.selectbox("اختر الصنف المراد إرجاعه للمورد", inv_df["كود الصنف"].values, format_func=safe_item_format, key="pret_code_box")
            pret_qty = prc4.number_input("الكمية المرجعة للمورد", min_value=1, step=1, key="pret_qty_val")
            pret_amt = prc5.number_input("المبلغ المسترد من المورد (جنيه)", min_value=0.0)
            
            if st.button("🔥 ترحيل فاتورة ارتجاع المشتريات"):
                if pret_supplier and pret_code:
                    idx = inv_df[inv_df['كود الصنف'] == pret_code].index[0]
                    if inv_df.at[idx, "الكمية"] < pret_qty:
                        st.error("⚠️ الكمية الموجودة بالمخزن أقل من الكمية المراد إرجاعها!")
                    else:
                        item_name = inv_df.at[idx, 'اسم الصنف']
                        new_pr = pd.DataFrame([{"رقم الإرجاع": "RETP-" + str(int(datetime.now().timestamp())), "رقم فاتورة الشراء": pret_invoice, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "اسم المورد": pret_supplier, "كود الصنف": pret_code, "الصنف": item_name, "الكمية المرجعة": pret_qty, "المبلغ المسترد": pret_amt, "المسؤول": st.session_state.user}])
                        st.session_state.p_returns_df = pd.concat([p_returns_df, new_pr], ignore_index=True)
                        st.session_state.p_returns_df.to_csv(PURCHASE_RETURNS_FILE, index=False, encoding='utf-8-sig')
                        
                        st.session_state.inv_df.at[idx, "الكمية"] -= int(pret_qty)
                        st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                        st.success("🎉 تم تسجيل ارتجاع المشتريات بنجاح وخصم البضاعة من المخزن!")
                        st.rerun()

    # --- 6. حركة فواتير البيع المتطورة ---
    elif "حركة فواتير البيع" in choice:
        st.header("📤 لوحة حركة فواتير البيع")
        
        # اختيار نوع العميل: مكود مسجل أو سريع جديد
        cust_type = st.radio("🔄 اختر نوع العميل الحركي:", ["عميل سريع (جديد)", "عميل مكود (مسجل مسبقاً)"], horizontal=True, index=0 if st.session_state.state_sale_cust_type == "عميل سريع (جديد)" else 1)
        st.session_state.state_sale_cust_type = cust_type
        
        sale_cust = ""
        if cust_type == "عميل مكود (مسجل مسبقاً)":
            all_registered_custs = contacts_df[contacts_df["النوع"] == "عميل"]["الاسم"].unique() if not contacts_df.empty else []
            if len(all_registered_custs) > 0:
                sale_cust = st.selectbox("اختر اسم العميل المكود من القائمة:", all_registered_custs)
            else:
                st.info("لا يوجد عملاء مكودين، تم تحويلك للعميل السريع.")
                sale_cust = st.text_input("اسم العميل السريع", value=st.session_state.state_sale_cust_name_input)
        else:
            sale_cust = st.text_input("اسم العميل السريع (جديد)", value=st.session_state.state_sale_cust_name_input)
            st.session_state.state_sale_cust_name_input = sale_cust
            
        c_p1, c_p2 = st.columns(2)
        sale_phone = c_p1.text_input("رقم هاتف العميل", value=st.session_state.state_sale_cust_phone)
        st.session_state.state_sale_cust_phone = sale_phone
        sale_address = c_p2.text_input("عنوان العميل", value=st.session_state.state_sale_cust_address)
        st.session_state.state_sale_cust_address = sale_address

        st.markdown("### 🛒 إضافة المنتجات للسلة")
        sc1, sc2, sc3 = st.columns(3)
        if not inv_df.empty:
            selected_sale_code = sc1.selectbox("اختر الصنف", inv_df["كود الصنف"].values, format_func=safe_item_format)
            match_s = inv_df[inv_df["كود الصنف"] == selected_sale_code].iloc[0]
            sale_qty = sc2.number_input(f"الكمية (المتاحة: {match_s['الكمية']})", min_value=1, max_value=int(match_s['الكمية']) if int(match_s['الكمية']) > 0 else 1, step=1)
            sale_disc = sc3.number_input("الخصم %", min_value=0.0, max_value=100.0, value=0.0)
            
            if st.button("➕ إضافة الصنف للسلة الحالية"):
                if match_s['الكمية'] <= 0: st.error("المخزون صفر!")
                else:
                    final_tot = (sale_qty * match_s['سعر البيع']) - ((sale_qty * match_s['سعر البيع']) * (sale_disc / 100))
                    st.session_state.cart.append({
                        "id": len(st.session_state.cart), "item_code": selected_sale_code, "item_name": match_s['اسم الصنف'],
                        "category": match_s['تصنيف الصنف'], "unit": match_s['نوع الوحدة'], "warehouse_loc": match_s['موقع المخزن'],
                        "qty": int(sale_qty), "price": float(match_s['سعر البيع']), "discount": float(sale_disc), "final_total": float(final_tot), "purchase_cost": float(match_s['سعر الشراء'])
                    })
                    st.success("تم الإضافة للسلة")
                    st.rerun()

        if st.session_state.cart:
            st.markdown("### 🧾 البنود المدرجة حالياً في السلة")
            
            # عرض عناصر السلة مع إمكانية حذف صنف معين
            for idx, item in enumerate(st.session_state.cart):
                col_item1, col_item2, col_item3 = st.columns([5, 2, 2])
                col_item1.write(f"🔹 **{item['item_name']}** - الكمية: {item['qty']} - الإجمالي: {item['final_total']} جنيه")
                if col_item2.button(f"❌ حذف صنف", key=f"del_item_{item['id']}_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.success("تم حذف الصنف المختار من السلة!")
                    st.rerun()
            
            st.markdown("---")
            subtotal = sum(item['final_total'] for item in st.session_state.cart)
            discount_fixed = st.number_input("💵 خصم نقدي مباشر بالجنيه على إجمالي الفاتورة الكلي", min_value=0.0, value=st.session_state.state_sale_discount_fixed)
            st.session_state.state_sale_discount_fixed = discount_fixed
            
            total_invoice_amount = max(0.0, subtotal - discount_fixed)
            st.metric("🧾 الإجمالي المطلوب سداده الفعلي:", f"{total_invoice_amount:,.2f} جنيه")
            
            pay_type = st.radio("نوع الدفع", ["نقدي (كاش)", "آجل (على الحساب)"])
            if st.button("🚀 ترحيل الفاتورة نهائياً وطباعتها"):
                if not sale_cust: st.error("ادخل اسم العميل")
                else:
                    inv_id = "INV-" + str(int(datetime.now().timestamp()))
                    datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sales_rows = []
                    for item in st.session_state.cart:
                        sales_rows.append({
                            "رقم الفاتورة": inv_id, "التاريخ": datetime_str, "اسم العميل": sale_cust, "هاتف العميل": sale_phone, "العنوان": sale_address, "نوع البيع": pay_type, "نظام التحصيل": "غير محدد", "تاريخ التحصيل": "غير محدد", "المدفوع مقدم": 0, "المتبقي": 0, "كود الصنف": item['item_code'], "الصنف": item['item_name'], "تصنيف الصنف": item['category'], "نوع الوحدة": item['unit'], "موقع المخزن": item['warehouse_loc'], "الكمية": item['qty'], "سعر الوحدة": item['price'], "الخصم %": item['discount'], "خصم نقدي ثابت": discount_fixed, "إجمالي البيع": item['final_total'], "تكلفة الشراء الإجمالية": (item['qty'] * item['purchase_cost']), "صافي ربح الفاتورة": (item['final_total'] - (item['qty'] * item['purchase_cost'])), "المسؤول": st.session_state.user
                        })
                        idx_inv = inv_df[inv_df["كود الصنف"] == item['item_code']].index[0]
                        st.session_state.inv_df.at[idx_inv, "الكمية"] -= int(item['qty'])
                        
                    st.session_state.sales_df = pd.concat([sales_df, pd.DataFrame(sales_rows)], ignore_index=True)
                    st.session_state.sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    st.session_state.inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    html_invoice = generate_triple_invoice_html(inv_id, datetime_str, sale_cust, sale_phone, sale_address, pay_type, "غير محدد", "غير محدد", 0, 0, st.session_state.user, st.session_state.cart, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, discount_fixed=discount_fixed)
                    st.markdown(html_invoice, unsafe_allow_html=True)
                    st.session_state.cart = []
                    st.session_state.state_sale_cust_name_input = ""
                    st.session_state.state_sale_discount_fixed = 0.0

    # --- 7. ارتجاع فواتير البيع ---
    elif "ارتجاع فواتير البيع" in choice:
        st.header("↩️ لوحة تحكم مرتجعات فواتير البيع للعملاء")
        edited_returns = st.data_editor(returns_df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 حفظ جميع تعديلات المردودات وحذفها"):
            edited_returns.to_csv(RETURNS_FILE, index=False, encoding='utf-8-sig')
            st.session_state.returns_df = edited_returns
            st.success("تم حفظ التحديثات والتعديلات!")
            st.rerun()

    # --- 8. البحث عن الفواتير وطباعتها ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 محرك البحث عن الفواتير وطباعتها")
        search_id = st.text_input("ادخل رقم الفاتورة للبحث:")
        if search_id:
            f_sales = sales_df[sales_df["رقم الفاتورة"] == search_id]
            if not f_sales.empty:
                f_head = f_sales.iloc[0]
                re_items = [{"item_code": r["كود الصنف"], "item_name": r["الصنف"], "qty": int(r["الكمية"]), "price": float(r["سعر الوحدة"]), "discount": float(r["الخصم %"]), "final_total": float(r["إجمالي البيع"]), "warehouse_loc": "الرئيسي"} for _, r in f_sales.iterrows()]
                html_invoice = generate_triple_invoice_html(search_id, f_head["التاريخ"], f_head["اسم العميل"], f_head["هاتف العميل"], f_head["العنوان"], f_head["نوع البيع"], "غير محدد", "غير محدد", 0, 0, f_head["المسؤول"], re_items, SHOWROOM_NAME, SHOWROOM_ADDRESS, INQUIRY_NUMBER, discount_fixed=float(f_head.get("خصم نقدي ثابت", 0.0)))
                st.markdown(html_invoice, unsafe_allow_html=True)
            else: st.error("غير موجودة")

    # --- 9. التقارير المالية ---
    elif "تقارير البيع والشراء والأرباح" in choice:
        st.header("📈 لوحة التقارير الذكية والإحصائيات")
        total_s = pd.to_numeric(sales_df["إجمالي البيع"], errors='coerce').sum() if not sales_df.empty else 0.0
        total_p = pd.to_numeric(purchases_df["إجمالي الشراء"], errors='coerce').sum() if not purchases_df.empty else 0.0
        st.columns(2)[0].metric("🛒 إجمالي المبيعات", f"{total_s:,.2f} جنيه")
        st.columns(2)[1].metric("📥 إجمالي المشتريات", f"{total_p:,.2f} جنيه")

    # --- 10. المصاريف ---
    elif "المصاريف" in choice:
        st.header("💸 سجل إدارة المصاريف النثرية")
        st.dataframe(exp_df, use_container_width=True)

    # --- 11. الحضور والانصراف ---
    elif "الحضور والانصراف" in choice:
        st.header("⏰ دفتر الحضور والانصراف")
        st.dataframe(att_df, use_container_width=True)

    # --- 12. الصلاحيات والحسابات ---
    elif "إدارة وتعديل الصلاحيات والحسابات" in choice:
        st.header("⚙️ إدارة صلاحيات المستخدمين")
        edited_perms_df = st.data_editor(perms_df, use_container_width=True, disabled=["اسم الصفحة"])
        if st.button("💾 حفظ الصلاحيات والصفحات الجديدة"):
            edited_perms_df.to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')
            st.success("تم تحديث الصلاحيات")
            st.rerun()

    # --- 13. إعدادات النظام ---
    elif "إعدادات بيانات الفاتورة والدعم" in choice:
        st.header("⚙️ تحديث بيانات طباعة الفاتورة والدعم")
        with st.form("settings_form_updated"):
            new_showroom_name = st.text_input("اسم المعرض بالفاتورة", value=SHOWROOM_NAME)
            new_showroom_address = st.text_input("العنوان بالفاتورة", value=SHOWROOM_ADDRESS)
            new_inquiry_number = st.text_input("رقم الدعم الفني", value=INQUIRY_NUMBER)
            if st.form_submit_button("💾 حفظ البيانات الإعدادية الجديد"):
                pd.DataFrame([{"اسم المعرض": new_showroom_name, "العنوان": new_showroom_address, "رقم الدعم": new_inquiry_number}]).to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')
                st.success("تم حفظ البيانات بنجاح!")
                st.rerun()
