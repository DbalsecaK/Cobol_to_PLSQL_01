#!/usr/bin/env python3
"""
Quick Unknown Check - Verificación rápida de elementos UNKNOWN
"""

import json
import re
import sys
import os

def quick_unknown_analysis(ir_file_path: str):
    """Análisis rápido de elementos UNKNOWN"""
    print(f"🔍 Análisis rápido de UNKNOWN en: {ir_file_path}")
    
    try:
        with open(ir_file_path, 'r', encoding='utf-8') as f:
            ir = json.load(f)
        
        unknown_count = 0
        unknown_examples = []
        
        # Buscar UNKNOWN en procedimientos
        for procedure in ir.get("procedures", []):
            for stmt in procedure.get("statements", []):
                if stmt.get("op") == "UNKNOWN":
                    unknown_count += 1
                    if len(unknown_examples) < 10:  # Solo primeros 10 ejemplos
                        unknown_examples.append(stmt.get("raw", ""))
        
        print(f"❌ Total UNKNOWN encontrados: {unknown_count}")
        
        if unknown_examples:
            print(f"\n📋 Ejemplos de UNKNOWN:")
            for i, example in enumerate(unknown_examples, 1):
                print(f"  {i}. '{example}'")
        
        # Analizar patrones rápidamente
        patterns = {}
        for procedure in ir.get("procedures", []):
            for stmt in procedure.get("statements", []):
                if stmt.get("op") == "UNKNOWN":
                    raw = stmt.get("raw", "")
                    
                    if raw.strip().startswith("TO "):
                        pattern = "MOVE_CONTINUATION"
                    elif raw.strip().startswith("@"):
                        pattern = "PREPROCESSOR_DIRECTIVE"
                    elif " OF " in raw.upper():
                        pattern = "QUALIFIED_FIELD"
                    else:
                        pattern = "OTHER"
                    
                    patterns[pattern] = patterns.get(pattern, 0) + 1
        
        print(f"\n📊 Patrones de UNKNOWN:")
        for pattern, count in patterns.items():
            print(f"  {pattern}: {count}")
        
        return unknown_count, patterns
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0, {}

def main():
    if len(sys.argv) != 2:
        print("Uso: python quick_unknown_check.py archivo_ir.json")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    
    if not os.path.exists(ir_file):
        print(f"❌ Archivo no encontrado: {ir_file}")
        sys.exit(1)
    
    print("🔍 QUICK UNKNOWN CHECK")
    print("=" * 50)
    
    unknown_count, patterns = quick_unknown_analysis(ir_file)
    
    print(f"\n✅ Análisis completado en segundos")
    print(f"📊 UNKNOWN: {unknown_count}")
    print(f"📋 Patrones: {len(patterns)}")

if __name__ == "__main__":
    main()

