#!/usr/bin/env python3
"""
Verificar MOVE statements en el IR generado
"""

import json

def main():
    # Cargar IR
    with open('out/C1040_ir.json', 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    # Buscar MOVE statements
    moves = []
    for proc in ir.get('procedures', []):
        for stmt in proc.get('statements', []):
            if stmt.get('op') in ['MOVE', 'MOVE_CORRESPONDING']:
                moves.append(stmt)
    
    print(f"📊 MOVE statements encontrados: {len(moves)}")
    print("=" * 50)
    
    # Mostrar primeros 10
    for i, stmt in enumerate(moves[:10], 1):
        print(f"{i}. {stmt.get('raw', 'N/A')}")
        print(f"   Op: {stmt.get('op')}")
        print(f"   Src: {stmt.get('src', stmt.get('from', 'N/A'))}")
        print(f"   Dst: {stmt.get('dst', stmt.get('to', 'N/A'))}")
        print()

if __name__ == "__main__":
    main()
