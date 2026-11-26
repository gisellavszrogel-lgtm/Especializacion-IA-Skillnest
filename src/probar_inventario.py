import json
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

INSTRUCCION = """Eres el asistente de registro de inventario de un negocio de barrio.
Extrae los datos de la frase del usuario y responde SOLO con un objeto JSON válido (sin markdown ni texto extra) con exactamente estas 5 claves:
- "accion": "entrada", "faltante" o "merma"
- "producto": nombre del producto en minúsculas
- "cantidad": número entero o null si no se menciona
- "unidad": unidad de medida o "unidad" por defecto
- "nota": texto breve con vencimiento u observación, o null si no hay
"""

FRASES = [
    "Anota 12 paquetes de arroz grado 1 que llegaron hoy.",
    "Se acabaron las bebidas cola de litro y medio, hay que pedir.",
    "Agrega 6 botellas de aceite de maravilla, vencen en agosto.",
    "Quedan solo 2 cajas de huevos.",
    "Registra 20 bolsas de azúcar de 1 kilo.",
    "Nos faltan fósforos y velas.",
    "Entraron 10 tarros de leche condensada.",
    "Baja 3 unidades de pan de molde porque se vencieron.",
    "Anota 15 paquetes de tallarines y 10 de salsa de tomate.",
    "Quedan 4 bolsas de carbón.",
    "Se está agotando el detergente líquido, quedan 2.",
    "Suma 8 packs de yogur natural que vencen en 10 días.",
    "Hay que reponer té en bolsita y café instantáneo.",
    "Registra 5 bidones de agua de 5 litros.",
    "Quedan 6 latas de atún.",
    "Anota 12 paquetes de galletas surtidas que llegaron hoy.",
    "Se acabaron las bolsas de basura grandes.",
    "Agrega 4 cajas de leche descremada.",
    "Quedan 3 kilos de papas.",
    "Suma 10 jabones de barra.",
]

CLAVES_ESPERADAS = {"accion", "producto", "cantidad", "unidad", "nota"}
ACCIONES_VALIDAS = {"entrada", "faltante", "merma"}

fallos = 0

for i, frase in enumerate(FRASES, start=1):
    resp = None
    for intento in range(4):
        try:
            resp = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=f"{INSTRUCCION}\n\nFrase: {frase}",
            )
            break
        except ServerError:
            espera = 2 * (intento + 1)
            print(f"[{i:02d}/20] 503 temporal, reintentando en {espera}s...")
            time.sleep(espera)

    if resp is None:
        fallos += 1
        print(f"[{i:02d}/20] FALLO -> No respondió tras reintentos (503)")
        continue

    texto = resp.text.strip()
    motivo = ""

    try:
        dato = json.loads(texto)
        if not isinstance(dato, dict):
            motivo = "No devolvió un objeto JSON único (ej. devolvió lista)"
        elif set(dato.keys()) != CLAVES_ESPERADAS:
            motivo = f"Claves incorrectas: {list(dato.keys())}"
        elif dato.get("accion") not in ACCIONES_VALIDAS:
            motivo = f"Acción inválida: {dato.get('accion')}"
    except json.JSONDecodeError:
        motivo = "No es JSON puro (incluyó texto extra o bloques markdown)"

    if motivo:
        fallos += 1
        print(f"[{i:02d}/20] FALLO -> {motivo}")
        print(f"        Respuesta: {texto[:120]}")
    else:
        print(f"[{i:02d}/20] OK    -> {texto}")

print("\n===============================")
print(f"RESULTADO FINAL: {fallos} de 20 respuestas fallaron ({fallos * 5}%)")
print("problema_de_formato_o_tono:", fallos >= 3)