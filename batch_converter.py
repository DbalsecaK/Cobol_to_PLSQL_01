#!/usr/bin/env python3
"""
Convertidor por lotes para procesar múltiples archivos COBOL
"""
import sys
import os
import glob
import json
from datetime import datetime

def process_all_cobol_files():
    """Procesa todos los archivos .cob en el directorio samples"""
    
    # Buscar todos los archivos COBOL
    cob_files = glob.glob("samples/*.cob")
    
    if not cob_files:
        print("❌ No se encontraron archivos .cob en el directorio samples/")
        return
    
    print(f"🚀 Procesando {len(cob_files)} archivos COBOL...")
    print("=" * 60)
    
    results = []
    total_rules = 0
    total_gaps = 0
    
    for cob_file in cob_files:
        print(f"\n📁 Procesando: {cob_file}")
        try:
            # Ejecutar el convertidor
            os.system(f"python antlr_converter.py {cob_file}")
            
            # Leer el reporte generado
            program_name = os.path.splitext(os.path.basename(cob_file))[0].upper()
            report_file = f"out/{program_name}_antlr_report.json"
            
            if os.path.exists(report_file):
                with open(report_file, 'r') as f:
                    report = json.load(f)
                    results.append({
                        "file": cob_file,
                        "program": report["program"],
                        "rules": report["coverage"]["rules"],
                        "gaps": report["coverage"]["gaps"]
                    })
                    total_rules += report["coverage"]["rules"]
                    total_gaps += report["coverage"]["gaps"]
                    print(f"   ✅ {report['program']}: {report['coverage']['rules']} reglas, {report['coverage']['gaps']} gaps")
            else:
                print(f"   ❌ No se pudo leer el reporte: {report_file}")
                
        except Exception as e:
            print(f"   ❌ Error procesando {cob_file}: {e}")
    
    # Generar reporte consolidado
    print("\n" + "=" * 60)
    print("📊 REPORTE CONSOLIDADO")
    print("=" * 60)
    
    for result in results:
        print(f"📄 {result['file']}")
        print(f"   Programa: {result['program']}")
        print(f"   Cobertura: {result['rules']} reglas, {result['gaps']} gaps")
        print()
    
    print(f"🎯 TOTALES:")
    print(f"   Archivos procesados: {len(results)}")
    print(f"   Reglas aplicadas: {total_rules}")
    print(f"   Gaps encontrados: {total_gaps}")
    print(f"   Tasa de cobertura: {(total_rules/(total_rules+total_gaps)*100):.1f}%")
    
    # Guardar reporte consolidado
    consolidated_report = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "total_rules": total_rules,
        "total_gaps": total_gaps,
        "coverage_rate": (total_rules/(total_rules+total_gaps)*100) if (total_rules+total_gaps) > 0 else 0,
        "files": results
    }
    
    with open("out/consolidated_report.json", "w", encoding="utf-8") as f:
        json.dump(consolidated_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte consolidado guardado en: out/consolidated_report.json")

if __name__ == "__main__":
    process_all_cobol_files()
