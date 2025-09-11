#!/usr/bin/env python3
"""
Convertidor COBOL a PL/SQL mejorado para casos complejos
"""
import sys
import os
import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

def _clean_expression(expr: str) -> str:
    """Limpiar y formatear expresiones COBOL para PL/SQL"""
    if not expr:
        return expr
    
    # Manejar substrings: MSG-IN(9:2) -> SUBSTR(MSG_IN, 9, 2)
    expr = re.sub(r'([A-Z0-9_-]+)\((\d+):(\d+)\)', r'SUBSTR(\1, \2, \3)', expr, flags=re.IGNORECASE)
    
    # Manejar cláusulas OF: NUM-CUENTA OF MSG-IN -> MSG_IN.NUM_CUENTA
    expr = re.sub(r'([A-Z0-9_-]+)\s+OF\s+([A-Z0-9_-]+)', r'\2.\1', expr, flags=re.IGNORECASE)
    
    # Reemplazar guiones con guiones bajos para PL/SQL (múltiples ocurrencias)
    while '-' in expr:
        expr = re.sub(r'([A-Z0-9_]+)-([A-Z0-9_]+)', r'\1_\2', expr, flags=re.IGNORECASE)
    
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
    
    # Limpiar espacios extra y THEN al final
    cond = re.sub(r'\s+THEN\s*$', '', cond, flags=re.IGNORECASE)
    cond = cond.strip()
    
    return cond

def parse_cobol_to_ir_enhanced(file_path: str) -> Dict[str, Any]:
    """Parsear COBOL a IR usando lógica mejorada"""
    print(f"🔍 Parseando con lógica mejorada: {file_path}")
    
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
    
    # Extraer variables (básico)
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
    try:
        proc_section = re.search(r'PROCEDURE DIVISION(.*?)(?=STOP RUN\.|$)', content, re.DOTALL | re.IGNORECASE)
        if not proc_section:
            proc_section = re.search(r'PROCEDURE DIVISION(.*)', content, re.DOTALL | re.IGNORECASE)
        
        statements = []
        if proc_section:
            statements = _extract_statements_enhanced(proc_section.group(1))
        else:
            statements = [{"op": "GAP", "raw": "No PROCEDURE DIVISION found"}]
    except Exception as e:
        print(f"⚠️  Error extrayendo sentencias: {e}")
        statements = [{"op": "GAP", "raw": f"Error extracting statements: {e}"}]
    
    return {
        "program": program_name,
        "variables": variables,
        "procedures": [
            {"name": "MAIN", "statements": statements}
        ]
    }

def _extract_statements_enhanced(proc_text: str) -> List[Dict[str, Any]]:
    """Extraer sentencias con lógica mejorada para casos complejos"""
    lines = [ln.strip() for ln in proc_text.splitlines() if ln.strip()]
    stmts: List[Dict[str, Any]] = []
    
    i = 0
    while i < len(lines):
        try:
            ln = lines[i]
            
            # Skip empty lines and simple dots
            if ln.strip() in ['.', '']:
                i += 1
                continue
            
            # Manejar nombres de procedimientos (ej: 1400-ARMA-REC-T08CT176.)
            m = re.search(r'^(\d+-\w+(?:-\w+)*)\.?$', ln, re.IGNORECASE)
            if m:
                proc_name = m.group(1)
                stmts.append({"op":"PROCEDURE", "name": proc_name, "raw": ln})
                i += 1
                continue
        
            # MOVE statement con cláusulas OF
            m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?$', ln, re.IGNORECASE)
            if m:
                src = m.group(1).strip()
                dst = m.group(2).strip()
                stmts.append({"op":"MOVE", "src": src, "dst": dst, "raw": ln})
                i += 1
                continue
            
            # IF statement (simple o complejo)
            m = re.search(r'^IF\s+(.+?)(?:\s+THEN)?$', ln, re.IGNORECASE)
            if m:
                condition = m.group(1).strip()
                
                # Si la condición termina con OR, buscar la siguiente línea
                if condition.upper().endswith('OR'):
                    i += 1
                    if i < len(lines):
                        next_line = lines[i].strip()
                        condition += ' ' + next_line
                
                then_stmts = []
                else_stmts = []
                i += 1
            
                # Parse THEN block
                while i < len(lines) and not re.search(r'^ELSE', lines[i], re.IGNORECASE) and not re.search(r'^END-IF', lines[i], re.IGNORECASE):
                    then_ln = lines[i]
                    
                    # MOVE statement
                    m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?', then_ln, re.IGNORECASE)
                    if m:
                        then_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).strip(), "raw": then_ln})
                    # DISPLAY statement
                    elif re.search(r'^DISPLAY\s+(.+?)\.?', then_ln, re.IGNORECASE):
                        m = re.search(r'^DISPLAY\s+(.+?)\.?', then_ln, re.IGNORECASE)
                        then_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": then_ln})
                    # IF anidado
                    elif re.search(r'^IF\s+', then_ln, re.IGNORECASE):
                        nested_if = _parse_nested_if(lines, i)
                        then_stmts.append(nested_if["statement"])
                        i = nested_if["next_index"]
                        continue
                    
                    i += 1
            
            # Check for ELSE
            if i < len(lines) and re.search(r'^ELSE', lines[i], re.IGNORECASE):
                i += 1
                # Parse ELSE block
                while i < len(lines) and not re.search(r'^END-IF', lines[i], re.IGNORECASE):
                    else_ln = lines[i]
                    
                    # MOVE statement
                    m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?', else_ln, re.IGNORECASE)
                    if m:
                        else_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).strip(), "raw": else_ln})
                    # DISPLAY statement
                    elif re.search(r'^DISPLAY\s+(.+?)\.?', else_ln, re.IGNORECASE):
                        m = re.search(r'^DISPLAY\s+(.+?)\.?', else_ln, re.IGNORECASE)
                        else_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": else_ln})
                    # IF anidado
                    elif re.search(r'^IF\s+', else_ln, re.IGNORECASE):
                        nested_if = _parse_nested_if(lines, i)
                        else_stmts.append(nested_if["statement"])
                        i = nested_if["next_index"]
                        continue
                    
                    i += 1
            
            # Skip END-IF
            if i < len(lines) and re.search(r'^END-IF', lines[i], re.IGNORECASE):
                i += 1
            
            stmts.append({"op":"IF_ELSE", "cond": condition, "then": then_stmts, "else": else_stmts, "raw": f"IF {condition} ... END-IF"})
            continue
        
        # DISPLAY statement
        m = re.search(r'^DISPLAY\s+(.+?)\.?', ln, re.IGNORECASE)
        if m:
            value = m.group(1).strip()
            stmts.append({"op":"DISPLAY", "value": value, "raw": ln})
            i += 1
            continue
        
            # Skip END-IF huérfanos
            if ln.strip() == 'END-IF' or ln.strip() == 'END-IF.':
                i += 1
                continue
            
            stmts.append({"op":"UNKNOWN", "raw": ln})
            i += 1
            
        except Exception as e:
            # Si hay cualquier error, marcar como GAP y continuar
            print(f"⚠️  Error procesando línea {i+1}: {ln} - Error: {e}")
            stmts.append({"op":"GAP", "raw": ln, "error": str(e)})
            i += 1
    
    return stmts

def _parse_nested_if(lines: List[str], start_index: int) -> Dict[str, Any]:
    """Parsear IF anidado recursivamente"""
    try:
        ln = lines[start_index]
        m = re.search(r'^IF\s+(.+?)(?:\s+THEN)?$', ln, re.IGNORECASE)
        if not m:
            return {"statement": {"op":"GAP", "raw": ln}, "next_index": start_index + 1}
    
    condition = m.group(1).strip()
    then_stmts = []
    else_stmts = []
    i = start_index + 1
    
    # Parse THEN block
    while i < len(lines) and not re.search(r'^ELSE', lines[i], re.IGNORECASE) and not re.search(r'^END-IF', lines[i], re.IGNORECASE):
        then_ln = lines[i]
        
        # MOVE statement
        m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?', then_ln, re.IGNORECASE)
        if m:
            then_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).strip(), "raw": then_ln})
        # DISPLAY statement
        elif re.search(r'^DISPLAY\s+(.+?)\.?', then_ln, re.IGNORECASE):
            m = re.search(r'^DISPLAY\s+(.+?)\.?', then_ln, re.IGNORECASE)
            then_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": then_ln})
        # IF anidado
        elif re.search(r'^IF\s+', then_ln, re.IGNORECASE):
            nested_if = _parse_nested_if(lines, i)
            then_stmts.append(nested_if["statement"])
            i = nested_if["next_index"]
            continue
        
        i += 1
    
    # Check for ELSE
    if i < len(lines) and re.search(r'^ELSE', lines[i], re.IGNORECASE):
        i += 1
        # Parse ELSE block
        while i < len(lines) and not re.search(r'^END-IF', lines[i], re.IGNORECASE):
            else_ln = lines[i]
            
            # MOVE statement
            m = re.search(r'^MOVE\s+(.+?)\s+TO\s+(.+?)\.?', else_ln, re.IGNORECASE)
            if m:
                else_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).strip(), "raw": else_ln})
            # DISPLAY statement
            elif re.search(r'^DISPLAY\s+(.+?)\.?', else_ln, re.IGNORECASE):
                m = re.search(r'^DISPLAY\s+(.+?)\.?', else_ln, re.IGNORECASE)
                else_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": else_ln})
            # IF anidado
            elif re.search(r'^IF\s+', else_ln, re.IGNORECASE):
                nested_if = _parse_nested_if(lines, i)
                else_stmts.append(nested_if["statement"])
                i = nested_if["next_index"]
                continue
            
            i += 1
    
        # Skip END-IF
        if i < len(lines) and re.search(r'^END-IF', lines[i], re.IGNORECASE):
            i += 1
        
        return {
            "statement": {"op":"IF_ELSE", "cond": condition, "then": then_stmts, "else": else_stmts, "raw": f"IF {condition} ... END-IF"},
            "next_index": i
        }
    
    except Exception as e:
        # Si hay error en el parsing del IF anidado, marcar como GAP
        print(f"⚠️  Error en IF anidado línea {start_index+1}: {lines[start_index]} - Error: {e}")
        return {
            "statement": {"op":"GAP", "raw": lines[start_index], "error": str(e)},
            "next_index": start_index + 1
        }

def apply_rule(stmt: Dict[str, Any]) -> str:
    op = stmt.get("op", "UNKNOWN")
    
    if op == "MOVE":
        src = stmt.get("src", "")
        dst = stmt.get("dst", "")
        
        # Limpiar y formatear expresiones complejas
        src_clean = _clean_expression(src)
        dst_clean = _clean_expression(dst)
        
        return f"    {dst_clean} := {src_clean};"
    
    elif op == "DISPLAY":
        value = stmt.get("value", "")
        value_clean = _clean_expression(value)
        return f"    DBMS_OUTPUT.PUT_LINE({value_clean});"
    
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
    
    elif op == "GAP":
        error_msg = stmt.get("error", "")
        if error_msg:
            return f"    -- GAP: {stmt.get('raw', 'Unknown statement')} (Error: {error_msg})"
        else:
            return f"    -- GAP: {stmt.get('raw', 'Unknown statement')}"
    
    else:
        return f"    -- GAP: {stmt.get('raw', 'Unknown statement')}"

def generate_package(ir: Dict) -> tuple:
    program = ir.get("program", "COBOL_PROGRAM")
    vars_decl = []
    for v in ir.get("variables", []):
        if v["type"] == 'STRING':
            vars_decl.append(f"  {v['name']} VARCHAR2({v['size']});")
        else:
            vars_decl.append(f"  {v['name']} NUMBER({v['size']});")

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
    if len(sys.argv) < 2:
        print("Uso: python enhanced_converter.py <archivo.cob>")
        sys.exit(1)

    cob_path = sys.argv[1]
    
    try:
        print(f"🚀 Convertidor COBOL a PL/SQL Mejorado")
        print(f"📁 Archivo: {cob_path}")
        print("=" * 50)
        
        ir = parse_cobol_to_ir_enhanced(cob_path)
        print(f"📋 Programa: {ir['program']}")
        print(f"📊 Variables: {len(ir['variables'])}")
        print(f"📊 Sentencias: {len(ir['procedures'][0]['statements'])}")
        print("🔄 IR generado exitosamente")
        
        # Guardar IR en archivo JSON
        out_dir = os.path.join(os.path.dirname(__file__), "out")
        os.makedirs(out_dir, exist_ok=True)
        ir_file = os.path.join(out_dir, f"{ir['program']}_enhanced_ir.json")
        
        with open(ir_file, 'w', encoding='utf-8') as f:
            json.dump(ir, f, indent=2, ensure_ascii=False)
        print(f"💾 IR guardada en: {ir_file}")
        
        print("\n🔄 Generando PL/SQL...")
        plsql, coverage = generate_package(ir)
        
        pkg_path = os.path.join(out_dir, f"{ir['program']}_enhanced.sql")
        
        with open(pkg_path, "w", encoding="utf-8") as f:
            f.write(plsql)

        rep_path = os.path.join(out_dir, f"{ir['program']}_enhanced_report.json")
        with open(rep_path, "w", encoding="utf-8") as f:
            json.dump({"program": ir["program"], "coverage": coverage, "method": "ENHANCED"}, f, indent=2)

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
