import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Pobieranie danych uwierzytelniających z secrets
# Muszą być zdefiniowane w panelu Streamlit Cloud lub .streamlit/secrets.toml
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

# 2. Inicjalizacja bez jawnego typowania 'Client'
@st.cache_resource
def init_connection():
    return create_client(url, key)

supabase = init_connection()

st.set_page_config(page_title="Manager Magazynu", layout="wide")
st.title("📦 System Magazynowy Supabase")

# --- ZAKŁADKI ---
tab1, tab2 = st.tabs(["📂 Kategorie", "🍎 Produkty"])

# --- TAB 1: KATEGORIE ---
with tab1:
    st.header("Kategorie")
    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.form("form_kat"):
            st.subheader("Nowa Kategoria")
            c_nazwa = st.text_input("Nazwa")
            c_opis = st.text_area("Opis")
            if st.form_submit_button("Dodaj"):
                supabase.table("kategorie").insert({"nazwa": c_nazwa, "opis": c_opis}).execute()
                st.success("Dodano!")
                st.rerun()

    with col_b:
        st.subheader("Lista")
        res_cats = supabase.table("kategorie").select("*").execute()
        if res_cats.data:
            df_cats = pd.DataFrame(res_cats.data)
            st.dataframe(df_cats, use_container_width=True)
            
            cat_id_del = st.number_input("ID do usunięcia", min_value=1, step=1)
            if st.button("Usuń kategorię"):
                supabase.table("kategorie").delete().eq("id", cat_id_del).execute()
                st.rerun()

# --- TAB 2: PRODUKTY ---
with tab2:
    st.header("Produkty")
    
    # Pobranie kategorii do wyboru
    res_cats_list = supabase.table("kategorie").select("id, nazwa").execute()
    df_cats_list = pd.DataFrame(res_cats_list.data)
