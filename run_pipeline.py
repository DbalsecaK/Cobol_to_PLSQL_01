#!/usr/bin/env python3
"""
Pipeline Runner - Script para ejecutar el pipeline completo
Automatiza la ejecución de: COBOL → IR → PL/SQL

Uso: python run_pipeline.py archivo.cob
"""

import sys
import os
import subprocess
import time
from datetime import datetime

def run_command(cmd, description):
    """Ejecutar comando y mostrar progreso"""
    print(f"🔄 {description}...")
    print(f"💻 Ejecutando: {cmd}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} completado en {duration:.2f}s")
            if result.stdout:
                print("📄 Salida:")
                print(result.stdout)
            return True
        else:
            print(f"❌ Error en {description}")
            print("🔴 Error:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Excepción durante {description}: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python run_pipeline.py <archivo.cob>")
        print("Ejemplo: python run_pipeline.py samples/C1040.cob")
        sys.exit(1)
    
    cobol_file = sys.argv[1]
    
    if not os.path.exists(cobol_file):
        print(f"❌ Error: No se encuentra el archivo {cobol_file}")
        sys.exit(1)
    
    # Determinar nombres de archivos
    base_name = os.path.splitext(os.path.basename(cobol_file))[0].upper()
    ir_file = f"out/{base_name}_ir_fixed.json"
    
    print("=" * 70)
    print(f"🚀 PIPELINE COMPLETO COBOL → IR → PL/SQL")
    print(f"📁 Archivo fuente: {cobol_file}")
    print(f"⏰ Inicio: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    
    total_start = time.time()
    
    # Paso 1: COBOL → IR (USANDO LA VERSIÓN CORREGIDA)
    step1_success = run_command(
        f"python antlr_parser_fixed.py {cobol_file}",
        "Paso 1: Parsing COBOL → IR [FIXED VERSION]"
    )
    
    if not step1_success:
        print("❌ Pipeline abortado en Paso 1")
        sys.exit(1)
    
    # Verificar que se generó el IR
    if not os.path.exists(ir_file):
        print(f"❌ Error: No se generó el archivo IR {ir_file}")
        sys.exit(1)
    
    print()
    
    # Paso 2: IR → PL/SQL
    step2_success = run_command(
        f"python ir_to_plsql.py {ir_file}",
        "Paso 2: Conversión IR → PL/SQL"
    )
    
    if not step2_success:
        print("❌ Pipeline abortado en Paso 2")
        sys.exit(1)
    
    total_end = time.time()
    total_duration = total_end - total_start
    
    print()
    print("=" * 70)
    print("🎊 PIPELINE COMPLETADO EXITOSAMENTE!")
    print("=" * 70)
    print(f"⏰ Tiempo total: {total_duration:.2f} segundos")
    print(f"📁 Archivos generados en: out/")
    print(f"   📊 IR: {ir_file}")
    print(f"   📄 PL/SQL: out/{base_name}_generated.sql")
    print(f"   📊 Reportes: out/{base_name}_*_report.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
