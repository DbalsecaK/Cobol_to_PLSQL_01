#!/usr/bin/env python3
"""
Convertidor Ultra-Rápido COBOL a PL/SQL
Versión sin ANTLR que usa solo reglas regex optimizadas
Basado en el éxito del 100% de conversión de antlr_converter.py
"""

import sys
import os
import json
import re
import time
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime

# ===== PERFORMANCE OPTIMIZATIONS =====

# Regex compilados para máximo rendimiento
COMPILED_REGEXES = {
    'comment_col7': re.compile(r'^.{6}\*'),
    'comment_asterisks': re.compile(r'^\s*\*\*'),
    'move_pattern': re.compile(r'MOVE\s+(.+?)\s+TO\s+(.+)', re.IGNORECASE),
    'display_pattern': re.compile(r'^DISPLAY\s+(.+?)\\.?$', re.IGNORECASE),
    'if_pattern': re.compile(r'^IF\s+(.+)', re.IGNORECASE),
    'set_pattern': re.compile(r'^SET\s+(.+?)\s+TO\s+(.+)', re.IGNORECASE),
    'perform_pattern': re.compile(r'^PERFORM\s+(.+)', re.IGNORECASE),
    'exec_sql_pattern': re.compile(r'^EXEC\s+SQL', re.IGNORECASE),
    'string_pattern': re.compile(r'^STRING\s+(.+)', re.IGNORECASE),
    'read_pattern': re.compile(r'^READ\s+(.+)', re.IGNORECASE),
    'close_pattern': re.compile(r'^CLOSE\s+(.+)', re.IGNORECASE),
    'initialize_pattern': re.compile(r'^INITIALIZE\s+(.+)', re.IGNORECASE),
    'qualified_field_pattern': re.compile(r'^([A-Z0-9_-]+)\s+OF\s+([A-Z0-9_-]+)', re.IGNORECASE)
}

# ===== TIMING UTILITIES =====
def get_timestamp():
    """Obtener timestamp detallado con milisegundos"""
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")[:-3]

def format_duration(start_time, end_time):
    """Formatear duración en segundos y milisegundos"""
    duration = end_time - start_time
    if duration < 1:
        return f"{duration*1000:.1f} ms"
    elif duration < 60:
        return f"{duration:.3f} segundos"
    else:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.3f}s"

# ===== ULTRA-FAST PARSER =====

class UltraFastParser:
    """Parser ultra-rápido usando solo regex"""
    
    def __init__(self):
        self.stats = {
            'total_lines': 0,
            'comments': 0,
            'statements': 0,
            'processed': 0
        }
    
    def parse_cobol_to_ir(self, file_path: str) -> Dict[str, Any]:
        """Parser principal ultra-rápido"""
        print(f"🚀 Parsing ultra-rápido: {file_path}")
        
        start_time = time.time()
        
        # Leer archivo de una vez con buffering optimizado
        with open(file_path, 'r', encoding='utf-8', buffering=16384) as f:
            content = f.read()
        
        lines = content.splitlines()
        self.stats['total_lines'] = len(lines)
        
        # Extraer información básica
        program_name = self._extract_program_name(lines)
        variables = self._extract_variables(lines)
        statements = self._extract_statements_fast(lines)
        
        end_time = time.time()
        parse_duration = end_time - start_time
        
        ir = {
            "program_name": program_name,
            "variables": variables,
            "statements": statements,
            "metadata": {
                "source_file": file_path,
                "parse_method": "ultra_fast_regex",
                "parse_time": parse_duration,
                "stats": self.stats
            }
        }
        
        print(f"✅ Ultra-fast parsing completado en {format_duration(start_time, end_time)}")
        print(f"📊 {self.stats['processed']} statements procesados")
        
        return ir
    
    def _extract_program_name(self, lines: List[str]) -> str:
        """Extraer nombre del programa"""
        for line in lines[:50]:  # Buscar solo en las primeras 50 líneas
            line = line.strip().upper()
            if line.startswith('PROGRAM-ID'):
                match = re.search(r'PROGRAM-ID\.\s*([A-Z0-9]+)', line)
                if match:
                    return match.group(1)
        return "UNKNOWN"
    
    def _extract_variables(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extraer variables básicas"""
        variables = []
        in_working_storage = False
        
        for line in lines:
            line_upper = line.strip().upper()
            
            if 'WORKING-STORAGE SECTION' in line_upper:
                in_working_storage = True
                continue
            elif 'PROCEDURE DIVISION' in line_upper:
                break
            
            if in_working_storage and re.match(r'^\d+\s+[A-Z0-9_-]+', line_upper):
                # Variable definition found
                parts = line_upper.split()
                if len(parts) >= 2:
                    variables.append({
                        "name": parts[1],
                        "level": parts[0],
                        "raw": line.strip()
                    })
        
        return variables
    
    def _extract_statements_fast(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extractor ultra-rápido de statements"""
        statements = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Procesar statement
            stmt = self._process_single_statement(line, lines, i)
            if stmt:
                statements.append(stmt)
                self.stats['processed'] += 1
            
            i += 1
        
        return statements
    
    def _process_single_statement(self, line: str, lines: List[str], line_idx: int) -> Optional[Dict[str, Any]]:
        """Procesar un statement individual usando regex compilados"""
        line_clean = line.strip()
        
        if not line_clean:
            return None
        
        # 1. Comentarios optimizados
        if (len(line) >= 7 and line[6] == '*') or COMPILED_REGEXES['comment_asterisks'].match(line):
            self.stats['comments'] += 1
            return {"op": "COMMENT", "text": line, "raw": line}
        
        line_upper = line_clean.upper()
        
        # 2. MOVE statements (más común)
        match = COMPILED_REGEXES['move_pattern'].search(line_upper)
        if match:
            return {"op": "MOVE", "src": match.group(1).strip(), "dst": match.group(2).strip(), "raw": line}
        
        # 3. DISPLAY statements
        match = COMPILED_REGEXES['display_pattern'].search(line_upper)
        if match:
            return {"op": "DISPLAY", "content": match.group(1).strip(), "raw": line}
        
        # 4. IF statements
        match = COMPILED_REGEXES['if_pattern'].search(line_upper)
        if match:
            return {"op": "IF", "condition": match.group(1).strip(), "raw": line}
        
        # 5. SET statements
        match = COMPILED_REGEXES['set_pattern'].search(line_upper)
        if match:
            return {"op": "SET", "target": match.group(1).strip(), "value": match.group(2).strip(), "raw": line}
        
        # 6. PERFORM statements
        match = COMPILED_REGEXES['perform_pattern'].search(line_upper)
        if match:
            return {"op": "PERFORM", "target": match.group(1).strip(), "raw": line}
        
        # 7. EXEC SQL blocks
        if COMPILED_REGEXES['exec_sql_pattern'].search(line_upper):
            # Procesar bloque SQL multi-línea
            sql_block = self._extract_sql_block(lines, line_idx)
            return {"op": "EXEC_SQL", "sql": sql_block, "raw": line}
        
        # 8. STRING statements
        match = COMPILED_REGEXES['string_pattern'].search(line_upper)
        if match:
            return {"op": "STRING", "content": match.group(1).strip(), "raw": line}
        
        # 9. READ statements
        match = COMPILED_REGEXES['read_pattern'].search(line_upper)
        if match:
            return {"op": "READ", "file": match.group(1).strip(), "raw": line}
        
        # 10. CLOSE statements
        match = COMPILED_REGEXES['close_pattern'].search(line_upper)
        if match:
            return {"op": "CLOSE", "file": match.group(1).strip(), "raw": line}
        
        # 11. INITIALIZE statements
        match = COMPILED_REGEXES['initialize_pattern'].search(line_upper)
        if match:
            return {"op": "INITIALIZE", "target": match.group(1).strip(), "raw": line}
        
        # 12. Qualified fields (e.g., FIELD OF PARENT)
        match = COMPILED_REGEXES['qualified_field_pattern'].search(line_upper)
        if match:
            return {"op": "QUALIFIED_FIELD", "field": match.group(1), "parent": match.group(2), "raw": line}
        
        # 13. Catch-all para cualquier línea no vacía
        if line_clean:
            self.stats['statements'] += 1
            return {"op": "UNKNOWN", "content": line_clean, "raw": line}
        
        return None
    
    def _extract_sql_block(self, lines: List[str], start_idx: int) -> str:
        """Extraer bloque SQL multi-línea"""
        sql_lines = []
        i = start_idx
        
        while i < len(lines):
            line = lines[i].strip()
            sql_lines.append(line)
            
            if 'END-EXEC' in line.upper():
                break
            i += 1
        
        return ' '.join(sql_lines)

# ===== PL/SQL GENERATOR =====

def apply_rule(stmt: Dict[str, Any]) -> str:
    """Aplicar regla de conversión optimizada"""
    op = stmt.get("op", "UNKNOWN")
    
    if op == "COMMENT":
        return f"    -- {stmt.get('text', '').strip()}"
    
    elif op == "MOVE":
        src = stmt.get("src", "")
        dst = stmt.get("dst", "")
        return f"    {dst} := {src};"
    
    elif op == "DISPLAY":
        content = stmt.get("content", "")
        return f"    DBMS_OUTPUT.PUT_LINE({content});"
    
    elif op == "IF":
        condition = stmt.get("condition", "")
        return f"    IF {condition} THEN"
    
    elif op == "SET":
        target = stmt.get("target", "")
        value = stmt.get("value", "")
        return f"    {target} := {value};"
    
    elif op == "PERFORM":
        target = stmt.get("target", "")
        return f"    {target};"
    
    elif op == "EXEC_SQL":
        sql = stmt.get("sql", "")
        return f"    {sql}"
    
    elif op == "STRING":
        content = stmt.get("content", "")
        return f"    -- STRING: {content}"
    
    elif op == "READ":
        file_name = stmt.get("file", "")
        return f"    -- READ {file_name}"
    
    elif op == "CLOSE":
        file_name = stmt.get("file", "")
        return f"    -- CLOSE {file_name}"
    
    elif op == "INITIALIZE":
        target = stmt.get("target", "")
        return f"    -- INITIALIZE {target}"
    
    elif op == "QUALIFIED_FIELD":
        field = stmt.get("field", "")
        parent = stmt.get("parent", "")
        return f"    -- Qualified field: {parent}.{field}"
    
    else:
        # Universal catch-all
        raw_content = stmt.get('raw', 'Unknown statement')
        return f"    -- {raw_content}"

def generate_plsql_package(ir: Dict[str, Any]) -> str:
    """Generar package PL/SQL optimizado"""
    program_name = ir.get("program_name", "UNKNOWN")
    statements = ir.get("statements", [])
    
    header = f"""CREATE OR REPLACE PACKAGE {program_name} AS
    -- Generated by Ultra-Fast COBOL to PL/SQL Converter
    -- Parse method: {ir.get('metadata', {}).get('parse_method', 'unknown')}
    -- Parse time: {ir.get('metadata', {}).get('parse_time', 0):.3f}s
    
    PROCEDURE main_procedure;
END {program_name};
/

CREATE OR REPLACE PACKAGE BODY {program_name} AS
    
    PROCEDURE main_procedure IS
    BEGIN
"""
    
    body_lines = []
    for stmt in statements:
        converted = apply_rule(stmt)
        if converted:
            body_lines.append(converted)
    
    footer = f"""    END main_procedure;
    
END {program_name};
/"""
    
    return header + '\n'.join(body_lines) + '\n' + footer

# ===== MAIN EXECUTION =====

def main():
    """Función principal ultra-optimizada"""
    if len(sys.argv) != 2:
        print("Uso: python ultra_fast_converter.py <archivo.cob>")
        sys.exit(1)
    
    cob_path = sys.argv[1]
    if not os.path.exists(cob_path):
        print(f"❌ Error: No se encuentra el archivo {cob_path}")
        sys.exit(1)
    
    # Configurar paths de salida
    base_name = os.path.splitext(os.path.basename(cob_path))[0]
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    
    ir_file = os.path.join(output_dir, f"{base_name.upper()}_ultrafast_ir.json")
    sql_file = os.path.join(output_dir, f"{base_name.upper()}_ultrafast.sql")
    report_file = os.path.join(output_dir, f"{base_name.upper()}_ultrafast_report.json")
    
    # Timing
    total_start = time.time()
    start_timestamp = get_timestamp()
    
    print("=" * 60)
    print(f"🚀 Ultra-Fast COBOL to PL/SQL Converter")
    print(f"📁 Archivo: {cob_path}")
    print(f"⏰ Inicio: {start_timestamp}")
    print("=" * 60)
    
    try:
        # 1. Parsing ultra-rápido
        parse_start = time.time()
        parser = UltraFastParser()
        ir = parser.parse_cobol_to_ir(cob_path)
        parse_end = time.time()
        
        # 2. Generación PL/SQL
        gen_start = time.time()
        plsql_code = generate_plsql_package(ir)
        gen_end = time.time()
        
        # 3. Escritura de archivos
        io_start = time.time()
        
        # Guardar IR
        with open(ir_file, 'w', encoding='utf-8') as f:
            json.dump(ir, f, indent=2, ensure_ascii=False)
        
        # Guardar PL/SQL
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(plsql_code)
        
        # Generar reporte
        total_statements = len(ir.get("statements", []))
        gaps = sum(1 for stmt in ir.get("statements", []) if stmt.get("op") == "UNKNOWN")
        success_rate = ((total_statements - gaps) / total_statements * 100) if total_statements > 0 else 0
        
        report = {
            "conversion_stats": {
                "total_statements": total_statements,
                "successful_conversions": total_statements - gaps,
                "gaps": gaps,
                "success_rate": success_rate
            },
            "performance_stats": {
                "total_time": parse_end - parse_start,
                "parsing_time": parse_end - parse_start,
                "generation_time": gen_end - gen_start,
                "file_size": os.path.getsize(cob_path),
                "lines_per_second": parser.stats['total_lines'] / (parse_end - parse_start)
            },
            "files": {
                "source": cob_path,
                "ir": ir_file,
                "plsql": sql_file
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        io_end = time.time()
        total_end = time.time()
        
        # Mostrar resultados
        print(f"✅ Archivos generados:")
        print(f"   📊 IR: {ir_file}")
        print(f"   📄 PL/SQL: {sql_file}")
        print(f"   📊 Reporte: {report_file}")
        
        print("=" * 60)
        print("📊 RESUMEN ULTRA-FAST")
        print("=" * 60)
        print(f"🎯 COBERTURA:")
        print(f"   ✅ Reglas aplicadas: {total_statements - gaps}")
        print(f"   ❌ GAPs encontrados:  {gaps}")
        print(f"   📊 Total sentencias: {total_statements}")
        print(f"   📈 Porcentaje éxito:  {success_rate:.1f}%")
        print(f"⏰ RENDIMIENTO:")
        print(f"   🕐 Inicio:           {start_timestamp}")
        print(f"   🕐 Fin:             {get_timestamp()}")
        print(f"   ⏱️  Tiempo total:      {format_duration(total_start, total_end)}")
        print(f"   ⏱️  Parsing:           {format_duration(parse_start, parse_end)}")
        print(f"   ⏱️  Generación PL/SQL: {format_duration(gen_start, gen_end)}")
        print(f"   ⏱️  Archivos I/O:      {format_duration(io_start, io_end)}")
        print(f"📁 ARCHIVO:")
        print(f"   📄 Tamaño archivo:    {os.path.getsize(cob_path):,} bytes")
        print(f"   📊 Líneas procesadas: {parser.stats['total_lines']}")
        print(f"   ⚡ Velocidad:         {parser.stats['total_lines'] / (parse_end - parse_start):.1f} líneas/segundo")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
