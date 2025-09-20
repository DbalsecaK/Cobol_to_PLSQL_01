#!/usr/bin/env python3
"""
COBOL to PL/SQL Migrator - Migrador completo de COBOL a PL/SQL
Uso: python cobol_to_plsql_migrator.py <archivo_cobol> [opciones]
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

def get_timestamp():
    """Obtener timestamp"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def validate_cobol_file(cobol_file):
    """Validar que el archivo COBOL existe y es válido"""
    if not os.path.exists(cobol_file):
        print(f"❌ Error: Archivo COBOL no encontrado: {cobol_file}")
        return False
    
    if not cobol_file.lower().endswith(('.cob', '.cbl', '.cobol')):
        print(f"⚠️  Advertencia: El archivo no tiene extensión COBOL típica (.cob, .cbl, .cobol)")
    
    return True

def generate_output_filenames(cobol_file, output_dir="out"):
    """Generar nombres de archivos de salida basados en el archivo COBOL"""
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Obtener nombre base del archivo
    base_name = os.path.splitext(os.path.basename(cobol_file))[0]
    
    filenames = {
        'ir_file': os.path.join(output_dir, f"{base_name}_ir.json"),
        'sql_file': os.path.join(output_dir, f"{base_name}.sql"),
        'report_file': os.path.join(output_dir, f"{base_name}_migration_report.json"),
        'parsing_report': os.path.join(output_dir, f"{base_name}_parsing_report.json")
    }
    
    return filenames

def parse_cobol_to_ir(cobol_file, ir_file, parsing_report_file):
    """Parsear archivo COBOL a IR usando el parser directo"""
    print(f"🔄 Paso 1: Parseando COBOL a IR...")
    print(f"   📁 Entrada: {cobol_file}")
    print(f"   📄 Salida IR: {ir_file}")
    
    try:
        # Importar el parser corregido
        from antlr_parser_direct import CobolToIRParserDirect, save_ir_to_file, generate_parsing_report
        
        # Crear parser
        parser = CobolToIRParserDirect()
        
        # Parsear archivo
        start_time = time.time()
        ir = parser.parse_cobol_file(cobol_file)
        parsing_time = time.time()
        
        # Guardar IR
        io_time = save_ir_to_file(ir, ir_file)
        save_time = time.time()
        
        # Generar reporte de parsing
        report = generate_parsing_report(ir, parsing_report_file, parsing_time - start_time, io_time)
        
        # Verificar elementos UNKNOWN
        unknown_count = 0
        for procedure in ir.get("procedures", []):
            for stmt in procedure.get("statements", []):
                if stmt.get("op") == "UNKNOWN":
                    unknown_count += 1
        
        print(f"   ✅ IR generado exitosamente")
        print(f"   📊 Elementos UNKNOWN: {unknown_count}")
        print(f"   📄 Total statements: {report['parsing_summary']['total_statements']}")
        print(f"   ⏱️  Tiempo parsing: {save_time - start_time:.3f}s")
        
        if unknown_count > 0:
            print(f"   ⚠️  Advertencia: Hay {unknown_count} elementos UNKNOWN que pueden afectar la conversión")
        
        return ir, True
        
    except ImportError as e:
        print(f"   ❌ Error importando parser: {e}")
        print(f"   💡 Asegúrate de que antlr_parser_direct.py esté disponible")
        return None, False
        
    except Exception as e:
        print(f"   ❌ Error durante el parsing: {e}")
        import traceback
        traceback.print_exc()
        return None, False

def convert_ir_to_sql(ir_file, sql_file, report_file):
    """Convertir IR a SQL usando el convertidor avanzado"""
    print(f"\n🔄 Paso 2: Convirtiendo IR a PL/SQL...")
    print(f"   📁 Entrada IR: {ir_file}")
    print(f"   📄 Salida SQL: {sql_file}")
    print(f"   📊 Reporte: {report_file}")
    
    try:
        # Importar el convertidor
        from ir_to_sql_converter import IRToSQLConverter
        
        # Crear convertidor
        converter = IRToSQLConverter()
        
        # Leer IR
        with open(ir_file, 'r', encoding='utf-8') as f:
            ir_data = json.load(f)
        
        # Convertir a SQL
        start_time = time.time()
        sql_content, gap_count, macro_gap_count = converter.convert_ir_to_sql(ir_data)
        conversion_time = time.time() - start_time
        
        # Guardar SQL
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        # Generar reporte de conversión
        total_statements = sum(len(proc.get("statements", [])) for proc in ir_data.get("procedures", []))
        total_gaps = gap_count + macro_gap_count
        
        conversion_report = {
            "migration_summary": {
                "source_file": ir_file,
                "output_file": sql_file,
                "conversion_time": conversion_time,
                "total_statements": total_statements,
                "gap_count": gap_count,
                "macro_gap_count": macro_gap_count,
                "total_gaps": total_gaps,
                "gap_percentage": (gap_count / total_statements * 100) if total_statements > 0 else 0,
                "macro_gap_percentage": (macro_gap_count / total_statements * 100) if total_statements > 0 else 0,
                "total_gap_percentage": (total_gaps / total_statements * 100) if total_statements > 0 else 0,
                "success_percentage": (100 - (total_gaps / total_statements * 100)) if total_statements > 0 else 100
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Guardar reporte
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(conversion_report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ SQL generado exitosamente")
        print(f"   📊 Total statements: {total_statements}")
        print(f"   ❌ GAPs regulares: {gap_count}")
        print(f"   🔧 GAPs de macros: {macro_gap_count}")
        print(f"   📈 Éxito de conversión: {conversion_report['migration_summary']['success_percentage']:.1f}%")
        print(f"   ⏱️  Tiempo conversión: {conversion_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error durante la conversión: {e}")
        import traceback
        traceback.print_exc()
        return False

def migrate_cobol_to_plsql(cobol_file, output_dir="out", force=False):
    """Migrar completamente un archivo COBOL a PL/SQL"""
    
    print("=" * 80)
    print("🚀 COBOL TO PL/SQL MIGRATOR")
    print(f"⏰ Inicio: {get_timestamp()}")
    print(f"📁 Archivo COBOL: {cobol_file}")
    print(f"📂 Directorio salida: {output_dir}")
    print("=" * 80)
    
    # Validar archivo de entrada
    if not validate_cobol_file(cobol_file):
        return False
    
    # Generar nombres de archivos de salida
    filenames = generate_output_filenames(cobol_file, output_dir)
    
    # Verificar si ya existen archivos de salida
    if not force:
        existing_files = [f for f in filenames.values() if os.path.exists(f)]
        if existing_files:
            print(f"\n⚠️  Los siguientes archivos ya existen:")
            for f in existing_files:
                print(f"   📄 {f}")
            response = input("\n¿Sobrescribir? (s/N): ").lower()
            if response not in ['s', 'si', 'sí', 'y', 'yes']:
                print("❌ Operación cancelada por el usuario")
                return False
    
    success = True
    
    # Paso 1: Parsear COBOL a IR
    ir_data, parse_success = parse_cobol_to_ir(
        cobol_file, 
        filenames['ir_file'], 
        filenames['parsing_report']
    )
    
    if not parse_success:
        print(f"\n❌ Error en el parsing. Migración abortada.")
        return False
    
    # Paso 2: Convertir IR a SQL
    conversion_success = convert_ir_to_sql(
        filenames['ir_file'],
        filenames['sql_file'],
        filenames['report_file']
    )
    
    if not conversion_success:
        print(f"\n❌ Error en la conversión. Migración parcialmente completada.")
        success = False
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("=" * 80)
    
    if success:
        print("🎊 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print(f"\n📄 Archivos generados:")
        for key, filename in filenames.items():
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"   ✅ {key}: {filename} ({size:,} bytes)")
            else:
                print(f"   ❌ {key}: {filename} (no generado)")
    else:
        print("⚠️  MIGRACIÓN COMPLETADA CON ERRORES")
        print("   Revisa los mensajes anteriores para detalles")
    
    print(f"\n⏰ Fin: {get_timestamp()}")
    print("=" * 80)
    
    return success

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Migrador completo de COBOL a PL/SQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python cobol_to_plsql_migrator.py samples/C1040.cob
  python cobol_to_plsql_migrator.py samples/CTB30.CBL --output-dir results
  python cobol_to_plsql_migrator.py mi_programa.cob --force
        """
    )
    
    parser.add_argument(
        'cobol_file',
        help='Archivo COBOL a migrar (.cob, .cbl, .cobol)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='out',
        help='Directorio de salida para archivos generados (default: out)'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Sobrescribir archivos existentes sin preguntar'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='COBOL to PL/SQL Migrator v1.0.0'
    )
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar migración
    success = migrate_cobol_to_plsql(
        args.cobol_file,
        args.output_dir,
        args.force
    )
    
    # Código de salida
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


