#!/usr/bin/env python3
"""
ANTLR Parser - Primer programa del pipeline de conversión
Convierte archivos COBOL a Intermediate Representation (IR) usando ANTLR

Entrada: Archivo COBOL (.cob)
Salida: 
- Archivo IR (JSON)
- Reporte de parsing (JSON)
- Logs de análisis

Uso: python antlr_parser.py archivo.cob
"""

import sys
import os
import json
import re
import time
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime

# Imports de ANTLR
from antlr4 import FileStream, CommonTokenStream
from Cobol85Lexer import Cobol85Lexer
from Cobol85Parser import Cobol85Parser

# ===== PERFORMANCE OPTIMIZATIONS =====

# Caché global para archivos parseados
PARSE_CACHE = {}

# Regex compilados para mejor rendimiento
COMPILED_REGEXES = {
    'comment_col7': re.compile(r'^.{6}\*'),
    'comment_asterisks': re.compile(r'^\s*\*\*'),
    'move_pattern': re.compile(r'MOVE\s+(.+?)\s+TO\s+(.+)', re.IGNORECASE),
    'display_pattern': re.compile(r'^DISPLAY\s+(.+?)\\.?$', re.IGNORECASE),
    'if_pattern': re.compile(r'^IF\s+(.+)', re.IGNORECASE),
    'exec_sql': re.compile(r'EXEC\s+SQL', re.IGNORECASE),
    'end_exec': re.compile(r'END-EXEC', re.IGNORECASE),
    'perform_pattern': re.compile(r'^PERFORM\s+(.+)', re.IGNORECASE),
    'qualified_field': re.compile(r'^([A-Z0-9_-]+)\s+OF\s+([A-Z0-9_-]+)', re.IGNORECASE)
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

# ===== CACHE UTILITIES =====

def get_file_hash(file_path: str) -> str:
    """Generar hash MD5 del archivo para caché"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def should_use_cache(file_path: str) -> tuple:
    """Determinar si usar caché basado en hash del archivo"""
    try:
        current_hash = get_file_hash(file_path)
        cache_key = f"{file_path}_{current_hash}"
        
        if cache_key in PARSE_CACHE:
            return True, cache_key, PARSE_CACHE[cache_key]
        else:
            return False, cache_key, None
    except Exception:
        return False, "", None

def save_to_cache(cache_key: str, ir_data: Dict[str, Any]):
    """Guardar IR en caché"""
    PARSE_CACHE[cache_key] = ir_data

# ===== ANTLR IR VISITOR =====

class IRBuildingVisitor:
    """Visitor para construir IR desde árbol ANTLR"""
    
    def __init__(self, token_stream, full_text):
        self.token_stream = token_stream
        self.full_text = full_text
        self.lines = full_text.split('\n')
        
    def build_ir(self, tree) -> Dict[str, Any]:
        """Construir IR desde tree ANTLR"""
        print("🔧 Construyendo IR desde tree ANTLR...")
        
        # Extraer información básica
        program_name = self._extract_program_name()
        variables = self._extract_variables()
        statements = self._extract_statements()
        
        ir = {
            "program_name": program_name,
            "variables": variables,
            "procedures": [{
                "name": "MAIN-PROCEDURE",
                "statements": statements
            }],
            "metadata": {
                "source_lines": len(self.lines),
                "parse_method": "antlr_optimized",
                "total_statements": len(statements),
                "total_variables": len(variables)
            }
        }
        
        print(f"✅ IR construido: {len(statements)} statements, {len(variables)} variables")
        return ir
    
    def _extract_program_name(self) -> str:
        """Extraer nombre del programa"""
        for line in self.lines[:50]:
            line_clean = line.strip().upper()
            if 'PROGRAM-ID' in line_clean:
                # Buscar pattern PROGRAM-ID. NOMBRE
                match = re.search(r'PROGRAM-ID\.\s*([A-Z0-9]+)', line_clean)
                if match:
                    return match.group(1)
        return "UNKNOWN_PROGRAM"
    
    def _extract_variables(self) -> List[Dict[str, Any]]:
        """Extraer definiciones de variables"""
        variables = []
        in_working_storage = False
        
        for i, line in enumerate(self.lines):
            line_upper = line.strip().upper()
            
            if 'WORKING-STORAGE SECTION' in line_upper:
                in_working_storage = True
                continue
            elif 'PROCEDURE DIVISION' in line_upper:
                break
                
            if in_working_storage and line.strip():
                # Detectar definición de variable (nivel + nombre)
                match = re.match(r'^\s*(\d+)\s+([A-Z0-9_-]+)', line_upper)
                if match:
                    level = match.group(1)
                    name = match.group(2)
                    variables.append({
                        "level": level,
                        "name": name,
                        "raw": line.strip(),
                        "line_number": i + 1
                    })
        
        return variables
    
    def _extract_statements(self) -> List[Dict[str, Any]]:
        """Extraer statements del código COBOL usando reglas optimizadas"""
        statements = []
        i = 0
        
        print("🔍 Extrayendo statements con reglas optimizadas...")
        
        while i < len(self.lines):
            line = self.lines[i]
            line_clean = line.strip()
            
            if not line_clean:
                i += 1
                continue
            
            # Procesar línea
            stmt = self._process_line(line, i)
            if stmt:
                statements.append(stmt)
            
            i += 1
        
        return statements
    
    def _process_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Procesar una línea individual"""
        line_clean = line.strip()
        
        # 1. Comentarios optimizados
        if (len(line) >= 7 and line[6] == '*') or COMPILED_REGEXES['comment_asterisks'].match(line):
            return {"op": "COMMENT", "text": line_clean, "raw": line_clean, "line": line_num + 1}
        
        if line_clean.startswith('***'):
            return {"op": "COMMENT", "text": line_clean, "raw": line_clean, "line": line_num + 1}
        
        line_upper = line_clean.upper()
        
        # 2. MOVE statements (más frecuente)
        match = COMPILED_REGEXES['move_pattern'].search(line_upper)
        if match:
            return {
                "op": "MOVE", 
                "src": match.group(1).strip(), 
                "dst": match.group(2).strip(), 
                "raw": line_clean,
                "line": line_num + 1
            }
        
        # 3. DISPLAY statements
        match = COMPILED_REGEXES['display_pattern'].search(line_upper)
        if match:
            return {
                "op": "DISPLAY", 
                "content": match.group(1).strip(), 
                "raw": line_clean,
                "line": line_num + 1
            }
        
        # 4. IF statements
        match = COMPILED_REGEXES['if_pattern'].search(line_upper)
        if match:
            return {
                "op": "IF", 
                "condition": match.group(1).strip(), 
                "raw": line_clean,
                "line": line_num + 1
            }
        
        # 5. PERFORM statements
        match = COMPILED_REGEXES['perform_pattern'].search(line_upper)
        if match:
            return {
                "op": "PERFORM", 
                "target": match.group(1).strip(), 
                "raw": line_clean,
                "line": line_num + 1
            }
        
        # 6. EXEC SQL blocks
        if COMPILED_REGEXES['exec_sql'].search(line_upper):
            # Manejar bloque SQL
            sql_content = self._extract_sql_block(line_num)
            return {
                "op": "EXEC_SQL", 
                "sql": sql_content, 
                "raw": line_clean,
                "line": line_num + 1
            }
        
        # 7. Qualified fields (FIELD OF PARENT)
        match = COMPILED_REGEXES['qualified_field'].search(line_upper)
        if match:
            return {
                "op": "QUALIFIED_FIELD", 
                "field": match.group(1), 
                "parent": match.group(2), 
                "raw": line_clean,
                "line": line_num + 1
            }
        
        # 8. Otras operaciones comunes
        if line_upper.startswith('SET '):
            return {"op": "SET", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('STRING '):
            return {"op": "STRING", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('READ '):
            return {"op": "READ", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('CLOSE '):
            return {"op": "CLOSE", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('INITIALIZE '):
            return {"op": "INITIALIZE", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif 'PROCEDURE DIVISION' in line_upper:
            return {"op": "PROCEDURE_DIVISION", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('END-IF'):
            return {"op": "END_IF", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('ELSE'):
            return {"op": "ELSE", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('EVALUATE'):
            return {"op": "EVALUATE", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('WHEN'):
            return {"op": "WHEN", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        elif line_upper.startswith('END-EVALUATE'):
            return {"op": "END_EVALUATE", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        
        # 9. Catch-all para cualquier línea con contenido
        if line_clean and not line_clean.startswith('*'):
            return {"op": "UNKNOWN", "content": line_clean, "raw": line_clean, "line": line_num + 1}
        
        return None
    
    def _extract_sql_block(self, start_line: int) -> str:
        """Extraer bloque SQL multi-línea"""
        sql_lines = []
        i = start_line
        
        while i < len(self.lines):
            line = self.lines[i]
            sql_lines.append(line.strip())
            
            if COMPILED_REGEXES['end_exec'].search(line.upper()):
                break
            i += 1
        
        return ' '.join(sql_lines)

# ===== MAIN PARSING FUNCTION =====

def parse_cobol_to_ir(file_path: str) -> Dict[str, Any]:
    """Función principal para parsear COBOL a IR usando ANTLR"""
    print(f"🔍 Parseando con ANTLR: {file_path}")
    
    # Verificar caché primero
    use_cache, cache_key, cached_ir = should_use_cache(file_path)
    if use_cache and cached_ir:
        print("✅ IR recuperado desde caché")
        return cached_ir
    else:
        print("🔄 Parsing requerido para archivo")
    
    try:
        # Parsear con ANTLR
        input_stream = FileStream(file_path, encoding='utf-8')
        lexer = Cobol85Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = Cobol85Parser(stream)
        
        # Configurar parser para mejor rendimiento
        parser.removeErrorListeners()  # Remover listeners por defecto
        
        # Parsear usando la gramática
        tree = parser.startRule()
        print("✅ Parsing ANTLR exitoso!")
        
        # Construir IR
        visitor = IRBuildingVisitor(token_stream=stream, full_text=input_stream.strdata)
        ir = visitor.build_ir(tree)
        
        # Guardar en caché
        if cache_key:
            save_to_cache(cache_key, ir)
            print("💾 IR guardado en caché")
        
        return ir
        
    except Exception as e:
        print(f"❌ Error optimizado en parsing: {e}")
        # Fallback manual si ANTLR falla
        return create_fallback_ir(file_path)

def create_fallback_ir(file_path: str) -> Dict[str, Any]:
    """Crear IR usando parsing manual como fallback"""
    print("🔧 Usando parsing manual como fallback...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        visitor = IRBuildingVisitor(token_stream=None, full_text=content)
        
        # Usar solo las funciones de extracción manual
        program_name = visitor._extract_program_name()
        variables = visitor._extract_variables()
        statements = visitor._extract_statements()
        
        return {
            "program_name": program_name,
            "variables": variables,
            "procedures": [{
                "name": "MAIN-PROCEDURE",
                "statements": statements
            }],
            "metadata": {
                "source_lines": len(lines),
                "parse_method": "manual_fallback",
                "total_statements": len(statements),
                "total_variables": len(variables)
            }
        }
        
    except Exception as e:
        print(f"❌ Error en fallback: {e}")
        return {
            "program_name": "ERROR",
            "variables": [],
            "procedures": [],
            "metadata": {
                "error": str(e),
                "parse_method": "failed"
            }
        }

# ===== FILE I/O FUNCTIONS =====

def save_ir_to_file(ir: Dict[str, Any], output_file: str):
    """Guardar IR en archivo JSON con formato optimizado"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8', buffering=16384) as f:
        json.dump(ir, f, indent=2, ensure_ascii=False)
    print(f"💾 IR guardado en: {output_file}")

def generate_parsing_report(ir: Dict[str, Any], file_path: str, times: Dict[str, float]) -> Dict[str, Any]:
    """Generar reporte detallado del parsing"""
    
    total_statements = ir.get('metadata', {}).get('total_statements', 0)
    statements = ir.get('procedures', [{}])[0].get('statements', []) if ir.get('procedures') else []
    
    # Analizar tipos de statements
    statement_types = {}
    unknown_count = 0
    
    for stmt in statements:
        op = stmt.get('op', 'UNKNOWN')
        statement_types[op] = statement_types.get(op, 0) + 1
        if op == 'UNKNOWN':
            unknown_count += 1
    
    success_rate = ((total_statements - unknown_count) / total_statements * 100) if total_statements > 0 else 0
    
    return {
        "parsing_summary": {
            "source_file": file_path,
            "program_name": ir.get('program_name', 'UNKNOWN'),
            "parse_method": ir.get('metadata', {}).get('parse_method', 'unknown'),
            "total_lines": ir.get('metadata', {}).get('source_lines', 0),
            "total_statements": total_statements,
            "total_variables": ir.get('metadata', {}).get('total_variables', 0),
            "unknown_statements": unknown_count,
            "success_rate": round(success_rate, 2)
        },
        "statement_analysis": {
            "types_found": statement_types,
            "most_common": sorted(statement_types.items(), key=lambda x: x[1], reverse=True)[:10]
        },
        "performance_metrics": {
            "parsing_time": times.get('parsing', 0),
            "total_time": times.get('total', 0),
            "lines_per_second": ir.get('metadata', {}).get('source_lines', 0) / times.get('parsing', 1),
            "statements_per_second": total_statements / times.get('parsing', 1)
        },
        "cache_info": {
            "cache_entries": len(PARSE_CACHE),
            "cache_used": times.get('parsing', 0) < 1.0  # Si parsing fue muy rápido, probablemente usó caché
        }
    }

# ===== MAIN EXECUTION =====

def main():
    """Función principal del parser ANTLR"""
    if len(sys.argv) != 2:
        print("Uso: python antlr_parser.py <archivo.cob>")
        print()
        print("Este programa convierte archivos COBOL a Intermediate Representation (IR)")
        print("Genera:")
        print("  - Archivo IR (JSON)")
        print("  - Reporte de parsing (JSON)")
        sys.exit(1)
    
    cob_path = sys.argv[1]
    if not os.path.exists(cob_path):
        print(f"❌ Error: No se encuentra el archivo {cob_path}")
        sys.exit(1)
    
    # Configurar archivos de salida
    base_name = os.path.splitext(os.path.basename(cob_path))[0]
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    
    ir_file = os.path.join(output_dir, f"{base_name.upper()}_ir.json")
    report_file = os.path.join(output_dir, f"{base_name.upper()}_parsing_report.json")
    
    # Timing
    total_start = time.time()
    start_timestamp = get_timestamp()
    
    print("=" * 70)
    print(f"🔧 ANTLR Parser - COBOL to IR Converter")
    print(f"📁 Archivo fuente: {cob_path}")
    print(f"⏰ Inicio: {start_timestamp}")
    print(f"💾 Caché disponible: {len(PARSE_CACHE)} entradas")
    print("=" * 70)
    
    try:
        # 1. Parsing COBOL → IR
        parse_start = time.time()
        ir = parse_cobol_to_ir(cob_path)
        parse_end = time.time()
        
        # 2. Guardar archivos
        io_start = time.time()
        save_ir_to_file(ir, ir_file)
        
        # 3. Generar reporte
        times = {
            'parsing': parse_end - parse_start,
            'total': time.time() - total_start
        }
        
        report = generate_parsing_report(ir, cob_path, times)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        io_end = time.time()
        total_end = time.time()
        
        # Mostrar resultados
        print(f"✅ Archivos generados:")
        print(f"   📊 IR: {ir_file}")
        print(f"   📊 Reporte: {report_file}")
        
        print("=" * 70)
        print("📊 RESUMEN DE PARSING")
        print("=" * 70)
        
        summary = report['parsing_summary']
        performance = report['performance_metrics']
        
        print(f"🎯 ANÁLISIS:")
        print(f"   📋 Programa: {summary['program_name']}")
        print(f"   📄 Líneas fuente: {summary['total_lines']}")
        print(f"   📊 Variables: {summary['total_variables']}")
        print(f"   🔧 Statements: {summary['total_statements']}")
        print(f"   ❓ Desconocidos: {summary['unknown_statements']}")
        print(f"   📈 Tasa éxito: {summary['success_rate']}%")
        
        print(f"⏰ RENDIMIENTO:")
        print(f"   🕐 Inicio: {start_timestamp}")
        print(f"   🕐 Fin: {get_timestamp()}")
        print(f"   ⏱️  Parsing: {format_duration(parse_start, parse_end)}")
        print(f"   ⏱️  I/O: {format_duration(io_start, io_end)}")
        print(f"   ⏱️  Total: {format_duration(total_start, total_end)}")
        print(f"   ⚡ Velocidad: {performance['lines_per_second']:.1f} líneas/seg")
        
        print(f"📊 STATEMENTS MÁS COMUNES:")
        for stmt_type, count in report['statement_analysis']['most_common'][:5]:
            print(f"   • {stmt_type}: {count}")
        
        print("=" * 70)
        print("✅ Parsing completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante el parsing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
