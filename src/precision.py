from collections import Counter
from pipeline_limpieza import *
from cliente import *
import json
import time


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las coincidencias entre referencia y respuesta."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())

def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 de dos listas de tokens."""
    coincidencias = contar_coincidencias(
        tokens_referencia, tokens_respuesta
    )

    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    resultado = {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }

    return resultado

def calcular_metricas(texto_referencia, texto_respuesta):
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)
    
    return calcular_precision_cobertura_f1(
        tokens_referencia, tokens_respuesta
    )

casos = [
    # --- Stock mínimo y alertas de reposición ---
    (
        "¿Cuándo tengo que volver a comprar harina de kilo?",
        "Debes comprar harina cuando el stock baje de cinco paquetes.",
    ),
    (
        "¿Cuál es el stock mínimo que debo mantener de aceite de litro?",
        "El stock mínimo de aceite de litro es de seis botellas.",
    ),
    (
        "¿Me queda suficiente azúcar para el fin de semana?",
        "Te quedan diez kilos de azúcar, cantidad suficiente para el fin de semana.",
    ),
    (
        "¿Qué mercadería está por debajo del stock de seguridad hoy?",
        "El arroz y la leche entera están bajo el mínimo configurado.",
    ),
    (
        "¿Cuántas bandejas de huevos debo pedir para no quedarme sin stock?",
        "Debes encargar tres bandejas de huevos para cubrir la semana.",
    ),

    # --- Proveedores y días de visita/pedido ---
    (
        "¿Qué día viene el camión de las bebidas CCU?",
        "El repartidor de CCU viene todos los martes por la mañana.",
    ),
    (
        "¿Quién es el proveedor que nos trae los lácteos Soprole?",
        "El proveedor de lácteos es Distribuidora del Sur, atendido por Don Marcos.",
    ),
    (
        "¿A qué número llamo para pedir más pan corriente si se acaba?",
        "Llama a Panadería Central al número anotado en tu contacto de proveedores.",
    ),
    (
        "¿Cuál es el monto mínimo de compra que exige el proveedor de cecinas?",
        "El pedido mínimo de cecinas es de veinticinco mil pesos.",
    ),
    (
        "¿Qué proveedor me entrega la harina y legumbres más barato?",
        "Mayorista Los Álamos ofrece el menor precio en harina y legumbres.",
    ),

    # --- Fechas de compra y recepción de mercadería ---
    (
        "¿Cuándo fue la última fecha que le compramos al proveedor de galletas?",
        "La última compra de galletas se registró el martes pasado.",
    ),
    (
        "¿Cuándo llega el pedido de fideos y conservas que encargué ayer?",
        "El pedido de fideos llegará mañana jueves antes del mediodía.",
    ),
    (
        "¿Cuánto tiempo hace que no compramos cloro y lavalozas?",
        "Hace tres semanas que no registras compras de productos de aseo.",
    ),
    (
        "¿Para qué fecha está programada la entrega de las bebidas?",
        "La entrega de bebidas está agendada para este viernes temprano.",
    ),

    # --- Registro de ingresos, facturas y mermas ---
    (
        "¿En qué momento debo registrar la mercadería que me deja el camión?",
        "Debes registrar los productos apenas recibas y revises la factura del repartidor.",
    ),
    (
        "¿Cómo anoto una caja de leche que llegó rota y no puedo vender?",
        "Regístrala como merma o devolución presionando el botón de producto dañado.",
    ),
    (
        "¿Dónde anoto el precio nuevo si el proveedor me subió el aceite?",
        "Actualiza el costo en la ficha del producto antes de confirmar la recepción.",
    ),
    (
        "¿Cómo ingreso al sistema diez sacos de papas que compré en la feria?",
        "Presiona Entrada de Mercadería, selecciona papas y escribe diez sacos.",
    ),
    (
        "¿Debo registrar las compras antes o después de colocar los productos en el estante?",
        "Registra las compras antes de ordenar los productos en las estanterías.",
    ),
    (
        "¿Qué hago con el papel de la guía de despacho que me firmó el chofer?",
        "Guarda el documento y registra el número de guía en la entrada de inventario.",
    ),
]

resultados = []

for i, (consulta, referencia) in enumerate(casos, 1):
    print(f"\n[{i}/{len(casos)}] Procesando: {consulta}")
    
    respuesta = consultar_modelo(
        consulta, 
        system_instruction="Responde en español con una definición breve, en una sola oración de máximo 15 palabras. Sin listas, ejemplos ni introducciones."
    )
    
    metricas = calcular_metricas(referencia, respuesta)
    
    print("Respuesta:", respuesta)
    print("Métricas:", metricas)
    
    resultados.append({
        "consulta": consulta,
        "referencia": referencia,
        "respuesta": respuesta,
        **metricas,
    })
    
    time.sleep(4)

resultados = sorted(resultados, key=lambda r: r["f1"])

with open("resultados_metricas.json", "w", encoding="utf-8") as archivo:
    json.dump(resultados, archivo, indent=2, ensure_ascii=False)

def resumir_metricas(resultados):
    if not resultados:
        return {
            "precision_promedio": 0,
            "cobertura_promedio": 0,
            "f1_promedio": 0,
        }
    n = len(resultados)
    return {
        "precision_promedio": sum(r["precision"] for r in resultados) / n,
        "cobertura_promedio": sum(r["cobertura"] for r in resultados) / n,
        "f1_promedio": sum(r["f1"] for r in resultados) / n,
    }

print("\n--- Promedios Generales ---")
print(resumir_metricas(resultados))

print("\n--- 3 Casos con F1 más bajo ---")
for caso in resultados[:3]:
    print(f"- {caso['consulta']} (F1: {caso['f1']:.2f})")

print("\n--- 3 Casos con F1 más alto ---")
for caso in resultados[-3:]:
    print(f"- {caso['consulta']} (F1: {caso['f1']:.2f})")