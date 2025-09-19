#!/usr/bin/env python3

import json
from enhanced_converter import EnhancedCobolConverter

# Leer el IR
with open('out/CTB30_ir.json', 'r', encoding='utf-8') as f:
    ir = json.load(f)

# Crear el converter
converter = EnhancedCobolConverter()

print("=== ANALIZANDO _generate_package_body ===")

# Simular el bucle de generación de procedimientos
procedure_bodies = []
total_procs = len(ir.get("procedures", []))
print(f"Total de procedimientos en IR: {total_procs}")

skipped_count = 0
generated_count = 0

for i, proc in enumerate(ir.get("procedures", [])):
    proc_name = converter.clean_expression(proc.get("name", ""))
    proc_statements = converter._process_statements_with_context(proc.get("statements", []), "    ")
    
    print(f"\nProcedimiento {i+1}/{total_procs}: {proc_name}")
    print(f"  - Statements originales: {len(proc.get('statements', []))}")
    print(f"  - Statements procesados: {len(proc_statements)}")
    
    if proc_statements:
        print(f"  ✓ GENERANDO procedimiento {proc_name}")
        generated_count += 1
        if proc_name == "A8000_FINAL":
            print("  *** A8000_FINAL SE ESTÁ GENERANDO ***")
    else:
        print(f"  ✗ SALTANDO procedimiento {proc_name} (sin statements)")
        skipped_count += 1
        if proc_name == "A8000_FINAL":
            print("  *** PROBLEMA: A8000_FINAL SE ESTÁ SALTANDO ***")

print(f"\n=== RESUMEN ===")
print(f"Procedimientos generados: {generated_count}")
print(f"Procedimientos saltados: {skipped_count}")
print(f"Total: {generated_count + skipped_count}")






