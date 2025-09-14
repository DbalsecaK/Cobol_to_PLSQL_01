#!/usr/bin/env python3
"""
Convertidor Mejorado COBOL a PL/SQL
Versión corregida con soporte para PERFORM y VALUE
"""

import re
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple

class EnhancedCobolConverter:
    def __init__(self):
        self.program_name = ""
        self.variables = []
        self.files = []
        self.file_structures = []
        self.sql_declarations = []
        self.procedures = []
        
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
        """Parsea COBOL a representación intermedia mejorada"""
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
        
        return {
            "program": self.program_name,
            "variables": self.variables,
            "files": self.files,
            "file_structures": self.file_structures,
            "sql_declarations": self.sql_declarations,
            "procedures": self.procedures
        }
    
    def _parse_environment_division(self, content: str):
        """Parsea ENVIRONMENT DIVISION"""
        # INPUT-OUTPUT SECTION
        input_output_match = re.search(
            r'INPUT-OUTPUT\s+SECTION\.(.*?)(?=DATA\s+DIVISION|PROCEDURE\s+DIVISION|$)',
            content, re.IGNORECASE | re.DOTALL
        )
        
        if input_output_match:
            input_output_content = input_output_match.group(1)
            self._parse_file_control(input_output_content)
        
        # WORKING-STORAGE SECTION
        working_storage_match = re.search(
            r'WORKING-STORAGE\s+SECTION\.(.*?)(?=PROCEDURE\s+DIVISION|$)',
            content, re.IGNORECASE | re.DOTALL
        )
        
        if working_storage_match:
            working_storage_content = working_storage_match.group(1)
            self._parse_working_storage(working_storage_content)
    
    def _parse_file_control(self, content: str):
        """Parsea FILE-CONTROL"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # SELECT file-name ASSIGN TO logical-name
            select_match = re.match(r'SELECT\s+(\w+)\s+ASSIGN\s+TO\s+(\w+)', line, re.IGNORECASE)
            if select_match:
                file_name = select_match.group(1)
                logical_name = select_match.group(2)
                
                self.files.append({
                    "name": file_name,
                    "logical_name": logical_name
                })
    
    def _parse_working_storage(self, content: str):
        """Parsea WORKING-STORAGE SECTION mejorado con VALUE"""
        lines = content.split('\n')
        filler_counter = 1  # Contador para variables FILLER únicas
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # Parsear variables con nombres completos incluyendo VALUE
            var_match = re.match(r'(\d+)\s+([A-Z0-9-]+).*?PIC\s+([^\s]+)(?:\s+VALUE\s+([^\.]+))?', line, re.IGNORECASE)
            if var_match:
                level = var_match.group(1)
                name = var_match.group(2)
                pic_clause = var_match.group(3).strip()
                value_clause = var_match.group(4).strip() if var_match.group(4) else None
                
                # Hacer únicas las variables FILLER
                if name.upper() == 'FILLER':
                    name = f"FILLER_{filler_counter:03d}"
                    filler_counter += 1
                
                # Determinar tipo y tamaño
                var_type, size = self._parse_pic_clause(pic_clause)
                
                self.variables.append({
                    "level": level,
                    "name": name,
                    "type": var_type,
                    "size": size,
                    "pic_clause": pic_clause,
                    "value": value_clause
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
        s9_match = re.search(r'S9\((\d+)\)', pic_clause)
        if s9_match:
            return "NUMERIC", int(s9_match.group(1))
        
        # PIC S9n - Signed Numeric
        s9_match = re.search(r'S9(\d+)', pic_clause)
        if s9_match:
            return "NUMERIC", int(s9_match.group(1))
        
        # PIC Z(n) - Zero Suppressed Numeric
        z_match = re.search(r'Z\((\d+)\)', pic_clause)
        if z_match:
            return "NUMERIC", int(z_match.group(1))
        
        # PIC Zn - Zero Suppressed Numeric
        z_match = re.search(r'Z(\d+)', pic_clause)
        if z_match:
            return "NUMERIC", int(z_match.group(1))
        
        # Default
        return "STRING", 10
    
    def _parse_data_division(self, content: str):
        """Parsea DATA DIVISION"""
        # FILE SECTION
        file_section_match = re.search(
            r'FILE\s+SECTION\.(.*?)(?=WORKING-STORAGE\s+SECTION|PROCEDURE\s+DIVISION|$)',
            content, re.IGNORECASE | re.DOTALL
        )
        
        if file_section_match:
            file_section_content = file_section_match.group(1)
            self._parse_file_section(file_section_content)
    
    def _parse_file_section(self, content: str):
        """Parsea FILE SECTION"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # FD file-name
            fd_match = re.match(r'FD\s+(\w+)', line, re.IGNORECASE)
            if fd_match:
                file_name = fd_match.group(1)
                
                self.file_structures.append({
                    "name": file_name,
                    "type": "FD"
                })
    
    def _parse_procedure_division(self, content: str):
        """Parsea PROCEDURE DIVISION"""
        procedure_match = re.search(
            r'PROCEDURE\s+DIVISION\.(.*?)(?=END\s+PROGRAM|$)',
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
            
            # Identificar inicio de procedimiento (solo números seguidos de guiones y letras)
            proc_match = re.match(r'(\d+-\w+(?:-\w+)*)\.?$', line, re.IGNORECASE)
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
        
        # Palabras clave de cierre COBOL - ignorar
        if re.match(r'^(END-EXEC|END-IF|END-EVALUATE|END-PERFORM|END-READ|END-WRITE|END-STRING|END-UNSTRING)\.?$', line, re.IGNORECASE):
            return None
        
        # MACROS COBOL (líneas que inician con @)
        macro_match = re.match(r'@(\w+)(?:\(([^)]*)\))?', line, re.IGNORECASE)
        if macro_match:
            macro_name = macro_match.group(1)
            macro_params = macro_match.group(2) if macro_match.group(2) else ""
            return {
                "op": "MACRO",
                "macro_name": macro_name,
                "params": macro_params,
                "raw": line
            }
        
        # PERFORM - Corregido para capturar nombres completos
        perform_match = re.match(r'PERFORM\s+([A-Z0-9]+(?:-[A-Z0-9]+)*)\.?', line, re.IGNORECASE)
        if perform_match:
            return {
                "op": "PERFORM",
                "target": perform_match.group(1)
            }
        
        # PERFORM UNTIL - Corregido para capturar nombres completos
        perform_until_match = re.match(r'PERFORM\s+([A-Z0-9]+(?:-[A-Z0-9]+)*)\s+UNTIL\s+(.+)', line, re.IGNORECASE)
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
        
        # INITIALIZE
        initialize_match = re.match(r'INITIALIZE\s+(.+)', line, re.IGNORECASE)
        if initialize_match:
            return {
                "op": "INITIALIZE",
                "target": initialize_match.group(1).strip()
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
        # Buscar bloques EXEC SQL usando un enfoque más robusto
        exec_sql_pattern = r'EXEC\s+SQL\s+(.*?)END-EXEC\.'
        sql_blocks = re.findall(exec_sql_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for sql_block in sql_blocks:
            sql_block = sql_block.strip()
            
            # INCLUDE
            include_match = re.search(r'INCLUDE\s+(\w+)', sql_block, re.IGNORECASE)
            if include_match:
                table_name = include_match.group(1)
                self.sql_declarations.append({
                    "op": "SQL_INCLUDE",
                    "table": table_name,
                    "raw": f"EXEC SQL INCLUDE {table_name} END-EXEC."
                })
            
            # DECLARE CURSOR - buscar en todo el bloque
            cursor_match = re.search(r'DECLARE\s+(\w+)\s+CURSOR\s+(.*)', sql_block, re.IGNORECASE | re.DOTALL)
            if cursor_match:
                cursor_name = cursor_match.group(1)
                cursor_definition = cursor_match.group(2).strip()
                
                # Limpiar la definición del cursor
                # Remover WITH HOLD FOR y FOR al final
                cursor_definition = re.sub(r'\s+WITH\s+HOLD\s+FOR\s*$', '', cursor_definition, flags=re.IGNORECASE)
                cursor_definition = re.sub(r'\s+FOR\s*$', '', cursor_definition, flags=re.IGNORECASE)
                
                self.sql_declarations.append({
                    "op": "SQL_CURSOR_DECLARE",
                    "cursor_name": cursor_name,
                    "definition": cursor_definition,
                    "raw": f"EXEC SQL DECLARE {cursor_name} CURSOR {cursor_definition} END-EXEC."
                })
    
    def apply_rule(self, stmt: Dict[str, Any], base_indent: str = "    ") -> str:
        """Aplica reglas de conversión a una sentencia"""
        op = stmt.get("op", "UNKNOWN")
        
        if op == "MOVE":
            from_expr = self.clean_expression(stmt.get("from", ""))
            to_expr = self.clean_expression(stmt.get("to", ""))
            return f"{base_indent}{to_expr} := {from_expr};"
        
        elif op == "IF":
            condition = self.clean_expression(stmt.get("condition", ""))
            return f"{base_indent}IF {condition} THEN"
        
        elif op == "DISPLAY":
            message = stmt.get("message", "")
            return f"{base_indent}DBMS_OUTPUT.PUT_LINE({message});"
        
        elif op == "PERFORM":
            target = self.clean_expression(stmt.get("target", ""))
            return f"{base_indent}{target}();"
        
        elif op == "PERFORM_UNTIL":
            target = self.clean_expression(stmt.get("target", ""))
            condition = self.clean_expression(stmt.get("condition", ""))
            return f"{base_indent}WHILE NOT ({condition}) LOOP\n{base_indent}  {target}();\n{base_indent}END LOOP;"
        
        elif op == "INITIALIZE":
            target = self.clean_expression(stmt.get("target", ""))
            if target.upper() == "RETURN_CODE":
                return f"{base_indent}{target} := 0;"
            else:
                return f"{base_indent}{target} := NULL;"
        
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
            
            # Remover WITH HOLD FOR y FOR al final
            clean_definition = re.sub(r'\s+WITH\s+HOLD\s+FOR\s*$', '', clean_definition, flags=re.IGNORECASE)
            clean_definition = re.sub(r'\s+FOR\s*$', '', clean_definition, flags=re.IGNORECASE)
            
            # Convertir variables COBOL a PL/SQL (:WS-COD-INCID -> WS_COD_INCID)
            clean_definition = re.sub(r':([A-Z0-9-]+)', lambda m: self.clean_expression(m.group(1)), clean_definition)
            
            # Agregar esquema NEXTI a las tablas (FROM T12INC06 -> FROM NEXTI.T12INC06)
            clean_definition = re.sub(r'\bFROM\s+([A-Z0-9]+)\b', r'FROM NEXTI.\1', clean_definition, flags=re.IGNORECASE)
            
            clean_definition = clean_definition.strip()
            
            return f"{base_indent}CURSOR {cursor_clean} IS\n{base_indent}  {clean_definition};"
        
        elif op == "MACRO":
            macro_name = stmt.get("macro_name", "")
            macro_params = stmt.get("params", "")
            raw = stmt.get("raw", "")
            
            # Convertir macro a comentario PL/SQL
            if macro_params:
                return f"{base_indent}-- MACRO COBOL: {macro_name}({macro_params})"
            else:
                return f"{base_indent}-- MACRO COBOL: {macro_name}"
        
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
            value = var.get("value")
            
            if var_type == "STRING":
                plsql_type = f"VARCHAR2({size})"
            else:
                plsql_type = f"NUMBER({size})"
            
            # Incluir inicialización si hay VALUE
            if value:
                # Limpiar el valor (remover comillas si las tiene)
                clean_value = value.strip().strip("'\"")
                
                # Convertir valores COBOL a PL/SQL
                if clean_value.upper() == 'ZEROS':
                    if var_type == "NUMERIC":
                        clean_value = "0"
                    else:
                        clean_value = "'0'"
                elif clean_value.upper() == 'SPACES':
                    clean_value = "''"
                elif clean_value.upper() == 'SPACE':
                    clean_value = "' '"
                else:
                    # Si es un valor literal, mantenerlo con comillas
                    if not clean_value.startswith("'") and not clean_value.isdigit():
                        clean_value = f"'{clean_value}'"
                
                var_declarations.append(f"  {name} {plsql_type} := {clean_value};")
            else:
                var_declarations.append(f"  {name} {plsql_type};")
        
        # Generar declaraciones de archivos
        file_declarations = []
        for file in ir.get("files", []):
            file_name = self.clean_expression(file.get("name", ""))
            file_declarations.append(f"  {file_name} UTL_FILE.FILE_TYPE;")
        
        # Generar declaraciones de registros
        record_declarations = []
        for file_struct in ir.get("file_structures", []):
            file_name = self.clean_expression(file_struct.get("name", ""))
            record_declarations.append(f"  RECORD_{file_name} CHAR(133);")
        
        # Generar declaraciones SQL
        sql_declarations = []
        for sql_decl in ir.get("sql_declarations", []):
            sql_declarations.append(self.apply_rule(sql_decl, "  "))
        
        # Generar procedimientos
        procedure_declarations = []
        main_lines = []
        coverage = {"rules": 0, "gaps": 0}
        
        for proc in ir.get("procedures", []):
            proc_name = self.clean_expression(proc.get("name", ""))
            procedure_declarations.append(f"  PROCEDURE {proc_name};")
            
            # Generar implementación del procedimiento
            proc_lines = [f"  PROCEDURE {proc_name} IS"]
            proc_lines.append("  BEGIN")
            
            for stmt in proc.get("statements", []):
                converted = self.apply_rule(stmt, "    ")
                proc_lines.append(converted)
                
                # Contar reglas y gaps
                if stmt.get("op") == "UNKNOWN":
                    coverage["gaps"] += 1
                else:
                    coverage["rules"] += 1
            
            proc_lines.append("  END;")
            main_lines.extend(proc_lines)
            main_lines.append("")
        
        # Generar MAIN procedure
        main_lines.append("  -- MAIN PROCEDURE")
        main_lines.append("  PROCEDURE MAIN;")
        main_lines.append("")
        main_lines.append("  PROCEDURE MAIN IS")
        main_lines.append("  BEGIN")
        
        # Llamadas a procedimientos
        for proc in ir.get("procedures", []):
            proc_name = self.clean_expression(proc.get("name", ""))
            main_lines.append(f"    {proc_name}();")
        
        main_lines.append("  END;")
        
        # Construir el paquete completo
        package_lines = [
            f"CREATE OR REPLACE PACKAGE {program_name_clean} IS",
            "",
            "  -- ENVIRONMENT DIVISION.",
            "  -- INPUT-OUTPUT SECTION."
        ]
        
        if file_declarations:
            package_lines.extend(file_declarations)
            package_lines.append("")
        
        package_lines.extend([
            "  -- FILE SECTION."
        ])
        
        if record_declarations:
            package_lines.extend(record_declarations)
            package_lines.append("")
        
        package_lines.extend([
            "  -- WORKING-STORAGE SECTION."
        ])
        
        if var_declarations:
            package_lines.extend(var_declarations)
            package_lines.append("")
        
        if sql_declarations:
            package_lines.extend([
                "  -- SQL DECLARATIONS."
            ])
            package_lines.extend(sql_declarations)
            package_lines.append("")
        
        package_lines.extend([
            "  -- PROCEDURE DECLARATIONS."
        ])
        
        if procedure_declarations:
            package_lines.extend(procedure_declarations)
            package_lines.append("")
        
        package_lines.extend([
            "  -- MAIN PROCEDURE",
            "  PROCEDURE MAIN;",
            "",
            "END;",
            "/",
            "",
            f"CREATE OR REPLACE PACKAGE BODY {program_name_clean} IS",
            ""
        ])
        
        package_lines.extend(main_lines)
        package_lines.extend([
            "",
            "END;",
            "/"
        ])
        
        return "\n".join(package_lines)

def main():
    if len(sys.argv) != 2:
        print("Uso: python enhanced_converter_perform_fixed.py <archivo_cobol>")
        sys.exit(1)
    
    cobol_file = sys.argv[1]
    
    if not os.path.exists(cobol_file):
        print(f"Error: El archivo {cobol_file} no existe")
        sys.exit(1)
    
    # Leer archivo COBOL
    with open(cobol_file, 'r', encoding='utf-8', errors='ignore') as f:
        cobol_content = f.read()
    
    # Crear convertidor
    converter = EnhancedCobolConverter()
    
    # Parsear COBOL a IR
    ir = converter.parse_cobol_to_ir(cobol_content)
    
    # Generar PL/SQL
    plsql_code = converter.generate_package(ir)
    
    # Guardar archivos
    base_name = os.path.splitext(os.path.basename(cobol_file))[0]
    
    # IR
    ir_file = f"out/{base_name}_ir.json"
    with open(ir_file, 'w', encoding='utf-8') as f:
        json.dump(ir, f, indent=2, ensure_ascii=False)
    
    # PL/SQL
    sql_file = f"out/{base_name}.sql"
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(plsql_code)
    
    # Reporte
    coverage = {"rules": 0, "gaps": 0}
    for proc in ir.get("procedures", []):
        for stmt in proc.get("statements", []):
            if stmt.get("op") == "UNKNOWN":
                coverage["gaps"] += 1
            else:
                coverage["rules"] += 1
    
    report = {
        "program": base_name,
        "coverage": coverage,
        "method": "ENHANCED_PERFORM_FIXED"
    }
    
    report_file = f"out/{base_name}_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Conversión completada:")
    print(f"  IR: {ir_file}")
    print(f"  SQL: {sql_file}")
    print(f"  Reporte: {report_file}")
    print(f"  Reglas aplicadas: {coverage['rules']}")
    print(f"  GAPs: {coverage['gaps']}")

if __name__ == "__main__":
    main()
