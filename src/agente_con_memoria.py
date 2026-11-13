from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from pydantic import BaseModel, Field
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

import queue
import threading
import sys
from datetime import datetime, timezone
import json

#=== Configuraciones e Inicializaciones===
load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

#=== Persistencia y Análisis de Trazabilidad ===
def registrar_traza(session_id: str, entrada: str, resultado: dict) -> None:
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado.get("output", "")
    }

    with open("trazas_agente.jsonl", "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

#=== Auditoría/Human in the Loop ===
registro_aprobaciones = []

def esperar_aprobacion(mensaje: str, tiempo_limite_segundos: int = 15) -> bool:
    cola_respuesta = queue.Queue()

    def pedir_entrada():
        try:
            texto = input(mensaje)
            cola_respuesta.put(texto.strip().lower())
        except (EOFError, KeyboardInterrupt):
            cola_respuesta.put("")
    
    hilo = threading.Thread(target=pedir_entrada, daemon=True)
    hilo.start()

    try:
        respuesta = cola_respuesta.get(timeout=tiempo_limite_segundos)
        return respuesta == "s"
    except queue.Empty:
        print("Tiempo de espera agotado. Solicitud denegada por timeout")
        return False

def registrar_aprobacion(herramienta: str, argumentos: dict, aprobado: bool) -> None:
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "aprobado": aprobado,
        "fecha_hora": datetime.now().isoformat()
    })

#=== Esquemas de Validación ===
class ArgumentosConsultaStock(BaseModel):
    """Esquema para validar argumentos de consulta de inventario ante el LLM."""
    producto: str = Field(
        description="Nombre del producto a consultar, por ejemplo 'cafe' o 'arroz'."
    )

#=== Base de Datos Local ===
INVENTARIO = {
    "cafe": {"nombre": "Café Nescafé 170g", "stock": 10, "precio": 4500},
    "arroz": {"nombre": "Arroz Grado 1 1kg", "stock": 40, "precio": 1500}
}

#=== Herramientas ===
@tool(args_schema=ArgumentosConsultaStock)
def consultar_stock_producto(producto: str) -> str:
    """Consulta el stock y precio actual de un producto en el inventario (Riesgo bajo: solo lectura)."""
    item = INVENTARIO.get(producto.lower())
    if item is None:
        return f"No se encontró el producto '{producto}' en el inventario."
    return f"{item['nombre']}: {item['stock']} unidades disponibles (Precio: ${item['precio']})."

@tool
def calcular_valor_venta(cantidad: int, precio_unitario: float) -> str:
    """Calcula el total a cobrar por una venta según cantidad y precio unitario (Riesgo bajo: cálculo)."""
    total = cantidad * precio_unitario
    return f"El valor total es de ${total:.2f}"

@tool
def descontar_stock_venta(producto: str, cantidad: int) -> str:
    """Descuenta unidades del inventario por una venta. Acción con impacto en stock: requiere aprobación humana."""
    clave = producto.lower()
    if clave not in INVENTARIO:
        return f"No existe el producto '{producto}'."

    mensaje = f"[SUPERVISIÓN HUMANA REQUERIDA] Se descontarán {cantidad} unidades de '{producto}'. ¿Desea aprobar? (s/n): "
    aprobado = esperar_aprobacion(mensaje, tiempo_limite_segundos=15)

    registrar_aprobacion(
        herramienta="descontar_stock_venta",
        argumentos={"producto": producto, "cantidad": cantidad},
        aprobado=aprobado
    )

    if not aprobado:
        return "Descuento de stock no aprobado por el supervisor o cancelado por timeout."
    
    INVENTARIO[clave]["stock"] -= cantidad
    return f"Stock actualizado con éxito. Quedan {INVENTARIO[clave]['stock']} unidades de {INVENTARIO[clave]['nombre']}."

herramientas = [consultar_stock_producto, calcular_valor_venta, descontar_stock_venta]

#=== Gestión de historial en memoria ===
historiales = {}

def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]

#=== Construcción del agente ===
prompt_agente = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente de inventario que responde consultas y registra ventas usando las herramientas disponibles."),
    MessagesPlaceholder("chat_history"),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad")
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True,
    return_intermediate_steps=True
)

limpiar_salida = RunnableLambda(
    lambda d: {**d, "output": d["output"][0]["text"] if isinstance(d.get("output"), list) else d.get("output")}
)

cadena_agente = ejecutor_agente | limpiar_salida

agente_con_memoria = RunnableWithMessageHistory(
    cadena_agente,
    obtener_historial,
    input_messages_key="entrada",
    history_messages_key="chat_history",
    output_messages_key="output"
)

#=== Ejecución ===
if __name__ == "__main__":
    # 1. Prueba de riesgo bajo (Solo lectura)
    config1 = {"configurable": {"session_id": "tienda_01"}}
    entrada1 = "¿Cuánto stock de cafe queda?"
    resultado1 = agente_con_memoria.invoke({"entrada": entrada1}, config1)
    print(resultado1["output"])
    registrar_traza(session_id="tienda_01", entrada=entrada1, resultado=resultado1)

    # 2. Prueba de riesgo alto (Modifica stock y pide aprobación 's')
    entrada2 = "Vendí 3 unidades de cafe, descuéntalas del inventario."
    resultado2 = agente_con_memoria.invoke({"entrada": entrada2}, config1)
    print(resultado2["output"])
    registrar_traza(session_id="tienda_01", entrada=entrada2, resultado=resultado2)