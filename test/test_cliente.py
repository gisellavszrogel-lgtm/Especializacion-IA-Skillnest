from pathlib import Path
import sys

# Agrega la raíz del proyecto para que encuentre la carpeta 'src'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from unittest.mock import Mock, patch
import pytest

from src import cliente
from src.cliente import con_reintento, consultar_modelo, registrar_costo
from src.consumir_gemini import enviar_peticion


# Limpia antes de cada prueba para que no se contaminen entre sí
@pytest.fixture(autouse=True)
def reiniciar_costo():
  cliente.costo_total_sesion = 0.0
  yield


# 1. Credencial inválida (401 / 400)
def test_enviar_peticion_credencial_invalida():
  respuesta_falsa = Mock(status_code=401)
  with patch("src.cliente.requests.post", return_value=respuesta_falsa):
    with pytest.raises(ValueError):
      enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})


# 2. Reintento: si falla por timeout
def test_con_reintento_espera_entre_intentos():
  intentos = {"conteo": 0}

  def accion():
    intentos["conteo"] += 1
    if intentos["conteo"] == 1:
      raise TimeoutError("simulado")
    return "exito"

  with patch("src.cliente.time.sleep"):
    resultado = con_reintento(accion, intentos=3)

  assert resultado == "exito"
  assert intentos["conteo"] == 2


# 3. Reintento: agota las oportunidades
def test_con_reintento_falla_despues_de_maximos():

  def siempre_falla():
    raise TimeoutError("Servidor saturado")

  with patch("src.cliente.time.sleep"):
    with pytest.raises(TimeoutError):
      con_reintento(siempre_falla, intentos=3)


# 4. Contador: calcula y acumula tokens
def test_registrar_costo_acumula_correctamente():
  respuesta_falsa = {"usageMetadata": {"totalTokenCount": 1000}}
  costo = registrar_costo(respuesta_falsa)

  assert costo == cliente.COSTO_POR_1000_TOKENS
  assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS


# 5. Contador: si la respuesta viene vacía o falla, no altera el acumulador
def test_registrar_costo_no_registra_en_error():
  respuesta_invalida = {}
  costo = registrar_costo(respuesta_invalida)

  assert costo == 0.0
  assert cliente.costo_total_sesion == 0.0


# 6. Flujo exitoso
def test_enviar_peticion_limite_de_uso():
  payload_falso = {
      "candidates": [{"content": {"parts": [{"text": "Respuesta simulada"}]}}],
      "usageMetadata": {"totalTokenCount": 500},
  }

  with patch("src.cliente.con_reintento", return_value=payload_falso):
    texto = consultar_modelo("Hola mundo")

  assert texto == "Respuesta simulada"
  assert cliente.costo_total_sesion > 0


# 7. Red falló por completo y se agotaron los reintentos
def test_consultar_modelo_propaga_error_final():
  with patch("src.cliente.con_reintento", side_effect=TimeoutError("Agotado")):
    with pytest.raises(RuntimeError):
      consultar_modelo("Hola mundo")


if __name__ == "__main__":
  pytest.main([__file__, "-v"])