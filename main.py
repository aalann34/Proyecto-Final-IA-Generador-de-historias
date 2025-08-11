import openai
import os
from dotenv import load_dotenv

# Cargar configuracion de variables de entorno
load_dotenv()

def load_api_key_from_env():
    """
    Carga la clave de API de OpenAI desde archivo de configuracion
    """
    # Cargar desde variables de entorno
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"API key cargada desde configuracion: {api_key[:20]}...")
        return api_key
    
    # Lectura directa como respaldo
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
                    print(f"API key cargada desde archivo: {api_key[:20]}...")
                    return api_key
    except FileNotFoundError:
        print("Archivo de configuracion no encontrado")
    except Exception as e:
        print(f"Error leyendo configuracion: {e}")
    
    print("No se pudo cargar API key")
    return None

class StoryGenerator:
    """
    Generador de historias usando GPT-4o mini de OpenAI
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
        """
        if not self.client:
            return "Error: Cliente de OpenAI no configurado"
        
        if not prompt.strip():
            return "Error: Se requiere un prompt valido"
        
        # Construccion del prompt del sistema
        system_prompt = f"""Eres un escritor profesional especializado en narrativa creativa.

PARAMETROS:
- Genero: {story_type}
- Extension: {length}
- Tono: {tone}

REQUISITOS:
1. Estructura completa: inicio, desarrollo, climax, final
2. Personajes desarrollados con motivaciones claras
3. Dialogos que avancen la trama
4. Mantener tono {tone.lower()} consistente
5. Coherencia narrativa
6. Descripciones que creen atmosfera
7. Contenido apropiado

Genera una historia original basada en el concepto dado."""

        try:
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
        
        prompt = input("Ingrese concepto base para la historia: ").strip()
        if not prompt:
            print("Error: Se requiere un concepto valido")
            continue
        
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
        
        print("\nExtensiones disponibles:")
        longitudes = ["Corta (100-300 palabras)", "Media (300-600 palabras)", "Larga (600-1000 palabras)"]
        for i, long in enumerate(longitudes, 1):
            print(f"{i}. {long}")
        
        try:
            long_idx = int(input("Seleccione extension (1-3, por defecto=2): ") or "2") - 1
            length = longitudes[long_idx] if 0 <= long_idx < len(longitudes) else "Media (300-600 palabras)"
        except:
            length = "Media (300-600 palabras)"
        
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
        
        print(f"\nProcesando: Historia {story_type.lower()} con tono {tone.lower()}")
        print("Enviando solicitud al modelo GPT-4o mini...")
        
        story = generator.generate_story(prompt, story_type, length, tone)
        
        print("\n" + "=" * 80)
        print("RESULTADO DE GENERACION:")
        print("=" * 80)
        print(story)
        print("=" * 80)
        
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
        
        continuar = input("\nGenerar otra historia? (s/n): ").lower()
        if continuar != 's':
            break
        
        print("\n" + "-" * 80)
    
    print("\nPrograma finalizado.")
    print("Desarrollado usando OpenAI GPT-4o mini API")

if __name__ == "__main__":
    main()