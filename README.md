# COBOL to PL/SQL Converter

Convertidor robusto de código COBOL a PL/SQL usando ANTLR.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python enhanced_converter_v2.py samples/demo1.cob
```

## Características

- Conversión completa de COBOL a PL/SQL
- Manejo robusto de errores
- Generación de IR (JSON)
- Soporte para IF anidados y cláusulas OF

## Estructura

- `enhanced_converter_v2.py` - Convertidor principal
- `antlr_converter.py` - Convertidor ANTLR
- `samples/` - Archivos COBOL de prueba
- `out/` - Archivos generados
