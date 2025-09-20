#!/usr/bin/env python3

import json

# Leer el IR
with open('out/CTB30_ir.json', 'r', encoding='utf-8') as f:
    ir = json.load(f)

print("=== ORDEN DE PROCEDIMIENTOS EN EL IR ===")

procedures = ir.get("procedures", [])
for i, proc in enumerate(procedures):
    name = proc.get("name", "")
    print(f"{i+1:2d}: {name}")
    if name == "A8000-FINAL":
        print(f"    *** A8000-FINAL está en la posición {i+1} ***")

print(f"\nTotal de procedimientos: {len(procedures)}")

# Buscar A8000-FINAL específicamente
a8000_found = False
for i, proc in enumerate(procedures):
    if proc.get("name") == "A8000-FINAL":
        print(f"\n✓ A8000-FINAL encontrado en posición {i+1}")
        a8000_found = True
        break

if not a8000_found:
    print("\n✗ A8000-FINAL NO encontrado")










