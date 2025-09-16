#!/usr/bin/env python3
"""
Conversor simple de IR a SQL - Versión directa y eficiente
Genera PL/SQL válido desde IR completo
"""

import sys
import os
import json
import re
from datetime import datetime

def clean_expression(expr):
    """Limpiar expresiones para PL/SQL"""
    if not expr:
        return ""
    cleaned = re.sub(r'[^\w\s\-().,:]', '', str(expr))
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def extract_move_statements(content):
    """Extraer statements MOVE y convertir a PL/SQL"""
    statements = []
    
    # Buscar patrones MOVE robustos
    patterns = [
        r'MOVE\s+([^TO]+?)\s+TO\s+([A-Z0-9\-_]+)',
        r'MOVE\s+([^TO]+?)\s+TO\s+([^@\s\r\n]+?)(?:\s|@|$)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            source = clean_expression(match.group(1))
            target = clean_expression(match.group(2))
            
            # Limpiar y validar
            target = re.sub(r'[^A-Z0-9_\-].*$', '', target).strip()
            source = re.sub(r'[^A-Z0-9_\-\'"\s].*$', '', source).strip()
            
            if target and source and len(target) > 1 and len(source) > 1:
                statements.append(f"    {target} := {source};")
    
    return statements

def extract_display_statements(content):
    """Extraer statements DISPLAY y convertir a PL/SQL"""
    statements = []
    
    matches = re.finditer(r'DISPLAY\s+([^@\r\n.]+?)(?:\s|@|$)', content, re.IGNORECASE | re.MULTILINE)
    
    for match in matches:
        args = clean_expression(match.group(1))
        args = re.sub(r'[^A-Z0-9_\-\'"\s].*$', '', args).strip()
        
        if args and len(args) > 1:
            statements.append(f"    DBMS_OUTPUT.PUT_LINE({args});")
    
    return statements

def extract_perform_statements(content):
    """Extraer statements PERFORM y convertir a PL/SQL"""
    statements = []
    
    matches = re.finditer(r'PERFORM\s+([A-Z0-9\-_]+)', content, re.IGNORECASE | re.MULTILINE)
    
    for match in matches:
        proc_name = clean_expression(match.group(1))
        proc_name = re.sub(r'[^A-Z0-9_\-].*$', '', proc_name).strip()
        
        if proc_name and len(proc_name) > 2:
            proc_name = proc_name.replace('-', '_')
            statements.append(f"    {proc_name}();")
    
    return statements

def is_relevant_content(content):
    """Determinar si el contenido es relevante para PL/SQL"""
    if not content or len(content) < 10:
        return False
    
    # Omitir declaraciones de datos
    upper_content = content.upper()
    if any(pattern in upper_content for pattern in [
        'WORKING-STORAGE', 'FILE SECTION', 'DATA DIVISION',
        'IDENTIFICATION DIVISION', 'PIC ', 'VALUE ', 'REDEFINES'
    ]):
        return False
    
    # Omitir contenido muy largo (probablemente declaraciones)
    if len(content) > 1000:
        return False
    
    return True

def convert_ir_to_sql(ir_file):
    """Convertir IR a SQL"""
    print(f"📁 Cargando IR: {ir_file}")
    
    with open(ir_file, 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    program_name = ir.get("program_name", "UNKNOWN")
    statements = ir.get("statements", [])
    
    print(f"📊 Procesando {len(statements)} statements...")
    
    # Extraer statements convertidos
    all_sql_statements = []
    move_count = 0
    display_count = 0
    perform_count = 0
    
    for stmt in statements:
        content = stmt.get("content", "")
        
        if not is_relevant_content(content):
            continue
        
        # Extraer diferentes tipos de statements
        move_stmts = extract_move_statements(content)
        display_stmts = extract_display_statements(content)
        perform_stmts = extract_perform_statements(content)
        
        all_sql_statements.extend(move_stmts)
        all_sql_statements.extend(display_stmts)
        all_sql_statements.extend(perform_stmts)
        
        move_count += len(move_stmts)
        display_count += len(display_stmts)
        perform_count += len(perform_stmts)
    
    # Generar package PL/SQL
    package_name = re.sub(r'[^A-Z0-9_]', '', program_name.upper())
    if not package_name or not package_name[0].isalpha():
        package_name = f"PKG_{package_name}"
    
    # Package Spec
    package_spec = f"""-- =============================================
-- Package: {package_name}
-- Generated from COBOL program: {program_name}
-- MOVE statements: {move_count}
-- DISPLAY statements: {display_count}
-- PERFORM statements: {perform_count}
-- Total executable statements: {len(all_sql_statements)}
-- =============================================

CREATE OR REPLACE PACKAGE {package_name} IS
  PROCEDURE MAIN;
END {package_name};
/"""

    # Package Body
    package_body = f"""CREATE OR REPLACE PACKAGE BODY {package_name} IS

  PROCEDURE MAIN IS
  BEGIN
    -- Generated PL/SQL from COBOL
{chr(10).join(all_sql_statements)}
    
    -- End of main procedure
    NULL;
  END MAIN;

END {package_name};
/"""

    sql_content = f"{package_spec}\n\n{package_body}"
    
    # Guardar archivo
    output_file = f"out/{program_name}_simple.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✅ SQL generado: {output_file}")
    print(f"📊 Estadísticas:")
    print(f"   MOVE: {move_count}")
    print(f"   DISPLAY: {display_count}")
    print(f"   PERFORM: {perform_count}")
    print(f"   Total: {len(all_sql_statements)}")
    
    return output_file

def main():
    if len(sys.argv) != 2:
        print("Uso: python simple_ir_to_sql.py archivo_ir.json")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    if not os.path.exists(ir_file):
        print(f"❌ Archivo IR no encontrado: {ir_file}")
        sys.exit(1)
    
    try:
        convert_ir_to_sql(ir_file)
        print("🎊 ¡Conversión completada exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



