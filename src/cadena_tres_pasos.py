from dotenv import load_dotenv #lectura de variables de entorno
import os
from langchain_google_genai import ChatGoogleGenerativeAI #crea el modelo al que me quiero conectar
from langchain_core.prompts import PromptTemplate #importa la clase para crear una plantilla -> prompt dinámico
from langchain_core.output_parsers import StrOutputParser #parsea la respuesta y la transforma en un solo texto, sin datos innecesarios
from langchain_core.prompts import ChatPromptTemplate #plantilla que incluye el rol del sistema e instrucción

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

plantilla_extraccion = PromptTemplate.from_template(
    "Eres un asistente de inventario. Lee el siguiente dictado de un comerciante "
    "y extrae cada artículo mencionado con la cantidad o estado que se indica, "
    "uno por línea:\n\n{dictado}"
)
paso_extraccion = plantilla_extraccion | modelo | StrOutputParser()


plantilla_clasificacion = PromptTemplate.from_template(
        "A partir de estos artículos extraídos:\n\n{articulos_crudos}\n\n"
        "Estandariza el nombre de cada producto y clasifica su prioridad entre "
        "[URGENTE] (si está agotado) o [BAJO] (si queda poco stock). "
        "Entrega un artículo por línea."
    )
paso_clasificacion = plantilla_clasificacion | modelo | StrOutputParser()


plantilla_guia = PromptTemplate.from_template(
        "Convierte la siguiente lista clasificada en una guía de compras "
        "en viñetas markdown clara, sin introducciones ni despedidas:\n\n{clasificacion}"
    )
paso_guia = plantilla_guia | modelo | StrOutputParser()


cadena_tres_pasos = (
    paso_extraccion
    | (lambda articulos: {"articulos_crudos": articulos})
    | paso_clasificacion
    | (lambda clasificacion: {"clasificacion": clasificacion})
    | paso_guia
)

if __name__ == "__main__":
    dictado_prueba = (
        "Anota que se nos acabó por completo el Puré de papas, "
        "gelatina sabor fresa solo van quedando 2 unidades y polvos de hornear no quedan."
    )

    resultado = cadena_tres_pasos.invoke({"dictado": dictado_prueba})
    print("\n--- GUÍA GENERADA ---\n")
    print(resultado)