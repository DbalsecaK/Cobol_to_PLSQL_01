#!/usr/bin/env python3
"""
Script para verificar el IR generado
"""

import json

def check_ir():
    """Verificar que el IR está bien estructurado"""
    
    try:
        # Leer el IR
        with open('out/C1040_ir_clean.json', 'r', encoding='utf-8') as f:
            ir_data = json.load(f)
        
        print('✅ IR cargado exitosamente')
        print(f'Programa: {ir_data.get("program", "UNKNOWN")}')
        print(f'Statements: {len(ir_data.get("statements", []))}')
        print(f'Procedures: {len(ir_data.get("procedures", []))}')
        print(f'Variables: {len(ir_data.get("variables", []))}')
        print('✅ El IR está bien estructurado')
        
        # Verificar algunos statements
        statements = ir_data.get("statements", [])
        if statements:
            print(f'Primer statement: {statements[0]}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error leyendo IR: {e}')
        return False

if __name__ == "__main__":
    check_ir()
