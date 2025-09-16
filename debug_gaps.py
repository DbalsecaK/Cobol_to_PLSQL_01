#!/usr/bin/env python3
"""
Debug: Analizar qué statements están siendo clasificados como UNKNOWN
"""

import json

def debug_gaps():
    """Analiza el IR para ver qué está siendo clasificado como UNKNOWN"""
    
    try:
        with open('out/CS63_ir.json', 'r', encoding='utf-8') as f:
            ir = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró out/CS63_ir.json")
        return
    
    unknown_statements = []
    all_ops = {}
    
    for proc in ir.get("procedures", []):
        for stmt in proc.get("statements", []):
            op = stmt.get("op", "")
            all_ops[op] = all_ops.get(op, 0) + 1
            
            if op == "UNKNOWN":
                unknown_statements.append({
                    "content": stmt.get("content", ""),
                    "raw": stmt.get("raw", "")
                })
    
    print("📊 ESTADÍSTICAS POR TIPO DE OPERACIÓN:")
    print("=" * 50)
    for op, count in sorted(all_ops.items(), key=lambda x: x[1], reverse=True):
        print(f"  {op}: {count}")
    
    print(f"\n❌ STATEMENTS UNKNOWN ({len(unknown_statements)}):")
    print("=" * 50)
    for i, stmt in enumerate(unknown_statements[:20]):  # Mostrar solo los primeros 20
        content = stmt.get("content", "")[:60]
        raw = stmt.get("raw", "")[:60] 
        print(f"  {i+1:2d}. Content: {content}")
        print(f"      Raw: {raw}")
        print()
    
    if len(unknown_statements) > 20:
        print(f"... y {len(unknown_statements) - 20} más")

if __name__ == "__main__":
    debug_gaps()



