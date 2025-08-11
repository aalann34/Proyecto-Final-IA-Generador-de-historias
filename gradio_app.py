import gradio as gr
import openai
import os
from typing import Optional, Tuple
import pyttsx3
import threading
import io
from gtts import gTTS
import tempfile
from dotenv import load_dotenv

# Cargar configuracion de variables de entorno
load_dotenv()

def load_api_key_from_env():
    """
    Carga la clave de API de OpenAI desde archivo de configuracion
    """
    # Primer intento: usar dotenv
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key.strip():
        print(f"API key cargada desde dotenv: {api_key[:20]}...")
        return api_key.strip()
    
    # Segundo intento: lectura manual del archivo
    try:
        # Verificar que el archivo existe
        if not os.path.exists('.env'):
            print("Archivo .env no existe")
            return None
            
        # Leer archivo completo
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Contenido .env leido: {len(content)} caracteres")
            
        # Procesar linea por linea
        with open('.env', 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                print(f"Linea {line_num}: '{line[:50]}...'")
                
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    
                    # Limpiar comillas
                    if api_key.startswith('"') and api_key.endswith('"'):
                        api_key = api_key[1:-1]
                    if api_key.startswith("'") and api_key.endswith("'"):
                        api_key = api_key[1:-1]
                    
                    if api_key:
                        print(f"API key encontrada: {api_key[:20]}...")
                        return api_key
                        
    except FileNotFoundError:
        print("Archivo .env no encontrado")
    except Exception as e:
        print(f"Error leyendo .env: {e}")
    
    print("No se pudo cargar API key desde ninguna fuente")
    return None

class VoiceNarrator:
    """
    Maneja la conversion de texto a audio usando Google TTS
    """
    
    def __init__(self):
        self.engine = None
        self.setup_tts_engine()
    
    def setup_tts_engine(self):
        """Configura motor de sintesis de voz"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 0.9)
            
        except Exception as e:
            print(f"Error configurando TTS: {e}")
            self.engine = None
    
    def generate_audio_file(self, text: str, language: str = 'es') -> Optional[str]:
        """
        Convierte texto a archivo de audio MP3
        """
        try:
            clean_text = self.clean_text_for_tts(text)
            
            tts = gTTS(text=clean_text, lang=language, slow=False)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            tts.save(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generando audio: {e}")
            return None
    
    def clean_text_for_tts(self, text: str) -> str:
        """
        Limpia texto para optimizar la narracion
        """
        import re
        
        text = text.replace('\n\n', '. ')
        text = text.replace('\n', ' ')
        
        text = re.sub(r'[^\w\s.,;:¡!¿?áéíóúñüÁÉÍÓÚÑÜ-]', '', text)
        
        if len(text) > 5000:
            text = text[:4997] + "..."
        
        return text.strip()

class StoryGeneratorApp:
    """
    Aplicacion de generacion de historias usando GPT-4o mini
    """
    
    def __init__(self):
        self.client = None
        self.api_key = load_api_key_from_env()
        self.narrator = VoiceNarrator()
        self.setup_client()
    
    def setup_client(self):
        """Inicializa cliente OpenAI"""
        if self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Error configurando cliente: {e}")
                self.client = None
    
    def update_api_key(self, new_api_key: str):
        """Actualiza clave de API"""
        if new_api_key.strip():
            self.api_key = new_api_key.strip()
            self.setup_client()
    
    def generate_story(self, 
                      prompt: str, 
                      story_type: str, 
                      length: str, 
                      tone: str,
                      api_key_input: str = "") -> Tuple[str, str, Optional[str]]:
        """
        Genera historia personalizada usando modelo de lenguaje
        """
        
        if api_key_input.strip():
            self.update_api_key(api_key_input)
        
        if not self.client:
            return "", "Error: Cliente no configurado. Verificar API key.", None
        
        if not prompt.strip():
            return "", "Error: Se requiere concepto base.", None
        
        system_prompt = self._build_system_prompt(story_type, length, tone)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Concepto: {prompt}"}
                ],
                max_tokens=1500,
                temperature=0.8,
                top_p=0.9
            )
            
            story = response.choices[0].message.content
            status = f"Historia generada usando {response.model}"
            
            return story, status, None
            
        except openai.AuthenticationError:
            return "", "Error de autenticacion: Verificar API key", None
        except openai.RateLimitError:
            return "", "Error: Limite de uso excedido", None
        except openai.APIError as e:
            return "", f"Error de API: {str(e)}", None
        except Exception as e:
            return "", f"Error inesperado: {str(e)}", None
    
    def generate_audio_narration(self, story_text: str, voice_language: str = "es") -> Tuple[Optional[str], str]:
        """
        Genera narracion de audio para la historia
        """
        if not story_text.strip():
            return None, "Error: No hay contenido para narrar"
        
        try:
            audio_file = self.narrator.generate_audio_file(story_text, voice_language)
            if audio_file:
                return audio_file, "Audio generado correctamente"
            else:
                return None, "Error: Fallo en generacion de audio"
                
        except Exception as e:
            return None, f"Error en sintesis de voz: {str(e)}"
    
    def _build_system_prompt(self, story_type: str, length: str, tone: str) -> str:
        """
        Construye prompt para el modelo de IA
        """
        length_specs = {
            "Corta (100-300 palabras)": "Escriba una historia corta de 100-300 palabras.",
            "Media (300-600 palabras)": "Desarrolle una historia de 300-600 palabras.",
            "Larga (600-1000 palabras)": "Cree una historia extensa de 600-1000 palabras."
        }
        
        system_prompt = f"""Eres un escritor profesional especializado en narrativa.

PARAMETROS:
- Genero: {story_type}
- Extension: {length_specs.get(length, "Desarrolle historia apropiada.")}
- Tono: {tone}

REQUISITOS:
1. Estructura completa: inicio, desarrollo, climax, final
2. Personajes desarrollados con motivaciones claras
3. Dialogos que avancen la trama
4. Mantener tono {tone.lower()} consistente
5. Coherencia narrativa
6. Descripciones que creen atmosfera
7. Contenido apropiado

CONSIDERACIONES:
- Escribir con fluidez natural para lectura en voz alta
- Evitar construcciones complejas
- Ritmo narrativo apropiado

Genera una historia original basada en el concepto dado."""

        return system_prompt

def create_interface():
    """
    Crea interfaz grafica usando Gradio
    """
    
    app = StoryGeneratorApp()
    
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="gray"
    )
    
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
        margin: auto;
    }
    .story-output {
        font-family: 'Georgia', serif !important;
        line-height: 1.8 !important;
        padding: 25px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    .header-section {
        text-align: center !important;
        color: #2c3e50 !important;
        margin-bottom: 20px !important;
    }
    .config-panel {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 8px !important;
        border: 1px solid #e9ecef !important;
    }
    .audio-section {
        background-color: #f0f8ff !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border: 1px solid #b3d9ff !important;
        margin-top: 10px !important;
    }
    """
    
    with gr.Blocks(
        title="Generador de Historias con IA",
        theme=theme,
        css=custom_css
    ) as interface:
        
        gr.HTML("""
        <div class="header-section">
            <h1>GENERADOR DE HISTORIAS CON INTELIGENCIA ARTIFICIAL</h1>
            <h3>Sistema de Deep Learning con Sintesis de Voz</h3>
            <p>Implementado con GPT-4o mini y Google TTS usando Python y Gradio</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1, elem_classes=["config-panel"]):
                gr.Markdown("### Configuracion")
                
                api_key_input = gr.Textbox(
                    label="API Key OpenAI (opcional)",
                    placeholder="sk-...",
                    type="password",
                    info="Ingrese API key o use configuracion de entorno"
                )
                
                gr.Markdown("### Parametros de Historia")
                
                prompt_input = gr.Textbox(
                    label="Concepto Base",
                    placeholder="Describa la idea principal de la historia...",
                    lines=3,
                    info="Especifique la premisa narrativa",
                    value="Un robot que aprende a cocinar"
                )
                
                story_type = gr.Dropdown(
                    label="Genero",
                    choices=[
                        "Aventura", "Romance", "Misterio", "Ciencia Ficcion",
                        "Fantasy", "Terror", "Comedia", "Drama", "Historica", "Thriller"
                    ],
                    value="Aventura",
                    info="Seleccione genero literario"
                )
                
                length = gr.Dropdown(
                    label="Extension",
                    choices=[
                        "Corta (100-300 palabras)",
                        "Media (300-600 palabras)", 
                        "Larga (600-1000 palabras)"
                    ],
                    value="Media (300-600 palabras)",
                    info="Longitud del texto generado"
                )
                
                tone = gr.Dropdown(
                    label="Tono",
                    choices=[
                        "Dramatico", "Comico", "Serio", "Inspirador",
                        "Melancolico", "Misterioso", "Epico", "Romantico"
                    ],
                    value="Dramatico",
                    info="Tono emocional de la narrativa"
                )
                
                gr.Markdown("### Audio")
                
                voice_language = gr.Dropdown(
                    label="Idioma del Narrador",
                    choices=[
                        ("Español", "es"),
                        ("English", "en"),
                        ("Français", "fr"),
                        ("Deutsch", "de"),
                        ("Italiano", "it")
                    ],
                    value="es",
                    info="Idioma para sintesis de voz"
                )
                
                generate_btn = gr.Button(
                    "Generar Historia",
                    variant="primary",
                    size="lg"
                )
                
            with gr.Column(scale=2):
                gr.Markdown("### Historia Generada")
                
                story_output = gr.Textbox(
                    label="Texto Generado",
                    lines=20,
                    max_lines=30,
                    elem_classes=["story-output"],
                    placeholder="La historia aparecera aqui...",
                    show_copy_button=True,
                    interactive=False
                )
                
                with gr.Group(elem_classes=["audio-section"]):
                    gr.Markdown("### Narracion por Voz")
                    
                    generate_audio_btn = gr.Button(
                        "Generar Audio",
                        variant="secondary",
                        size="sm"
                    )
                    
                    audio_output = gr.Audio(
                        label="Archivo de Audio",
                        type="filepath",
                        autoplay=False,
                        show_download_button=True
                    )
                    
                    audio_status = gr.Textbox(
                        label="Estado del Audio",
                        lines=1,
                        interactive=False,
                        placeholder="Listo para generar audio..."
                    )
                
                status_output = gr.Textbox(
                    label="Estado del Sistema", 
                    lines=1,
                    interactive=False,
                    placeholder="Sistema listo"
                )
        
        generate_btn.click(
            fn=app.generate_story,
            inputs=[prompt_input, story_type, length, tone, api_key_input],
            outputs=[story_output, status_output, audio_output]
        )
        
        generate_audio_btn.click(
            fn=app.generate_audio_narration,
            inputs=[story_output, voice_language],
            outputs=[audio_output, audio_status]
        )
        
        gr.Markdown("### Ejemplos")
        examples = gr.Examples(
            examples=[
                ["Un detective que lee memorias de objetos", "Misterio", "Media (300-600 palabras)", "Misterioso"],
                ["Dos robots que desarrollan emociones", "Romance", "Media (300-600 palabras)", "Romantico"],
                ["Un chef con recetas magicas", "Fantasy", "Larga (600-1000 palabras)", "Dramatico"],
                ["Un gato que habla los miercoles", "Comedia", "Corta (100-300 palabras)", "Comico"]
            ],
            inputs=[prompt_input, story_type, length, tone]
        )
        
        gr.Markdown("""
        ### Informacion Tecnica
        
        **Modelo:** GPT-4o mini (OpenAI)  
        **Sintesis de Voz:** Google Text-to-Speech  
        **Framework:** Gradio  
        **Idiomas:** Español, Ingles, Frances, Aleman, Italiano  
        **Formato Audio:** MP3
        
        **Requisitos:**
        - Conexion a internet
        - API key de OpenAI valida
        - Navegador moderno
        """)
    
    return interface

def main():
    """
    Funcion principal de la aplicacion
    """
    print("Iniciando generador de historias...")
    print("Configurando interfaz...")
    print("Inicializando sintesis de voz...")
    
    interface = create_interface()
    
    print("Sistema listo")
    print("Lanzando aplicacion web...")
    
    interface.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()