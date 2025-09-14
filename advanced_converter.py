#!/usr/bin/env python3
"""
Convertidor Avanzado COBOL a PL/SQL
Basado en el análisis del programa C1040.cob y su migración manual
"""

import re
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple

class AdvancedCobolConverter:
    def __init__(self):
        self.program_name = ""
        self.variables = []
        self.files = []
        self.file_structures = []
        self.sql_declarations = []
        self.procedures = []
        self.cursors = []
        self.services = []
        self.macros = []
        self.conditions = []
        self.literals = []
        self.structures = []
        
    def clean_expression(self, expr: str) -> str:
        """Limpia expresiones COBOL para PL/SQL"""
        if not expr:
            return ""
        
        # Reemplazar guiones con guiones bajos
        expr = expr.replace('-', '_')
        
        # Limpiar espacios y caracteres especiales
        expr = re.sub(r'\s+', ' ', expr.strip())
        
        return expr
    
    def parse_cobol_to_ir(self, cobol_content: str) -> Dict[str, Any]:
        """Parsea COBOL a representación intermedia avanzada"""
        lines = cobol_content.split('\n')
        
        # Extraer nombre del programa
        program_match = re.search(r'PROGRAM-ID\.\s+(\w+)', cobol_content, re.IGNORECASE)
        if program_match:
            self.program_name = program_match.group(1).upper()
        
        # Parsear secciones
        self._parse_environment_division(cobol_content)
        self._parse_data_division(cobol_content)
        self._parse_procedure_division(cobol_content)
        self._parse_sql_declarations(cobol_content)
        self._parse_cursors(cobol_content)
        self._parse_services(cobol_content)
        self._parse_macros(cobol_content)
        self._parse_conditions(cobol_content)
        self._parse_literals(cobol_content)
        self._parse_structures(cobol_content)
        
        return {
            "program": self.program_name,
            "variables": self.variables,
            "files": self.files,
            "file_structures": self.file_structures,
            "sql_declarations": self.sql_declarations,
            "procedures": self.procedures,
            "cursors": self.cursors,
            "services": self.services,
            "macros": self.macros,
            "conditions": self.conditions,
            "literals": self.literals,
            "structures": self.structures
        }
    
    def _parse_environment_division(self, content: str):
        """Parsea ENVIRONMENT DIVISION"""
        # INPUT-OUTPUT SECTION
        input_output_match = re.search(
            r'INPUT-OUTPUT\s+SECTION\.(.*?)(?=DATA\s+DIVISION|$)',
            content, re.IGNORECASE | re.DOTALL
        )
        
        if input_output_match:
            input_output_content = input_output_match.group(1)
            
            # FILE-CONTROL
            file_control_match = re.search(
                r'FILE-CONTROL\.(.*?)(?=DATA\s+DIVISION|$)',
                input_output_content, re.IGNORECASE | re.DOTALL
            )
            
            if file_control_match:
                file_control_content = file_control_match.group(1)
                
                # Parsear SELECT statements
                select_pattern = r'SELECT\s+(\w+)\s+ASSIGN\s+TO\s+(\w+)(?:\s+FILE\s+STATUS\s+IS\s+(\w+))?'
                for match in re.finditer(select_pattern, file_control_content, re.IGNORECASE):
                    file_name = match.group(1)
                    assign_to = match.group(2)
                    file_status = match.group(3) if match.group(3) else None
                    
                    self.files.append({
                        "name": file_name,
                        "assign_to": assign_to,
                        "file_status": file_status
                    })
    
    def _parse_data_division(self, content: str):
        """Parsea DATA DIVISION"""
        # FILE SECTION
        file_section_match = re.search(
            r'FILE\s+SECTION\.(.*?)(?=WORKING-STORAGE\s+SECTION|$)',
            content, re.IGNORECASE | re.DOTALL
        )
        
        if file_section_match:
            file_section_content = file_section_match.group(1)
            
            # Parsear FD statements
            fd_pattern = r'FD\s+(\w+).*?01\s+(\w+).*?PIC\s+([^\.]+)'
            for match in re.finditer(fd_pattern, file_section_content, re.IGNORECASE | re.DOTALL):
                file_name = match.group(1)
                record_name = match.group(2)
                pic_clause = match.group(3).strip()
                
                self.file_structures.append({
                    "file_name": file_name,
                    "record_name": record_name,
                    "pic_clause": pic_clause
                })
        
        # WORKING-STORAGE SECTION
        working_storage_match = re.search(
            r'WORKING-STORAGE\s+SECTION\.(.*?)(?=PROCEDURE\s+DIVISION|$)',
            content, re.IGNORECASE | re.DOTALL
        )
        
        if working_storage_match:
            working_storage_content = working_storage_match.group(1)
            self._parse_working_storage(working_storage_content)
    
    def _parse_working_storage(self, content: str):
        """Parsea WORKING-STORAGE SECTION"""
        lines = content.split('\n')
        current_group = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # Parsear variables
            var_match = re.match(r'(\d+)\s+(\w+).*?PIC\s+([^\.]+)', line, re.IGNORECASE)
            if var_match:
                level = var_match.group(1)
                name = var_match.group(2)
                pic_clause = var_match.group(3).strip()
                
                # Determinar tipo y tamaño
                var_type, size = self._parse_pic_clause(pic_clause)
                
                self.variables.append({
                    "level": level,
                    "name": name,
                    "type": var_type,
                    "size": size,
                    "pic_clause": pic_clause
                })
            
            # Parsear condiciones 88
            condition_match = re.match(r'88\s+(\w+).*?VALUE\s+([^\.]+)', line, re.IGNORECASE)
            if condition_match:
                condition_name = condition_match.group(1)
                condition_value = condition_match.group(2).strip()
                
                self.conditions.append({
                    "name": condition_name,
                    "value": condition_value
                })
            
            # Parsear literales
            literal_match = re.match(r'(\d+)\s+(\w+).*?VALUE\s+([^\.]+)', line, re.IGNORECASE)
            if literal_match:
                level = literal_match.group(1)
                name = literal_match.group(2)
                value = literal_match.group(3).strip()
                
                self.literals.append({
                    "level": level,
                    "name": name,
                    "value": value
                })
    
    def _parse_pic_clause(self, pic_clause: str) -> Tuple[str, int]:
        """Parsea cláusula PIC para determinar tipo y tamaño"""
        pic_clause = pic_clause.upper().strip()
        
        # PIC X(n) - String
        x_match = re.search(r'X\((\d+)\)', pic_clause)
        if x_match:
            return "STRING", int(x_match.group(1))
        
        # PIC Xn - String
        x_match = re.search(r'X(\d+)', pic_clause)
        if x_match:
            return "STRING", int(x_match.group(1))
        
        # PIC 9(n) - Numeric
        nine_match = re.search(r'9\((\d+)\)', pic_clause)
        if nine_match:
            return "NUMERIC", int(nine_match.group(1))
        
        # PIC 9n - Numeric
        nine_match = re.search(r'9(\d+)', pic_clause)
        if nine_match:
            return "NUMERIC", int(nine_match.group(1))
        
        # PIC S9(n) - Signed Numeric
        s_match = re.search(r'S9\((\d+)\)', pic_clause)
        if s_match:
            return "NUMERIC", int(s_match.group(1))
        
        # PIC S9n - Signed Numeric
        s_match = re.search(r'S9(\d+)', pic_clause)
        if s_match:
            return "NUMERIC", int(s_match.group(1))
        
        # Default
        return "STRING", 1
    
    def _parse_procedure_division(self, content: str):
        """Parsea PROCEDURE DIVISION"""
        procedure_match = re.search(
            r'PROCEDURE\s+DIVISION\.(.*?)$',
            content, re.IGNORECASE | re.DOTALL
        )
        
        if procedure_match:
            procedure_content = procedure_match.group(1)
            self._parse_procedures(procedure_content)
    
    def _parse_procedures(self, content: str):
        """Parsea procedimientos y sentencias"""
        lines = content.split('\n')
        current_procedure = None
        current_statements = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # Identificar inicio de procedimiento
            proc_match = re.match(r'(\w+-\w+)\.', line)
            if proc_match:
                # Guardar procedimiento anterior
                if current_procedure:
                    self.procedures.append({
                        "name": current_procedure,
                        "statements": current_statements
                    })
                
                # Iniciar nuevo procedimiento
                current_procedure = proc_match.group(1)
                current_statements = []
                continue
            
            # Parsear sentencias
            if current_procedure:
                statement = self._parse_statement(line)
                if statement:
                    current_statements.append(statement)
        
        # Guardar último procedimiento
        if current_procedure:
            self.procedures.append({
                "name": current_procedure,
                "statements": current_statements
            })
    
    def _parse_statement(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsea una sentencia COBOL"""
        line = line.strip()
        
        # PERFORM
        perform_match = re.match(r'PERFORM\s+(\w+-\w+)\.?', line, re.IGNORECASE)
        if perform_match:
            return {
                "op": "PERFORM",
                "target": perform_match.group(1)
            }
        
        # PERFORM UNTIL
        perform_until_match = re.match(r'PERFORM\s+(\w+-\w+)\s+UNTIL\s+(.+)', line, re.IGNORECASE)
        if perform_until_match:
            return {
                "op": "PERFORM_UNTIL",
                "target": perform_until_match.group(1),
                "condition": perform_until_match.group(2)
            }
        
        # MOVE
        move_match = re.match(r'MOVE\s+(.+?)\s+TO\s+(.+)', line, re.IGNORECASE)
        if move_match:
            return {
                "op": "MOVE",
                "from": move_match.group(1).strip(),
                "to": move_match.group(2).strip()
            }
        
        # IF
        if_match = re.match(r'IF\s+(.+?)\s+THEN', line, re.IGNORECASE)
        if if_match:
            return {
                "op": "IF",
                "condition": if_match.group(1).strip()
            }
        
        # DISPLAY
        display_match = re.match(r'DISPLAY\s+(.+)', line, re.IGNORECASE)
        if display_match:
            return {
                "op": "DISPLAY",
                "message": display_match.group(1).strip()
            }
        
        # STRING
        string_match = re.match(r'STRING\s+(.+)', line, re.IGNORECASE)
        if string_match:
            return {
                "op": "STRING",
                "expression": string_match.group(1).strip()
            }
        
        # EVALUATE
        evaluate_match = re.match(r'EVALUATE\s+(.+)', line, re.IGNORECASE)
        if evaluate_match:
            return {
                "op": "EVALUATE",
                "expression": evaluate_match.group(1).strip()
            }
        
        # OPEN
        open_match = re.match(r'OPEN\s+(INPUT|OUTPUT)\s+(\w+)', line, re.IGNORECASE)
        if open_match:
            return {
                "op": "OPEN",
                "mode": open_match.group(1).upper(),
                "file": open_match.group(2)
            }
        
        # CLOSE
        close_match = re.match(r'CLOSE\s+(\w+)', line, re.IGNORECASE)
        if close_match:
            return {
                "op": "CLOSE",
                "file": close_match.group(1)
            }
        
        # READ
        read_match = re.match(r'READ\s+(\w+).*?AT\s+END', line, re.IGNORECASE)
        if read_match:
            return {
                "op": "READ",
                "file": read_match.group(1)
            }
        
        # WRITE
        write_match = re.match(r'WRITE\s+(\w+)', line, re.IGNORECASE)
        if write_match:
            return {
                "op": "WRITE",
                "file": write_match.group(1)
            }
        
        # INITIALIZE
        initialize_match = re.match(r'INITIALIZE\s+(.+)', line, re.IGNORECASE)
        if initialize_match:
            return {
                "op": "INITIALIZE",
                "target": initialize_match.group(1).strip()
            }
        
        # ADD
        add_match = re.match(r'ADD\s+(\d+)\s+TO\s+(.+)', line, re.IGNORECASE)
        if add_match:
            return {
                "op": "ADD",
                "value": add_match.group(1),
                "to": add_match.group(2).strip()
            }
        
        # COMMIT
        if re.match(r'COMMIT', line, re.IGNORECASE):
            return {"op": "COMMIT"}
        
        # ROLLBACK
        if re.match(r'ROLLBACK', line, re.IGNORECASE):
            return {"op": "ROLLBACK"}
        
        # GAP - sentencia no reconocida
        return {
            "op": "UNKNOWN",
            "raw": line
        }
    
    def _parse_sql_declarations(self, content: str):
        """Parsea declaraciones SQL"""
        # EXEC SQL ... END-EXEC
        sql_blocks = re.findall(r'EXEC\s+SQL\s+(.*?)END-EXEC\.', content, re.IGNORECASE | re.DOTALL)
        
        for block in sql_blocks:
            block = block.strip()
            
            # INCLUDE
            include_match = re.search(r'INCLUDE\s+(\w+)', block, re.IGNORECASE)
            if include_match:
                self.sql_declarations.append({
                    "op": "SQL_INCLUDE",
                    "table": include_match.group(1),
                    "raw": f"EXEC SQL {block} END-EXEC."
                })
            
            # DECLARE CURSOR
            cursor_match = re.search(r'DECLARE\s+(\w+)\s+CURSOR.*?FOR\s+(.*)', block, re.IGNORECASE | re.DOTALL)
            if cursor_match:
                cursor_name = cursor_match.group(1)
                cursor_definition = cursor_match.group(2).strip()
                
                self.sql_declarations.append({
                    "op": "SQL_CURSOR_DECLARE",
                    "cursor_name": cursor_name,
                    "definition": cursor_definition,
                    "raw": f"EXEC SQL {block} END-EXEC."
                })
    
    def _parse_cursors(self, content: str):
        """Parsea cursores SQL"""
        # OPEN CURSOR
        open_cursor_pattern = r'OPEN\s+(\w+)'
        for match in re.finditer(open_cursor_pattern, content, re.IGNORECASE):
            cursor_name = match.group(1)
            self.cursors.append({
                "op": "OPEN_CURSOR",
                "cursor_name": cursor_name
            })
        
        # FETCH CURSOR
        fetch_cursor_pattern = r'FETCH\s+(\w+)\s+INTO\s+(.+)'
        for match in re.finditer(fetch_cursor_pattern, content, re.IGNORECASE):
            cursor_name = match.group(1)
            into_clause = match.group(2)
            self.cursors.append({
                "op": "FETCH_CURSOR",
                "cursor_name": cursor_name,
                "into_clause": into_clause
            })
        
        # CLOSE CURSOR
        close_cursor_pattern = r'CLOSE\s+(\w+)'
        for match in re.finditer(close_cursor_pattern, content, re.IGNORECASE):
            cursor_name = match.group(1)
            self.cursors.append({
                "op": "CLOSE_CURSOR",
                "cursor_name": cursor_name
            })
    
    def _parse_services(self, content: str):
        """Parsea llamadas a servicios"""
        # @INVOCAR
        invocar_pattern = r'@INVOCAR\((\w+),(\w+)\)'
        for match in re.finditer(invocar_pattern, content, re.IGNORECASE):
            service_name = match.group(1)
            service_type = match.group(2)
            self.services.append({
                "op": "INVOCAR",
                "service_name": service_name,
                "service_type": service_type
            })
        
        # PRC_SRV_*
        prc_pattern = r'PRC_SRV_(\w+)'
        for match in re.finditer(prc_pattern, content, re.IGNORECASE):
            service_name = match.group(1)
            self.services.append({
                "op": "PRC_SRV",
                "service_name": service_name
            })
    
    def _parse_macros(self, content: str):
        """Parsea macros COBOL"""
        macro_pattern = r'@(\w+)\(([^)]*)\)'
        for match in re.finditer(macro_pattern, content, re.IGNORECASE):
            macro_name = match.group(1)
            macro_params = match.group(2) if match.group(2) else ""
            self.macros.append({
                "op": "MACRO",
                "macro_name": macro_name,
                "params": macro_params
            })
    
    def _parse_conditions(self, content: str):
        """Parsea condiciones 88"""
        # Ya se parsean en _parse_working_storage
        pass
    
    def _parse_literals(self, content: str):
        """Parsea literales"""
        # Ya se parsean en _parse_working_storage
        pass
    
    def _parse_structures(self, content: str):
        """Parsea estructuras complejas"""
        # REDEFINES
        redefines_pattern = r'(\d+)\s+(\w+)\s+REDEFINES\s+(\w+)'
        for match in re.finditer(redefines_pattern, content, re.IGNORECASE):
            level = match.group(1)
            name = match.group(2)
            redefines = match.group(3)
            self.structures.append({
                "op": "REDEFINES",
                "level": level,
                "name": name,
                "redefines": redefines
            })
    
    def apply_rule(self, stmt: Dict[str, Any], base_indent: str = "    ") -> str:
        """Aplica reglas de conversión a sentencias"""
        op = stmt.get("op", "UNKNOWN")
        
        if op == "PERFORM":
            target = stmt.get("target", "")
            target_clean = self.clean_expression(target)
            return f"{base_indent}{target_clean}();"
        
        elif op == "PERFORM_UNTIL":
            target = stmt.get("target", "")
            condition = stmt.get("condition", "")
            target_clean = self.clean_expression(target)
            condition_clean = self.clean_expression(condition)
            return f"{base_indent}WHILE NOT ({condition_clean}) LOOP\n{base_indent}  {target_clean}();\n{base_indent}END LOOP;"
        
        elif op == "MOVE":
            from_val = stmt.get("from", "")
            to_val = stmt.get("to", "")
            from_clean = self.clean_expression(from_val)
            to_clean = self.clean_expression(to_val)
            return f"{base_indent}{to_clean} := {from_clean};"
        
        elif op == "IF":
            condition = stmt.get("condition", "")
            condition_clean = self.clean_expression(condition)
            return f"{base_indent}IF {condition_clean} THEN"
        
        elif op == "DISPLAY":
            message = stmt.get("message", "")
            message_clean = self.clean_expression(message)
            return f"{base_indent}DBMS_OUTPUT.PUT_LINE({message_clean});"
        
        elif op == "STRING":
            expression = stmt.get("expression", "")
            return f"{base_indent}-- STRING: {expression}"
        
        elif op == "EVALUATE":
            expression = stmt.get("expression", "")
            return f"{base_indent}-- EVALUATE: {expression}"
        
        elif op == "OPEN":
            mode = stmt.get("mode", "")
            file_name = stmt.get("file", "")
            file_clean = self.clean_expression(file_name)
            return f"{base_indent}-- OPEN {mode} {file_clean}"
        
        elif op == "CLOSE":
            file_name = stmt.get("file", "")
            file_clean = self.clean_expression(file_name)
            return f"{base_indent}-- CLOSE {file_clean}"
        
        elif op == "READ":
            file_name = stmt.get("file", "")
            file_clean = self.clean_expression(file_name)
            return f"{base_indent}-- READ {file_clean}"
        
        elif op == "WRITE":
            file_name = stmt.get("file", "")
            file_clean = self.clean_expression(file_name)
            return f"{base_indent}-- WRITE {file_clean}"
        
        elif op == "INITIALIZE":
            target = stmt.get("target", "")
            target_clean = self.clean_expression(target)
            if "RETURN-CODE" in target.upper():
                return f"{base_indent}RETURN_CODE := 0;"
            else:
                return f"{base_indent}{target_clean} := NULL;"
        
        elif op == "ADD":
            value = stmt.get("value", "")
            to_val = stmt.get("to", "")
            to_clean = self.clean_expression(to_val)
            return f"{base_indent}{to_clean} := {to_clean} + {value};"
        
        elif op == "COMMIT":
            return f"{base_indent}COMMIT;"
        
        elif op == "ROLLBACK":
            return f"{base_indent}ROLLBACK;"
        
        elif op == "SQL_INCLUDE":
            table_name = stmt.get("table", "")
            table_clean = self.clean_expression(table_name)
            return f"{base_indent}-- INCLUDE de tabla {table_clean}\n{base_indent}-- %INCLUDE {table_clean}.INC"
        
        elif op == "SQL_CURSOR_DECLARE":
            cursor_name = stmt.get("cursor_name", "")
            cursor_definition = stmt.get("definition", "")
            cursor_clean = self.clean_expression(cursor_name)
            
            # Limpiar la definición del cursor para PL/SQL
            clean_definition = cursor_definition
            clean_definition = re.sub(r'^WITH\s+HOLD\s+FOR\s*', '', clean_definition, flags=re.IGNORECASE)
            clean_definition = re.sub(r'^FOR\s*', '', clean_definition, flags=re.IGNORECASE)
            clean_definition = clean_definition.strip()
            
            return f"{base_indent}CURSOR {cursor_clean} IS\n{base_indent}  {clean_definition};"
        
        else:
            # GAP - sentencia no reconocida
            raw = stmt.get("raw", "")
            return f"{base_indent}-- GAP: {raw}"
    
    def generate_package(self, ir: Dict[str, Any]) -> str:
        """Genera el paquete PL/SQL completo"""
        program_name = ir.get("program", "UNKNOWN")
        program_name_clean = self.clean_expression(program_name)
        
        # Generar declaraciones de variables
        var_declarations = []
        for var in ir.get("variables", []):
            name = self.clean_expression(var.get("name", ""))
            var_type = var.get("type", "STRING")
            size = var.get("size", 1)
            
            if var_type == "STRING":
                plsql_type = f"VARCHAR2({size})"
            else:
                plsql_type = f"NUMBER({size})"
            
            var_declarations.append(f"  {name} {plsql_type};")
        
        # Generar declaraciones de archivos
        file_declarations = []
        for file in ir.get("files", []):
            file_name = self.clean_expression(file.get("name", ""))
            file_declarations.append(f"  {file_name} UTL_FILE.FILE_TYPE;")
        
        # Generar declaraciones de registros
        record_declarations = []
        for record in ir.get("file_structures", []):
            record_name = self.clean_expression(record.get("record_name", ""))
            pic_clause = record.get("pic_clause", "")
            # Extraer tamaño del PIC
            size_match = re.search(r'(\d+)', pic_clause)
            size = int(size_match.group(1)) if size_match else 80
            record_declarations.append(f"  {record_name} CHAR({size});")
        
        # Generar declaraciones SQL
        sql_declarations = []var
        for sql_decl in ir.get("sql_declarations", []):
            sql_declarations.append(self.apply_rule(sql_decl, "  "))
        
        # Generar cursores
        cursor_declarations = []
        for cursor in ir.get("cursors", []):
            if cursor.get("op") == "OPEN_CURSOR":
                cursor_name = self.clean_expression(cursor.get("cursor_name", ""))
                cursor_declarations.append(f"  -- OPEN {cursor_name}")
            elif cursor.get("op") == "FETCH_CURSOR":
                cursor_name = self.clean_expression(cursor.get("cursor_name", ""))
                into_clause = cursor.get("into_clause", "")
                cursor_declarations.append(f"  -- FETCH {cursor_name} INTO {into_clause}")
            elif cursor.get("op") == "CLOSE_CURSOR":
                cursor_name = self.clean_expression(cursor.get("cursor_name", ""))
                cursor_declarations.append(f"  -- CLOSE {cursor_name}")
        
        # Generar procedimientos
        procedure_declarations = []
        for proc in ir.get("procedures", []):
            proc_name = self.clean_expression(proc.get("name", ""))
            procedure_declarations.append(f"  PROCEDURE {proc_name};")
        
        # Generar cuerpo del paquete
        package_body = self._generate_package_body(ir)
        
        # Construir el paquete completo
        package = f"""CREATE OR REPLACE PACKAGE {program_name_clean} IS

  -- ENVIRONMENT DIVISION.
  -- INPUT-OUTPUT SECTION.
{chr(10).join(file_declarations)}

  -- FILE SECTION.
{chr(10).join(record_declarations)}

  -- WORKING-STORAGE SECTION.
{chr(10).join(var_declarations)}

  -- SQL DECLARATIONS.
{chr(10).join(sql_declarations)}

  -- CURSOR OPERATIONS.
{chr(10).join(cursor_declarations)}

  -- PROCEDURE DECLARATIONS.
{chr(10).join(procedure_declarations)}

  -- MAIN PROCEDURE
  PROCEDURE MAIN;

END {program_name_clean};
/

{package_body}"""
        
        return package
    
    def _generate_package_body(self, ir: Dict[str, Any]) -> str:
        """Genera el cuerpo del paquete PL/SQL"""
        program_name = ir.get("program", "UNKNOWN")
        program_name_clean = self.clean_expression(program_name)
        
        # Generar procedimiento MAIN
        main_lines = []
        for proc in ir.get("procedures", []):
            for stmt in proc.get("statements", []):
                out = self.apply_rule(stmt)
                main_lines.append(out)
        
        # Generar procedimientos individuales
        procedure_bodies = []
        for proc in ir.get("procedures", []):
            proc_name = self.clean_expression(proc.get("name", ""))
            proc_statements = []
            
            for stmt in proc.get("statements", []):
                out = self.apply_rule(stmt)
                proc_statements.append(out)
            
            if proc_statements:
                procedure_bodies.append(f"""  PROCEDURE {proc_name} IS
  BEGIN
{chr(10).join(proc_statements)}
  END {proc_name};""")
        
        # Construir el cuerpo del paquete
        package_body = f"""CREATE OR REPLACE PACKAGE BODY {program_name_clean} IS

  PROCEDURE MAIN IS
  BEGIN
{chr(10).join(main_lines)}
  END MAIN;

{chr(10).join(procedure_bodies)}

END {program_name_clean};
/"""
        
        return package_body

def main():
    if len(sys.argv) != 2:
        print("Uso: python advanced_converter.py <archivo_cobol>")
        sys.exit(1)
    
    cobol_file = sys.argv[1]
    
    if not os.path.exists(cobol_file):
        print(f"Error: El archivo {cobol_file} no existe")
        sys.exit(1)
    
    # Leer archivo COBOL
    with open(cobol_file, 'r', encoding='utf-8', errors='ignore') as f:
        cobol_content = f.read()
    
    # Convertir
    converter = AdvancedCobolConverter()
    ir = converter.parse_cobol_to_ir(cobol_content)
    
    # Generar archivos de salida
    base_name = os.path.splitext(os.path.basename(cobol_file))[0]
    
    # Guardar IR
    ir_file = f"out/{base_name}_ir.json"
    with open(ir_file, 'w', encoding='utf-8') as f:
        json.dump(ir, f, indent=2, ensure_ascii=False)
    
    # Generar PL/SQL
    plsql_content = converter.generate_package(ir)
    sql_file = f"out/{base_name}.sql"
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(plsql_content)
    
    # Generar reporte
    report = {
        "program": base_name,
        "coverage": {
            "rules": len([stmt for proc in ir.get("procedures", []) for stmt in proc.get("statements", []) if stmt.get("op") != "UNKNOWN"]),
            "gaps": len([stmt for proc in ir.get("procedures", []) for stmt in proc.get("statements", []) if stmt.get("op") == "UNKNOWN"])
        },
        "method": "ADVANCED"
    }
    
    report_file = f"out/{base_name}_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Conversión completada:")
    print(f"  IR: {ir_file}")
    print(f"  SQL: {sql_file}")
    print(f"  Reporte: {report_file}")
    print(f"  Reglas aplicadas: {report['coverage']['rules']}")
    print(f"  GAPs: {report['coverage']['gaps']}")

if __name__ == "__main__":
    main()

