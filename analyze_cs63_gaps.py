#!/usr/bin/env python3
"""
Analizar patrones de GAPs en CS63 para optimización
"""

import re
from collections import Counter

def analyze_gaps():
    """Analiza los GAPs de CS63 para identificar patrones"""
    
    try:
        with open('out/CS63.sql', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ No se encontró out/CS63.sql")
        return
    
    # Extraer todos los GAPs
    gap_pattern = r'-- GAP: (.+)'
    gaps = re.findall(gap_pattern, content)
    
    print(f"📊 Total GAPs encontrados: {len(gaps)}")
    
    # Categorizar GAPs por patrones
    categories = {
        'sql_fields': [],
        'sql_values': [],
        'sql_statements': [],
        'conditions': [],
        'references': [],
        'comments': [],
        'simple_strings': [],
        'others': []
    }
    
    for gap in gaps:
        gap = gap.strip()
        
        if re.match(r'^\w+\s*,$', gap):  # "GUID ,"
            categories['sql_fields'].append(gap)
        elif re.match(r'^:T\d+\w+\.\w+', gap):  # ":T08CT176.GUID"
            categories['sql_values'].append(gap)
        elif gap in ['VALUES', ')', '(', 'SET', 'WHERE', 'AND']:
            categories['sql_statements'].append(gap)
        elif 'EQUAL' in gap or 'THEN' in gap or 'OF MSG-IN' in gap:
            categories['conditions'].append(gap)
        elif gap.startswith("'") and gap.endswith("'"):
            categories['simple_strings'].append(gap)
        elif gap.startswith('CJP01') or gap.startswith('OF '):
            categories['references'].append(gap)
        else:
            categories['others'].append(gap)
    
    # Mostrar estadísticas
    print("\n📈 Categorías de GAPs:")
    for category, items in categories.items():
        if items:
            print(f"  • {category}: {len(items)} GAPs")
            # Mostrar ejemplos
            examples = list(set(items))[:3]
            for example in examples:
                print(f"    - {example}")
    
    # Top 10 GAPs más frecuentes
    gap_counter = Counter(gaps)
    print(f"\n🔝 Top 10 GAPs más frecuentes:")
    for gap, count in gap_counter.most_common(10):
        print(f"  {count}x: {gap}")

if __name__ == "__main__":
    analyze_gaps()






