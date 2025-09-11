#!/usr/bin/env python3
"""
Convertidor COBOL a PL/SQL usando ANTLR completo
"""
import sys
import os
import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

# Imports de ANTLR
from antlr4 import FileStream, CommonTokenStream
from Cobol85Lexer import Cobol85Lexer
from Cobol85Parser import Cobol85Parser

# ===== IR VISITOR =====
class IRBuildingVisitor:
    def __init__(self, token_stream, full_text: str):
        self.ts = token_stream
        self.text = full_text
        self.program_name: str = "COBOL_PROGRAM"
        self.variables: List[Dict[str, Any]] = []
        self.statements: List[Dict[str, Any]] = []

    def build_ir(self, entry) -> Dict[str, Any]:
        self.program_name = self._find_program_id(entry) or self.program_name
        self.variables = self._extract_variables(entry)
        self.statements = self._extract_statements(entry)
        return {
            "program": self.program_name,
            "variables": self.variables,
            "procedures": [
                {"name": "MAIN", "statements": self.statements}
            ]
        }

    def _find_program_id(self, entry) -> Optional[str]:
        m = re.search(r'PROGRAM-ID\.\s*([A-Z0-9_-]+)\.', self.text, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        return None

    def _extract_section_text(self, start_marker: str, end_marker: Optional[str]=None) -> str:
        s = re.search(start_marker, self.text, flags=re.IGNORECASE)
        if not s:
            return ""
        if end_marker:
            e = re.search(end_marker, self.text, flags=re.IGNORECASE)
            if e and e.start() > s.end():
                return self.text[s.end():e.start()]
            return self.text[s.end():]
        return self.text[s.end():]

    def _extract_variables(self, entry) -> List[Dict[str, Any]]:
        ws_text = self._extract_section_text(r'WORKING-STORAGE SECTION', r'PROCEDURE DIVISION')
        vars_found: List[Dict[str, Any]] = []
        for name, pic in re.findall(r'^\s*01\s+([A-Z0-9_-]+)\s+PIC\s+([XS9]\(\d+\))', ws_text, flags=re.MULTILINE | re.IGNORECASE):
            name = name.upper()
            pic_u = pic.upper()
            size = int(re.findall(r'\((\d+)\)', pic_u)[0])
            vtype = 'STRING' if pic_u.startswith('X(') else 'NUMERIC'
            vars_found.append({"name": name, "type": vtype, "size": size})
        return vars_found

    def _extract_statements(self, entry) -> List[Dict[str, Any]]:
        proc_text = self._extract_section_text(r'PROCEDURE DIVISION', r'STOP RUN\.')
        if not proc_text:
            proc_text = self._extract_section_text(r'PROCEDURE DIVISION')
        lines = [ln.strip() for ln in proc_text.splitlines() if ln.strip()]
        stmts: List[Dict[str, Any]] = []

        i = 0
        while i < len(lines):
            ln = lines[i]
            
            # Combinar líneas continuas de MOVE
            if ln.startswith('MOVE') and not ln.endswith('.'):
                # Buscar la línea TO correspondiente
                j = i + 1
                while j < len(lines) and not lines[j].startswith(('MOVE', 'ADD', 'IF', 'DISPLAY', 'ELSE', 'END-IF')):
                    if lines[j].startswith('TO'):
                        ln = ln + ' ' + lines[j]
                        break
                    j += 1
            
            # MOVE statement (mejorado para manejar substrings y OF)
            m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?$', ln, re.IGNORECASE)
            if m:
                src = m.group(1).strip()
                dst = m.group(2).strip()
                stmts.append({"op":"MOVE", "src": src, "dst": dst, "raw": ln})
                i += 1
                continue

            # ADD with GIVING
            m = re.search(r'^ADD\s+([A-Z0-9_-]+)\s+TO\s+([A-Z0-9_-]+)\s+GIVING\s+([A-Z0-9_-]+)\.', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"ADD_GIVING", "src1": m.group(1).upper(), "src2": m.group(2).upper(), "dst": m.group(3).upper(), "raw": ln})
                i += 1
                continue

            # ADD simple
            m = re.search(r'^ADD\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"ADD", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": ln})
                i += 1
                continue

            # IF-ELSE-END-IF block (solo si no termina con punto)
            m = re.search(r'^IF\s+(.+?)(?:\s+THEN)?$', ln, re.IGNORECASE)
            if m and not ln.strip().endswith('.'):
                condition = m.group(1).strip()
                then_stmts = []
                else_stmts = []
                in_else = False
                i += 1
                
                # Parse THEN block
                while i < len(lines) and not re.search(r'^ELSE', lines[i], re.IGNORECASE) and not re.search(r'^END-IF', lines[i], re.IGNORECASE):
                    then_ln = lines[i]
                    # MOVE statement
                    m = re.search(r'^MOVE\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.?', then_ln, re.IGNORECASE)
                    if m:
                        then_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": then_ln})
                    # DISPLAY statement
                    elif re.search(r'^DISPLAY\s+(.+?)\.?', then_ln, re.IGNORECASE):
                        m = re.search(r'^DISPLAY\s+(.+?)\.?', then_ln, re.IGNORECASE)
                        then_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": then_ln})
                    i += 1
                
                # Check for ELSE
                if i < len(lines) and re.search(r'^ELSE', lines[i], re.IGNORECASE):
                    i += 1
                    # Parse ELSE block
                    while i < len(lines) and not re.search(r'^END-IF', lines[i], re.IGNORECASE):
                        else_ln = lines[i]
                        # MOVE statement
                        m = re.search(r'^MOVE\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.?', else_ln, re.IGNORECASE)
                        if m:
                            else_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": else_ln})
                        # DISPLAY statement
                        elif re.search(r'^DISPLAY\s+(.+?)\.?', else_ln, re.IGNORECASE):
                            m = re.search(r'^DISPLAY\s+(.+?)\.?', else_ln, re.IGNORECASE)
                            else_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": else_ln})
                        i += 1
                
                # Skip END-IF
                if i < len(lines) and re.search(r'^END-IF', lines[i], re.IGNORECASE):
                    i += 1
                
                stmts.append({"op":"IF_ELSE", "cond": condition, "then": then_stmts, "else": else_stmts, "raw": f"IF {condition} ... END-IF"})
                continue

            # Simple IF statement (legacy) - IF condition DISPLAY value.
            m = re.search(r'^IF\s+(.+?)\s+DISPLAY\s+(.+?)\.', ln, re.IGNORECASE)
            if m:
                condition = m.group(1).strip()
                value = m.group(2).strip()
                stmts.append({"op":"IF", "cond": condition, "then":[{"op":"DISPLAY","value": value}], "raw": ln})
                i += 1
                continue

            # DISPLAY statement
            m = re.search(r'^DISPLAY\s+(.+?)\.', ln, re.IGNORECASE)
            if m:
                value = m.group(1).strip()
                # Check if it's a variable or literal
                if re.match(r'^[A-Z0-9_-]+$', value, re.IGNORECASE):
                    stmts.append({"op":"DISPLAY_VAR", "variable": value.upper(), "raw": ln})
                else:
                    stmts.append({"op":"DISPLAY", "value": value, "raw": ln})
                i += 1
                continue

            # Manejar comentarios COBOL (***)
            if ln.startswith('***'):
                stmts.append({"op":"COMMENT", "text": ln, "raw": ln})
                i += 1
                continue

            # Manejar nombres de procedimientos (ej: 1400-ARMA-REC-T08CT176.)
            m = re.search(r'^(\d+-\w+(?:-\w+)*)\.?$', ln, re.IGNORECASE)
            if m:
                proc_name = m.group(1)
                stmts.append({"op":"PROCEDURE", "name": proc_name, "raw": ln})
                i += 1
                continue

            # Manejar PERFORM statement
            m = re.search(r'^PERFORM\s+(.+?)\.?$', ln, re.IGNORECASE)
            if m:
                perform_target = m.group(1).strip()
                stmts.append({"op":"PERFORM", "target": perform_target, "raw": ln})
                i += 1
                continue

            # Manejar EXEC SQL (básico)
            if ln.strip().startswith('EXEC SQL'):
                sql_content = []
                sql_content.append(ln)
                i += 1
                # Recopilar líneas hasta END-EXEC
                while i < len(lines) and not lines[i].strip().startswith('END-EXEC'):
                    sql_content.append(lines[i])
                    i += 1
                if i < len(lines):
                    sql_content.append(lines[i])  # END-EXEC
                stmts.append({"op":"EXEC_SQL", "content": sql_content, "raw": '\n'.join(sql_content)})
                i += 1
                continue

            # Manejar ELSE huérfano
            if ln.strip() == 'ELSE' or ln.strip() == 'ELSE.':
                stmts.append({"op":"ELSE", "raw": ln})
                i += 1
                continue

            # Manejar EXIT statement
            if ln.strip() == 'EXIT' or ln.strip() == 'EXIT.':
                stmts.append({"op":"EXIT", "raw": ln})
                i += 1
                continue

            # Manejar CONTINUE statement
            if ln.strip() == 'CONTINUE' or ln.strip() == 'CONTINUE.':
                stmts.append({"op":"CONTINUE", "raw": ln})
                i += 1
                continue

            # Manejar END-IF huérfanos
            if ln.strip() == 'END-IF' or ln.strip() == 'END-IF.':
                stmts.append({"op":"END_IF", "raw": ln})
                i += 1
                continue

            # Skip simple dots, empty lines, or lines that start with TO (part of MOVE)
            if ln.strip() in ['.', ''] or ln.startswith('TO'):
                i += 1
                continue
                
            stmts.append({"op":"UNKNOWN", "raw": ln})
            i += 1
        return stmts

# ===== RULES ENGINE =====
def declare_var(name: str, vtype: str, size: int) -> str:
    if vtype == 'STRING':
        return f"  {name} VARCHAR2({size});"
    else:
        return f"  {name} NUMBER({size});"

def _clean_expression(expr: str) -> str:
    """Limpiar y formatear expresiones COBOL para PL/SQL"""
    if not expr:
        return expr
    
    # Manejar substrings: MSG-IN(9:2) -> SUBSTR(MSG_IN, 9, 2)
    expr = re.sub(r'([A-Z0-9_-]+)\((\d+):(\d+)\)', r'SUBSTR(\1, \2, \3)', expr, flags=re.IGNORECASE)
    
    # Manejar cláusulas OF: NUM-CUENTA OF MSG-IN -> MSG_IN.NUM_CUENTA
    expr = re.sub(r'([A-Z0-9_-]+)\s+OF\s+([A-Z0-9_-]+)', r'\2.\1', expr, flags=re.IGNORECASE)
    
    # Reemplazar guiones con guiones bajos para PL/SQL
    expr = re.sub(r'([A-Z0-9]+)-([A-Z0-9]+)', r'\1_\2', expr, flags=re.IGNORECASE)
    
    # Limpiar espacios extra
    expr = expr.strip()
    
    return expr

def _clean_condition(cond: str) -> str:
    """Limpiar y formatear condiciones COBOL para PL/SQL"""
    if not cond:
        return cond
    
    # Reemplazar operadores COBOL con operadores PL/SQL
    cond = re.sub(r'\s+NOT\s+EQUAL\s+', ' != ', cond, flags=re.IGNORECASE)
    cond = re.sub(r'\s+EQUAL\s+', ' = ', cond, flags=re.IGNORECASE)
    cond = re.sub(r'\s+AND\s+', ' AND ', cond, flags=re.IGNORECASE)
    cond = re.sub(r'\s+OR\s+', ' OR ', cond, flags=re.IGNORECASE)
    
    # Limpiar expresiones complejas
    cond = _clean_expression(cond)
    
    return cond

def apply_rule(stmt: Dict[str, Any]) -> str:
    op = stmt.get("op", "UNKNOWN")
    
    if op == "MOVE":
        src = stmt.get("src", "")
        dst = stmt.get("dst", "")
        
        # Limpiar y formatear expresiones complejas
        src_clean = _clean_expression(src)
        dst_clean = _clean_expression(dst)
        
        return f"    {dst_clean} := {src_clean};"
    
    elif op == "ADD":
        src = stmt.get("src", "")
        dst = stmt.get("dst", "")
        return f"    {dst} := {dst} + {src};"
    
    elif op == "ADD_GIVING":
        src1 = stmt.get("src1", "")
        src2 = stmt.get("src2", "")
        dst = stmt.get("dst", "")
        return f"    {dst} := {src1} + {src2};"
    
    elif op == "DISPLAY":
        value = stmt.get("value", "")
        return f"    DBMS_OUTPUT.PUT_LINE({value});"
    
    elif op == "DISPLAY_VAR":
        variable = stmt.get("variable", "")
        return f"    DBMS_OUTPUT.PUT_LINE({variable});"
    
    elif op == "IF":
        cond = stmt.get("cond", "")
        then_stmts = stmt.get("then", [])
        then_code = "\n".join([apply_rule(t) for t in then_stmts])
        
        # Limpiar condición
        cond_clean = _clean_condition(cond)
        
        return f"    IF {cond_clean} THEN\n{then_code}\n    END IF;"
    
    elif op == "IF_ELSE":
        cond = stmt.get("cond", "")
        then_stmts = stmt.get("then", [])
        else_stmts = stmt.get("else", [])
        then_code = "\n".join([apply_rule(t) for t in then_stmts])
        else_code = "\n".join([apply_rule(t) for t in else_stmts])
        
        # Limpiar condición
        cond_clean = _clean_condition(cond)
        
        return f"    IF {cond_clean} THEN\n{then_code}\n    ELSE\n{else_code}\n    END IF;"
    
    elif op == "PROCEDURE":
        proc_name = stmt.get("name", "")
        proc_clean = proc_name.replace('-', '_')
        return f"    -- PROCEDURE: {proc_clean}"
    
    elif op == "COMMENT":
        comment_text = stmt.get("text", "")
        return f"    -- {comment_text}"
    
    elif op == "END_IF":
        return f"    END IF;"
    
    elif op == "CONTINUE":
        return f"    NULL; -- CONTINUE"
    
    elif op == "PERFORM":
        target = stmt.get("target", "")
        target_clean = target.replace('-', '_')
        return f"    {target_clean}(); -- PERFORM"
    
    elif op == "EXIT":
        return f"    RETURN; -- EXIT"
    
    elif op == "EXEC_SQL":
        content = stmt.get("content", [])
        sql_lines = []
        for line in content:
            if line.strip().startswith('EXEC SQL'):
                sql_lines.append("    -- EXEC SQL")
            elif line.strip().startswith('END-EXEC'):
                sql_lines.append("    -- END-EXEC")
            else:
                sql_lines.append(f"    -- {line.strip()}")
        return '\n'.join(sql_lines)
    
    else:
        return f"    -- GAP: {stmt.get('raw', 'Unknown statement')}"

# ===== PACKAGE GENERATOR =====
def generate_package(ir: Dict) -> tuple:
    program = ir.get("program", "COBOL_PROGRAM")
    vars_decl = [declare_var(v["name"], v["type"], v["size"]) for v in ir.get("variables", [])]

    coverage = {"rules":0, "gaps":0}
    lines: List[str] = []
    for proc in ir.get("procedures", []):
        for s in proc.get("statements", []):
            out = apply_rule(s)
            if out.startswith("    -- GAP"):
                coverage["gaps"] += 1
            else:
                coverage["rules"] += 1
            lines.append(out)

    vars_decl_str = '\n'.join(vars_decl)
    lines_str = '\n'.join(lines)
    
    body = f"""CREATE OR REPLACE PACKAGE BODY {program} IS
  PROCEDURE MAIN IS
{vars_decl_str}
  BEGIN
{lines_str}
  END MAIN;
END {program};
/"""
    return body, coverage

# ===== MAIN FUNCTION =====
def parse_cobol_to_ir(file_path: str):
    """Función para parsear COBOL a IR usando ANTLR"""
    print(f"🔍 Parseando con ANTLR: {file_path}")
    
    input_stream = FileStream(file_path, encoding='utf-8')
    lexer = Cobol85Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Cobol85Parser(stream)
    
    # Parsear usando la gramática
    tree = parser.startRule()
    print("✅ Parsing ANTLR exitoso!")
    
    visitor = IRBuildingVisitor(token_stream=stream, full_text=input_stream.strdata)
    return visitor.build_ir(tree)


def save_ir_to_file(ir: Dict[str, Any], output_file: str):
    """Función para guardar la IR en un archivo JSON"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ir, f, indent=2, ensure_ascii=False)
    print(f"💾 IR guardada en: {output_file}")

def update_readme_with_ir_info(ir_files: List[str]):
    """Actualizar el README con información de los archivos IR generados"""
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        return
    
    # Leer el README actual
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Generar sección de archivos IR
    ir_section = f"""
## 📊 Archivos de Representación Intermedia (IR)

Los siguientes archivos IR han sido generados automáticamente:

"""
    
    for ir_file in ir_files:
        if os.path.exists(ir_file):
            program_name = os.path.basename(ir_file).replace('_ir.json', '')
            ir_section += f"- **{program_name}**: `{ir_file}`\n"
    
    ir_section += f"""
### 📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 🔍 Cómo ver la IR:

```bash
# Ver IR en consola
python view_ir.py samples/demo1.cob

# Ver IR y guardarla en archivo JSON
python view_ir.py samples/demo1.cob --save
```

### 📋 Estructura de la IR:

```json
{{
  "program": "NOMBRE_PROGRAMA",
  "variables": [
    {{
      "name": "VARIABLE",
      "type": "STRING|NUMERIC",
      "size": 20
    }}
  ],
  "procedures": [
    {{
      "name": "MAIN",
      "statements": [
        {{
          "op": "MOVE|ADD|IF_ELSE|DISPLAY",
          "src": "origen",
          "dst": "destino",
          "raw": "sentencia COBOL original"
        }}
      ]
    }}
  ]
}}
```

"""
    
    # Buscar si ya existe una sección de IR y reemplazarla
    if "## 📊 Archivos de Representación Intermedia (IR)" in readme_content:
        # Reemplazar sección existente
        start_marker = "## 📊 Archivos de Representación Intermedia (IR)"
        end_marker = "## "
        start_idx = readme_content.find(start_marker)
        if start_idx != -1:
            end_idx = readme_content.find(end_marker, start_idx + len(start_marker))
            if end_idx != -1:
                readme_content = readme_content[:start_idx] + ir_section + readme_content[end_idx:]
            else:
                readme_content = readme_content[:start_idx] + ir_section
    else:
        # Agregar nueva sección al final
        readme_content += ir_section
    
    # Escribir el README actualizado
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📝 README actualizado con información de archivos IR")

def main():
    if len(sys.argv) < 2:
        print("Uso: python antlr_converter.py <archivo.cob>")
        sys.exit(1)

    cob_path = sys.argv[1]
    
    try:
        print(f"🚀 Convertidor COBOL a PL/SQL con ANTLR")
        print(f"📁 Archivo: {cob_path}")
        print("=" * 50)
        
        ir = parse_cobol_to_ir(cob_path)
        print(f"📋 Programa: {ir['program']}")
        print(f"📊 Variables: {len(ir['variables'])}")
        print(f"📊 Sentencias: {len(ir['procedures'][0]['statements'])}")
        
        # Guardar IR en archivo JSON
        out_dir = os.path.join(os.path.dirname(__file__), "out")
        os.makedirs(out_dir, exist_ok=True)
        ir_file = os.path.join(out_dir, f"{ir['program']}_ir.json")
        save_ir_to_file(ir, ir_file)
        
        print("\n🔄 Generando PL/SQL...")
        plsql, coverage = generate_package(ir)
        
        pkg_path = os.path.join(out_dir, f"{ir['program']}_antlr.sql")
        
        with open(pkg_path, "w", encoding="utf-8") as f:
            f.write(plsql)

        rep_path = os.path.join(out_dir, f"{ir['program']}_antlr_report.json")
        with open(rep_path, "w", encoding="utf-8") as f:
            json.dump({"program": ir["program"], "coverage": coverage, "method": "ANTLR"}, f, indent=2)

        # Actualizar README con información de IR
        update_readme_with_ir_info([ir_file])

        print("✅ Archivos generados:")
        print(f"   📊 IR: {ir_file}")
        print(f"   📄 PL/SQL: {pkg_path}")
        print(f"   📊 Reporte: {rep_path}")
        print(f"📈 Cobertura: {coverage['rules']} reglas, {coverage['gaps']} gaps")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
