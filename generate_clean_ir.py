#!/usr/bin/env python3
"""
Generate Clean IR - Generar IR limpio sin elementos UNKNOWN
"""

import os
import sys
import json
import time
from datetime import datetime

def get_timestamp():
    """Obtener timestamp"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def generate_clean_ir():
    """Generar IR limpio usando el parser corregido"""
    print("🔧 Generando IR limpio sin elementos UNKNOWN...")
    
    # Importar el parser corregido
    try:
        from antlr_parser_direct import CobolToIRParserDirect, save_ir_to_file, generate_parsing_report
    except ImportError as e:
        print(f"❌ Error importando parser: {e}")
        return False
    
    cobol_file = "samples/C1040.cob"
    
    if not os.path.exists(cobol_file):
        print(f"❌ Archivo COBOL no encontrado: {cobol_file}")
        return False
    
    print(f"📁 Procesando: {cobol_file}")
    
    try:
        # Crear parser
        parser = CobolToIRParserDirect()
        
        # Parsear archivo
        start_time = time.time()
        ir = parser.parse_cobol_file(cobol_file)
        parsing_time = time.time()
        
        # Guardar IR
        output_file = "out/C1040_ir_clean.json"
        io_time = save_ir_to_file(ir, output_file)
        save_time = time.time()
        
        # Generar reporte
        report_file = "out/C1040_parsing_report_clean.json"
        report = generate_parsing_report(ir, report_file, parsing_time - start_time, io_time)
        
        print(f"✅ IR limpio generado: {output_file}")
        print(f"📊 Reporte: {report_file}")
        
        # Verificar elementos UNKNOWN
        unknown_count = 0
        for procedure in ir.get("procedures", []):
            for stmt in procedure.get("statements", []):
                if stmt.get("op") == "UNKNOWN":
                    unknown_count += 1
        
        print(f"\n📊 RESULTADOS:")
        print(f"   ❌ Elementos UNKNOWN: {unknown_count}")
        print(f"   📄 Total statements: {report['parsing_summary']['total_statements']}")
        print(f"   ⏱️  Tiempo: {save_time - start_time:.3f}s")
        
        if unknown_count == 0:
            print(f"\n🎊 ¡ÉXITO! IR completamente limpio sin elementos UNKNOWN")
        else:
            print(f"\n⚠️  Aún hay {unknown_count} elementos UNKNOWN")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando IR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("======================================================================")
    print("🔧 GENERATE CLEAN IR - Generando IR limpio sin UNKNOWN")
    print(f"⏰ Inicio: {get_timestamp()}")
    print("🎯 Usando parser corregido para eliminar elementos UNKNOWN")
    print("======================================================================")
    
    if generate_clean_ir():
        print(f"\n⏰ Fin: {get_timestamp()}")
        print("======================================================================")
        print("🎊 ¡ÉXITO! IR limpio generado")
        print("✅ Listo para conversión a SQL sin problemas")
    else:
        print(f"\n⏰ Fin: {get_timestamp()}")
        print("======================================================================")
        print("❌ Error generando IR limpio")

if __name__ == "__main__":
    main()

