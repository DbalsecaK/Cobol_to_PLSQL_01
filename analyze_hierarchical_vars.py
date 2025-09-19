#!/usr/bin/env python3
"""
Analizar variables jerárquicas en el IR
"""
import json
import sys

def analyze_hierarchical_variables(ir_file):
    """Analizar variables jerárquicas con REDEFINES"""
    
    print(f"🔍 Analizando variables jerárquicas en: {ir_file}")
    
    try:
        with open(ir_file, 'r', encoding='utf-8') as f:
            ir = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo IR: {e}")
        return
    
    print("\n📊 ANÁLISIS DE VARIABLES JERÁRQUICAS:")
    print("=" * 70)
    
    # Analizar Working-Storage Section
    data_division = ir.get("data_division", {})
    working_storage = data_division.get("working_storage_section", {})
    variables = working_storage.get("variables", [])
    
    print(f"📋 Total variables en Working-Storage: {len(variables)}")
    
    # Categorizar por nivel
    level_01 = [v for v in variables if v.get("level") == "01"]
    level_05 = [v for v in variables if v.get("level") == "05"]
    level_10 = [v for v in variables if v.get("level") == "10"]
    other_levels = [v for v in variables if v.get("level") not in ["01", "05", "10"]]
    
    print(f"\n🏷️ VARIABLES POR NIVEL:")
    print(f"   Nivel 01: {len(level_01)} variables")
    print(f"   Nivel 05: {len(level_05)} variables")
    print(f"   Nivel 10: {len(level_10)} variables")
    print(f"   Otros niveles: {len(other_levels)} variables")
    
    # Buscar variables REDEFINES
    redefines_vars = [v for v in variables if "REDEFINES" in v.get("raw", "").upper()]
    filler_vars = [v for v in variables if "FILLER" in v.get("name", "").upper()]
    value_vars = [v for v in variables if "VALUE" in v.get("raw", "").upper()]
    
    print(f"\n📂 VARIABLES ESPECIALES:")
    print(f"   Variables con REDEFINES: {len(redefines_vars)}")
    print(f"   Variables FILLER: {len(filler_vars)}")
    print(f"   Variables con VALUE: {len(value_vars)}")
    
    # Mostrar ejemplos de estructuras jerárquicas
    print(f"\n📝 EJEMPLOS DE VARIABLES NIVEL 01:")
    for i, var in enumerate(level_01[:10]):
        name = var.get("name", "")
        pic = var.get("pic_clause", "")
        raw = var.get("raw", "")[:80] + "..." if len(var.get("raw", "")) > 80 else var.get("raw", "")
        print(f"   {i+1:2d}. {name:<25} {pic:<15} | {raw}")
    
    print(f"\n📝 EJEMPLOS DE VARIABLES REDEFINES:")
    for i, var in enumerate(redefines_vars[:5]):
        name = var.get("name", "")
        raw = var.get("raw", "")
        print(f"   {i+1:2d}. {name:<25} | {raw}")
    
    print(f"\n📝 EJEMPLOS DE VARIABLES FILLER:")
    for i, var in enumerate(filler_vars[:5]):
        name = var.get("name", "")
        level = var.get("level", "")
        raw = var.get("raw", "")[:60] + "..." if len(var.get("raw", "")) > 60 else var.get("raw", "")
        print(f"   {i+1:2d}. {level} {name:<20} | {raw}")
    
    # Buscar patrones específicos mencionados por el usuario
    ws_num_cuenta = [v for v in variables if "WS-NUM-CUENTA" in v.get("name", "")]
    ws_numcuen = [v for v in variables if "WS-NUMCUEN" in v.get("name", "")]
    ws_var_aux = [v for v in variables if "WS-VAR-AUX" in v.get("name", "")]
    ws_hora_vars = [v for v in variables if "WS-HORA" in v.get("name", "")]
    
    print(f"\n🎯 VARIABLES ESPECÍFICAS MENCIONADAS:")
    print(f"   WS-NUM-CUENTA: {len(ws_num_cuenta)} variables")
    print(f"   WS-NUMCUEN: {len(ws_numcuen)} variables")
    print(f"   WS-VAR-AUX: {len(ws_var_aux)} variables")
    print(f"   Variables WS-HORA*: {len(ws_hora_vars)} variables")
    
    # Mostrar detalles de estas variables
    if ws_num_cuenta:
        print(f"\n📝 DETALLE WS-NUM-CUENTA:")
        for var in ws_num_cuenta:
            print(f"      {var.get('raw', '')}")
    
    if ws_numcuen:
        print(f"\n📝 DETALLE WS-NUMCUEN:")
        for var in ws_numcuen:
            print(f"      {var.get('raw', '')}")
    
    if ws_var_aux:
        print(f"\n📝 DETALLE WS-VAR-AUX:")
        for var in ws_var_aux:
            print(f"      {var.get('raw', '')}")
    
    # Buscar variables subordinadas de WS-VAR-AUX
    subordinate_vars = []
    for i, var in enumerate(variables):
        if i > 0 and variables[i-1].get("name") == "WS-VAR-AUX":
            # Buscar variables que vengan después de WS-VAR-AUX
            for j in range(i+1, min(i+20, len(variables))):
                next_var = variables[j]
                next_level = next_var.get("level", "")
                if next_level in ["05", "10"] and ("WS-HORA" in next_var.get("name", "") or "WS-COD-CENT-COMP" in next_var.get("name", "")):
                    subordinate_vars.append(next_var)
    
    print(f"\n📝 VARIABLES SUBORDINADAS ENCONTRADAS ({len(subordinate_vars)}):")
    for var in subordinate_vars[:10]:
        level = var.get("level", "")
        name = var.get("name", "")
        raw = var.get("raw", "")
        print(f"      {level} {name:<25} | {raw}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    ir_file = "out/C1040_ir_clean.json"
    analyze_hierarchical_variables(ir_file)



