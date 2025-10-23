import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""
    
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración de página
st.set_page_config(
    page_title="Mythos Canvas - Análisis Mitológico",
    page_icon="🔮",
    layout="centered"
)

# Estilos con tema rosa pastel
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        color: #8B4789;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8B4789, #E6A8D7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .canvas-container {
        background: linear-gradient(135deg, #FDF6F8, #FAF0F4);
        border: 3px solid #E6A8D7;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(139, 71, 137, 0.1);
    }
    .analyze-btn {
        background: linear-gradient(135deg, #8B4789, #D8A1C4);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1rem 0;
        width: 100%;
    }
    .analyze-btn:hover {
        background: linear-gradient(135deg, #7A3A78, #C891B4);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    .mythology-section {
        background: linear-gradient(135deg, #FFF0F5, #FFE4EC);
        border: 2px solid #D8A1C4;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .section-title {
        color: #8B4789;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E6A8D7;
        padding-bottom: 0.5rem;
    }
    .api-input {
        background: white;
        border: 2px solid #E6A8D7;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<div class="main-title">🔮 Mythos Canvas</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Descubre los secretos mitológicos y científicos de tus dibujos</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Configuración")
    
    with st.container():
        st.markdown("**🎨 Herramientas de Dibujo**")
        stroke_width = st.slider('Ancho del trazo', 1, 25, 8)
        stroke_color = st.color_picker('Color del trazo', '#8B4789')
    
    with st.container():
        st.markdown("**🔑 Configuración API**")
        api_key = st.text_input('Clave de OpenAI', type="password", 
                               help="Ingresa tu API key de OpenAI para usar la inteligencia artificial")
    
    st.markdown("---")
    st.markdown("### Acerca de")
    st.markdown("""
    **Mythos Canvas** analiza tus dibujos y revela:
    - **Mitología** relacionada
    - **Datos científicos** fascinantes  
    - **Historia** y simbolismo
    - **Conexiones culturales**
    """)

# Área principal de dibujo
st.markdown('<div class="section-title">Panel de Dibujo</div>', unsafe_allow_html=True)

canvas_result = st_canvas(
    fill_color="rgba(139, 71, 137, 0.2)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",
    height=400,
    width=600,
    drawing_mode="freedraw",
    key="canvas",
)

st.markdown('</div>', unsafe_allow_html=True)

# Botón de análisis
if st.button("🔍 Analizar Dibujo Mitológico", use_container_width=True, type="primary"):
    if canvas_result.image_data is not None and api_key:
        with st.spinner("🔮 Consultando los secretos del universo..."):
            # Procesar imagen
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
            input_image.save('img.png')
            
            # Codificar imagen
            base64_image = encode_image_to_base64("img.png")
            st.session_state.base64_image = base64_image
            
            # Prompt mejorado para análisis mitológico y científico
            prompt_text = """Analiza este dibujo y proporciona:
            
1. **ANÁLISIS MITOLÓGICO**: 
   - ¿Qué figuras mitológicas podrían estar representadas?
   - Significado simbólico en diferentes mitologías
   - Historias o leyendas relacionadas

2. **DATOS CIENTÍFICOS**:
   - Explicación científica si corresponde a fenómenos naturales
   - Curiosidades relevantes
   - Perspectiva histórica o antropológica

3. **INTERPRETACIÓN CULTURAL**:
   - Simbolismo en diferentes culturas
   - Representaciones artísticas similares

Responde en español, sé detallado pero conciso, separando claramente cada sección."""
            
            try:
                os.environ['OPENAI_API_KEY'] = api_key
                client = OpenAI(api_key=api_key)
                
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
                    max_tokens=800,
                )
                
                if response.choices[0].message.content is not None:
                    full_response = response.choices[0].message.content
                    
                    # Guardar en session_state
                    st.session_state.full_response = full_response
                    st.session_state.analysis_done = True
                    
            except Exception as e:
                st.error(f"❌ Error en el análisis: {str(e)}")
    else:
        if not api_key:
            st.warning("🔑 Por favor ingresa tu API key de OpenAI")
        if canvas_result.image_data is None:
            st.info("🎨 Dibuja algo en el panel para analizar")

# Mostrar resultados del análisis
if st.session_state.analysis_done and st.session_state.full_response:
    st.markdown("---")
    st.markdown('<div class="section-title">📜 Análisis Mitológico y Científico</div>', unsafe_allow_html=True)
    st.markdown('<div class="response-box">', unsafe_allow_html=True)
    st.write(st.session_state.full_response)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #8B4789; padding: 2rem 0;'>"
    "✨ Descubre la magia en tus trazos • Mythos Canvas 🔮"
    "</div>",
    unsafe_allow_html=True
)
