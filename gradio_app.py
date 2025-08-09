import gradio as gr
import openai
import os
from typing import Optional, Tuple

def load_api_key_from_env():
    """
    Carga la clave de API de OpenAI desde el archivo .env
    Retorna la clave como string o None si no se encuentra
    """
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    if api_key.startswith('"') and api_key.endswith('"'):
                        api_key = api_key[1:-1]
                    if api_key.startswith("'") and api_key.endswith("'"):
                        api_key = api_key[1:-1]
                    return api_key
    except FileNotFoundError:
        pass
    except Exception:
        pass
    
    return os.getenv('OPENAI_API_KEY')

class StoryGeneratorApp:
    """
    Aplicación principal para generación de historias con IA
    Implementa interfaz gráfica usando Gradio y modelo GPT-4o mini
    """
    
    def __init__(self):
        self.client = None
        self.api_key = load_api_key_from_env()
        self.setup_client()
    
    def setup_client(self):
        """Configura el cliente de OpenAI"""
        if self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Error configurando cliente: {e}")
                self.client = None
    
    def update_api_key(self, new_api_key: str):
        """Actualiza la clave de API"""
        if new_api_key.strip():
            self.api_key = new_api_key.strip()
            self.setup_client()
    
    def generate_story(self, 
                      prompt: str, 
                      story_type: str, 
                      length: str, 
                      tone: str,
                      api_key_input: str = "") -> Tuple[str, str]:
        """
        Genera una historia basada en los parámetros especificados
        
        Parámetros:
        - prompt: concepto base para la historia
        - story_type: género narrativo
        - length: extensión deseada
        - tone: tono narrativo
        - api_key_input: clave de API opcional
        
        Retorna: tupla (historia_generada, estado_del_proceso)
        """
        
        # Actualizar API key si se proporciona una nueva
        if api_key_input.strip():
            self.update_api_key(api_key_input)
        
        # Validaciones
        if not self.client:
            return "", "Error: Cliente de OpenAI no configurado. Verifique su clave de API."
        
        if not prompt.strip():
            return "", "Error: Se requiere un concepto base para generar la historia."
        
        # Construcción del prompt del sistema
        system_prompt = self._build_system_prompt(story_type, length, tone)
        
        try:
            # Llamada a la API de OpenAI
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
            status = f"Historia generada exitosamente usando {response.model}"
            
            return story, status
            
        except openai.AuthenticationError:
            return "", "Error de autenticación: Verifique su clave de API de OpenAI"
        except openai.RateLimitError:
            return "", "Error: Límite de velocidad excedido. Intente nuevamente en unos momentos"
        except openai.APIError as e:
            return "", f"Error de API de OpenAI: {str(e)}"
        except Exception as e:
            return "", f"Error inesperado: {str(e)}"
    
    def _build_system_prompt(self, story_type: str, length: str, tone: str) -> str:
        """
        Construye el prompt del sistema para el modelo de IA
        """
        length_specs = {
            "Corta (100-300 palabras)": "Escriba una narrativa concisa de 100-300 palabras.",
            "Media (300-600 palabras)": "Desarrolle una historia de extensión media de 300-600 palabras.",
            "Larga (600-1000 palabras)": "Cree una narrativa extensa de 600-1000 palabras."
        }
        
        system_prompt = f"""Usted es un escritor profesional especializado en narrativa creativa y envolvente.

ESPECIFICACIONES DE GENERACIÓN:
- Género narrativo: {story_type}
- Extensión: {length_specs.get(length, "Desarrolle una historia de extensión apropiada.")}
- Tono narrativo: {tone}

DIRECTRICES TÉCNICAS:
1. Implemente estructura narrativa completa con inicio, desarrollo, clímax y resolución
2. Desarrolle personajes tridimensionales con motivaciones claras
3. Incorpore diálogos que avancen la trama y revelen personalidad
4. Mantenga consistencia en el tono {tone.lower()} establecido
5. Asegure coherencia lógica y continuidad narrativa
6. Utilice técnicas descriptivas para crear atmósfera inmersiva
7. Produzca contenido apropiado para audiencia general

Genere una historia original y técnicamente competente basada en el concepto proporcionado."""

        return system_prompt

def create_interface():
    """
    Crea y configura la interfaz gráfica usando Gradio
    Retorna la interfaz configurada para lanzamiento
    """
    
    app = StoryGeneratorApp()
    
    # Configuración de tema y estilos
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="gray"
    )
    
    # CSS personalizado para apariencia profesional
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
        margin: auto;
    }
    .story-output {
        font-family: 'Georgia', 'Times New Roman', serif !important;
        line-height: 1.8 !important;
        padding: 25px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    .header-text {
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
    """
    
    with gr.Blocks(
        title="Generador de Historias con IA",
        theme=theme,
        css=custom_css
    ) as interface:
        
        # Encabezado principal
        gr.HTML("""
        <div class="header-text">
            <h1>GENERADOR DE HISTORIAS CON INTELIGENCIA ARTIFICIAL</h1>
            <h3>Sistema de Deep Learning para Generación de Contenido Narrativo</h3>
            <p>Implementado con GPT-4o mini de OpenAI y interfaz Gradio</p>
        </div>
        """)
        
        with gr.Row():
            # Panel de configuración (columna izquierda)
            with gr.Column(scale=1, elem_classes=["config-panel"]):
                gr.Markdown("### Configuración del Sistema")
                
                # Campo para API key
                api_key_input = gr.Textbox(
                    label="Clave de API de OpenAI (opcional)",
                    placeholder="sk-...",
                    type="password",
                    info="Configure su clave de API o úsela desde variables de entorno"
                )
                
                gr.Markdown("### Parámetros de Generación")
                
                # Campo de concepto base
                prompt_input = gr.Textbox(
                    label="Concepto Base",
                    placeholder="Ejemplo: Un científico descubre una señal extraterrestre en su laboratorio...",
                    lines=3,
                    info="Describa la premisa fundamental de su historia"
                )
                
                # Selector de género
                story_type = gr.Dropdown(
                    label="Género Narrativo",
                    choices=[
                        "Aventura",
                        "Romance", 
                        "Misterio",
                        "Ciencia Ficción",
                        "Fantasy",
                        "Terror",
                        "Comedia",
                        "Drama",
                        "Histórica",
                        "Thriller"
                    ],
                    value="Aventura",
                    info="Seleccione el género predominante"
                )
                
                # Selector de extensión
                length = gr.Dropdown(
                    label="Extensión Narrativa",
                    choices=[
                        "Corta (100-300 palabras)",
                        "Media (300-600 palabras)", 
                        "Larga (600-1000 palabras)"
                    ],
                    value="Media (300-600 palabras)",
                    info="Determine la longitud del texto generado"
                )
                
                # Selector de tono
                tone = gr.Dropdown(
                    label="Tono Narrativo",
                    choices=[
                        "Dramático",
                        "Cómico",
                        "Serio",
                        "Inspirador",
                        "Melancólico",
                        "Misterioso", 
                        "Épico",
                        "Romántico"
                    ],
                    value="Dramático",
                    info="Establezca el tono emocional predominante"
                )
                
                # Botón de generación
                generate_btn = gr.Button(
                    "Generar Historia",
                    variant="primary",
                    size="lg"
                )
                
            # Panel de resultados (columna derecha)
            with gr.Column(scale=2):
                gr.Markdown("### Historia Generada")
                
                # Área de output de la historia
                story_output = gr.Textbox(
                    label="Resultado de Generación",
                    lines=25,
                    max_lines=35,
                    elem_classes=["story-output"],
                    placeholder="La historia generada aparecerá aquí...",
                    show_copy_button=True,
                    interactive=False
                )
                
                # Indicador de estado
                status_output = gr.Textbox(
                    label="Estado del Sistema", 
                    lines=1,
                    interactive=False,
                    placeholder="Sistema listo para generar contenido"
                )
        
        # Configuración del evento de generación
        generate_btn.click(
            fn=app.generate_story,
            inputs=[prompt_input, story_type, length, tone, api_key_input],
            outputs=[story_output, status_output]
        )
        
        # Sección de ejemplos predefinidos
        gr.Markdown("### Ejemplos de Conceptos Base")
        examples = gr.Examples(
            examples=[
                ["Un detective que puede percibir las emociones de los objetos en escenas de crimen", "Misterio", "Media (300-600 palabras)", "Misterioso"],
                ["Dos ingenieros de software desarrollan consciencia artificial por accidente", "Ciencia Ficción", "Media (300-600 palabras)", "Dramático"],
                ["Un chef descubre que sus recetas pueden alterar los recuerdos de los comensales", "Fantasy", "Larga (600-1000 palabras)", "Misterioso"],
                ["Una bibliotecaria viaja en el tiempo cada vez que lee un libro específico", "Aventura", "Media (300-600 palabras)", "Épico"],
                ["El último humano en la Tierra recibe una transmisión de radio misteriosa", "Drama", "Larga (600-1000 palabras)", "Melancólico"]
            ],
            inputs=[prompt_input, story_type, length, tone]
        )
        
        # Información técnica del sistema
        gr.Markdown("""
        ### Especificaciones Técnicas
        
        **Modelo de IA:** GPT-4o mini (OpenAI)  
        **Framework de Interfaz:** Gradio  
        **Lenguaje de Programación:** Python  
        **Arquitectura:** Cliente-Servidor con API REST  
        **Funcionalidades:** Generación de texto, personalización de parámetros, interfaz web responsiva
        
        ---
        
        **Nota Técnica:** Se requiere una clave de API válida de OpenAI para el funcionamiento del sistema.  
        Obtenga su clave en [platform.openai.com](https://platform.openai.com/)
        """)
    
    return interface

def main():
    """
    Función principal para lanzar la aplicación
    """
    print("Iniciando Generador de Historias con IA...")
    print("Configurando interfaz gráfica Gradio...")
    
    # Crear interfaz
    interface = create_interface()
    
    print("Sistema inicializado correctamente")
    print("Lanzando interfaz web...")
    
    # Lanzar aplicación
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