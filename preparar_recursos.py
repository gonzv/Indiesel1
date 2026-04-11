"""
preparar_recursos.py
--------------------
Corre este script UNA SOLA VEZ para preparar los archivos de firma y logo
que usa generar_informe.py.

Requiere:
  - firma_original.png   : foto de la firma en paint (fondo blanco, trazo negro)
  - logo_original.png    : logo de Indiesel (fondo gris, trazo teal/verde)

Genera:
  - firma.png            : firma con fondo transparente
  - indiesel_logo_gray.png : logo en gris con fondo transparente
"""

from PIL import Image
import numpy as np


def preparar_firma(ruta_entrada, ruta_salida):
    """
    Recibe una imagen de firma con fondo blanco y trazo oscuro.
    Genera PNG con fondo transparente.
    """
    img = Image.open(ruta_entrada).convert("RGBA")
    data = np.array(img)

    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # Píxeles oscuros = firma
    is_signature = (r < 100) & (g < 100) & (b < 100)

    new_data = np.zeros_like(data)
    new_data[is_signature] = [30, 30, 30, 255]   # negro
    new_data[~is_signature] = [0, 0, 0, 0]        # transparente

    # Recorte ajustado automáticamente
    alpha = new_data[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    pad = 15
    rmin = max(0, rmin - pad)
    rmax = min(new_data.shape[0] - 1, rmax + pad)
    cmin = max(0, cmin - pad)
    cmax = min(new_data.shape[1] - 1, cmax + pad)
    tight = new_data[rmin:rmax, cmin:cmax]

    result = Image.fromarray(tight, "RGBA")
    result.save(ruta_salida)
    print(f"Firma guardada: {ruta_salida}  ({result.size})")
    # Proporción usada en el PDF: height/width = 255/671
    print(f"  Proporción real: {result.height}/{result.width} = {result.height/result.width:.4f}")


def preparar_logo(ruta_entrada, ruta_salida):
    """
    Recibe el logo de Indiesel con fondo gris y trazo teal.
    Convierte el trazo teal a gris y hace el fondo transparente.
    """
    img = Image.open(ruta_entrada).convert("RGBA")
    data = np.array(img)

    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # Teal: G y B altos, G > R por bastante margen
    is_teal = (g > 150) & (b > 150) & (g.astype(int) > r.astype(int) + 50)

    new_data = np.zeros_like(data)
    new_data[is_teal] = [120, 120, 120, 255]   # gris
    new_data[~is_teal] = [0, 0, 0, 0]           # transparente

    result = Image.fromarray(new_data.astype(np.uint8), "RGBA")
    result.save(ruta_salida)
    print(f"Logo guardado: {ruta_salida}  ({result.size})")


if __name__ == "__main__":
    preparar_firma(
        ruta_entrada="firma_original.png",
        ruta_salida="firma.png"
    )
    preparar_logo(
        ruta_entrada="logo_original.png",
        ruta_salida="indiesel_logo_gray.png"
    )
