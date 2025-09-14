#!/usr/bin/env python3
"""
Verificar el MOVE específico mencionado por el usuario
"""

import json

def main():
    # Cargar IR
    with open('out/C1040_ir.json', 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    # Buscar el MOVE específico
    target_move = "FEM-MAQUINA"
    target_dest = "FEM-OPERACION"
    
    print(f"🔍 Buscando MOVE statements con {target_move} y {target_dest}:")
    print("=" * 60)
    
    found_moves = []
    for proc in ir.get('procedures', []):
        for stmt in proc.get('statements', []):
            if stmt.get('op') == 'MOVE':
                src = stmt.get('src', '')
                dst = stmt.get('dst', '')
                if target_move in src and target_dest in dst:
                    found_moves.append({
                        'proc': proc.get('name', 'N/A'),
                        'stmt': stmt
                    })
    
    print(f"📊 Encontrados {len(found_moves)} MOVE statements:")
    
    for i, move in enumerate(found_moves, 1):
        stmt = move['stmt']
        print(f"\n{i}. Procedimiento: {move['proc']}")
        print(f"   COBOL: {stmt.get('raw', 'N/A')}")
        print(f"   Fuente: {stmt.get('src', 'N/A')}")
        print(f"   Destino: {stmt.get('dst', 'N/A')}")
        
        # Simular conversión
        from enhanced_converter import EnhancedCobolConverter
        converter = EnhancedCobolConverter()
        converted = converter.convert_move_statement_enhanced(stmt)
        print(f"   PL/SQL:")
        for line in converted.split('\n'):
            print(f"      {line}")

if __name__ == "__main__":
    main()
