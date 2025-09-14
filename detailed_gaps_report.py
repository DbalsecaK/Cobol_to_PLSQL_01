#!/usr/bin/env python3
"""
Reporte detallado de GAPs con ejemplos específicos
"""

import json
import re

def main():
    # Cargar IR
    with open('out/C1040_ir.json', 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    print("📋 REPORTE DETALLADO DE GAPs EN C1040.COB")
    print("=" * 70)
    
    # Recopilar GAPs por tipo
    gaps_by_type = {}
    
    for proc in ir.get('procedures', []):
        proc_name = proc.get('name', 'N/A')
        
        for stmt in proc.get('statements', []):
            if stmt.get('op') == 'UNKNOWN':
                raw = stmt.get('raw', '')
                gap_type = classify_gap(raw)
                
                if gap_type not in gaps_by_type:
                    gaps_by_type[gap_type] = []
                
                gaps_by_type[gap_type].append({
                    'proc': proc_name,
                    'raw': raw
                })
    
    # Reporte detallado por tipo
    for gap_type, gaps in gaps_by_type.items():
        print(f"\n🔍 {gap_type} ({len(gaps)} GAPs)")
        print("-" * 50)
        
        # Mostrar ejemplos únicos
        unique_examples = list(set([gap['raw'] for gap in gaps]))
        
        for i, example in enumerate(unique_examples[:5], 1):  # Máximo 5 ejemplos
            print(f"   {i}. {example}")
        
        if len(unique_examples) > 5:
            print(f"   ... y {len(unique_examples) - 5} más")
    
    # Análisis de impacto
    print(f"\n📊 ANÁLISIS DE IMPACTO:")
    print("-" * 30)
    
    total_gaps = sum(len(gaps) for gaps in gaps_by_type.values())
    
    for gap_type, gaps in sorted(gaps_by_type.items(), key=lambda x: len(x[1]), reverse=True):
        percentage = (len(gaps) / total_gaps * 100) if total_gaps > 0 else 0
        print(f"   {gap_type}: {len(gaps)} GAPs ({percentage:.1f}%)")
    
    # Prioridades de implementación
    print(f"\n🎯 PRIORIDADES DE IMPLEMENTACIÓN:")
    print("-" * 40)
    
    priorities = [
        ("IF/EVALUATE", "Crítico - Estructuras de control fundamentales"),
        ("ARITHMETIC", "Alto - Operaciones matemáticas básicas"),
        ("FILE_OPERATIONS", "Alto - Operaciones de archivo esenciales"),
        ("STRING_OPERATIONS", "Medio - Manipulación de strings"),
        ("SET", "Medio - Asignación de valores booleanos"),
        ("OTHER", "Bajo - Casos específicos y edge cases")
    ]
    
    for gap_type, priority in priorities:
        if gap_type in gaps_by_type:
            count = len(gaps_by_type[gap_type])
            print(f"   {priority}: {count} GAPs")

def classify_gap(raw_text):
    """Clasifica el tipo de GAP basado en el contenido"""
    raw_upper = raw_text.upper()
    
    # PERFORM statements
    if re.match(r'PERFORM\s+', raw_upper):
        return 'PERFORM'
    
    # IF/EVALUATE statements
    if re.match(r'(IF|EVALUATE|WHEN|ELSE)\s+', raw_upper):
        return 'IF/EVALUATE'
    
    # SQL statements
    if re.match(r'(EXEC\s+SQL|SELECT|INSERT|UPDATE|DELETE|DECLARE)\s+', raw_upper):
        return 'SQL'
    
    # File operations
    if re.match(r'(READ|WRITE|REWRITE|DELETE|OPEN|CLOSE)\s+', raw_upper):
        return 'FILE_OPERATIONS'
    
    # String operations
    if re.match(r'(STRING|UNSTRING|INSPECT)\s+', raw_upper):
        return 'STRING_OPERATIONS'
    
    # Arithmetic operations
    if re.match(r'(ADD|SUBTRACT|MULTIPLY|DIVIDE|COMPUTE)\s+', raw_upper):
        return 'ARITHMETIC'
    
    # CALL statements
    if re.match(r'CALL\s+', raw_upper):
        return 'CALL'
    
    # EXIT statements
    if re.match(r'EXIT\s+', raw_upper):
        return 'EXIT'
    
    # ACCEPT/DISPLAY
    if re.match(r'(ACCEPT|DISPLAY)\s+', raw_upper):
        return 'I/O_OPERATIONS'
    
    # SET statements
    if re.match(r'SET\s+', raw_upper):
        return 'SET'
    
    # STOP statements
    if re.match(r'STOP\s+', raw_upper):
        return 'STOP'
    
    # GO TO statements
    if re.match(r'GO\s+TO\s+', raw_upper):
        return 'GO_TO'
    
    # Default classification
    return 'OTHER'

if __name__ == "__main__":
    main()
