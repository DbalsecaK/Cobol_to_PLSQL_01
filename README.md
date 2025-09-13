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



## 📊 Archivos de Representación Intermedia (IR)

Los siguientes archivos IR han sido generados automáticamente:

- **VALIDACION**: `out\VALIDACION_ir.json`

### 📅 Última actualización: 2025-09-13 18:29:30

### 🔍 Cómo ver la IR:

```bash
# Ver IR en consola
python view_ir.py samples/demo1.cob

# Ver IR y guardarla en archivo JSON
python view_ir.py samples/demo1.cob --save
```

### 📋 Estructura de la IR:

```json
{
  "program": "NOMBRE_PROGRAMA",
  "variables": [
    {
      "name": "VARIABLE",
      "type": "STRING|NUMERIC",
      "size": 20
    }
  ],
  "procedures": [
    {
      "name": "MAIN",
      "statements": [
        {
          "op": "MOVE|ADD|IF_ELSE|DISPLAY",
          "src": "origen",
          "dst": "destino",
          "raw": "sentencia COBOL original"
        }
      ]
    }
  ]
}
```

## 📅 Última actualización: 2025-09-13 18:29:23

### 🔍 Cómo ver la IR:

```bash
# Ver IR en consola
python view_ir.py samples/demo1.cob

# Ver IR y guardarla en archivo JSON
python view_ir.py samples/demo1.cob --save
```

### 📋 Estructura de la IR:

```json
{
  "program": "NOMBRE_PROGRAMA",
  "variables": [
    {
      "name": "VARIABLE",
      "type": "STRING|NUMERIC",
      "size": 20
    }
  ],
  "procedures": [
    {
      "name": "MAIN",
      "statements": [
        {
          "op": "MOVE|ADD|IF_ELSE|DISPLAY",
          "src": "origen",
          "dst": "destino",
          "raw": "sentencia COBOL original"
        }
      ]
    }
  ]
}
```

## 📅 Última actualización: 2025-09-13 18:29:15

### 🔍 Cómo ver la IR:

```bash
# Ver IR en consola
python view_ir.py samples/demo1.cob

# Ver IR y guardarla en archivo JSON
python view_ir.py samples/demo1.cob --save
```

### 📋 Estructura de la IR:

```json
{
  "program": "NOMBRE_PROGRAMA",
  "variables": [
    {
      "name": "VARIABLE",
      "type": "STRING|NUMERIC",
      "size": 20
    }
  ],
  "procedures": [
    {
      "name": "MAIN",
      "statements": [
        {
          "op": "MOVE|ADD|IF_ELSE|DISPLAY",
          "src": "origen",
          "dst": "destino",
          "raw": "sentencia COBOL original"
        }
      ]
    }
  ]
}
```

