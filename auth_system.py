import streamlit as st
import time

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state.update({'logged_in': False, 'user': '', 'role': '', 'perms': {}})

    if not st.session_state['logged_in']:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<h2 style='text-align: center;'>🔐 بوابة الوكالة</h2>", unsafe_allow_html=True)
            with st.form("login"):
                u = st.text_input("المستخدم")
                p = st.text_input("كلمة المرور", type="password")
                if st.form_submit_button("دخول", use_container_width=True):
                    try:
                        res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
                        if res.data and res.data[0]['is_active']:
                            user = res.data[0]
                            st.session_state['logged_in'] = True
                            st.session_state['user'] = u
                            st.session_state['role'] = user['role']
                            # تحميل الصلاحيات
                            st.session_state['perms'] = {
                                'hunt': user.get('can_hunt', True),
                                'camp': user.get('can_campaign', True),
                                'share': user.get('can_share', True)
                            }
                            st.rerun()
                        else: st.error("خطأ في البيانات أو الحساب موقوف")
                    except: st.error("خطأ في الاتصال")
        return False
    return True
