from database import supabase
from catalogo import generar_embedding

def buscar_producto(consulta: str, umbral: float = 0.50):
    """Busca el producto más parecido usando vectores en Supabase."""
    vector_busqueda = generar_embedding(consulta)
    
    respuesta = supabase.rpc(
        "buscar_producto_similar",
        {
            "query_embedding": vector_busqueda,
            "match_threshold": umbral,
            "match_count": 1
        }
    ).execute()
    
    if respuesta.data:
        return respuesta.data[0]
    return None

def registrar_movimiento(consulta_producto: str, tipo: str, cantidad: float, precio: float = None):
    """Encuentra el producto, anota el movimiento y actualiza el stock."""
    try:
        # 1. Identificamos el producto en el catálogo
        producto = buscar_producto(consulta_producto)
        if not producto:
            print(f"No encontré ningún producto parecido a '{consulta_producto}'.")
            return None

        producto_id = producto["id"]
        nombre = producto["nombre_oficial"]
        stock_viejo = float(producto["stock_actual"])

        # 2. Calculamos el nuevo stock
        if tipo == "entrada":
            nuevo_stock = stock_viejo + cantidad
        elif tipo == "salida":
            nuevo_stock = stock_viejo - cantidad
        else:
            print("Tipo inválido. Usa 'entrada' o 'salida'.")
            return None

        # 3. Guardamos el movimiento en la libreta (Tabla 2)
        supabase.table("movimientos_inventario").insert({
            "producto_id": producto_id,
            "tipo_movimiento": tipo,
            "cantidad": cantidad,
            "precio_unitario": precio
        }).execute()

        # 4. Actualizamos el saldo en el catálogo (Tabla 1)
        supabase.table("catalogo_productos").update({
            "stock_actual": nuevo_stock
        }).eq("id", producto_id).execute()

        print(f"{tipo.upper()}: {cantidad} {producto['unidad_estandar']} de '{nombre}' (Similitud: {producto['similitud']:.2f})")
        print(f"   Stock actualizado: {stock_viejo} -> {nuevo_stock}")
        return True

    except Exception as e:
        print(f"Error al registrar movimiento: {e}")
        return None

if __name__ == "__main__":
    # Probamos con palabras naturales (distintas al nombre oficial)
    registrar_movimiento("tarro de café", "salida", 2)
    registrar_movimiento("bolsa de arroz", "entrada", 10, precio=950)