#!/usr/bin/env python3
"""
Verificar si hay GAPs relacionados con MOVE statements
"""

import json

def main():
    # Cargar IR
    with open('out/C1040_ir.json', 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    print("🔍 Verificando GAPs relacionados con MOVE statements:")
    print("=" * 60)
    
    move_gaps = []
    for proc in ir.get('procedures', []):
        for stmt in proc.get('statements', []):
            if stmt.get('op') == 'UNKNOWN':
                raw = stmt.get('raw', '')
                if 'MOVE' in raw.upper():
                    move_gaps.append({
                        'proc': proc.get('name', 'N/A'),
                        'raw': raw
                    })
    
    print(f"📊 GAPs relacionados con MOVE: {len(move_gaps)}")
    
    if move_gaps:
        print("\nGAPs encontrados:")
        for i, gap in enumerate(move_gaps[:10], 1):  # Mostrar solo los primeros 10
            print(f"{i}. {gap['proc']}: {gap['raw']}")
    else:
        print("✅ No hay GAPs relacionados con MOVE statements!")

if __name__ == "__main__":
    main()
