import sys
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage
from src.cadena_tres_pasos import cadena_tres_pasos


def test_cadena_tres_pasos():
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="puré de papas: 0\ngelatina sabor frambuesa: 2\npolvo de hornear: 0"),
        AIMessage(content="[URGENTE] Puré de papas\n[BAJO] gelatina sabor frambuesa (2)\n[URGENTE] Polvo de Hornear"),
        AIMessage(content="- [URGENTE] Puré de papas\n- [BAJO] Gelatina sabor frambuesa (2)\n- [URGENTE] Polvo de Hornear"),
    ]

    # Limpiamos la memoria previa del módulo si ya se había importado
    sys.modules.pop("src.cadena_tres_pasos", None)

    # Interceptamos la creación de ChatGoogleGenerativeAI para entregar el mock
    with patch("langchain_google_genai.ChatGoogleGenerativeAI", return_value=modelo_falso):
        
        resultado = cadena_tres_pasos.invoke({"dictado": "prueba de audio"})

    assert modelo_falso.call_count == 3
    assert "[URGENTE]" in resultado