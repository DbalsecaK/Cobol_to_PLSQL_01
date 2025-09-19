#!/usr/bin/env python3
"""
Script para validar líneas SQL problemáticas
"""

# Líneas problemáticas actuales
problematic_lines = [
    "FILLER_28 VARCHAR2(47) := 'ALL '-';",
    "FILLER_46 VARCHAR2(12) := 'ALL '-';", 
    "FILLER_48 VARCHAR2(42) := 'ALL '-';",
    "FILLER_65 VARCHAR2(47) := 'ALL '-';",
    "FILLER_77 VARCHAR2(132) := 'ALL '=';"
]

print("=== ANÁLISIS DE SINTAXIS SQL ===")
print()

for i, line in enumerate(problematic_lines, 1):
    print(f"Línea {i}: {line}")
    
    # Verificar balance de comillas
    single_quotes = line.count("'")
    print(f"  Comillas simples encontradas: {single_quotes}")
    
    # Buscar el patrón problemático
    if "'ALL '" in line:
        start_pos = line.find("'ALL '")
        end_part = line[start_pos + 6:]
        print(f"  Después de 'ALL ': {end_part}")
        
        if end_part.startswith("-'") or end_part.startswith("='"):
            print(f"  ❌ ERROR: Comilla no cerrada correctamente")
            
            # Sugerir corrección
            if "-'" in end_part:
                corrected = line.replace("'ALL '-'", "'ALL ''-'''")
            elif "='" in end_part:
                corrected = line.replace("'ALL '='", "'ALL ''='''")
            else:
                corrected = line
                
            print(f"  ✅ CORRECCIÓN: {corrected}")
        else:
            print(f"  ✅ OK: Sintaxis correcta")
    else:
        print(f"  ℹ️  No contiene patrón 'ALL '")
    
    print()

print("=== EXPLICACIÓN ===")
print("En PL/SQL, para incluir una comilla simple dentro de una cadena:")
print("- INCORRECTO: 'ALL '-'   (comilla no escapada)")
print("- CORRECTO:   'ALL ''-''' (comilla escapada con '')")
print()
print("La cadena 'ALL ''-''' se interpreta como: ALL '-'")




