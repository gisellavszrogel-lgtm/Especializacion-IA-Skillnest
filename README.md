# Integración Backend con Inteligencia Artificial - Gate 1
### Por Gisella Velásquez Rogel

Pipeline en Python para la ingesta, normalización y extracción estructurada de catálogos de e-commerce mediante Google Gemini API (`gemini-3.6-flash`), aplicando validación determinista de esquemas JSON para su integración con Shopify Admin API.

---

### Requisitos del Sistema

* **Python 3.10** o superior.
* Clave de API activa de Google Gemini (`GEMINI_API_KEY`).
* Git configurado en tu equipo.

---

### Guía de Instalación Paso a Paso

#### 1. Clonar el repositorio
Abre tu terminal y clona este proyecto:
```bash
git clone https://github.com/gisellavszrogel-lgtm/Especializacion-IA-Skillnest
cd plantilla-repositorio-base
```

#### 2. Crear y activar el entorno virtual
* En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
* En macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno
Copia la plantilla base y completa tu clave de API:
* En Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```
* En macOS / Linux:
```bash
cp .env.example .env
```

Contenido requerido dentro de `.env`:
```env
GEMINI_API_KEY=tu_api_key_aqui
```

---

### Instrucciones de Ejecución

#### 1. Consumo funcional de la API
Ejecuta la llamada base modular para procesar una solicitud de producto, medir latencia y calcular costo:
```bash
python src/consumir_gemini.py
```
* **Salida esperada:** Registro de latencia en consola, costo estimado en USD y el objeto JSON normalizado según el esquema.

#### 2. Suite de consistencia de prompts
Ejecuta la batería de pruebas automatizadas sobre el banco de prompts (evaluación por triplicado):
```bash
python src/prompts/test_consistencia.py
```
* **Salida esperada:** 12 casos evaluados exitosamente (12/12 válidas) y actualización del reporte en `src/prompts/registro_resultados.json`.

---

### Estructura del Repositorio

* `src/` : Código fuente del pipeline y script de consumo modular (`consumir_gemini.py`).
* `src/prompts/` : Banco de prompts (`banco.py`), runner de consistencia (`test_consistencia.py`) y registro de métricas (`registro_resultados.json`).
* `docs/` : Documentación técnica y justificación de selección de modelo (`decision_arquitectura.md`).
* `requirements.txt` : Lista de dependencias del entorno de desarrollo.
* `.env.example` : Plantilla de variables de entorno requeridas.