from typing import List, Literal
from typing import Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()


# Molde individual de cada producto
class MovimientoInventario(BaseModel):
  producto: str = Field(
      description=(
          "Nombre del producto comenzando con mayúscula (ej: 'Puré de papas',"
          " 'Arroz'). Obligatorio."
      )
  )
  tipo_movimiento: Literal["entrada", "salida"] = Field(
      description=(
          "'entrada' si ingresa/compra o 'salida' si se consume/merma/vende."
          " Obligatorio."
      )
  )
  cantidad: float = Field(
      description="Cantidad numérica del movimiento. Obligatorio."
  )
  precio_unitario: Optional[float] = Field(
    default=None,
    description="Precio de compra por unidad. Obligatorio si es 'entrada'. Déjalo vacío (None) si es 'salida'."
)
  unidad: str = Field(
      default="unidades",
      description="Unidad de medida: kilos, litros y/o unidades. Opcional.",
  )


# Contenedor para capturar múltiples productos a la vez
class ListaMovimientos(BaseModel):
  movimientos: List[MovimientoInventario] = Field(
      description="Lista con todos los productos mencionados en el mensaje"
  )


# Modelo y extractor actualizado
modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)

extractor = modelo.with_structured_output(ListaMovimientos)


if __name__ == "__main__":
    mensaje_mixto = "Compramos 4 paquetes de Fideos a 850 pesos cada uno y consumimos 2 litros de Leche"
    
    print("Analizando mensaje mixto...")
    resultado = extractor.invoke(mensaje_mixto)
    
    print("\n--- Ficha Extraída ---")
    for item in resultado.movimientos:
        print(item)