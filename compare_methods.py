#!/usr/bin/env python3
"""
Script para comparar los resultados entre método simplificado y ANTLR
"""
import os
import json
import glob

def compare_methods():
    """Compara los resultados de ambos métodos"""
    
    print("🔍 COMPARACIÓN DE MÉTODOS DE CONVERSIÓN")
    print("=" * 60)
    
    # Buscar archivos de reporte
    simple_reports = glob.glob("out/*.json")
    antlr_reports = glob.glob("out/*_antlr_report.json")
    
    print(f"📊 Reportes encontrados:")
    print(f"   Método simplificado: {len([r for r in simple_reports if '_antlr' not in r])}")
    print(f"   Método ANTLR: {len(antlr_reports)}")
    
    # Comparar archivos SQL generados
    print(f"\n📄 Archivos SQL generados:")
    sql_files = glob.glob("out/*.sql")
    
    for sql_file in sorted(sql_files):
        method = "ANTLR" if "_antlr" in sql_file else "Simplificado"
        size = os.path.getsize(sql_file)
        print(f"   {method}: {sql_file} ({size} bytes)")
    
    # Mostrar contenido de algunos archivos para comparación
    print(f"\n🔍 COMPARACIÓN DE CONTENIDO:")
    print("=" * 60)
    
    # Comparar DEMO1
    demo1_simple = "out/DEMO1.sql"
    demo1_antlr = "out/DEMO1_antlr.sql"
    
    if os.path.exists(demo1_simple) and os.path.exists(demo1_antlr):
        print("📄 DEMO1 - Comparación:")
        
        with open(demo1_simple, 'r') as f:
            simple_content = f.read()
        
        with open(demo1_antlr, 'r') as f:
            antlr_content = f.read()
        
        if simple_content == antlr_content:
            print("   ✅ CONTENIDO IDÉNTICO")
        else:
            print("   ⚠️  CONTENIDO DIFERENTE")
            print("   Diferencias encontradas en las líneas:")
            
            simple_lines = simple_content.split('\n')
            antlr_lines = antlr_content.split('\n')
            
            for i, (s_line, a_line) in enumerate(zip(simple_lines, antlr_lines)):
                if s_line != a_line:
                    print(f"     Línea {i+1}:")
                    print(f"       Simplificado: {s_line}")
                    print(f"       ANTLR:        {a_line}")
    
    # Mostrar estadísticas de cobertura
    print(f"\n📈 ESTADÍSTICAS DE COBERTURA:")
    print("=" * 60)
    
    for report_file in sorted(glob.glob("out/*_report.json")):
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        method = report.get("method", "Simplificado")
        program = report["program"]
        rules = report["coverage"]["rules"]
        gaps = report["coverage"]["gaps"]
        total = rules + gaps
        coverage = (rules / total * 100) if total > 0 else 0
        
        print(f"📊 {program} ({method}):")
        print(f"   Reglas: {rules}")
        print(f"   Gaps: {gaps}")
        print(f"   Cobertura: {coverage:.1f}%")
        print()

if __name__ == "__main__":
    compare_methods()
