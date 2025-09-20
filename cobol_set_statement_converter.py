#!/usr/bin/env python3
"""
COBOL SET STATEMENT CONVERTER - Conversor de sentencias SET COBOL a PL/SQL

Basado en el archivo de migración de sentencias SET y el programa manual C1040_A_MANO.pck
Implementa conversión de todas las variantes de SET COBOL a PL/SQL siguiendo principios SOLID.

PRINCIPIOS SOLID APLICADOS:
- S: Single Responsibility - Cada clase maneja un aspecto específico de SET
- O: Open/Closed - Extensible para nuevas variantes sin modificar código existente  
- L: Liskov Substitution - Conversores intercambiables
- I: Interface Segregation - Interfaces específicas por tipo de SET
- D: Dependency Inversion - Abstracción de estrategias de conversión

VARIANTES DE SET IMPLEMENTADAS:
1. SET condition-name TO TRUE/FALSE (88 levels)
2. SET index TO value (índices de tabla) 
3. SET index UP BY/DOWN BY increment
4. SET variable TO TRUE/FALSE (flags booleanos)
5. SET pointer TO ADDRESS/NULL
6. SET index TO other-index

PATRONES DEL ARCHIVO MANUAL C1040_A_MANO.pck:
- NO_ENCONTRADO := TRUE;
- Variable := valor; (asignaciones directas)
- Uso de BOOLEAN para flags
"""

import re
from typing import Dict, Any, List, Optional, Union, Tuple
from abc import ABC, abstractmethod
from enum import Enum

class SetOperation(Enum):
    """Tipos de operaciones SET"""
    CONDITION_NAME_TRUE = "condition_name_true"
    CONDITION_NAME_FALSE = "condition_name_false"
    INDEX_TO_VALUE = "index_to_value"
    INDEX_UP_BY = "index_up_by"
    INDEX_DOWN_BY = "index_down_by"
    INDEX_TO_INDEX = "index_to_index"
    VARIABLE_TO_TRUE = "variable_to_true"
    VARIABLE_TO_FALSE = "variable_to_false"
    VARIABLE_TO_NULL = "variable_to_null"
    POINTER_TO_ADDRESS = "pointer_to_address"
    ADDRESS_TO_POINTER = "address_to_pointer"

class ISetStatementConverter(ABC):
    """Interface para conversores de sentencias SET - Interface Segregation Principle"""
    
    @abstractmethod
    def convert(self, set_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir sentencia SET COBOL a PL/SQL"""
        pass
    
    @abstractmethod
    def can_handle(self, set_type: str) -> bool:
        """Verificar si puede manejar este tipo de SET"""
        pass
    
    @abstractmethod
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        pass

class ISetStatementParser(ABC):
    """Interface para parseadores de sentencias SET"""
    
    @abstractmethod
    def parse_set_statement(self, statement: str) -> Dict[str, Any]:
        """Parsear sentencia SET COBOL"""
        pass

class CobolSetStatementParser(ISetStatementParser):
    """Parser de sentencias SET COBOL basado en el documento de migración"""
    
    def __init__(self):
        # Patrones para diferentes tipos de SET
        self.set_patterns = {
            # SET condition-name TO TRUE/FALSE
            'condition_to_true': r'SET\s+([A-Z][\w\-]*)\s+TO\s+TRUE',
            'condition_to_false': r'SET\s+([A-Z][\w\-]*)\s+TO\s+FALSE',
            
            # SET index operations
            'index_to_value': r'SET\s+([A-Z][\w\-]*)\s+TO\s+([0-9]+|[A-Z][\w\-]*)',
            'index_up_by': r'SET\s+([A-Z][\w\-]*)\s+UP\s+BY\s+([0-9]+|[A-Z][\w\-]*)',
            'index_down_by': r'SET\s+([A-Z][\w\-]*)\s+DOWN\s+BY\s+([0-9]+|[A-Z][\w\-]*)',
            
            # SET variable TO boolean
            'variable_to_true': r'SET\s+([A-Z][\w\-]*)\s+TO\s+TRUE',
            'variable_to_false': r'SET\s+([A-Z][\w\-]*)\s+TO\s+FALSE',
            'variable_to_null': r'SET\s+([A-Z][\w\-]*)\s+TO\s+NULL',
            
            # SET pointer operations
            'pointer_to_address': r'SET\s+([A-Z][\w\-]*)\s+TO\s+ADDRESS\s+OF\s+([A-Z][\w\-]*)',
            'address_to_pointer': r'SET\s+ADDRESS\s+OF\s+([A-Z][\w\-]*)\s+TO\s+([A-Z][\w\-]*)',
        }
    
    def parse_set_statement(self, statement: str) -> Dict[str, Any]:
        """Parsear sentencia SET COBOL"""
        statement = statement.strip()
        
        # Buscar patrón que coincida
        for set_type, pattern in self.set_patterns.items():
            match = re.search(pattern, statement, re.IGNORECASE)
            if match:
                return self._build_set_info(set_type, match, statement)
        
        # No reconocida
        return {
            'type': 'unknown',
            'raw': statement,
            'is_set_statement': False
        }
    
    def _build_set_info(self, set_type: str, match, statement: str) -> Dict[str, Any]:
        """Construir información de sentencia SET"""
        base_info = {
            'type': set_type,
            'raw': statement,
            'is_set_statement': True
        }
        
        if set_type in ['condition_to_true', 'condition_to_false', 'variable_to_true', 'variable_to_false', 'variable_to_null']:
            base_info.update({
                'variable': self._clean_identifier(match.group(1)),
                'operation': SetOperation.CONDITION_NAME_TRUE if 'true' in set_type else 
                           SetOperation.CONDITION_NAME_FALSE if 'false' in set_type else
                           SetOperation.VARIABLE_TO_NULL if 'null' in set_type else
                           SetOperation.VARIABLE_TO_TRUE if 'variable' in set_type and 'true' in set_type else
                           SetOperation.VARIABLE_TO_FALSE
            })
        
        elif set_type == 'index_to_value':
            base_info.update({
                'index': self._clean_identifier(match.group(1)),
                'value': match.group(2),
                'operation': SetOperation.INDEX_TO_VALUE
            })
        
        elif set_type == 'index_up_by':
            base_info.update({
                'index': self._clean_identifier(match.group(1)),
                'increment': match.group(2),
                'operation': SetOperation.INDEX_UP_BY
            })
        
        elif set_type == 'index_down_by':
            base_info.update({
                'index': self._clean_identifier(match.group(1)),
                'decrement': match.group(2),
                'operation': SetOperation.INDEX_DOWN_BY
            })
        
        elif set_type == 'pointer_to_address':
            base_info.update({
                'pointer': self._clean_identifier(match.group(1)),
                'target_variable': self._clean_identifier(match.group(2)),
                'operation': SetOperation.POINTER_TO_ADDRESS
            })
        
        elif set_type == 'address_to_pointer':
            base_info.update({
                'target_variable': self._clean_identifier(match.group(1)),
                'pointer': self._clean_identifier(match.group(2)),
                'operation': SetOperation.ADDRESS_TO_POINTER
            })
        
        return base_info
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador COBOL para PL/SQL"""
        if not identifier:
            return identifier
        return identifier.strip().lower().replace('-', '_')

class ConditionNameSetConverter(ISetStatementConverter):
    """Conversor para SET con condition names (88 levels) - Single Responsibility Principle"""
    
    def can_handle(self, set_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return set_type in ['condition_to_true', 'condition_to_false']
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "CONDITION_NAME"
    
    def convert(self, set_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir SET condition-name TO TRUE/FALSE"""
        variable = set_info.get('variable', 'unknown_variable')
        set_type = set_info.get('type', '')
        
        # Patrón del archivo manual: variable := TRUE/FALSE;
        if 'true' in set_type:
            # SET condition-name TO TRUE
            # En el archivo manual se ve: NO_ENCONTRADO := TRUE;
            return f"""
    {variable.upper()} := TRUE;"""
        else:
            # SET condition-name TO FALSE
            return f"""
    {variable.upper()} := FALSE;"""

class IndexSetConverter(ISetStatementConverter):
    """Conversor para SET con índices de tabla - Single Responsibility Principle"""
    
    def can_handle(self, set_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return set_type in ['index_to_value', 'index_up_by', 'index_down_by']
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "INDEX"
    
    def convert(self, set_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir SET index operations"""
        set_type = set_info.get('type', '')
        
        if set_type == 'index_to_value':
            index = set_info.get('index', 'unknown_index')
            value = set_info.get('value', '1')
            
            # Determinar si el valor es numérico o variable
            if value.isdigit():
                return f"""
    {index.upper()} := {value};"""
            else:
                # Es una variable
                value_clean = value.lower().replace('-', '_')
                return f"""
    {index.upper()} := {value_clean.upper()};"""
        
        elif set_type == 'index_up_by':
            index = set_info.get('index', 'unknown_index')
            increment = set_info.get('increment', '1')
            
            if increment.isdigit():
                return f"""
    {index.upper()} := {index.upper()} + {increment};"""
            else:
                # Es una variable
                increment_clean = increment.lower().replace('-', '_')
                return f"""
    {index.upper()} := {index.upper()} + {increment_clean.upper()};"""
        
        elif set_type == 'index_down_by':
            index = set_info.get('index', 'unknown_index')
            decrement = set_info.get('decrement', '1')
            
            if decrement.isdigit():
                return f"""
    {index.upper()} := {index.upper()} - {decrement};"""
            else:
                # Es una variable
                decrement_clean = decrement.lower().replace('-', '_')
                return f"""
    {index.upper()} := {index.upper()} - {decrement_clean.upper()};"""
        
        return f"""
    -- GAP -- {set_info.get('raw', '')} -- (INDEX SET not supported)"""

class BooleanSetConverter(ISetStatementConverter):
    """Conversor para SET con variables booleanas - Single Responsibility Principle"""
    
    def can_handle(self, set_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return set_type in ['variable_to_true', 'variable_to_false', 'variable_to_null']
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "BOOLEAN"
    
    def convert(self, set_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir SET variable TO TRUE/FALSE/NULL"""
        variable = set_info.get('variable', 'unknown_variable')
        set_type = set_info.get('type', '')
        
        if 'true' in set_type:
            # Patrón del archivo manual: variable := TRUE;
            return f"""
    {variable.upper()} := TRUE;"""
        elif 'false' in set_type:
            return f"""
    {variable.upper()} := FALSE;"""
        elif 'null' in set_type:
            return f"""
    {variable.upper()} := NULL;"""
        
        return f"""
    -- GAP -- {set_info.get('raw', '')} -- (BOOLEAN SET not supported)"""

class PointerSetConverter(ISetStatementConverter):
    """Conversor para SET con punteros - Single Responsibility Principle"""
    
    def can_handle(self, set_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return set_type in ['pointer_to_address', 'address_to_pointer']
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "POINTER"
    
    def convert(self, set_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir SET pointer operations"""
        set_type = set_info.get('type', '')
        raw_content = set_info.get('raw', '')
        
        if set_type == 'pointer_to_address':
            pointer = set_info.get('pointer', 'unknown_pointer')
            target_variable = set_info.get('target_variable', 'unknown_variable')
            
            # PL/SQL no tiene punteros como COBOL - usar referencia simbólica
            return f"""
    -- GAP -- {raw_content} -- (POINTER operations not directly supported in PL/SQL)
    -- TODO: Consider using REF CURSOR or symbolic references
    {pointer.upper()}_REF := '{target_variable.upper()}';"""
        
        elif set_type == 'address_to_pointer':
            target_variable = set_info.get('target_variable', 'unknown_variable')
            pointer = set_info.get('pointer', 'unknown_pointer')
            
            return f"""
    -- GAP -- {raw_content} -- (ADDRESS operations not directly supported in PL/SQL)
    -- TODO: Consider using direct variable assignment
    {target_variable.upper()} := {pointer.upper()}_VALUE;"""
        
        return f"""
    -- GAP -- {raw_content} -- (POINTER SET not supported)"""

class SetStatementConverterFactory:
    """Factory para crear conversores de sentencias SET - Dependency Inversion Principle"""
    
    def __init__(self):
        self.converters = [
            ConditionNameSetConverter(),
            IndexSetConverter(),
            BooleanSetConverter(),
            PointerSetConverter()
        ]
        self.parser = CobolSetStatementParser()
    
    def get_converter(self, set_type: str) -> Optional[ISetStatementConverter]:
        """Obtener conversor apropiado para el tipo de SET"""
        for converter in self.converters:
            if converter.can_handle(set_type):
                return converter
        return None
    
    def convert_set_statement(self, statement: str, context: Dict[str, Any] = None) -> str:
        """Convertir sentencia SET completa"""
        # Parsear la sentencia
        set_info = self.parser.parse_set_statement(statement)
        
        if not set_info.get('is_set_statement', False):
            return f"  -- GAP -- {statement} -- (Unknown SET statement)"
        
        # Obtener conversor apropiado
        set_type = set_info.get('type', 'unknown')
        converter = self.get_converter(set_type)
        
        if not converter:
            return f"  -- GAP -- {statement} -- (SET operation not supported: {set_type})"
        
        try:
            return converter.convert(set_info, context)
        except Exception as e:
            return f"  -- GAP -- {statement} -- (SET conversion error: {e})"
    
    def detect_set_statements(self, cobol_code: str) -> List[Dict[str, Any]]:
        """Detectar todas las sentencias SET en código COBOL"""
        lines = cobol_code.split('\n')
        set_statements = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            set_info = self.parser.parse_set_statement(line)
            if set_info.get('is_set_statement', False):
                set_info['line_number'] = i + 1
                set_statements.append(set_info)
        
        return set_statements
    
    def generate_condition_name_constants(self, set_statements: List[Dict[str, Any]]) -> str:
        """Generar constantes para condition names basado en sentencias SET detectadas"""
        constants = []
        condition_names = set()
        
        for stmt in set_statements:
            if stmt.get('operation') in [SetOperation.CONDITION_NAME_TRUE, SetOperation.CONDITION_NAME_FALSE]:
                variable = stmt.get('variable', '')
                if variable and variable not in condition_names:
                    condition_names.add(variable)
                    # Generar constantes según el patrón del documento
                    constants.append(f"    c_{variable.upper()}_TRUE  CONSTANT BOOLEAN := TRUE;")
                    constants.append(f"    c_{variable.upper()}_FALSE CONSTANT BOOLEAN := FALSE;")
        
        if constants:
            return """
  -- CONDITION NAME CONSTANTS
""" + '\n'.join(constants)
        else:
            return ""
    
    def generate_set_utility_functions(self, set_statements: List[Dict[str, Any]]) -> str:
        """Generar funciones utilitarias para SET basado en el documento de migración"""
        functions = []
        processed_variables = set()
        
        for stmt in set_statements:
            if stmt.get('operation') in [SetOperation.CONDITION_NAME_TRUE, SetOperation.CONDITION_NAME_FALSE]:
                variable = stmt.get('variable', '')
                if variable and variable not in processed_variables:
                    processed_variables.add(variable)
                    
                    # Generar función IS_ y procedimiento SET_
                    functions.append(f"""
    FUNCTION IS_{variable.upper()} RETURN BOOLEAN IS
    BEGIN
        RETURN {variable.upper()};
    END IS_{variable.upper()};
    
    PROCEDURE SET_{variable.upper()}(p_value BOOLEAN) IS
    BEGIN
        {variable.upper()} := p_value;
    END SET_{variable.upper()};""")
        
        if functions:
            return """
  -- SET UTILITY FUNCTIONS
""" + '\n'.join(functions)
        else:
            return ""

# Utilidades de migración avanzada
class CobolSetMigrator:
    """Migrador completo de sentencias SET COBOL"""
    
    def __init__(self):
        self.factory = SetStatementConverterFactory()
    
    def migrate_set_statements_in_procedure(self, procedure_code: str) -> str:
        """Migrar sentencias SET en PROCEDURE DIVISION"""
        lines = procedure_code.split('\n')
        converted_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                converted_lines.append(line)
                continue
            
            # Intentar convertir como sentencia SET
            set_info = self.factory.parser.parse_set_statement(line_stripped)
            
            if set_info.get('is_set_statement', False):
                converted = self.factory.convert_set_statement(line_stripped)
                converted_lines.append(converted)
            else:
                converted_lines.append(line)
        
        return '\n'.join(converted_lines)
    
    def generate_set_migration_report(self, cobol_code: str) -> Dict[str, Any]:
        """Generar reporte de migración de sentencias SET"""
        set_statements = self.factory.detect_set_statements(cobol_code)
        
        # Agrupar por tipo
        types_count = {}
        for stmt in set_statements:
            operation = stmt.get('operation', 'unknown')
            types_count[operation.value if hasattr(operation, 'value') else str(operation)] = types_count.get(operation.value if hasattr(operation, 'value') else str(operation), 0) + 1
        
        return {
            'total_set_statements': len(set_statements),
            'statements_by_type': types_count,
            'detected_statements': set_statements,
            'supported_types': len([s for s in set_statements if s.get('type') != 'unknown']),
            'unsupported_types': len([s for s in set_statements if s.get('type') == 'unknown'])
        }

# Función de prueba
def main():
    """Función de prueba del conversor de sentencias SET"""
    factory = SetStatementConverterFactory()
    
    # Casos de prueba basados en el documento de migración
    test_cases = [
        # Condition names (88 levels)
        "SET ACTIVO TO TRUE",
        "SET INACTIVO TO FALSE", 
        "SET CLIENTE-VIP TO TRUE",
        "SET PROCESO-TERMINADO TO TRUE",
        
        # Índices de tabla
        "SET IDX TO 1",
        "SET IDX1 TO IDX2",
        "SET IDX UP BY 1",
        "SET IDX DOWN BY 2",
        "SET IDX-FILA TO 3",
        "SET IDX-COL UP BY IDX-INCREMENTO",
        
        # Variables booleanas
        "SET EOF-FLAG TO TRUE",
        "SET ERROR-FLAG TO FALSE",
        "SET WS-POINTER TO NULL",
        
        # Punteros (casos especiales)
        "SET WS-POINTER TO ADDRESS OF WS-VARIABLE",
        "SET ADDRESS OF WS-VARIABLE TO WS-POINTER",
        
        # Del archivo manual (ya convertido)
        "NO_ENCONTRADO := TRUE;",  # Ya en PL/SQL
        
        # Casos combinados del documento
        "SET PROCESO-ACTIVO TO TRUE",
        "SET EOF-ENCONTRADO TO TRUE"
    ]
    
    print("🧪 PRUEBAS DEL CONVERSOR DE SENTENCIAS SET")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: {test_case}")
        print("-" * 40)
        
        try:
            result = factory.convert_set_statement(test_case)
            print(f"Resultado:\n{result}")
        except Exception as e:
            print(f"ERROR: {e}")
    
    # Prueba de detección de sentencias
    sample_cobol = """
WORKING-STORAGE SECTION.
01 WS-ESTADO PIC X VALUE 'N'.
   88 ACTIVO VALUE 'S'.
   88 INACTIVO VALUE 'N'.

01 WS-TABLA.
   05 WS-ELEMENTO OCCURS 10 TIMES INDEXED BY IDX PIC X(10).

PROCEDURE DIVISION.
    SET ACTIVO TO TRUE
    SET IDX TO 1
    SET IDX UP BY 1
    SET EOF-FLAG TO TRUE
    SET WS-POINTER TO NULL
    """
    
    print(f"\n\n🔍 DETECCIÓN DE SENTENCIAS SET EN CÓDIGO COBOL:")
    print("-" * 50)
    
    statements = factory.detect_set_statements(sample_cobol)
    for stmt in statements:
        print(f"Línea {stmt['line_number']}: {stmt['type']} - {stmt['raw']}")
    
    # Generar utilidades
    print(f"\n\n🔧 UTILIDADES GENERADAS:")
    print("-" * 30)
    constants = factory.generate_condition_name_constants(statements)
    if constants:
        print(constants)
    
    utilities = factory.generate_set_utility_functions(statements)
    if utilities:
        print(utilities)

if __name__ == "__main__":
    main()
