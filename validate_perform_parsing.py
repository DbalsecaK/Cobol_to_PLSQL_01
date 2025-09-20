#!/usr/bin/env python3
"""
VALIDATE PERFORM PARSING - Validar captura de sentencias PERFORM desde el árbol ANTLR

Este script valida si el generador de IR está capturando correctamente todas las sentencias PERFORM,
especialmente las principales del PROCEDURE DIVISION.
"""

import os
import sys
import json
import re
from typing import List, Dict, Any

def extract_expected_performs_from_cobol(cobol_file: str) -> List[Dict[str, Any]]:
    """Extraer manualmente todas las sentencias PERFORM del archivo COBOL"""
    performs = []
    in_procedure_division = False
    line_number = 0
    
    with open(cobol_file, 'r', encoding='utf-8') as f:
        for line in f:
            line_number += 1
            
            # Procesar formato fijo COBOL
            if len(line) > 7:
                line_content = line[7:].strip()
            else:
                line_content = line.strip()
            
            # Detectar PROCEDURE DIVISION
            if 'PROCEDURE DIVISION' in line_content.upper():
                in_procedure_division = True
                print(f"✅ PROCEDURE DIVISION encontrada en línea {line_number}")
                continue
                
            # Buscar PERFORM statements
            if in_procedure_division and 'PERFORM' in line_content.upper():
                # Limpiar comentarios
                clean_line = re.sub(r'\*.*$', '', line_content).strip()
                
                if clean_line and 'PERFORM' in clean_line.upper():
                    # Diferentes tipos de PERFORM
                    perform_info = {
                        "line_number": line_number,
                        "raw_line": line_content,
                        "clean_line": clean_line,
                        "type": "UNKNOWN"
                    }
                    
                    # PERFORM simple: PERFORM paragraph-name
                    simple_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)\s*\.?\s*$', clean_line, re.IGNORECASE)
                    if simple_match:
                        perform_info.update({
                            "type": "SIMPLE",
                            "target": simple_match.group(1),
                            "pattern": "PERFORM target"
                        })
                    
                    # PERFORM UNTIL: PERFORM paragraph UNTIL condition
                    elif re.search(r'PERFORM\s+.*UNTIL', clean_line, re.IGNORECASE):
                        until_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)(?:\s+THRU\s+([A-Z0-9\-_]+))?\s+UNTIL\s+(.+?)\s*\.?\s*$', clean_line, re.IGNORECASE)
                        if until_match:
                            perform_info.update({
                                "type": "UNTIL",
                                "target": until_match.group(1),
                                "thru_target": until_match.group(2),
                                "until_condition": until_match.group(3).strip(),
                                "pattern": "PERFORM target UNTIL condition"
                            })
                    
                    # PERFORM THRU: PERFORM paragraph1 THRU paragraph2
                    elif re.search(r'PERFORM\s+.*THRU', clean_line, re.IGNORECASE):
                        thru_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)\s+THRU\s+([A-Z0-9\-_]+)\s*\.?\s*$', clean_line, re.IGNORECASE)
                        if thru_match:
                            perform_info.update({
                                "type": "THRU",
                                "target": thru_match.group(1),
                                "thru_target": thru_match.group(2),
                                "pattern": "PERFORM target THRU target2"
                            })
                    
                    # PERFORM TIMES: PERFORM paragraph N TIMES
                    elif re.search(r'PERFORM\s+.*TIMES', clean_line, re.IGNORECASE):
                        times_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)(?:\s+THRU\s+([A-Z0-9\-_]+))?\s+(\d+|\w[\w\-]*)\s+TIMES\s*\.?\s*$', clean_line, re.IGNORECASE)
                        if times_match:
                            perform_info.update({
                                "type": "TIMES",
                                "target": times_match.group(1),
                                "thru_target": times_match.group(2),
                                "times": times_match.group(3),
                                "pattern": "PERFORM target N TIMES"
                            })
                    
                    # PERFORM VARYING
                    elif re.search(r'PERFORM\s+.*VARYING', clean_line, re.IGNORECASE):
                        perform_info.update({
                            "type": "VARYING",
                            "pattern": "PERFORM target VARYING ..."
                        })
                    
                    performs.append(perform_info)
                    print(f"📝 PERFORM encontrado: {perform_info['type']} en línea {line_number}: {clean_line}")
    
    return performs

def analyze_ir_performs(ir_file: str) -> Dict[str, Any]:
    """Analizar las sentencias PERFORM capturadas en el IR"""
    if not os.path.exists(ir_file):
        return {"error": f"Archivo IR no encontrado: {ir_file}"}
    
    with open(ir_file, 'r', encoding='utf-8') as f:
        ir = json.load(f)
    
    analysis = {
        "ir_file": ir_file,
        "program_name": ir.get("program", "UNKNOWN"),
        "parse_method": ir.get("parse_method", "UNKNOWN"),
        "perform_statements": [],
        "procedure_division_raw": "",
        "total_performs_in_ir": 0,
        "performs_by_type": {},
        "main_performs_found": []
    }
    
    # Obtener PERFORM statements directos
    perform_statements = ir.get("perform_statements", [])
    analysis["perform_statements"] = perform_statements
    analysis["total_performs_in_ir"] = len(perform_statements)
    
    # Contar por tipo
    for perform in perform_statements:
        perf_type = perform.get("perform_type", "UNKNOWN")
        if perf_type not in analysis["performs_by_type"]:
            analysis["performs_by_type"][perf_type] = 0
        analysis["performs_by_type"][perf_type] += 1
    
    # Obtener raw content del PROCEDURE DIVISION
    proc_div = ir.get("procedure_division", {})
    analysis["procedure_division_raw"] = proc_div.get("raw_content", "")
    
    # Buscar los PERFORM principales en el raw content
    main_performs = ["1000-INICIO", "2000-PROCESO UNTIL NO-ENCONTRADO", "8000-FINAL"]
    
    for main_perform in main_performs:
        if main_perform in analysis["procedure_division_raw"]:
            analysis["main_performs_found"].append(main_perform)
    
    # Buscar PERFORM statements también en procedimientos
    procedures = ir.get("procedures", [])
    for proc in procedures:
        statements = proc.get("statements", [])
        for stmt in statements:
            if stmt.get("op") == "PERFORM":
                # Buscar detalles del PERFORM
                details = stmt.get("details", {})
                if details:
                    analysis["perform_statements"].append(details)
    
    # También buscar en cobol_statements
    cobol_statements = ir.get("cobol_statements", [])
    for stmt in cobol_statements:
        if stmt.get("statement_type") == "PERFORM":
            analysis["perform_statements"].append(stmt)
    
    return analysis

def validate_perform_migration(cobol_file: str, ir_file: str = None) -> Dict[str, Any]:
    """Validar la migración completa de sentencias PERFORM"""
    
    # Generar nombre del IR si no se proporciona
    if ir_file is None:
        base_name = os.path.splitext(os.path.basename(cobol_file))[0]
        ir_file = f"out/{base_name}_ir_clean.json"
    
    print("="*80)
    print("🔍 VALIDACIÓN DE CAPTURA DE SENTENCIAS PERFORM")
    print("="*80)
    print(f"📁 Archivo COBOL: {cobol_file}")
    print(f"📁 Archivo IR: {ir_file}")
    print()
    
    # Paso 1: Extraer PERFORM esperados del COBOL
    print("📋 PASO 1: Extraer PERFORM statements del archivo COBOL...")
    expected_performs = extract_expected_performs_from_cobol(cobol_file)
    print(f"✅ Encontrados {len(expected_performs)} PERFORM statements en el COBOL")
    print()
    
    # Paso 2: Analizar PERFORM en el IR
    print("📋 PASO 2: Analizar PERFORM statements en el IR...")
    ir_analysis = analyze_ir_performs(ir_file)
    
    if "error" in ir_analysis:
        print(f"❌ {ir_analysis['error']}")
        return {"error": ir_analysis["error"]}
    
    print(f"✅ Encontrados {ir_analysis['total_performs_in_ir']} PERFORM statements en el IR")
    print()
    
    # Paso 3: Comparación y validación
    print("📋 PASO 3: Comparación y validación...")
    
    validation_result = {
        "cobol_file": cobol_file,
        "ir_file": ir_file,
        "expected_performs_count": len(expected_performs),
        "ir_performs_count": ir_analysis["total_performs_in_ir"],
        "expected_performs": expected_performs,
        "ir_analysis": ir_analysis,
        "main_performs_status": {},
        "missing_performs": [],
        "validation_summary": {}
    }
    
    # Verificar PERFORM principales específicos
    main_performs_expected = ["1000-INICIO", "2000-PROCESO", "8000-FINAL"]
    
    print("🎯 PERFORM PRINCIPALES:")
    for main_perform in main_performs_expected:
        found_in_cobol = any(main_perform in perf.get("target", "") or main_perform in perf.get("clean_line", "") 
                            for perf in expected_performs)
        found_in_ir = any(main_perform in perf.get("target", "") or main_perform in str(perf) 
                         for perf in ir_analysis["perform_statements"])
        
        status = "✅" if found_in_ir else "❌"
        validation_result["main_performs_status"][main_perform] = {
            "found_in_cobol": found_in_cobol,
            "found_in_ir": found_in_ir,
            "status": "OK" if found_in_ir else "MISSING"
        }
        
        print(f"   {status} {main_perform}: COBOL={found_in_cobol}, IR={found_in_ir}")
    
    print()
    
    # Mostrar detalles de PERFORM encontrados
    print("📝 PERFORM STATEMENTS ENCONTRADOS EN COBOL:")
    for i, perform in enumerate(expected_performs, 1):
        print(f"   {i:2d}. Línea {perform['line_number']:4d}: {perform['type']:8s} - {perform['clean_line']}")
    
    print()
    print("📝 PERFORM STATEMENTS ENCONTRADOS EN IR:")
    if ir_analysis["perform_statements"]:
        for i, perform in enumerate(ir_analysis["perform_statements"], 1):
            perf_type = perform.get("perform_type", perform.get("type", "UNKNOWN"))
            target = perform.get("target", "N/A")
            raw = perform.get("raw", str(perform))[:80]
            print(f"   {i:2d}. Tipo: {perf_type:8s} - Target: {target:15s} - {raw}")
    else:
        print("   ⚠️  No se encontraron PERFORM statements en el IR")
    
    print()
    
    # Resumen de validación
    missing_count = sum(1 for status in validation_result["main_performs_status"].values() 
                       if status["status"] == "MISSING")
    
    validation_result["validation_summary"] = {
        "total_expected": len(expected_performs),
        "total_in_ir": ir_analysis["total_performs_in_ir"],
        "main_performs_missing": missing_count,
        "migration_rate": (ir_analysis["total_performs_in_ir"] / len(expected_performs) * 100) if expected_performs else 0,
        "main_performs_rate": ((len(main_performs_expected) - missing_count) / len(main_performs_expected) * 100),
        "overall_status": "PASS" if missing_count == 0 else "FAIL"
    }
    
    print("📊 RESUMEN DE VALIDACIÓN:")
    print(f"   📋 PERFORM esperados: {validation_result['validation_summary']['total_expected']}")
    print(f"   📋 PERFORM en IR: {validation_result['validation_summary']['total_in_ir']}")
    print(f"   📊 Tasa de migración: {validation_result['validation_summary']['migration_rate']:.1f}%")
    print(f"   🎯 PERFORM principales capturados: {validation_result['validation_summary']['main_performs_rate']:.1f}%")
    print(f"   ✅ Estado general: {validation_result['validation_summary']['overall_status']}")
    
    if missing_count > 0:
        print(f"   ⚠️  {missing_count} PERFORM principales NO capturados")
    
    print()
    print("="*80)
    
    return validation_result

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python validate_perform_parsing.py archivo.cob [archivo_ir.json]")
        print()
        print("Ejemplos:")
        print("  python validate_perform_parsing.py samples/C1040.cob")
        print("  python validate_perform_parsing.py samples/C1040.cob out/C1040_ir_clean.json")
        sys.exit(1)
    
    cobol_file = sys.argv[1]
    ir_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(cobol_file):
        print(f"❌ Error: Archivo COBOL no encontrado: {cobol_file}")
        sys.exit(1)
    
    # Ejecutar validación
    result = validate_perform_migration(cobol_file, ir_file)
    
    if "error" in result:
        sys.exit(1)
    
    # Guardar resultado en archivo JSON
    output_file = f"perform_validation_report_{os.path.splitext(os.path.basename(cobol_file))[0]}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Reporte guardado en: {output_file}")

if __name__ == "__main__":
    main()

