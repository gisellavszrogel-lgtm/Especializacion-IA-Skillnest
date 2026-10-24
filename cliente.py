import time
from typing import Callable, Any

from src.consumir_gemini import armar_peticion, extraer_texto, enviar_peticion

def con_reintento(
    función: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,        
) -> Any:
    for intento in range(intentos):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos-1
                raise
            print(f'Intento{intento+1} de {intentos} falló por límites de uso/servidor. Reintentando...')
            time.sleep(espera_segundos)


#cómo ejecuto esto?