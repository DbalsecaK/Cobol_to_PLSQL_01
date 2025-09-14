#!/usr/bin/env python3
"""
Analizar patrones de IF/EVALUATE en C1040.cob
"""

import json
import re

def main():
    # Cargar IR
    with open('out/C1040_ir.json', 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    print("🔍 ANÁLISIS DE PATRONES IF/EVALUATE EN C1040.COB")
    print("=" * 60)
    
    # Recopilar todos los GAPs de IF/EVALUATE
    if_evaluate_gaps = []
    
    for proc in ir.get('procedures', []):
        proc_name = proc.get('name', 'N/A')
        
        for stmt in proc.get('statements', []):
            if stmt.get('op') == 'UNKNOWN':
                raw = stmt.get('raw', '')
                if re.match(r'(IF|EVALUATE|WHEN|ELSE)\s+', raw.upper()):
                    if_evaluate_gaps.append({
                        'proc': proc_name,
                        'raw': raw
                    })
    
    print(f"📊 Total de IF/EVALUATE GAPs: {len(if_evaluate_gaps)}")
    
    # Clasificar por tipo
    if_statements = []
    evaluate_statements = []
    when_statements = []
    else_statements = []
    
    for gap in if_evaluate_gaps:
        raw = gap['raw'].upper()
        if raw.startswith('IF '):
            if_statements.append(gap)
        elif raw.startswith('EVALUATE '):
            evaluate_statements.append(gap)
        elif raw.startswith('WHEN '):
            when_statements.append(gap)
        elif raw.startswith('ELSE'):
            else_statements.append(gap)
    
    print(f"\n📋 CLASIFICACIÓN:")
    print(f"   IF statements: {len(if_statements)}")
    print(f"   EVALUATE statements: {len(evaluate_statements)}")
    print(f"   WHEN statements: {len(when_statements)}")
    print(f"   ELSE statements: {len(else_statements)}")
    
    # Analizar patrones de IF
    print(f"\n🔍 PATRONES DE IF STATEMENTS:")
    print("-" * 40)
    
    if_patterns = {}
    for gap in if_statements:
        raw = gap['raw']
        # Extraer la condición
        if_match = re.match(r'IF\s+(.+?)(?:\s+THEN)?$', raw, re.IGNORECASE)
        if if_match:
            condition = if_match.group(1).strip()
            pattern = classify_condition(condition)
            if pattern not in if_patterns:
                if_patterns[pattern] = []
            if_patterns[pattern].append(condition)
    
    for pattern, conditions in if_patterns.items():
        print(f"\n   {pattern} ({len(conditions)} ejemplos):")
        for condition in conditions[:3]:  # Mostrar máximo 3 ejemplos
            print(f"      - {condition}")
        if len(conditions) > 3:
            print(f"      ... y {len(conditions) - 3} más")
    
    # Analizar patrones de EVALUATE
    print(f"\n🔍 PATRONES DE EVALUATE STATEMENTS:")
    print("-" * 40)
    
    for gap in evaluate_statements:
        print(f"   - {gap['raw']}")
    
    # Analizar patrones de WHEN
    print(f"\n🔍 PATRONES DE WHEN STATEMENTS:")
    print("-" * 40)
    
    when_patterns = {}
    for gap in when_statements:
        raw = gap['raw']
        when_match = re.match(r'WHEN\s+(.+?)(?:\s+THEN)?$', raw, re.IGNORECASE)
        if when_match:
            condition = when_match.group(1).strip()
            pattern = classify_condition(condition)
            if pattern not in when_patterns:
                when_patterns[pattern] = []
            when_patterns[pattern].append(condition)
    
    for pattern, conditions in when_patterns.items():
        print(f"\n   {pattern} ({len(conditions)} ejemplos):")
        for condition in conditions[:3]:
            print(f"      - {condition}")
        if len(conditions) > 3:
            print(f"      ... y {len(conditions) - 3} más")

def classify_condition(condition):
    """Clasifica el tipo de condición"""
    condition_upper = condition.upper()
    
    if ' NOT = ' in condition_upper or ' NOT EQUAL ' in condition_upper:
        return 'NOT_EQUAL'
    elif ' = ' in condition_upper or ' EQUAL ' in condition_upper:
        return 'EQUAL'
    elif ' > ' in condition_upper or ' GREATER ' in condition_upper:
        return 'GREATER_THAN'
    elif ' < ' in condition_upper or ' LESS ' in condition_upper:
        return 'LESS_THAN'
    elif ' >= ' in condition_upper or ' GREATER OR EQUAL ' in condition_upper:
        return 'GREATER_EQUAL'
    elif ' <= ' in condition_upper or ' LESS OR EQUAL ' in condition_upper:
        return 'LESS_EQUAL'
    elif 'TRUE' in condition_upper:
        return 'TRUE'
    elif 'FALSE' in condition_upper:
        return 'FALSE'
    elif 'OTHER' in condition_upper:
        return 'OTHER'
    else:
        return 'COMPLEX'

if __name__ == "__main__":
    main()
