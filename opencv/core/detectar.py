import os
import sys
import cv2
import threading
import requests
import numpy as np
from collections import Counter
from ultralytics import YOLO

_PATH_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PATH_RAIZ not in sys.path:
    sys.path.insert(0, _PATH_RAIZ)

from core.extraer_texto import obtener_patente

PATH_MODELO = os.path.join(_PATH_RAIZ, "entrenamiento", "modelo_yolo.pt")
PATH_COCO = os.path.join(_PATH_RAIZ, "core", "yolov8n.pt")
API_URL = "http://localhost:8000/verificar"
TIMEOUT_API = 2

CONF_YOLO = 0.50
CONF_COCO = 0.45
CONF_OCR_MIN = 0.85
CONF_OCR_CONFIRMAR = 0.90
FRAMES_VENTANA_OCR = 6
MIN_MUESTRAS_OCR = 3
IOU_UMBRAL = 0.3
EMA_ALPHA = 0.6
MAX_FRAMES_SIN_PATENTE = 30
MAX_FRAMES_VEHICULO_MUERTO = 8

COCO_CLASES = {0: "Persona", 2: "Auto", 3: "Moto", 5: "Colectivo", 7: "Camioneta"}
COCO_COLORS = {0: (0, 255, 255), 2: (0, 255, 255), 3: (0, 215, 255), 5: (0, 165, 255), 7: (0, 255, 200)}

modelo_patentes = YOLO(PATH_MODELO)
modelo_coco = YOLO(PATH_COCO)
camara = cv2.VideoCapture(0)

track_patente = None
track_patente_vida = 0
track_vehiculo = None
track_vehiculo_vida = 0

buffer_ocr = []
resultado_api = None
resultado_api_en_curso = False
texto_confirmado = ""
ultima_respuesta_texto = ""
ultimo_label_respuesta = ""
ultimo_color_respuesta = (0, 255, 0)

estado = "buscar"
frames_sin_patente = 0
texto_actual = ""
conf_actual = 0.0


def iou(a, b):
    xi1 = max(a[0], b[0])
    yi1 = max(a[1], b[1])
    xi2 = min(a[2], b[2])
    yi2 = min(a[3], b[3])
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    if inter == 0:
        return 0
    a_area = (a[2] - a[0]) * (a[3] - a[1])
    b_area = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (a_area + b_area - inter)


def ema(old_box, new_box):
    if old_box is None:
        return new_box
    return tuple(
        int(EMA_ALPHA * n + (1 - EMA_ALPHA) * o)
        for n, o in zip(new_box, old_box)
    )


def llamar_api(texto):
    global resultado_api, resultado_api_en_curso
    try:
        r = requests.post(API_URL, json={"patente": texto}, timeout=TIMEOUT_API)
        if r.status_code == 200:
            resultado_api = r.json().get("autorizado", False)
        else:
            resultado_api = -1
    except Exception:
        resultado_api = -1
    finally:
        resultado_api_en_curso = False


def preprocesar_frame(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    img_out = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(img_out, -1, kernel)


while True:
    ok, frame = camara.read()
    if not ok:
        break
    h, w = frame.shape[:2]

    # --- COCO vehiculos ---
    mejor_vehiculo = None
    for r in modelo_coco(frame, imgsz=320, stream=True, verbose=False):
        for box in r.boxes:
            conf = float(box.conf[0])
            if conf >= CONF_COCO:
                cls_id = int(box.cls[0])
                if cls_id in COCO_CLASES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    color = COCO_COLORS[cls_id]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{COCO_CLASES[cls_id]} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    area = (x2 - x1) * (y2 - y1)
                    if not mejor_vehiculo or area > mejor_vehiculo[4]:
                        mejor_vehiculo = (x1, y1, x2, y2, area)

    if mejor_vehiculo:
        nueva_pos = mejor_vehiculo[:4]
        if track_vehiculo and iou(track_vehiculo, nueva_pos) >= IOU_UMBRAL:
            track_vehiculo = ema(track_vehiculo, nueva_pos)
        else:
            track_vehiculo = nueva_pos
        track_vehiculo_vida = 0
    elif track_vehiculo is not None:
        track_vehiculo_vida += 1
        if track_vehiculo_vida >= MAX_FRAMES_VEHICULO_MUERTO:
            track_vehiculo = None

    # --- YOLO patente (frame preprocesado) ---
    frame_pp = preprocesar_frame(frame)
    mejor_patente = None
    best_conf = 0
    for r in modelo_patentes(frame_pp, stream=True, verbose=False):
        for box in r.boxes:
            conf = float(box.conf[0])
            if conf > CONF_YOLO:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                if conf > best_conf:
                    best_conf = conf
                    mejor_patente = (x1, y1, x2, y2)

    if mejor_patente:
        if track_patente and iou(track_patente, mejor_patente) >= IOU_UMBRAL:
            track_patente = ema(track_patente, mejor_patente)
        else:
            track_patente = mejor_patente
        track_patente_vida = 0
    elif track_patente is not None:
        track_patente_vida += 1
        if track_patente_vida >= 8:
            track_patente = None

    # --- OCR ---
    texto_actual = ""
    conf_actual = 0.0
    if track_patente is not None:
        x1, y1, x2, y2 = map(int, track_patente)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        recorte = frame[y1:y2, x1:x2]
        texto_actual, conf_actual = obtener_patente(recorte)

    # --- Maquina de estados ---
    if estado == "buscar":
        frames_sin_patente = 0
        if track_patente is not None and texto_actual and conf_actual >= CONF_OCR_MIN:
            buffer_ocr.append((texto_actual, conf_actual))
            if len(buffer_ocr) > FRAMES_VENTANA_OCR:
                buffer_ocr.pop(0)

            if len(buffer_ocr) >= MIN_MUESTRAS_OCR:
                agrupado = {}
                for t, c in buffer_ocr:
                    agrupado.setdefault(t, []).append(c)

                for t, confs in agrupado.items():
                    avg = float(np.mean(confs))
                    if len(confs) >= MIN_MUESTRAS_OCR and avg >= CONF_OCR_CONFIRMAR:
                        if t != ultima_respuesta_texto:
                            estado = "verificar"
                            texto_confirmado = t
                            resultado_api = None
                            resultado_api_en_curso = True
                            threading.Thread(target=llamar_api, args=(t,), daemon=True).start()
                        break

    elif estado == "verificar":
        if not resultado_api_en_curso and resultado_api is not None:
            if resultado_api == -1:
                estado = "sin_conexion"
                ultima_respuesta_texto = texto_confirmado
                ultimo_label_respuesta = "SIN CONEXION"
                ultimo_color_respuesta = (100, 100, 100)
            elif resultado_api:
                estado = "concedido"
                ultima_respuesta_texto = texto_confirmado
                ultimo_label_respuesta = "ACCESO CONCEDIDO"
                ultimo_color_respuesta = (0, 255, 0)
            else:
                estado = "denegado"
                ultima_respuesta_texto = texto_confirmado
                ultimo_label_respuesta = "NO HABILITADA"
                ultimo_color_respuesta = (0, 0, 255)

    elif estado in ("concedido", "denegado", "sin_conexion"):
        if track_patente is None:
            frames_sin_patente += 1
            if frames_sin_patente >= MAX_FRAMES_SIN_PATENTE:
                estado = "buscar"
                buffer_ocr.clear()
                frames_sin_patente = 0
        elif texto_actual and texto_actual != ultima_respuesta_texto and conf_actual >= CONF_OCR_CONFIRMAR:
            estado = "buscar"
            buffer_ocr.clear()
            frames_sin_patente = 0

    # --- Overlay UI ---
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (480, 110), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

    cv2.putText(frame, "SISTEMA DE ACCESO", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    if estado == "buscar":
        if texto_actual:
            cv2.putText(frame, f"PATENTE: {texto_actual}", (10, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            bar_w = int(conf_actual * 100)
            cv2.rectangle(frame, (10, 65), (10 + bar_w, 72), (0, 255, 0), -1)
            if buffer_ocr:
                mejor = Counter(t for t, _ in buffer_ocr).most_common(1)[0][0]
                cv2.putText(frame, f"Acumulando: {mejor}", (10, 95),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        else:
            cv2.putText(frame, "PATENTE: Buscando...", (10, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    elif estado == "verificar":
        cv2.putText(frame, f"PATENTE: {texto_confirmado}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, "VERIFICANDO...", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    elif estado == "concedido":
        cv2.putText(frame, f"PATENTE: {ultima_respuesta_texto}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, "ACCESO CONCEDIDO", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    elif estado == "denegado":
        cv2.putText(frame, f"PATENTE: {ultima_respuesta_texto}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, "NO HABILITADA", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    elif estado == "sin_conexion":
        cv2.putText(frame, f"PATENTE: {ultima_respuesta_texto}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
        cv2.putText(frame, "SIN CONEXION", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)

    cv2.imshow("Control de Acceso", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

camara.release()
cv2.destroyAllWindows()
