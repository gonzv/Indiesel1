from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

W, H = A4
M = 13 * mm

# ============================================================
# SCRIPT: generar_informe.py
# Indiesel - Laboratorio Diesel, Mar del Plata
# Técnico Responsable: Gonzalo De Pilato
# ============================================================

# ============================================================
# INSTRUCCIONES DE USO:
# 1. Completar los datos en la sección "DATOS A CAMBIAR"
# 2. Ejecutar: python3 generar_informe.py
# 3. El PDF se genera en /mnt/user-data/outputs/
#
# PRUEBAS DISPONIBLES (nombre sugerido → escalon banco):
#   Estanqueidad → LEAK
#   Plena carga  → VL
#   Retorno      → VL(R)
#   Emisiones    → EM
#   Ralenti      → LL
#   Pre-inyeccion→ VE
#   (VE(R) y VE2 no se incluyen en el informe)
#
# FORMATO ref: "valor_central+-tolerancia"  ej: "62.2+-4.2"
# El campo 'ok' es MANUAL: True = tilde, False = X
# ============================================================


def parse_ref(r):
    if "+-" in r:
        cv, t = r.split("+-")
        return float(cv) - float(t), float(cv) + float(t)
    return None, None


def ref_display(r):
    return r.replace("+-", "\u00b1")


def bar_pct(val, ref):
    mn, mx = parse_ref(ref)
    if mn is None or mx == mn:
        return 0.5
    rng = mx - mn
    margin = rng * 0.30
    total = rng + 2 * margin
    return max(0.01, min(0.99, (val - (mn - margin)) / total))


def draw_bar(c, x, y, w, h, pct, ref_str):
    mn, mx = parse_ref(ref_str)
    if mn is not None and mx != mn:
        rng = mx - mn
        margin = rng * 0.30
        total = rng + 2 * margin
        zone_start = margin / total
        zone_end = (margin + rng) / total
    else:
        zone_start, zone_end = 0.25, 0.75
    c.setFillColor(colors.HexColor("#F0F0F0"))
    c.setStrokeColor(colors.HexColor("#BBBBBB"))
    c.setLineWidth(0.4)
    c.rect(x, y, w, h, fill=1, stroke=1)
    zx = x + zone_start * w
    zw = (zone_end - zone_start) * w
    c.setFillColor(colors.HexColor("#CECECE"))
    c.rect(zx, y, zw, h, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#555555"))
    c.setLineWidth(0.7)
    c.line(zx, y - 1.5, zx, y + h + 1.5)
    c.line(zx + zw, y - 1.5, zx + zw, y + h + 1.5)
    c.setStrokeColor(colors.black)
    c.setLineWidth(2.0)
    c.line(x + pct * w, y - 2.5, x + pct * w, y + h + 2.5)


def generar_pdf(inyectores, vehiculo, fecha, n_informe, tecnico,
                ruta_firma, ruta_logo, ruta_salida):

    c = canvas.Canvas(ruta_salida, pagesize=A4)

    # --- ENCABEZADO ---
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.black)
    c.drawCentredString(W / 2, H - 44, "INDIESEL")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawCentredString(W / 2, H - 57, "Laboratorio Diesel")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(W / 2, H - 73, "INFORME DE PRUEBA DE INYECTORES")
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.6)
    c.line(M, H - 80, W - M, H - 80)

    # --- TABLA DE INFO ---
    y = H - 96
    row_h = 15
    info_rows = [("Fecha:", fecha), ("Vehiculo:", vehiculo), ("N\u00b0 Informe:", n_informe)]
    label_col = 72
    val_col = 165
    table_w = label_col + val_col
    table_x = (W - table_w) / 2
    for i, (label, val) in enumerate(info_rows):
        if i % 2 == 0:
            c.setFillColor(colors.HexColor("#F8F8F8"))
            c.rect(table_x - 6, y - 4, table_w + 12, row_h, fill=1, stroke=0)
        c.setFont("Helvetica", 9.5)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(table_x, y, label)
        c.setFillColor(colors.black)
        c.drawString(table_x + label_col, y, val)
        c.setStrokeColor(colors.HexColor("#DDDDDD"))
        c.setLineWidth(0.3)
        c.line(table_x - 6, y - 4, table_x + table_w + 6, y - 4)
        y -= row_h
    c.setLineWidth(0.6)
    c.setStrokeColor(colors.black)
    c.line(M, y - 2, W - M, y - 2)
    y -= 15

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(M, y, "RESULTADOS DE PRUEBA")
    y -= 14

    # --- GRILLA DE INYECTORES ---
    FOOTER_H = 90
    available = y - FOOTER_H
    n = len(inyectores)
    cols = 2 if n > 1 else 1
    gap = 12
    col_w = (W - M * 2 - gap * (cols - 1)) / cols
    col_x = [M + i * (col_w + gap) for i in range(cols)]
    TITLE_H = 12; PN_H = 18; BADGE_H = 15; SUBHDR_H = 9; BLOCK_PAD = 8
    n_per_col = -(-n // cols)
    fixed_h = n_per_col * (TITLE_H + PN_H + BADGE_H + SUBHDR_H + BLOCK_PAD)
    rows_total = n_per_col * len(inyectores[0]["pruebas"])
    row_h_dyn = max(13, min(19, (available - fixed_h) / max(rows_total, 1)))
    BAR_H = max(5, row_h_dyn * 0.40)
    NAME_W = col_w * 0.27; VAL_W = col_w * 0.11; REF_W = col_w * 0.22
    SYM_W = col_w * 0.09; BAR_W = col_w - NAME_W - VAL_W - REF_W - SYM_W - 2
    col_y = [y] * cols

    for idx, inj in enumerate(inyectores):
        col = idx % cols
        cx = col_x[col]
        cy = col_y[col]
        ok_all = all(p["ok"] for p in inj["pruebas"])
        if col_y[col] < y - 2:
            cy -= 4
            c.setStrokeColor(colors.HexColor("#CCCCCC"))
            c.setLineWidth(0.4)
            c.line(cx, cy + 2, cx + col_w, cy + 2)
            cy -= 4
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(cx, cy, f"INYECTOR {idx + 1}")
        cy -= TITLE_H
        c.setFont("Helvetica", 8.5)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(cx, cy, f"Nro de inyector: {inj['pn']}   Fabricante: {inj['fab']}")
        cy -= PN_H
        c.setLineWidth(0.6)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.HexColor("#E8E8E8") if ok_all else colors.HexColor("#CCCCCC"))
        c.rect(cx, cy - 3, col_w, 13, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(colors.black)
        c.drawCentredString(cx + col_w / 2, cy + 1.5, "APROBADO" if ok_all else "REQUIERE REPARACION")
        cy -= BADGE_H
        bar_x = cx + NAME_W + VAL_W + REF_W
        sym_x = cx + col_w
        c.setFont("Helvetica", 5.5)
        c.setFillColor(colors.HexColor("#AAAAAA"))
        c.drawString(cx, cy, "PRUEBA")
        c.drawString(cx + NAME_W, cy, "VALOR")
        c.drawString(cx + NAME_W + VAL_W, cy, "REFERENCIA")
        c.drawString(bar_x, cy, "RANGO")
        cy -= SUBHDR_H
        for p in inj["pruebas"]:
            row_y = cy
            c.setFont("Helvetica", 7.5)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawString(cx, row_y, p["nombre"])
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.black)
            c.drawString(cx + NAME_W, row_y, str(p["val"]))
            c.setFont("Helvetica", 6.5)
            c.setFillColor(colors.HexColor("#777777"))
            c.drawString(cx + NAME_W + VAL_W, row_y, ref_display(p["ref"]))
            pct = bar_pct(p["val"], p["ref"])
            bar_y = row_y - BAR_H + 1.5
            draw_bar(c, bar_x, bar_y, BAR_W, BAR_H, pct, p["ref"])
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.black)
            c.drawRightString(sym_x, bar_y + BAR_H / 2 - 3.5, "OK" if p["ok"] else "X")
            cy -= row_h_dyn
        col_y[col] = cy - BLOCK_PAD
        if col == cols - 1:
            min_y = min(col_y)
            col_y = [min_y] * cols

    # --- OBSERVACION ---
    y = min(col_y) - 4
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.black)
    c.line(M, y, W - M, y)
    y -= 14
    fallidas = [i + 1 for i, inj in enumerate(inyectores) if not all(p["ok"] for p in inj["pruebas"])]
    if not fallidas:
        obs = "Todos los inyectores aprobaron las pruebas. Se encuentran dentro de los parametros de fabrica."
    else:
        nums = ", ".join(str(x) for x in fallidas)
        plural = len(fallidas) > 1
        obs = (f"Inyector{'es' if plural else ''} {nums}: "
               f"resultado{'s' if plural else ''} fuera de rango. "
               f"Requier{'en' if plural else 'e'} reparacion.")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(M, y, "OBSERVACION")
    y -= 12
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#333333"))
    words = obs.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if c.stringWidth(test, "Helvetica", 9) < (W - M * 2):
            line = test
        else:
            c.drawString(M, y, line)
            y -= 12
            line = word
    if line:
        c.drawString(M, y, line)

    # --- FIRMA ---
    firma_w = 25 * mm
    firma_h = firma_w * (255 / 671)
    firma_x = M
    firma_y = 52
    c.drawImage(ruta_firma, firma_x, firma_y, width=firma_w, height=firma_h, mask="auto")
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.black)
    c.line(firma_x, firma_y - 3, firma_x + firma_w, firma_y - 3)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.black)
    c.drawString(firma_x, firma_y - 11, tecnico)
    c.drawString(firma_x, firma_y - 19, "Tecnico Responsable")

    # --- LOGO ---
    logo_pts = 28 * mm
    c.drawImage(ruta_logo, W / 2 - logo_pts / 2, 38, width=logo_pts, height=logo_pts, mask="auto")
    c.setLineWidth(0.4)
    c.setStrokeColor(colors.HexColor("#AAAAAA"))
    c.line(M, 32, W - M, 32)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.black)
    c.drawCentredString(W / 2, 22, "WhatsApp: 2233059372  |  Tel: 223 478-9900")
    c.drawCentredString(W / 2, 13, "Mar del Plata, Argentina")

    c.save()
    print(f"PDF generado: {ruta_salida}")


# ============================================================
# ===== DATOS A CAMBIAR POR INFORME =====
# ============================================================

inyectores = [
    {
        "pn": "0445110231", "fab": "Bosch",
        "pruebas": [
            {"nombre": "Estanqueidad",  "val": 0.7,  "ref": "35.0+-35.0", "ok": True},
            {"nombre": "Plena carga",   "val": 55.6, "ref": "62.2+-4.2",  "ok": True},
            {"nombre": "Retorno",       "val": 13.9, "ref": "30.0+-25.0", "ok": True},
            {"nombre": "Emisiones",     "val": 16.2, "ref": "17.2+-3.0",  "ok": True},
            {"nombre": "Ralenti",       "val": 4.1,  "ref": "4.4+-2.0",   "ok": True},
            {"nombre": "Pre-inyeccion", "val": 0.6,  "ref": "1.7+-1.3",   "ok": True},
        ]
    },
    # Agregar más inyectores aquí con el mismo formato...
]

vehiculo  = "Chevrolet S10 2.8 MWM"
fecha     = "10/04/2026 - 14:59 hs"
n_informe = "0002"
tecnico   = "Gonzalo De Pilato"

# Rutas de archivos de recursos
ruta_firma  = "/home/claude/firma.png"       # firma con fondo transparente
ruta_logo   = "/home/claude/indiesel_logo_gray.png"  # logo gris con fondo transparente
ruta_salida = f"/mnt/user-data/outputs/Indiesel_Informe_{n_informe}.pdf"

# ============================================================

generar_pdf(inyectores, vehiculo, fecha, n_informe, tecnico,
            ruta_firma, ruta_logo, ruta_salida)
