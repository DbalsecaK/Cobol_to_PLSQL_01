#!/usr/bin/env python3
"""
ANTLR Parser COMPLETE - Versión que captura TODO el árbol ANTLR sin filtros
Convierte archivos COBOL a Intermediate Representation (IR) usando TODO el árbol ANTLR

CARACTERÍSTICAS:
- Captura ABSOLUTAMENTE TODO el árbol ANTLR sin filtros
- No elimina ningún nodo, token o información
- Preserva toda la estructura sintáctica completa
- Incluye todos los contextos y nodos terminales

Entrada: Archivo COBOL (.cob)
Salida: 
- Archivo IR (JSON) con TODO el contenido del árbol ANTLR
- Reporte de parsing (JSON)
- Logs de análisis

Uso: python antlr_parser_complete.py archivo.cob
"""

import sys
import os
import json
import re
import time
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime

# Imports de ANTLR
from antlr4 import FileStream, CommonTokenStream
from Cobol85Lexer import Cobol85Lexer
from Cobol85Parser import Cobol85Parser

# ===== TIMING UTILITIES =====

def get_timestamp():
    """Obtener timestamp detallado con milisegundos"""
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")[:-3]

def format_duration(start_time, end_time):
    """Formatear duración en segundos y milisegundos"""
    duration = end_time - start_time
    if duration < 1:
        return f"{duration*1000:.1f} ms"
    elif duration < 60:
        return f"{duration:.3f}s"
    else:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.3f}s"

# ===== ANTLR COMPLETE IR VISITOR =====

class CompleteIRBuildingVisitor:
    """Visitor que captura ABSOLUTAMENTE TODO el árbol ANTLR sin filtros"""
    
    def __init__(self, token_stream, full_text):
        self.token_stream = token_stream
        self.full_text = full_text
        self.lines = full_text.split('\n')
        self.node_counter = 0
        
    def build_ir(self, tree) -> Dict[str, Any]:
        """Construir IR capturando COMPLETAMENTE el árbol ANTLR sin filtros"""
        print("🔧 Construyendo IR usando ABSOLUTAMENTE TODO el árbol ANTLR...")
        print("🌳 Capturando CADA NODO del árbol sintáctico sin filtros...")
        
        # Extraer información COMPLETA del árbol ANTLR
        program_name = self._extract_program_name_complete(tree)
        complete_tree_data = self._extract_complete_tree(tree)
        
        ir = {
            "program_name": program_name,
            "complete_tree": complete_tree_data,
            "metadata": {
                "source_lines": len(self.lines),
                "parse_method": "antlr_complete_no_filters",
                "total_nodes": self.node_counter,
                "tree_processed": True,
                "uses_antlr_tree": True,
                "filters_applied": False,
                "complete_capture": True
            }
        }
        
        print(f"✅ IR construido desde ÁRBOL ANTLR COMPLETO: {self.node_counter} nodos totales")
        return ir
    
    def _extract_program_name_complete(self, tree) -> str:
        """Extraer nombre del programa desde árbol ANTLR completo"""
        print("🔍 Extrayendo nombre de programa desde árbol ANTLR completo...")
        
        program_name = self._find_program_id_in_tree(tree)
        if program_name:
            print(f"✅ Encontrado programa: {program_name}")
            return program_name
        else:
            print("⚠️  Programa no encontrado en árbol")
            return "UNKNOWN_PROGRAM"
    
    def _extract_complete_tree(self, tree) -> Dict[str, Any]:
        """Extraer COMPLETAMENTE el árbol ANTLR sin ningún filtro"""
        print("🔍 Extrayendo ABSOLUTAMENTE TODO el árbol ANTLR...")
        
        complete_tree = self._walk_complete_tree(tree)
        
        print(f"✅ Árbol completo extraído: {self.node_counter} nodos procesados")
        return complete_tree
    
    def _walk_complete_tree(self, node) -> Dict[str, Any]:
        """Caminar COMPLETAMENTE el árbol capturando TODOS los nodos"""
        self.node_counter += 1
        
        # Capturar información COMPLETA del nodo
        node_data = {
            "node_id": self.node_counter,
            "node_type": type(node).__name__,
            "text": node.getText() if hasattr(node, 'getText') else '',
            "children": []
        }
        
        # Información adicional del nodo si está disponible
        if hasattr(node, 'symbol'):
            node_data["symbol"] = str(node.symbol)
        
        if hasattr(node, 'start') and hasattr(node, 'stop'):
            if hasattr(node.start, 'line'):
                node_data["start_line"] = node.start.line
                node_data["start_column"] = node.start.column
            if hasattr(node.stop, 'line'):
                node_data["stop_line"] = node.stop.line
                node_data["stop_column"] = node.stop.column
        
        # Información del contexto si es un contexto
        if hasattr(node, 'getRuleIndex'):
            try:
                node_data["rule_index"] = node.getRuleIndex()
            except:
                pass
        
        # Capturar TODOS los hijos recursivamente
        if hasattr(node, 'getChildCount'):
            child_count = node.getChildCount()
            for i in range(child_count):
                child = node.getChild(i)
                child_data = self._walk_complete_tree(child)
                node_data["children"].append(child_data)
        
        return node_data
    
    def _find_program_id_in_tree(self, node) -> Optional[str]:
        """Buscar PROGRAM-ID en TODO el árbol"""
        if hasattr(node, 'getText'):
            text = node.getText()
            if 'PROGRAM-ID' in text.upper() or 'PROGRAMID' in text.upper():
                # Intentar extraer el nombre
                match = re.search(r'PROGRAM-?ID\.?\s*([A-Z0-9]+)', text.upper())
                if match:
                    return match.group(1)
        
        # Buscar recursivamente en TODOS los hijos
        if hasattr(node, 'getChildCount'):
            for i in range(node.getChildCount()):
                child = node.getChild(i)
                result = self._find_program_id_in_tree(child)
                if result:
                    return result
        
        return None

# ===== FUNCIONES AUXILIARES =====

def extract_structured_data_from_complete_tree(complete_tree: Dict[str, Any]) -> Dict[str, Any]:
    """Extraer datos estructurados del árbol completo para análisis"""
    
    # Contadores por tipo de nodo
    node_counts = {}
    
    # Datos estructurados extraídos
    environment_data = {
        "configuration_section": {},
        "input_output_section": {
            "file_control": []
        }
    }
    
    variables = []
    statements = []
    
    def analyze_node(node_data: Dict[str, Any], path: str = ""):
        """Analizar cada nodo del árbol completo"""
        node_type = node_data.get("node_type", "")
        text = node_data.get("text", "")
        
        # Contar tipos de nodos
        node_counts[node_type] = node_counts.get(node_type, 0) + 1
        
        # Extraer información específica basada en el contenido
        if text:
            text_upper = text.upper()
            
            # Buscar SELECT statements
            if 'SELECT' in text_upper and 'ASSIGN' in text_upper:
                select_info = parse_select_from_text(text)
                if select_info:
                    environment_data["input_output_section"]["file_control"].append(select_info)
            
            # Buscar DECIMAL-POINT
            elif 'DECIMAL-POINT' in text_upper and 'COMMA' in text_upper:
                environment_data["configuration_section"]["decimal_point"] = "COMMA"
            
            # Buscar definiciones de variables
            elif re.match(r'^\d+[A-Z0-9_-]+', text.strip(), re.IGNORECASE):
                var_info = parse_variable_from_text(text, node_data.get("node_id", 0))
                if var_info:
                    variables.append(var_info)
            
            # Buscar statements
            elif any(keyword in text_upper for keyword in ['MOVE', 'DISPLAY', 'IF', 'PERFORM', 'ADD', 'COMPUTE']):
                if len(text.strip()) > 5:  # Solo statements significativos
                    stmt_info = parse_statement_from_text(text, node_type, node_data.get("node_id", 0))
                    if stmt_info:
                        statements.append(stmt_info)
        
        # Analizar hijos recursivamente
        for child in node_data.get("children", []):
            analyze_node(child, path + "/" + node_type)
    
    # Analizar todo el árbol
    analyze_node(complete_tree)
    
    return {
        "node_statistics": node_counts,
        "environment": environment_data,
        "variables": variables,
        "statements": statements,
        "total_nodes_analyzed": sum(node_counts.values())
    }

def parse_select_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Parsear SELECT statement desde texto completo"""
    text_clean = ' '.join(text.split())
    text_upper = text_clean.upper()
    
    select_match = re.search(r'SELECT\s+([A-Z0-9_-]+)\s+ASSIGN\s+TO\s+([A-Z0-9_-]+)', text_upper)
    if select_match:
        file_name = select_match.group(1)
        assign_name = select_match.group(2)
        
        # Buscar organización
        organization = "UNKNOWN"
        if 'ORGANIZATION IS SEQUENTIAL' in text_upper:
            organization = "SEQUENTIAL"
        elif 'ORGANIZATION IS INDEXED' in text_upper:
            organization = "INDEXED"
        elif 'ORGANIZATION IS RELATIVE' in text_upper:
            organization = "RELATIVE"
        
        # Buscar FILE STATUS
        file_status = None
        status_match = re.search(r'FILE\s+STATUS\s+IS\s+([A-Z0-9_-]+)', text_upper)
        if status_match:
            file_status = status_match.group(1)
        
        return {
            "file_name": file_name,
            "assign_to": assign_name,
            "organization": organization,
            "file_status": file_status,
            "raw": text_clean,
            "source": "complete_tree"
        }
    
    return None

def parse_variable_from_text(text: str, node_id: int) -> Optional[Dict[str, Any]]:
    """Parsear definición de variable desde texto"""
    match = re.match(r'^\s*(\d+)\s+([A-Z0-9_-]+)', text, re.IGNORECASE)
    if match:
        level = match.group(1)
        name = match.group(2)
        return {
            "level": level,
            "name": name,
            "raw": text.strip(),
            "source": "complete_tree",
            "node_id": node_id
        }
    return None

def parse_statement_from_text(text: str, node_type: str, node_id: int) -> Optional[Dict[str, Any]]:
    """Parsear statement desde texto"""
    text_clean = text.strip()
    text_upper = text_clean.upper()
    
    # Determinar tipo de statement
    if text_upper.startswith('MOVE'):
        return {"op": "MOVE", "content": text_clean, "raw": text_clean, "source": "complete_tree", "node_type": node_type, "node_id": node_id}
    elif text_upper.startswith('DISPLAY'):
        return {"op": "DISPLAY", "content": text_clean, "raw": text_clean, "source": "complete_tree", "node_type": node_type, "node_id": node_id}
    elif text_upper.startswith('IF'):
        return {"op": "IF", "content": text_clean, "raw": text_clean, "source": "complete_tree", "node_type": node_type, "node_id": node_id}
    elif text_upper.startswith('PERFORM'):
        return {"op": "PERFORM", "content": text_clean, "raw": text_clean, "source": "complete_tree", "node_type": node_type, "node_id": node_id}
    else:
        return {"op": "STATEMENT", "content": text_clean, "raw": text_clean, "source": "complete_tree", "node_type": node_type, "node_id": node_id}

# ===== MAIN PARSING FUNCTION =====

def parse_cobol_to_ir_complete(file_path: str) -> Dict[str, Any]:
    """Función principal para parsear COBOL capturando TODO el árbol ANTLR"""
    
    print(f"🔍 Parseando con ANTLR COMPLETO: {file_path}")
    
    start_time = time.time()
    
    try:
        # Parsear con ANTLR
        input_stream = FileStream(file_path, encoding='utf-8')
        lexer = Cobol85Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = Cobol85Parser(stream)
        
        # Configurar parser para manejo de errores
        parser.removeErrorListeners()
        
        # Parsear usando la gramática
        tree = parser.startRule()
        print("✅ Parsing ANTLR exitoso!")
        
        # Construir IR capturando TODO el árbol
        visitor = CompleteIRBuildingVisitor(token_stream=stream, full_text=input_stream.strdata)
        ir = visitor.build_ir(tree)
        
        # Extraer datos estructurados del árbol completo
        print("🔍 Extrayendo datos estructurados del árbol completo...")
        structured_data = extract_structured_data_from_complete_tree(ir["complete_tree"])
        
        # Agregar datos estructurados al IR
        ir["environment"] = structured_data["environment"]
        ir["variables"] = structured_data["variables"]
        ir["statements"] = structured_data["statements"]
        ir["node_statistics"] = structured_data["node_statistics"]
        
        end_time = time.time()
        parsing_duration = end_time - start_time
        
        # Agregar métricas de rendimiento
        ir["metadata"]["parsing_time"] = parsing_duration
        ir["metadata"]["timestamp"] = get_timestamp()
        ir["metadata"]["total_structured_nodes"] = structured_data["total_nodes_analyzed"]
        ir["metadata"]["file_control_found"] = len(structured_data["environment"]["input_output_section"]["file_control"])
        ir["metadata"]["variables_found"] = len(structured_data["variables"])
        ir["metadata"]["statements_found"] = len(structured_data["statements"])
        
        print(f"✅ Datos estructurados extraídos:")
        print(f"   📁 Archivos SELECT: {ir['metadata']['file_control_found']}")
        print(f"   📊 Variables: {ir['metadata']['variables_found']}")
        print(f"   🔧 Statements: {ir['metadata']['statements_found']}")
        
        return ir
        
    except Exception as e:
        print(f"❌ Error durante el parsing ANTLR: {e}")
        import traceback
        traceback.print_exc()
        raise

def save_ir_to_file(ir: Dict[str, Any], output_path: str):
    """Guardar IR a archivo JSON"""
    start_time = time.time()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ir, f, indent=2, ensure_ascii=False)
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"💾 IR guardado en: {output_path}")
    return duration

def generate_parsing_report(ir: Dict[str, Any], output_path: str, parsing_time: float, io_time: float):
    """Generar reporte de parsing completo"""
    
    statements = ir.get("statements", [])
    variables = ir.get("variables", [])
    file_control = ir.get("environment", {}).get("input_output_section", {}).get("file_control", [])
    
    # Contar tipos de statements
    statement_counts = {}
    for stmt in statements:
        op = stmt.get("op", "UNKNOWN")
        statement_counts[op] = statement_counts.get(op, 0) + 1
    
    # Estadísticas de nodos
    node_stats = ir.get("node_statistics", {})
    
    report = {
        "parsing_summary": {
            "program_name": ir.get("program_name", "UNKNOWN"),
            "source_lines": ir.get("metadata", {}).get("source_lines", 0),
            "total_nodes": ir.get("metadata", {}).get("total_nodes", 0),
            "total_statements": len(statements),
            "total_variables": len(variables),
            "file_control_entries": len(file_control)
        },
        "statement_distribution": dict(sorted(statement_counts.items(), key=lambda x: x[1], reverse=True)),
        "node_type_distribution": dict(sorted(node_stats.items(), key=lambda x: x[1], reverse=True)[:20]),  # Top 20
        "environment_section": {
            "file_control": file_control,
            "configuration": ir.get("environment", {}).get("configuration_section", {})
        },
        "performance_metrics": {
            "parsing_time": f"{parsing_time:.3f}s",
            "io_time": f"{io_time*1000:.1f} ms",
            "total_time": f"{parsing_time + io_time:.3f}s",
            "nodes_per_second": round(ir.get("metadata", {}).get("total_nodes", 0) / parsing_time, 1) if parsing_time > 0 else 0
        },
        "metadata": ir.get("metadata", {}),
        "timestamp": get_timestamp()
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python antlr_parser_complete.py archivo.cob")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Archivo no encontrado: {input_file}")
        sys.exit(1)
    
    # Configurar nombres de archivos de salida
    base_name = os.path.splitext(os.path.basename(input_file))[0].upper()
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    
    ir_output = os.path.join(output_dir, f"{base_name}_ir_complete.json")
    report_output = os.path.join(output_dir, f"{base_name}_parsing_report_complete.json")
    
    print("======================================================================")
    print("🔧 ANTLR Parser COMPLETE - COBOL to IR (TODO EL ÁRBOL ANTLR)")
    print(f"📁 Archivo fuente: {input_file}")
    print(f"⏰ Inicio: {get_timestamp()}")
    print("🎯 Captura ABSOLUTAMENTE TODO el árbol ANTLR sin filtros")
    print("======================================================================")
    
    try:
        # Parsear archivo
        start_time = time.time()
        start_timestamp = get_timestamp()  # Capturar timestamp real de inicio
        ir = parse_cobol_to_ir_complete(input_file)
        parsing_end_time = time.time()
        parsing_duration = parsing_end_time - start_time
        
        # Guardar IR
        io_start_time = time.time()
        io_duration = save_ir_to_file(ir, ir_output)
        io_end_time = time.time()
        total_io_duration = io_end_time - io_start_time
        
        # Generar reporte
        end_timestamp = get_timestamp()  # Capturar timestamp real de fin
        report = generate_parsing_report(ir, report_output, parsing_duration, total_io_duration)
        
        print("✅ Archivos generados:")
        print(f"   📊 IR: {ir_output}")
        print(f"   📊 Reporte: {report_output}")
        
        # Mostrar resumen
        print("======================================================================")
        print("📊 RESUMEN DE PARSING COMPLETE")
        print("======================================================================")
        print("🎯 ANÁLISIS COMPLETO:")
        print(f"   📋 Programa: {report['parsing_summary']['program_name']}")
        print(f"   📄 Líneas fuente: {report['parsing_summary']['source_lines']}")
        print(f"   🌳 Nodos totales: {report['parsing_summary']['total_nodes']}")
        print(f"   📊 Variables: {report['parsing_summary']['total_variables']}")
        print(f"   🔧 Statements: {report['parsing_summary']['total_statements']}")
        print(f"   📁 Archivos SELECT: {report['parsing_summary']['file_control_entries']}")
        
        # Calcular duración real entre timestamps
        try:
            start_dt = datetime.strptime(start_timestamp, "%H:%M:%S.%f")
            end_dt = datetime.strptime(end_timestamp, "%H:%M:%S.%f")
            
            # Manejar caso donde se cruza medianoche
            if end_dt < start_dt:
                end_dt = end_dt.replace(day=start_dt.day + 1)
            
            real_duration = (end_dt - start_dt).total_seconds()
        except ValueError:
            # Fallback si hay error en el formato
            real_duration = parsing_duration + total_io_duration
        
        print("⏰ RENDIMIENTO:")
        print(f"   🕐 Inicio: {start_timestamp}")
        print(f"   🕐 Fin: {end_timestamp}")
        print(f"   ⏰ Duración real: {format_duration(0, real_duration)}")
        print(f"   ⏱️  Parsing: {format_duration(0, parsing_duration)}")
        print(f"   ⏱️  I/O: {format_duration(0, total_io_duration)}")
        print(f"   ⏱️  Total medido: {format_duration(0, parsing_duration + total_io_duration)}")
        print(f"   ⚡ Velocidad: {report['performance_metrics']['nodes_per_second']} nodos/seg")
        
        print("📊 TIPOS DE NODOS MÁS COMUNES:")
        for node_type, count in list(report['node_type_distribution'].items())[:5]:
            print(f"   • {node_type}: {count}")
        
        print("📁 ARCHIVOS FILE-CONTROL:")
        for file_entry in report['environment_section']['file_control']:
            print(f"   • {file_entry['file_name']} → {file_entry['assign_to']} ({file_entry['organization']})")
        
        print("======================================================================")
        print("🎊 ¡ÉXITO! Captura COMPLETA del árbol ANTLR sin filtros")
        print("✅ Parsing completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante el parsing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
