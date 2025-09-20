#!/usr/bin/env python3
"""
Verificar si la corrección en el IR funcionó
"""

import json
import re

def check_ir_classification():
    """Verifica cómo se clasifican los statements MOVE OF en el IR"""
    
    try:
        with open('out/CTB30_ir.json', 'r', encoding='utf-8') as f:
            ir_data = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró out/CTB30_ir.json")
        return
    
    print("🔍 ANÁLISIS DE CLASIFICACIÓN IR - CTB30:")
    print("=" * 50)
    
    # Buscar todos los statements que contengan "MOVE" y "OF T08CT093 TO"
    move_of_statements = []
    field_display_statements = []
    unknown_statements = []
    move_statements = []
    
    for procedure in ir_data.get("procedures", []):
        for statement in procedure.get("statements", []):
            raw = statement.get("raw", "")
            op = statement.get("op", "")
            
            if "MOVE" in raw and "OF T08CT093 TO" in raw:
                if op == "FIELD_DISPLAY":
                    field_display_statements.append(raw)
                elif op == "MOVE_OF_INCOMPLETE":
                    move_of_statements.append(raw)
                elif op == "UNKNOWN":
                    unknown_statements.append(raw)
                elif op == "MOVE":
                    move_statements.append(raw)
                else:
                    print(f"   Clasificación inesperada: {op} -> {raw}")
    
    print(f"📊 RESULTADOS:")
    print(f"   MOVE (completos): {len(move_statements)}")
    print(f"   MOVE_OF_INCOMPLETE: {len(move_of_statements)}")
    print(f"   FIELD_DISPLAY (incorrecto): {len(field_display_statements)}")
    print(f"   UNKNOWN: {len(unknown_statements)}")
    
    if field_display_statements:
        print(f"\n❌ AÚN HAY CLASIFICACIONES INCORRECTAS:")
        for stmt in field_display_statements[:3]:
            print(f"   - {stmt}")
    
    if move_of_statements:
        print(f"\n✅ CLASIFICACIONES CORRECTAS MOVE_OF_INCOMPLETE:")
        for stmt in move_of_statements[:3]:
            print(f"   - {stmt}")
    
    if unknown_statements:
        print(f"\n⚠️  CLASIFICACIONES UNKNOWN:")
        for stmt in unknown_statements[:3]:
            print(f"   - {stmt}")
    
    # Status final
    if field_display_statements:
        print(f"\n🎯 CONCLUSIÓN: AÚN HAY {len(field_display_statements)} STATEMENTS MAL CLASIFICADOS")
        print("   Necesita más correcciones en el parser")
    else:
        print(f"\n🎉 CONCLUSIÓN: ¡TODOS LOS STATEMENTS MOVE OF ESTÁN BIEN CLASIFICADOS!")
        print("   El problema debe estar en la conversión")

if __name__ == "__main__":
    check_ir_classification()










