#!/usr/bin/env python3
"""
Convertidor Mejorado COBOL a PL/SQL
Versión mejorada basada en el análisis del programa C1040.cob
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
        
        # Configuración de valores especiales COBOL para MOVE statements
        self.special_values = {
            'SPACES': "''",  # Empty string
            'ZEROS': '0',
            'ZERO': '0',
            'HIGH-VALUES': "CHR(255)",
            'LOW-VALUES': "CHR(0)",
            'QUOTES': "'\"'",
        }
        
        # Patrones para diferentes tipos de valores
        self.numeric_pattern = re.compile(r'^\d+(\.\d+)?$')
        self.string_literal_pattern = re.compile(r'^[\'"](.*?)[\'"]$')
        self.identifier_pattern = re.compile(r'^[A-Z0-9_-]+$', re.IGNORECASE)
        
    def clean_expression(self, expr: str) -> str:
        """Limpia expresiones COBOL para PL/SQL"""
        if not expr:
            return ""
        
        # Reemplazar guiones con guiones bajos
        expr = expr.replace('-', '_')
        
        # Limpiar espacios y caracteres especiales
        expr = re.sub(r'\s+', ' ', expr.strip())
        
        return expr
    
    def clean_identifier(self, identifier: str) -> str:
        """Clean and normalize COBOL identifiers for PL/SQL"""
        cleaned = re.sub(r'\s+', ' ', identifier.strip())
        return cleaned.lower()
    
    def parse_move_source(self, source: str) -> str:
        """Parse MOVE source expression with all variations"""
        source = source.strip()
        
        # Handle string literals
        if (source.startswith("'") and source.endswith("'")) or \
           (source.startswith('"') and source.endswith('"')):
            return source
        
        # Handle numeric literals
        if self.numeric_pattern.match(source):
            return source
        
        # Handle special COBOL values
        upper_source = source.upper()
        if upper_source in self.special_values:
            return self.special_values[upper_source]
        
        # Handle qualified names (FIELD OF GROUP)
        if ' OF ' in upper_source:
            parts = source.split(' OF ')
            if len(parts) == 2:
                field = self.clean_identifier(parts[0])
                group = self.clean_identifier(parts[1])
                return f"{group}.{field}"
        
        # Handle subscripted variables (FIELD(INDEX))
        if '(' in source and ')' in source:
            match = re.match(r'^([A-Z0-9_-]+)\(([A-Z0-9_-]+)\)', source, re.IGNORECASE)
            if match:
                var_name = self.clean_identifier(match.group(1))
                index = self.clean_identifier(match.group(2))
                return f"{var_name}({index})"
        
        # Regular variable name
        return self.clean_identifier(source)
    
    def parse_move_targets(self, targets: str) -> List[str]:
        """Parse multiple targets in MOVE statement"""
        targets_list = []
        current_target = ""
        paren_count = 0
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(targets):
            char = targets[i]
            
            # Handle quotes
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            
            # Handle parentheses (for subscripted variables and qualified names)
            if not in_quotes:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == ',' and paren_count == 0:
                    if current_target.strip():
                        targets_list.append(current_target.strip())
                    current_target = ""
                    i += 1
                    continue
            
            current_target += char
            i += 1
        
        if current_target.strip():
            targets_list.append(current_target.strip())
        
        return targets_list
    
    def parse_move_statement_enhanced(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a complete MOVE statement with all variations"""
        # Enhanced regex patterns for MOVE statements
        patterns = [
            # MOVE with CORRESPONDING (debe ir primero para evitar conflictos)
            r'^MOVE\s+CORRESPONDING\s+(.+?)\s+TO\s+(.+?)(?:\.|$)',
            # Standard MOVE pattern
            r'^MOVE\s+(.+?)\s+TO\s+(.+?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                source = match.group(1).strip()
                targets = match.group(2).strip()
                
                # Check if it's CORRESPONDING
                is_corresponding = 'CORRESPONDING' in line.upper()
                
                return {
                    'op': 'MOVE_CORRESPONDING' if is_corresponding else 'MOVE',
                    'src': source,
                    'dst': targets,
                    'raw': line,
                    'is_corresponding': is_corresponding
                }
        
        return None
    
    def convert_move_statement_enhanced(self, stmt: Dict[str, Any]) -> str:
        """Convert MOVE statement to PL/SQL with proper formatting"""
        source = stmt.get('src', '')
        targets = stmt.get('dst', '')
        is_corresponding = stmt.get('is_corresponding', False)
        
        if is_corresponding:
            return self.convert_move_corresponding(source, targets)
        
        # Parse source
        source_expr = self.parse_move_source(source)
        
        # Parse targets (handle multiple targets)
        target_list = self.parse_move_targets(targets)
        
        # Generate assignments
        assignments = []
        for target in target_list:
            target_expr = self.parse_move_source(target)
            assignments.append(f"{target_expr} := {source_expr};")
        
        return "\n".join(assignments)
    
    def convert_move_corresponding(self, source: str, targets: str) -> str:
        """Convert MOVE CORRESPONDING to PL/SQL"""
        source_clean = self.clean_identifier(source)
        targets_clean = self.clean_identifier(targets)
        
        return f"-- MOVE CORRESPONDING {source_clean} TO {targets_clean}\n" \
               f"-- Note: This requires field-by-field mapping analysis\n" \
               f"-- {targets_clean} := {source_clean};"

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
        """Parsea WORKING-STORAGE SECTION mejorado"""
        lines = content.split('\n')
        filler_counter = 1  # Contador para nombres FILLER únicos
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # Parsear variables con nombres completos incluyendo VALUE
            # Improved approach: split by VALUE first, then parse PIC
            if 'PIC' in line.upper():
                # Split the line at VALUE to separate PIC and VALUE clauses
                if 'VALUE' in line.upper():
                    parts = re.split(r'\s+VALUE\s+', line, flags=re.IGNORECASE)
                    pic_part = parts[0]
                    value_clause = parts[1].rstrip('.').strip() if len(parts) > 1 else None
                else:
                    pic_part = line.rstrip('.')
                    value_clause = None
                
                # Parse the PIC part
                var_match = re.match(r'(\d+)\s+([A-Z0-9-]+).*?PIC\s+(.+)', pic_part, re.IGNORECASE)
                if var_match:
                    level = var_match.group(1)
                    name = var_match.group(2)
                    pic_clause = var_match.group(3).strip()
                    
                    # Si el nombre es FILLER, agregar secuencia numérica
                    if name.upper() == 'FILLER':
                        name = f"FILLER_{filler_counter}"
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
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('*'):
                i += 1
                continue
            
            # Identificar inicio de procedimiento
            # Solo procedimientos que empiecen con números o con letra seguida de números
            # Excluir variables (WS-, S21-, FS-, MSG-, etc.) y palabras clave de COBOL
            proc_match = re.match(r'((?:\d+|[A-Z]\d+)-[A-Z0-9]+(?:-[A-Z0-9]+)*)\.?$', line, re.IGNORECASE)
            if proc_match and not re.match(r'(END-\w+|WS-|S21-|FS-|MSG-|TL-|LT-|CABE-|REG-|NUM-|COD-|FEM-|HOR-)', line, re.IGNORECASE):
                # Guardar procedimiento anterior
                if current_procedure:
                    self.procedures.append({
                        "name": current_procedure,
                        "statements": current_statements
                    })
                
                # Iniciar nuevo procedimiento
                current_procedure = proc_match.group(1)
                current_statements = []
                i += 1
                continue
            
            # Parsear sentencias
            if current_procedure:
                # Verificar si es una sentencia multi-línea
                if re.match(r'(FETCH|SELECT)\s+[A-Z0-9_-]+', line, re.IGNORECASE):
                    # Buscar líneas continuas que contengan INTO o FROM
                    full_statement = line
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith('END-EXEC'):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('*'):
                            full_statement += " " + next_line
                        j += 1
                    
                    statement = self._parse_statement(full_statement)
                    if statement:
                        current_statements.append(statement)
                    i = j
                elif re.match(r'MOVE\s+', line, re.IGNORECASE):
                    # Manejar MOVE multi-línea
                    full_statement = line
                    j = i + 1
                    
                    # Buscar líneas continuas hasta encontrar un punto o una nueva sentencia
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line or next_line.startswith('*'):
                            j += 1
                            continue
                        
                        # Si la línea siguiente empieza con TO, es continuación del MOVE
                        if re.match(r'TO\s+', next_line, re.IGNORECASE):
                            full_statement += " " + next_line
                            j += 1
                        # Si la línea siguiente no empieza con TO y no es continuación, terminar
                        elif not re.match(r'^\s+[A-Z0-9_-]', next_line, re.IGNORECASE):
                            break
                        else:
                            # Es una línea de continuación (sin TO)
                            full_statement += " " + next_line
                            j += 1
                    
                    statement = self._parse_statement(full_statement)
                    if statement:
                        current_statements.append(statement)
                    i = j
                else:
                    statement = self._parse_statement(line)
                    if statement:
                        current_statements.append(statement)
                    i += 1
            else:
                i += 1
        
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
        
        # PERFORM
        perform_match = re.match(r'PERFORM\s+([A-Z0-9-]+)\.?', line, re.IGNORECASE)
        if perform_match:
            return {
                "op": "PERFORM",
                "target": perform_match.group(1)
            }
        
        # PERFORM UNTIL
        perform_until_match = re.match(r'PERFORM\s+([A-Z0-9-]+)\s+UNTIL\s+(.+)', line, re.IGNORECASE)
        if perform_until_match:
            return {
                "op": "PERFORM_UNTIL",
                "target": perform_until_match.group(1),
                "condition": perform_until_match.group(2)
            }
        
        # MOVE - Enhanced parsing
        move_result = self.parse_move_statement_enhanced(line)
        if move_result:
            return move_result
        
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
        
        # EXEC SQL blocks
        if re.match(r'EXEC\s+SQL', line, re.IGNORECASE):
            return {
                "op": "SQL_BLOCK_START",
                "raw": line
            }
        
        # OPEN CURSOR
        open_cursor_match = re.match(r'OPEN\s+([A-Z0-9_-]+)', line, re.IGNORECASE)
        if open_cursor_match:
            return {
                "op": "SQL_OPEN_CURSOR",
                "cursor_name": open_cursor_match.group(1)
            }
        
        # CLOSE CURSOR
        close_cursor_match = re.match(r'CLOSE\s+([A-Z0-9_-]+)', line, re.IGNORECASE)
        if close_cursor_match:
            return {
                "op": "SQL_CLOSE_CURSOR",
                "cursor_name": close_cursor_match.group(1)
            }
        
        # FETCH CURSOR
        fetch_cursor_match = re.match(r'FETCH\s+([A-Z0-9_-]+)', line, re.IGNORECASE)
        if fetch_cursor_match:
            return {
                "op": "SQL_FETCH_CURSOR",
                "cursor_name": fetch_cursor_match.group(1),
                "raw": line
            }
        
        # SELECT INTO (single row) - handle multi-line statements
        if re.match(r'SELECT\s+', line, re.IGNORECASE) and 'INTO' in line.upper():
            # Extract the complete SELECT statement
            select_match = re.search(r'SELECT\s+(.+?)\s+INTO\s+(.+)', line, re.IGNORECASE | re.DOTALL)
            if select_match:
                select_clause = select_match.group(1).strip()
                into_clause = select_match.group(2).strip()
                
                # Clean up the SELECT clause (remove FROM and WHERE parts)
                from_match = re.search(r'(.+?)\s+FROM\s+(.+)', select_clause, re.IGNORECASE)
                if from_match:
                    select_fields = from_match.group(1).strip()
                    from_clause = from_match.group(2).strip()
                    
                    # Extract WHERE clause if present
                    where_match = re.search(r'(.+?)\s+WHERE\s+(.+)', from_clause, re.IGNORECASE)
                    if where_match:
                        from_table = where_match.group(1).strip()
                        where_clause = where_match.group(2).strip()
                    else:
                        from_table = from_clause
                        where_clause = ""
                    
                    return {
                        "op": "SQL_SELECT_INTO",
                        "select_fields": select_fields,
                        "from_table": from_table,
                        "where_clause": where_clause,
                        "into_clause": into_clause,
                        "raw": line
                    }
                else:
                    return {
                        "op": "SQL_SELECT_INTO",
                        "select_clause": select_clause,
                        "into_clause": into_clause,
                        "raw": line
                    }
        
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
            cursor_match = re.search(r'DECLARE\s+([A-Z0-9_-]+)\s+CURSOR.*?FOR\s+(.*)', block, re.IGNORECASE | re.DOTALL)
            if cursor_match:
                cursor_name = cursor_match.group(1)
                cursor_definition = cursor_match.group(2).strip()
                
                self.sql_declarations.append({
                    "op": "SQL_CURSOR_DECLARE",
                    "cursor_name": cursor_name,
                    "definition": cursor_definition,
                    "raw": f"EXEC SQL {block} END-EXEC."
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
        
        elif op == "MOVE" or op == "MOVE_CORRESPONDING":
            return self.convert_move_statement_enhanced(stmt)
        
        elif op == "IF":
            condition = stmt.get("condition", "")
            condition_clean = self.clean_expression(condition)
            return f"{base_indent}IF {condition_clean} THEN"
        
        elif op == "DISPLAY":
            message = stmt.get("message", "")
            message_clean = self.clean_expression(message)
            return f"{base_indent}DBMS_OUTPUT.PUT_LINE({message_clean});"
        
        elif op == "INITIALIZE":
            target = stmt.get("target", "")
            target_clean = self.clean_expression(target)
            if "RETURN-CODE" in target.upper():
                return f"{base_indent}RETURN_CODE := 0;"
            else:
                return f"{base_indent}{target_clean} := NULL;"
        
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
            # Preserve cursor names with hyphens by replacing with underscores
            cursor_clean = cursor_name.replace('-', '_')
            
            # Limpiar la definición del cursor para PL/SQL
            clean_definition = cursor_definition
            clean_definition = re.sub(r'^WITH\s+HOLD\s+FOR\s*', '', clean_definition, flags=re.IGNORECASE)
            clean_definition = re.sub(r'^FOR\s*', '', clean_definition, flags=re.IGNORECASE)
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
        
        elif op == "SQL_OPEN_CURSOR":
            cursor_name = stmt.get("cursor_name", "")
            # Preserve cursor names with hyphens by replacing with underscores
            cursor_clean = cursor_name.replace('-', '_')
            return f"{base_indent}OPEN {cursor_clean};"
        
        elif op == "SQL_CLOSE_CURSOR":
            cursor_name = stmt.get("cursor_name", "")
            # Preserve cursor names with hyphens by replacing with underscores
            cursor_clean = cursor_name.replace('-', '_')
            return f"{base_indent}CLOSE {cursor_clean};"
        
        elif op == "SQL_FETCH_CURSOR":
            cursor_name = stmt.get("cursor_name", "")
            raw = stmt.get("raw", "")
            # Preserve cursor names with hyphens by replacing with underscores
            cursor_clean = cursor_name.replace('-', '_')
            
            # Extraer la cláusula INTO del FETCH
            into_match = re.search(r'INTO\s+(.+)', raw, re.IGNORECASE)
            if into_match:
                into_clause = into_match.group(1).strip()
                # Limpiar las variables de host (remover :)
                into_clean = re.sub(r':(\w+)', r'\1', into_clause)
                into_clean = self.clean_expression(into_clean)
                return f"{base_indent}FETCH {cursor_clean} INTO {into_clean};"
            else:
                return f"{base_indent}FETCH {cursor_clean};"
        
        elif op == "SQL_SELECT_INTO":
            # Handle enhanced SELECT INTO with separate components
            if "select_fields" in stmt:
                select_fields = stmt.get("select_fields", "")
                from_table = stmt.get("from_table", "")
                where_clause = stmt.get("where_clause", "")
                into_clause = stmt.get("into_clause", "")
                
                select_clean = self.clean_expression(select_fields)
                from_clean = self.clean_expression(from_table)
                into_clean = self.clean_expression(into_clause)
                # Limpiar las variables de host (remover :)
                into_clean = re.sub(r':(\w+)', r'\1', into_clean)
                
                if where_clause:
                    where_clean = self.clean_expression(where_clause)
                    where_clean = re.sub(r':(\w+)', r'\1', where_clean)
                    return f"{base_indent}SELECT {select_clean} FROM {from_clean} WHERE {where_clean} INTO {into_clean};"
                else:
                    return f"{base_indent}SELECT {select_clean} FROM {from_clean} INTO {into_clean};"
            else:
                # Fallback to original format
                select_clause = stmt.get("select_clause", "")
                into_clause = stmt.get("into_clause", "")
                select_clean = self.clean_expression(select_clause)
                into_clean = self.clean_expression(into_clause)
                # Limpiar las variables de host (remover :)
                into_clean = re.sub(r':(\w+)', r'\1', into_clean)
                return f"{base_indent}SELECT {select_clean} INTO {into_clean};"
        
        elif op == "SQL_BLOCK_START":
            return f"{base_indent}-- SQL Block Start"
        
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
                var_declarations.append(f"  {name} {plsql_type} := '{clean_value}';")
            else:
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
        sql_declarations = []
        for sql_decl in ir.get("sql_declarations", []):
            result = self.apply_rule(sql_decl, "  ")
            sql_declarations.append(result)
        
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
        print("Uso: python enhanced_converter.py <archivo_cobol>")
        sys.exit(1)

    cobol_file = sys.argv[1]
    
    if not os.path.exists(cobol_file):
        print(f"Error: El archivo {cobol_file} no existe")
        sys.exit(1)
    
    # Leer archivo COBOL
    with open(cobol_file, 'r', encoding='utf-8', errors='ignore') as f:
        cobol_content = f.read()
    
    # Convertir
    converter = EnhancedCobolConverter()
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
        "method": "ENHANCED"
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