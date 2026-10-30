from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

import time
from src import consumir_gemini
from src.cliente import con_reintento


def evaluar_modelo(nombre_modelo, pregunta, system_instruction, precio_entrada, precio_salida, repeticiones=4):
    """
    Ejecuta 'repeticiones' veces la misma petición para un modelo específico.
    Calcula e imprime Latencia, Costo y Respuesta de cada intento,
    captura posibles errores temporales de red/servidor (como el 503)
    y calcula el resumen acumulado al final.
    """
    print("=" * 70)
    print(f"EVALUANDO MODELO: {nombre_modelo}")
    print("=" * 70)

    latencias = []
    costos = []

    for i in range(1, repeticiones + 1):
        print(f"\n--- Intento {i} de {repeticiones} ({nombre_modelo}) ---")

        # 1. Armar la petición
        url, body = consumir_gemini.armar_peticion(nombre_modelo, pregunta, system_instruction)

        # 2. Captura de excepciones durante la conexión y el procesamiento
        try:
            inicio = time.perf_counter()
            datos = con_reintento(lambda: consumir_gemini.enviar_peticion(url, body))
            fin = time.perf_counter()

            latencia = fin - inicio
            latencias.append(latencia)

            costo = consumir_gemini.calcular_costo(datos, precio_entrada, precio_salida)
            costos.append(costo)

            respuesta = consumir_gemini.extraer_texto(datos)

            print(f"Latencia:  {latencia:.2f} segundos")
            print(f"Costo:     ${costo:.6f} USD")
            print(f"Respuesta: {respuesta.strip()}")

        except RuntimeError as error:
            # Atrapa errores 503, 500, caídas de red o JSON inválido
            print(f"Aviso en Intento {i}: {error}")
            print("Pausando 2 segundos para dar tiempo al servidor...")
            time.sleep(2)

    # 3. Resumen acumulado (solo si hubo al menos un intento exitoso)
    if latencias:
        latencia_promedio = sum(latencias) / len(latencias)
        costo_total = sum(costos)

        print("\n" + "-" * 40)
        print(f" RESUMEN {nombre_modelo}:")
        print(f" Latencia promedio: {latencia_promedio:.2f} segundos")
        print(f" Costo acumulado ({len(latencias)} peticiones exitosas): ${costo_total:.6f} USD")
        print("-" * 40 + "\n")
    else:
        print(f"\n[ALERTA] No se pudo completar ninguna petición para {nombre_modelo}.\n")


# ==============================================================================
# CONFIGURACIÓN GENERAL Y MODELOS A EVALUAR
# ==============================================================================
pregunta_prueba = ("Procesa la siguiente fila de CSV: ""'Prod: Chaleco Lana Merino Talla M; Cod_Interno: MER-CHAL-M; Bodega_Central: LOC_0987; Conteo_Fisico: 18 uds'")
instruccion_sistema = ("Eres Eva, asistente técnica de Kerna. Extrae los datos para facturación electrónica " "y responde exclusivamente en formato JSON con las claves: " "rut, razon_social, monto_total, tipo_documento. Sin formato Markdown ni comentarios.")


modelos = [
    {
        "nombre": "gemini-3.6-flash",
        "precio_entrada": 0.00000075,
        "precio_salida": 0.00000375,
    },
    {
        "nombre": "gemini-3.5-flash-lite",
        "precio_entrada": 0.0000003,
        "precio_salida": 0.0000025,
    },
    {
        "nombre": "gemini-3.8-flash",
        "precio_entrada": 0.00000075,
        "precio_salida": 0.00000375,
    },
]

# Bucle principal para evaluar los 3 modelos
for config in modelos:
    evaluar_modelo(
        nombre_modelo=config["nombre"],
        pregunta=pregunta_prueba,
        system_instruction=instruccion_sistema,
        precio_entrada=config["precio_entrada"],
        precio_salida=config["precio_salida"],
        repeticiones=4,
    )