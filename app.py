import streamlit as st

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="نظام شركة الربوة - المبيعات والأصناف",
    page_icon="📦",
    layout="wide"
)

# 2. تهيئة حالة الجلسة (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # تسجيل دخول تلقائي للتجربة
if "user_role" not in st.session_state:
    st.session_state.user_role = "Admin"
if "selected_items" not in st.session_state:
    st.session_state.selected_items = []

# قاعدة بيانات نموذجية للأصناف
PRODUCTS_DB = {
    "الكترونيات": ["شاشة 24 بوصة", "لوحة مفاتيح ميكانيكية", "ماوس لاسلكي", "سماعة رأس"],
    "أدوات مكتبية": ["ورق A4 طباعة", "قلم حبر أزرق", "دباسة مكتب", "دفتر ملاحظات"],
    "مواد غذائية": ["عصير برتقال 1 ليتر", "بسكويت شاي", "مياه معدنية", "قهوة سريعة التحضير"]
}

# 3. النافذة المنبثقة لاختيار الأصناف (Modal Dialog)
@st.dialog("🎯 نافذة اختيار الأصناف")
def select_items_dialog():
    st.write("اختر القسم ثم حدد المنتجات المطلوبة لإضافتها للفاتورة:")
    
    category = st.selectbox("اختر الفئة / القسم:", list(PRODUCTS_DB.keys()))
    available_items = PRODUCTS_DB[category]
    
    st.markdown("**الأصناف المتاحة:**")
    temp_selected = []
    
    for item in available_items:
        # التحقق مما إذا كان الصنف مضافاً مسبقاً
        is_checked = item in st.session_state.selected_items
        if st.checkbox(item, value=is_checked, key=f"chk_{category}_{item}"):
            temp_selected.append(item)
            
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("حفظ وإضافة", type="primary", use_container_width=True):
            for item in temp_selected:
                if item not in st.session_state.selected_items:
                    st.session_state.selected_items.append(item)
            st.rerun()
            
    with col2:
        if st.button("إلغاء", use_container_width=True):
            st.rerun()

# 4. القائمة الجانبية (Sidebar)
st.sidebar.title("🏢 شركة الربوة")
st.sidebar.write(f"👤 المستخدم: **Admin**")
st.sidebar.divider()

# التأكد من صلاحية الأدمن لعرض كامل القائمة
role = str(st.session_state.get('user_role', '')).strip().lower()

if role in ['admin', 'مدير']:
    menu_options = [
        "الرئيسية واختيار الأصناف",
        "تقارير البيع والشراء والأرباح",
        "المصاريف",
        "الحضور والانصراف",
        "إدارة وتعديل الصلاحيات والحسابات",
        "إعدادات بيانات الفاتورة والدعم"
    ]
else:
    menu_options = ["الرئيسية واختيار الأصناف"]

selected_page = st.sidebar.radio("قائمة النظام:", menu_options)

# 5. محتوى الصفحات
if selected_page == "الرئيسية واختيار الأصناف":
    st.title("🛒 شاشة اختيار الأصناف والفواتير")
    
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("➕ اختيار الأصناف", type="primary"):
            select_items_dialog()

    st.divider()
    st.subheader("📋 الأصناف المحددة حالياً:")

    if st.session_state.selected_items:
        for idx, item in enumerate(st.session_state.selected_items, start=1):
            c1, c2, c3 = st.columns([1, 4, 1])
            c1.write(f"**#{idx}**")
            c2.write(item)
            if c3.button("حذف", key=f"del_{idx}"):
                st.session_state.selected_items.remove(item)
                st.rerun()
                
        st.divider()
        if st.button("تفريغ القائمة بالكامل", type="secondary"):
            st.session_state.selected_items = []
            st.rerun()
    else:
        st.info("لم يتم اختيار أي أصناف بعد. اضغط على زر 'اختيار الأصناف' بالأنف للبدء.")

elif selected_page == "تقارير البيع والشراء والأرباح":
    st.title("📊 تقارير البيع والشراء والأرباح")
    st.write("محتوى تقارير المبيعات والأرباح...")

elif selected_page == "المصاريف":
    st.title("💸 إدارة المصاريف")
    st.write("محتوى تسجيل ومتابعة المصاريف...")

elif selected_page == "الحضور والانصراف":
    st.title("⏰ الحضور والانصراف")
    st.write("محتوى سجلات الحضور والانصراف...")

elif selected_page == "إدارة وتعديل الصلاحيات والحسابات":
    st.title("⚙️ إدارة وتعديل الصلاحيات والحسابات")
    st.write("محتوى التحكم في الموظفين والمستخدمين...")

elif selected_page == "إعدادات بيانات الفاتورة والدعم":
    st.title("⚙️ إعدادات بيانات الفاتورة والدعم")
    st.write("محتوى إعدادات الفواتير والتواصل مع الدعم...")
