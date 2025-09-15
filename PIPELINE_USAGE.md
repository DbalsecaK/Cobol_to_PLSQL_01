# 🔄 Pipeline de Conversión COBOL → PL/SQL

## 📖 Descripción General

El proceso de conversión se ha dividido en **dos programas independientes** para mayor flexibilidad y control:

1. **`antlr_parser.py`** - Convierte COBOL a Intermediate Representation (IR)
2. **`ir_to_plsql.py`** - Convierte IR a código PL/SQL

## 🚀 Uso del Pipeline

### **Paso 1: Parsing COBOL → IR**

```bash
python antlr_parser.py samples/C1040.cob
```

**Salidas generadas:**
- `out/C1040_ir.json` - Archivo IR con estructura completa
- `out/C1040_parsing_report.json` - Reporte detallado del parsing

### **Paso 2: Conversión IR → PL/SQL**

```bash
python ir_to_plsql.py out/C1040_ir.json
```

**Salidas generadas:**
- `out/C1040_generated.sql` - Código PL/SQL generado
- `out/C1040_conversion_report.json` - Reporte de conversión

## 📊 Ventajas de la Separación

### ✅ **Beneficios del Pipeline Dividido**

1. **🔧 Depuración independiente** - Cada fase se puede analizar por separado
2. **⚡ Reutilización de IR** - No necesitas re-parsear si solo cambias la generación
3. **🎯 Desarrollo incremental** - Puedes mejorar cada parte independientemente
4. **📈 Análisis granular** - Reportes específicos para cada fase
5. **🔄 Múltiples salidas** - Un IR puede generar diferentes targets (PL/SQL, Java, etc.)

### 📁 **Estructura de Archivos Generados**

```
out/
├── C1040_ir.json                    # IR completo
├── C1040_parsing_report.json        # Análisis del parsing
├── C1040_generated.sql              # PL/SQL generado
└── C1040_conversion_report.json     # Análisis de conversión
```

## 🔍 Análisis de Archivos

### **1. Archivo IR (`_ir.json`)**
```json
{
  "program_name": "CAB1040",
  "variables": [...],
  "procedures": [{
    "name": "MAIN-PROCEDURE",
    "statements": [...]
  }],
  "metadata": {
    "source_lines": 1847,
    "parse_method": "antlr_optimized",
    "total_statements": 689,
    "total_variables": 23
  }
}
```

### **2. Reporte de Parsing (`_parsing_report.json`)**
```json
{
  "parsing_summary": {
    "success_rate": 99.5,
    "unknown_statements": 3
  },
  "statement_analysis": {
    "most_common": [
      ["MOVE", 156],
      ["DISPLAY", 89],
      ["IF", 45]
    ]
  },
  "performance_metrics": {
    "parsing_time": 2.34,
    "lines_per_second": 788.5
  }
}
```

### **3. Código PL/SQL (`_generated.sql`)**
```sql
CREATE OR REPLACE PACKAGE CAB1040 AS
    -- Variables globales
    T30DOR10 VARCHAR2(100);
    
    PROCEDURE main_procedure;
END CAB1040;
/

CREATE OR REPLACE PACKAGE BODY CAB1040 AS
    PROCEDURE main_procedure IS
    BEGIN
        -- Statements convertidos
        VAR1 := 'VALUE';
        DBMS_OUTPUT.PUT_LINE('Hello World');
        -- ...
    END main_procedure;
END CAB1040;
/
```

## ⚡ Comandos Útiles

### **Procesamiento Completo en Una Línea**
```bash
# Parsing + Conversión automática
python antlr_parser.py samples/C1040.cob && python ir_to_plsql.py out/C1040_ir.json
```

### **Solo Análisis (sin generar PL/SQL)**
```bash
# Solo parsing para analizar estructura
python antlr_parser.py samples/C1040.cob
```

### **Conversión de IR Existente**
```bash
# Usar IR previamente generado
python ir_to_plsql.py out/C1040_ir.json
```

### **Batch Processing de Múltiples Archivos**
```bash
# Procesar múltiples archivos COBOL
for file in samples/*.cob; do
    echo "Procesando $file"
    python antlr_parser.py "$file"
done

# Convertir todos los IR generados
for ir in out/*_ir.json; do
    echo "Convirtiendo $ir"
    python ir_to_plsql.py "$ir"
done
```

## 📈 Métricas de Rendimiento

### **Parser ANTLR (`antlr_parser.py`)**
- **Velocidad típica**: 3-8 líneas/segundo
- **Tiempo promedio**: 2-4 minutos para C1040.cob
- **Caché**: Reutiliza parsing si el archivo no cambió

### **Generador PL/SQL (`ir_to_plsql.py`)**
- **Velocidad típica**: 1000+ statements/segundo  
- **Tiempo promedio**: < 1 segundo para archivos típicos
- **Instantáneo**: Una vez que tienes el IR

## 🔧 Resolución de Problemas

### **Error: "No se encuentra el archivo"**
```bash
# Verificar que el archivo existe
ls -la samples/C1040.cob

# Usar ruta absoluta si es necesario
python antlr_parser.py /ruta/completa/archivo.cob
```

### **Error: "IR file not found"**
```bash
# Verificar que el parsing se completó
ls -la out/*_ir.json

# Usar nombre exacto del archivo IR
python ir_to_plsql.py out/C1040_ir.json
```

### **Bajo rendimiento en parsing**
```bash
# El caché mejora significativamente el rendimiento en ejecuciones repetidas
# Primera ejecución: ~3 minutos
# Ejecuciones posteriores (sin cambios): ~10 segundos
```

## 🎯 Casos de Uso Específicos

### **1. Desarrollo Iterativo**
```bash
# 1. Parse una vez
python antlr_parser.py samples/C1040.cob

# 2. Mejora reglas de conversión
# 3. Re-convierte rápidamente
python ir_to_plsql.py out/C1040_ir.json

# 4. Repite paso 2-3 hasta estar satisfecho
```

### **2. Análisis de Cobertura**
```bash
# Analizar qué statements no se reconocen
python antlr_parser.py samples/C1040.cob
cat out/C1040_parsing_report.json | grep "unknown_statements"
```

### **3. Comparación de Métodos**
```bash
# Comparar con el converter unificado original
python antlr_converter.py samples/C1040.cob

# Comparar con el pipeline separado
python antlr_parser.py samples/C1040.cob
python ir_to_plsql.py out/C1040_ir.json

# Los resultados deben ser equivalentes
```

## 📚 Archivos de Utilidades

- **`conversion_utils.py`** - Funciones comunes compartidas
- **`antlr_converter.py`** - Versión original unificada (referencia)
- **`ultra_fast_converter.py`** - Versión experimental sin ANTLR

## 🎊 Próximos Pasos

1. **Ejecutar pipeline completo** con C1040.cob
2. **Analizar reportes** para identificar áreas de mejora
3. **Iterar en reglas** de conversión usando solo `ir_to_plsql.py`
4. **Expandir a múltiples archivos** una vez validado el proceso
