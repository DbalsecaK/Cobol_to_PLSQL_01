#!/usr/bin/env python3
"""
ANTLR Parser DIRECT - Versión que usa parsing directo sin ANTLR
Convierte archivos COBOL a Intermediate Representation (IR) usando parsing directo

CARACTERÍSTICAS:
- Parsing directo de formato fijo COBOL sin dependencias ANTLR
- Extracción completa de variables, procedimientos y divisiones
- Procesamiento rápido y eficiente para archivos grandes
- IR optimizado compatible con generadores SQL

Uso: python antlr_parser_direct.py archivo.cob
"""

import sys
import os
import json
import re
import time
import tempfile
from typing import Any, Dict, List, Optional
from datetime import datetime

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
        return f"{minutes}m {seconds:.1f}s"

class CobolToIRParserDirect:
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
        """Parse COBOL file usando parsing directo"""
        try:
            # Verificar tamaño del archivo
            file_size = os.path.getsize(file_path)
            print(f"📁 Tamaño de archivo: {file_size / (1024*1024):.1f} MB")
            
            # Procesar archivo línea por línea
            with open(file_path, 'r', encoding='utf-8') as f:
                self._process_file_direct(f)
            
            # Construir IR optimizado
            ir = {
                "program": self.program_name,
                "parse_method": "direct_parsing",
                
                # Divisiones COBOL preservadas
                "identification_division": self.identification_division,
                "environment_division": self.environment_division,
                "data_division": self.data_division,
                "procedure_division": self.procedure_division,
                
                # Datos estructurados para SQL (retrocompatibilidad)
                "variables": self.variables,
                "files": self.files,
                "file_structures": self.file_structures,
                "sql_declarations": self.sql_declarations,
                "procedures": self.procedures,
                "perform_statements": self.perform_statements,
                "cobol_statements": self.cobol_statements,
                
                "optimization_stats": {
                    "total_variables": len(self.variables),
                    "total_procedures": len(self.procedures),
                    "total_files": len(self.files),
                    "total_statements": sum(len(proc.get('statements', [])) for proc in self.procedures),
                    "total_performs": len(self.perform_statements),
                    "total_sql_statements": len(self.sql_declarations),
                    "total_cobol_statements": len(self.cobol_statements),
                    "file_size_mb": file_size / (1024*1024),
                    "processing_mode": "direct_parsing"
                }
            }
            
            return ir
            
        except Exception as e:
            print(f"❌ Error parseando {file_path}: {str(e)}")
            return {
                "program": self.program_name,
                "parse_method": "direct_parsing_failed",
                "error": str(e),
                "variables": self.variables,
                "files": self.files,
                "file_structures": self.file_structures,
                "sql_declarations": self.sql_declarations,
                "procedures": self.procedures,
                "perform_statements": self.perform_statements,
                "cobol_statements": self.cobol_statements,
                "identification_division": self.identification_division,
                "environment_division": self.environment_division,
                "data_division": self.data_division,
                "procedure_division": self.procedure_division
            }

    def _process_file_direct(self, file_handle):
        """Procesar archivo COBOL directamente línea por línea"""
        # Estados de parsing
        in_identification = False
        in_environment = False
        in_file_control = False
        in_data_division = False
        in_file_section = False
        in_working_storage = False
        in_linkage = False
        in_procedure_division = False
        
        # Almacenamiento de contenido raw
        identification_lines = []
        environment_lines = []
        data_division_lines = []
        file_section_lines = []
        working_storage_lines = []
        linkage_lines = []
        procedure_lines = []
        
        # Estado para parsing de SELECT statements
        current_select = None
        select_buffer = []
        
        # Estado para parsing de FD (File Descriptions) 
        current_fd = None
        fd_buffer = []
        
        # Estado para parsing de EXEC SQL statements
        in_exec_sql = False
        current_exec_sql = None
        exec_sql_buffer = []
        
        # Estado para tracking de procedimientos actuales
        current_procedure = None
        
        line_count = 0
        
        for line in file_handle:
            line_count += 1
            if line_count % 500 == 0:
                print(f"📊 Procesando línea {line_count}...")
            
            # Procesar formato fijo COBOL
            processed_line = self._process_fixed_format_line(line).strip()
            
            # Almacenar contenido raw según el estado
            if in_identification:
                identification_lines.append(processed_line)
            elif in_environment:
                environment_lines.append(processed_line)
            elif in_data_division:
                data_division_lines.append(processed_line)
                if in_file_section:
                    file_section_lines.append(processed_line)
                elif in_working_storage:
                    working_storage_lines.append(processed_line)
                elif in_linkage:
                    linkage_lines.append(processed_line)
            elif in_procedure_division:
                procedure_lines.append(processed_line)
            
            if not processed_line or processed_line.startswith('*'):
                continue
            
            # Detectar divisiones y secciones
            if 'IDENTIFICATION DIVISION' in processed_line.upper():
                in_identification = True
                in_environment = False
                in_file_control = False
                identification_lines.append(processed_line)
                continue
            elif 'ENVIRONMENT DIVISION' in processed_line.upper():
                in_identification = False
                in_environment = True
                in_file_control = False
                environment_lines.append(processed_line)
                continue
            elif 'DATA DIVISION' in processed_line.upper():
                in_identification = False
                in_environment = False
                in_file_control = False
                in_data_division = True
                data_division_lines.append(processed_line)
                print("📊 Entrando en DATA DIVISION")
                continue
            elif 'PROCEDURE DIVISION' in processed_line.upper():
                in_identification = False
                in_environment = False
                in_file_control = False
                in_data_division = False
                in_file_section = False
                in_working_storage = False
                in_linkage = False
                in_procedure_division = True
                procedure_lines.append(processed_line)
                print("🔧 Entrando en PROCEDURE DIVISION")
                
                # Extraer USING clause
                using_match = re.search(r'PROCEDURE\s+DIVISION\s+USING\s+([^\n.]*)', processed_line, re.IGNORECASE)
                if using_match:
                    self.procedure_division["using_clause"] = using_match.group(1).strip()
                continue
            
            # Detectar FILE-CONTROL dentro de ENVIRONMENT DIVISION
            if in_environment and 'FILE-CONTROL' in processed_line.upper():
                in_file_control = True
                print("📁 Entrando en FILE-CONTROL section")
                continue
            
            # Detectar secciones dentro de DATA DIVISION
            if in_data_division:
                if 'FILE SECTION' in processed_line.upper():
                    in_file_section = True
                    in_working_storage = False
                    in_linkage = False
                    file_section_lines.append(processed_line)
                    continue
                elif 'WORKING-STORAGE SECTION' in processed_line.upper():
                    in_file_section = False
                    in_working_storage = True
                    in_linkage = False
                    working_storage_lines.append(processed_line)
                    print("📊 Entrando en WORKING-STORAGE SECTION")
                    continue
                elif 'LINKAGE SECTION' in processed_line.upper():
                    in_file_section = False
                    in_working_storage = False
                    in_linkage = True
                    linkage_lines.append(processed_line)
                    print("📊 Entrando en LINKAGE SECTION")
                    continue
            
            # Extraer PROGRAM-ID
            if not self.program_name or self.program_name == "UNKNOWN":
                # Buscar PROGRAM-ID
                match = re.search(r'PROGRAM-ID\.\s*([A-Z0-9\-_]+)', processed_line, re.IGNORECASE)
                if match:
                    self.program_name = match.group(1).upper()
                    self.identification_division["program_id"] = self.program_name
                    print(f"✅ Programa encontrado: {self.program_name}")
                
                # Buscar @INTERFAZ como fallback
                match = re.search(r'@INTERFAZ\s*\(\s*([^,\)]+)', processed_line, re.IGNORECASE)
                if match:
                    self.program_name = match.group(1).strip().upper()
                    self.identification_division["program_id"] = self.program_name
                    print(f"✅ Programa encontrado (INTERFAZ): {self.program_name}")
            
            # Parsear FD declarations en FILE SECTION
            if in_file_section:
                # Detectar inicio de FD
                fd_match = re.match(r'^\s*FD\s+([A-Z0-9\-_]+)', processed_line, re.IGNORECASE)
                if fd_match:
                    # Si hay FD previo en buffer, procesarlo
                    if current_fd and fd_buffer:
                        self._process_fd_statement(current_fd, fd_buffer)
                    
                    # Iniciar nuevo FD
                    current_fd = {
                        "file_name": fd_match.group(1),
                        "recording_mode": "",
                        "block_contains": "",
                        "label_record": "",
                        "data_record": "",
                        "record_layouts": [],
                        "raw_lines": []
                    }
                    fd_buffer = [processed_line]
                    continue
                
                # Si estamos en un FD, acumular líneas
                elif current_fd:
                    fd_buffer.append(processed_line)
                    
                    # Detectar propiedades del FD
                    if 'RECORDING MODE IS' in processed_line.upper():
                        rec_match = re.search(r'RECORDING\s+MODE\s+IS\s+([A-Z]+)', processed_line, re.IGNORECASE)
                        if rec_match:
                            current_fd["recording_mode"] = rec_match.group(1)
                    
                    elif 'BLOCK CONTAINS' in processed_line.upper():
                        block_match = re.search(r'BLOCK\s+CONTAINS\s+([^R\n]+)', processed_line, re.IGNORECASE)
                        if block_match:
                            current_fd["block_contains"] = block_match.group(1).strip()
                    
                    elif 'LABEL RECORD' in processed_line.upper():
                        label_match = re.search(r'LABEL\s+RECORD[^.]*?([A-Z\s]+)', processed_line, re.IGNORECASE)
                        if label_match:
                            current_fd["label_record"] = label_match.group(1).strip()
                    
                    elif 'DATA RECORD IS' in processed_line.upper():
                        data_match = re.search(r'DATA\s+RECORD\s+IS\s+([A-Z0-9\-_]+)', processed_line, re.IGNORECASE)
                        if data_match:
                            current_fd["data_record"] = data_match.group(1)
                    
                    # Detectar layout de record (01 level)
                    elif re.match(r'^\s*01\s+([A-Z0-9\-_]+)', processed_line, re.IGNORECASE):
                        layout_match = re.match(r'^\s*01\s+([A-Z0-9\-_]+)(?:\s+PIC\s+([^.\s]+))?', processed_line, re.IGNORECASE)
                        if layout_match:
                            record_layout = {
                                "name": layout_match.group(1),
                                "pic_clause": layout_match.group(2) if layout_match.group(2) else "",
                                "raw": processed_line
                            }
                            current_fd["record_layouts"].append(record_layout)
                    
                    # Detectar fin del FD (nueva sección o nuevo FD)
                    if (any(keyword in processed_line.upper() for keyword in ['WORKING-STORAGE', 'LINKAGE', 'FD ']) and
                        not processed_line.upper().strip().startswith('FD')):
                        self._process_fd_statement(current_fd, fd_buffer)
                        current_fd = None
                        fd_buffer = []
                        continue
            
            # Extraer variables
            if in_working_storage or in_linkage:
                section_type = "WORKING-STORAGE" if in_working_storage else "LINKAGE"
                variable = self._parse_variable_line(processed_line, section_type)
                if variable:
                    self.variables.append(variable)
                    
                    if section_type == "WORKING-STORAGE":
                        self.data_division["working_storage_section"]["variables"].append(variable)
                    elif section_type == "LINKAGE":
                        self.data_division["linkage_section"]["variables"].append(variable)
            
            # Parsear SELECT statements en FILE-CONTROL
            if in_file_control:
                # Detectar inicio de SELECT statement
                select_match = re.match(r'^\s*SELECT\s+([A-Z0-9\-_]+)\s+ASSIGN\s+TO\s+([A-Z0-9\-_]+)', processed_line, re.IGNORECASE)
                if select_match:
                    # Si hay un SELECT previo en buffer, procesarlo
                    if current_select and select_buffer:
                        self._process_select_statement(current_select, select_buffer)
                    
                    # Iniciar nuevo SELECT
                    current_select = {
                        "logical_name": select_match.group(1),
                        "external_name": select_match.group(2),
                        "organization": "",
                        "file_status": "",
                        "record_delimiter": "",
                        "access_mode": "",
                        "raw_lines": []
                    }
                    select_buffer = [processed_line]
                    continue
                
                # Si estamos en un SELECT, acumular líneas
                elif current_select:
                    select_buffer.append(processed_line)
                    
                    # Detectar propiedades del SELECT
                    if 'ORGANIZATION IS' in processed_line.upper():
                        org_match = re.search(r'ORGANIZATION\s+IS\s+([A-Z\-_]+)', processed_line, re.IGNORECASE)
                        if org_match:
                            current_select["organization"] = org_match.group(1)
                    
                    elif 'FILE STATUS IS' in processed_line.upper():
                        fs_match = re.search(r'FILE\s+STATUS\s+IS\s+([A-Z0-9\-_]+)', processed_line, re.IGNORECASE)
                        if fs_match:
                            current_select["file_status"] = fs_match.group(1)
                    
                    elif 'ACCESS MODE IS' in processed_line.upper():
                        access_match = re.search(r'ACCESS\s+MODE\s+IS\s+([A-Z\-_]+)', processed_line, re.IGNORECASE)
                        if access_match:
                            current_select["access_mode"] = access_match.group(1)
                    
                    # Detectar fin del SELECT (línea que termina en punto o nueva sección)
                    if (processed_line.strip().endswith('.') or 
                        any(keyword in processed_line.upper() for keyword in ['DATA DIVISION', 'WORKING-STORAGE', 'SELECT'])):
                        self._process_select_statement(current_select, select_buffer)
                        current_select = None
                        select_buffer = []
                        continue
            
            # Parsear EXEC SQL statements (pueden estar en cualquier sección)
            if not in_exec_sql and 'EXEC SQL' in processed_line.upper():
                in_exec_sql = True
                current_exec_sql = {
                    "type": "EXEC_SQL",
                    "sql_statement": "",
                    "host_variables": [],
                    "section": "PROCEDURE" if in_procedure_division else "DATA" if in_data_division else "OTHER",
                    "raw_lines": [],
                    "complete": False
                }
                exec_sql_buffer = [processed_line]
                
                # Si la línea contiene también END-EXEC, es una statement de una sola línea
                if 'END-EXEC' in processed_line.upper():
                    current_exec_sql["complete"] = True
                    self._process_exec_sql_statement(current_exec_sql, exec_sql_buffer, current_procedure)
                    in_exec_sql = False
                    current_exec_sql = None
                    exec_sql_buffer = []
                continue
            
            # Si estamos dentro de EXEC SQL, acumular líneas
            elif in_exec_sql and current_exec_sql:
                exec_sql_buffer.append(processed_line)
                
                # Detectar fin de EXEC SQL
                if 'END-EXEC' in processed_line.upper():
                    current_exec_sql["complete"] = True
                    self._process_exec_sql_statement(current_exec_sql, exec_sql_buffer, current_procedure)
                    in_exec_sql = False
                    current_exec_sql = None
                    exec_sql_buffer = []
                continue
            
            # Parsear TODOS los comandos COBOL en PROCEDURE DIVISION (incluyendo PERFORM)
            if in_procedure_division and not in_exec_sql and processed_line.strip():
                # Primero verificar si es un PERFORM para parsing específico
                perform_info = None
                if 'PERFORM' in processed_line.upper():
                    perform_info = self._parse_perform_statement(processed_line)
                    if perform_info:
                        self.perform_statements.append(perform_info)
                        print(f"🔄 PERFORM procesado: {perform_info['perform_type']} -> {perform_info.get('target', 'N/A')}")
                
                # Luego parsear como statement COBOL general
                cobol_statement = self._parse_cobol_statement(processed_line)
                if cobol_statement:
                    # Agregar al array global
                    self.cobol_statements.append(cobol_statement)
                    
                    # Si estamos dentro de un procedimiento, agregarlo también al procedimiento
                    if current_procedure:
                        cobol_statement["procedure"] = current_procedure["name"]
                        current_procedure["cobol_statements"].append(cobol_statement)
                        
                        # Para PERFORM statements, usar la info específica si existe
                        if perform_info:
                            current_procedure["statements"].append({
                                "op": "PERFORM",
                                "raw": perform_info["raw"],
                                "details": perform_info
                            })
                        else:
                            current_procedure["statements"].append({
                                "op": cobol_statement["statement_type"],
                                "raw": cobol_statement["raw"],
                                "details": cobol_statement["details"]
                            })
                    
                    if len(self.cobol_statements) % 50 == 0:
                        print(f"📝 {len(self.cobol_statements)} statements COBOL procesados...")
            
            # Extraer procedimientos
            if in_procedure_division and not in_exec_sql:
                proc_match = re.match(r'^([A-Z0-9]+(?:-[A-Z0-9]+)*)\.\s*$', processed_line, re.IGNORECASE)
                if proc_match:
                    proc_name = proc_match.group(1)
                    
                    # Filtrar variables y palabras clave
                    if not re.match(r'(END-\w+|WS-|S21-|FS-|MSG-|TL-|LT-|CABE-|REG-|NUM-|COD-|FEM-|HOR-)', proc_name, re.IGNORECASE):
                        procedure = {
                            "name": proc_name,
                            "statements": [],  # Inicializar array vacío para statements
                            "cobol_statements": [],  # Array específico para statements COBOL 
                            "raw": f"{proc_name}."
                        }
                        self.procedures.append(procedure)
                        self.procedure_division["procedures"].append(procedure)
                        
                        # Actualizar procedimiento actual
                        current_procedure = procedure
                        print(f"🏷️  Entrando en procedimiento: {proc_name}")
        
        # Procesar último SELECT si queda en buffer
        if current_select and select_buffer:
            self._process_select_statement(current_select, select_buffer)
        
        # Procesar último FD si queda en buffer
        if current_fd and fd_buffer:
            self._process_fd_statement(current_fd, fd_buffer)
        
        # Procesar último EXEC SQL si queda en buffer
        if current_exec_sql and exec_sql_buffer:
            current_exec_sql["complete"] = False  # Marcarlo como incompleto
            self._process_exec_sql_statement(current_exec_sql, exec_sql_buffer, current_procedure)
        
        # Asignar contenido raw
        self.identification_division["raw_content"] = '\n'.join(identification_lines)
        self.environment_division["raw_content"] = '\n'.join(environment_lines)
        self.data_division["raw_content"] = '\n'.join(data_division_lines)
        self.data_division["file_section"]["raw_content"] = '\n'.join(file_section_lines)
        self.data_division["working_storage_section"]["raw_content"] = '\n'.join(working_storage_lines)
        self.data_division["linkage_section"]["raw_content"] = '\n'.join(linkage_lines)
        self.procedure_division["raw_content"] = '\n'.join(procedure_lines)
        
        print(f"✅ Procesamiento completado: {len(self.variables)} variables, {len(self.procedures)} procedimientos")

    def _process_fixed_format_line(self, line: str) -> str:
        """Procesar línea de formato fijo COBOL"""
        if len(line) < 7:
            return line
        
        # Extraer partes del formato fijo COBOL
        indicator = line[6] if len(line) > 6 else " "       # Col 7: indicador
        cobol_code = line[7:] if len(line) > 7 else ""      # Cols 8+: código COBOL
        
        # Procesar según el indicador
        if indicator == '*':
            return f"      * {cobol_code}"
        elif indicator == '/':
            return f"      * {cobol_code}"
        elif indicator == '-':
            return f"      {cobol_code}"
        elif indicator in ['D', 'd']:
            return f"      * DEBUG: {cobol_code}"
        else:
            return f"      {cobol_code}"

    def _parse_variable_line(self, line: str, section_type: str) -> Optional[Dict[str, Any]]:
        """Parsear una línea de variable"""
        # Patrón básico de variable: 05 VAR-NAME PIC X(10) VALUE 'default'.
        var_match = re.match(r'(\d+)\s+([A-Z0-9\-_]+)(?:\s+PIC\s+([^.\s]+))?(?:\s+VALUE\s+([^.]+))?', 
                            line, re.IGNORECASE)
        if var_match:
            level = var_match.group(1)
            name = var_match.group(2)
            pic_clause = var_match.group(3) if var_match.group(3) else ""
            value_clause = var_match.group(4) if var_match.group(4) else ""
            
            var_type, size = self._parse_pic_clause(pic_clause)
            
            return {
                "level": level,
                "name": name,
                "type": var_type,
                "size": size,
                "pic_clause": pic_clause.strip(),
                "value": value_clause.strip().strip("'\""),
                "section": section_type,
                "raw": line
            }
        return None

    def _parse_pic_clause(self, pic_clause: str) -> tuple:
        """Parsear PIC clause para determinar tipo y tamaño"""
        if not pic_clause:
            return "STRING", 0
        
        pic_clean = pic_clause.upper().strip()
        
        # Numérico: 9(5), S9(3)V9(2), etc.
        if re.search(r'9', pic_clean):
            size_match = re.search(r'9\((\d+)\)', pic_clean)
            size = int(size_match.group(1)) if size_match else 1
            return "NUMERIC", size
        
        # Alfanumérico: X(10), A(5), etc.
        elif re.search(r'[XA]', pic_clean):
            size_match = re.search(r'[XA]\((\d+)\)', pic_clean)
            size = int(size_match.group(1)) if size_match else 1
            return "STRING", size
        
        # Display: Z(5), etc.
        elif 'Z' in pic_clean:
            size_match = re.search(r'Z\((\d+)\)', pic_clean)
            size = int(size_match.group(1)) if size_match else 1
            return "DISPLAY", size
        
        return "STRING", 0

    def _process_select_statement(self, select_info: dict, buffer_lines: list):
        """Procesar y almacenar un SELECT statement completo"""
        select_info["raw_lines"] = buffer_lines
        select_info["raw_content"] = '\n'.join(buffer_lines)
        
        # Almacenar en environment division
        self.environment_division["input_output_section"]["file_control"].append(select_info)
        
        # También crear entrada en files para retrocompatibilidad
        file_entry = {
            "name": select_info["logical_name"],
            "external_name": select_info["external_name"],
            "organization": select_info["organization"],
            "access_mode": select_info["access_mode"],
            "file_status": select_info["file_status"],
            "type": "FILE",
            "raw": select_info["raw_content"]
        }
        self.files.append(file_entry)
        
        print(f"📁 SELECT procesado: {select_info['logical_name']} -> {select_info['external_name']}")

    def _process_fd_statement(self, fd_info: dict, buffer_lines: list):
        """Procesar y almacenar una declaración FD completa"""
        fd_info["raw_lines"] = buffer_lines
        fd_info["raw_content"] = '\n'.join(buffer_lines)
        
        # Almacenar en data division - file section
        self.data_division["file_section"]["file_descriptions"].append(fd_info)
        
        # También crear entrada en file_structures para retrocompatibilidad
        file_structure = {
            "name": fd_info["file_name"],
            "recording_mode": fd_info["recording_mode"],
            "block_contains": fd_info["block_contains"],
            "label_record": fd_info["label_record"],
            "data_record": fd_info["data_record"],
            "record_layouts": fd_info["record_layouts"],
            "type": "FILE_DESCRIPTION",
            "raw": fd_info["raw_content"]
        }
        self.file_structures.append(file_structure)
        
        print(f"📄 FD procesado: {fd_info['file_name']} ({len(fd_info['record_layouts'])} layouts)")

    def _process_exec_sql_statement(self, exec_sql_info: dict, buffer_lines: list, current_procedure: Optional[Dict] = None):
        """Procesar y almacenar una sentencia EXEC SQL completa"""
        exec_sql_info["raw_lines"] = buffer_lines
        exec_sql_info["raw_content"] = '\n'.join(buffer_lines)
        
        # Extraer el SQL puro (sin EXEC SQL y END-EXEC)
        sql_content = exec_sql_info["raw_content"]
        
        # Remover EXEC SQL del inicio
        sql_content = re.sub(r'^\s*EXEC\s+SQL\s*', '', sql_content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remover END-EXEC del final
        sql_content = re.sub(r'\s*END-EXEC\s*\.?\s*$', '', sql_content, flags=re.IGNORECASE | re.MULTILINE)
        
        exec_sql_info["sql_statement"] = sql_content.strip()
        
        # Extraer host variables (variables que empiezan con :)
        host_vars = re.findall(r':([A-Z0-9\-_]+)', sql_content, re.IGNORECASE)
        exec_sql_info["host_variables"] = list(set(host_vars))  # Eliminar duplicados
        
        # Determinar tipo de SQL
        sql_upper = sql_content.upper().strip()
        if sql_upper.startswith('SELECT'):
            exec_sql_info["sql_type"] = "SELECT"
        elif sql_upper.startswith('INSERT'):
            exec_sql_info["sql_type"] = "INSERT"
        elif sql_upper.startswith('UPDATE'):
            exec_sql_info["sql_type"] = "UPDATE"
        elif sql_upper.startswith('DELETE'):
            exec_sql_info["sql_type"] = "DELETE"
        elif sql_upper.startswith('DECLARE'):
            exec_sql_info["sql_type"] = "DECLARE"
        elif sql_upper.startswith('OPEN'):
            exec_sql_info["sql_type"] = "OPEN"
        elif sql_upper.startswith('FETCH'):
            exec_sql_info["sql_type"] = "FETCH"
        elif sql_upper.startswith('CLOSE'):
            exec_sql_info["sql_type"] = "CLOSE"
        elif sql_upper.startswith('COMMIT'):
            exec_sql_info["sql_type"] = "COMMIT"
        elif sql_upper.startswith('ROLLBACK'):
            exec_sql_info["sql_type"] = "ROLLBACK"
        else:
            exec_sql_info["sql_type"] = "OTHER"
        
        # Almacenar en sql_declarations
        self.sql_declarations.append(exec_sql_info)
        
        # Asociar al procedimiento actual si existe
        if current_procedure:
            exec_sql_info["procedure"] = current_procedure["name"]
            current_procedure["statements"].append({
                "op": "EXEC_SQL",
                "raw": exec_sql_info["raw_content"],
                "details": exec_sql_info
            })
        
        # También almacenar en la sección correspondiente si es DATA DIVISION
        if exec_sql_info["section"] == "DATA":
            if "sql_statements" not in self.data_division:
                self.data_division["sql_statements"] = []
            self.data_division["sql_statements"].append(exec_sql_info)
        
        status = "✅" if exec_sql_info["complete"] else "⚠️ "
        print(f"🔍 EXEC SQL procesado: {exec_sql_info['sql_type']} {status} ({len(exec_sql_info['host_variables'])} host vars)")

    def _parse_perform_statement(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsear una sentencia PERFORM"""
        try:
            line_upper = line.upper().strip()
            
            # PERFORM simple: PERFORM paragraph-name
            simple_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)\s*\.?\s*$', line, re.IGNORECASE)
            if simple_match:
                return {
                    "type": "PERFORM_STATEMENT",
                    "perform_type": "SIMPLE",
                    "target": simple_match.group(1),
                    "thru_target": None,
                    "times": None,
                    "until_condition": None,
                    "varying_clause": None,
                    "raw": line
                }
            
            # PERFORM THRU: PERFORM paragraph1 THRU paragraph2
            thru_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)\s+THRU\s+([A-Z0-9\-_]+)\s*\.?\s*$', line, re.IGNORECASE)
            if thru_match:
                return {
                    "type": "PERFORM_STATEMENT",
                    "perform_type": "THRU",
                    "target": thru_match.group(1),
                    "thru_target": thru_match.group(2),
                    "times": None,
                    "until_condition": None,
                    "varying_clause": None,
                    "raw": line
                }
            
            # PERFORM TIMES: PERFORM paragraph-name N TIMES
            times_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)(?:\s+THRU\s+([A-Z0-9\-_]+))?\s+(\d+|\w[\w\-]*)\s+TIMES\s*\.?\s*$', line, re.IGNORECASE)
            if times_match:
                return {
                    "type": "PERFORM_STATEMENT",
                    "perform_type": "TIMES",
                    "target": times_match.group(1),
                    "thru_target": times_match.group(2),
                    "times": times_match.group(3),
                    "until_condition": None,
                    "varying_clause": None,
                    "raw": line
                }
            
            # PERFORM UNTIL: PERFORM paragraph-name UNTIL condition
            until_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)(?:\s+THRU\s+([A-Z0-9\-_]+))?\s+UNTIL\s+(.+?)\s*\.?\s*$', line, re.IGNORECASE)
            if until_match:
                return {
                    "type": "PERFORM_STATEMENT",
                    "perform_type": "UNTIL",
                    "target": until_match.group(1),
                    "thru_target": until_match.group(2),
                    "times": None,
                    "until_condition": until_match.group(3).strip(),
                    "varying_clause": None,
                    "raw": line
                }
            
            # PERFORM VARYING: PERFORM paragraph-name VARYING var FROM start BY increment UNTIL condition
            varying_match = re.match(r'^\s*PERFORM\s+([A-Z0-9\-_]+)(?:\s+THRU\s+([A-Z0-9\-_]+))?\s+VARYING\s+(.+?)\s+FROM\s+(.+?)\s+BY\s+(.+?)\s+UNTIL\s+(.+?)\s*\.?\s*$', line, re.IGNORECASE)
            if varying_match:
                return {
                    "type": "PERFORM_STATEMENT",
                    "perform_type": "VARYING",
                    "target": varying_match.group(1),
                    "thru_target": varying_match.group(2),
                    "times": None,
                    "until_condition": varying_match.group(6).strip(),
                    "varying_clause": {
                        "variable": varying_match.group(3).strip(),
                        "from_value": varying_match.group(4).strip(),
                        "by_value": varying_match.group(5).strip()
                    },
                    "raw": line
                }
            
            # PERFORM inline (sin target específico)
            if 'PERFORM' in line_upper and not re.search(r'PERFORM\s+[A-Z0-9\-_]+', line, re.IGNORECASE):
                return {
                    "type": "PERFORM_STATEMENT",
                    "perform_type": "INLINE",
                    "target": None,
                    "thru_target": None,
                    "times": None,
                    "until_condition": None,
                    "varying_clause": None,
                    "raw": line
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error parseando PERFORM: {str(e)} en línea: {line}")
            return None

    def _parse_cobol_statement(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsear cualquier sentencia COBOL"""
        try:
            line_clean = line.strip()
            if not line_clean or line_clean.startswith('*'):
                return None
            
            line_upper = line_clean.upper()
            
            # Detectar diferentes tipos de statements COBOL
            statement_type = "UNKNOWN"
            details = {}
            
            # Directivas del preprocesador (PRIMERO)
            if re.match(r'^\s*@DEFINE\s*\([^)]+\)', line, re.IGNORECASE):
                statement_type = "PREPROCESSOR_DEFINE"
                details = {"directive": "DEFINE", "preprocessor": True}
            elif re.match(r'^\s*@CTRLERR\s*\([^)]+\)', line, re.IGNORECASE):
                statement_type = "PREPROCESSOR_CTRLERR"
                details = {"directive": "CTRLERR", "preprocessor": True}
            elif re.match(r'^\s*@INIBAT\s*\([^)]*\)', line, re.IGNORECASE):
                statement_type = "PREPROCESSOR_INIBAT"
                details = {"directive": "INIBAT", "preprocessor": True}
            elif re.match(r'^\s*@FINBAT\s*\([^)]*\)', line, re.IGNORECASE):
                statement_type = "PREPROCESSOR_FINBAT"
                details = {"directive": "FINBAT", "preprocessor": True}
            elif re.match(r'^\s*@CTRL\s*\([^)]+\)', line, re.IGNORECASE):
                statement_type = "PREPROCESSOR_CTRL"
                details = {"directive": "CTRL", "preprocessor": True}
            elif re.match(r'^\s*@\w+\s*\([^)]*\)', line, re.IGNORECASE):
                statement_type = "FUNCTION_CALL"
                details = {"function_call": True}
            
            # MOVE statements
            if re.match(r'^\s*MOVE\s+', line, re.IGNORECASE):
                statement_type = "MOVE"
                move_match = re.match(r'^\s*MOVE\s+(.*?)\s+TO\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if move_match:
                    details = {
                        "source": move_match.group(1).strip(),
                        "target": move_match.group(2).strip()
                    }
            
            # IF statements
            elif re.match(r'^\s*IF\s+', line, re.IGNORECASE):
                statement_type = "IF"
                if_match = re.match(r'^\s*IF\s+(.*?)\s+THEN\s*(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if if_match:
                    details = {
                        "condition": if_match.group(1).strip(),
                        "then_action": if_match.group(2).strip() if if_match.group(2) else None
                    }
                else:
                    # IF sin THEN explícito
                    condition_match = re.match(r'^\s*IF\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                    if condition_match:
                        details = {
                            "condition": condition_match.group(1).strip(),
                            "then_action": None
                        }
            
            # DISPLAY statements
            elif re.match(r'^\s*DISPLAY\s+', line, re.IGNORECASE):
                statement_type = "DISPLAY"
                display_match = re.match(r'^\s*DISPLAY\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if display_match:
                    details = {
                        "content": display_match.group(1).strip()
                    }
            
            # CALL statements
            elif re.match(r'^\s*CALL\s+', line, re.IGNORECASE):
                statement_type = "CALL"
                call_match = re.match(r'^\s*CALL\s+[\'"]?([^\'"]*)[\'"]?\s*(?:USING\s+(.*?))?\s*\.?\s*$', line, re.IGNORECASE)
                if call_match:
                    details = {
                        "program": call_match.group(1).strip(),
                        "using_params": call_match.group(2).strip() if call_match.group(2) else None
                    }
            
            # COMPUTE statements
            elif re.match(r'^\s*COMPUTE\s+', line, re.IGNORECASE):
                statement_type = "COMPUTE"
                compute_match = re.match(r'^\s*COMPUTE\s+(.*?)\s*=\s*(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if compute_match:
                    details = {
                        "target": compute_match.group(1).strip(),
                        "expression": compute_match.group(2).strip()
                    }
            
            # ADD statements
            elif re.match(r'^\s*ADD\s+', line, re.IGNORECASE):
                statement_type = "ADD"
                add_match = re.match(r'^\s*ADD\s+(.*?)\s+TO\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if add_match:
                    details = {
                        "addend": add_match.group(1).strip(),
                        "target": add_match.group(2).strip()
                    }
            
            # SUBTRACT statements
            elif re.match(r'^\s*SUBTRACT\s+', line, re.IGNORECASE):
                statement_type = "SUBTRACT"
                sub_match = re.match(r'^\s*SUBTRACT\s+(.*?)\s+FROM\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if sub_match:
                    details = {
                        "subtrahend": sub_match.group(1).strip(),
                        "target": sub_match.group(2).strip()
                    }
            
            # MULTIPLY statements
            elif re.match(r'^\s*MULTIPLY\s+', line, re.IGNORECASE):
                statement_type = "MULTIPLY"
                mult_match = re.match(r'^\s*MULTIPLY\s+(.*?)\s+BY\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if mult_match:
                    details = {
                        "multiplicand": mult_match.group(1).strip(),
                        "target": mult_match.group(2).strip()
                    }
            
            # DIVIDE statements
            elif re.match(r'^\s*DIVIDE\s+', line, re.IGNORECASE):
                statement_type = "DIVIDE"
                div_match = re.match(r'^\s*DIVIDE\s+(.*?)\s+(?:INTO|BY)\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if div_match:
                    details = {
                        "dividend": div_match.group(1).strip(),
                        "divisor": div_match.group(2).strip()
                    }
            
            # SET statements
            elif re.match(r'^\s*SET\s+', line, re.IGNORECASE):
                statement_type = "SET"
                set_match = re.match(r'^\s*SET\s+(.*?)\s+TO\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if set_match:
                    details = {
                        "target": set_match.group(1).strip(),
                        "value": set_match.group(2).strip()
                    }
            
            # OPEN statements
            elif re.match(r'^\s*OPEN\s+', line, re.IGNORECASE):
                statement_type = "OPEN"
                open_match = re.match(r'^\s*OPEN\s+(INPUT|OUTPUT|I-O|EXTEND)\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if open_match:
                    details = {
                        "mode": open_match.group(1).strip(),
                        "file": open_match.group(2).strip()
                    }
            
            # CLOSE statements
            elif re.match(r'^\s*CLOSE\s+', line, re.IGNORECASE):
                statement_type = "CLOSE"
                close_match = re.match(r'^\s*CLOSE\s+(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if close_match:
                    details = {
                        "file": close_match.group(1).strip()
                    }
            
            # READ statements
            elif re.match(r'^\s*READ\s+', line, re.IGNORECASE):
                statement_type = "READ"
                read_match = re.match(r'^\s*READ\s+(.*?)\s*(?:INTO\s+(.*?))?\s*(?:AT\s+END\s+(.*?))?\s*\.?\s*$', line, re.IGNORECASE)
                if read_match:
                    details = {
                        "file": read_match.group(1).strip(),
                        "into": read_match.group(2).strip() if read_match.group(2) else None,
                        "at_end": read_match.group(3).strip() if read_match.group(3) else None
                    }
            
            # WRITE statements
            elif re.match(r'^\s*WRITE\s+', line, re.IGNORECASE):
                statement_type = "WRITE"
                write_match = re.match(r'^\s*WRITE\s+(.*?)\s*(?:FROM\s+(.*?))?\s*\.?\s*$', line, re.IGNORECASE)
                if write_match:
                    details = {
                        "record": write_match.group(1).strip(),
                        "from": write_match.group(2).strip() if write_match.group(2) else None
                    }
            
            # GOBACK statements
            elif re.match(r'^\s*GOBACK\s*\.?\s*$', line, re.IGNORECASE):
                statement_type = "GOBACK"
            
            # EXIT statements
            elif re.match(r'^\s*EXIT\s*\.?\s*$', line, re.IGNORECASE):
                statement_type = "EXIT"
            
            # STOP statements
            elif re.match(r'^\s*STOP\s+', line, re.IGNORECASE):
                statement_type = "STOP"
                stop_match = re.match(r'^\s*STOP\s+(RUN|.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if stop_match:
                    details = {
                        "type": stop_match.group(1).strip()
                    }
            
            # END-IF, END-PERFORM, etc.
            elif re.match(r'^\s*END-', line, re.IGNORECASE):
                end_match = re.match(r'^\s*END-(\w+)\s*\.?\s*$', line, re.IGNORECASE)
                if end_match:
                    statement_type = f"END-{end_match.group(1).upper()}"
            
            # ELSE statements
            elif re.match(r'^\s*ELSE\s*', line, re.IGNORECASE):
                statement_type = "ELSE"
                else_match = re.match(r'^\s*ELSE\s*(.*?)\s*\.?\s*$', line, re.IGNORECASE)
                if else_match and else_match.group(1):
                    details = {
                        "action": else_match.group(1).strip()
                    }
            
            # PERFORM statements (muy importante - muchos se están perdiendo)
            elif re.match(r'^\s*PERFORM\s+', line, re.IGNORECASE):
                statement_type = "PERFORM"
                perform_match = re.match(r'^\s*PERFORM\s+(.+?)(?:\s*\.)?\s*$', line, re.IGNORECASE)
                if perform_match:
                    details = {"target": perform_match.group(1).strip()}
            
            # CONTINUE statements
            elif re.match(r'^\s*CONTINUE\s*\.?\s*$', line, re.IGNORECASE):
                statement_type = "CONTINUE"
                details = {"control_flow": True}
            
            # Campos calificados (FIELD OF GROUP)
            elif ' OF ' in line_upper:
                statement_type = "QUALIFIED_FIELD"
                details = {"qualified": True, "field": line.strip()}
            
            # Variables simples (nombres de variables)
            elif re.match(r'^[A-Z0-9-]+(?:-[A-Z0-9-]+)*\.?\s*$', line, re.IGNORECASE):
                statement_type = "VARIABLE_REFERENCE"
                details = {"variable": line.strip().rstrip('.')}
            
            # Continuaciones de statements MOVE (líneas que empiezan con TO)
            elif re.match(r'^\s*TO\s+', line, re.IGNORECASE):
                statement_type = "MOVE_CONTINUATION"
                details = {"continuation": True, "move_target": line.strip()}
            
            # Líneas que empiezan con INTO (continuaciones)
            elif re.match(r'^\s*INTO\s+', line, re.IGNORECASE):
                statement_type = "INTO_CONTINUATION"
                details = {"continuation": True, "into_target": line.strip()}
            
            # Líneas que empiezan con DELIMITED BY
            elif re.match(r'^\s*DELIMITED\s+BY\s+', line, re.IGNORECASE):
                statement_type = "DELIMITED_BY"
                details = {"delimiter": True, "content": line.strip()}
            
            # Líneas con BY (INITIALIZE, etc.)
            elif re.match(r'^\s*BY\s+', line, re.IGNORECASE):
                statement_type = "BY_CLAUSE"
                details = {"by_clause": True, "content": line.strip()}
            
            # Líneas con literales y variables (concatenación)
            elif re.search(r"'[^']*'\s+[A-Z0-9-]+", line, re.IGNORECASE):
                statement_type = "LITERAL_CONCATENATION"
                details = {"concatenation": True, "content": line.strip()}
            
            # Líneas con SQLSTATE o SQLCODE
            elif re.search(r'\bSQLSTATE\b|\bSQLCODE\b', line, re.IGNORECASE):
                statement_type = "SQL_REFERENCE"
                details = {"sql_reference": True, "content": line.strip()}
            
            # Líneas con variables y literales mezclados
            elif re.search(r"[A-Z0-9-]+\s+'.*'", line, re.IGNORECASE):
                statement_type = "VARIABLE_LITERAL_MIX"
                details = {"mixed": True, "content": line.strip()}
            
            # Otras estructuras de control
            elif any(keyword in line_upper for keyword in ['EVALUATE', 'WHEN', 'STRING', 'UNSTRING', 'INSPECT', 'INITIALIZE']):
                for keyword in ['EVALUATE', 'WHEN', 'STRING', 'UNSTRING', 'INSPECT', 'INITIALIZE']:
                    if line_upper.startswith(keyword):
                        statement_type = keyword
                        break
            
            # Comentarios y etiquetas de procedimiento ya se manejan arriba
            elif re.match(r'^[A-Z0-9]+(?:-[A-Z0-9]+)*\.\s*$', line, re.IGNORECASE):
                return None  # Ya se maneja como procedimiento
            
            return {
                "type": "COBOL_STATEMENT",
                "statement_type": statement_type,
                "details": details,
                "raw": line,
                "line_number": None  # Se podría agregar después
            }
            
        except Exception as e:
            print(f"⚠️ Error parseando statement COBOL: {str(e)} en línea: {line}")
            return None

# ===== FILE I/O UTILITIES =====

def save_ir_to_file(ir: Dict[str, Any], output_path: str) -> float:
    """Guardar IR a archivo JSON con timing"""
    start_time = time.time()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ir, f, indent=2, ensure_ascii=False)
    
    end_time = time.time()
    return end_time - start_time

def generate_parsing_report(ir: Dict[str, Any], report_path: str, parsing_duration: float, io_duration: float) -> Dict[str, Any]:
    """Generar reporte de parsing directo"""
    
    total_statements = sum(len(proc.get('statements', [])) for proc in ir.get('procedures', []))
    
    report = {
        "timestamp": get_timestamp(),
        "parsing_summary": {
            "program_name": ir.get("program", "UNKNOWN"),
            "parse_method": ir.get("parse_method", "direct_parsing"),
            "total_variables": len(ir.get("variables", [])),
            "total_procedures": len(ir.get("procedures", [])),
            "total_statements": total_statements,
            "total_files": len(ir.get("files", [])),
            "file_control_entries": len(ir.get("environment_division", {}).get("input_output_section", {}).get("file_control", []))
        },
        "optimization_metrics": {
            "direct_parsing": True,
            "format_fixed_handled": True,
            "memory_efficient": True,
            "sql_ready_format": True
        },
        "performance_metrics": {
            "parsing_duration_seconds": parsing_duration,
            "io_duration_seconds": io_duration,
            "total_duration_seconds": parsing_duration + io_duration,
            "statements_per_second": total_statements / parsing_duration if parsing_duration > 0 else 0
        },
        "structure_analysis": {
            "has_working_storage": any(var.get("section") == "WORKING-STORAGE" for var in ir.get("variables", [])),
            "has_linkage_section": any(var.get("section") == "LINKAGE" for var in ir.get("variables", [])),
            "has_file_control": len(ir.get("files", [])) > 0,
            "has_procedures": len(ir.get("procedures", [])) > 0
        },
        "sql_generation_readiness": {
            "program_name_extracted": bool(ir.get("program")),
            "variables_structured": len(ir.get("variables", [])) > 0,
            "procedures_with_statements": sum(1 for proc in ir.get("procedures", []) if proc.get("statements")),
            "file_operations_detected": any("FILE" in str(proc) for proc in ir.get("procedures", [])),
            "estimated_sql_complexity": "HIGH" if total_statements > 100 else "MEDIUM" if total_statements > 20 else "LOW"
        }
    }
    
    # Guardar reporte
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def parse_cobol_to_ir_direct(file_path: str) -> Dict[str, Any]:
    """Función principal para parsear COBOL a IR directo"""
    parser = CobolToIRParserDirect()
    return parser.parse_cobol_file(file_path)

# ===== MAIN FUNCTION =====

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python antlr_parser_direct.py archivo.cob")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Archivo no encontrado: {input_file}")
        sys.exit(1)
    
    # Configurar nombres de archivos de salida
    base_name = os.path.splitext(os.path.basename(input_file))[0].upper()
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    
    ir_output = os.path.join(output_dir, f"{base_name}_ir_direct.json")
    report_output = os.path.join(output_dir, f"{base_name}_parsing_report_direct.json")
    
    print("======================================================================")
    print("🔧 ANTLR Parser DIRECT - COBOL to IR (PARSING DIRECTO)")
    print(f"📁 Archivo fuente: {input_file}")
    print(f"⏰ Inicio: {get_timestamp()}")
    print("🎯 Parsing directo sin ANTLR - rápido y eficiente")
    print("======================================================================")
    
    try:
        # Parsear archivo
        start_time = time.time()
        start_timestamp = get_timestamp()
        ir = parse_cobol_to_ir_direct(input_file)
        parsing_end_time = time.time()
        parsing_duration = parsing_end_time - start_time
        
        # Guardar IR
        io_start_time = time.time()
        io_duration = save_ir_to_file(ir, ir_output)
        io_end_time = time.time()
        total_io_duration = io_end_time - io_start_time
        
        # Generar reporte
        end_timestamp = get_timestamp()
        report = generate_parsing_report(ir, report_output, parsing_duration, total_io_duration)
        
        print("✅ Archivos generados:")
        print(f"   📊 IR: {ir_output}")
        print(f"   📊 Reporte: {report_output}")
        
        # Mostrar resumen
        print("======================================================================")
        print("📊 RESUMEN DE PARSING DIRECTO")
        print("======================================================================")
        print("🎯 ANÁLISIS DIRECTO:")
        print(f"   📋 Programa: {report['parsing_summary']['program_name']}")
        print(f"   📊 Variables: {report['parsing_summary']['total_variables']}")
        print(f"   🔧 Procedimientos: {report['parsing_summary']['total_procedures']}")
        print(f"   📄 Statements: {report['parsing_summary']['total_statements']}")
        print(f"   📁 Archivos: {report['parsing_summary']['total_files']}")
        
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
        print(f"   ⚡ Velocidad: {report['performance_metrics']['statements_per_second']:.1f} statements/seg")
        
        print("🚀 VENTAJAS:")
        print("   ✅ Parsing directo sin dependencias ANTLR")
        print("   ✅ Manejo correcto de formato fijo COBOL")
        print("   ✅ Procesamiento rápido y eficiente")
        print("   ✅ IR completo con todas las divisiones")
        
        print("📁 LISTOS PARA SQL:")
        readiness = report['sql_generation_readiness']
        print(f"   • Programa: {'✅' if readiness['program_name_extracted'] else '❌'}")
        print(f"   • Variables: {'✅' if readiness['variables_structured'] else '❌'}")
        print(f"   • Procedimientos: {readiness['procedures_with_statements']} con statements")
        print(f"   • Complejidad: {readiness['estimated_sql_complexity']}")
        
        print("======================================================================")
        
    except Exception as e:
        print(f"❌ Error durante el parsing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
