import streamlit as st
from datetime import datetime, timedelta
from database import supabase

def main():
    st.set_page_config(page_title="Hunter Pro CRM", layout="wide")
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login()
        return
    
    show_dashboard()

def show_login():
    st.title("🔐 Hunter Pro - تسجيل الدخول")
    
    with st.form("login"):
        username = st.text_input("المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.form_submit_button("دخول"):
            if username and password:
                st.success(f"مرحباً {username}! (سيتم تفعيل الدخول الفعلي قريباً)")
                st.session_state.authenticated = True
                st.session_state.user = {"username": username, "role": "admin"}
                st.rerun()
            else:
                st.error("ادخل البيانات المطلوبة")

def show_dashboard():
    st.title(f"🎯 لوحة تحكم Hunter Pro")
    
    # إحصائيات بسيطة
    st.subheader("📊 الإحصائيات")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("إجمالي العملاء", "150")
    with col2:
        st.metric("عملاء جدد", "25")
    with col3:
        st.metric("معدل النجاح", "68%")
    
    # بحث سريع
    st.subheader("🔍 بحث سريع")
    with st.form("quick_search"):
        intent = st.text_input("نية البحث", placeholder="مطلوب شقة في التجمع")
        city = st.selectbox("المدينة", ["القاهرة", "الجيزة", "الإسكندرية"])
        
        if st.form_submit_button("بدء البحث"):
            if intent:
                st.success(f"بدأ البحث عن: {intent} في {city}")
            else:
                st.error("ادخل نية البحث")
    
    # قائمة العملاء
    st.subheader("👥 العملاء المحتملين")
    st.info("قائمة العملاء ستعرض هنا بعد تفعيل الاتصال بقاعدة البيانات")

if __name__ == "__main__":
    main()
