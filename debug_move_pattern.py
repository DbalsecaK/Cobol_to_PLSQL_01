#!/usr/bin/env python3
"""
Debug específico del patrón MOVE OF
"""

import re

def test_move_pattern_debug():
    """Debug del patrón MOVE OF"""
    
    test_line = "MOVE COD-SUC-PROPIE OF T08CT093 TO"
    
    print("🐛 DEBUG MOVE OF PATTERN:")
    print("=" * 50)
    print(f"Línea de prueba: '{test_line}'")
    print()
    
    # Test 1: Verificar si es detectado como MOVE OF incompleto
    pattern1 = r'^MOVE\s+[\w-]+\s+OF\s+[\w-]+\s+TO\s*$'
    match1 = re.search(pattern1, test_line, re.IGNORECASE)
    print(f"1. Patrón MOVE OF incompleto: {pattern1}")
    print(f"   Resultado: {'✅ COINCIDE' if match1 else '❌ NO COINCIDE'}")
    if match1:
        print(f"   Match: {match1.group(0)}")
    print()
    
    # Test 2: Verificar si es capturado por el patrón general
    pattern2 = r'^MOVE\s+(.+?)\s+TO\s+(.+?)(?:\.|$)'
    match2 = re.search(pattern2, test_line, re.IGNORECASE)
    print(f"2. Patrón MOVE general: {pattern2}")
    print(f"   Resultado: {'✅ COINCIDE' if match2 else '❌ NO COINCIDE'}")
    if match2:
        print(f"   Source: '{match2.group(1)}'")
        print(f"   Target: '{match2.group(2)}'")
        print(f"   Target está vacío: {not match2.group(2).strip()}")
    print()
    
    # Test 3: Simular el flujo completo
    print("3. Simulación del flujo:")
    
    # Primero verificar si es MOVE OF incompleto
    if re.search(r'^MOVE\s+[\w-]+\s+OF\s+[\w-]+\s+TO\s*$', test_line, re.IGNORECASE):
        print("   ✅ Es MOVE OF incompleto - debe ir a _parse_statement")
        
        # Simular _parse_statement
        line_clean = test_line.strip()
        if re.search(r'^MOVE\s+[\w-]+\s+OF\s+[\w-]+\s+TO\s*$', line_clean, re.IGNORECASE):
            print("   ✅ _parse_statement detecta MOVE_OF_INCOMPLETE")
            print("   ✅ GAP debería cerrarse")
        else:
            print("   ❌ _parse_statement NO detecta MOVE_OF_INCOMPLETE")
    else:
        print("   ❌ NO es detectado como MOVE OF incompleto")
    
    print("\n🎯 CONCLUSIÓN:")
    print("   Si todos los tests son ✅, el GAP debería cerrarse")
    print("   Si algún test es ❌, hay que revisar los patrones")

if __name__ == "__main__":
    test_move_pattern_debug()






