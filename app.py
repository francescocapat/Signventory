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
try:
    # Recuperiamo l'elenco di TUTTI i nomi dei fogli presenti nel tuo file
    fogli_disponibili = conn.list_worksheets()
    st.write(f"🔍 Fogli trovati nel tuo file Google: `{fogli_disponibili}`")
    
    # Tentativo di caricamento mirato
    df_movimenti = conn.read(worksheet="Movimenti")
    materiali = conn.read(worksheet="Materiali")['item'].tolist()
    dimensioni = conn.read(worksheet="Dimensioni")['item'].tolist()
    st.success("✅ Connessione riuscita!")
except Exception as e:
    st.error(f"❌ Errore specifico: {e}")
    st.info("Controlla se i nomi sopra corrispondono esattamente a Movimenti, Materiali e Dimensioni.")
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