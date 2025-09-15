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

- **CAB1040**: `out\CAB1040_ir.json`

### 📅 Última actualización: 2025-09-15 15:50:59

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

## 📅 Última actualización: 2025-09-15 15:19:20

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

## 📅 Última actualización: 2025-09-15 15:07:59

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

## 📅 Última actualización: 2025-09-15 15:07:31

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

## 📅 Última actualización: 2025-09-15 15:06:33

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

## 📅 Última actualización: 2025-09-15 15:00:20

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

## 📅 Última actualización: 2025-09-15 14:52:33

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

## 📅 Última actualización: 2025-09-15 14:51:29

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

## 📅 Última actualización: 2025-09-15 14:49:34

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

## 📅 Última actualización: 2025-09-15 14:47:46

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

## 📅 Última actualización: 2025-09-15 14:45:46

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

## 📅 Última actualización: 2025-09-15 14:28:14

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

## 📅 Última actualización: 2025-09-15 14:19:46

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

## 📅 Última actualización: 2025-09-15 12:40:32

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

## 📅 Última actualización: 2025-09-15 12:39:12

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

## 📅 Última actualización: 2025-09-15 12:38:35

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

## 📅 Última actualización: 2025-09-15 12:37:21

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

## 📅 Última actualización: 2025-09-15 12:34:18

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

## 📅 Última actualización: 2025-09-15 12:32:42

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

## 📅 Última actualización: 2025-09-15 12:16:47

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

## 📅 Última actualización: 2025-09-15 12:04:32

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

## 📅 Última actualización: 2025-09-15 11:59:52

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

## 📅 Última actualización: 2025-09-15 11:52:35

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

## 📅 Última actualización: 2025-09-15 11:50:50

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

## 📅 Última actualización: 2025-09-15 11:48:43

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

## 📅 Última actualización: 2025-09-15 11:48:16

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

## 📅 Última actualización: 2025-09-15 11:41:53

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

## 📅 Última actualización: 2025-09-13 18:29:30

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

