from unittest.mock import MagicMock
from langchain_core.runnables import RunnableLambda
from src.enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_cadena_alerta_segura,
    procesar_mensaje_seguro,
)

def test_cadena_alerta_usa_fallback_ante_fallo_del_modelo():
    # 1. Simulamos que el modelo se quedó sin internet
    def fallar_a_proposito(x):
        raise ConnectionError("simulado")

    cadena_falsa = RunnableLambda(fallar_a_proposito)
    cadena_segura = construir_cadena_alerta_segura(cadena_falsa)

    # 2. Ejecutamos la cadena
    resultado = cadena_segura.invoke({"mensaje": "se rompió una caja"})

    # 3. Comprobamos que respondió el mensaje de salvavidas amigable
    assert "disculpa" in resultado.lower() or "equipo" in resultado.lower()

def test_procesar_mensaje_seguro_no_propaga_excepciones():
    # 1. Simulamos un fallo general en la clasificación inicial
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.side_effect = ConnectionError("simulado")

    cadena_falsa = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa
    )

    # 2. Procesamos el mensaje a través del protector try/except
    resultado = procesar_mensaje_seguro(cadena_falsa, "mensaje de prueba")

    # 3. Comprobamos que entregó un mensaje seguro y no rompió la app
    assert "no pudimos procesar" in resultado.lower() or "problema técnico" in resultado.lower()