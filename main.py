import openai
import os

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
                    # Limpiar comillas si existen
                    if api_key.startswith('"') and api_key.endswith('"'):
                        api_key = api_key[1:-1]
                    if api_key.startswith("'") and api_key.endswith("'"):
                        api_key = api_key[1:-1]
                    return api_key
    except FileNotFoundError:
        print("Error: No se encontro el archivo .env")
    except Exception as e:
        print(f"Error leyendo archivo .env: {e}")
    
    return os.getenv('OPENAI_API_KEY')

class StoryGenerator:
    """
    Clase principal para generar historias usando la API de OpenAI GPT-4o mini
    Implementa funcionalidad de deep learning para generacion de texto
    """
    
    def __init__(self):
        self.api_key = load_api_key_from_env()
        
        if not self.api_key:
            print("No se encontro la clave de API.")
            print("Opciones disponibles:")
            print("1. Verificar archivo .env con OPENAI_API_KEY")
            print("2. Ingresar clave manualmente")
            self.api_key = input("Ingrese su clave de API de OpenAI: ").strip()
        
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
            print(f"API key configurada correctamente")
        else:
            print("Error: No se pudo configurar la clave de API")
            self.client = None
    
    def generate_story(self, prompt, story_type="Aventura", length="Media", tone="Dramatico"):
        """
        Genera una historia usando el modelo GPT-4o mini
        
        Parametros:
        - prompt: idea base para la historia
        - story_type: genero de la historia
        - length: extension deseada
        - tone: tono narrativo
        
        Retorna: string con la historia generada
        """
        if not self.client:
            return "Error: Cliente de OpenAI no configurado"
        
        if not prompt.strip():
            return "Error: Se requiere un prompt valido"
        
        # Construccion del prompt del sistema para el modelo
        system_prompt = f"""Eres un escritor profesional especializado en narrativa creativa.

PARAMETROS DE GENERACION:
- Genero: {story_type}
- Extension: {length}
- Tono: {tone}

ESPECIFICACIONES TECNICAS:
1. Estructura narrativa completa: inicio, desarrollo, climax y resolucion
2. Desarrollo de personajes con arcos narrativos coherentes
3. Inclusion de dialogos cuando sea apropiado para el desarrollo
4. Mantenimiento consistente del tono especificado
5. Coherencia interna y logica narrativa
6. Uso de tecnicas descriptivas para ambientacion
7. Contenido apropiado para audiencia general

Genere una historia original basada en el concepto proporcionado."""

        try:
            # Llamada a la API de OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Concepto: {prompt}"}
                ],
                max_tokens=1200,
                temperature=0.8,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error en generacion: {str(e)}"

def main():
    """
    Funcion principal del programa
    Implementa interfaz de usuario para interaccion con el generador
    """
    print("GENERADOR DE HISTORIAS CON INTELIGENCIA ARTIFICIAL")
    print("Aplicacion de Deep Learning para Generacion de Texto")
    print("=" * 60)
    
    generator = StoryGenerator()
    
    if not generator.client:
        print("Error: No se pudo inicializar el sistema. Verifique configuracion.")
        return
    
    while True:
        print("\nNUEVA SESION DE GENERACION")
        print("-" * 40)
        
        # Entrada de datos del usuario
        prompt = input("Ingrese concepto base para la historia: ").strip()
        if not prompt:
            print("Error: Se requiere un concepto valido")
            continue
        
        # Seleccion de genero
        print("\nGeneros disponibles:")
        tipos = ["Aventura", "Romance", "Misterio", "Ciencia Ficcion", "Fantasy", 
                "Terror", "Comedia", "Drama", "Historica", "Thriller"]
        for i, tipo in enumerate(tipos, 1):
            print(f"{i:2d}. {tipo}")
        
        try:
            tipo_idx = int(input("Seleccione genero (1-10, por defecto=1): ") or "1") - 1
            story_type = tipos[tipo_idx] if 0 <= tipo_idx < len(tipos) else "Aventura"
        except:
            story_type = "Aventura"
        
        # Seleccion de extension
        print("\nExtensiones disponibles:")
        longitudes = ["Corta (100-300 palabras)", "Media (300-600 palabras)", "Larga (600-1000 palabras)"]
        for i, long in enumerate(longitudes, 1):
            print(f"{i}. {long}")
        
        try:
            long_idx = int(input("Seleccione extension (1-3, por defecto=2): ") or "2") - 1
            length = longitudes[long_idx] if 0 <= long_idx < len(longitudes) else "Media (300-600 palabras)"
        except:
            length = "Media (300-600 palabras)"
        
        # Seleccion de tono
        print("\nTonos narrativos disponibles:")
        tonos = ["Dramatico", "Comico", "Serio", "Inspirador", "Melancolico", 
                "Misterioso", "Epico", "Romantico"]
        for i, tono in enumerate(tonos, 1):
            print(f"{i}. {tono}")
        
        try:
            tono_idx = int(input("Seleccione tono (1-8, por defecto=1): ") or "1") - 1
            tone = tonos[tono_idx] if 0 <= tono_idx < len(tonos) else "Dramatico"
        except:
            tone = "Dramatico"
        
        # Proceso de generacion
        print(f"\nProcesando: Historia {story_type.lower()} con tono {tone.lower()}")
        print("Enviando solicitud al modelo GPT-4o mini...")
        
        story = generator.generate_story(prompt, story_type, length, tone)
        
        # Presentacion de resultados
        print("\n" + "=" * 80)
        print("RESULTADO DE GENERACION:")
        print("=" * 80)
        print(story)
        print("=" * 80)
        
        # Opcion de guardado
        guardar = input("\nGuardar resultado en archivo de texto? (s/n): ").lower()
        if guardar == 's':
            filename = f"historia_{story_type.lower().replace(' ', '_')}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"GENERO: {story_type}\n")
                    f.write(f"TONO: {tone}\n")
                    f.write(f"CONCEPTO: {prompt}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(story)
                print(f"Archivo guardado como: {filename}")
            except Exception as e:
                print(f"Error al guardar archivo: {e}")
        
        # Continuacion del programa
        continuar = input("\nGenerar otra historia? (s/n): ").lower()
        if continuar != 's':
            break
        
        print("\n" + "-" * 80)
    
    print("\nPrograma finalizado.")
    print("Desarrollado usando OpenAI GPT-4o mini API")

if __name__ == "__main__":
    main()