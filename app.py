import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Cargar los datos desde el archivo Excel
df = pd.read_excel(fr"C:\Users\vidal\Desktop\Transformed_Plantillas_y_precios.xlsx")


# Inicializar las selecciones previas en la sesión de Streamlit si no existen
if 'jugadores_seleccionados' not in st.session_state:
    st.session_state.jugadores_seleccionados = {}

# Título de la aplicación
st.title("App Simulador Plantillas")

# Definir las alineaciones
ALINEACIONES = {
    "532": {"PORTERO": 1, "DEFENSA": 5, "MEDIOCENTRO": 3, "DELANTERO": 2},
    "433": {"PORTERO": 1, "DEFENSA": 4, "MEDIOCENTRO": 3, "DELANTERO": 3},
    "442": {"PORTERO": 1, "DEFENSA": 4, "MEDIOCENTRO": 4, "DELANTERO": 2}
}

# Crear un selectbox para seleccionar la alineación
alineacion = st.selectbox("Selecciona una alineación", list(ALINEACIONES.keys()))

# Mostrar la alineación seleccionada
st.subheader(f"Alineación seleccionada: {alineacion}")

# Filtros de precio y equipo para búsqueda
precio_min, precio_max = st.slider("Rango de precio", min_value=float(df['Precio'].min()), max_value=float(df['Precio'].max()), value=(float(df['Precio'].min()), float(df['Precio'].max())))
equipo_filtro = st.selectbox("Filtrar por equipo", options=["Todos"] + df['Equipo'].unique().tolist())

# Filtrar los jugadores según el precio y equipo seleccionado, pero solo para los desplegables
df_filtrado = df[(df['Precio'] >= precio_min) & (df['Precio'] <= precio_max)]

if equipo_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Equipo'] == equipo_filtro]

# Función para distribuir los selectores de jugadores
def distribuir_posiciones(posicion, cantidad):
    cols = st.columns(cantidad)
    for i in range(cantidad):
        key = f"{posicion}_{i+1}"
        jugadores_posicion = df[df['Posición'] == posicion]['Jugador'].tolist()
        opciones_filtradas = df_filtrado[df_filtrado['Posición'] == posicion]['Jugador'].tolist()
        seleccion_previa = st.session_state.jugadores_seleccionados.get(key, [])
        seleccion_actual = [jugador for jugador in seleccion_previa if jugador in jugadores_posicion]

        with cols[i]:
            seleccionados = st.multiselect(f"Selecciona {posicion} {i+1}", opciones_filtradas + seleccion_actual,
                                           default=seleccion_actual,
                                           max_selections=1,
                                           key=key)
            if seleccionados:
                st.session_state.jugadores_seleccionados[key] = seleccionados
                precio_jugador = df[df['Jugador'] == seleccionados[0]]['Precio'].values[0]
                st.write(f"Precio: {precio_jugador} millones")

# Crear los selectores distribuidos por posición
for posicion, cantidad in ALINEACIONES[alineacion].items():
    st.subheader(f"{posicion}:")
    distribuir_posiciones(posicion, cantidad)

# Calcular el presupuesto gastado
precio_total = 0
jugadores_seleccionados = []
for key, seleccion in st.session_state.jugadores_seleccionados.items():
    if seleccion:
        precio_total += df[df['Jugador'].isin(seleccion)]['Precio'].sum()
        jugadores_seleccionados.extend(seleccion)

total_presupuesto = 250 - precio_total
st.subheader(f"Presupuesto restante: {total_presupuesto:.2f} millones")

# Comprobar si se ha excedido el presupuesto
if total_presupuesto < 0:
    st.warning("¡Has excedido el presupuesto!")

# Validación final para asegurarse de que se han seleccionado todos los jugadores requeridos
completo = True
for posicion, cantidad in ALINEACIONES[alineacion].items():
    for i in range(cantidad):
        key = f"{posicion}_{i+1}"
        if len(st.session_state.jugadores_seleccionados.get(key, [])) == 0:
            completo = False
            break

if completo and total_presupuesto >= 0:
    st.success("Alineación completa dentro del presupuesto.")
else:
    st.error("Faltan jugadores por seleccionar o te has excedido del presupuesto.")

# ==============================
# Resumen Estadístico
# ==============================
if completo and total_presupuesto >= 0:
    st.header("Resumen Estadístico")

    # Crear DataFrame de los jugadores seleccionados
    df_seleccionados = df[df['Jugador'].isin(jugadores_seleccionados)]

    # Gráfico de barras de jugadores más caros a más baratos
    st.subheader("Jugadores más caros a más baratos")
    df_ordenado = df_seleccionados.sort_values(by='Precio', ascending=True)
    fig, ax = plt.subplots()
    ax.barh(df_ordenado['Jugador'], df_ordenado['Precio'], color='blue')
    ax.set_xlabel('Precio (millones)')
    st.pyplot(fig)

    # Gráfico circular del presupuesto según la zona del campo
    st.subheader("Presupuesto según zona del campo")
    df_seleccionados['Zona'] = df_seleccionados['Posición'].apply(lambda x: 'Portero' if x == 'PORTERO' else ('Defensa' if x == 'DEFENSA' else ('Mediocentro' if x == 'MEDIOCENTRO' else 'Delantero')))
    presupuesto_por_zona = df_seleccionados.groupby('Zona')['Precio'].sum()

    fig2, ax2 = plt.subplots()
    ax2.pie(presupuesto_por_zona, labels=presupuesto_por_zona.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')  # Para que el gráfico sea circular
    st.pyplot(fig2)

    # Estadísticas adicionales
    st.subheader("Estadísticas Adicionales")
    
    # Jugador más caro
    jugador_mas_caro = df_ordenado.iloc[0]['Jugador']
    precio_mas_caro = df_ordenado.iloc[0]['Precio']
    st.write(f"Jugador más caro: {jugador_mas_caro} ({precio_mas_caro} millones)")

    # Equipo más utilizado
    equipo_mas_utilizado = df_seleccionados['Equipo'].mode()[0]
    st.write(f"Equipo más utilizado: {equipo_mas_utilizado}")

    # Total jugadores por equipo
    jugadores_por_equipo = df_seleccionados['Equipo'].value_counts()
    st.write("Jugadores por equipo:")
    st.write(jugadores_por_equipo)
