# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Indiesel is a PDF report generator for diesel injector testing, built for Laboratorio Diesel in Mar del Plata, Argentina. It produces professional test reports showing measured values against acceptance tolerances for each injector.

## Commands

### Setup (one-time)
```bash
pip install reportlab pillow
python preparar_recursos.py
```
`preparar_recursos.py` processes raw image assets (`firma_original.png`, `logo_original.png`) into transparent PNGs (`firma.png`, `indiesel_logo_gray.png`) required by the PDF generator.

### Generate a report
```bash
python generar_informe.py
```
Outputs `Indiesel_Informe_<number>.pdf` to the configured output path.

## Architecture

### Two-track PDF generation

**Python backend (`generar_informe.py`)** — primary production tool using ReportLab canvas-based drawing. Produces A4 PDFs with 13mm margins. All text is in Spanish.

**Web frontend (`index.html`, `indiesel_presupuesto.html`, `informe.html`)** — standalone HTML pages using jsPDF for client-side PDF generation. These are independent of the Python backend and not integrated with it.

### generar_informe.py structure

The script has a clearly marked `# DATOS A CAMBIAR` section at the top where report data is configured before each run:
- `inyectores[]` — list of injector dicts with part number, manufacturer, and test results
- `vehiculo`, `fecha`, `n_informe`, `tecnico` — report metadata
- File paths for assets and output

The `generar_pdf()` function handles layout logic:
- 1-column layout for ≤2 injectors, 2-column for more
- Row heights auto-calculated to fill the page
- Sections: header → vehicle info table → injector results grid → observations → footer with signature

### Test result data format

Each injector entry in `inyectores[]`:
```python
{
    "pn": "0445110231",      # Part number
    "fab": "Bosch",          # Manufacturer
    "pruebas": [
        {
            "nombre": "Estanqueidad",
            "val": 0.7,              # Measured value
            "ref": "35.0±35.0",      # Center ± tolerance → range [0.0, 70.0]
            "ok": True               # Manually set pass/fail (not auto-calculated)
        },
        # ...
    ]
}
```

The six test types in order: `Estanqueidad`, `Plena carga`, `Retorno`, `Emisiones`, `Ralenti`, `Pre-inyección`.

### Reference range parsing

`parse_ref(r)` splits `"value±tolerance"` into `(center, tolerance)`. The acceptable range is `[center - tolerance, center + tolerance]`. `bar_pct(val, ref)` maps the measured value onto a 0–100% scale across this range for the visual bar indicator.

The `ok` field is set manually from actual test bench readings — it is not derived from `val` vs `ref`.

### preparar_recursos.py

Two image preprocessing functions:
- `preparar_firma()` — white-background BMP/PNG → transparent PNG using RGB threshold (dark pixels kept)
- `preparar_logo()` — teal-on-gray logo → grayscale transparent PNG using channel-difference detection (teal: `G > R + 50` and `B` high)
