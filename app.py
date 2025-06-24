import streamlit as st
import json
import time
from datetime import datetime
from utils.document_processor import DocumentProcessor
from utils.ai_service import AIService
from utils.webhook_handler import WebhookHandler
from utils.excel_converter import ExcelConverter

# Configuración de la página
st.set_page_config(
    page_title="AI Quest Generator",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para el diseño simple
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .step-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
def init_session_state():
    defaults = {
        'step': 1,
        'full_text': '',
        'metadata': {},
        'embedding': None,
        'json_response': None,
        'processing_id': None,
        'excel_ready': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    init_session_state()
    
    # CSS personalizado con colores Atlantia
    st.markdown("""
    <style>
        /* Importar fuentes Atlantia */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Hind:wght@400;500;600&display=swap');
        
        /* Variables de colores Atlantia */
        :root {
            --atlantia-violet: #6546C3;
            --atlantia-purple: #AA49CA;
            --atlantia-lemon: #77C014;
            --atlantia-turquoise: #04D1CD;
            --atlantia-white: #FFFFFF;
            --atlantia-green: #23B776;
            --atlantia-yellow: #FFB73B;
            --atlantia-orange: #FF9231;
            --atlantia-red: #E61252;
            --atlantia-black: #000000;
        }
        
        /* Tipografía base Atlantia */
        * {
            font-family: 'Hind', sans-serif;
        }
        
        /* Títulos - Poppins Bold 24-18pt Violet */
        h1, .main-title {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            font-size: 24pt !important;
            color: var(--atlantia-violet) !important;
        }
        
        h2, .section-title {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            font-size: 20pt !important;
            color: var(--atlantia-violet) !important;
        }
        
        h3, .subsection-title {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            font-size: 18pt !important;
            color: var(--atlantia-violet) !important;
        }
        
        /* Subtítulos de indicadores - Hind 14pt Violet */
        .indicator-subtitle, .metric-label, .stMetric label {
            font-family: 'Hind', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14pt !important;
            color: var(--atlantia-violet) !important;
        }
        
        /* Cuerpo de texto - Hind 12pt Negro */
        p, .body-text, .stMarkdown, .stText, label {
            font-family: 'Hind', sans-serif !important;
            font-weight: 400 !important;
            font-size: 12pt !important;
            color: var(--atlantia-black) !important;
        }
        
        /* Elementos específicos de Streamlit */
        .stButton button {
            font-family: 'Hind', sans-serif !important;
            font-weight: 600 !important;
            font-size: 12pt !important;
        }
        
        .stSelectbox label, .stTextInput label, .stTextArea label {
            font-family: 'Hind', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14pt !important;
            color: var(--atlantia-violet) !important;
        }
        
        .stDataFrame, .stTable {
            font-family: 'Hind', sans-serif !important;
            font-size: 12pt !important;
        }
        
        .stExpander summary {
            font-family: 'Hind', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14pt !important;
            color: var(--atlantia-violet) !important;
        }
        
        /* Header principal con gradiente Atlantia */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, var(--atlantia-violet) 0%, var(--atlantia-purple) 100%);
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
        }
        
        .main-header h1 {
            color: white !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            font-size: 24pt !important;
            margin-bottom: 0.5rem;
        }
        
        .main-header h3 {
            color: rgba(255, 255, 255, 0.9) !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            font-size: 18pt !important;
        }
        
        .main-header p {
            color: rgba(255, 255, 255, 0.8) !important;
            font-family: 'Hind', sans-serif !important;
            font-size: 12pt !important;
            font-style: italic;
        }
        
        /* Logo container */
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .atlantia-logo {
            width: 60px;
            height: auto;
        }
        
        /* Contenedores de pasos */
        .step-container {
            background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
            border: 2px solid var(--atlantia-violet);
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 15px rgba(101, 70, 195, 0.1);
        }
        
        /* Caja de éxito */
        .success-box {
            background: linear-gradient(135deg, var(--atlantia-green) 0%, var(--atlantia-lemon) 100%);
            border: none;
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        /* Progress bar personalizada */
        .progress-step-active {
            background-color: var(--atlantia-violet) !important;
            color: white !important;
            border-radius: 8px;
            padding: 0.5rem;
            font-family: 'Hind', sans-serif !important;
            font-weight: 600 !important;
            font-size: 12pt !important;
            text-align: center;
        }
        
        .progress-step-completed {
            background-color: var(--atlantia-lemon) !important;
            color: white !important;
            border-radius: 8px;
            padding: 0.5rem;
            font-family: 'Hind', sans-serif !important;
            font-weight: 500 !important;
            font-size: 12pt !important;
            text-align: center;
        }
        
        .progress-step-pending {
            background-color: #f0f2f6;
            color: #666;
            border-radius: 8px;
            padding: 0.5rem;
            font-family: 'Hind', sans-serif !important;
            font-weight: 400 !important;
            font-size: 12pt !important;
            text-align: center;
        }
        
        /* Métricas personalizadas */
        .metric-container {
            background: white;
            border: 2px solid var(--atlantia-turquoise);
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(4, 209, 205, 0.1);
        }
        
        /* Botones primarios */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--atlantia-violet) 0%, var(--atlantia-purple) 100%) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(101, 70, 195, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(101, 70, 195, 0.4) !important;
        }
        
        /* Botones secundarios */
        .stButton > button[kind="secondary"] {
            background: white !important;
            border: 2px solid var(--atlantia-turquoise) !important;
            color: var(--atlantia-turquoise) !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        
        /* Alertas y notificaciones */
        .stAlert > div[data-baseweb="notification"] {
            border-radius: 10px !important;
        }
        
        .stSuccess > div {
            background-color: var(--atlantia-green) !important;
            color: white !important;
        }
        
        .stWarning > div {
            background-color: var(--atlantia-orange) !important;
            color: white !important;
        }
        
        .stError > div {
            background-color: var(--atlantia-red) !important;
            color: white !important;
        }
        
        .stInfo > div {
            background-color: var(--atlantia-turquoise) !important;
            color: white !important;
        }
        
        /* File uploader */
        .stFileUploader > div > div {
            border: 2px dashed var(--atlantia-violet) !important;
            border-radius: 10px !important;
            background-color: rgba(101, 70, 195, 0.05) !important;
        }
        
        /* Data editor */
        .stDataFrame {
            border: 2px solid var(--atlantia-turquoise) !important;
            border-radius: 10px !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background-color: rgba(101, 70, 195, 0.1) !important;
            border: 1px solid var(--atlantia-violet) !important;
            border-radius: 8px !important;
        }
        
        /* Inputs */
        .stTextInput > div > div > input {
            border: 2px solid #e0e0e0 !important;
            border-radius: 8px !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--atlantia-violet) !important;
            box-shadow: 0 0 0 3px rgba(101, 70, 195, 0.1) !important;
        }
        
        .stTextArea > div > div > textarea {
            border: 2px solid #e0e0e0 !important;
            border-radius: 8px !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--atlantia-violet) !important;
            box-shadow: 0 0 0 3px rgba(101, 70, 195, 0.1) !important;
        }
        
        /* Footer branding */
        .footer-branding {
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
            border-top: 2px solid var(--atlantia-turquoise);
            color: var(--atlantia-violet);
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principal con logo y branding
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    
    # Logo y título
    st.markdown("""
    <div class="logo-container">
        <svg class="atlantia-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="atlantiaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#04D1CD"/>
                    <stop offset="50%" style="stop-color:#6546C3"/>
                    <stop offset="100%" style="stop-color:#AA49CA"/>
                </linearGradient>
            </defs>
            <path d="M20,80 L50,20 L80,80 L65,80 L50,50 L35,80 Z" fill="url(#atlantiaGradient)" stroke="white" stroke-width="2"/>
        </svg>
        <div>
            <h1 style="margin: 0; font-size: 2.5rem;">AI Quest Generator</h1>
            <div style="color: rgba(255,255,255,0.9); font-size: 1.2rem; font-weight: 500;">Powered by Atlantia</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Generación Automática de Cuestionarios")
    st.markdown("*De Brief a Excel en minutos*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mostrar progreso
    show_progress_bar()
    
    # Renderizar paso actual
    if st.session_state.step == 1:
        step_upload_documents()
    elif st.session_state.step == 2:
        step_process_documents()
    elif st.session_state.step == 3:
        step_review_metadata()
    elif st.session_state.step == 4:
        step_generate_questionnaire()
    elif st.session_state.step == 5:
        step_edit_questionnaire()
    elif st.session_state.step == 6:
        step_download_excel()
    
    # Footer branding
    st.markdown('''
    <div class="footer-branding">
        🚀 Powered by <strong>Atlantia</strong> - Innovación en Investigación de Mercados
    </div>
    ''', unsafe_allow_html=True)

def show_progress_bar():
    """Muestra barra de progreso del proceso con colores Atlantia"""
    steps = ["📁 Cargar", "🔄 Procesar", "✏️ Revisar", "🎯 Generar", "🛠️ Editar", "📊 Descargar"]
    current = st.session_state.step
    
    cols = st.columns(6)
    for i, (col, step_name) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current:
                # Paso completado - Verde Atlantia
                st.markdown(f'''
                <div class="progress-step-completed">
                    ✅ {step_name}
                </div>
                ''', unsafe_allow_html=True)
            elif i == current:
                # Paso actual - Violeta Atlantia
                st.markdown(f'''
                <div class="progress-step-active">
                    🔄 {step_name}
                </div>
                ''', unsafe_allow_html=True)
            else:
                # Paso pendiente - Gris
                st.markdown(f'''
                <div class="progress-step-pending">
                    ⏳ {step_name}
                </div>
                ''', unsafe_allow_html=True)

def step_upload_documents():
    """Paso 1: Cargar documentos"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.subheader("📁 Paso 1: Cargar Documentos")
    
    st.markdown("""
    **Tipos de archivo soportados:** DOCX, PDF, TXT  
    **Documentos requeridos:** Brief del cliente y/o Kick-Off  
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Brief del Cliente**")
        brief_file = st.file_uploader(
            "Selecciona el Brief", 
            type=['docx', 'pdf', 'txt'],
            key="brief_uploader",
            help="Documento con contexto y objetivos"
        )
    
    with col2:
        st.markdown("**Kick-Off/Minuta**")
        ko_file = st.file_uploader(
            "Selecciona el KO", 
            type=['docx', 'pdf', 'txt'],
            key="ko_uploader",
            help="Documento con especificaciones metodológicas"
        )
    
    # Botón para continuar
    if brief_file or ko_file:
        if st.button("🚀 Continuar al Procesamiento", type="primary", use_container_width=True):
            # Guardar archivos en session state
            st.session_state.brief_file = brief_file
            st.session_state.ko_file = ko_file
            st.session_state.step = 2
            st.rerun()
    else:
        st.info("📋 Selecciona al menos un documento para continuar")
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_process_documents():
    """Paso 2: Procesar documentos"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.subheader("🔄 Paso 2: Procesamiento Automático")
    
    # Auto-procesar al llegar a este paso
    if st.session_state.full_text == "":
        with st.spinner("🔄 Procesando documentos..."):
            process_documents()
    
    if st.session_state.full_text:
        st.success("✅ Documentos procesados exitosamente")
        
        # Mostrar resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Caracteres extraídos", len(st.session_state.full_text))
        with col2:
            st.metric("🧠 Metadatos extraídos", len(st.session_state.metadata))
        with col3:
            st.metric("🔗 Embedding generado", "✅" if st.session_state.embedding else "❌")
        
        # Vista previa del texto
        with st.expander("👀 Vista previa del contenido extraído"):
            st.text_area("Contenido", st.session_state.full_text[:500] + "...", height=150, disabled=True)
        
        if st.button("➡️ Revisar Metadatos", type="primary", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def process_documents():
    """Procesa los documentos cargados"""
    try:
        processor = DocumentProcessor()
        ai_service = AIService()
        
        # Extraer texto
        full_text = ""
        
        if hasattr(st.session_state, 'brief_file') and st.session_state.brief_file:
            text1 = processor.extract_text(st.session_state.brief_file)
            full_text += text1
        
        if hasattr(st.session_state, 'ko_file') and st.session_state.ko_file:
            text2 = processor.extract_text(st.session_state.ko_file)
            full_text += "\n" + text2
        
        st.session_state.full_text = full_text
        
        # Extraer metadatos con IA
        metadata = ai_service.extract_metadata(full_text)
        st.session_state.metadata = metadata
        
        # Generar embedding
        embedding = ai_service.generate_embedding(full_text)
        st.session_state.embedding = embedding
        
    except Exception as e:
        st.error(f"❌ Error durante el procesamiento: {str(e)}")

def step_review_metadata():
    """Paso 3: Revisar metadatos"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.subheader("✏️ Paso 3: Revisar y Editar Metadatos")
    
    metadata = st.session_state.metadata
    
    with st.form("metadata_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_proyecto = st.text_input("Nombre del Proyecto", value=metadata.get("nombre_proyecto", ""))
            marca = st.text_input("Marca/Cliente", value=metadata.get("marca", ""))
            tipo_estudio = st.text_input("Tipo de Estudio", value=metadata.get("tipo_estudio", ""))
            target = st.text_area("Target", value=metadata.get("target", ""))
        
        with col2:
            industria = st.text_input("Industria", value=metadata.get("industria", ""))
            muestra_planificada = st.text_input("Muestra", value=metadata.get("muestra_planificada", ""))
            objetivo_general = st.text_area("Objetivo General", value=metadata.get("objetivo_general", ""))
            decisiones_a_tomar = st.text_area("Decisiones a Tomar", value=metadata.get("decisiones_a_tomar", ""))
# Preguntas de negocio
            st.markdown("**Preguntas de Negocio**")
            preguntas_text = "\n".join(metadata.get("preguntas_negocio", []))
            preguntas_negocio = st.text_area(
                "Una pregunta por línea", 
                value=preguntas_text, 
                height=100,
                help="Escribe cada pregunta de negocio en una línea separada"
            )
        
        col3, col4 = st.columns(2)
        with col3:
            submitted = st.form_submit_button("💾 Guardar y Continuar", type="primary")
        with col4:
            if st.form_submit_button("⬅️ Volver"):
                st.session_state.step = 2
                st.rerun()
        
        if submitted:
            # Actualizar metadata
            updated_metadata = {
                "nombre_proyecto": nombre_proyecto,
                "marca": marca,
                "tipo_estudio": tipo_estudio,
                "industria": industria,
                "target": target,
                "muestra_planificada": muestra_planificada,
                "objetivo_general": objetivo_general,
                "decisiones_a_tomar": decisiones_a_tomar,
                "preguntas_negocio": [p.strip() for p in preguntas_negocio.split('\n') if p.strip()],
                "hipotesis": metadata.get("hipotesis", ""),
                "texto_preview": st.session_state.full_text[:500],
                "archivo_link": "",
                "tiene_brief": metadata.get("tiene_brief", False),
                "tiene_kickoff": metadata.get("tiene_kickoff", False)
            }
            
            st.session_state.metadata = updated_metadata
            st.session_state.step = 4
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_generate_questionnaire():
    """Paso 4: Generar cuestionario"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.subheader("🎯 Paso 4: Generar Cuestionario")
    
    metadata = st.session_state.metadata
    
    # Mostrar resumen del proyecto
    st.markdown("### 📋 Resumen del Proyecto")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Proyecto", metadata.get("nombre_proyecto", "N/A"))
    with col2:
        st.metric("Tipo", metadata.get("tipo_estudio", "N/A"))
    with col3:
        st.metric("Marca", metadata.get("marca", "N/A"))
    
    # Botón de generación
    if not st.session_state.json_response:
        if st.button("🚀 Generar Cuestionario con IA", type="primary", use_container_width=True):
            generate_questionnaire()
    else:
        st.success("✅ Cuestionario generado exitosamente")
        
        # Mostrar información del cuestionario
        try:
            # Usar el método de limpieza del converter
            converter = ExcelConverter()
            data = converter.load_json_from_content(st.session_state.json_response)
            questions = data.get('questions', [])
            st.metric("📊 Total de preguntas generadas", len(questions))
            
            with st.expander("👀 Vista previa del cuestionario"):
                st.json(data['metadata'] if 'metadata' in data else {})
        except:
            st.warning("⚠️ Respuesta generada, preparando para descarga...")
        
        if st.button("➡️ Revisar y Editar Cuestionario", type="primary", use_container_width=True):
            st.session_state.step = 5
            st.rerun()
    
    # Botón volver
    if st.button("⬅️ Volver a Metadatos"):
        st.session_state.step = 3
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_questionnaire():
    """Genera el cuestionario enviando datos a Make"""
    try:
        webhook_handler = WebhookHandler()
        
        with st.spinner("🤖 Generando cuestionario con IA..."):
            # Generar ID único para el procesamiento
            processing_id = f"quest_{int(time.time())}"
            st.session_state.processing_id = processing_id
            
            # Enviar datos a Make y recibir respuesta
            success, response = webhook_handler.send_to_make(
                st.session_state.embedding,
                st.session_state.metadata,
                processing_id
            )
            
            if success:
                # Procesar la respuesta de Make
                if isinstance(response, dict):
                    # Ya es un diccionario JSON
                    st.session_state.json_response = json.dumps(response)
                elif isinstance(response, str):
                    # Es una string, verificar si es JSON válido
                    try:
                        # Verificar que es JSON válido
                        json.loads(response)
                        st.session_state.json_response = response
                    except json.JSONDecodeError:
                        # Si no es JSON válido, usar como respuesta raw
                        st.session_state.json_response = response
                else:
                    st.error("❌ Formato de respuesta inesperado de Make")
                    return
                
                st.success("✅ Cuestionario generado con IA")
                st.rerun()
            else:
                st.error(f"❌ Error al generar cuestionario: {response}")
                
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        
def step_edit_questionnaire():
    """Paso 5: Editar cuestionario de forma interactiva"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.subheader("🛠️ Paso 5: Editar Cuestionario")
    
    if not st.session_state.json_response:
        st.error("❌ No hay cuestionario generado. Vuelve al paso anterior.")
        return
    
    try:
        # Cargar datos actuales
        converter = ExcelConverter()
        data = converter.load_json_from_content(st.session_state.json_response)
        questions = data.get('questions', [])
        
        if not questions:
            st.error("❌ No se encontraron preguntas para editar.")
            return
        
        # Información del cuestionario
        st.markdown(f"### 📊 Editando {len(questions)} preguntas")
        
        # Botones de acción superiores
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info("💡 Haz cambios en la tabla y presiona 'Guardar Cambios' antes de continuar")
        with col2:
            if st.button("⬅️ Volver"):
                st.session_state.step = 4
                st.rerun()
        with col3:
            if st.button("➡️ Finalizar"):
                st.session_state.step = 6
                st.rerun()
        
        # Editor de preguntas con st.data_editor
        st.markdown("### ✏️ Editor de Preguntas")
        
        # Preparar datos para el editor
        edit_data = []
        for i, q in enumerate(questions):
            edit_data.append({
                'ID': q.get('No. Pregunta', f'P{i+1}'),
                'Módulo': q.get('KPI base o Modulo', ''),
                'Pregunta': q.get('Pregunta', ''),
                'Tipo': q.get('Tipo de respuesta', ''),
                'Opciones': q.get('Opciones de respuesta', '').replace('\r\n', ' | '),
                'Indicador': q.get('Indicador', ''),
                'Lógica': q.get('Lógica de programación', '')
            })
        
        # Configuración de columnas para el editor
        column_config = {
            'ID': st.column_config.TextColumn('ID', width='small'),
            'Módulo': st.column_config.TextColumn('Módulo', width='medium'),
            'Pregunta': st.column_config.TextColumn('Pregunta', width='large'),
            'Tipo': st.column_config.SelectboxColumn(
                'Tipo',
                options=[
                    'Única',
                    'Múltiple', 
                    'Abierta',
                    'Matriz de opción única por fila',
                    'Ranking',
                    'Numérica Abierta / Slider',
                    'Texto/Imagen',
                    'Única (Escala)',
                    'Heat map / Image Highlighter'
                ],
                width='medium'
            ),
            'Opciones': st.column_config.TextColumn('Opciones (separar con |)', width='large'),
            'Indicador': st.column_config.TextColumn('Indicador', width='medium'),
            'Lógica': st.column_config.TextColumn('Lógica', width='large')
        }
        
        # Editor interactivo
        edited_data = st.data_editor(
            edit_data,
            column_config=column_config,
            num_rows="dynamic",  # Permite agregar/eliminar filas
            use_container_width=True,
            height=400,
            key="questionnaire_editor"
        )
        
        # Botón para guardar cambios
        if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
            save_questionnaire_changes(edited_data, data)
            st.success("✅ Cambios guardados exitosamente")
            st.rerun()
        
        # Mostrar estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total preguntas", len(edited_data))
        with col2:
            tipos_unicos = len(set(row['Tipo'] for row in edited_data if row['Tipo']))
            st.metric("🎯 Tipos únicos", tipos_unicos)
        with col3:
            modulos_unicos = len(set(row['Módulo'] for row in edited_data if row['Módulo']))
            st.metric("📋 Módulos únicos", modulos_unicos)
        
        # Vista previa de cambios
        if len(edited_data) != len(questions):
            st.info(f"ℹ️ Has modificado el número de preguntas: {len(questions)} → {len(edited_data)}")
    
    except Exception as e:
        st.error(f"❌ Error al cargar el editor: {str(e)}")
        
        # Debug info
        with st.expander("🔍 Debug Info"):
            st.write("**Error detallado:**", str(e))
            st.write("**Tipo de json_response:**", type(st.session_state.json_response))
    
    st.markdown('</div>', unsafe_allow_html=True)

def save_questionnaire_changes(edited_data, original_data):
    """Guarda los cambios del editor en el session state"""
    try:
        # Convertir datos editados de vuelta al formato original
        new_questions = []
        for row in edited_data:
            question = {
                'No. Pregunta': row['ID'],
                'KPI base o Modulo': row['Módulo'],
                'Pregunta': row['Pregunta'],
                'Tipo de respuesta': row['Tipo'],
                'Opciones de respuesta': row['Opciones'].replace(' | ', '\r\n'),
                'Indicador': row['Indicador'],
                'Lógica de programación': row['Lógica']
            }
            new_questions.append(question)
        
        # Actualizar metadata
        updated_data = original_data.copy()
        updated_data['questions'] = new_questions
        if 'metadata' in updated_data:
            updated_data['metadata']['totalQuestions'] = len(new_questions)
        
        # Guardar en session state
        st.session_state.json_response = json.dumps(updated_data)
        
    except Exception as e:
        st.error(f"❌ Error al guardar cambios: {str(e)}")

def step_download_excel():
    """Paso 5: Descargar Excel"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.subheader("📊 Paso 5: Descargar Cuestionario")
    
    if st.session_state.json_response:
        try:
            converter = ExcelConverter()
            excel_data = converter.json_to_excel(st.session_state.json_response)
            
            # Información del archivo
            # Usar el método de limpieza del converter
            converter = ExcelConverter()
            data = converter.load_json_from_content(st.session_state.json_response)
            metadata = data.get('metadata', {})
            questions = data.get('questions', [])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📋 Total preguntas", len(questions))
            with col2:
                st.metric("📁 Archivo", metadata.get('fileName', 'cuestionario'))
            with col3:
                st.metric("📊 Formato", "Excel (.xlsx)")
            
            # Mostrar preview de las primeras preguntas
            with st.expander("👀 Vista previa de preguntas generadas"):
                if len(questions) > 0:
                    st.write(f"**Mostrando 3 de {len(questions)} preguntas:**")
                    for i, q in enumerate(questions[:3], 1):
                        st.write(f"**{q.get('No. Pregunta', f'P{i}')}:** {q.get('Pregunta', 'Sin texto')[:100]}...")
                
            # Botón de descarga
            filename = f"cuestionario_{metadata.get('fileName', 'generated')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            
            st.download_button(
                label="📥 Descargar Cuestionario Excel",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )
            
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("### 🎉 ¡Proceso Completado!")
            st.markdown("Su cuestionario ha sido generado exitosamente y está listo para descargar.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botón para nuevo proyecto
            # Botón para volver al editor
            if st.button("⬅️ Volver al Editor", use_container_width=True):
                st.session_state.step = 5
                st.rerun()
                # Reset session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error al generar Excel: {str(e)}")
            
            # Debug info para troubleshooting
            with st.expander("🔍 Debug Info"):
                st.write("**Tipo de json_response:**", type(st.session_state.json_response))
                st.write("**Contenido (primeros 500 chars):**")
                st.text(str(st.session_state.json_response)[:500])
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()