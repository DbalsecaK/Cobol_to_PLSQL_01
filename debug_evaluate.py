#!/usr/bin/env python3
"""Debug script para EVALUATE statements"""

import re
import json

def test_evaluate_patterns():
    """Probar patrones de EVALUATE"""
    
    test_cases = [
        "EVALUATE TRUE",
        "EVALUATE TRUE.",
        "EVALUATE VARIABLE",
        "EVALUATE VARIABLE.",
        "EVALUATE VAR1 ALSO VAR2",
        "EVALUATE VAR1 ALSO VAR2."
    ]
    
    patterns = {
        "true": r"EVALUATE\s+TRUE\s*(?:\.|$)",
        "range": r"EVALUATE\s+(.+?)\s+ALSO\s+(.+?)(?:\.|$)",
        "simple": r"EVALUATE\s+(.+?)(?:\.|$)",
    }
    
    print("🔍 Probando patrones de EVALUATE:")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📝 Texto: '{test_case}'")
        upper_line = test_case.upper()
        
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, upper_line, re.IGNORECASE)
            if match:
                print(f"  ✅ {pattern_name}: {match.groups()}")
                break
        else:
            print(f"  ❌ No match")

def test_evaluate_from_ir():
    """Probar con datos reales del IR"""
    
    print("\n🔍 Probando con datos reales del IR:")
    print("=" * 50)
    
    # Cargar IR
    with open('out/C1040_ir_clean.json', 'r', encoding='utf-8') as f:
        ir_data = json.load(f)
    
    # Buscar statements EVALUATE
    main_statements = ir_data.get("cobol_statements", [])
    evaluate_count = 0
    
    for stmt in main_statements:
        if stmt.get("statement_type") == "EVALUATE":
            evaluate_count += 1
            raw = stmt.get("raw", "")
            print(f"\n📝 EVALUATE #{evaluate_count}: '{raw}'")
            
            # Probar parsing
            patterns = {
                "true": r"EVALUATE\s+TRUE\s*(?:\.|$)",
                "range": r"EVALUATE\s+(.+?)\s+ALSO\s+(.+?)(?:\.|$)",
                "simple": r"EVALUATE\s+(.+?)(?:\.|$)",
            }
            
            upper_line = raw.upper()
            for pattern_name, pattern in patterns.items():
                match = re.search(pattern, upper_line, re.IGNORECASE)
                if match:
                    print(f"  ✅ {pattern_name}: {match.groups()}")
                    break
            else:
                print(f"  ❌ No match")
    
    print(f"\n📊 Total EVALUATE statements encontrados: {evaluate_count}")

if __name__ == "__main__":
    test_evaluate_patterns()
    test_evaluate_from_ir()
