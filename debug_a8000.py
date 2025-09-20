#!/usr/bin/env python3

import json
from enhanced_converter import EnhancedCobolConverter

# Leer el IR
with open('out/CTB30_ir.json', 'r', encoding='utf-8') as f:
    ir = json.load(f)

# Encontrar A8000-FINAL
converter = EnhancedCobolConverter()
a8000_proc = None

for proc in ir.get("procedures", []):
    if proc.get("name") == "A8000-FINAL":
        a8000_proc = proc
        break

if a8000_proc:
    print("=== A8000-FINAL ENCONTRADO ===")
    print(f"Nombre: {a8000_proc.get('name')}")
    print(f"Número de statements: {len(a8000_proc.get('statements', []))}")
    
    print("\n=== STATEMENTS ORIGINALES ===")
    for i, stmt in enumerate(a8000_proc.get('statements', [])):
        print(f"{i}: {stmt.get('op')} - {stmt.get('raw', '')}")
    
    print("\n=== PROCESANDO CON _process_statements_with_context ===")
    processed = converter._process_statements_with_context(a8000_proc.get('statements', []), "    ")
    
    print(f"Resultado procesado: {len(processed)} líneas")
    for i, line in enumerate(processed):
        print(f"{i}: {repr(line)}")
    
    if not processed:
        print("¡PROBLEMA! No se generaron líneas procesadas")
    else:
        print("✓ Se generaron líneas correctamente")
else:
    print("ERROR: A8000-FINAL no encontrado en procedures")










