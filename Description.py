import streamlit as st
import yfinance as yf
import altair as alt
import pandas as pd
import google.generativeai as genai

# Configura tu API Key
tokenGenAi = "AIzaSyAt3B4Xa7FRqbreSwXrEWnbHtMWW-O4EqI"
genai.configure(api_key=tokenGenAi)

# Cargar el modelo de Gemini
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Configuración de la app
st.set_page_config(page_title="Buscador de Empresas", layout="centered")
st.title("🔍 Buscador de acciones del mercado estadounidense")

# Entrada de símbolo y selector de intervalo
symbol = st.text_input("Ingresa el símbolo de la acción (ej. AAPL, MSFT, TSLA):", "", placeholder="Buscar...")
intervalo = st.selectbox("Selecciona el intervalo de precios históricos:", ["6mo", "1y", "5y", "max"])

if st.button("Buscar"):
    if symbol.strip():
        try:
            ticker = yf.Ticker(symbol.strip().upper())
            info = ticker.get_info()

            # Información general
            nombre_largo = info.get("longName", "NA")
            descripcion = info.get("longBusinessSummary", "NA")
            sector = info.get("sector", "NA")
            industria = info.get("industry", "NA")
            pais = info.get("country", "NA")

            # Traducción con Gemini
            prompt = f"Traduce al español este texto técnico de una empresa:\n\n{descripcion}"
            response = model.generate_content(prompt)
            descripcion_traducida = response.text

            # Mostrar información
            st.markdown(f"## {nombre_largo}")
            st.markdown(f"**Descripción traducida:**\n\n{descripcion_traducida}")

            st.markdown("---")
            st.subheader("Resumen de la compañía")
            st.markdown(f"**Sector:** {sector}")
            st.markdown(f"**Industria:** {industria}")
            st.markdown(f"**País:** {pais}")

            # Historial de precios
            hist = ticker.history(period=intervalo)
            hist = hist.reset_index()  # Asegura que la fecha esté como columna
            hist["MA20"] = hist["Close"].rolling(window=20).mean()  # Media móvil

            st.subheader("📈 Precio histórico con media móvil y volumen")

            # Gráfico de línea: Close + MA20
            lineas = alt.Chart(hist).mark_line().encode(
                x="Date:T",
                y=alt.Y("Close:Q", title="Precio de cierre"),
                tooltip=["Date:T", "Close:Q", "MA20:Q"]
            ).properties(height=300)

            ma20 = alt.Chart(hist).mark_line(strokeDash=[4,4], color="orange").encode(
                x="Date:T",
                y="MA20:Q"
            )

            # Gráfico de barras: Volumen
            barras = alt.Chart(hist).mark_bar(opacity=0.3).encode(
                x="Date:T",
                y=alt.Y("Volume:Q", title="Volumen"),
                tooltip=["Date:T", "Volume:Q"]
            ).properties(height=100)

            # Combinar gráficos
            chart = (lineas + ma20) & barras
            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"No se pudo obtener la información. Error: {str(e)}")
    else:
        st.warning("Por favor, ingresa un símbolo válido.")

