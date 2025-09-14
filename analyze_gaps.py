#!/usr/bin/env python3
"""
Análisis completo de GAPs en C1040.cob
"""

import json
import re
from collections import Counter

def main():
    # Cargar IR
    with open('out/C1040_ir.json', 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    print("📊 ANÁLISIS COMPLETO DE GAPs EN C1040.COB")
    print("=" * 60)
    
    # Recopilar todos los GAPs
    gaps = []
    procedures_with_gaps = {}
    
    for proc in ir.get('procedures', []):
        proc_name = proc.get('name', 'N/A')
        proc_gaps = []
        
        for stmt in proc.get('statements', []):
            if stmt.get('op') == 'UNKNOWN':
                raw = stmt.get('raw', '')
                gaps.append({
                    'proc': proc_name,
                    'raw': raw,
                    'type': classify_gap(raw)
                })
                proc_gaps.append(raw)
        
        if proc_gaps:
            procedures_with_gaps[proc_name] = proc_gaps
    
    # Estadísticas generales
    total_gaps = len(gaps)
    total_procedures = len(ir.get('procedures', []))
    procedures_with_gaps_count = len(procedures_with_gaps)
    
    print(f"📈 ESTADÍSTICAS GENERALES:")
    print(f"   Total de GAPs: {total_gaps}")
    print(f"   Total de procedimientos: {total_procedures}")
    print(f"   Procedimientos con GAPs: {procedures_with_gaps_count}")
    print(f"   Porcentaje de cobertura: {((total_procedures - procedures_with_gaps_count) / total_procedures * 100):.1f}%")
    
    # Clasificación de GAPs por tipo
    gap_types = Counter([gap['type'] for gap in gaps])
    
    print(f"\n🔍 CLASIFICACIÓN DE GAPs POR TIPO:")
    print("-" * 40)
    for gap_type, count in gap_types.most_common():
        percentage = (count / total_gaps * 100) if total_gaps > 0 else 0
        print(f"   {gap_type}: {count} ({percentage:.1f}%)")
    
    # Top 10 procedimientos con más GAPs
    proc_gap_counts = {proc: len(gaps) for proc, gaps in procedures_with_gaps.items()}
    top_procedures = sorted(proc_gap_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n📋 TOP 10 PROCEDIMIENTOS CON MÁS GAPs:")
    print("-" * 50)
    for i, (proc, count) in enumerate(top_procedures, 1):
        print(f"   {i:2d}. {proc}: {count} GAPs")
    
    # Ejemplos de GAPs por tipo
    print(f"\n📝 EJEMPLOS DE GAPs POR TIPO:")
    print("-" * 40)
    
    gap_examples = {}
    for gap in gaps:
        gap_type = gap['type']
        if gap_type not in gap_examples:
            gap_examples[gap_type] = []
        if len(gap_examples[gap_type]) < 3:  # Máximo 3 ejemplos por tipo
            gap_examples[gap_type].append(gap['raw'])
    
    for gap_type, examples in gap_examples.items():
        print(f"\n   {gap_type}:")
        for example in examples:
            print(f"      - {example}")
    
    # Análisis de patrones comunes
    print(f"\n🔍 ANÁLISIS DE PATRONES COMUNES:")
    print("-" * 40)
    
    # Palabras clave más comunes en GAPs
    all_gap_text = ' '.join([gap['raw'] for gap in gaps])
    words = re.findall(r'\b[A-Z][A-Z0-9-]+\b', all_gap_text)
    word_counts = Counter(words)
    
    print("   Palabras clave más frecuentes en GAPs:")
    for word, count in word_counts.most_common(10):
        print(f"      {word}: {count}")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES PARA REDUCIR GAPs:")
    print("-" * 50)
    
    if gap_types.get('PERFORM', 0) > 0:
        print("   • Implementar parsing mejorado para PERFORM statements")
    
    if gap_types.get('IF/EVALUATE', 0) > 0:
        print("   • Mejorar manejo de estructuras de control IF/EVALUATE")
    
    if gap_types.get('SQL', 0) > 0:
        print("   • Expandir soporte para sentencias SQL complejas")
    
    if gap_types.get('FILE_OPERATIONS', 0) > 0:
        print("   • Implementar operaciones de archivo (READ, WRITE, etc.)")
    
    if gap_types.get('STRING_OPERATIONS', 0) > 0:
        print("   • Agregar soporte para operaciones de string (STRING, UNSTRING)")
    
    print("   • Implementar parsing de expresiones aritméticas complejas")
    print("   • Agregar soporte para CALL statements")
    print("   • Mejorar manejo de EXIT statements")

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
