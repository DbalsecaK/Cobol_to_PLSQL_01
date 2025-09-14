"""
COBOL STRING Handler - Implementación completa con principios SOLID
Maneja todas las variaciones de STRING de COBOL a PL/SQL según el documento de migración
"""

from typing import Optional, Dict, Any, List, Tuple
import re


class StringOperationType:
    """Enum para tipos de operaciones STRING"""
    BASIC_STRING = "BASIC_STRING"
    STRING_WITH_DELIMITED_BY_SIZE = "STRING_WITH_DELIMITED_BY_SIZE"
    STRING_WITH_DELIMITED_BY_SPACES = "STRING_WITH_DELIMITED_BY_SPACES"
    STRING_WITH_DELIMITED_BY_LITERAL = "STRING_WITH_DELIMITED_BY_LITERAL"
    STRING_WITH_DELIMITED_BY_VARIABLE = "STRING_WITH_DELIMITED_BY_VARIABLE"
    STRING_WITH_POINTER = "STRING_WITH_POINTER"
    STRING_WITH_OVERFLOW = "STRING_WITH_OVERFLOW"
    UNKNOWN = "UNKNOWN"


class StringComponent:
    """Clase para representar un componente de STRING"""
    
    def __init__(self, field: str, delimiter_type: str, delimiter_value: str = None):
        self.field = field
        self.delimiter_type = delimiter_type  # SIZE, SPACES, LITERAL, VARIABLE
        self.delimiter_value = delimiter_value  # Para LITERAL y VARIABLE
        self.clean_field = field.replace('-', '_').lower()
    
    def to_plsql(self) -> str:
        """Convierte el componente a PL/SQL"""
        if self.delimiter_type == "SIZE":
            return f"NVL({self.clean_field}, '')"
        elif self.delimiter_type == "SPACES":
            return f"RTRIM(NVL({self.clean_field}, ''))"
        elif self.delimiter_type == "LITERAL":
            return f"SUBSTR(NVL({self.clean_field}, ''), 1, INSTR(NVL({self.clean_field}, ''), '{self.delimiter_value}') - 1)"
        elif self.delimiter_type == "VARIABLE":
            clean_delimiter = self.delimiter_value.replace('-', '_').lower()
            return f"SUBSTR(NVL({self.clean_field}, ''), 1, INSTR(NVL({self.clean_field}, ''), {clean_delimiter}) - 1)"
        else:
            return f"NVL({self.clean_field}, '')"


class StringPatternMatcher:
    """
    Clase para detectar patrones de STRING
    Implementa Single Responsibility Principle
    """
    
    def __init__(self):
        self.patterns = {
            StringOperationType.BASIC_STRING: [
                r'^\s*STRING\s+(.+?)\s+INTO\s+([A-Z0-9-]+)\s*\.?\s*$',
                r'^\s*STRING\s+(.+?)\s+INTO\s+([A-Z0-9-]+)\s*$'
            ],
            StringOperationType.STRING_WITH_DELIMITED_BY_SIZE: [
                r'^\s*STRING\s+(.+?)\s+DELIMITED\s+BY\s+SIZE\s+INTO\s+([A-Z0-9-]+)\s*\.?\s*$'
            ],
            StringOperationType.STRING_WITH_DELIMITED_BY_SPACES: [
                r'^\s*STRING\s+(.+?)\s+DELIMITED\s+BY\s+SPACES\s+INTO\s+([A-Z0-9-]+)\s*\.?\s*$'
            ],
            StringOperationType.STRING_WITH_DELIMITED_BY_LITERAL: [
                r'^\s*STRING\s+(.+?)\s+DELIMITED\s+BY\s+\'([^\']+)\'\s+INTO\s+([A-Z0-9-]+)\s*\.?\s*$'
            ],
            StringOperationType.STRING_WITH_DELIMITED_BY_VARIABLE: [
                r'^\s*STRING\s+(.+?)\s+DELIMITED\s+BY\s+([A-Z0-9-]+)\s+INTO\s+([A-Z0-9-]+)\s*\.?\s*$'
            ]
        }
        
        # Patrones para detectar inicio de STRING multi-línea
        self.string_start_patterns = [
            r'^\s*STRING\s+(.+?)$',
            r'^\s*STRING\s*$'
        ]
        
        # Patrones para detectar continuaciones de STRING
        self.string_continuation_patterns = [
            r'^\s*([A-Z0-9_-]+)\s*$',  # Campo simple (más flexible con _)
            r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+SIZE\s*$',
            r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+SPACES\s*$',
            r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+\'([^\']+)\'\s*$',
            r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+([A-Z0-9_-]+)\s*$',
            r'^\s*INTO\s+([A-Z0-9_-]+)\s*\.?\s*$'
        ]
        
        # Patrones que indican el final del STRING
        self.string_end_patterns = [
            r'^\s*MOVE\s+',  # MOVE statement
            r'^\s*IF\s+',    # IF statement
            r'^\s*WHEN\s+',  # WHEN statement
            r'^\s*ELSE\s*$', # ELSE statement
            r'^\s*END\s+',   # END statement
            r'^\s*PERFORM\s+', # PERFORM statement
            r'^\s*CALL\s+',  # CALL statement
            r'^\s*EXIT\s+',  # EXIT statement
            r'^\s*STOP\s+',  # STOP statement
            r'^\s*GO\s+',    # GO statement
            r'^\s*GOTO\s+',  # GOTO statement
            r'^\s*RETURN\s*', # RETURN statement
            r'^\s*--\s*',    # Comment
            r'^\s*$'         # Empty line
        ]
    
    def match_pattern(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Detecta el patrón de STRING en la línea
        Args:
            line: Línea de código COBOL
        Returns:
            Dict con información del patrón encontrado o None
        """
        line_clean = line.strip().upper()
        
        for operation_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.match(pattern, line_clean, re.IGNORECASE)
                if match:
                    return {
                        'operation_type': operation_type,
                        'groups': match.groups(),
                        'pattern': pattern,
                        'raw': line.strip()
                    }
        
        return None
    
    def is_string_start(self, line: str) -> bool:
        """Detecta si la línea es el inicio de un STRING"""
        line_clean = line.strip().upper()
        for pattern in self.string_start_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def is_string_continuation(self, line: str) -> bool:
        """Detecta si la línea es una continuación de STRING"""
        line_clean = line.strip().upper()
        for pattern in self.string_continuation_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def debug_string_continuation(self, line: str) -> Dict[str, Any]:
        """Debug temporal para ver qué está pasando con las continuaciones"""
        line_clean = line.strip().upper()
        debug_info = {
            'original_line': line.strip(),
            'clean_line': line_clean,
            'matches': []
        }
        
        for i, pattern in enumerate(self.string_continuation_patterns):
            match = re.match(pattern, line_clean, re.IGNORECASE)
            if match:
                debug_info['matches'].append({
                    'pattern_index': i,
                    'pattern': pattern,
                    'groups': match.groups()
                })
        
        return debug_info
    
    def is_string_end(self, line: str) -> bool:
        """Detecta si la línea indica el final del STRING"""
        line_clean = line.strip().upper()
        for pattern in self.string_end_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def parse_string_start(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsea el inicio de un STRING"""
        line_clean = line.strip().upper()
        
        # STRING con contenido inicial
        match = re.match(r'^\s*STRING\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'STRING_START',
                'initial_content': match.group(1),
                'raw': line.strip()
            }
        
        # STRING sin contenido inicial
        match = re.match(r'^\s*STRING\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'STRING_START',
                'initial_content': '',
                'raw': line.strip()
            }
        
        return None
    
    def parse_string_continuation(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsea una continuación de STRING"""
        line_clean = line.strip().upper()
        
        # Campo simple (más flexible)
        match = re.match(r'^\s*([A-Z0-9_-]+)\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'STRING_FIELD',
                'field': match.group(1),
                'delimiter': 'SIZE',
                'raw': line.strip()
            }
        
        # DELIMITED BY SIZE
        match = re.match(r'^\s*([A-Z0-9-]+)\s+DELIMITED\s+BY\s+SIZE\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'STRING_FIELD',
                'field': match.group(1),
                'delimiter': 'SIZE',
                'raw': line.strip()
            }
        
        # DELIMITED BY SPACES
        match = re.match(r'^\s*([A-Z0-9-]+)\s+DELIMITED\s+BY\s+SPACES\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'STRING_FIELD',
                'field': match.group(1),
                'delimiter': 'SPACES',
                'raw': line.strip()
            }
        
        # DELIMITED BY literal
        match = re.match(r'^\s*([A-Z0-9-]+)\s+DELIMITED\s+BY\s+\'([^\']+)\'\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'STRING_FIELD',
                'field': match.group(1),
                'delimiter': 'LITERAL',
                'delimiter_value': match.group(2),
                'raw': line.strip()
            }
        
        # DELIMITED BY variable
        match = re.match(r'^\s*([A-Z0-9-]+)\s+DELIMITED\s+BY\s+([A-Z0-9-]+)\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'STRING_FIELD',
                'field': match.group(1),
                'delimiter': 'VARIABLE',
                'delimiter_value': match.group(2),
                'raw': line.strip()
            }
        
        # INTO destination
        match = re.match(r'^\s*INTO\s+([A-Z0-9-]+)\s*\.?\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'STRING_INTO',
                'destination': match.group(1),
                'raw': line.strip()
            }
        
        return None


class StringComponentParser:
    """
    Clase para parsear componentes de STRING
    Implementa Single Responsibility Principle
    """
    
    def parse_components(self, components_text: str) -> List[StringComponent]:
        """
        Parsea los componentes de STRING
        Args:
            components_text: Texto con los componentes
        Returns:
            Lista de StringComponent
        """
        components = []
        
        # Dividir por líneas y procesar cada una
        lines = components_text.split('\n')
        current_delimiter = "SIZE"  # Default
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detectar cambio de delimitador
            if "DELIMITED BY SIZE" in line.upper():
                current_delimiter = "SIZE"
                # Extraer el campo antes del DELIMITED BY
                field_match = re.match(r'^\s*([A-Z0-9-]+)\s+DELIMITED\s+BY\s+SIZE', line, re.IGNORECASE)
                if field_match:
                    components.append(StringComponent(field_match.group(1), "SIZE"))
            elif "DELIMITED BY SPACES" in line.upper():
                current_delimiter = "SPACES"
                field_match = re.match(r'^\s*([A-Z0-9-]+)\s+DELIMITED\s+BY\s+SPACES', line, re.IGNORECASE)
                if field_match:
                    components.append(StringComponent(field_match.group(1), "SPACES"))
            elif "DELIMITED BY" in line.upper():
                # Delimitador literal o variable
                literal_match = re.match(r'^\s*([A-Z0-9-]+)\s+DELIMITED\s+BY\s+\'([^\']+)\'', line, re.IGNORECASE)
                if literal_match:
                    components.append(StringComponent(literal_match.group(1), "LITERAL", literal_match.group(2)))
                else:
                    variable_match = re.match(r'^\s*([A-Z0-9-]+)\s+DELIMITED\s+BY\s+([A-Z0-9-]+)', line, re.IGNORECASE)
                    if variable_match:
                        components.append(StringComponent(variable_match.group(1), "VARIABLE", variable_match.group(2)))
            else:
                # Campo simple sin delimitador explícito
                field_match = re.match(r'^\s*([A-Z0-9-]+)', line, re.IGNORECASE)
                if field_match:
                    components.append(StringComponent(field_match.group(1), current_delimiter))
        
        return components


class StringConverter:
    """
    Clase para convertir operaciones STRING a PL/SQL
    Implementa Single Responsibility Principle
    """
    
    def __init__(self):
        self.component_parser = StringComponentParser()
    
    def convert_string_operation(self, operation_info: Dict[str, Any], base_indent: str) -> str:
        """
        Convierte una operación STRING a PL/SQL
        Args:
            operation_info: Información de la operación parseada
            base_indent: Indentación base
        Returns:
            str: Código PL/SQL equivalente
        """
        operation_type = operation_info.get('operation_type')
        groups = operation_info.get('groups', [])
        raw = operation_info.get('raw', '')
        
        if not groups:
            return f"{base_indent}-- GAP: {raw}"
        
        if operation_type == StringOperationType.BASIC_STRING:
            return self._convert_basic_string(groups[0], groups[1], base_indent)
        
        elif operation_type == StringOperationType.STRING_WITH_DELIMITED_BY_SIZE:
            return self._convert_string_with_delimited_by_size(groups[0], groups[1], base_indent)
        
        elif operation_type == StringOperationType.STRING_WITH_DELIMITED_BY_SPACES:
            return self._convert_string_with_delimited_by_spaces(groups[0], groups[1], base_indent)
        
        elif operation_type == StringOperationType.STRING_WITH_DELIMITED_BY_LITERAL:
            return self._convert_string_with_delimited_by_literal(groups[0], groups[1], groups[2], base_indent)
        
        elif operation_type == StringOperationType.STRING_WITH_DELIMITED_BY_VARIABLE:
            return self._convert_string_with_delimited_by_variable(groups[0], groups[1], groups[2], base_indent)
        
        else:
            return f"{base_indent}-- GAP: {raw}"
    
    def _convert_basic_string(self, components_text: str, destination: str, base_indent: str) -> str:
        """Convierte STRING básico"""
        components = self.component_parser.parse_components(components_text)
        if not components:
            return f"{base_indent}-- GAP: STRING {components_text} INTO {destination}"
        
        clean_destination = destination.replace('-', '_').lower()
        plsql_components = [comp.to_plsql() for comp in components]
        concatenation = ' || '.join(plsql_components)
        
        return f"{base_indent}{clean_destination} := {concatenation}; -- STRING operation"
    
    def _convert_string_with_delimited_by_size(self, components_text: str, destination: str, base_indent: str) -> str:
        """Convierte STRING con DELIMITED BY SIZE"""
        components = self.component_parser.parse_components(components_text)
        if not components:
            return f"{base_indent}-- GAP: STRING {components_text} DELIMITED BY SIZE INTO {destination}"
        
        clean_destination = destination.replace('-', '_').lower()
        plsql_components = [comp.to_plsql() for comp in components]
        concatenation = ' || '.join(plsql_components)
        
        return f"{base_indent}{clean_destination} := {concatenation}; -- STRING DELIMITED BY SIZE"
    
    def _convert_string_with_delimited_by_spaces(self, components_text: str, destination: str, base_indent: str) -> str:
        """Convierte STRING con DELIMITED BY SPACES"""
        components = self.component_parser.parse_components(components_text)
        if not components:
            return f"{base_indent}-- GAP: STRING {components_text} DELIMITED BY SPACES INTO {destination}"
        
        clean_destination = destination.replace('-', '_').lower()
        plsql_components = [comp.to_plsql() for comp in components]
        concatenation = ' || '.join(plsql_components)
        
        return f"{base_indent}{clean_destination} := {concatenation}; -- STRING DELIMITED BY SPACES"
    
    def _convert_string_with_delimited_by_literal(self, components_text: str, literal: str, destination: str, base_indent: str) -> str:
        """Convierte STRING con DELIMITED BY literal"""
        components = self.component_parser.parse_components(components_text)
        if not components:
            return f"{base_indent}-- GAP: STRING {components_text} DELIMITED BY '{literal}' INTO {destination}"
        
        clean_destination = destination.replace('-', '_').lower()
        plsql_components = [comp.to_plsql() for comp in components]
        concatenation = ' || '.join(plsql_components)
        
        return f"{base_indent}{clean_destination} := {concatenation}; -- STRING DELIMITED BY '{literal}'"
    
    def _convert_string_with_delimited_by_variable(self, components_text: str, delimiter_var: str, destination: str, base_indent: str) -> str:
        """Convierte STRING con DELIMITED BY variable"""
        components = self.component_parser.parse_components(components_text)
        if not components:
            return f"{base_indent}-- GAP: STRING {components_text} DELIMITED BY {delimiter_var} INTO {destination}"
        
        clean_destination = destination.replace('-', '_').lower()
        plsql_components = [comp.to_plsql() for comp in components]
        concatenation = ' || '.join(plsql_components)
        
        return f"{base_indent}{clean_destination} := {concatenation}; -- STRING DELIMITED BY {delimiter_var}"


class CobolStringHandler:
    """
    Handler principal para operaciones STRING de COBOL
    Implementa principios SOLID:
    - SRP: Solo maneja operaciones STRING
    - OCP: Abierto para extensión, cerrado para modificación
    - LSP: Intercambiable con otros handlers
    - ISP: Interfaz específica para STRING
    - DIP: Depende de abstracciones (matcher y converter)
    """
    
    def __init__(self):
        self.pattern_matcher = StringPatternMatcher()
        self.converter = StringConverter()
        self.string_context = None  # Para manejar STRING multi-línea
    
    def can_handle(self, line: str) -> bool:
        """
        Verifica si la línea puede ser manejada por este handler
        Args:
            line: Línea de código COBOL
        Returns:
            bool: True si puede manejar la línea
        """
        return (self.pattern_matcher.match_pattern(line) is not None or
                self.pattern_matcher.is_string_start(line) or
                self.pattern_matcher.is_string_continuation(line))
    
    def is_string_context_active(self) -> bool:
        """Verifica si hay un contexto de STRING activo"""
        return self.string_context is not None
    
    def start_string_context(self, line: str) -> Optional[Dict[str, Any]]:
        """Inicia un contexto de STRING"""
        start_info = self.pattern_matcher.parse_string_start(line)
        if start_info:
            self.string_context = {
                'initial_content': start_info.get('initial_content', ''),
                'fields': [],
                'destination': None,
                'raw_lines': [line.strip()]
            }
            return {
                'op': 'STRING_CONTEXT_START',
                'context': self.string_context,
                'raw': line.strip()
            }
        return None
    
    def add_to_string_context(self, line: str) -> Optional[Dict[str, Any]]:
        """Agrega una línea al contexto de STRING"""
        if not self.string_context:
            return None
        
        continuation_info = self.pattern_matcher.parse_string_continuation(line)
        if continuation_info:
            self.string_context['raw_lines'].append(line.strip())
            
            if continuation_info['type'] == 'STRING_FIELD':
                self.string_context['fields'].append({
                    'field': continuation_info['field'],
                    'delimiter': continuation_info['delimiter'],
                    'delimiter_value': continuation_info.get('delimiter_value')
                })
                return {
                    'op': 'STRING_CONTEXT_FIELD',
                    'field_info': continuation_info,
                    'raw': line.strip()
                }
            elif continuation_info['type'] == 'STRING_INTO':
                self.string_context['destination'] = continuation_info['destination']
                # Cuando encontramos INTO, completar el STRING inmediatamente
                return self.complete_string_context()
        
        return None
    
    def complete_string_context(self) -> Optional[Dict[str, Any]]:
        """Completa el contexto de STRING y retorna la operación completa"""
        if not self.string_context:
            return None
        
        context = self.string_context.copy()
        self.string_context = None  # Limpiar contexto
        
        return {
            'op': 'STRING',
            'operation_type': 'MULTI_LINE_STRING',
            'context': context,
            'raw': ' | '.join(context['raw_lines'])
        }
    
    def parse_string_operation(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parsea una línea de STRING
        Args:
            line: Línea de código COBOL
        Returns:
            Dict con información del STRING o None si no es válido
        """
        # Si hay contexto activo, verificar si esta línea es una continuación
        if self.string_context:
            if self.pattern_matcher.is_string_continuation(line):
                return self.add_to_string_context(line)
            elif self.pattern_matcher.is_string_end(line):
                # Es el final del STRING, completarlo
                return self.complete_string_context()
            else:
                # Verificar si es una línea que debería ser parte del STRING
                if self._is_string_related_line(line):
                    # Es una línea relacionada con STRING, procesarla
                    return self.add_to_string_context(line)
                else:
                    # No es continuación ni final, completar el STRING
                    return self.complete_string_context()
    
    def _is_string_related_line(self, line: str) -> bool:
        """Verifica si una línea está relacionada con STRING"""
        line_clean = line.strip().upper()
        
        # Patrones que indican que la línea es parte del STRING
        string_related_patterns = [
            r'^\s*DELIMITED\s+BY\s+SIZE\s*$',
            r'^\s*DELIMITED\s+BY\s+SPACES\s*$',
            r'^\s*DELIMITED\s+BY\s+\'[^\']+\'\s*$',
            r'^\s*DELIMITED\s+BY\s+[A-Z0-9-]+\s*$',
            r'^\s*INTO\s+[A-Z0-9-]+\s*\.?\s*$'
        ]
        
        for pattern in string_related_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        
        return False
        
        # Intentar parsear como STRING completo en una línea
        pattern_result = self.pattern_matcher.match_pattern(line)
        if pattern_result:
            return {
                'op': 'STRING',
                'operation_type': pattern_result['operation_type'],
                'groups': pattern_result['groups'],
                'raw': pattern_result['raw']
            }
        
        # Intentar iniciar un contexto de STRING
        if self.pattern_matcher.is_string_start(line):
            return self.start_string_context(line)
        
        return None
    
    def convert_string_operation(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """
        Convierte STRING a PL/SQL
        Args:
            stmt: Declaración parseada de STRING
            base_indent: Indentación base
        Returns:
            str: Código PL/SQL equivalente
        """
        op = stmt.get('op', '')
        
        if op == 'STRING_CONTEXT_START':
            return f"{base_indent}-- STRING context started"
        
        elif op == 'STRING_CONTEXT_FIELD':
            return f"{base_indent}-- STRING field: {stmt.get('field_info', {}).get('field', '')}"
        
        elif op == 'STRING_CONTEXT_INTO':
            return f"{base_indent}-- STRING destination: {stmt.get('destination', '')}"
        
        elif op == 'STRING' and stmt.get('operation_type') == 'MULTI_LINE_STRING':
            return self._convert_multi_line_string(stmt, base_indent)
        
        else:
            return self.converter.convert_string_operation(stmt, base_indent)
    
    def _convert_multi_line_string(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """Convierte STRING multi-línea a PL/SQL"""
        context = stmt.get('context', {})
        destination = context.get('destination')
        
        # Debug temporal
        if not destination:
            return f"{base_indent}-- GAP: STRING without destination (context: {context})"
        
        clean_destination = destination.replace('-', '_').lower()
        
        # Construir la concatenación
        parts = []
        
        # Contenido inicial
        initial_content = context.get('initial_content', '').strip()
        if initial_content:
            # Limpiar comillas si las tiene
            if initial_content.startswith("'") and initial_content.endswith("'"):
                initial_content = initial_content[1:-1]
            parts.append(f"'{initial_content}'")
        
        # Campos
        for field_info in context.get('fields', []):
            field = field_info['field']
            delimiter = field_info['delimiter']
            delimiter_value = field_info.get('delimiter_value')
            
            clean_field = field.replace('-', '_').lower()
            
            if delimiter == 'SIZE':
                parts.append(f"NVL({clean_field}, '')")
            elif delimiter == 'SPACES':
                parts.append(f"RTRIM(NVL({clean_field}, ''))")
            elif delimiter == 'LITERAL':
                parts.append(f"SUBSTR(NVL({clean_field}, ''), 1, INSTR(NVL({clean_field}, ''), '{delimiter_value}') - 1)")
            elif delimiter == 'VARIABLE':
                clean_delimiter = delimiter_value.replace('-', '_').lower()
                parts.append(f"SUBSTR(NVL({clean_field}, ''), 1, INSTR(NVL({clean_field}, ''), {clean_delimiter}) - 1)")
            else:
                parts.append(f"NVL({clean_field}, '')")
        
        if not parts:
            return f"{base_indent}-- GAP: STRING without components"
        
        concatenation = ' || '.join(parts)
        return f"{base_indent}{clean_destination} := {concatenation}; -- STRING operation"


class StringHandlerFactory:
    """
    Factory para crear handlers de STRING
    Implementa el patrón Factory con principios SOLID
    """
    
    @staticmethod
    def create_standard_handler() -> CobolStringHandler:
        """
        Crea un handler estándar de STRING
        Returns:
            CobolStringHandler: Handler configurado
        """
        return CobolStringHandler()
    
    @staticmethod
    def create_custom_handler(custom_patterns: Dict[str, List[str]]) -> CobolStringHandler:
        """
        Crea un handler personalizado de STRING
        Args:
            custom_patterns: Patrones personalizados
        Returns:
            CobolStringHandler: Handler con patrones personalizados
        """
        handler = CobolStringHandler()
        handler.pattern_matcher.patterns.update(custom_patterns)
        return handler
