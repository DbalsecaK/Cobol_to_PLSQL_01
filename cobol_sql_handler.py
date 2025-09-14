"""
COBOL SQL Handler - Implementación especializada con principios SOLID
Maneja comandos SQL embebidos en COBOL (EXEC SQL ... END-EXEC)
"""

from typing import Optional, Dict, Any, List
import re


class SqlCommandType:
    """
    Enum para tipos de comandos SQL
    Implementa Single Responsibility Principle
    """
    ROLLBACK = "ROLLBACK"
    COMMIT = "COMMIT"
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    DECLARE = "DECLARE"
    OPEN = "OPEN"
    FETCH = "FETCH"
    CLOSE = "CLOSE"
    UNKNOWN = "UNKNOWN"


class SqlPatternMatcher:
    """
    Clase para detectar patrones de comandos SQL embebidos
    Implementa Single Responsibility Principle
    """
    
    def __init__(self):
        # Patrones para detectar bloques SQL
        self.sql_block_patterns = [
            r'^\s*EXEC\s+SQL\s*$',
            r'^\s*EXEC\s+SQL\s+(.+?)$'
        ]
        
        # Patrones para detectar comandos SQL específicos
        self.sql_command_patterns = {
            SqlCommandType.ROLLBACK: [
                r'^\s*ROLLBACK\s*$',
                r'^\s*ROLLBACK\s+TO\s+SAVEPOINT\s+([A-Z0-9_-]+)\s*$'
            ],
            SqlCommandType.COMMIT: [
                r'^\s*COMMIT\s*$',
                r'^\s*COMMIT\s+WORK\s*$'
            ],
            SqlCommandType.SELECT: [
                r'^\s*SELECT\s+(.+?)$'
            ],
            SqlCommandType.INSERT: [
                r'^\s*INSERT\s+(.+?)$'
            ],
            SqlCommandType.UPDATE: [
                r'^\s*UPDATE\s+(.+?)$'
            ],
            SqlCommandType.DELETE: [
                r'^\s*DELETE\s+(.+?)$'
            ],
            SqlCommandType.DECLARE: [
                r'^\s*DECLARE\s+(.+?)$'
            ],
            SqlCommandType.OPEN: [
                r'^\s*OPEN\s+([A-Z0-9_-]+)\s*$'
            ],
            SqlCommandType.FETCH: [
                r'^\s*FETCH\s+(.+?)$'
            ],
            SqlCommandType.CLOSE: [
                r'^\s*CLOSE\s+([A-Z0-9_-]+)\s*$'
            ]
        }
        
        # Patrones para detectar el final del bloque SQL
        self.sql_end_patterns = [
            r'^\s*END-EXEC\s*\.?\s*$'
        ]
    
    def is_sql_block_start(self, line: str) -> bool:
        """Detecta si la línea es el inicio de un bloque SQL"""
        line_clean = line.strip().upper()
        for pattern in self.sql_block_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def is_sql_command(self, line: str) -> bool:
        """Detecta si la línea es un comando SQL"""
        line_clean = line.strip().upper()
        for command_type, patterns in self.sql_command_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line_clean, re.IGNORECASE):
                    return True
        return False
    
    def is_sql_block_end(self, line: str) -> bool:
        """Detecta si la línea es el final de un bloque SQL"""
        line_clean = line.strip().upper()
        for pattern in self.sql_end_patterns:
            if re.match(pattern, line_clean, re.IGNORECASE):
                return True
        return False
    
    def parse_sql_block_start(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsea el inicio de un bloque SQL"""
        line_clean = line.strip().upper()
        
        # EXEC SQL sin comando
        match = re.match(r'^\s*EXEC\s+SQL\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_BLOCK_START',
                'command': None,
                'raw': line.strip()
            }
        
        # EXEC SQL con comando
        match = re.match(r'^\s*EXEC\s+SQL\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_BLOCK_START',
                'command': match.group(1).strip(),
                'raw': line.strip()
            }
        
        return None
    
    def parse_sql_command(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsea un comando SQL"""
        line_clean = line.strip().upper()
        
        # ROLLBACK simple
        match = re.match(r'^\s*ROLLBACK\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.ROLLBACK,
                'command': 'ROLLBACK',
                'parameters': None,
                'raw': line.strip()
            }
        
        # ROLLBACK TO SAVEPOINT
        match = re.match(r'^\s*ROLLBACK\s+TO\s+SAVEPOINT\s+([A-Z0-9_-]+)\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.ROLLBACK,
                'command': 'ROLLBACK TO SAVEPOINT',
                'parameters': match.group(1),
                'raw': line.strip()
            }
        
        # COMMIT
        match = re.match(r'^\s*COMMIT\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.COMMIT,
                'command': 'COMMIT',
                'parameters': None,
                'raw': line.strip()
            }
        
        # COMMIT WORK
        match = re.match(r'^\s*COMMIT\s+WORK\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.COMMIT,
                'command': 'COMMIT WORK',
                'parameters': None,
                'raw': line.strip()
            }
        
        # SELECT
        match = re.match(r'^\s*SELECT\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.SELECT,
                'command': 'SELECT',
                'parameters': match.group(1).strip(),
                'raw': line.strip()
            }
        
        # INSERT
        match = re.match(r'^\s*INSERT\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.INSERT,
                'command': 'INSERT',
                'parameters': match.group(1).strip(),
                'raw': line.strip()
            }
        
        # UPDATE
        match = re.match(r'^\s*UPDATE\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.UPDATE,
                'command': 'UPDATE',
                'parameters': match.group(1).strip(),
                'raw': line.strip()
            }
        
        # DELETE
        match = re.match(r'^\s*DELETE\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.DELETE,
                'command': 'DELETE',
                'parameters': match.group(1).strip(),
                'raw': line.strip()
            }
        
        # DECLARE
        match = re.match(r'^\s*DECLARE\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.DECLARE,
                'command': 'DECLARE',
                'parameters': match.group(1).strip(),
                'raw': line.strip()
            }
        
        # OPEN
        match = re.match(r'^\s*OPEN\s+([A-Z0-9_-]+)\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.OPEN,
                'command': 'OPEN',
                'parameters': match.group(1),
                'raw': line.strip()
            }
        
        # FETCH
        match = re.match(r'^\s*FETCH\s+(.+?)$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.FETCH,
                'command': 'FETCH',
                'parameters': match.group(1).strip(),
                'raw': line.strip()
            }
        
        # CLOSE
        match = re.match(r'^\s*CLOSE\s+([A-Z0-9_-]+)\s*$', line_clean, re.IGNORECASE)
        if match:
            return {
                'type': 'SQL_COMMAND',
                'command_type': SqlCommandType.CLOSE,
                'command': 'CLOSE',
                'parameters': match.group(1),
                'raw': line.strip()
            }
        
        return None


class SqlConverter:
    """
    Clase para convertir comandos SQL embebidos a PL/SQL
    Implementa Single Responsibility Principle
    """
    
    def convert_sql_command(self, command_info: Dict[str, Any], base_indent: str) -> str:
        """Convierte un comando SQL a PL/SQL"""
        command_type = command_info.get('command_type')
        command = command_info.get('command')
        parameters = command_info.get('parameters')
        
        if command_type == SqlCommandType.ROLLBACK:
            if parameters:
                return f"{base_indent}ROLLBACK TO SAVEPOINT {parameters};"
            else:
                return f"{base_indent}ROLLBACK;"
        
        elif command_type == SqlCommandType.COMMIT:
            return f"{base_indent}COMMIT;"
        
        elif command_type == SqlCommandType.SELECT:
            return f"{base_indent}-- SELECT: {parameters}"
        
        elif command_type == SqlCommandType.INSERT:
            return f"{base_indent}-- INSERT: {parameters}"
        
        elif command_type == SqlCommandType.UPDATE:
            return f"{base_indent}-- UPDATE: {parameters}"
        
        elif command_type == SqlCommandType.DELETE:
            return f"{base_indent}-- DELETE: {parameters}"
        
        elif command_type == SqlCommandType.DECLARE:
            return f"{base_indent}-- DECLARE: {parameters}"
        
        elif command_type == SqlCommandType.OPEN:
            return f"{base_indent}OPEN {parameters};"
        
        elif command_type == SqlCommandType.FETCH:
            return f"{base_indent}-- FETCH: {parameters}"
        
        elif command_type == SqlCommandType.CLOSE:
            return f"{base_indent}CLOSE {parameters};"
        
        else:
            return f"{base_indent}-- GAP: Unknown SQL command: {command}"


class CobolSqlHandler:
    """
    Handler principal para comandos SQL embebidos de COBOL
    Implementa principios SOLID:
    - SRP: Solo maneja comandos SQL embebidos
    - OCP: Abierto para extensión, cerrado para modificación
    - LSP: Intercambiable con otros handlers
    - ISP: Interfaz específica para SQL embebido
    - DIP: Depende de abstracciones (detector, converter)
    """
    
    def __init__(self):
        self.pattern_matcher = SqlPatternMatcher()
        self.converter = SqlConverter()
        self.sql_context = None
    
    def can_handle(self, line: str) -> bool:
        """Verifica si puede manejar la línea"""
        return (self.pattern_matcher.is_sql_block_start(line) or
                self.pattern_matcher.is_sql_command(line) or
                self.pattern_matcher.is_sql_block_end(line) or
                self.sql_context is not None)
    
    def is_sql_context_active(self) -> bool:
        """Verifica si hay contexto SQL activo"""
        return self.sql_context is not None
    
    def parse_sql_operation(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsea una línea de comando SQL embebido"""
        if self.sql_context:
            return self._process_sql_continuation(line)
        else:
            return self._process_sql_start(line)
    
    def _process_sql_start(self, line: str) -> Optional[Dict[str, Any]]:
        """Procesa el inicio de un bloque SQL"""
        if self.pattern_matcher.is_sql_block_start(line):
            block_info = self.pattern_matcher.parse_sql_block_start(line)
            if block_info:
                self.sql_context = {
                    'commands': [],
                    'raw_lines': [line.strip()]
                }
                
                # Si hay comando en la misma línea
                if block_info.get('command'):
                    command_info = self.pattern_matcher.parse_sql_command(block_info['command'])
                    if command_info:
                        self.sql_context['commands'].append(command_info)
                
                return {
                    'op': 'SQL_BLOCK_START',
                    'raw': line.strip()
                }
        return None
    
    def _process_sql_continuation(self, line: str) -> Optional[Dict[str, Any]]:
        """Procesa una continuación de bloque SQL"""
        self.sql_context['raw_lines'].append(line.strip())
        
        if self.pattern_matcher.is_sql_command(line):
            command_info = self.pattern_matcher.parse_sql_command(line)
            if command_info:
                self.sql_context['commands'].append(command_info)
                return {
                    'op': 'SQL_COMMAND',
                    'command_info': command_info,
                    'raw': line.strip()
                }
        
        elif self.pattern_matcher.is_sql_block_end(line):
            # Completar el bloque SQL
            context = self.sql_context.copy()
            self.sql_context = None
            return {
                'op': 'SQL_BLOCK',
                'commands': context['commands'],
                'raw': ' | '.join(context['raw_lines'])
            }
        
        return None
    
    def convert_sql_operation(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """Convierte comando SQL embebido a PL/SQL"""
        op = stmt.get('op', '')
        
        if op == 'SQL_BLOCK_START':
            return f"{base_indent}-- SQL Block Start"
        
        elif op == 'SQL_COMMAND':
            command_info = stmt.get('command_info', {})
            return self.converter.convert_sql_command(command_info, base_indent)
        
        elif op == 'SQL_BLOCK':
            commands = stmt.get('commands', [])
            if not commands:
                return f"{base_indent}-- GAP: Empty SQL block"
            
            # Convertir todos los comandos
            results = []
            for command_info in commands:
                result = self.converter.convert_sql_command(command_info, base_indent)
                results.append(result)
            
            return '\n'.join(results)
        
        else:
            return f"{base_indent}-- GAP: Unknown SQL operation"


class SqlHandlerFactory:
    """
    Factory para crear handlers de SQL embebido
    Implementa el patrón Factory con principios SOLID
    """
    
    @staticmethod
    def create_standard_handler() -> CobolSqlHandler:
        """Crea un handler estándar de SQL embebido"""
        return CobolSqlHandler()
    
    @staticmethod
    def create_custom_handler(custom_patterns: Dict[str, List[str]]) -> CobolSqlHandler:
        """Crea un handler personalizado de SQL embebido"""
        handler = CobolSqlHandler()
        # Aquí se podrían agregar patrones personalizados
        return handler
