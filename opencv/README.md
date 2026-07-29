# Control de Acceso por Patentes

Sistema de reconocimiento de patentes vehiculares en tiempo real que funciona en tres etapas: primero detecta vehículos con YOLOv8n, y cuando un auto se acerca lo suficiente, detecta y recorta la patente. Posteriormente se extrae su texto mediante OCR especializado. Finalmente verifica el acceso contra una API REST.

Para probarlo rápidamente, ejecutá el detector con el video de prueba `video-prueba` — ahí se puede ver cómo se detectan los autos y, a medida que el auto blanco se acerca, el sistema logra detectar la patente y extraer su texto correctamente, mandando la petición http correspondiente y dando acceso.

## Tecnologías

- **YOLOv8n** — fine-tuneado para detección de patentes en imágenes de cámara. Entrenado con un dataset de más de 5000 imágenes anotadas con bounding boxes de patentes.

- **fast-plate-ocr** — OCR de código abierto entrenado exclusivamente con patentes vehículares. Reemplaza a EasyOCR y PaddleOCR, que al ser OCRs de propósito general generaban más errores en la inferencia de caracteres alfanuméricos de patentes. Este modelo especializado mejora notablemente la precisión.

- **FastAPI** — API REST para verificar si una patente está autorizada contra una base de datos SQLite.

- **OpenCV** — captura de video en vivo desde la cámara, dibujo de bounding boxes y overlays de estado en tiempo real.

- **PyTorch** — backend del modelo YOLO y del OCR.

## Estructura

```
api/            API REST con FastAPI y SQLite
core/           Lógica principal: detección YOLO, OCR y flujo de video
entrenamiento/  Scripts y dataset para fine-tuning de YOLOv8n (datasets excluidos del repo para ahorrar el peso de cargar imagenes a GitHub)
```

## Cómo usar

1. **Activar el entorno virtual** e instalar dependencias:
   ```powershell
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Iniciar la API REST** (en una terminal aparte, con el entorno activado):
   ```powershell
   uvicorn api.api:app --host 0.0.0.0 --port 8000
   ```

3. **Crear la base de datos** con patentes autorizadas (en otra terminal, con el entorno activado):
   ```powershell
   python api/crear_bd.py
   ```

4. **Ejecutar el detector** (en otra terminal, con el entorno activado):
   ```powershell
   python run.py
   ```
