import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAZIONE ---
FILE_DATA = "magazzino_dati.csv"

# Dimensioni predefinite come richiesto
DIMENSIONI = [
    "Disco Ø 40 cm", "Disco Ø 60 cm", "Disco Ø 90 cm",
    "Triangolo 60 cm", "Triangolo 90 cm", "Triangolo 120 cm",
    "Quadrato 40x40 cm", "Quadrato 60x60 cm", "Quadrato 90x90 cm",
    "Rettangolo 40x60 cm", "Rettangolo 60x90 cm", "Rettangolo 25x105 cm",
    "Ottagono 60 cm (STOP)", "Ottagono 90 cm (STOP)"
]

MATERIALI = ["Ferro Scatolato", "Alluminio Piano", "Pellicola R1", "Pellicola R2", "Pellicola R3"]

# --- FUNZIONI DATI ---
def load_data():
    if os.path.exists(FILE_DATA):
        return pd.read_csv(FILE_DATA)
    return pd.DataFrame(columns=["Data", "Tipo", "Materiale", "Dimensione", "Quantità", "Data_Prod", "Note"])

def save_data(df):
    df.to_csv(FILE_DATA, index=False)

# --- INTERFACCIA ---
st.set_page_config(page_title="Inventario Segnaletica", layout="wide")
st.title("🚧 Gestione Produzione Segnaletica")

df = load_data()

# Sidebar per inserimento
st.sidebar.header("➕ Nuovo Movimento")
with st.sidebar.form("form_inserimento"):
    tipo = st.selectbox("Tipo Operazione", ["Entrata (+)", "Uscita (-)"])
    mat = st.selectbox("Materiale", MATERIALI)
    dim = st.selectbox("Dimensione", DIMENSIONI)
    qty = st.number_input("Quantità", min_value=1, step=1)
    data_p = st.date_input("Data Produzione (se Pellicola)", datetime.now())
    note = st.text_input("Note/Commessa")
    
    submit = st.form_submit_button("Registra Movimento")

if submit:
    nuova_riga = {
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Tipo": tipo,
        "Materiale": mat,
        "Dimensione": dim,
        "Quantità": qty if "Entrata" in tipo else -qty,
        "Data_Prod": data_p.strftime("%d/%m/%Y"),
        "Note": note
    }
    df = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
    save_data(df)
    st.sidebar.success("Registrato con successo!")

# --- DASHBOARD PRINCIPALE ---
tab1, tab2 = st.tabs(["📊 Giacenze Attuali", "📜 Storico Movimenti"])

with tab1:
    st.subheader("Stato del Magazzino")
    if not df.empty:
        # Calcolo Giacenza
        giacenza = df.groupby(["Materiale", "Dimensione"])["Quantità"].sum().reset_index()
        giacenza.columns = ["Materiale", "Dimensione", "Pezzi in Magazzino"]
        
        # Filtro rapido
        search = st.text_input("Filtra per materiale o dimensione...")
        if search:
            giacenza = giacenza[giacenza.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        st.dataframe(giacenza, use_container_width=True, hide_index=True)
    else:
        st.info("Il magazzino è vuoto. Inserisci il primo movimento dalla barra laterale.")

with tab2:
    st.subheader("Ultimi 50 movimenti")
    st.dataframe(df.iloc[::-1].head(50), use_container_width=True, hide_index=True)
    
    if st.button("Scarica Backup Excel"):
        df.to_csv("backup_inventario.csv", index=False)
        st.success("File generato localmente.")