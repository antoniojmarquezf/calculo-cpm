import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# =========================
# Datos del proyecto
# =========================
sucesores = {
    "A": ["B", "C"],   # Diseñar planos
    "B": ["D"],        # Comprar materiales
    "C": ["D"],        # Construcción de cimentación
    "D": ["E", "F"],   # Montaje de bomba
    "E": ["G"],        # Conexión eléctrica
    "F": ["G"],        # Instalación de tuberías
    "G": []            # Pruebas finales
}

duraciones = {
    "A": 3,
    "B": 4,
    "C": 5,
    "D": 2,
    "E": 3,
    "F": 4,
    "G": 2
}

# =========================
# Cálculo CPM (automático para corrección)
# =========================
# Crear grafo dirigido
G = nx.DiGraph()
for act, succs in sucesores.items():
    for s in succs:
        G.add_edge(act, s)

# Forward Pass (Inicio/Fin temprano)
ES, EF = {}, {}
for act in nx.topological_sort(G):
    if not list(G.predecessors(act)):
        ES[act] = 0
    else:
        ES[act] = max(EF[p] for p in G.predecessors(act))
    EF[act] = ES[act] + duraciones[act]

# Backward Pass (Inicio/Fin tardío)
LS, LF = {}, {}
max_time = max(EF.values())
for act in reversed(list(nx.topological_sort(G))):
    if list(G.successors(act)):
        LF[act] = min(LS[s] for s in G.successors(act))
    else:
        LF[act] = max_time
    LS[act] = LF[act] - duraciones[act]

# Holgura
slack = {a: LS[a] - ES[a] for a in duraciones}
ruta_critica = [a for a, h in slack.items() if h == 0]

# =========================
# Interfaz Streamlit
# =========================
st.title("🎯 Juego CPM - Método de la Ruta Crítica")

st.markdown("Ingresa tus cálculos de Inicio/Fin Temprano y Tardío para cada actividad:")

# Formulario de respuestas del estudiante
respuestas = {}
for act in duraciones.keys():
    st.subheader(f"Actividad {act} (Duración {duraciones[act]} días)")
    es = st.number_input(f"Inicio Temprano (ES) {act}", min_value=0, key=f"ES_{act}")
    ef = st.number_input(f"Fin Temprano (EF) {act}", min_value=0, key=f"EF_{act}")
    ls = st.number_input(f"Inicio Tardío (LS) {act}", min_value=0, key=f"LS_{act}")
    lf = st.number_input(f"Fin Tardío (LF) {act}", min_value=0, key=f"LF_{act}")
    respuestas[act] = {"ES": es, "EF": ef, "LS": ls, "LF": lf}

# Botón para corregir
if st.button("✅ Verificar respuestas"):
    st.subheader("📊 Corrección")
    for act in duraciones.keys():
        st.write(f"**{act}**")
        st.write(f"- Tu respuesta: {respuestas[act]}")
        st.write(f"- Correcto: ES={ES[act]}, EF={EF[act]}, LS={LS[act]}, LF={LF[act]}")

    st.subheader("🚀 Ruta Crítica")
    st.write(f"Actividades en la ruta crítica: {', '.join(ruta_critica)}")

    # Dibujar grafo
    pos = nx.spring_layout(G)
    colors = ["red" if n in ruta_critica else "lightblue" for n in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1500, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): "" for u, v in G.edges()})
    st.pyplot(plt)


