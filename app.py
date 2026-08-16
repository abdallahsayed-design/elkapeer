import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==========================================
# 1. إعدادات الصفحة والترويسة الرئيسية
# ==========================================
st.set_page_config(
    page_title="شركة الربوة - نظام إدارة المبيعات والمخزون",
    page_icon="📦",
    layout="wide"
)

# تطبيق تنسيق CSS مخصص للواجهة والطباعة
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E3A8A;
        font-family: 'Cairo', sans-serif;
        font-weight: bold;
        padding: 10px;
        background-color: #F0F4F8;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    @media print {
        .stButton, .stSelectbox, .stSidebar, .stNumberInput {
            display: none !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏢 شركة الربوة - نظام المبيعات والمخزون</h1>", unsafe_allow_html=True)

# ==========================================
# 2. تهيئة قاعدة البيانات (SQLite)
# ==========================================
def init_db():
    conn = sqlite3.connect("elrabwah_system.db")
    cursor = conn.cursor()
    
    # جدول الأصناف / المخزون
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_code TEXT PRIMARY KEY,
            item_name TEXT,
            category TEXT,
            unit TEXT,
            location TEXT,
            quantity INTEGER,
            purchase_price REAL,
            sale_price REAL
        )
    """)
    
    # جدول الفواتير
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            date TEXT,
            customer_name TEXT,
            total_amount REAL,
            discount REAL,
            final_amount REAL
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 3. إدارة جلسة العمل (Session State)
# ==========================================
if "cart" not in st.session_state:
    st.session_state.cart = []

def get_inventory():
    conn = sqlite3.connect("elrabwah_system.db")
    df = pd.read_sql_query("SELECT item_code AS 'كود الصنف', item_name AS 'اسم الصنف', category AS 'تصنيف الصنف', unit AS 'نوع الوحدة', location AS 'موقع المخزن', quantity AS 'الكمية', purchase_price AS 'سعر الشراء', sale_price AS 'سعر البيع' FROM inventory", conn)
    conn.close()
    return df

# ==========================================
# 4. القائمة الجانبية للتنقل
# ==========================================
menu = ["📤 حركة فواتير البيع", "📦 إدارة المخزون والأصناف", "📑 سجل الفواتير والتقارير"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

# ==========================================
# 5. قسم حركة فواتير البيع
# ==========================================
if choice == "📤 حركة فواتير البيع":
    st.subheader("📤 إنشاء فاتورة بيع جديدة")
    
    inv_df = get_inventory()
    
    if inv_df.empty:
        st.warning("⚠️ لا توجد أصناف مسجلة في المخزون حالياً. يرجى إضافة أصناف أولاً من قسم إدارة المخزون.")
    else:
        # 1. تجهيز قائمة المنتجات للبحث السريع (الكود + الاسم + المتاحة)
        item_options = {
            f"{row['كود الصنف']} - {row['اسم الصنف']} (المتاح: {row['الكمية']})": row['كود الصنف']
            for _, row in inv_df.iterrows()
        }
        
        # 2. القائمة المنسدلة التفاعلية للبحث
        selected_item_label = st.selectbox(
            "🔎 ابحث واختر المنتج من القائمة:",
            options=list(item_options.keys()),
            index=0,
            help="يمكنك كتابة اسم المنتج أو الكود للوصول السريع"
        )
        
        selected_sale_code = item_options[selected_item_label]
        match_s = inv_df[inv_df["كود الصنف"] == selected_sale_code].iloc[0]

        # 3. أدوات إدخال الكميات والأسعار
        sc1, sc2, sc3, sc4 = st.columns(4)
        
        max_qty = int(match_s['الكمية']) if int(match_s['الكمية']) > 0 else 1
        sale_qty = sc1.number_input(
            f"الكمية المطلوبة (المتاحة: {match_s['الكمية']})", 
            min_value=1, 
            max_value=max_qty, 
            step=1
        )
        custom_sale_price = sc2.number_input("سعر البيع المعتمد", value=float(match_s['سعر البيع']), min_value=0.0)
        custom_purchase_cost = sc3.number_input("سعر الشراء المعتمد", value=float(match_s['سعر الشراء']), min_value=0.0)
        sale_disc = sc4.number_input("نسبة الخصم %", min_value=0.0, max_value=100.0, step=1.0, value=0.0)

        if st.button("➕ إضافة المنتج المختار إلى سلة الفاتورة", use_container_width=True):
            if match_s['الكمية'] > 0:
                tot_b = sale_qty * custom_sale_price
                final_tot_p = tot_b - (tot_b * (sale_disc / 100))
                st.session_state.cart.append({
                    "item_code": selected_sale_code, 
                    "item_name": match_s['اسم الصنف'],
                    "category": match_s['تصنيف الصنف'], 
                    "unit": match_s['نوع الوحدة'],
                    "location": match_s['موقع المخزن'], 
                    "qty": int(sale_qty),
                    "price": float(custom_sale_price), 
                    "discount": float(sale_disc),
                    "final_total": float(final_tot_p), 
                    "purchase_cost": float(custom_purchase_cost)
                })
                st.success("✅ تم إضافة المنتج للسلة بنجاح!")
                st.rerun()
            else:
                st.error("❌ لا يمكن إضافة المنتج! الكمية المتاحة في المخزن صفر.")

    st.divider()

    # عرض سلة الفاتورة الحالية
    st.subheader("🛒 سلة الفاتورة الحالية")
    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df, use_container_width=True)
        
        total_invoice = sum(item["final_total"] for item in st.session_state.cart)
        st.markdown(f"### 💰 **إجمالي الفاتورة: {total_invoice:,.2f} جنيه**")
        
        c1, c2 = st.columns(2)
        customer_name = c1.text_input("اسم العميل", value="عميل نقدي")
        
        if c2.button("💾 حفظ وإصدار الفاتورة", use_container_width=True):
            conn = sqlite3.connect("elrabwah_system.db")
            cursor = conn.cursor()
            inv_num = f"INV-{int(datetime.now().timestamp())}"
            
            # حفظ الفاتورة
            cursor.execute(
                "INSERT INTO sales_invoices (invoice_number, date, customer_name, total_amount, discount, final_amount) VALUES (?, ?, ?, ?, ?, ?)",
                (inv_num, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), customer_name, total_invoice, 0.0, total_invoice)
            )
            
            # خصم الكميات من المخزن
            for item in st.session_state.cart:
                cursor.execute(
                    "UPDATE inventory SET quantity = quantity - ? WHERE item_code = ?",
                    (item["qty"], item["item_code"])
                )
                
            conn.commit()
            conn.close()
            
            st.session_state.cart = []
            st.success(f"✅ تم حفظ الفاتورة بنجاح برقم: {inv_num}")
            st.rerun()
            
        if st.button("🗑️ تفريغ السلة", type="secondary"):
            st.session_state.cart = []
            st.rerun()
    else:
        st.info("السلة فارغة حالياً.")

# ==========================================
# 6. قسم إدارة المخزون وإضافة الأصناف
# ==========================================
elif choice == "📦 إدارة المخزون والأصناف":
    st.subheader("➕ إضافة صنف جديد للمخزن")
    
    with st.form("add_item_form"):
        col1, col2, col3 = st.columns(3)
        code = col1.text_input("كود الصنف (الباركود)")
        name = col2.text_input("اسم الصنف")
        category = col3.text_input("التصنيف", value="عام")
        
        col4, col5, col6 = st.columns(3)
        unit = col4.selectbox("الوحدة", ["قطعة", "كرتونة", "طقم", "متر", "كيلو"])
        location = col5.text_input("موقع المخزن", value="الرئيسي")
        qty = col6.number_input("الكمية الابتدائية", min_value=0, value=10)
        
        col7, col8 = st.columns(2)
        p_price = col7.number_input("سعر الشراء", min_value=0.0, value=0.0)
        s_price = col8.number_input("سعر البيع", min_value=0.0, value=0.0)
        
        submit = st.form_submit_button("إضافة الصنف للمخزن")
        
        if submit:
            if code and name:
                conn = sqlite3.connect("elrabwah_system.db")
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (code, name, category, unit, location, qty, p_price, s_price)
                    )
                    conn.commit()
                    st.success("✅ تم إضافة الصنف بنجاح!")
                except sqlite3.IntegrityError:
                    st.error("❌ كود الصنف موجود بالفعل! استخدم كوداً مختلفاً.")
                finally:
                    conn.close()
            else:
                st.error("❌ يرجى ملء البيانات الأساسية (الكود والاسم).")

    st.divider()
    st.subheader("📋 قائمة الأصناف المسجلة")
    st.dataframe(get_inventory(), use_container_width=True)

# ==========================================
# 7. قسم سجل الفواتير
# ==========================================
elif choice == "📑 سجل الفواتير والتقارير":
    st.subheader("📜 سجل فواتير المبيعات")
    conn = sqlite3.connect("elrabwah_system.db")
    invoices_df = pd.read_sql_query("SELECT invoice_number AS 'رقم الفاتورة', date AS 'التاريخ', customer_name AS 'العميل', final_amount AS 'الإجمالي' FROM sales_invoices ORDER BY id DESC", conn)
    conn.close()
    
    if not invoices_df.empty:
        st.dataframe(invoices_df, use_container_width=True)
    else:
        st.info("لا توجد فواتير مسجلة بعد.")
