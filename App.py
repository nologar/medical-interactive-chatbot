import streamlit as st
import requests

# Configuración de la página
st.set_page_config(
    page_title="Asistente Cardiológico de Derivación",
    page_icon="🫠🩺",
    layout="centered"
)

# Inicializar el estado de la sesión para el historial del chat
if "chat" not in st.session_state:
    st.session_state.chat = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Título y advertencia
st.title("🫀🩺 Asistente Cardiológico de Derivación")

with st.container():
    st.markdown(
    """
    <div style="background-color:#fef3c7; border-left: 5px solid #f59e0b; padding: 1rem; border-radius: 6px;">
        <span style="color:#92400e; font-weight:bold;">⚠️ Advertencia:</span>
        <span style="color:#1f2937;">
        Este asistente tiene carácter exclusivamente orientativo y no sustituye, en ningún caso, el juicio clínico del profesional sanitario.
        Las recomendaciones aquí ofrecidas se basan en algoritmos y criterios estandarizados, pero deben ser valoradas siempre en el contexto clínico individual del paciente.
        La decisión final sobre la derivación y manejo corresponde únicamente al facultativo responsable, quien deberá ejercer su criterio profesional conforme a la información clínica disponible y a las guías de práctica clínica vigentes.
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# Mostrar el historial de la conversación
for mensaje in st.session_state.chat:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"], unsafe_allow_html=True)

# Entrada del usuario
prompt = st.chat_input("¿Derivo al paciente si tiene disnea y ECG anómalo.?")
if prompt:
    # Mostrar mensaje del usuario
    st.chat_message("user").markdown(prompt)
    st.session_state.chat.append({"rol": "user", "contenido": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Generando respuesta..."):
            try:
                response = requests.post(
                    "https://v0mokre1xk.execute-api.eu-west-3.amazonaws.com/dev/ask",
                    headers={"Content-Type": "application/json"},
                    json={"prompt": prompt, "session_id": st.session_state.session_id} if st.session_state.session_id else {"prompt": prompt}
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data.get("session_id")

                    # --- CORRECCIÓN DE FORMATO ---
                    recommendation = data["recommendation"].strip()
                    recommendation = recommendation.replace("\n\n", "<br><br>")
                    recommendation = recommendation.replace("\n", "<br>")

                    # Mostrar recomendación con HTML seguro
                    st.markdown(recommendation, unsafe_allow_html=True)

                    # Guardar en historial la recomendación formateada
                    st.session_state.chat.append({"rol": "assistant", "contenido": recommendation})

                    # Mostrar fragmentos y guías
                    with st.expander("📄 Fragmentos de contexto utilizados"):
                        for frag in data.get("context_fragments", []):
                            st.markdown(f"- {frag}")

                    with st.expander("📁 Guías utilizadas"):
                        for loc in data.get("locations", []):
                            st.markdown(f"- `{loc}`")

                else:
                    error_msg = response.json().get("error", "Error inesperado")
                    st.error(f"❌ Error: {error_msg}")
                    st.session_state.chat.append({"rol": "assistant", "contenido": f"❌ Error: {error_msg}"})

            except Exception as e:
                st.error("Error de conexión con el servidor.")
                st.session_state.chat.append({"rol": "assistant", "contenido": "Error de conexión con el servidor."})