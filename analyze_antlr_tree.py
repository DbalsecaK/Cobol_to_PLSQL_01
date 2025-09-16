#!/usr/bin/env python3
"""
Analyze ANTLR Tree - Análisis completo del árbol ANTLR y su traducción al IR
"""

import json
import re
import sys
import os
from typing import Dict, List, Any
from antlr4 import *
from Cobol85Lexer import Cobol85Lexer
from Cobol85Parser import Cobol85Parser

def print_antlr_tree(node, indent=0, max_depth=10):
    """Imprimir el árbol ANTLR de forma legible"""
    if indent > max_depth:
        return
    
    prefix = "  " * indent
    
    # Obtener información del nodo
    node_type = type(node).__name__
    node_text = node.getText() if hasattr(node, 'getText') else str(node)
    
    # Limpiar texto para mostrar
    if len(node_text) > 100:
        node_text = node_text[:100] + "..."
    node_text = node_text.replace('\n', '\\n').replace('\r', '\\r')
    
    print(f"{prefix}{node_type}: '{node_text}'")
    
    # Recursivamente imprimir hijos
    if hasattr(node, 'children') and node.children:
        for child in node.children:
            print_antlr_tree(child, indent + 1, max_depth)

def analyze_antlr_to_ir_mapping(cobol_file_path: str):
    """Analizar cómo el árbol ANTLR se mapea al IR"""
    print(f"🔍 Analizando árbol ANTLR para: {cobol_file_path}")
    
    try:
        # Parsear con ANTLR
        input_stream = FileStream(cobol_file_path, encoding='utf-8')
        lexer = Cobol85Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = Cobol85Parser(stream)
        
        # Configurar parser
        parser.removeErrorListeners()
        
        # Parsear
        tree = parser.startRule()
        print("✅ Parsing ANTLR exitoso!")
        
        # Analizar el árbol
        print(f"\n🌳 ÁRBOL ANTLR (primeros 3 niveles):")
        print("=" * 80)
        print_antlr_tree(tree, max_depth=3)
        
        # Buscar nodos problemáticos
        print(f"\n🔍 BUSCANDO NODOS PROBLEMÁTICOS:")
        print("=" * 80)
        
        problematic_nodes = []
        _find_problematic_nodes(tree, problematic_nodes, 0, 10)
        
        print(f"📊 Nodos problemáticos encontrados: {len(problematic_nodes)}")
        for i, node_info in enumerate(problematic_nodes[:10]):  # Mostrar solo los primeros 10
            print(f"\n  {i+1}. {node_info['type']} (nivel {node_info['depth']}):")
            print(f"     Texto: '{node_info['text']}'")
            print(f"     Contexto: {node_info['context']}")
        
        return tree, problematic_nodes
        
    except Exception as e:
        print(f"❌ Error durante el análisis ANTLR: {e}")
        import traceback
        traceback.print_exc()
        return None, []

def _find_problematic_nodes(node, problematic_nodes, depth, max_depth):
    """Encontrar nodos que podrían causar elementos UNKNOWN"""
    if depth > max_depth:
        return
    
    node_type = type(node).__name__
    node_text = node.getText() if hasattr(node, 'getText') else str(node)
    
    # Criterios para nodos problemáticos
    is_problematic = False
    reason = ""
    
    if node_text and len(node_text.strip()) > 0:
        text_clean = node_text.strip()
        
        # Líneas que empiezan con TO
        if re.match(r'^\s*TO\s+', text_clean, re.IGNORECASE):
            is_problematic = True
            reason = "Línea que empieza con TO (posible continuación de MOVE)"
        
        # Directivas del preprocesador
        elif text_clean.startswith('@'):
            is_problematic = True
            reason = "Directiva del preprocesador"
        
        # Líneas con OF
        elif ' OF ' in text_clean.upper():
            is_problematic = True
            reason = "Campo calificado con OF"
        
        # Líneas muy cortas pero no vacías
        elif len(text_clean) < 10 and text_clean and not text_clean.startswith('*'):
            is_problematic = True
            reason = "Línea muy corta"
        
        # Nodos con texto que podría ser UNKNOWN
        elif any(keyword in text_clean.upper() for keyword in ['UNKNOWN', 'ERROR', 'MISSING']):
            is_problematic = True
            reason = "Contiene palabras problemáticas"
    
    if is_problematic:
        problematic_nodes.append({
            'type': node_type,
            'text': node_text[:100] + "..." if len(node_text) > 100 else node_text,
            'depth': depth,
            'reason': reason,
            'context': _get_node_context(node)
        })
    
    # Recursivamente buscar en hijos
    if hasattr(node, 'children') and node.children:
        for child in node.children:
            _find_problematic_nodes(child, problematic_nodes, depth + 1, max_depth)

def _get_node_context(node):
    """Obtener contexto de un nodo"""
    try:
        if hasattr(node, 'getSourceInterval'):
            interval = node.getSourceInterval()
            return f"Interval: {interval}"
        return "No context available"
    except:
        return "Context error"

def analyze_ir_unknown_sources(ir_file_path: str):
    """Analizar de dónde vienen los elementos UNKNOWN en el IR"""
    print(f"\n🔍 Analizando fuentes de UNKNOWN en IR: {ir_file_path}")
    
    with open(ir_file_path, 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    unknown_sources = []
    
    # Analizar statements en procedimientos
    for proc_idx, procedure in enumerate(ir.get("procedures", [])):
        proc_name = procedure.get("name", f"PROC_{proc_idx}")
        statements = procedure.get("statements", [])
        
        for stmt_idx, stmt in enumerate(statements):
            if stmt.get("op") == "UNKNOWN":
                unknown_sources.append({
                    "procedure": proc_name,
                    "statement_index": stmt_idx,
                    "raw": stmt.get("raw", ""),
                    "details": stmt.get("details", {}),
                    "source": "procedure_statements"
                })
    
    # Analizar statements globales
    for stmt_idx, stmt in enumerate(ir.get("statements", [])):
        if stmt.get("op") == "UNKNOWN":
            unknown_sources.append({
                "procedure": "GLOBAL",
                "statement_index": stmt_idx,
                "raw": stmt.get("raw", ""),
                "details": stmt.get("details", {}),
                "source": "global_statements"
            })
    
    print(f"📊 UNKNOWN encontrados: {len(unknown_sources)}")
    
    # Agrupar por patrón
    patterns = {}
    for unknown in unknown_sources:
        raw = unknown["raw"]
        
        if raw.strip().startswith("TO "):
            pattern = "MOVE_CONTINUATION"
        elif raw.strip().startswith("@"):
            pattern = "PREPROCESSOR_DIRECTIVE"
        elif " OF " in raw.upper():
            pattern = "QUALIFIED_FIELD"
        elif len(raw.strip()) < 10:
            pattern = "SHORT_LINE"
        else:
            pattern = "OTHER"
        
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(unknown)
    
    print(f"\n📋 PATRONES DE UNKNOWN:")
    for pattern, unknowns in patterns.items():
        print(f"  {pattern}: {len(unknowns)}")
        for unknown in unknowns[:3]:  # Mostrar primeros 3 ejemplos
            print(f"    '{unknown['raw']}'")
        if len(unknowns) > 3:
            print(f"    ... y {len(unknowns) - 3} más")
    
    return unknown_sources, patterns

def generate_antlr_fix_recommendations(problematic_nodes: List[Dict], unknown_patterns: Dict):
    """Generar recomendaciones específicas basadas en el análisis ANTLR"""
    print(f"\n💡 RECOMENDACIONES BASADAS EN ANÁLISIS ANTLR:")
    print("=" * 80)
    
    recommendations = []
    
    # Analizar nodos problemáticos del árbol ANTLR
    to_nodes = [n for n in problematic_nodes if "TO" in n['reason']]
    if to_nodes:
        recommendations.append({
            "issue": "ANTLR_TO_NODES",
            "count": len(to_nodes),
            "description": "Nodos ANTLR que contienen líneas que empiezan con TO",
            "antlr_fix": "Modificar el visitor para reconocer continuaciones de MOVE",
            "parser_fix": "Agregar reconocimiento de líneas TO en _parse_cobol_statement"
        })
    
    preprocessor_nodes = [n for n in problematic_nodes if "preprocesador" in n['reason']]
    if preprocessor_nodes:
        recommendations.append({
            "issue": "ANTLR_PREPROCESSOR_NODES",
            "count": len(preprocessor_nodes),
            "description": "Nodos ANTLR que contienen directivas del preprocesador",
            "antlr_fix": "Crear reglas específicas para directivas @ en la gramática",
            "parser_fix": "Agregar reconocimiento de directivas @ en _parse_cobol_statement"
        })
    
    # Analizar patrones de UNKNOWN
    for pattern, unknowns in unknown_patterns.items():
        if pattern == "MOVE_CONTINUATION":
            recommendations.append({
                "issue": "MOVE_CONTINUATION_PATTERN",
                "count": len(unknowns),
                "description": "Líneas que empiezan con TO no reconocidas como continuaciones",
                "antlr_fix": "Modificar la gramática para manejar MOVE multilínea",
                "parser_fix": "Implementar lógica de continuación de statements"
            })
        elif pattern == "PREPROCESSOR_DIRECTIVE":
            recommendations.append({
                "issue": "PREPROCESSOR_PATTERN",
                "count": len(unknowns),
                "description": "Directivas del preprocesador no reconocidas",
                "antlr_fix": "Agregar reglas para directivas @ en la gramática",
                "parser_fix": "Agregar patrones regex para @DEFINE, @CTRLERR, etc."
            })
    
    for rec in recommendations:
        print(f"\n🔧 {rec['issue']} ({rec['count']} casos):")
        print(f"   Descripción: {rec['description']}")
        print(f"   Fix ANTLR: {rec['antlr_fix']}")
        print(f"   Fix Parser: {rec['parser_fix']}")
    
    return recommendations

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python analyze_antlr_tree.py archivo.cob")
        sys.exit(1)
    
    cobol_file = sys.argv[1]
    
    if not os.path.exists(cobol_file):
        print(f"❌ Error: Archivo COBOL no encontrado: {cobol_file}")
        sys.exit(1)
    
    print("======================================================================")
    print("🌳 ANALYZE ANTLR TREE - Análisis completo del árbol ANTLR")
    print(f"📁 Archivo COBOL: {cobol_file}")
    print("🎯 Analizando árbol ANTLR y mapeo al IR para identificar UNKNOWN")
    print("======================================================================")
    
    try:
        # Analizar árbol ANTLR
        tree, problematic_nodes = analyze_antlr_to_ir_mapping(cobol_file)
        
        # Analizar IR existente
        base_name = os.path.splitext(os.path.basename(cobol_file))[0]
        ir_file = f"out/{base_name}_ir_direct.json"
        
        unknown_sources = []
        unknown_patterns = {}
        
        if os.path.exists(ir_file):
            unknown_sources, unknown_patterns = analyze_ir_unknown_sources(ir_file)
        else:
            print(f"⚠️  Archivo IR no encontrado: {ir_file}")
        
        # Generar recomendaciones
        recommendations = generate_antlr_fix_recommendations(problematic_nodes, unknown_patterns)
        
        print(f"\n======================================================================")
        print("📊 RESUMEN DEL ANÁLISIS ANTLR")
        print("======================================================================")
        print(f"🌳 Nodos problemáticos en árbol ANTLR: {len(problematic_nodes)}")
        print(f"❌ UNKNOWN en IR: {len(unknown_sources)}")
        print(f"📋 Patrones de UNKNOWN: {len(unknown_patterns)}")
        print(f"💡 Recomendaciones: {len(recommendations)}")
        print("======================================================================")
        print("🎊 Análisis ANTLR completado - Revisar recomendaciones arriba")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

