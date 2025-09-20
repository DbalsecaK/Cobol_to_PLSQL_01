#!/usr/bin/env python3
"""
Script para verificar el IR en detalle
"""

import json

def check_ir_detailed():
    """Verificar el IR en detalle"""
    
    try:
        # Leer el IR
        with open('out/C1040_ir_clean.json', 'r', encoding='utf-8') as f:
            ir_data = json.load(f)
        
        print('✅ IR cargado exitosamente')
        print(f'Programa: {ir_data.get("program", "UNKNOWN")}')
        print(f'Statements principales: {len(ir_data.get("statements", []))}')
        print(f'Procedures: {len(ir_data.get("procedures", []))}')
        print(f'Variables: {len(ir_data.get("variables", []))}')
        
        # Verificar statements en procedimientos
        procedures = ir_data.get("procedures", [])
        total_statements_in_procedures = 0
        
        for proc in procedures:
            proc_name = proc.get("name", "UNKNOWN")
            proc_statements = proc.get("statements", [])
            total_statements_in_procedures += len(proc_statements)
            print(f'  {proc_name}: {len(proc_statements)} statements')
        
        print(f'Total statements en procedimientos: {total_statements_in_procedures}')
        
        # Verificar si hay cobol_statements
        cobol_statements = ir_data.get("cobol_statements", [])
        print(f'COBOL statements: {len(cobol_statements)}')
        
        # Verificar si hay perform_statements
        perform_statements = ir_data.get("perform_statements", [])
        print(f'PERFORM statements: {len(perform_statements)}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error leyendo IR: {e}')
        return False

if __name__ == "__main__":
    check_ir_detailed()
