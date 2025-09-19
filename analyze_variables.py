#!/usr/bin/env python3
"""
Analizar variables en el IR para validar la migración
"""
import json
import sys

def analyze_ir_variables(ir_file):
    """Analizar variables en el IR"""
    
    print(f"🔍 Analizando variables en: {ir_file}")
    
    try:
        with open(ir_file, 'r', encoding='utf-8') as f:
            ir = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo IR: {e}")
        return
    
    print("\n📊 ANÁLISIS COMPLETO DE VARIABLES:")
    print("=" * 60)
    
    # Analizar Data Division
    data_division = ir.get("data_division", {})
    
    # Working-Storage Section
    working_storage = data_division.get("working_storage_section", {})
    ws_variables = working_storage.get("variables", [])
    
    print(f"📋 Working-Storage Section: {len(ws_variables)} variables")
    
    # Categorizar variables
    constants = []
    work_variables = []
    auxiliary_variables = []
    level_01_vars = []
    level_05_vars = []
    other_level_vars = []
    
    for i, var in enumerate(ws_variables):
        var_name = var.get("name", "")
        var_value = var.get("value", "")
        level = var.get("level", "")
        pic_clause = var.get("pic_clause", "")
        
        # Categorizar por nivel
        if level == "01":
            level_01_vars.append(var)
        elif level == "05":
            level_05_vars.append(var)
        else:
            other_level_vars.append(var)
        
        # Categorizar por tipo
        if var_value and var_value != "":
            constants.append(var)
        elif "LT_" in var_name or "LITERAL" in var_name.upper():
            constants.append(var)
        elif "WS_" in var_name:
            work_variables.append(var)
        else:
            auxiliary_variables.append(var)
    
    print(f"\n🏷️ VARIABLES POR NIVEL:")
    print(f"   Nivel 01: {len(level_01_vars)} variables")
    print(f"   Nivel 05: {len(level_05_vars)} variables")
    print(f"   Otros niveles: {len(other_level_vars)} variables")
    
    print(f"\n📂 VARIABLES POR CATEGORÍA:")
    print(f"   Constantes: {len(constants)} variables")
    print(f"   Variables de trabajo (WS_): {len(work_variables)} variables")
    print(f"   Variables auxiliares: {len(auxiliary_variables)} variables")
    
    # Mostrar primeras 20 variables de cada categoría
    print(f"\n📝 MUESTRA DE CONSTANTES (primeras 10):")
    for i, const in enumerate(constants[:10]):
        name = const.get("name", "").replace("-", "_")
        value = const.get("value", "")
        pic = const.get("pic_clause", "")
        print(f"   {i+1:2d}. {name:<25} = {value:<10} ({pic})")
    
    print(f"\n📝 MUESTRA DE VARIABLES DE TRABAJO (primeras 10):")
    for i, var in enumerate(work_variables[:10]):
        name = var.get("name", "").replace("-", "_")
        value = var.get("value", "")
        pic = var.get("pic_clause", "")
        print(f"   {i+1:2d}. {name:<25} = {value:<10} ({pic})")
    
    print(f"\n📝 MUESTRA DE VARIABLES AUXILIARES (primeras 10):")
    for i, var in enumerate(auxiliary_variables[:10]):
        name = var.get("name", "").replace("-", "_")
        value = var.get("value", "")
        pic = var.get("pic_clause", "")
        print(f"   {i+1:2d}. {name:<25} = {value:<10} ({pic})")
    
    # Analizar File Section
    file_section = data_division.get("file_section", {})
    file_descriptions = file_section.get("file_descriptions", [])
    
    file_records = 0
    for file_desc in file_descriptions:
        record_layouts = file_desc.get("record_layouts", [])
        file_records += len(record_layouts)
    
    print(f"\n📁 File Section: {len(file_descriptions)} archivos, {file_records} records")
    
    # Variables totales
    total_variables = len(ws_variables) + file_records
    
    print(f"\n🎯 RESUMEN TOTAL:")
    print(f"   Variables Working-Storage: {len(ws_variables)}")
    print(f"   Records File Section: {file_records}")
    print(f"   TOTAL VARIABLES: {total_variables}")
    
    # Análizar problemas de generación
    print(f"\n⚠️ ANÁLISIS DE POSIBLES PROBLEMAS:")
    
    # Variables sin nombre
    no_name = [v for v in ws_variables if not v.get("name", "")]
    print(f"   Variables sin nombre: {len(no_name)}")
    
    # Variables sin pic clause
    no_pic = [v for v in ws_variables if not v.get("pic_clause", "")]
    print(f"   Variables sin PIC clause: {len(no_pic)}")
    
    # Variables con levels no estándar
    weird_levels = [v for v in ws_variables if v.get("level", "") not in ["01", "05", "77"]]
    print(f"   Variables con levels no estándar: {len(weird_levels)}")
    
    # Variables FILLER
    fillers = [v for v in ws_variables if "FILLER" in v.get("name", "").upper()]
    print(f"   Variables FILLER: {len(fillers)}")
    
    if fillers:
        print(f"   📝 Ejemplos de FILLER:")
        for i, filler in enumerate(fillers[:5]):
            name = filler.get("name", "")
            pic = filler.get("pic_clause", "")
            print(f"      {i+1}. {name} ({pic})")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    ir_file = "out/C1040_ir_clean.json"
    analyze_ir_variables(ir_file)



