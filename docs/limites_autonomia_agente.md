# Límites de autonomía: Asistente de Inventario

## Herramientas y nivel de riesgo
- consultar_stock_producto: riesgo bajo (solo lectura; consulta el diccionario INVENTARIO sin modificar datos ni ejecutar acciones externas).
- calcular_valor_venta: riesgo bajo (solo calcula una multiplicación matemática, no modifica el sistema ni mueve recursos).
- descontar_stock_venta: riesgo alto (escritura con impacto económico y operativo; modifica directamente las unidades disponibles en el inventario y requiere aprobación humana).

## Herramientas que requieren aprobación humana
- descontar_stock_venta: Requiere confirmación humana mediante `esperar_aprobacion()` (con límite de 15 segundos) porque altera el stock disponible del negocio y un descuento erróneo descuadra el inventario físico. Las herramientas `consultar_stock_producto` y `calcular_valor_venta` no requieren aprobación porque solo consultan o calculan datos sin modificar registros.

## Revisión de trazas
- Frecuencia: Revisión diaria al cierre de jornada o cada 20 interacciones registradas en `trazas_agente.jsonl`.
- Qué se busca:
  - Llamadas a `descontar_stock_venta` con cantidades anómalas o sin solicitud explícita del usuario.
  - Rechazos o cancelaciones por timeout registradas en `registro_aprobaciones`.
  - Consultas repetidas a productos inexistentes en `consultar_stock_producto`.

## Qué hacer ante un comportamiento inesperado
- 1. Desactivar inmediatamente `descontar_stock_venta` quitándola de la lista `herramientas` en `src/agente_con_memoria.py` para dejar al agente solo en modo lectura.
- 2. Revisar las últimas líneas de `trazas_agente.jsonl` y `registro_aprobaciones` para identificar el `session_id` y los argumentos que causaron el fallo.
- 3. Ajustar el docstring de la herramienta afectada o el esquema `ArgumentosConsultaStock`, y reforzar el prompt `system`.
- 4. Ejecutar pruebas controladas en consola verificando que `esperar_aprobacion()` frene la acción antes de volver a activar la herramienta.