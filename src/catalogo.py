import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from database import supabase

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generar_embedding(texto: str) -> list[float]:
    """Convierte el texto del producto en una lista de 768 números."""
    respuesta = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texto,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    return respuesta.embeddings[0].values

def agregar_producto_catalogo(nombre: str, unidad: str = "unidades", stock_inicial: float = 0):
    """Genera el vector y guarda un producto nuevo en Supabase."""
    try:
        # 1. Creamos el texto descriptivo para el vector
        texto_a_vectorizar = f"{nombre} ({unidad})"
        vector = generar_embedding(texto_a_vectorizar)

        # 2. Preparamos la fila exacta que pide nuestra tabla SQL
        nuevo_producto = {
            "nombre_oficial": nombre,
            "unidad_estandar": unidad,
            "stock_actual": stock_inicial,
            "embedding": vector
        }

        # 3. Guardamos en Supabase
        resultado = supabase.table("catalogo_productos").insert(nuevo_producto).execute()
        print(f"Guardado: {nombre} | Stock: {stock_inicial} {unidad}")
        return resultado.data

    except Exception as e:
        print(f"Error al guardar '{nombre}': {e}")
        return None

if __name__ == "__main__":
    # Prueba rápida con 3 productos iniciales
    agregar_producto_catalogo("Café Nescafé Tradición 170g", "frascos", 12)
    agregar_producto_catalogo("Arroz Grado 1 1kg", "kilos", 25)
    agregar_producto_catalogo("Leche Entera 1L", "cajas", 18)