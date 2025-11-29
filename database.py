import os
import streamlit as st
from supabase import create_client

# محاولة جلب المفاتيح من الـ Secrets (لو محلي) أو Environment (لو سيرفر)
try:
    SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    DB_STATUS = True
except:
    supabase = None
    DB_STATUS = False

def init_db():
    if not DB_STATUS: return
    # دالة للتأكد من وجود الجداول (للاحتياط)
    pass
  
