import streamlit as st
import sqlite3
import pandas as pd

# Inicjalizacja bazy danych zgodnie ze schematem
def init_db():
    conn = sqlite3.connect('magazyn.db', check_same_thread=False)
    c = conn.cursor()
    # Tabela Kategorie
    c.execute('''CREATE TABLE IF NOT EXISTS kategorie
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nazwa TEXT NOT NULL, 
                  opis TEXT)''')
    # Tabela Produkty
    c.execute('''CREATE TABLE IF NOT EXISTS produkty
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nazwa TEXT NOT NULL, 
                  liczba INTEGER, 
                  cena REAL, 
                  kategoria_id INTEGER,
                  FOREIGN KEY(kategoria_id) REFERENCES kategorie(id))''')
    conn.commit()
    return conn

db_conn = init_db()
cursor = db_conn.cursor()

st.set_page_config(page_title="Manager Magazynu", layout="wide")
st.title("📦 System Zarządzania Produktami i Kategoriami")

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
                cursor.execute("INSERT INTO kategorie (nazwa, opis) VALUES (?, ?)", (c_nazwa, c_opis))
                db_conn.commit()
                st.success("Kategoria dodana!")
                st.rerun()

    with col_b:
        st.subheader("Lista i Usuwanie")
        df_cats = pd.read_sql("SELECT * FROM kategorie", db_conn)
        st.dataframe(df_cats, use_container_width=True)
        
        cat_id_del = st.number_input("ID kategorii do usunięcia", min_value=1, step=1)
        if st.button("Usuń kategorię"):
            cursor.execute("DELETE FROM kategorie WHERE id = ?", (cat_id_del,))
            db_conn.commit()
            st.warning(f"Usunięto kategorię o ID {cat_id_del}")
            st.rerun()

# --- TAB 2: PRODUKTY ---
with tab2:
    st.header("Zarządzanie Produktami")
    
    # Pobranie kategorii do selectboxa
    df_cats_for_prod = pd.read_sql("SELECT id, nazwa FROM kategorie", db_conn)
    
    with st.expander("➕ Dodaj nowy produkt"):
        if not df_cats_for_prod.empty:
            with st.form("add_prod_form"):
                p_nazwa = st.text_input("Nazwa produktu")
                p_liczba = st.number_input("Liczba (szt.)", min_value=0, step=1)
                p_cena = st.number_input("Cena", min_value=0.0, format="%.2f")
                
                cat_options = dict(zip(df_cats_for_prod['nazwa'], df_cats_for_prod['id']))
                p_kat_name = st.selectbox("Wybierz kategorię", options=list(cat_options.keys()))
                
                if st.form_submit_button("Zapisz produkt"):
                    cursor.execute("""INSERT INTO produkty (nazwa, liczba, cena, kategoria_id) 
                                   VALUES (?, ?, ?, ?)""", 
                                   (p_nazwa, p_liczba, p_cena, cat_options[p_kat_name]))
                    db_conn.commit()
                    st.success("Produkt dodany!")
                    st.rerun()
        else:
            st.error("Musisz najpierw dodać przynajmniej jedną kategorię!")

    st.subheader("Stan Magazynowy")
    query = """
    SELECT p.id, p.nazwa, p.liczba, p.cena, k.nazwa as kategoria 
    FROM produkty p 
    LEFT JOIN kategorie k ON p.kategoria_id = k.id
    """
    df_prods = pd.read_sql(query, db_conn)
    st.table(df_prods)

    if not df_prods.empty:
        prod_id_del = st.number_input("ID produktu do usunięcia", min_value=1, step=1)
        if st.button("Usuń wybrany produkt"):
            cursor.execute("DELETE FROM produkty WHERE id = ?", (prod_id_del,))
            db_conn.commit()
            st.success("Produkt usunięty.")
            st.rerun()
