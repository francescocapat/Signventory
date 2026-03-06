import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Inventario Segnaletica Pro", layout="wide")

# Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INIZIALIZZAZIONE VARIABILI DI EMERGENZA ---
# Definiamo il menu subito per evitare il NameError
menu = ["📊 Dashboard", "➕ Registra", "⚙️ Impostazioni"]
materiali = ["Ferro Scatolato", "Alluminio Piano", "Pellicola R1", "Pellicola R2", "Pellicola R3"]
dimensioni = ["Disco Ø 60 cm", "Triangolo 90 cm", "Quadrato 60x60 cm"]
df_movimenti = pd.DataFrame(columns=["Data", "Tipo", "Materiale", "Dimensione", "Quantita", "Data_Prod", "Note"])

# --- CARICAMENTO DATI DAL CLOUD ---
try:
    # 1. Carichiamo il foglio principale (Movimenti) - deve essere il primo a sinistra
    df_movimenti = conn.read().dropna(how="all")
    st.sidebar.success("✅ Database Movimenti Connesso")

    # 2. Proviamo a caricare i Materiali
    try:
        mat_df = conn.read(worksheet="Materiali")
        if not mat_df.empty:
            materiali = mat_df['item'].dropna().tolist()
    except Exception:
        st.sidebar.warning("⚠️ Uso materiali predefiniti")

    # 3. Proviamo a caricare le Dimensioni
    try:
        dim_df = conn.read(worksheet="Dimensioni")
        if not dim_df.empty:
            dimensioni = dim_df['item'].dropna().tolist()
    except Exception:
        st.sidebar.warning("⚠️ Uso dimensioni predefinite")

except Exception as e:
    st.error(f"❌ Errore critico di connessione: {e}")
    st.info("L'app userà le impostazioni di emergenza per permetterti di lavorare.")

# --- INTERFACCIA ---
st.title("🚧 Sistema Segnaletica (Cloud Sync)")
choice = st.sidebar.selectbox("Menu", menu)

# --- SEZIONE: REGISTRA ---
if choice == "➕ Registra":
    st.subheader("Registra Movimento Pezzi")
    with st.form("mov_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.radio("Operazione", ["Entrata (+)", "Uscita (-)"])
            mat = st.selectbox("Materiale", materiali)
            dim = st.selectbox("Dimensione", dimensioni)
        with col2:
            qty = st.number_input("Quantità", min_value=1, step=1)
            d_prod = st.date_input("Data Produzione", datetime.now())
            note = st.text_input("Note / Commessa")
        
        if st.form_submit_button("Salva su Google Sheets"):
            nuova_riga = pd.DataFrame([{
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Tipo": tipo,
                "Materiale": mat,
                "Dimensione": dim,
                "Quantita": qty if "Entrata" in tipo else -qty,
                "Data_Prod": d_prod.strftime("%d/%m/%Y"),
                "Note": note
            }])
            # Uniamo i nuovi dati a quelli vecchi e carichiamo
            updated_df = pd.concat([df_movimenti, nuova_riga], ignore_index=True)
            conn.update(data=updated_df) # Aggiorna il foglio primario
            st.success("✅ Caricato con successo! Aggiorna la pagina per vedere le giacenze.")
            st.balloons()

# --- SEZIONE: DASHBOARD ---
elif choice == "📊 Dashboard":
    st.subheader("Giacenze di Magazzino")
    if not df_movimenti.empty:
        # Calcolo Giacenza reale (Somma delle quantità)
        # Convertiamo la colonna Quantita in numerico per sicurezza
        df_movimenti["Quantita"] = pd.to_numeric(df_movimenti["Quantita"])
        giacenza = df_movimenti.groupby(["Materiale", "Dimensione"])["Quantita"].sum().reset_index()
        giacenza.columns = ["Materiale", "Dimensione", "Disponibili"]
        
        # Mostriamo la tabella con stile
        st.dataframe(giacenza, width='stretch', hide_index=True)
    else:
        st.info("Il magazzino è attualmente vuoto.")

# --- SEZIONE: IMPOSTAZIONI ---
elif choice == "⚙️ Impostazioni":
    st.info("Per aggiungere nuovi materiali o dimensioni in questa versione Cloud, aggiungi semplicemente una riga nei fogli 'Materiali' o 'Dimensioni' del tuo file Google Sheets e riavvia l'app.")