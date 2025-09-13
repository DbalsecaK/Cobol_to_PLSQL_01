#!/usr/bin/env python3
"""
Convertidor COBOL a PL/SQL mejorado para manejar estructuras complejas
"""
import sys
import os
import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

def parse_cobol_to_ir(file_path: str) -> Dict[str, Any]:
    """Parsear COBOL a IR usando método mejorado"""
    print(f"🔍 Parseando archivo: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return {
            "program": "ERROR",
            "variables": [],
            "procedures": [{"name": "MAIN", "statements": [{"op": "GAP", "raw": f"Error reading file: {e}"}]}]
        }
    
    # Extraer información del programa
    program_match = re.search(r'PROGRAM-ID\.\s*([A-Z0-9_-]+)\.', content, re.IGNORECASE)
    program_name = program_match.group(1).upper() if program_match else "COBOL_PROGRAM"
    
    # Extraer variables
    variables = []
    ws_section = re.search(r'WORKING-STORAGE SECTION(.*?)(?=PROCEDURE DIVISION)', content, re.DOTALL | re.IGNORECASE)
    if ws_section:
        var_matches = re.findall(r'^\s*01\s+([A-Z0-9_-]+)\s+PIC\s+([XS9]\(\d+\))', ws_section.group(1), re.MULTILINE | re.IGNORECASE)
        for name, pic in var_matches:
            name = name.upper()
            pic_u = pic.upper()
            size = int(re.findall(r'\((\d+)\)', pic_u)[0])
            vtype = 'STRING' if pic_u.startswith('X(') else 'NUMERIC'
            variables.append({"name": name, "type": vtype, "size": size})
    
    # Extraer sentencias del PROCEDURE DIVISION
    statements = []
    proc_section = re.search(r'PROCEDURE DIVISION(.*?)(?=STOP RUN\.|$)', content, re.DOTALL | re.IGNORECASE)
    if proc_section:
        statements = extract_statements_improved(proc_section.group(1))
    
    return {
        "program": program_name,
        "variables": variables,
        "procedures": [
            {"name": "MAIN", "statements": statements}
        ]
    }

def extract_statements_improved(proc_text: str) -> List[Dict[str, Any]]:
    """Extraer sentencias de manera mejorada para estructuras complejas"""
    lines = [ln.strip() for ln in proc_text.splitlines() if ln.strip()]
    stmts: List[Dict[str, Any]] = []
    
    i = 0
    while i < len(lines):
        try:
            ln = lines[i]
            
            # Skip empty lines and dots
            if ln.strip() in ['.', '']:
                i += 1
                continue
            
            # Procedure names
            m = re.search(r'^(\d+-\w+(?:-\w+)*)\.?$', ln, re.IGNORECASE)
            if m:
                proc_name = m.group(1)
                stmts.append({"op":"PROCEDURE", "name": proc_name, "raw": ln})
                i += 1
                continue
            
            # IF statement (mejorado para manejar múltiples líneas)
            if re.search(r'^IF\s+', ln, re.IGNORECASE):
                if_result = parse_if_statement(lines, i)
                stmts.append(if_result["statement"])
                i = if_result["next_index"]
                continue
            
            # MOVE statement
            m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?$', ln, re.IGNORECASE)
            if m:
                src = m.group(1).strip()
                dst = m.group(2).strip()
                stmts.append({"op":"MOVE", "src": src, "dst": dst, "raw": ln})
                i += 1
                continue
            
            # DISPLAY statement
            m = re.search(r'^DISPLAY\s+(.+?)\.?$', ln, re.IGNORECASE)
            if m:
                value = m.group(1).strip()
                stmts.append({"op":"DISPLAY", "value": value, "raw": ln})
                i += 1
                continue
            
            # ADD statement
            m = re.search(r'^ADD\s+(.+?)\s+TO\s+(.+?)\.?$', ln, re.IGNORECASE)
            if m:
                src = m.group(1).strip()
                dst = m.group(2).strip()
                stmts.append({"op":"ADD", "src": src, "dst": dst, "raw": ln})
                i += 1
                continue
            
            # ADD with GIVING
            m = re.search(r'^ADD\s+([A-Z0-9_-]+)\s+TO\s+([A-Z0-9_-]+)\s+GIVING\s+([A-Z0-9_-]+)\.', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"ADD_GIVING", "src1": m.group(1).upper(), "src2": m.group(2).upper(), "dst": m.group(3).upper(), "raw": ln})
                i += 1
                continue
            
            # Skip END-IF, ELSE, etc.
            if re.search(r'^(END-IF|ELSE)\.?$', ln, re.IGNORECASE):
                i += 1
                continue
            
            # Unknown statement
            stmts.append({"op":"UNKNOWN", "raw": ln})
            i += 1
            
        except Exception as e:
            print(f"⚠️  Error procesando línea {i+1}: {ln} - Error: {e}")
            stmts.append({"op":"GAP", "raw": ln, "error": str(e)})
            i += 1
    
    return stmts

def parse_if_statement(lines: List[str], start_index: int) -> Dict[str, Any]:
    """Parsear sentencia IF compleja"""
    condition_parts = []
    then_stmts = []
    else_stmts = []
    
    i = start_index
    ln = lines[i]
    
    # Construir condición (puede estar en múltiples líneas)
    condition = ln.replace('IF ', '').replace(' THEN', '').strip()
    
    # Si la línea termina con OR, buscar la siguiente línea
    if condition.upper().endswith('OR'):
        i += 1
        if i < len(lines):
            next_line = lines[i].strip()
            condition += ' ' + next_line
    
    i += 1
    
    # Parsear bloque THEN
    while i < len(lines):
        ln = lines[i].strip()
        
        if re.search(r'^ELSE', ln, re.IGNORECASE):
            break
        if re.search(r'^END-IF', ln, re.IGNORECASE):
            break
        
        # Procesar sentencias dentro del THEN
        if re.search(r'^MOVE\s+', ln, re.IGNORECASE):
            m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?$', ln, re.IGNORECASE)
            if m:
                then_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).strip(), "raw": ln})
        elif re.search(r'^DISPLAY\s+', ln, re.IGNORECASE):
            m = re.search(r'^DISPLAY\s+(.+?)\.?$', ln, re.IGNORECASE)
            if m:
                then_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": ln})
        elif re.search(r'^IF\s+', ln, re.IGNORECASE):
            # IF anidado
            nested_if = parse_if_statement(lines, i)
            then_stmts.append(nested_if["statement"])
            i = nested_if["next_index"]
            continue
        
        i += 1
    
    # Parsear bloque ELSE si existe
    if i < len(lines) and re.search(r'^ELSE', lines[i], re.IGNORECASE):
        i += 1
        while i < len(lines):
            ln = lines[i].strip()
            
            if re.search(r'^END-IF', ln, re.IGNORECASE):
                break
            
            # Procesar sentencias dentro del ELSE
            if re.search(r'^MOVE\s+', ln, re.IGNORECASE):
                m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?$', ln, re.IGNORECASE)
                if m:
                    else_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).strip(), "raw": ln})
            elif re.search(r'^DISPLAY\s+', ln, re.IGNORECASE):
                m = re.search(r'^DISPLAY\s+(.+?)\.?$', ln, re.IGNORECASE)
                if m:
                    else_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": ln})
            elif re.search(r'^IF\s+', ln, re.IGNORECASE):
                # IF anidado
                nested_if = parse_if_statement(lines, i)
                else_stmts.append(nested_if["statement"])
                i = nested_if["next_index"]
                continue
            
            i += 1
    
    # Saltar END-IF
    if i < len(lines) and re.search(r'^END-IF', lines[i], re.IGNORECASE):
        i += 1
    
    return {
        "statement": {
            "op": "IF_ELSE",
            "cond": condition,
            "then": then_stmts,
            "else": else_stmts,
            "raw": f"IF {condition} ... END-IF"
        },
        "next_index": i
    }

def apply_rule(stmt: Dict[str, Any], indent_level: int = 1) -> str:
    """Aplicar regla de conversión mejorada con indentación"""
    op = stmt.get("op", "UNKNOWN")
    base_indent = "    " * indent_level
    
    if op == "MOVE":
        src = stmt.get("src", "")
        dst = stmt.get("dst", "")
        
        # Limpiar expresiones
        src_clean = clean_expression(src)
        dst_clean = clean_expression(dst)
        
        return f"{base_indent}{dst_clean} := {src_clean};"
    
    elif op == "ADD":
        src = stmt.get("src", "")
        dst = stmt.get("dst", "")
        return f"{base_indent}{dst} := {dst} + {src};"
    
    elif op == "ADD_GIVING":
        src1 = stmt.get("src1", "")
        src2 = stmt.get("src2", "")
        dst = stmt.get("dst", "")
        return f"{base_indent}{dst} := {src1} + {src2};"
    
    elif op == "DISPLAY":
        value = stmt.get("value", "")
        value_clean = clean_expression(value)
        return f"{base_indent}DBMS_OUTPUT.PUT_LINE({value_clean});"
    
    elif op == "IF_ELSE":
        cond = stmt.get("cond", "")
        then_stmts = stmt.get("then", [])
        else_stmts = stmt.get("else", [])
        
        # Aplicar reglas con indentación incrementada
        then_code = "\n".join([apply_rule(t, indent_level + 1) for t in then_stmts])
        else_code = "\n".join([apply_rule(t, indent_level + 1) for t in else_stmts])
        
        cond_clean = clean_condition(cond)
        
        if else_stmts:
            return f"{base_indent}IF {cond_clean} THEN\n{then_code}\n{base_indent}ELSE\n{else_code}\n{base_indent}END IF;"
        else:
            return f"{base_indent}IF {cond_clean} THEN\n{then_code}\n{base_indent}END IF;"
    
    elif op == "PROCEDURE":
        proc_name = stmt.get("name", "")
        proc_clean = proc_name.replace('-', '_')
        return f"{base_indent}-- PROCEDURE: {proc_clean}"
    
    elif op == "GAP":
        error_msg = stmt.get("error", "")
        if error_msg:
            return f"{base_indent}-- GAP: {stmt.get('raw', 'Unknown statement')} (Error: {error_msg})"
        else:
            return f"{base_indent}-- GAP: {stmt.get('raw', 'Unknown statement')}"
    
    else:
        return f"{base_indent}-- GAP: {stmt.get('raw', 'Unknown statement')}"

def clean_expression(expr: str) -> str:
    """Limpiar y formatear expresiones COBOL para PL/SQL"""
    if not expr:
        return expr
    
    # Manejar substrings: MSG-IN(9:2) -> SUBSTR(MSG_IN, 9, 2)
    expr = re.sub(r'([A-Z0-9_-]+)\((\d+):(\d+)\)', r'SUBSTR(\1, \2, \3)', expr, flags=re.IGNORECASE)
    
    # Manejar cláusulas OF: NUM-CUENTA OF MSG-IN -> MSG_IN.NUM_CUENTA
    expr = re.sub(r'([A-Z0-9_-]+)\s+OF\s+([A-Z0-9_-]+)', r'\2.\1', expr, flags=re.IGNORECASE)
    
    # Reemplazar guiones con guiones bajos para PL/SQL (múltiples guiones)
    expr = re.sub(r'([A-Z0-9]+)-([A-Z0-9_-]+)', r'\1_\2', expr, flags=re.IGNORECASE)
    # Continuar reemplazando hasta que no queden guiones
    while '-' in expr:
        expr = re.sub(r'([A-Z0-9_]+)-([A-Z0-9_-]+)', r'\1_\2', expr, flags=re.IGNORECASE)
    
    return expr.strip()

def clean_condition(cond: str) -> str:
    """Limpiar y formatear condiciones COBOL para PL/SQL"""
    if not cond:
        return cond
    
    # Reemplazar operadores COBOL con operadores PL/SQL
    cond = re.sub(r'\s+NOT\s+EQUAL\s+', ' != ', cond, flags=re.IGNORECASE)
    cond = re.sub(r'\s+EQUAL\s+', ' = ', cond, flags=re.IGNORECASE)
    cond = re.sub(r'\s+AND\s+', ' AND ', cond, flags=re.IGNORECASE)
    cond = re.sub(r'\s+OR\s+', ' OR ', cond, flags=re.IGNORECASE)
    
    # Limpiar expresiones complejas
    cond = clean_expression(cond)
    
    # Limpiar THEN duplicado
    cond = re.sub(r'\s+THEN\s+THEN\s*$', '', cond, flags=re.IGNORECASE)
    cond = re.sub(r'\s+THEN\s*$', '', cond, flags=re.IGNORECASE)
    
    return cond

def declare_var(name: str, vtype: str, size: int) -> str:
    """Declarar variable en PL/SQL"""
    if vtype == 'STRING':
        return f"  {name} VARCHAR2({size});"
    else:
        return f"  {name} NUMBER({size});"

def generate_package(ir: Dict) -> tuple:
    """Generar paquete PL/SQL"""
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

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python improved_converter.py <archivo.cob>")
        sys.exit(1)

    cob_path = sys.argv[1]
    
    try:
        print(f"🚀 Convertidor COBOL a PL/SQL Mejorado")
        print(f"📁 Archivo: {cob_path}")
        print("=" * 50)
        
        ir = parse_cobol_to_ir(cob_path)
        print(f"📋 Programa: {ir['program']}")
        print(f"📊 Variables: {len(ir['variables'])}")
        print(f"📊 Sentencias: {len(ir['procedures'][0]['statements'])}")
        
        # Guardar IR en archivo JSON
        out_dir = os.path.join(os.path.dirname(__file__), "out")
        os.makedirs(out_dir, exist_ok=True)
        ir_file = os.path.join(out_dir, f"{ir['program']}_improved_ir.json")
        
        with open(ir_file, 'w', encoding='utf-8') as f:
            json.dump(ir, f, indent=2, ensure_ascii=False)
        print(f"💾 IR guardada en: {ir_file}")
        
        print("\n🔄 Generando PL/SQL...")
        plsql, coverage = generate_package(ir)
        
        pkg_path = os.path.join(out_dir, f"{ir['program']}_improved.sql")
        
        with open(pkg_path, "w", encoding="utf-8") as f:
            f.write(plsql)

        rep_path = os.path.join(out_dir, f"{ir['program']}_improved_report.json")
        with open(rep_path, "w", encoding="utf-8") as f:
            json.dump({"program": ir["program"], "coverage": coverage, "method": "IMPROVED"}, f, indent=2)

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
