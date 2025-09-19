#!/usr/bin/env python3
"""
Conversor directo que usa los statements ya procesados del IR fixed
Evita el procesamiento del árbol completo masivo
"""

import sys
import os
import json
import re

def convert_move_statement(stmt):
    """Convertir statement MOVE a PL/SQL"""
    content = stmt.get('content', '')
    src = stmt.get('src', '')
    dst = stmt.get('dst', '')
    op = stmt.get('op', '')
    
    # Si tenemos src y dst directamente del IR fixed
    if src and dst and op == 'MOVE':
        # Limpiar variables
        src_clean = src.strip().replace('-', '_')
        dst_clean = dst.strip().replace('-', '_')
        return f"    {dst_clean} := {src_clean};"
    
    # Si tenemos content, parsearlo
    if content:
        move_match = re.search(r'MOVE\s+(.+?)\s+TO\s+(.+?)(?:\.|$)', content, re.IGNORECASE)
        if move_match:
            src_clean = move_match.group(1).strip().replace('-', '_')
            dst_clean = move_match.group(2).strip().replace('-', '_')
            return f"    {dst_clean} := {src_clean};"
    
    return None

def convert_display_statement(stmt):
    """Convertir statement DISPLAY a PL/SQL"""
    content = stmt.get('content', '')
    op = stmt.get('op', '')
    
    if op == 'DISPLAY' or 'DISPLAY' in content:
        display_match = re.search(r'DISPLAY\s+(.+)', content, re.IGNORECASE)
        if display_match:
            args = display_match.group(1).strip()
            return f"    DBMS_OUTPUT.PUT_LINE({args});"
    
    return None

def convert_perform_statement(stmt):
    """Convertir statement PERFORM a PL/SQL"""
    content = stmt.get('content', '')
    target = stmt.get('target', '')
    op = stmt.get('op', '')
    
    # Si tenemos target directamente del IR fixed
    if target and op == 'PERFORM':
        target_clean = target.replace('-', '_')
        return f"    {target_clean}();"
    
    # Si tenemos content, parsearlo
    if content:
        perform_match = re.search(r'PERFORM\s+([A-Z0-9\-_]+)', content, re.IGNORECASE)
        if perform_match:
            target_clean = perform_match.group(1).replace('-', '_')
            return f"    {target_clean}();"
    
    return None

def convert_ir_to_sql_direct(ir_file):
    """Conversión directa usando statements ya procesados"""
    print(f"📁 Cargando IR: {ir_file}")
    
    with open(ir_file, 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    program_name = ir.get("program_name", "UNKNOWN")
    statements = ir.get("statements", [])
    
    print(f"📊 Procesando {len(statements)} statements...")
    
    # Contadores y SQL generado
    sql_lines = []
    move_count = 0
    display_count = 0
    perform_count = 0
    
    for stmt in statements:
        converted = None
        
        # Intentar convertir cada tipo
        converted = convert_move_statement(stmt)
        if converted:
            sql_lines.append(converted)
            move_count += 1
            continue
            
        converted = convert_display_statement(stmt)
        if converted:
            sql_lines.append(converted)
            display_count += 1
            continue
            
        converted = convert_perform_statement(stmt)
        if converted:
            sql_lines.append(converted)
            perform_count += 1
            continue
    
    # Generar package PL/SQL
    package_name = re.sub(r'[^A-Z0-9_]', '', program_name.upper())
    if not package_name or not package_name[0].isalpha():
        package_name = f"PKG_{package_name}"
    
    # Crear SQL final
    sql_content = f"""-- =============================================
-- Package: {package_name} - CONVERSIÓN DIRECTA
-- Generated from COBOL program: {program_name}
-- MOVE statements: {move_count}
-- DISPLAY statements: {display_count}
-- PERFORM statements: {perform_count}
-- Total: {len(sql_lines)}
-- =============================================

CREATE OR REPLACE PACKAGE {package_name} IS
  PROCEDURE MAIN;
END {package_name};
/

CREATE OR REPLACE PACKAGE BODY {package_name} IS

  PROCEDURE MAIN IS
  BEGIN
    -- Converted COBOL statements
{chr(10).join(sql_lines)}
    
    -- End of main procedure
    NULL;
  END MAIN;

END {package_name};
/"""

    # Guardar archivo
    output_file = f"out/{program_name}_direct.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✅ SQL generado: {output_file}")
    print(f"📊 Conversiones:")
    print(f"   MOVE: {move_count}")
    print(f"   DISPLAY: {display_count}")
    print(f"   PERFORM: {perform_count}")
    print(f"   Total: {len(sql_lines)}")
    
    return output_file

def main():
    if len(sys.argv) != 2:
        print("Uso: python direct_converter.py archivo_ir.json")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    if not os.path.exists(ir_file):
        print(f"❌ Archivo IR no encontrado: {ir_file}")
        sys.exit(1)
    
    try:
        convert_ir_to_sql_direct(ir_file)
        print("🎊 ¡Conversión directa completada!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()




