import cv2
import os

directorio = "capturas/fotos"
formato = "foto_{:03d}.JPG"
cantidad = 3

imagenes = []
for i in range(cantidad):
    path = os.path.join(directorio, formato.format(i))
    img = cv2.imread(path)
    if img is not None:
        print(f"✓ Imagen cargada: {path} - Tamaño: {img.shape}")
        imagenes.append(img)
    else:
        print(f"✗ Error al cargar: {path}")
        

if len(imagenes) < 2:
    print("No hay suficientes imágenes para hacer el stiching.")
    exit()

stitcher = cv2.Stitcher_create()
status, resultado = stitcher.stitch(imagenes)
if status == cv2.Stitcher_OK:
    cv2.imshow("Resultado del Stiching", resultado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print(f"Error al hacer el stiching: {status}")