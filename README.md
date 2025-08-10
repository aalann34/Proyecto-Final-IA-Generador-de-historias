# Proyecto-de-Final-IA

## Información del Estudiante

**Nombre:** Alan Alberto Martinez Ubiera  
**Matrícula:** 23-eisn-2-062  
**Proyecto:** Generador de Historias con Inteligencia Artificial

---

## Descripción

Este proyecto es un generador de historias que usa inteligencia artificial. Permite crear cuentos personalizados seleccionando el género, tono y extensión que quieras.

## ¿Qué hace?

- Genera historias automáticamente usando IA
- Puedes elegir diferentes géneros (aventura, romance, misterio, etc.)
- Seleccionar el tono (dramático, cómico, serio, etc.)  
- Decidir qué tan larga quieres la historia
- Funciona tanto en línea de comandos como en interfaz web

## Tecnologías Utilizadas

- **Python** - Lenguaje de programación principal
- **OpenAI GPT-4o mini** - Modelo de inteligencia artificial para generar texto
- **Gradio** - Para crear la interfaz web
- **API de OpenAI** - Conexión con el modelo de IA

## Instalación

### 1. Activar entorno virtual
```bash
story_env\Scripts\activate
```

### 2. Instalar librerías necesarias
```bash
pip install openai gradio python-dotenv
```

### 3. Configurar API key
Crear un archivo `.env` con tu clave de OpenAI:
```
OPENAI_API_KEY=tu-clave-aqui
```

## Cómo usar

### Versión de consola:
```bash
python main.py
```

### Versión web:
```bash
python gradio_app.py
```
Luego abrir en el navegador: `http://localhost:7860`

## Archivos del proyecto

- `main.py` - Aplicación de consola
- `gradio_app.py` - Aplicación web  
- `.env` - Archivo con la clave de API
- `requirements.txt` - Lista de librerías necesarias

## Ejemplo de uso

1. Ejecutar el programa
2. Escribir una idea para la historia (ej: "Un robot que aprende a cocinar")
3. Seleccionar género, tono y extensión
4. El programa genera la historia automáticamente

## Requisitos

- Python 3.8+
- Clave de API de OpenAI (gratis en platform.openai.com)
- Conexión a internet

---

**Desarrollado por:** Alan Alberto Martinez Ubiera  
**Para:** Proyecto Final - Curso de Inteligencia Artificial  
**Año:** 2024