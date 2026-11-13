import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from database import supabase
from inventario import buscar_producto, registrar_movimiento

load_dotenv()

# --- 1. HERRAMIENTAS LANGCHAIN (@tool) ---
@tool
def tool_consultar_stock(producto: str) -> str:
    """Consulta el stock disponible de un producto en el catálogo."""
    item = buscar_producto(producto)
    if not item:
        return f"No encontré ningún producto parecido a '{producto}'."
    return f"Producto: {item['nombre_oficial']} | Stock: {item['stock_actual']} {item['unidad_estandar']}"

@tool
def tool_registrar_movimiento(producto: str, tipo: str, cantidad: float, precio: float = None) -> str:
    """Registra una 'entrada' (compra) o 'salida' (venta/uso) de inventario."""
    exito = registrar_movimiento(producto, tipo, cantidad, precio)
    if exito:
        return f"Movimiento registrado: {tipo} de {cantidad} en '{producto}'."
    return f"No pude registrar el movimiento para '{producto}'."

herramientas = [tool_consultar_stock, tool_registrar_movimiento]
mapa_herramientas = {t.name: t for t in herramientas}

# --- 2. MODELO LANGCHAIN CON TOOLS ---
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.environ.get("GEMINI_API_KEY"),
    temperature=0.2
).bind_tools(herramientas)

# --- 3. MEMORIA EN SUPABASE ---
def guardar_mensaje(session_id: str, rol: str, mensaje: str):
    supabase.table("historial_chat").insert({
        "session_id": session_id,
        "rol": rol,
        "mensaje": mensaje
    }).execute()

def obtener_historial(session_id: str, limite: int = 6) -> list:
    res = supabase.table("historial_chat")\
        .select("rol, mensaje")\
        .eq("session_id", session_id)\
        .order("creado_en", desc=True)\
        .limit(limite)\
        .execute()
    
    mensajes = [
        SystemMessage(
            content="Eres un asistente experto de inventario. SIEMPRE consulta tus herramientas antes de afirmar si un producto existe o cuál es su stock. Responde breve y claro."
        )
    ]
    for m in reversed(res.data):
        if m["rol"] == "user":
            mensajes.append(HumanMessage(content=m["mensaje"]))
        else:
            mensajes.append(AIMessage(content=m["mensaje"]))
    return mensajes

# --- 4. ORQUESTADOR LANGCHAIN ---
def chatear_con_inventario(session_id: str, mensaje_usuario: str) -> str:
    try:
        historial = obtener_historial(session_id)
        historial.append(HumanMessage(content=mensaje_usuario))

        respuesta = llm.invoke(historial)

        # Si el modelo decide ejecutar herramientas
        if respuesta.tool_calls:
            historial.append(respuesta)
            for llamada in respuesta.tool_calls:
                fn = mapa_herramientas[llamada["name"]]
                resultado = fn.invoke(llamada["args"])
                historial.append(ToolMessage(content=str(resultado), tool_call_id=llamada["id"]))
            
            respuesta = llm.invoke(historial)

        if isinstance(respuesta.content, list):
            texto_final = "".join(b.get("text", "") for b in respuesta.content if isinstance(b, dict))
        else:
            texto_final = str(respuesta.content)

        guardar_mensaje(session_id, "user", mensaje_usuario)
        guardar_mensaje(session_id, "assistant", texto_final)
        return texto_final

    except Exception as e:
        return f"Error en LangChain: {e}"

if __name__ == "__main__":
    sesion = "tienda_01"
    print("🤖:", chatear_con_inventario(sesion, "¿Cuánto café me queda?"))
    print("🤖:", chatear_con_inventario(sesion, "Vendí 3 frascos de café y llegaron 5 kilos de arroz a 950"))