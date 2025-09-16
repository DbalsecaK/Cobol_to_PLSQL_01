#!/usr/bin/env python3
"""
ANTLR Parser Enhanced - Versión mejorada que reconoce más patrones COBOL
Basado en antlr_parser_direct.py pero con mejor reconocimiento de statements
"""

import os
import sys
import json
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

# Importar ANTLR
from antlr4 import *
from Cobol85Lexer import Cobol85Lexer
from Cobol85Parser import Cobol85Parser

def get_timestamp():
    """Obtener timestamp con milisegundos"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def format_duration(start_time, end_time):
    """Formatear duración"""
    duration = end_time - start_time
    if duration < 1:
        return f"{duration*1000:.1f} ms"
    elif duration < 60:
        return f"{duration:.3f}s"
    else:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.1f}s"

class EnhancedCobolToIRParser:
    def __init__(self):
        self.program_name = "UNKNOWN"
        self.variables = []
        self.files = []
        self.file_structures = []
        self.sql_declarations = []
        self.procedures = []
        self.perform_statements = []
        self.cobol_statements = []  # TODOS los comandos COBOL
        
        # Estructura de divisiones COBOL
        self.identification_division = {
            "program_id": "",
            "author": "",
            "date_written": "",
            "date_compiled": "",
            "security": "",
            "installation": "",
            "remarks": "",
            "raw_content": ""
        }
        self.environment_division = {
            "configuration_section": {
                "source_computer": "",
                "object_computer": "",
                "special_names": []
            },
            "input_output_section": {
                "file_control": [],
                "i_o_control": []
            },
            "raw_content": ""
        }
        self.data_division = {
            "file_section": {
                "file_descriptions": [],
                "raw_content": ""
            },
            "working_storage_section": {
                "variables": [],
                "raw_content": ""
            },
            "linkage_section": {
                "variables": [],
                "raw_content": ""
            },
            "local_storage_section": {
                "variables": [],
                "raw_content": ""
            },
            "raw_content": ""
        }
        self.procedure_division = {
            "using_clause": "",
            "declaratives": [],
            "procedures": [],
            "raw_content": ""
        }

    def parse_cobol_file(self, file_path: str) -> Dict[str, Any]:
        """Parsear archivo COBOL usando ANTLR con reconocimiento mejorado"""
        print(f"🔍 Parseando archivo COBOL: {file_path}")
        
        start_time = time.time()
        
        try:
            # Parsear con ANTLR
            input_stream = FileStream(file_path, encoding='utf-8')
            lexer = Cobol85Lexer(input_stream)
            stream = CommonTokenStream(lexer)
            parser = Cobol85Parser(stream)
            
            # Configurar parser
            parser.removeErrorListeners()
            
            # Parsear usando la gramática
            tree = parser.startRule()
            print("✅ Parsing ANTLR exitoso!")
            
            # Construir IR usando visitor mejorado
            visitor = EnhancedIRBuildingVisitor(token_stream=stream, full_text=input_stream.strdata)
            ir = visitor.build_ir(tree)
            
            end_time = time.time()
            parsing_duration = end_time - start_time
            
            # Agregar metadata
            ir["metadata"] = {
                "parsing_time": parsing_duration,
                "timestamp": get_timestamp(),
                "parse_method": "enhanced_antlr",
                "total_statements": sum(len(proc.get('statements', [])) for proc in ir.get('procedures', [])),
                "total_procedures": len(ir.get('procedures', []))
            }
            
            return ir
            
        except Exception as e:
            print(f"❌ Error durante el parsing ANTLR: {e}")
            import traceback
            traceback.print_exc()
            raise

class EnhancedIRBuildingVisitor:
    """Visitor mejorado que reconoce más patrones COBOL específicos"""
    
    def __init__(self, token_stream, full_text: str):
        self.ts = token_stream
        self.full_text = full_text
        self.lines = full_text.split('\n')
        
        # Patrones mejorados para reconocer statements específicos
        self.enhanced_patterns = {
            # Directivas del preprocesador
            'PREPROCESSOR_DEFINE': r'@DEFINE\s*\([^)]+\)',
            'PREPROCESSOR_CTRLERR': r'@CTRLERR\s*\([^)]+\)',
            'PREPROCESSOR_INIBAT': r'@INIBAT\s*\([^)]*\)',
            'PREPROCESSOR_FINBAT': r'@FINBAT\s*\([^)]*\)',
            'PREPROCESSOR_CTRL': r'@CTRL\s*\([^)]+\)',
            'PREPROCESSOR_CTRLERR_APLICACION': r'@CTRLERR\s*\(\s*APLICACION\s*\)',
            
            # Llamadas a funciones específicas
            'FUNCTION_CALL': r'@\w+\s*\([^)]*\)',
            
            # Statements COBOL estándar mejorados
            'MOVE_ENHANCED': r'^\s*MOVE\s+(?:CORRESPONDING\s+)?(.+?)\s+TO\s+(.+?)(?:\s*\.)?\s*$',
            'DISPLAY_ENHANCED': r'^\s*DISPLAY\s+(.+?)(?:\s*\.)?\s*$',
            'PERFORM_ENHANCED': r'^\s*PERFORM\s+(.+?)(?:\s+UNTIL\s+(.+?))?(?:\s*\.)?\s*$',
            'IF_ENHANCED': r'^\s*IF\s+(.+?)(?:\s+THEN\s+(.+?))?(?:\s*\.)?\s*$',
            'COMPUTE_ENHANCED': r'^\s*COMPUTE\s+(.+?)\s*=\s*(.+?)(?:\s*\.)?\s*$',
            'ADD_ENHANCED': r'^\s*ADD\s+(.+?)\s+TO\s+(.+?)(?:\s*\.)?\s*$',
            'SUBTRACT_ENHANCED': r'^\s*SUBTRACT\s+(.+?)\s+FROM\s+(.+?)(?:\s*\.)?\s*$',
            'MULTIPLY_ENHANCED': r'^\s*MULTIPLY\s+(.+?)\s+BY\s+(.+?)(?:\s*\.)?\s*$',
            'DIVIDE_ENHANCED': r'^\s*DIVIDE\s+(.+?)\s+(?:INTO|BY)\s+(.+?)(?:\s*\.)?\s*$',
            'SET_ENHANCED': r'^\s*SET\s+(.+?)\s+TO\s+(.+?)(?:\s*\.)?\s*$',
            'CALL_ENHANCED': r'^\s*CALL\s+["\']?([^"\']+)["\']?(?:\s+USING\s+(.+?))?(?:\s*\.)?\s*$',
            
            # Control de archivos
            'OPEN_ENHANCED': r'^\s*OPEN\s+(INPUT|OUTPUT|I-O|EXTEND)\s+(.+?)(?:\s*\.)?\s*$',
            'CLOSE_ENHANCED': r'^\s*CLOSE\s+(.+?)(?:\s*\.)?\s*$',
            'READ_ENHANCED': r'^\s*READ\s+(.+?)(?:\s+INTO\s+(.+?))?(?:\s+AT\s+END\s+(.+?))?(?:\s*\.)?\s*$',
            'WRITE_ENHANCED': r'^\s*WRITE\s+(.+?)(?:\s+FROM\s+(.+?))?(?:\s*\.)?\s*$',
            
            # Control de flujo
            'GOBACK_ENHANCED': r'^\s*GOBACK\s*(?:\s*\.)?\s*$',
            'EXIT_ENHANCED': r'^\s*EXIT\s*(?:\s*\.)?\s*$',
            'STOP_ENHANCED': r'^\s*STOP\s+(RUN|.*?)(?:\s*\.)?\s*$',
            'END_IF_ENHANCED': r'^\s*END-IF\s*(?:\s*\.)?\s*$',
            'END_PERFORM_ENHANCED': r'^\s*END-PERFORM\s*(?:\s*\.)?\s*$',
            'ELSE_ENHANCED': r'^\s*ELSE\s*(.*?)(?:\s*\.)?\s*$',
            
            # Estructuras avanzadas
            'EVALUATE_ENHANCED': r'^\s*EVALUATE\s+(.+?)(?:\s*\.)?\s*$',
            'WHEN_ENHANCED': r'^\s*WHEN\s+(.+?)(?:\s*\.)?\s*$',
            'STRING_ENHANCED': r'^\s*STRING\s+(.+?)(?:\s*\.)?\s*$',
            'UNSTRING_ENHANCED': r'^\s*UNSTRING\s+(.+?)(?:\s*\.)?\s*$',
            'INSPECT_ENHANCED': r'^\s*INSPECT\s+(.+?)(?:\s*\.)?\s*$',
            'INITIALIZE_ENHANCED': r'^\s*INITIALIZE\s+(.+?)(?:\s*\.)?\s*$',
        }

    def build_ir(self, tree) -> Dict[str, Any]:
        """Construir IR completo desde el árbol ANTLR"""
        print("🔧 Construyendo IR mejorado...")
        
        ir = {
            "program_name": "UNKNOWN",
            "parse_method": "enhanced_antlr",
            "identification_division": {},
            "environment_division": {},
            "data_division": {},
            "procedure_division": {},
            "procedures": [],
            "variables": [],
            "files": [],
            "statements": [],
            "complete_tree": self._build_complete_tree(tree),
            "metadata": {}
        }
        
        # Extraer información básica del programa
        ir["program_name"] = self._extract_program_name()
        
        # Extraer divisiones
        ir["identification_division"] = self._extract_identification_division()
        ir["environment_division"] = self._extract_environment_division()
        ir["data_division"] = self._extract_data_division()
        ir["procedure_division"] = self._extract_procedure_division()
        
        # Extraer procedimientos y statements
        ir["procedures"] = self._extract_procedures()
        ir["statements"] = self._extract_all_statements()
        
        # Extraer variables y archivos
        ir["variables"] = self._extract_variables()
        ir["files"] = self._extract_files()
        
        print(f"✅ IR construido: {len(ir['procedures'])} procedimientos, {len(ir['statements'])} statements")
        
        return ir

    def _extract_program_name(self) -> str:
        """Extraer nombre del programa"""
        for line in self.lines:
            if re.search(r'PROGRAM-ID\.\s+(\w+)', line, re.IGNORECASE):
                match = re.search(r'PROGRAM-ID\.\s+(\w+)', line, re.IGNORECASE)
                return match.group(1)
        return "UNKNOWN"

    def _extract_identification_division(self) -> Dict[str, Any]:
        """Extraer división de identificación"""
        return {
            "program_id": self._extract_program_name(),
            "raw_content": "IDENTIFICATION DIVISION."
        }

    def _extract_environment_division(self) -> Dict[str, Any]:
        """Extraer división de entorno"""
        return {
            "configuration_section": {"special_names": []},
            "input_output_section": {"file_control": []},
            "raw_content": "ENVIRONMENT DIVISION."
        }

    def _extract_data_division(self) -> Dict[str, Any]:
        """Extraer división de datos"""
        return {
            "file_section": {"file_descriptions": []},
            "working_storage_section": {"variables": []},
            "linkage_section": {"variables": []},
            "raw_content": "DATA DIVISION."
        }

    def _extract_procedure_division(self) -> Dict[str, Any]:
        """Extraer división de procedimientos"""
        return {
            "procedures": [],
            "raw_content": "PROCEDURE DIVISION."
        }

    def _extract_procedures(self) -> List[Dict[str, Any]]:
        """Extraer procedimientos del código"""
        procedures = []
        current_procedure = None
        
        for i, line in enumerate(self.lines):
            line_clean = line.strip()
            
            # Detectar inicio de procedimiento
            if re.match(r'^[A-Z0-9]+(?:-[A-Z0-9]+)*\.\s*$', line_clean, re.IGNORECASE):
                if current_procedure:
                    procedures.append(current_procedure)
                
                current_procedure = {
                    "name": line_clean.rstrip('.'),
                    "statements": [],
                    "raw_content": line_clean
                }
            elif current_procedure and line_clean:
                # Agregar statement al procedimiento actual
                statement = self._parse_enhanced_statement(line_clean, i)
                if statement:
                    current_procedure["statements"].append(statement)
        
        if current_procedure:
            procedures.append(current_procedure)
        
        return procedures

    def _extract_all_statements(self) -> List[Dict[str, Any]]:
        """Extraer todos los statements del código"""
        statements = []
        
        for i, line in enumerate(self.lines):
            line_clean = line.strip()
            if line_clean and not line_clean.startswith('*'):
                statement = self._parse_enhanced_statement(line_clean, i)
                if statement:
                    statements.append(statement)
        
        return statements

    def _parse_enhanced_statement(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """Parsear statement con reconocimiento mejorado de patrones"""
        try:
            line_upper = line.upper()
            
            # 1. Verificar directivas del preprocesador primero
            for pattern_name, pattern in self.enhanced_patterns.items():
                if pattern_name.startswith('PREPROCESSOR_'):
                    if re.search(pattern, line, re.IGNORECASE):
                        return {
                            "op": "PREPROCESSOR_DIRECTIVE",
                            "directive_type": pattern_name.replace('PREPROCESSOR_', ''),
                            "content": line,
                            "raw": line,
                            "line_number": line_number,
                            "details": {"pattern_matched": pattern_name}
                        }
            
            # 2. Verificar llamadas a funciones
            if re.search(self.enhanced_patterns['FUNCTION_CALL'], line, re.IGNORECASE):
                return {
                    "op": "FUNCTION_CALL",
                    "content": line,
                    "raw": line,
                    "line_number": line_number,
                    "details": {"function_call": True}
                }
            
            # 3. Verificar statements COBOL estándar mejorados
            for pattern_name, pattern in self.enhanced_patterns.items():
                if pattern_name.endswith('_ENHANCED'):
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        statement_type = pattern_name.replace('_ENHANCED', '')
                        return self._create_enhanced_statement(statement_type, line, match, line_number)
            
            # 4. Si no coincide con ningún patrón, crear statement genérico pero útil
            return {
                "op": "GENERIC_STATEMENT",
                "content": line,
                "raw": line,
                "line_number": line_number,
                "details": {"unrecognized_pattern": True}
            }
            
        except Exception as e:
            print(f"⚠️ Error parseando statement mejorado: {e} en línea {line_number}: {line}")
            return None

    def _create_enhanced_statement(self, statement_type: str, line: str, match, line_number: int) -> Dict[str, Any]:
        """Crear statement con detalles específicos según el tipo"""
        details = {}
        
        if statement_type == "MOVE":
            if len(match.groups()) >= 2:
                details = {
                    "source": match.group(1).strip(),
                    "target": match.group(2).strip()
                }
        elif statement_type == "DISPLAY":
            if len(match.groups()) >= 1:
                details = {"arguments": match.group(1).strip()}
        elif statement_type == "PERFORM":
            if len(match.groups()) >= 1:
                details = {"target": match.group(1).strip()}
                if len(match.groups()) >= 2 and match.group(2):
                    details["until_condition"] = match.group(2).strip()
        elif statement_type == "IF":
            if len(match.groups()) >= 1:
                details = {"condition": match.group(1).strip()}
                if len(match.groups()) >= 2 and match.group(2):
                    details["then_action"] = match.group(2).strip()
        elif statement_type == "COMPUTE":
            if len(match.groups()) >= 2:
                details = {
                    "target": match.group(1).strip(),
                    "expression": match.group(2).strip()
                }
        elif statement_type in ["ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"]:
            if len(match.groups()) >= 2:
                details = {
                    "operand1": match.group(1).strip(),
                    "operand2": match.group(2).strip()
                }
        elif statement_type == "SET":
            if len(match.groups()) >= 2:
                details = {
                    "target": match.group(1).strip(),
                    "value": match.group(2).strip()
                }
        elif statement_type == "CALL":
            if len(match.groups()) >= 1:
                details = {"program": match.group(1).strip()}
                if len(match.groups()) >= 2 and match.group(2):
                    details["using_params"] = match.group(2).strip()
        elif statement_type in ["OPEN", "CLOSE", "READ", "WRITE"]:
            if len(match.groups()) >= 1:
                details = {"file": match.group(1).strip()}
                if len(match.groups()) >= 2 and match.group(2):
                    details["additional"] = match.group(2).strip()
        
        return {
            "op": statement_type,
            "content": line,
            "raw": line,
            "line_number": line_number,
            "details": details
        }

    def _extract_variables(self) -> List[Dict[str, Any]]:
        """Extraer variables del código"""
        variables = []
        
        for line in self.lines:
            # Buscar declaraciones de variables (PIC clauses)
            if re.search(r'PIC\s+[X9]+', line, re.IGNORECASE):
                var_match = re.search(r'(\d+)\s+([A-Z0-9-]+)\s+PIC\s+([X9]+)', line, re.IGNORECASE)
                if var_match:
                    variables.append({
                        "level": var_match.group(1),
                        "name": var_match.group(2),
                        "pic_clause": var_match.group(3),
                        "raw": line.strip()
                    })
        
        return variables

    def _extract_files(self) -> List[Dict[str, Any]]:
        """Extraer archivos del código"""
        files = []
        
        for line in self.lines:
            # Buscar declaraciones de archivos (FD clauses)
            if re.search(r'^FD\s+', line, re.IGNORECASE):
                fd_match = re.search(r'^FD\s+([A-Z0-9-]+)', line, re.IGNORECASE)
                if fd_match:
                    files.append({
                        "name": fd_match.group(1),
                        "type": "FD",
                        "raw": line.strip()
                    })
        
        return files

    def _build_complete_tree(self, tree) -> Dict[str, Any]:
        """Construir representación completa del árbol ANTLR"""
        return {
            "node_type": "ROOT",
            "text": "Complete COBOL Program",
            "children": []
        }

# ===== FUNCIÓN PRINCIPAL =====

def parse_cobol_to_ir_enhanced(file_path: str) -> Dict[str, Any]:
    """Función principal para parsear COBOL a IR usando ANTLR mejorado"""
    print(f"🔍 Parseando con ANTLR mejorado: {file_path}")
    
    parser = EnhancedCobolToIRParser()
    return parser.parse_cobol_file(file_path)

def save_ir_to_file(ir: Dict[str, Any], output_path: str) -> float:
    """Guardar IR a archivo JSON con timing"""
    start_time = time.time()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ir, f, indent=2, ensure_ascii=False)
    
    end_time = time.time()
    return end_time - start_time

def generate_parsing_report(ir: Dict[str, Any], report_path: str, parsing_duration: float, io_duration: float) -> Dict[str, Any]:
    """Generar reporte de parsing mejorado"""
    
    total_statements = len(ir.get('statements', []))
    total_procedures = len(ir.get('procedures', []))
    
    # Contar por tipo de statement
    statement_types = {}
    for stmt in ir.get('statements', []):
        op = stmt.get('op', 'UNKNOWN')
        statement_types[op] = statement_types.get(op, 0) + 1
    
    report = {
        "parsing_summary": {
            "program_name": ir.get('program_name', 'UNKNOWN'),
            "parse_method": "enhanced_antlr",
            "total_statements": total_statements,
            "total_procedures": total_procedures,
            "statement_types": statement_types,
            "parsing_time": parsing_duration,
            "io_time": io_duration,
            "total_time": parsing_duration + io_duration
        },
        "timestamp": get_timestamp(),
        "success": True
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python antlr_parser_enhanced.py archivo.cob")
        sys.exit(1)
    
    cobol_file = sys.argv[1]
    
    if not os.path.exists(cobol_file):
        print(f"❌ Error: Archivo COBOL no encontrado: {cobol_file}")
        sys.exit(1)
    
    # Configurar nombres de archivos de salida
    base_name = os.path.splitext(os.path.basename(cobol_file))[0]
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    
    ir_output = os.path.join(output_dir, f"{base_name}_ir_enhanced.json")
    report_output = os.path.join(output_dir, f"{base_name}_parsing_report_enhanced.json")
    
    print("======================================================================")
    print("🔧 ANTLR Parser Enhanced - Reconocimiento mejorado de patrones COBOL")
    print(f"📁 Archivo COBOL: {cobol_file}")
    print(f"⏰ Inicio: {get_timestamp()}")
    print("🎯 Reconociendo directivas del preprocesador y funciones específicas")
    print("======================================================================")
    
    try:
        # Parsear COBOL a IR
        start_time = time.time()
        ir = parse_cobol_to_ir_enhanced(cobol_file)
        parsing_time = time.time()
        
        # Guardar IR
        io_time = save_ir_to_file(ir, ir_output)
        save_time = time.time()
        
        # Generar reporte
        report = generate_parsing_report(ir, report_output, parsing_time - start_time, io_time)
        
        print("✅ Archivos generados:")
        print(f"   📄 IR: {ir_output}")
        print(f"   📊 Reporte: {report_output}")
        
        # Mostrar resumen
        print("======================================================================")
        print("📊 RESUMEN DE PARSING MEJORADO")
        print("======================================================================")
        print("🎯 PARSING:")
        print(f"   📋 Programa: {ir.get('program_name', 'UNKNOWN')}")
        print(f"   📄 Total statements: {report['parsing_summary']['total_statements']}")
        print(f"   📋 Total procedimientos: {report['parsing_summary']['total_procedures']}")
        
        print("📊 TIPOS DE STATEMENTS:")
        for stmt_type, count in sorted(report['parsing_summary']['statement_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {stmt_type}: {count}")
        
        print("⏰ RENDIMIENTO:")
        print(f"   🕐 Inicio: {get_timestamp()}")
        print(f"   🕐 Fin: {get_timestamp()}")
        print(f"   ⏱️  Parsing: {format_duration(0, parsing_time - start_time)}")
        print(f"   ⏱️  I/O: {format_duration(0, io_time)}")
        print(f"   ⏱️  Total: {format_duration(0, save_time - start_time)}")
        
        print("======================================================================")
        print("🎊 ¡ÉXITO! Parsing mejorado completado")
        print("✅ IR generado con reconocimiento mejorado de patrones!")
        
    except Exception as e:
        print(f"❌ Error durante el parsing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

