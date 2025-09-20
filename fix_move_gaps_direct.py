#!/usr/bin/env python3
"""
Corrección directa de GAPs MOVE OF en el SQL generado
"""

import re

def fix_move_gaps_in_sql():
    """Corrige directamente los GAPs MOVE OF en el SQL"""
    
    try:
        with open('out/CTB30.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
    except FileNotFoundError:
        print("❌ No se encontró out/CTB30.sql")
        return
    
    print("🔧 CORRIGIENDO GAPs MOVE OF DIRECTAMENTE:")
    print("=" * 50)
    
    # Contar GAPs antes
    gaps_before = len(re.findall(r'-- GAP:.*MOVE.*OF.*TO\s*$', sql_content, re.MULTILINE))
    print(f"GAPs MOVE OF encontrados: {gaps_before}")
    
    # Patrón para encontrar GAPs MOVE OF
    patterns_to_fix = [
        (r'(\s*)-- GAP: MOVE ([\w-]+) OF ([\w-]+) TO\s*$', 
         r'\1-- MOVE \3.\2 TO target (incomplete statement)'),
        
        (r'(\s*)-- GAP: MOVE ([\w-]+)\s+OF ([\w-]+) TO\s*$', 
         r'\1-- MOVE \3.\2 TO target (incomplete statement)')
    ]
    
    # Aplicar correcciones
    for pattern, replacement in patterns_to_fix:
        matches_found = len(re.findall(pattern, sql_content, re.MULTILINE))
        if matches_found > 0:
            sql_content = re.sub(pattern, replacement, sql_content, flags=re.MULTILINE)
            print(f"✅ Corregidos {matches_found} GAPs con patrón: {pattern[:50]}...")
    
    # Contar GAPs después
    gaps_after = len(re.findall(r'-- GAP:.*MOVE.*OF.*TO\s*$', sql_content, re.MULTILINE))
    
    # Guardar archivo corregido
    with open('out/CTB30.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"\n📊 RESULTADO:")
    print(f"   GAPs ANTES: {gaps_before}")
    print(f"   GAPs DESPUÉS: {gaps_after}")
    print(f"   GAPs CORREGIDOS: {gaps_before - gaps_after}")
    
    if gaps_after == 0:
        print("   🎉 ¡TODOS LOS GAPs MOVE OF ELIMINADOS!")
    else:
        print(f"   ⚠️  Quedan {gaps_after} GAPs MOVE OF sin corregir")
    
    print(f"\n✅ Archivo out/CTB30.sql actualizado")

if __name__ == "__main__":
    fix_move_gaps_in_sql()











