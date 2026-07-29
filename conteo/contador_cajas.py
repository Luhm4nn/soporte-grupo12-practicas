import cv2
import numpy as np

VIDEO_PATH = "video.mp4"

# Color marrón en HSV
# Subimos luminosidad mínima para tonos marrones más claritos (cartón claro)
LOWER = np.array([8, 15, 60])
UPPER = np.array([30, 180, 255])

MIN_AREA = 4000
MAX_AREA = 60000

cap = cv2.VideoCapture(VIDEO_PATH)

trackers = {}   # id -> {bbox, perdido, contada}
next_id = 0
total = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER, UPPER)
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=2)

    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detecciones = []
    
    # Línea vertical a 1/2 (un tercio) desde la izquierda
    limite_x = frame.shape[1] // 2 

    for c in contornos:
        if MIN_AREA < cv2.contourArea(c) < MAX_AREA:
            x, y, w, h = cv2.boundingRect(c)
            # Solo tomar detecciones cuyo centro esté a la derecha del primer tercio (los 2/3 derechos)
            if x + (w // 2) > limite_x:
                detecciones.append((x, y, w, h))

    def iou(a, b):
        ax1, ay1, ax2, ay2 = a[0], a[1], a[0]+a[2], a[1]+a[3]
        bx1, by1, bx2, by2 = b[0], b[1], b[0]+b[2], b[1]+b[3]
        ix = max(0, min(ax2,bx2) - max(ax1,bx1))
        iy = max(0, min(ay2,by2) - max(ay1,by1))
        inter = ix * iy
        union = a[2]*a[3] + b[2]*b[3] - inter
        return inter / union if union else 0

    usados_trackers = set()
    usados_dets     = set()
    pares = []  # (iou, tid, det_idx)

    for tid, data in trackers.items():
        for i, det in enumerate(detecciones):
            v = iou(data['bbox'], det)
            if v > 0.25:
                pares.append((v, tid, i))

    pares.sort(reverse=True)

    nuevos = {}
    for _, tid, i in pares:
        if tid in usados_trackers or i in usados_dets:
            continue
        nuevos[tid] = trackers[tid]
        nuevos[tid]['bbox']    = detecciones[i]
        nuevos[tid]['perdido'] = 0
        usados_trackers.add(tid)
        usados_dets.add(i)

    # Detecciones sin match → nueva caja
    for i, det in enumerate(detecciones):
        if i not in usados_dets:
            nuevos[next_id] = {'bbox': det, 'perdido': 0, 'contada': False}
            next_id += 1

    # Trackers sin match → perdido; si lleva mucho tiempo, eliminar
    for tid, data in trackers.items():
        if tid not in nuevos:
            data['perdido'] += 1
            if data['perdido'] < 10:
                nuevos[tid] = data

    trackers = nuevos

    for tid, data in trackers.items():
        if not data['contada'] and data['perdido'] == 0:
            data['contada'] = True
            total += 1

    display = frame.copy()
    
    cv2.line(display, (limite_x, 0), (limite_x, display.shape[0]), (255, 0, 0), 2)

    for tid, data in trackers.items():
        if data['perdido'] > 0:
            continue
        x, y, w, h = data['bbox']
        cx, cy = x + w//2, y + h//2
        cv2.rectangle(display, (x, y), (x+w, y+h), (0, 220, 80), 2)
        cv2.circle(display,   (cx, cy), 5, (0, 220, 80), -1)
        cv2.putText(display, f"ID {tid}", (x, y-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 80), 1, cv2.LINE_AA)

    cv2.putText(display, f"Cajas: {total}", (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 80), 3, cv2.LINE_AA)

    cv2.imshow("Contador", display)
    cv2.imshow("Mascara",  mask)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Total cajas detectadas: {total}")