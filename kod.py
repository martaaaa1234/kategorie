import streamlit as st
from supabase import create_client
import pandas as pd

# Pobieranie danych uwierzytelniających z secrets
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Supabase Inventory Manager", layout="wide")
st.title("📦 Manager Magazynu (Supabase)")

# --- ZAKŁADKI ---
tab1, tab2 = st.tabs(["📂 Kategorie", "🍎 Produkty"])

# --- TAB 1: KATEGORIE ---
with tab1:
    st.header("Zarządzanie Kategoriami")
    
    col_a, col_b = st.columns(2)
    with col_a:
        with st.form("add_cat_form"):
            st.subheader("Dodaj nową kategorię")
            c_nazwa = st.text_input("Nazwa kategorii")
            c_opis = st.text_area("Opis")
            if st.form_submit_button("Dodaj"):
                data = {"nazwa": c_nazwa, "opis": c_opis}
                supabase.table("kategorie").insert(data).execute()
                st.success("Kategoria dodana!")
                st.rerun()

    with col_b:
        st.subheader("Lista Kategorii")
        # Pobieranie danych z Supabase
        res_cats = supabase.table("kategorie").select("*").execute()
        df_cats = pd.DataFrame(res_cats.data)
        
        if not df_cats.empty:
            st.dataframe(df_cats, use_container_width=True)
            cat_id_del = st.number_input("ID kategorii do usunięcia", min_value=1, step=1, key="del_cat")
            if st.button("Usuń kategorię"):
                supabase.table("kategorie").delete().eq("id", cat_id_del).execute()
                st.warning(f"Usunięto kategorię {cat_id_del}")
                st.rerun()

# --- TAB 2: PRODUKTY ---
with tab2:
    st.header("Zarządzanie Produktami")
    
    # Pobranie kategorii do selectboxa
    res_cats_list = supabase.table("kategorie").select("id, nazwa").execute()
    df_cats_list = pd.DataFrame(res_cats_list.data)
    
    with st.expander("➕ Dodaj nowy produkt"):
        if not df_cats_list.empty:
            with st.form("add_prod_form"):
                p_nazwa = st.text_input("Nazwa produktu")
                p_liczba = st.number_input("Liczba", min_value=0, step=1)
                p_cena = st.number_input("Cena", min_value=0.0)
                
                cat_options = dict(zip(df_cats_list['nazwa'], df_cats_list['id']))
                p_kat_name = st.selectbox("Wybierz kategorię", options=list(cat_options.keys()))
                
                if st.form_submit_button("Zapisz produkt"):
                    prod_data = {
                        "nazwa": p_nazwa, 
                        "liczba": p_liczba, 
                        "cena": p_cena, 
                        "kategoria_id": cat_options[p_kat_name]
                    }
                    supabase.table("produkty").insert(prod_data).execute()
                    st.success("Produkt dodany!")
                    st.rerun()
        else:
            st.info("Najpierw dodaj kategorię.")

    st.subheader("Stan Magazynowy")
    # Pobieranie produktów z joinem do kategorii
    res_prods = supabase.table("produkty").select("id, nazwa, liczba, cena, kategorie(nazwa)").execute()
    if res_prods.data:
        # Przekształcenie zagnieżdżonego słownika z joinu na płaski format
        df_p = pd.json_normalize(res_prods.data)
        df_p.columns = ['ID', 'Nazwa', 'Liczba', 'Cena', 'Kategoria']
        st.table(df_p)
        
        p_id_del = st.number_input("ID produktu do usunięcia", min_value=1, step=1, key="del_prod")
        if st.button("Usuń wybrany produkt"):
            supabase.table("produkty").delete().eq("id", p_id_del).execute()
            st.success("Usunięto.")
            st.rerun()
