#!/usr/bin/env python3
"""
Verificar que IF/EVALUATE se están procesando correctamente en C1040.cob
"""

import json

def main():
    # Cargar IR
    with open('out/C1040_ir.json', 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    print("🔍 Verificando IF/EVALUATE en C1040.cob:")
    print("=" * 50)
    
    # Buscar IF/EVALUATE/WHEN statements
    if_statements = []
    evaluate_statements = []
    when_statements = []
    
    for proc in ir.get('procedures', []):
        for stmt in proc.get('statements', []):
            if stmt.get('op') == 'IF':
                if_statements.append(stmt)
            elif stmt.get('op') == 'EVALUATE':
                evaluate_statements.append(stmt)
            elif stmt.get('op') == 'WHEN':
                when_statements.append(stmt)
    
    print(f"📊 IF/EVALUATE/WHEN statements procesados:")
    print(f"   IF statements: {len(if_statements)}")
    print(f"   EVALUATE statements: {len(evaluate_statements)}")
    print(f"   WHEN statements: {len(when_statements)}")
    print(f"   Total: {len(if_statements) + len(evaluate_statements) + len(when_statements)}")
    
    # Verificar que no hay GAPs de IF/EVALUATE
    if_evaluate_gaps = []
    for proc in ir.get('procedures', []):
        for stmt in proc.get('statements', []):
            if stmt.get('op') == 'UNKNOWN':
                raw = stmt.get('raw', '')
                if any(keyword in raw.upper() for keyword in ['IF ', 'EVALUATE ', 'WHEN ']):
                    if_evaluate_gaps.append(stmt)
    
    print(f"\n📊 GAPs de IF/EVALUATE restantes: {len(if_evaluate_gaps)}")
    
    if len(if_evaluate_gaps) == 0:
        print("✅ ¡Todos los IF/EVALUATE/WHEN statements se están procesando correctamente!")
    else:
        print("❌ Aún hay GAPs de IF/EVALUATE:")
        for gap in if_evaluate_gaps[:5]:  # Mostrar máximo 5
            print(f"   - {gap.get('raw', 'N/A')}")
    
    # Mostrar algunos ejemplos de IF procesados
    print(f"\n📝 Ejemplos de IF statements procesados:")
    for i, stmt in enumerate(if_statements[:5], 1):
        print(f"   {i}. {stmt.get('raw', 'N/A')}")
        print(f"      Condición: {stmt.get('condition', 'N/A')}")

if __name__ == "__main__":
    main()
