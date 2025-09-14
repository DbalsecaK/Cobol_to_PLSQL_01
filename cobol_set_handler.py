"""
COBOL SET Handler - Implementación completa con principios SOLID
Maneja todas las variaciones de SET de COBOL a PL/SQL según el documento de migración
"""

from typing import Optional, Dict, Any, List
import re


class SetOperationType:
    """Enum para tipos de operaciones SET"""
    CONDITION_TO_TRUE = "CONDITION_TO_TRUE"
    CONDITION_TO_FALSE = "CONDITION_TO_FALSE"
    INDEX_TO_VALUE = "INDEX_TO_VALUE"
    INDEX_UP_BY = "INDEX_UP_BY"
    INDEX_DOWN_BY = "INDEX_DOWN_BY"
    INDEX_TO_INDEX = "INDEX_TO_INDEX"
    POINTER_TO_ADDRESS = "POINTER_TO_ADDRESS"
    VARIABLE_TO_TRUE = "VARIABLE_TO_TRUE"
    VARIABLE_TO_FALSE = "VARIABLE_TO_FALSE"
    VARIABLE_TO_NULL = "VARIABLE_TO_NULL"
    SWITCH_TO_ON = "SWITCH_TO_ON"
    SWITCH_TO_OFF = "SWITCH_TO_OFF"
    UNKNOWN = "UNKNOWN"


class SetPatternMatcher:
    """
    Clase para detectar patrones de SET
    Implementa Single Responsibility Principle
    """
    
    def __init__(self):
        self.patterns = {
            SetOperationType.CONDITION_TO_TRUE: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+TRUE\s*\.?\s*$',
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+TRUE\s*$'
            ],
            SetOperationType.CONDITION_TO_FALSE: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+FALSE\s*\.?\s*$',
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+FALSE\s*$'
            ],
            SetOperationType.INDEX_TO_VALUE: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+(\d+)\s*\.?\s*$',
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+([A-Z0-9-]+)\s*\.?\s*$'
            ],
            SetOperationType.INDEX_UP_BY: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+UP\s+BY\s+(\d+)\s*\.?\s*$',
                r'^\s*SET\s+([A-Z0-9-]+)\s+UP\s+BY\s+([A-Z0-9-]+)\s*\.?\s*$'
            ],
            SetOperationType.INDEX_DOWN_BY: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+DOWN\s+BY\s+(\d+)\s*\.?\s*$',
                r'^\s*SET\s+([A-Z0-9-]+)\s+DOWN\s+BY\s+([A-Z0-9-]+)\s*\.?\s*$'
            ],
            SetOperationType.INDEX_TO_INDEX: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+([A-Z0-9-]+)\s*\.?\s*$'
            ],
            SetOperationType.POINTER_TO_ADDRESS: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+ADDRESS\s+OF\s+([A-Z0-9-]+)\s*\.?\s*$'
            ],
            SetOperationType.VARIABLE_TO_TRUE: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+TRUE\s*\.?\s*$'
            ],
            SetOperationType.VARIABLE_TO_FALSE: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+FALSE\s*\.?\s*$'
            ],
            SetOperationType.VARIABLE_TO_NULL: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+NULL\s*\.?\s*$'
            ],
            SetOperationType.SWITCH_TO_ON: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+ON\s*\.?\s*$'
            ],
            SetOperationType.SWITCH_TO_OFF: [
                r'^\s*SET\s+([A-Z0-9-]+)\s+TO\s+OFF\s*\.?\s*$'
            ],
            # Casos especiales con nombres calificados
            'QUALIFIED_CONDITION_TO_TRUE': [
                r'^\s*SET\s+([A-Z0-9-]+)\s+OF\s+([A-Z0-9-]+)\s+OF\s+([A-Z0-9-]+)\s+TO\s+TRUE\s*\.?\s*$',
                r'^\s*SET\s+([A-Z0-9-]+)\s+OF\s+([A-Z0-9-]+)\s+TO\s+TRUE\s*\.?\s*$'
            ]
        }
    
    def match_pattern(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Detecta el patrón de SET en la línea
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


class SetConverter:
    """
    Clase para convertir operaciones SET a PL/SQL
    Implementa Single Responsibility Principle
    """
    
    def __init__(self):
        self.condition_names = set()  # Para trackear condition names conocidos
        self.index_names = set()      # Para trackear índices conocidos
    
    def convert_set_operation(self, operation_info: Dict[str, Any], base_indent: str) -> str:
        """
        Convierte una operación SET a PL/SQL
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
        
        if operation_type == SetOperationType.CONDITION_TO_TRUE:
            return self._convert_condition_to_true(groups[0], base_indent)
        
        elif operation_type == SetOperationType.CONDITION_TO_FALSE:
            return self._convert_condition_to_false(groups[0], base_indent)
        
        elif operation_type == SetOperationType.INDEX_TO_VALUE:
            return self._convert_index_to_value(groups[0], groups[1], base_indent)
        
        elif operation_type == SetOperationType.INDEX_UP_BY:
            return self._convert_index_up_by(groups[0], groups[1], base_indent)
        
        elif operation_type == SetOperationType.INDEX_DOWN_BY:
            return self._convert_index_down_by(groups[0], groups[1], base_indent)
        
        elif operation_type == SetOperationType.INDEX_TO_INDEX:
            return self._convert_index_to_index(groups[0], groups[1], base_indent)
        
        elif operation_type == SetOperationType.POINTER_TO_ADDRESS:
            return self._convert_pointer_to_address(groups[0], groups[1], base_indent)
        
        elif operation_type == SetOperationType.VARIABLE_TO_TRUE:
            return self._convert_variable_to_true(groups[0], base_indent)
        
        elif operation_type == SetOperationType.VARIABLE_TO_FALSE:
            return self._convert_variable_to_false(groups[0], base_indent)
        
        elif operation_type == SetOperationType.VARIABLE_TO_NULL:
            return self._convert_variable_to_null(groups[0], base_indent)
        
        elif operation_type == SetOperationType.SWITCH_TO_ON:
            return self._convert_switch_to_on(groups[0], base_indent)
        
        elif operation_type == SetOperationType.SWITCH_TO_OFF:
            return self._convert_switch_to_off(groups[0], base_indent)
        
        elif operation_type == 'QUALIFIED_CONDITION_TO_TRUE':
            if len(groups) == 3:
                return self._convert_qualified_condition_to_true(groups[0], groups[1], groups[2], base_indent)
            elif len(groups) == 2:
                return self._convert_qualified_condition_to_true(groups[0], groups[1], None, base_indent)
        
        else:
            return f"{base_indent}-- GAP: {raw}"
    
    def _convert_condition_to_true(self, condition_name: str, base_indent: str) -> str:
        """Convierte SET condition-name TO TRUE"""
        clean_name = condition_name.replace('-', '_').lower()
        self.condition_names.add(clean_name)
        return f"{base_indent}{clean_name} := TRUE; -- SET {condition_name} TO TRUE"
    
    def _convert_condition_to_false(self, condition_name: str, base_indent: str) -> str:
        """Convierte SET condition-name TO FALSE"""
        clean_name = condition_name.replace('-', '_').lower()
        self.condition_names.add(clean_name)
        return f"{base_indent}{clean_name} := FALSE; -- SET {condition_name} TO FALSE"
    
    def _convert_index_to_value(self, index_name: str, value: str, base_indent: str) -> str:
        """Convierte SET index TO value"""
        clean_index = index_name.replace('-', '_').lower()
        self.index_names.add(clean_index)
        
        # Verificar si el valor es numérico
        if value.isdigit():
            return f"{base_indent}{clean_index} := {value}; -- SET {index_name} TO {value}"
        else:
            clean_value = value.replace('-', '_').lower()
            return f"{base_indent}{clean_index} := {clean_value}; -- SET {index_name} TO {value}"
    
    def _convert_index_up_by(self, index_name: str, increment: str, base_indent: str) -> str:
        """Convierte SET index UP BY value"""
        clean_index = index_name.replace('-', '_').lower()
        self.index_names.add(clean_index)
        
        if increment.isdigit():
            return f"{base_indent}{clean_index} := {clean_index} + {increment}; -- SET {index_name} UP BY {increment}"
        else:
            clean_increment = increment.replace('-', '_').lower()
            return f"{base_indent}{clean_index} := {clean_index} + {clean_increment}; -- SET {index_name} UP BY {increment}"
    
    def _convert_index_down_by(self, index_name: str, decrement: str, base_indent: str) -> str:
        """Convierte SET index DOWN BY value"""
        clean_index = index_name.replace('-', '_').lower()
        self.index_names.add(clean_index)
        
        if decrement.isdigit():
            return f"{base_indent}{clean_index} := {clean_index} - {decrement}; -- SET {index_name} DOWN BY {decrement}"
        else:
            clean_decrement = decrement.replace('-', '_').lower()
            return f"{base_indent}{clean_index} := {clean_index} - {clean_decrement}; -- SET {index_name} DOWN BY {decrement}"
    
    def _convert_index_to_index(self, index1: str, index2: str, base_indent: str) -> str:
        """Convierte SET index1 TO index2"""
        clean_index1 = index1.replace('-', '_').lower()
        clean_index2 = index2.replace('-', '_').lower()
        self.index_names.add(clean_index1)
        self.index_names.add(clean_index2)
        return f"{base_indent}{clean_index1} := {clean_index2}; -- SET {index1} TO {index2}"
    
    def _convert_pointer_to_address(self, pointer_name: str, variable_name: str, base_indent: str) -> str:
        """Convierte SET pointer TO ADDRESS OF variable"""
        clean_pointer = pointer_name.replace('-', '_').lower()
        clean_variable = variable_name.replace('-', '_').lower()
        return f"{base_indent}{clean_pointer} := '{clean_variable}'; -- SET {pointer_name} TO ADDRESS OF {variable_name}"
    
    def _convert_variable_to_true(self, variable_name: str, base_indent: str) -> str:
        """Convierte SET variable TO TRUE"""
        clean_name = variable_name.replace('-', '_').lower()
        return f"{base_indent}{clean_name} := TRUE; -- SET {variable_name} TO TRUE"
    
    def _convert_variable_to_false(self, variable_name: str, base_indent: str) -> str:
        """Convierte SET variable TO FALSE"""
        clean_name = variable_name.replace('-', '_').lower()
        return f"{base_indent}{clean_name} := FALSE; -- SET {variable_name} TO FALSE"
    
    def _convert_variable_to_null(self, variable_name: str, base_indent: str) -> str:
        """Convierte SET variable TO NULL"""
        clean_name = variable_name.replace('-', '_').lower()
        return f"{base_indent}{clean_name} := NULL; -- SET {variable_name} TO NULL"
    
    def _convert_switch_to_on(self, switch_name: str, base_indent: str) -> str:
        """Convierte SET switch TO ON"""
        clean_name = switch_name.replace('-', '_').lower()
        return f"{base_indent}{clean_name} := TRUE; -- SET {switch_name} TO ON"
    
    def _convert_switch_to_off(self, switch_name: str, base_indent: str) -> str:
        """Convierte SET switch TO OFF"""
        clean_name = switch_name.replace('-', '_').lower()
        return f"{base_indent}{clean_name} := FALSE; -- SET {switch_name} TO OFF"
    
    def _convert_qualified_condition_to_true(self, field_name: str, group1: str, group2: Optional[str], base_indent: str) -> str:
        """Convierte SET field OF group1 [OF group2] TO TRUE"""
        clean_field = field_name.replace('-', '_').lower()
        clean_group1 = group1.replace('-', '_').lower()
        
        if group2:
            clean_group2 = group2.replace('-', '_').lower()
            qualified_name = f"{clean_group2}.{clean_group1}.{clean_field}"
            original = f"{field_name} OF {group1} OF {group2}"
        else:
            qualified_name = f"{clean_group1}.{clean_field}"
            original = f"{field_name} OF {group1}"
        
        return f"{base_indent}{qualified_name} := TRUE; -- SET {original} TO TRUE"


class CobolSetHandler:
    """
    Handler principal para operaciones SET de COBOL
    Implementa principios SOLID:
    - SRP: Solo maneja operaciones SET
    - OCP: Abierto para extensión, cerrado para modificación
    - LSP: Intercambiable con otros handlers
    - ISP: Interfaz específica para SET
    - DIP: Depende de abstracciones (matcher y converter)
    """
    
    def __init__(self):
        self.pattern_matcher = SetPatternMatcher()
        self.converter = SetConverter()
    
    def can_handle(self, line: str) -> bool:
        """
        Verifica si la línea puede ser manejada por este handler
        Args:
            line: Línea de código COBOL
        Returns:
            bool: True si puede manejar la línea
        """
        return self.pattern_matcher.match_pattern(line) is not None
    
    def parse_set_operation(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parsea una línea de SET
        Args:
            line: Línea de código COBOL
        Returns:
            Dict con información del SET o None si no es válido
        """
        pattern_result = self.pattern_matcher.match_pattern(line)
        if not pattern_result:
            return None
        
        return {
            'op': 'SET',
            'operation_type': pattern_result['operation_type'],
            'groups': pattern_result['groups'],
            'raw': pattern_result['raw']
        }
    
    def convert_set_operation(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """
        Convierte SET a PL/SQL
        Args:
            stmt: Declaración parseada de SET
            base_indent: Indentación base
        Returns:
            str: Código PL/SQL equivalente
        """
        return self.converter.convert_set_operation(stmt, base_indent)
    
    def get_known_condition_names(self) -> set:
        """Retorna los condition names conocidos"""
        return self.converter.condition_names.copy()
    
    def get_known_index_names(self) -> set:
        """Retorna los índices conocidos"""
        return self.converter.index_names.copy()


class SetHandlerFactory:
    """
    Factory para crear handlers de SET
    Implementa el patrón Factory con principios SOLID
    """
    
    @staticmethod
    def create_standard_handler() -> CobolSetHandler:
        """
        Crea un handler estándar de SET
        Returns:
            CobolSetHandler: Handler configurado
        """
        return CobolSetHandler()
    
    @staticmethod
    def create_custom_handler(custom_patterns: Dict[str, List[str]]) -> CobolSetHandler:
        """
        Crea un handler personalizado de SET
        Args:
            custom_patterns: Patrones personalizados
        Returns:
            CobolSetHandler: Handler con patrones personalizados
        """
        handler = CobolSetHandler()
        handler.pattern_matcher.patterns.update(custom_patterns)
        return handler
