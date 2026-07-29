import re
import numpy as np
from fast_plate_ocr import LicensePlateRecognizer

PATRONES_VALIDOS = [
    r'^[A-Z]{3}\d{3}$',
    r'^[A-Z]{2}\d{3}[A-Z]{2}$'
]

_recognizer = None


def _get_recognizer():
    global _recognizer
    if _recognizer is None:
        _recognizer = LicensePlateRecognizer('cct-xs-v2-global-model')
    return _recognizer


def corregir_caracteres(texto):
    mapa_a_numero = {'O': '0', 'Q': '0', 'B': '8', 'Z': '7', 'I': '1', 'S': '5', 'G': '6'}
    mapa_a_letra = {'0': 'O', '8': 'B', '7': 'Z', '1': 'I', '5': 'S', '6': 'G'}

    lista = list(texto)
    if len(texto) == 6:
        for i in range(3):
            if lista[i] in mapa_a_letra: lista[i] = mapa_a_letra[lista[i]]
        for i in range(3, 6):
            if lista[i] in mapa_a_numero: lista[i] = mapa_a_numero[lista[i]]
    elif len(texto) == 7:
        for i in range(2):
            if lista[i] in mapa_a_letra: lista[i] = mapa_a_letra[lista[i]]
        for i in range(2, 5):
            if lista[i] in mapa_a_numero: lista[i] = mapa_a_numero[lista[i]]
        for i in range(5, 7):
            if lista[i] in mapa_a_letra: lista[i] = mapa_a_letra[lista[i]]

    return "".join(lista)


def obtener_patente(imagen_recorte):
    if imagen_recorte is None or imagen_recorte.size == 0:
        return None, 0.0

    m = _get_recognizer()
    preds = m.run(imagen_recorte, return_confidence=True)
    if not preds:
        return None, 0.0

    texto = preds[0].plate.upper()
    conf = float(np.mean(preds[0].char_probs)) if preds[0].char_probs is not None else 0.0

    if any(re.match(p, texto) for p in PATRONES_VALIDOS):
        return texto, conf

    texto_corregido = corregir_caracteres(texto)
    if any(re.match(p, texto_corregido) for p in PATRONES_VALIDOS):
        return texto_corregido, conf * 0.95

    return None, 0.0
