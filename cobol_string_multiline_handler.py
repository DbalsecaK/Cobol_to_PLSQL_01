"""
COBOL STRING Multi-line Handler - Implementación especializada con principios SOLID
Maneja específicamente STRING multi-línea que no se pueden procesar en una sola línea
"""

from typing import Optional, Dict, Any, List
import re


class StringMultilineContext:
    """
    Clase para manejar el contexto de STRING multi-línea
    Implementa Single Responsibility Principle
    """
    
    def __init__(self):
        self.is_active = False
        self.initial_content = ""
        self.fields = []
        self.destination = None
        self.raw_lines = []
    
    def start(self, initial_content: str, raw_line: str):
        """Inicia el contexto de STRING"""
        self.is_active = True
        self.initial_content = initial_content
        self.fields = []
        self.destination = None
        self.raw_lines = [raw_line]
    
    def add_field(self, field: str, delimiter: str, delimiter_value: str = None):
        """Agrega un campo al contexto"""
        self.fields.append({
            'field': field,
            'delimiter': delimiter,
            'delimiter_value': delimiter_value
        })
    
    def set_destination(self, destination: str):
        """Establece el destino del STRING"""
        self.destination = destination
    
    def add_raw_line(self, line: str):
        """Agrega una línea raw al contexto"""
        self.raw_lines.append(line)
    
    def complete(self) -> Dict[str, Any]:
        """Completa el contexto y retorna la operación"""
        context = {
            'initial_content': self.initial_content,
            'fields': self.fields.copy(),
            'destination': self.destination,
            'raw_lines': self.raw_lines.copy()
        }
        self.reset()
        return context
    
    def reset(self):
        """Resetea el contexto"""
        self.is_active = False
        self.initial_content = ""
        self.fields = []
        self.destination = None
        self.raw_lines = []


class StringMultilineDetector:
    """
    Clase para detectar patrones de STRING multi-línea
    Implementa Single Responsibility Principle
    """
    
    def __init__(self):
        self.start_patterns = [
            r'^\s*STRING\s+(.+?)$',
            r'^\s*STRING\s*$'
        ]
        
        self.field_patterns = [
            r'^\s*([A-Z0-9_-]+)\s*$',  # Campo simple
            r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+SIZE\s*$',
            r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+SPACES\s*$',
            r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+\'([^\']+)\'\s*$',
            r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+([A-Z0-9_-]+)\s*$'
        ]
        
        self.destination_patterns = [
            r'^\s*INTO\s+([A-Z0-9_-]+)\s*\.?\s*$'
        ]
        
        self.end_patterns = [
            r'^\s*MOVE\s+',
            r'^\s*IF\s+',
            r'^\s*WHEN\s+',
            r'^\s*ELSE\s*$',
            r'^\s*END\s+',
            r'^\s*PERFORM\s+',
            r'^\s*CALL\s+',
            r'^\s*EXIT\s+',
            r'^\s*STOP\s+',
            r'^\s*GO\s+',
            r'^\s*GOTO\s+',
            r'^\s*RETURN\s*',
            r'^\s*--\s*',
            r'^\s*$'
        ]
    
    def is_string_start(self, line: str) -> bool:
        """Detecta si la línea es el inicio de un STRING"""
        line_clean = line.strip().upper()
        for pattern in self.start_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def is_string_field(self, line: str) -> bool:
        """Detecta si la línea es un campo de STRING"""
        line_clean = line.strip().upper()
        for pattern in self.field_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def is_string_destination(self, line: str) -> bool:
        """Detecta si la línea es el destino de STRING"""
        line_clean = line.strip().upper()
        for pattern in self.destination_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def is_string_end(self, line: str) -> bool:
        """Detecta si la línea indica el final del STRING"""
        line_clean = line.strip().upper()
        for pattern in self.end_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def parse_string_start(self, line: str) -> Optional[str]:
        """Parsea el inicio de un STRING"""
        line_clean = line.strip().upper()
        
        # STRING con contenido inicial
        match = re.match(r'^\s*STRING\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # STRING sin contenido inicial
        match = re.match(r'^\s*STRING\s*$', line_clean, re.IGNORECASE)
        if match:
            return ""
        
        return None
    
    def parse_string_field(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsea un campo de STRING"""
        line_clean = line.strip().upper()
        
        # Campo simple
        match = re.match(r'^\s*([A-Z0-9_-]+)\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'field': match.group(1),
                'delimiter': 'SIZE',
                'delimiter_value': None
            }
        
        # DELIMITED BY SIZE
        match = re.match(r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+SIZE\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'field': match.group(1),
                'delimiter': 'SIZE',
                'delimiter_value': None
            }
        
        # DELIMITED BY SPACES
        match = re.match(r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+SPACES\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'field': match.group(1),
                'delimiter': 'SPACES',
                'delimiter_value': None
            }
        
        # DELIMITED BY literal
        match = re.match(r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+\'([^\']+)\'\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'field': match.group(1),
                'delimiter': 'LITERAL',
                'delimiter_value': match.group(2)
            }
        
        # DELIMITED BY variable
        match = re.match(r'^\s*([A-Z0-9_-]+)\s+DELIMITED\s+BY\s+([A-Z0-9_-]+)\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'field': match.group(1),
                'delimiter': 'VARIABLE',
                'delimiter_value': match.group(2)
            }
        
        return None
    
    def parse_string_destination(self, line: str) -> Optional[str]:
        """Parsea el destino de STRING"""
        line_clean = line.strip().upper()
        
        match = re.match(r'^\s*INTO\s+([A-Z0-9_-]+)\s*\.?\s*$', line_clean, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None


class StringMultilineConverter:
    """
    Clase para convertir STRING multi-línea a PL/SQL
    Implementa Single Responsibility Principle
    """
    
    def convert_multiline_string(self, context: Dict[str, Any], base_indent: str) -> str:
        """Convierte STRING multi-línea a PL/SQL"""
        destination = context.get('destination')
        
        if not destination:
            return f"{base_indent}-- GAP: STRING without destination"
        
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
        fields = context.get('fields', [])
        
        for field_info in fields:
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


class CobolStringMultilineHandler:
    """
    Handler principal para STRING multi-línea de COBOL
    Implementa principios SOLID:
    - SRP: Solo maneja STRING multi-línea
    - OCP: Abierto para extensión, cerrado para modificación
    - LSP: Intercambiable con otros handlers
    - ISP: Interfaz específica para STRING multi-línea
    - DIP: Depende de abstracciones (detector, converter, context)
    """
    
    def __init__(self):
        self.context = StringMultilineContext()
        self.detector = StringMultilineDetector()
        self.converter = StringMultilineConverter()
    
    def can_handle(self, line: str) -> bool:
        """Verifica si puede manejar la línea"""
        return (self.context.is_active or 
                self.detector.is_string_start(line) or
                self.detector.is_string_field(line) or
                self.detector.is_string_destination(line) or
                self._is_string_related_line(line))
    
    def is_context_active(self) -> bool:
        """Verifica si hay contexto activo"""
        return self.context.is_active
    
    def parse_string_operation(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsea una línea de STRING multi-línea"""
        if self.context.is_active:
            return self._process_continuation(line)
        else:
            return self._process_start(line)
    
    def _process_start(self, line: str) -> Optional[Dict[str, Any]]:
        """Procesa el inicio de un STRING"""
        if self.detector.is_string_start(line):
            initial_content = self.detector.parse_string_start(line)
            if initial_content is not None:
                self.context.start(initial_content, line.strip())
                return {
                    'op': 'STRING_MULTILINE_START',
                    'raw': line.strip()
                }
        return None
    
    def _process_continuation(self, line: str) -> Optional[Dict[str, Any]]:
        """Procesa una continuación de STRING"""
        self.context.add_raw_line(line.strip())
        
        if self.detector.is_string_field(line):
            field_info = self.detector.parse_string_field(line)
            if field_info:
                self.context.add_field(
                    field_info['field'],
                    field_info['delimiter'],
                    field_info.get('delimiter_value')
                )
                return {
                    'op': 'STRING_MULTILINE_FIELD',
                    'field_info': field_info,
                    'raw': line.strip()
                }
        
        elif self.detector.is_string_destination(line):
            destination = self.detector.parse_string_destination(line)
            if destination:
                self.context.set_destination(destination)
                # Completar el STRING cuando encontramos el destino
                context = self.context.complete()
                return {
                    'op': 'STRING',
                    'operation_type': 'MULTI_LINE_STRING',
                    'context': context,
                    'raw': ' | '.join(context['raw_lines'])
                }
        
        elif self.detector.is_string_end(line):
            # Completar el STRING cuando encontramos el final
            context = self.context.complete()
            return {
                'op': 'STRING',
                'operation_type': 'MULTI_LINE_STRING',
                'context': context,
                'raw': ' | '.join(context['raw_lines'])
            }
        
        # Verificar si es una línea que debería ser parte del STRING
        elif self._is_string_related_line(line):
            # Es una línea relacionada con STRING, procesarla
            return self._process_string_related_line(line)
        
        return None
    
    def _is_string_related_line(self, line: str) -> bool:
        """Verifica si una línea está relacionada con STRING"""
        line_clean = line.strip().upper()
        
        # DELIMITED BY SIZE en línea separada
        if re.match(r'^\s*DELIMITED\s+BY\s+SIZE\s*$', line_clean, re.IGNORECASE):
            return True
        
        # DELIMITED BY SPACES en línea separada
        if re.match(r'^\s*DELIMITED\s+BY\s+SPACES\s*$', line_clean, re.IGNORECASE):
            return True
        
        # DELIMITED BY literal en línea separada
        if re.match(r'^\s*DELIMITED\s+BY\s+\'([^\']+)\'\s*$', line_clean, re.IGNORECASE):
            return True
        
        # DELIMITED BY variable en línea separada
        if re.match(r'^\s*DELIMITED\s+BY\s+([A-Z0-9_-]+)\s*$', line_clean, re.IGNORECASE):
            return True
        
        return False
    
    def _process_string_related_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Procesa una línea relacionada con STRING"""
        line_clean = line.strip().upper()
        
        # DELIMITED BY SIZE en línea separada
        match = re.match(r'^\s*DELIMITED\s+BY\s+SIZE\s*$', line_clean, re.IGNORECASE)
        if match:
            # Actualizar el último campo agregado con DELIMITED BY SIZE
            if self.context.fields:
                last_field = self.context.fields[-1]
                last_field['delimiter'] = 'SIZE'
                last_field['delimiter_value'] = None
            return {
                'op': 'STRING_MULTILINE_DELIMITER',
                'delimiter': 'SIZE',
                'raw': line.strip()
            }
        
        # DELIMITED BY SPACES en línea separada
        match = re.match(r'^\s*DELIMITED\s+BY\s+SPACES\s*$', line_clean, re.IGNORECASE)
        if match:
            # Actualizar el último campo agregado con DELIMITED BY SPACES
            if self.context.fields:
                last_field = self.context.fields[-1]
                last_field['delimiter'] = 'SPACES'
                last_field['delimiter_value'] = None
            return {
                'op': 'STRING_MULTILINE_DELIMITER',
                'delimiter': 'SPACES',
                'raw': line.strip()
            }
        
        # DELIMITED BY literal en línea separada
        match = re.match(r'^\s*DELIMITED\s+BY\s+\'([^\']+)\'\s*$', line_clean, re.IGNORECASE)
        if match:
            # Actualizar el último campo agregado con DELIMITED BY literal
            if self.context.fields:
                last_field = self.context.fields[-1]
                last_field['delimiter'] = 'LITERAL'
                last_field['delimiter_value'] = match.group(1)
            return {
                'op': 'STRING_MULTILINE_DELIMITER',
                'delimiter': 'LITERAL',
                'delimiter_value': match.group(1),
                'raw': line.strip()
            }
        
        # DELIMITED BY variable en línea separada
        match = re.match(r'^\s*DELIMITED\s+BY\s+([A-Z0-9_-]+)\s*$', line_clean, re.IGNORECASE)
        if match:
            # Actualizar el último campo agregado con DELIMITED BY variable
            if self.context.fields:
                last_field = self.context.fields[-1]
                last_field['delimiter'] = 'VARIABLE'
                last_field['delimiter_value'] = match.group(1)
            return {
                'op': 'STRING_MULTILINE_DELIMITER',
                'delimiter': 'VARIABLE',
                'delimiter_value': match.group(1),
                'raw': line.strip()
            }
        
        return None
    
    def convert_string_operation(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """Convierte STRING multi-línea a PL/SQL"""
        op = stmt.get('op', '')
        
        if op == 'STRING_MULTILINE_START':
            return f"{base_indent}-- STRING multi-line started"
        
        elif op == 'STRING_MULTILINE_FIELD':
            return f"{base_indent}-- STRING field: {stmt.get('field_info', {}).get('field', '')}"
        
        elif op == 'STRING_MULTILINE_DELIMITER':
            return f"{base_indent}-- STRING delimiter: {stmt.get('delimiter', '')}"
        
        elif op == 'STRING' and stmt.get('operation_type') == 'MULTI_LINE_STRING':
            return self.converter.convert_multiline_string(stmt.get('context', {}), base_indent)
        
        else:
            return f"{base_indent}-- GAP: Unknown STRING operation"


class StringMultilineHandlerFactory:
    """
    Factory para crear handlers de STRING multi-línea
    Implementa el patrón Factory con principios SOLID
    """
    
    @staticmethod
    def create_standard_handler() -> CobolStringMultilineHandler:
        """Crea un handler estándar de STRING multi-línea"""
        return CobolStringMultilineHandler()
    
    @staticmethod
    def create_custom_handler(custom_patterns: Dict[str, List[str]]) -> CobolStringMultilineHandler:
        """Crea un handler personalizado de STRING multi-línea"""
        handler = CobolStringMultilineHandler()
        # Aquí se podrían agregar patrones personalizados
        return handler
