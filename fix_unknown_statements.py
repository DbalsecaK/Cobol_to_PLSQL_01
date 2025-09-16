#!/usr/bin/env python3
"""
Fix Unknown Statements - Corregir elementos UNKNOWN en archivos IR existentes
"""

import json
import re
import sys
import os
from typing import Dict, List, Any

def fix_unknown_statements(ir_file_path: str) -> Dict[str, Any]:
    """Corregir elementos UNKNOWN en un archivo IR existente"""
    print(f"🔧 Corrigiendo elementos UNKNOWN en: {ir_file_path}")
    
    # Cargar IR existente
    with open(ir_file_path, 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    # Patrones para reconocer statements específicos
    patterns = {
        'PREPROCESSOR_DEFINE': r'@DEFINE\s*\([^)]+\)',
        'PREPROCESSOR_CTRLERR': r'@CTRLERR\s*\([^)]+\)',
        'PREPROCESSOR_INIBAT': r'@INIBAT\s*\([^)]*\)',
        'PREPROCESSOR_FINBAT': r'@FINBAT\s*\([^)]*\)',
        'PREPROCESSOR_CTRL': r'@CTRL\s*\([^)]+\)',
        'FUNCTION_CALL': r'@\w+\s*\([^)]*\)',
        'MOVE': r'^\s*MOVE\s+(?:CORRESPONDING\s+)?(.+?)\s+TO\s+(.+?)(?:\s*\.)?\s*$',
        'DISPLAY': r'^\s*DISPLAY\s+(.+?)(?:\s*\.)?\s*$',
        'PERFORM': r'^\s*PERFORM\s+(.+?)(?:\s+UNTIL\s+(.+?))?(?:\s*\.)?\s*$',
        'IF': r'^\s*IF\s+(.+?)(?:\s+THEN\s+(.+?))?(?:\s*\.)?\s*$',
        'COMPUTE': r'^\s*COMPUTE\s+(.+?)\s*=\s*(.+?)(?:\s*\.)?\s*$',
        'ADD': r'^\s*ADD\s+(.+?)\s+TO\s+(.+?)(?:\s*\.)?\s*$',
        'SUBTRACT': r'^\s*SUBTRACT\s+(.+?)\s+FROM\s+(.+?)(?:\s*\.)?\s*$',
        'MULTIPLY': r'^\s*MULTIPLY\s+(.+?)\s+BY\s+(.+?)(?:\s*\.)?\s*$',
        'DIVIDE': r'^\s*DIVIDE\s+(.+?)\s+(?:INTO|BY)\s+(.+?)(?:\s*\.)?\s*$',
        'SET': r'^\s*SET\s+(.+?)\s+TO\s+(.+?)(?:\s*\.)?\s*$',
        'CALL': r'^\s*CALL\s+["\']?([^"\']+)["\']?(?:\s+USING\s+(.+?))?(?:\s*\.)?\s*$',
        'OPEN': r'^\s*OPEN\s+(INPUT|OUTPUT|I-O|EXTEND)\s+(.+?)(?:\s*\.)?\s*$',
        'CLOSE': r'^\s*CLOSE\s+(.+?)(?:\s*\.)?\s*$',
        'READ': r'^\s*READ\s+(.+?)(?:\s+INTO\s+(.+?))?(?:\s+AT\s+END\s+(.+?))?(?:\s*\.)?\s*$',
        'WRITE': r'^\s*WRITE\s+(.+?)(?:\s+FROM\s+(.+?))?(?:\s*\.)?\s*$',
        'GOBACK': r'^\s*GOBACK\s*(?:\s*\.)?\s*$',
        'EXIT': r'^\s*EXIT\s*(?:\s*\.)?\s*$',
        'STOP': r'^\s*STOP\s+(RUN|.*?)(?:\s*\.)?\s*$',
        'END_IF': r'^\s*END-IF\s*(?:\s*\.)?\s*$',
        'END_PERFORM': r'^\s*END-PERFORM\s*(?:\s*\.)?\s*$',
        'ELSE': r'^\s*ELSE\s*(.*?)(?:\s*\.)?\s*$',
        'EVALUATE': r'^\s*EVALUATE\s+(.+?)(?:\s*\.)?\s*$',
        'WHEN': r'^\s*WHEN\s+(.+?)(?:\s*\.)?\s*$',
        'STRING': r'^\s*STRING\s+(.+?)(?:\s*\.)?\s*$',
        'UNSTRING': r'^\s*UNSTRING\s+(.+?)(?:\s*\.)?\s*$',
        'INSPECT': r'^\s*INSPECT\s+(.+?)(?:\s*\.)?\s*$',
        'INITIALIZE': r'^\s*INITIALIZE\s+(.+?)(?:\s*\.)?\s*$',
    }
    
    # Contadores
    fixed_count = 0
    total_unknown = 0
    
    def fix_statement(stmt: Dict[str, Any]) -> Dict[str, Any]:
        """Corregir un statement individual"""
        nonlocal fixed_count, total_unknown
        
        if stmt.get("op") == "UNKNOWN":
            total_unknown += 1
            raw_content = stmt.get("raw", "")
            
            # Intentar reconocer el patrón
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, raw_content, re.IGNORECASE):
                    match = re.search(pattern, raw_content, re.IGNORECASE)
                    
                    # Crear statement corregido
                    fixed_stmt = {
                        "op": pattern_name,
                        "content": raw_content,
                        "raw": raw_content,
                        "details": {}
                    }
                    
                    # Agregar detalles específicos según el tipo
                    if pattern_name == "PREPROCESSOR_DEFINE":
                        fixed_stmt["details"] = {"directive": "DEFINE", "preprocessor": True}
                    elif pattern_name == "PREPROCESSOR_CTRLERR":
                        fixed_stmt["details"] = {"directive": "CTRLERR", "preprocessor": True}
                    elif pattern_name == "PREPROCESSOR_INIBAT":
                        fixed_stmt["details"] = {"directive": "INIBAT", "preprocessor": True}
                    elif pattern_name == "FUNCTION_CALL":
                        fixed_stmt["details"] = {"function_call": True}
                    elif pattern_name == "MOVE" and match and len(match.groups()) >= 2:
                        fixed_stmt["details"] = {
                            "source": match.group(1).strip(),
                            "target": match.group(2).strip()
                        }
                    elif pattern_name == "DISPLAY" and match and len(match.groups()) >= 1:
                        fixed_stmt["details"] = {"arguments": match.group(1).strip()}
                    elif pattern_name == "PERFORM" and match and len(match.groups()) >= 1:
                        fixed_stmt["details"] = {"target": match.group(1).strip()}
                        if len(match.groups()) >= 2 and match.group(2):
                            fixed_stmt["details"]["until_condition"] = match.group(2).strip()
                    elif pattern_name == "IF" and match and len(match.groups()) >= 1:
                        fixed_stmt["details"] = {"condition": match.group(1).strip()}
                        if len(match.groups()) >= 2 and match.group(2):
                            fixed_stmt["details"]["then_action"] = match.group(2).strip()
                    elif pattern_name == "COMPUTE" and match and len(match.groups()) >= 2:
                        fixed_stmt["details"] = {
                            "target": match.group(1).strip(),
                            "expression": match.group(2).strip()
                        }
                    elif pattern_name in ["ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"] and match and len(match.groups()) >= 2:
                        fixed_stmt["details"] = {
                            "operand1": match.group(1).strip(),
                            "operand2": match.group(2).strip()
                        }
                    elif pattern_name == "SET" and match and len(match.groups()) >= 2:
                        fixed_stmt["details"] = {
                            "target": match.group(1).strip(),
                            "value": match.group(2).strip()
                        }
                    elif pattern_name == "CALL" and match and len(match.groups()) >= 1:
                        fixed_stmt["details"] = {"program": match.group(1).strip()}
                        if len(match.groups()) >= 2 and match.group(2):
                            fixed_stmt["details"]["using_params"] = match.group(2).strip()
                    
                    fixed_count += 1
                    return fixed_stmt
            
            # Si no se pudo reconocer, mantener como UNKNOWN pero con más información
            return {
                "op": "UNKNOWN",
                "content": raw_content,
                "raw": raw_content,
                "details": {"unrecognized": True, "attempted_fix": True}
            }
        
        return stmt
    
    # Procesar statements en procedimientos
    for procedure in ir.get("procedures", []):
        if "statements" in procedure:
            procedure["statements"] = [fix_statement(stmt) for stmt in procedure["statements"]]
    
    # Procesar statements globales
    if "statements" in ir:
        ir["statements"] = [fix_statement(stmt) for stmt in ir["statements"]]
    
    # Agregar metadata de corrección
    if "metadata" not in ir:
        ir["metadata"] = {}
    
    ir["metadata"]["unknown_fixes"] = {
        "total_unknown_found": total_unknown,
        "successfully_fixed": fixed_count,
        "fix_rate": round((fixed_count / total_unknown * 100) if total_unknown > 0 else 0, 2)
    }
    
    print(f"✅ Corrección completada:")
    print(f"   📊 Total UNKNOWN encontrados: {total_unknown}")
    print(f"   🔧 Corregidos exitosamente: {fixed_count}")
    print(f"   📈 Tasa de corrección: {ir['metadata']['unknown_fixes']['fix_rate']}%")
    
    return ir

def generate_fix_report(ir: Dict[str, Any], report_path: str):
    """Generar reporte de corrección"""
    fix_info = ir.get("metadata", {}).get("unknown_fixes", {})
    
    # Contar tipos de statements después de la corrección
    statement_types = {}
    total_statements = 0
    
    for procedure in ir.get("procedures", []):
        for stmt in procedure.get("statements", []):
            op = stmt.get("op", "UNKNOWN")
            statement_types[op] = statement_types.get(op, 0) + 1
            total_statements += 1
    
    if "statements" in ir:
        for stmt in ir["statements"]:
            op = stmt.get("op", "UNKNOWN")
            statement_types[op] = statement_types.get(op, 0) + 1
            total_statements += 1
    
    report = {
        "fix_summary": {
            "program_name": ir.get("program_name", "UNKNOWN"),
            "total_statements": total_statements,
            "statement_types": statement_types,
            "unknown_fixes": fix_info
        },
        "timestamp": "2024-01-01 00:00:00",
        "success": True
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python fix_unknown_statements.py archivo_ir.json")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    
    if not os.path.exists(ir_file):
        print(f"❌ Error: Archivo IR no encontrado: {ir_file}")
        sys.exit(1)
    
    # Configurar nombres de archivos de salida
    base_name = os.path.splitext(os.path.basename(ir_file))[0]
    if base_name.endswith("_ir_direct"):
        base_name = base_name[:-10]  # Remover "_ir_direct"
    
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    
    fixed_ir_output = os.path.join(output_dir, f"{base_name}_ir_fixed.json")
    fix_report_output = os.path.join(output_dir, f"{base_name}_fix_report.json")
    
    print("======================================================================")
    print("🔧 Fix Unknown Statements - Corrigiendo elementos UNKNOWN en IR")
    print(f"📁 Archivo IR: {ir_file}")
    print("🎯 Reconociendo patrones específicos de COBOL")
    print("======================================================================")
    
    try:
        # Corregir IR
        fixed_ir = fix_unknown_statements(ir_file)
        
        # Guardar IR corregido
        with open(fixed_ir_output, 'w', encoding='utf-8') as f:
            json.dump(fixed_ir, f, indent=2, ensure_ascii=False)
        
        # Generar reporte
        report = generate_fix_report(fixed_ir, fix_report_output)
        
        print("✅ Archivos generados:")
        print(f"   📄 IR corregido: {fixed_ir_output}")
        print(f"   📊 Reporte: {fix_report_output}")
        
        # Mostrar resumen
        print("======================================================================")
        print("📊 RESUMEN DE CORRECCIÓN")
        print("======================================================================")
        print("🎯 CORRECCIÓN:")
        print(f"   📋 Programa: {fixed_ir.get('program_name', 'UNKNOWN')}")
        print(f"   📄 Total statements: {report['fix_summary']['total_statements']}")
        print(f"   ❌ UNKNOWN encontrados: {report['fix_summary']['unknown_fixes']['total_unknown_found']}")
        print(f"   ✅ Corregidos: {report['fix_summary']['unknown_fixes']['successfully_fixed']}")
        print(f"   📈 Tasa de corrección: {report['fix_summary']['unknown_fixes']['fix_rate']}%")
        
        print("📊 TIPOS DE STATEMENTS DESPUÉS DE CORRECCIÓN:")
        for stmt_type, count in sorted(report['fix_summary']['statement_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {stmt_type}: {count}")
        
        print("======================================================================")
        print("🎊 ¡ÉXITO! Corrección de UNKNOWN completada")
        print("✅ IR corregido listo para conversión a SQL!")
        
    except Exception as e:
        print(f"❌ Error durante la corrección: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

