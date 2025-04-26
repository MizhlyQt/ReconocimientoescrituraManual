import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración de la página
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')
with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
    bg_image = st.file_uploader("Carga una Imagen de Fondo:", type=["png", "jpg", "jpeg"])

st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarla")

# Configuración del lienzo
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = st.sidebar.color_picker("Selecciona el color del trazo", "#000000")
bg_color = '#FFFFFF'

background_image = None
if bg_image is not None:
    background_image = Image.open(bg_image)

# Crear el componente del lienzo
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Color de relleno fijo con algo de opacidad
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    background_image=background_image if bg_image else None,
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke

# Recuperar la clave API de OpenAI
api_key = os.environ['OPENAI_API_KEY']

# Inicializar el cliente de OpenAI con la clave API
client = OpenAI(api_key=api_key)

analyze_button = st.button("Analiza la imagen", type="secondary")

# Verificar si se ha dibujado algo en el lienzo, si está disponible la clave API, y si se ha presionado el botón
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Codificar la imagen
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
            
        prompt_text = (f"Describe en español brevemente la imagen")
    
        # Realizar la solicitud a la API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")
            # Actualización final después de la respuesta
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    # Avisos para acción requerida
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
