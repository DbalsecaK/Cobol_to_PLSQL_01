# COBOL to PL/SQL Migrator

## 📋 Descripción

Programa completo para migrar archivos COBOL a PL/SQL que recibe como parámetro el archivo COBOL a migrar.

## 🚀 Uso

### Sintaxis básica:
```bash
python cobol_to_plsql_migrator.py <archivo_cobol> [opciones]
```

### Ejemplos:

#### 1. Migrar C1040.cob
```bash
python cobol_to_plsql_migrator.py samples/C1040.cob
```

#### 2. Migrar CTB30.CBL especificando directorio de salida
```bash
python cobol_to_plsql_migrator.py samples/CTB30.CBL --output-dir resultados
```

#### 3. Migrar forzando sobrescritura
```bash
python cobol_to_plsql_migrator.py mi_programa.cob --force
```

#### 4. Ver ayuda
```bash
python cobol_to_plsql_migrator.py --help
```

## 📂 Archivos generados

Para cada programa COBOL migrado se generan:

- **`{programa}_ir.json`** - Intermediate Representation
- **`{programa}.sql`** - Código PL/SQL generado
- **`{programa}_migration_report.json`** - Reporte de migración
- **`{programa}_parsing_report.json`** - Reporte de parsing

## 🔧 Opciones disponibles

| Opción | Descripción |
|--------|-------------|
| `--output-dir, -o` | Directorio de salida (default: `out`) |
| `--force, -f` | Sobrescribir archivos sin preguntar |
| `--version, -v` | Mostrar versión |
| `--help, -h` | Mostrar ayuda |

## 📊 Proceso de migración

1. **Validación** - Verifica que el archivo COBOL existe
2. **Parsing** - Convierte COBOL a IR usando `antlr_parser_direct.py`
3. **Conversión** - Convierte IR a PL/SQL usando `ir_to_sql_converter.py`
4. **Reportes** - Genera estadísticas detalladas

## 📈 Reportes

### Reporte de parsing
- Tiempo de procesamiento
- Total de statements
- Elementos UNKNOWN detectados

### Reporte de migración
- Porcentaje de éxito
- GAPs regulares y de macros
- Estadísticas detalladas

## 🎯 Características

- ✅ Acepta cualquier archivo COBOL (.cob, .cbl, .cobol)
- ✅ Genera nombres de archivos automáticamente
- ✅ Validación de entrada y salida
- ✅ Reportes detallados
- ✅ Manejo de errores robusto
- ✅ Confirmación antes de sobrescribir

## 🔍 Ejemplos de uso específicos

### Migrar todos los programas del directorio samples:
```bash
# C1040
python cobol_to_plsql_migrator.py samples/C1040.cob

# CTB30
python cobol_to_plsql_migrator.py samples/CTB30.CBL

# CS63
python cobol_to_plsql_migrator.py samples/CS63.CBL

# CTB0001
python cobol_to_plsql_migrator.py samples/CTB0001.CBL
```

### Migrar con directorio específico:
```bash
python cobol_to_plsql_migrator.py samples/C1040.cob --output-dir migraciones_c1040
```

## ⚠️ Notas importantes

1. El archivo COBOL debe existir y ser accesible
2. Se creará el directorio de salida si no existe
3. El programa validará archivos existentes antes de sobrescribir
4. Los errores se reportan en consola y en archivos de reporte

## 🛠️ Dependencias

- `antlr_parser_direct.py` - Parser COBOL a IR
- `ir_to_sql_converter.py` - Convertidor IR a PL/SQL


