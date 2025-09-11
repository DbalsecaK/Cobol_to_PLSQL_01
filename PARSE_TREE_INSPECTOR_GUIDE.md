# 🌳 Guía: Parse Tree Inspector de ANTLR

## 🎯 **¿Qué es el Parse Tree Inspector?**

El Parse Tree Inspector es una herramienta visual que te permite ver el árbol de parseo que genera ANTLR cuando procesa tu código COBOL. Es muy útil para:

- **Debugging** de la gramática
- **Entender** cómo ANTLR interpreta tu código
- **Visualizar** la estructura jerárquica del código
- **Identificar** problemas de parsing

## 🔧 **Configuración del Parse Tree Inspector**

### **Opción 1: VS Code (Recomendado)**

1. **Instalar Plugin:**
   ```
   Extensions → Buscar "ANTLR4 grammar syntax support"
   → Instalar
   ```

2. **Configurar:**
   - Abre el archivo `Cobol85.g4`
   - Clic derecho en el archivo
   - Selecciona "Test Rule"
   - Selecciona un archivo COBOL (ej: `samples/demo1.cob`)
   - ¡Verás el árbol visualmente!

### **Opción 2: IntelliJ IDEA**

1. **Instalar Plugin:**
   ```
   File → Settings → Plugins
   → Buscar "ANTLR v4 grammar plugin"
   → Instalar
   ```

2. **Usar:**
   - Abre `Cobol85.g4`
   - Clic derecho → "Test Rule"
   - Selecciona archivo COBOL
   - Visualiza el árbol

### **Opción 3: ANTLR4 Web Tool (Online)**

1. **Acceder:**
   - URL: https://www.antlr.org/grammar/
   - Sube tu archivo `Cobol85.g4`
   - Pega código COBOL de prueba
   - Ve el árbol online

### **Opción 4: Script Python (Local)**

```bash
python generate_parse_tree.py
```

## 📁 **Archivos Necesarios**

Para que funcione el Parse Tree Inspector, necesitas:

- ✅ `Cobol85.g4` - Gramática ANTLR
- ✅ `Cobol85Lexer.py` - Lexer generado
- ✅ `Cobol85Parser.py` - Parser generado
- ✅ Archivos COBOL de prueba en `samples/`

## 🎯 **Ejemplo de Uso**

### **1. Archivo COBOL Simple:**
```cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. TEST.

DATA DIVISION.
WORKING-STORAGE SECTION.
01  VAR1    PIC X(10).

PROCEDURE DIVISION.
    MOVE 'HELLO' TO VAR1.
    STOP RUN.
```

### **2. Árbol de Parseo Resultante:**
```
(program (programUnit (identificationDivision (IDENTIFICATION DIVISION .) (programIdParagraph (PROGRAM-ID . TEST .)) (identificationDivisionBody*)) (dataDivision (DATA DIVISION .) (dataDivisionBody (workingStorageSection (WORKING-STORAGE SECTION .) (dataDescriptionEntry (levelNumber 01) (dataName VAR1) (PIC X(10) .))))) (procedureDivision (PROCEDURE DIVISION .) (procedureDivisionBody (statement (moveStatement (MOVE 'HELLO' TO VAR1 .)))) (statement (stopStatement (STOP RUN .))))))
```

## 🔍 **Interpretación del Árbol**

### **Estructura Jerárquica:**
```
program
├── programUnit
│   ├── identificationDivision
│   │   ├── IDENTIFICATION DIVISION
│   │   └── programIdParagraph
│   ├── dataDivision
│   │   └── workingStorageSection
│   └── procedureDivision
│       └── statement
│           ├── moveStatement
│           └── stopStatement
```

### **Nodos Importantes:**
- **`program`** - Raíz del árbol
- **`programUnit`** - Unidad de programa
- **`identificationDivision`** - División de identificación
- **`dataDivision`** - División de datos
- **`procedureDivision`** - División de procedimientos
- **`statement`** - Sentencias individuales

## 🚀 **Beneficios del Parse Tree Inspector**

### **1. Debugging:**
- Ver exactamente cómo ANTLR interpreta tu código
- Identificar errores de parsing
- Entender por qué ciertas sentencias fallan

### **2. Desarrollo de Gramática:**
- Probar nuevas reglas
- Verificar que las reglas funcionan correctamente
- Optimizar la gramática

### **3. Comprensión:**
- Entender la estructura del código COBOL
- Ver la jerarquía de elementos
- Aprender cómo funciona ANTLR

## 🛠️ **Solución de Problemas**

### **Problema: "No veo el árbol visualmente"**

**Soluciones:**
1. **Verificar Plugin:** Asegúrate de tener el plugin ANTLR4 instalado
2. **Regenerar Archivos:** Ejecuta `java -jar antlr-4.13.1-complete.jar Cobol85.g4`
3. **Verificar Archivos:** Asegúrate de que `Cobol85Lexer.py` y `Cobol85Parser.py` existen
4. **Usar Archivo Simple:** Prueba con `samples/demo1.cob` primero

### **Problema: "Error de parsing"**

**Soluciones:**
1. **Verificar Gramática:** Asegúrate de que `Cobol85.g4` es válida
2. **Verificar Código COBOL:** Asegúrate de que el código COBOL es válido
3. **Usar Código Simple:** Prueba con código COBOL básico primero

## 📋 **Comandos Útiles**

### **Regenerar Archivos ANTLR:**
```bash
java -jar C:\antlr\antlr-4.13.1-complete.jar Cobol85.g4
```

### **Generar Árbol de Parseo:**
```bash
python generate_parse_tree.py
```

### **Ver Archivos Generados:**
```bash
dir *.py
```

## 🎉 **Resultado Esperado**

Cuando configures correctamente el Parse Tree Inspector, deberías ver:

1. **Árbol Visual** en tu IDE
2. **Estructura Jerárquica** del código COBOL
3. **Nodos Expandibles** para explorar
4. **Información Detallada** de cada elemento

---

**¡Con el Parse Tree Inspector podrás visualizar exactamente cómo ANTLR interpreta tu código COBOL!** 🌳
