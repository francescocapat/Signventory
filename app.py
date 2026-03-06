import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Inventario Segnaletica Pro", layout="wide")

# Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNZIONI DI CARICAMENTO ---
def get_data(worksheet):
    return conn.read(worksheet=worksheet).dropna(how="all")

# --- INTERFACCIA ---
st.title("🚧 Sistema Segnaletica (Cloud Sync)")

# Caricamento dinamico delle liste dai fogli
# --- CODICE DETECTIVE PER DIAGNOSI ---
# --- NUOVO CODICE DETECTIVE ---
# --- CARICAMENTO DATI OTTIMIZZATO ---
try:
    # 1. Carichiamo il foglio principale (il primo a sinistra) come Movimenti
    df_movimenti = conn.read().dropna(how="all")
    
    # 2. Proviamo a caricare le liste. Se falliscono, usiamo liste vuote per non bloccare l'app
    try:
        materiali = conn.read(worksheet="Materiali")['item'].dropna().tolist()
    except:
        st.warning("⚠️ Foglio 'Materiali' non trovato. Uso lista di emergenza.")
        materiali = ["Ferro Scatolato", "Alluminio Piano", "Pellicola R1"]
        
    try:
        dimensioni = conn.read(worksheet="Dimensioni")['item'].dropna().tolist()
    except:
        st.warning("⚠️ Foglio 'Dimensioni' non trovato. Uso lista di emergenza.")
        dimensioni = ["Disco Ø 60 cm", "Triangolo 90 cm"]

    st.success("✅ Sistema pronto!")
except Exception as e:
    st.error(f"❌ Errore critico: {e}")
    st.stop()
    menu = ["📊 Dashboard", "➕ Registra", "⚙️ Impostazioni"]
choice = st.sidebar.selectbox("Menu", menu)

# --- SEZIONE: REGISTRA ---
if choice == "➕ Registra":
    with st.form("mov_form"):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.radio("Operazione", ["Entrata (+)", "Uscita (-)"])
            mat = st.selectbox("Materiale", materiali)
            dim = st.selectbox("Dimensione", dimensioni)
        with col2:
            qty = st.number_input("Quantità", min_value=1)
            d_prod = st.date_input("Data Produzione", datetime.now())
            note = st.text_input("Note")
        
        if st.form_submit_button("Invia a Google Sheets"):
            nuova_riga = pd.DataFrame([{
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Tipo": tipo,
                "Materiale": mat,
                "Dimensione": dim,
                "Quantita": qty if "Entrata" in tipo else -qty,
                "Data_Prod": d_prod.strftime("%d/%m/%Y"),
                "Note": note
            }])
            updated_df = pd.concat([df_movimenti, nuova_riga], ignore_index=True)
            conn.update(worksheet="Movimenti", data=updated_df)
            st.success("Dati salvati!")
            st.cache_data.clear()

# --- SEZIONE: DASHBOARD ---
elif choice == "📊 Dashboard":
    if not df_movimenti.empty:
        # Calcolo Giacenza
        giacenza = df_movimenti.groupby(["Materiale", "Dimensione"])["Quantita"].sum().reset_index()
        st.subheader("Giacenze in Tempo Reale")
        st.dataframe(giacenza, use_container_width=True, hide_index=True)
    else:
        st.info("Database vuoto.")

# --- SEZIONE: IMPOSTAZIONI ---
elif choice == "⚙️ Impostazioni":
    st.subheader("Aggiungi Nuovi Materiali/Formati")
    tipo_agg = st.selectbox("Cosa vuoi aggiungere?", ["Materiali", "Dimensioni"])
    nuovo_val = st.text_input("Nome nuovo elemento")
    
    if st.button("Salva Nuova Voce"):
        current_list = get_data(tipo_agg)
        nuova_voce = pd.DataFrame([{"item": nuovo_val}])
        updated_list = pd.concat([current_list, nuova_voce], ignore_index=True)
        conn.update(worksheet=tipo_agg, data=updated_list)
        st.success(f"{nuovo_val} aggiunto correttamente!")
        st.cache_data.clear()