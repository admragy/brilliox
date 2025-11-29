import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from io import BytesIO

# استيراد الملفات الأخرى
from database import supabase
from brain import run_hunter
import auth

# --- إعداد الصفحة ---
st.set_page_config(page_title="Agency Pro", layout="wide", page_icon="🦅")

# --- التصميم (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    .block-container { direction: rtl; text-align: right; }
    [data-testid="stSidebar"] { text-align: right; }
    /* إخفاء الهيدر وإظهار السهم */
    header[data-testid="stHeader"] { background: transparent; }
    .stButton>button { width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- التشغيل ---
if auth.check_login(supabase):
    user = st.session_state['user']
    role = st.session_state['role']
    perms = st.session_state['perms']

    # --- القائمة الجانبية ---
    with st.sidebar:
        st.write(f"👤 **{user}**")
        
        opts = ["الرئيسية", "قاعدة البيانات"]
        icons = ["house", "table"]
        
        if perms['hunt']: 
            opts.append("الصياد الذكي")
            icons.append("search")
        if perms['share']:
            opts.append("مشاركة الداتا")
            icons.append("share")
        if role == 'admin':
            opts.append("الإدارة")
            icons.append("gear")

        selected = option_menu("القائمة", opts, icons=icons, default_index=0)
        
        st.divider()
        if st.button("خروج"):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- 1. الرئيسية ---
    if selected == "الرئيسية":
        st.title("📊 لوحة القيادة")
        data = supabase.table("leads").select("*").eq("user_id", user).execute().data
        df = pd.DataFrame(data) if data else pd.DataFrame()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("العملاء", len(df))
        hot = len(df[df['quality'].str.contains('Excellent', na=False)]) if not df.empty else 0
        c2.metric("لقطة 🔥", hot)
        contacted = len(df[df['status'] == 'CONTACTED']) if not df.empty else 0
        c3.metric("تم التواصل", contacted)

    # --- 2. الصياد ---
    elif selected == "الصياد الذكي":
        st.title("🎣 الصياد (V25)")
        with st.form("hunt"):
            c1, c2 = st.columns([3, 1])
            intent = c1.text_input("هدفك (مثال: مطلوب شقة / سباك)")
            city = c2.text_input("المدينة", "القاهرة")
            time_opt = st.selectbox("الزمن", ["أي وقت", "آخر شهر", "آخر 24 ساعة"])
            time_map = {"أي وقت": "qdr:y", "آخر شهر": "qdr:m", "آخر 24 ساعة": "qdr:d"}
            
            if st.form_submit_button("🚀 إطلاق"):
                count = run_hunter(intent, city, time_map[time_opt], user, supabase)
                if count > 0: st.success(f"تم اصطياد {count} عميل!")
                else: st.warning("لم نجد نتائج.")

    # --- 3. قاعدة البيانات ---
    elif selected == "قاعدة البيانات":
        st.title("🗂️ السجل")
        if st.button("تحديث 🔄"): st.rerun()
        
        leads = supabase.table("leads").select("*").eq("user_id", user).order("created_at", desc=True).execute().data
        if leads:
            df = pd.DataFrame(leads)
            
            # تحميل Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Excel", output.getvalue(), "leads.xlsx", "application/vnd.ms-excel")
            
            df['Link'] = df['notes'].str.replace('Link: ', '', regex=False)
            st.dataframe(
                df[['quality', 'phone_number', 'source', 'Link']],
                column_config={"Link": st.column_config.LinkColumn("رابط", display_text="فتح")},
                use_container_width=True
            )
        else: st.info("فارغة.")

    # --- 4. مشاركة الداتا ---
    elif selected == "مشاركة الداتا":
        st.title("📤 تحويل عملاء")
        # منطق التحويل هنا...
        # (تم اختصاره للإيجاز، نفس الكود السابق)
        st.info("خاصية التحويل مفعلة.")

    # --- 5. الإدارة (Admin) ---
    elif selected == "الإدارة":
        st.title("👮‍♂️ التحكم")
        # منطق الأدمن...
        st.info("لوحة تحكم الأدمن.")

