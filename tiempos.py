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
# Cálculo CPM (automático)
# =========================
G = nx.DiGraph()
for act, succs in sucesores.items():
    for s in succs:
        G.add_edge(act, s)

# Forward Pass
ES, EF = {}, {}
for act in nx.topological_sort(G):
    if not list(G.predecessors(act)):
        ES[act] = 0
    else:
        ES[act] = max(EF[p] for p in G.predecessors(act))
    EF[act] = ES[act] + duraciones[act]

# Backward Pass
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

st.markdown("👉 Ingresa tus cálculos de Inicio/Fin Temprano y Tardío para cada actividad:")

respuestas = {}
for act in duraciones.keys():
    st.subheader(f"Actividad {act} (Duración {duraciones[act]} días)")
    es = st.number_input(f"Inicio Temprano (ES) {act}", min_value=0, key=f"ES_{act}")
    ef = st.number_input(f"Fin Temprano (EF) {act}", min_value=0, key=f"EF_{act}")
    ls = st.number_input(f"Inicio Tardío (LS) {act}", min_value=0, key=f"LS_{act}")
    lf = st.number_input(f"Fin Tardío (LF) {act}", min_value=0, key=f"LF_{act}")
    respuestas[act] = {"ES": es, "EF": ef, "LS": ls, "LF": lf}

# Botón de corrección
if st.button("✅ Verificar respuestas"):
    st.subheader("📊 Corrección")

    errores = []
    for act in duraciones.keys():
        correcto = {"ES": ES[act], "EF": EF[act], "LS": LS[act], "LF": LF[act]}
        if respuestas[act] != correcto:
            errores.append(act)

        st.write(f"**{act}**")
        st.write(f"- Tu respuesta: {respuestas[act]}")
        st.write(f"- Correcto: {correcto}")
        st.markdown("---")

    # Resumen de resultados
    if errores:
        st.error(f"❌ Hubo errores en las siguientes actividades: {', '.join(errores)}")
    else:
        st.success("✅ ¡Perfecto! Todos los tiempos son correctos 🎉")

    # Mostrar ruta crítica
    st.subheader("🚀 Ruta Crítica")
    st.write(f"Actividades en la ruta crítica: {', '.join(ruta_critica)}")

    # Dibujar grafo con ruta crítica en rojo
    pos = nx.spring_layout(G, seed=42)
    colors = ["red" if n in ruta_critica else "lightblue" for n in G.nodes()]
    fig, ax = plt.subplots()
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1500, font_size=10, ax=ax)
    st.pyplot(fig)



