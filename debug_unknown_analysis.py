#!/usr/bin/env python3
"""
Debug Unknown Analysis - Análisis profundo de elementos UNKNOWN en el IR
"""

import json
import re
import sys
import os
from typing import Dict, List, Any

def analyze_unknown_statements(ir_file_path: str):
    """Analizar elementos UNKNOWN en detalle"""
    print(f"🔍 Analizando elementos UNKNOWN en: {ir_file_path}")
    
    # Cargar IR
    with open(ir_file_path, 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    unknown_statements = []
    all_statement_types = {}
    
    # Analizar statements en procedimientos
    for proc_idx, procedure in enumerate(ir.get("procedures", [])):
        proc_name = procedure.get("name", f"PROC_{proc_idx}")
        statements = procedure.get("statements", [])
        
        for stmt_idx, stmt in enumerate(statements):
            op = stmt.get("op", "UNKNOWN")
            raw = stmt.get("raw", "")
            
            # Contar tipos de statements
            all_statement_types[op] = all_statement_types.get(op, 0) + 1
            
            # Recopilar UNKNOWN
            if op == "UNKNOWN":
                unknown_statements.append({
                    "procedure": proc_name,
                    "statement_index": stmt_idx,
                    "raw": raw,
                    "details": stmt.get("details", {}),
                    "context": _get_context(statements, stmt_idx)
                })
    
    # Mostrar estadísticas
    print(f"\n📊 ESTADÍSTICAS DE STATEMENTS:")
    print("=" * 60)
    for stmt_type, count in sorted(all_statement_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {stmt_type}: {count}")
    
    print(f"\n❌ ELEMENTOS UNKNOWN ENCONTRADOS: {len(unknown_statements)}")
    print("=" * 60)
    
    # Analizar patrones en UNKNOWN
    unknown_patterns = {}
    for unknown in unknown_statements:
        raw = unknown["raw"]
        
        # Clasificar por patrón
        if raw.strip().startswith("TO "):
            pattern = "MOVE_CONTINUATION"
        elif raw.strip().startswith("@"):
            pattern = "PREPROCESSOR_DIRECTIVE"
        elif " OF " in raw.upper():
            pattern = "QUALIFIED_FIELD"
        elif len(raw.strip()) < 10:
            pattern = "SHORT_LINE"
        elif raw.strip().endswith("."):
            pattern = "END_STATEMENT"
        else:
            pattern = "OTHER"
        
        unknown_patterns[pattern] = unknown_patterns.get(pattern, 0) + 1
    
    print(f"\n🔍 PATRONES EN ELEMENTOS UNKNOWN:")
    print("=" * 60)
    for pattern, count in sorted(unknown_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern}: {count}")
    
    # Mostrar ejemplos de cada patrón
    print(f"\n📋 EJEMPLOS POR PATRÓN:")
    print("=" * 60)
    
    examples_by_pattern = {}
    for unknown in unknown_statements:
        raw = unknown["raw"]
        
        if raw.strip().startswith("TO "):
            pattern = "MOVE_CONTINUATION"
        elif raw.strip().startswith("@"):
            pattern = "PREPROCESSOR_DIRECTIVE"
        elif " OF " in raw.upper():
            pattern = "QUALIFIED_FIELD"
        elif len(raw.strip()) < 10:
            pattern = "SHORT_LINE"
        elif raw.strip().endswith("."):
            pattern = "END_STATEMENT"
        else:
            pattern = "OTHER"
        
        if pattern not in examples_by_pattern:
            examples_by_pattern[pattern] = []
        if len(examples_by_pattern[pattern]) < 3:  # Solo 3 ejemplos por patrón
            examples_by_pattern[pattern].append(raw)
    
    for pattern, examples in examples_by_pattern.items():
        print(f"\n  {pattern}:")
        for example in examples:
            print(f"    '{example}'")
    
    return unknown_statements, all_statement_types

def _get_context(statements: List[Dict], current_idx: int, context_size: int = 2) -> Dict[str, str]:
    """Obtener contexto alrededor de un statement"""
    context = {
        "before": [],
        "after": []
    }
    
    # Statements anteriores
    start_idx = max(0, current_idx - context_size)
    for i in range(start_idx, current_idx):
        if i < len(statements):
            context["before"].append(statements[i].get("raw", "")[:50])
    
    # Statements posteriores
    end_idx = min(len(statements), current_idx + context_size + 1)
    for i in range(current_idx + 1, end_idx):
        if i < len(statements):
            context["after"].append(statements[i].get("raw", "")[:50])
    
    return context

def analyze_cobol_source_patterns(cobol_file_path: str):
    """Analizar patrones en el archivo COBOL fuente"""
    print(f"\n🔍 Analizando patrones en archivo COBOL: {cobol_file_path}")
    
    with open(cobol_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    patterns = {
        "TO_lines": [],
        "AT_lines": [],
        "OF_lines": [],
        "short_lines": [],
        "preprocessor_lines": []
    }
    
    for line_num, line in enumerate(lines, 1):
        line_clean = line.strip()
        
        if not line_clean or line_clean.startswith('*'):
            continue
        
        # Líneas que empiezan con TO
        if re.match(r'^\s*TO\s+', line_clean, re.IGNORECASE):
            patterns["TO_lines"].append((line_num, line_clean))
        
        # Líneas que empiezan con @
        if line_clean.startswith('@'):
            patterns["preprocessor_lines"].append((line_num, line_clean))
        
        # Líneas con OF
        if ' OF ' in line_clean.upper():
            patterns["OF_lines"].append((line_num, line_clean))
        
        # Líneas muy cortas
        if len(line_clean) < 10 and line_clean:
            patterns["short_lines"].append((line_num, line_clean))
    
    print(f"\n📊 PATRONES EN ARCHIVO COBOL:")
    print("=" * 60)
    for pattern_name, pattern_list in patterns.items():
        print(f"  {pattern_name}: {len(pattern_list)}")
        if pattern_list and len(pattern_list) <= 5:  # Mostrar ejemplos si son pocos
            for line_num, line in pattern_list:
                print(f"    L{line_num}: '{line}'")
        elif pattern_list:
            print(f"    Ejemplos:")
            for line_num, line in pattern_list[:3]:
                print(f"      L{line_num}: '{line}'")
            if len(pattern_list) > 3:
                print(f"      ... y {len(pattern_list) - 3} más")
    
    return patterns

def generate_fix_recommendations(unknown_statements: List[Dict], cobol_patterns: Dict):
    """Generar recomendaciones para corregir elementos UNKNOWN"""
    print(f"\n💡 RECOMENDACIONES PARA CORREGIR UNKNOWN:")
    print("=" * 60)
    
    recommendations = []
    
    # Analizar continuaciones de MOVE
    move_continuations = [u for u in unknown_statements if u["raw"].strip().startswith("TO ")]
    if move_continuations:
        recommendations.append({
            "issue": "MOVE_CONTINUATION",
            "count": len(move_continuations),
            "fix": "Agregar reconocimiento de líneas que empiezan con 'TO' como continuaciones de MOVE",
            "code": """
elif re.match(r'^\\s*TO\\s+', line, re.IGNORECASE):
    statement_type = "MOVE_CONTINUATION"
    details = {"continuation": True, "move_target": line.strip()}
"""
        })
    
    # Analizar directivas del preprocesador
    preprocessor_directives = [u for u in unknown_statements if u["raw"].strip().startswith("@")]
    if preprocessor_directives:
        recommendations.append({
            "issue": "PREPROCESSOR_DIRECTIVE",
            "count": len(preprocessor_directives),
            "fix": "Agregar reconocimiento de directivas del preprocesador (@DEFINE, @CTRLERR, etc.)",
            "code": """
elif re.match(r'^\\s*@\\w+\\s*\\([^)]*\\)', line, re.IGNORECASE):
    statement_type = "PREPROCESSOR_DIRECTIVE"
    details = {"directive": True, "content": line.strip()}
"""
        })
    
    # Analizar campos calificados
    qualified_fields = [u for u in unknown_statements if " OF " in u["raw"].upper()]
    if qualified_fields:
        recommendations.append({
            "issue": "QUALIFIED_FIELD",
            "count": len(qualified_fields),
            "fix": "Agregar reconocimiento de campos calificados (FIELD OF GROUP)",
            "code": """
elif " OF " in line_upper:
    statement_type = "QUALIFIED_FIELD"
    details = {"qualified": True, "field": line.strip()}
"""
        })
    
    for rec in recommendations:
        print(f"\n🔧 {rec['issue']} ({rec['count']} casos):")
        print(f"   Problema: {rec['fix']}")
        print(f"   Solución:")
        print(f"   {rec['code']}")
    
    return recommendations

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python debug_unknown_analysis.py archivo_ir.json")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    
    if not os.path.exists(ir_file):
        print(f"❌ Error: Archivo IR no encontrado: {ir_file}")
        sys.exit(1)
    
    print("======================================================================")
    print("🔍 DEBUG UNKNOWN ANALYSIS - Análisis profundo de elementos UNKNOWN")
    print(f"📁 Archivo IR: {ir_file}")
    print("🎯 Identificando patrones y generando recomendaciones de corrección")
    print("======================================================================")
    
    try:
        # Analizar IR
        unknown_statements, all_types = analyze_unknown_statements(ir_file)
        
        # Analizar archivo COBOL fuente si existe
        base_name = os.path.splitext(os.path.basename(ir_file))[0]
        if base_name.endswith("_ir_direct"):
            base_name = base_name[:-10]
        
        cobol_file = f"samples/{base_name}.cob"
        cobol_patterns = {}
        if os.path.exists(cobol_file):
            cobol_patterns = analyze_cobol_source_patterns(cobol_file)
        
        # Generar recomendaciones
        recommendations = generate_fix_recommendations(unknown_statements, cobol_patterns)
        
        print(f"\n======================================================================")
        print("📊 RESUMEN DEL ANÁLISIS")
        print("======================================================================")
        print(f"❌ Total UNKNOWN: {len(unknown_statements)}")
        print(f"📋 Total tipos de statements: {len(all_types)}")
        print(f"💡 Recomendaciones generadas: {len(recommendations)}")
        print("======================================================================")
        print("🎊 Análisis completado - Revisar recomendaciones arriba")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

