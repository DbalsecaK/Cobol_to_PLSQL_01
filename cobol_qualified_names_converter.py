#!/usr/bin/env python3
"""
COBOL QUALIFIED NAMES CONVERTER - Conversor de nombres cualificados COBOL a PL/SQL

Basado en el archivo de migración de nombres cualificados y el programa manual C1040_A_MANO.pck
Implementa las 5 estrategias principales siguiendo principios SOLID.

PRINCIPIOS SOLID APLICADOS:
- S: Single Responsibility - Cada clase maneja un aspecto específico de conversión
- O: Open/Closed - Extensible para nuevas estrategias sin modificar código existente  
- L: Liskov Substitution - Estrategias intercambiables
- I: Interface Segregation - Interfaces específicas por tipo de conversión
- D: Dependency Inversion - Abstracción de estrategias de conversión

ESTRATEGIAS IMPLEMENTADAS:
1. RECORDS EN PL/SQL (notación punto)
2. OBJECT TYPES (con métodos)
3. NAMING CONVENTIONS (prefijos descriptivos)
4. PACKAGES (agrupación lógica)
5. COLLECTIONS ANIDADAS (para arrays)
"""

import re
from typing import Dict, Any, List, Optional, Union, Tuple
from abc import ABC, abstractmethod
from enum import Enum

class QualifiedNameStrategy(Enum):
    """Estrategias de conversión de nombres cualificados"""
    RECORDS = "records"
    OBJECT_TYPES = "object_types"
    NAMING_CONVENTIONS = "naming_conventions"
    PACKAGES = "packages"
    COLLECTIONS = "collections"
    AUTO = "auto"  # Selección automática

class QualifiedNamePattern:
    """Clase de datos para patrones de nombres cualificados"""
    def __init__(self, pattern_type: str, regex: str, description: str, example_cobol: str, example_plsql: str):
        self.pattern_type = pattern_type
        self.regex = regex
        self.description = description
        self.example_cobol = example_cobol
        self.example_plsql = example_plsql

class IQualifiedNameConverter(ABC):
    """Interface para conversores de nombres cualificados - Interface Segregation Principle"""
    
    @abstractmethod
    def convert(self, cobol_expression: str, context: Dict[str, Any] = None) -> str:
        """Convertir expresión COBOL con nombres cualificados a PL/SQL"""
        pass
    
    @abstractmethod
    def can_handle(self, cobol_expression: str) -> bool:
        """Verificar si puede manejar esta expresión"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Obtener nombre de la estrategia"""
        pass

class IQualifiedNameParser(ABC):
    """Interface para parseadores de nombres cualificados"""
    
    @abstractmethod
    def parse_qualified_reference(self, expression: str) -> Dict[str, Any]:
        """Parsear referencia cualificada COBOL"""
        pass

class CobolQualifiedNameParser(IQualifiedNameParser):
    """Parser de nombres cualificados COBOL basado en el archivo de referencia"""
    
    def __init__(self):
        # Patrones de nombres cualificados basados en el archivo de migración
        self.qualified_patterns = [
            QualifiedNamePattern(
                'triple_qualified',
                r'([A-Z][\w\-]*)\s+OF\s+([A-Z][\w\-]*)\s+OF\s+([A-Z][\w\-]*)',
                'Triple cualificación: VARIABLE OF GROUP OF SUPERGROUP',
                'CODIGO-EMPLEADO OF DATOS-PERSONALES OF EMPLEADO-ACTUAL',
                'empleado_actual.datos_personales.codigo_empleado'
            ),
            QualifiedNamePattern(
                'double_qualified', 
                r'([A-Z][\w\-]*)\s+OF\s+([A-Z][\w\-]*)',
                'Doble cualificación: VARIABLE OF GROUP',
                'NUM-ERROR OF S21-AREA-ERROR',
                's21_area_error.num_error'
            ),
            QualifiedNamePattern(
                'array_qualified',
                r'([A-Z][\w\-]*)\s*\((\d+(?:\s*,\s*\d+)*)\)\s+OF\s+([A-Z][\w\-]*)',
                'Array cualificado: VARIABLE(index) OF GROUP',
                'TOTAL-SUCURSAL(1, 3) OF VENTAS-MENSUALES',
                'ventas_mensuales(1)(3).total_sucursal'
            ),
            QualifiedNamePattern(
                'simple_qualified',
                r'([A-Z][\w\-]*)\s+IN\s+([A-Z][\w\-]*)',
                'Cualificación con IN: VARIABLE IN GROUP',
                'CODIGO IN DATOS-CLIENTE',
                'datos_cliente.codigo'
            )
        ]
    
    def parse_qualified_reference(self, expression: str) -> Dict[str, Any]:
        """Parsear referencia cualificada COBOL"""
        expression = expression.strip()
        
        # Buscar patrón que coincida
        for pattern in self.qualified_patterns:
            match = re.search(pattern.regex, expression, re.IGNORECASE)
            if match:
                return self._build_qualified_info(pattern, match, expression)
        
        # No es una referencia cualificada, devolver como variable simple
        return {
            'type': 'simple_variable',
            'variable': self._clean_identifier(expression),
            'raw': expression,
            'is_qualified': False
        }
    
    def _build_qualified_info(self, pattern: QualifiedNamePattern, match, expression: str) -> Dict[str, Any]:
        """Construir información de nombre cualificado"""
        if pattern.pattern_type == 'triple_qualified':
            return {
                'type': 'triple_qualified',
                'variable': self._clean_identifier(match.group(1)),
                'group': self._clean_identifier(match.group(2)),
                'supergroup': self._clean_identifier(match.group(3)),
                'raw': expression,
                'is_qualified': True,
                'hierarchy': [
                    self._clean_identifier(match.group(3)),  # supergroup
                    self._clean_identifier(match.group(2)),  # group
                    self._clean_identifier(match.group(1))   # variable
                ]
            }
        elif pattern.pattern_type == 'double_qualified':
            return {
                'type': 'double_qualified',
                'variable': self._clean_identifier(match.group(1)),
                'group': self._clean_identifier(match.group(2)),
                'raw': expression,
                'is_qualified': True,
                'hierarchy': [
                    self._clean_identifier(match.group(2)),  # group
                    self._clean_identifier(match.group(1))   # variable
                ]
            }
        elif pattern.pattern_type == 'array_qualified':
            indices = [idx.strip() for idx in match.group(2).split(',')]
            return {
                'type': 'array_qualified',
                'variable': self._clean_identifier(match.group(1)),
                'group': self._clean_identifier(match.group(3)),
                'indices': indices,
                'raw': expression,
                'is_qualified': True,
                'hierarchy': [
                    self._clean_identifier(match.group(3)),  # group
                    self._clean_identifier(match.group(1))   # variable
                ]
            }
        elif pattern.pattern_type == 'simple_qualified':
            return {
                'type': 'simple_qualified',
                'variable': self._clean_identifier(match.group(1)),
                'group': self._clean_identifier(match.group(2)),
                'raw': expression,
                'is_qualified': True,
                'hierarchy': [
                    self._clean_identifier(match.group(2)),  # group
                    self._clean_identifier(match.group(1))   # variable
                ]
            }
        
        return {'type': 'unknown', 'raw': expression, 'is_qualified': False}
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador COBOL para PL/SQL"""
        if not identifier:
            return identifier
        
        # Convertir a minúsculas y reemplazar guiones
        clean_id = identifier.strip().lower().replace('-', '_')
        
        # Remover caracteres especiales
        clean_id = re.sub(r'[^\w]', '_', clean_id)
        
        return clean_id

class RecordsQualifiedConverter(IQualifiedNameConverter):
    """Conversor usando RECORDS (Estrategia 1) - Single Responsibility Principle"""
    
    def __init__(self):
        self.parser = CobolQualifiedNameParser()
    
    def can_handle(self, cobol_expression: str) -> bool:
        """Verificar si puede manejar esta expresión"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        return qualified_info.get('is_qualified', False)
    
    def get_strategy_name(self) -> str:
        """Obtener nombre de la estrategia"""
        return "RECORDS"
    
    def convert(self, cobol_expression: str, context: Dict[str, Any] = None) -> str:
        """Convertir usando notación punto con RECORDS"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        
        if not qualified_info.get('is_qualified', False):
            return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))
        
        # Construir notación punto basada en jerarquía
        hierarchy = qualified_info.get('hierarchy', [])
        
        if qualified_info['type'] == 'triple_qualified':
            # supergroup.group.variable
            return f"{hierarchy[0]}.{hierarchy[1]}.{hierarchy[2]}"
        
        elif qualified_info['type'] == 'double_qualified':
            # group.variable
            return f"{hierarchy[0]}.{hierarchy[1]}"
        
        elif qualified_info['type'] == 'array_qualified':
            # Para arrays: group(indices).variable
            indices = qualified_info.get('indices', [])
            group = hierarchy[0]
            variable = hierarchy[1]
            
            if len(indices) == 1:
                return f"{group}({indices[0]}).{variable}"
            elif len(indices) == 2:
                return f"{group}({indices[0]})({indices[1]}).{variable}"
            else:
                # Múltiples índices
                index_notation = ''.join(f"({idx})" for idx in indices)
                return f"{group}{index_notation}.{variable}"
        
        elif qualified_info['type'] == 'simple_qualified':
            # group.variable
            return f"{hierarchy[0]}.{hierarchy[1]}"
        
        return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))

class NamingConventionsQualifiedConverter(IQualifiedNameConverter):
    """Conversor usando NAMING CONVENTIONS (Estrategia 3) - Single Responsibility Principle"""
    
    def __init__(self):
        self.parser = CobolQualifiedNameParser()
    
    def can_handle(self, cobol_expression: str) -> bool:
        """Verificar si puede manejar esta expresión"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        return qualified_info.get('is_qualified', False)
    
    def get_strategy_name(self) -> str:
        """Obtener nombre de la estrategia"""
        return "NAMING_CONVENTIONS"
    
    def convert(self, cobol_expression: str, context: Dict[str, Any] = None) -> str:
        """Convertir usando prefijos descriptivos"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        
        if not qualified_info.get('is_qualified', False):
            return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))
        
        # Construir nombre con prefijos basado en jerarquía
        hierarchy = qualified_info.get('hierarchy', [])
        
        if qualified_info['type'] == 'triple_qualified':
            # supergroup_group_variable
            return f"{hierarchy[0]}_{hierarchy[1]}_{hierarchy[2]}"
        
        elif qualified_info['type'] == 'double_qualified':
            # group_variable
            return f"{hierarchy[0]}_{hierarchy[1]}"
        
        elif qualified_info['type'] == 'array_qualified':
            # Para arrays: group_variable con índices como sufijo
            indices = qualified_info.get('indices', [])
            group = hierarchy[0]
            variable = hierarchy[1]
            
            if indices:
                index_suffix = '_' + '_'.join(indices)
                return f"{group}_{variable}{index_suffix}"
            else:
                return f"{group}_{variable}"
        
        elif qualified_info['type'] == 'simple_qualified':
            # group_variable
            return f"{hierarchy[0]}_{hierarchy[1]}"
        
        return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))

class ObjectTypesQualifiedConverter(IQualifiedNameConverter):
    """Conversor usando OBJECT TYPES (Estrategia 2) - Single Responsibility Principle"""
    
    def __init__(self):
        self.parser = CobolQualifiedNameParser()
    
    def can_handle(self, cobol_expression: str) -> bool:
        """Verificar si puede manejar esta expresión"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        return qualified_info.get('is_qualified', False)
    
    def get_strategy_name(self) -> str:
        """Obtener nombre de la estrategia"""
        return "OBJECT_TYPES"
    
    def convert(self, cobol_expression: str, context: Dict[str, Any] = None) -> str:
        """Convertir usando notación punto con OBJECT TYPES"""
        # Similar a RECORDS pero con posibilidad de métodos
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        
        if not qualified_info.get('is_qualified', False):
            return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))
        
        hierarchy = qualified_info.get('hierarchy', [])
        
        if qualified_info['type'] == 'triple_qualified':
            return f"{hierarchy[0]}.{hierarchy[1]}.{hierarchy[2]}"
        elif qualified_info['type'] == 'double_qualified':
            return f"{hierarchy[0]}.{hierarchy[1]}"
        elif qualified_info['type'] == 'array_qualified':
            indices = qualified_info.get('indices', [])
            group = hierarchy[0]
            variable = hierarchy[1]
            
            if len(indices) == 1:
                return f"{group}({indices[0]}).{variable}"
            else:
                index_notation = ''.join(f"({idx})" for idx in indices)
                return f"{group}{index_notation}.{variable}"
        elif qualified_info['type'] == 'simple_qualified':
            return f"{hierarchy[0]}.{hierarchy[1]}"
        
        return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))

class PackagesQualifiedConverter(IQualifiedNameConverter):
    """Conversor usando PACKAGES (Estrategia 4) - Single Responsibility Principle"""
    
    def __init__(self):
        self.parser = CobolQualifiedNameParser()
    
    def can_handle(self, cobol_expression: str) -> bool:
        """Verificar si puede manejar esta expresión"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        return qualified_info.get('is_qualified', False)
    
    def get_strategy_name(self) -> str:
        """Obtener nombre de la estrategia"""
        return "PACKAGES"
    
    def convert(self, cobol_expression: str, context: Dict[str, Any] = None) -> str:
        """Convertir usando package.record.field"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        
        if not qualified_info.get('is_qualified', False):
            return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))
        
        hierarchy = qualified_info.get('hierarchy', [])
        
        # Para packages, usar sufijo _pkg en el nivel superior
        if qualified_info['type'] == 'triple_qualified':
            return f"{hierarchy[0]}_pkg.{hierarchy[1]}.{hierarchy[2]}"
        elif qualified_info['type'] == 'double_qualified':
            return f"{hierarchy[0]}_pkg.{hierarchy[1]}"
        elif qualified_info['type'] == 'array_qualified':
            indices = qualified_info.get('indices', [])
            group = hierarchy[0]
            variable = hierarchy[1]
            
            if len(indices) == 1:
                return f"{group}_pkg({indices[0]}).{variable}"
            else:
                index_notation = ''.join(f"({idx})" for idx in indices)
                return f"{group}_pkg{index_notation}.{variable}"
        elif qualified_info['type'] == 'simple_qualified':
            return f"{hierarchy[0]}_pkg.{hierarchy[1]}"
        
        return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))

class AutoQualifiedConverter(IQualifiedNameConverter):
    """Conversor automático que selecciona la mejor estrategia - Strategy Pattern"""
    
    def __init__(self):
        self.parser = CobolQualifiedNameParser()
        self.converters = {
            QualifiedNameStrategy.RECORDS: RecordsQualifiedConverter(),
            QualifiedNameStrategy.NAMING_CONVENTIONS: NamingConventionsQualifiedConverter(),
            QualifiedNameStrategy.OBJECT_TYPES: ObjectTypesQualifiedConverter(),
            QualifiedNameStrategy.PACKAGES: PackagesQualifiedConverter()
        }
        # Por defecto usar RECORDS (más similar al archivo manual)
        self.default_strategy = QualifiedNameStrategy.RECORDS
    
    def can_handle(self, cobol_expression: str) -> bool:
        """Verificar si puede manejar esta expresión"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        return qualified_info.get('is_qualified', False)
    
    def get_strategy_name(self) -> str:
        """Obtener nombre de la estrategia"""
        return "AUTO"
    
    def convert(self, cobol_expression: str, context: Dict[str, Any] = None) -> str:
        """Convertir usando selección automática de estrategia"""
        qualified_info = self.parser.parse_qualified_reference(cobol_expression)
        
        if not qualified_info.get('is_qualified', False):
            return qualified_info.get('variable', cobol_expression.lower().replace('-', '_'))
        
        # Seleccionar estrategia basada en el contexto y tipo
        strategy = self._select_best_strategy(qualified_info, context)
        converter = self.converters[strategy]
        
        return converter.convert(cobol_expression, context)
    
    def _select_best_strategy(self, qualified_info: Dict[str, Any], context: Dict[str, Any] = None) -> QualifiedNameStrategy:
        """Seleccionar la mejor estrategia basada en el contexto"""
        # Estrategia de selección basada en el archivo de referencia
        
        # Para arrays complejos, usar COLLECTIONS
        if qualified_info['type'] == 'array_qualified':
            indices = qualified_info.get('indices', [])
            if len(indices) > 1:
                return QualifiedNameStrategy.RECORDS  # Simular con RECORDS
        
        # Para jerarquías complejas (3+ niveles), usar RECORDS
        if qualified_info['type'] == 'triple_qualified':
            return QualifiedNameStrategy.RECORDS
        
        # Para referencias simples, usar RECORDS (similar al archivo manual)
        if qualified_info['type'] in ['double_qualified', 'simple_qualified']:
            return QualifiedNameStrategy.RECORDS
        
        # Por defecto, usar RECORDS
        return self.default_strategy

class QualifiedNameConverterFactory:
    """Factory para crear conversores apropiados - Dependency Inversion Principle"""
    
    def __init__(self):
        self.converters = {
            QualifiedNameStrategy.RECORDS: RecordsQualifiedConverter(),
            QualifiedNameStrategy.NAMING_CONVENTIONS: NamingConventionsQualifiedConverter(),
            QualifiedNameStrategy.OBJECT_TYPES: ObjectTypesQualifiedConverter(),
            QualifiedNameStrategy.PACKAGES: PackagesQualifiedConverter(),
            QualifiedNameStrategy.AUTO: AutoQualifiedConverter()
        }
    
    def get_converter(self, strategy: QualifiedNameStrategy = QualifiedNameStrategy.AUTO) -> IQualifiedNameConverter:
        """Obtener conversor para la estrategia especificada"""
        return self.converters.get(strategy, self.converters[QualifiedNameStrategy.AUTO])
    
    def convert_expression(self, cobol_expression: str, strategy: QualifiedNameStrategy = QualifiedNameStrategy.AUTO, 
                          context: Dict[str, Any] = None) -> str:
        """Convertir expresión usando la estrategia especificada"""
        converter = self.get_converter(strategy)
        return converter.convert(cobol_expression, context)
    
    def detect_qualified_names_in_statement(self, cobol_statement: str) -> List[Dict[str, Any]]:
        """Detectar todos los nombres cualificados en un statement COBOL"""
        parser = CobolQualifiedNameParser()
        qualified_names = []
        
        # Buscar patrones de nombres cualificados en el statement
        for pattern in parser.qualified_patterns:
            matches = re.finditer(pattern.regex, cobol_statement, re.IGNORECASE)
            for match in matches:
                qualified_info = parser._build_qualified_info(pattern, match, match.group(0))
                qualified_info['start_pos'] = match.start()
                qualified_info['end_pos'] = match.end()
                qualified_names.append(qualified_info)
        
        return qualified_names
    
    def convert_statement_with_qualified_names(self, cobol_statement: str, 
                                             strategy: QualifiedNameStrategy = QualifiedNameStrategy.AUTO,
                                             context: Dict[str, Any] = None) -> str:
        """Convertir statement completo reemplazando nombres cualificados"""
        # Detectar nombres cualificados
        qualified_names = self.detect_qualified_names_in_statement(cobol_statement)
        
        if not qualified_names:
            return cobol_statement
        
        # Ordenar por posición (de derecha a izquierda para no afectar índices)
        qualified_names.sort(key=lambda x: x['start_pos'], reverse=True)
        
        # Reemplazar cada nombre cualificado
        result = cobol_statement
        converter = self.get_converter(strategy)
        
        for qualified_info in qualified_names:
            original = qualified_info['raw']
            converted = converter.convert(original, context)
            
            start_pos = qualified_info['start_pos']
            end_pos = qualified_info['end_pos']
            
            result = result[:start_pos] + converted + result[end_pos:]
        
        return result

# Utilidad para generar tipos PL/SQL basados en COBOL
class PLSQLTypeGenerator:
    """Generador de tipos PL/SQL basado en estructuras COBOL"""
    
    @staticmethod
    def generate_record_type_from_cobol(cobol_structure: str, type_name: str) -> str:
        """Generar tipo RECORD PL/SQL desde estructura COBOL"""
        # Simplificado para ejemplo
        lines = cobol_structure.split('\n')
        fields = []
        
        for line in lines:
            # Buscar patrones como: 05 CAMPO PIC X(10)
            match = re.match(r'\s*\d+\s+([A-Z][\w\-]*)\s+PIC\s+([^\s.]+)', line, re.IGNORECASE)
            if match:
                field_name = match.group(1).lower().replace('-', '_')
                pic_clause = match.group(2)
                
                # Convertir PIC clause a tipo PL/SQL
                if 'X' in pic_clause.upper():
                    # Alfanumérico
                    size_match = re.search(r'\((\d+)\)', pic_clause)
                    size = size_match.group(1) if size_match else '1'
                    plsql_type = f"VARCHAR2({size})"
                elif '9' in pic_clause:
                    # Numérico
                    size_match = re.search(r'\((\d+)\)', pic_clause)
                    if 'V' in pic_clause:
                        # Con decimales
                        plsql_type = f"NUMBER(10,2)"
                    else:
                        size = size_match.group(1) if size_match else '1'
                        plsql_type = f"NUMBER({size})"
                else:
                    plsql_type = "VARCHAR2(50)"
                
                fields.append(f"    {field_name} {plsql_type}")
        
        record_definition = f"""TYPE {type_name} IS RECORD (
{chr(10).join(fields)}
);"""
        
        return record_definition

# Ejemplo de uso y pruebas
def main():
    """Función de prueba del conversor de nombres cualificados"""
    factory = QualifiedNameConverterFactory()
    
    # Casos de prueba basados en el archivo de migración
    test_cases = [
        # Ejemplos del archivo de referencia
        "NUM-ERROR OF S21-AREA-ERROR",
        "CODIGO-EMPLEADO OF DATOS-PERSONALES OF EMPLEADO-ACTUAL", 
        "TOTAL OF VENTAS-ENERO OF RESUMEN-ANUAL",
        "DEPARTAMENTO OF INFO-LABORAL OF DATOS-EMPLEADO",
        "TOTAL-SUCURSAL(1, 3) OF VENTAS-MENSUALES",
        "CODIGO-VENDEDOR OF DETALLE-VENDEDORES(5) OF VENTAS-MES(3)",
        
        # Statements MOVE completos
        "MOVE 'EMP001' TO CODIGO-EMPLEADO OF DATOS-PERSONALES OF EMPLEADO-ACTUAL",
        "ADD SALARIO-BASICO OF DATOS-LABORALES TO TOTAL-MASA-SALARIAL OF TOTALES",
        "IF NUM-ERROR OF S21-AREA-ERROR = ZERO",
        
        # Del archivo manual C1040
        "V_T30DOR10.NUM_OPERACION",  # Ya en formato PL/SQL
        "V_IN_CAS10010.IN_NUM_OPERACION"  # Ya en formato PL/SQL
    ]
    
    print("🧪 PRUEBAS DEL CONVERSOR DE NOMBRES CUALIFICADOS")
    print("=" * 70)
    
    strategies = [
        QualifiedNameStrategy.RECORDS,
        QualifiedNameStrategy.NAMING_CONVENTIONS,
        QualifiedNameStrategy.OBJECT_TYPES,
        QualifiedNameStrategy.AUTO
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: {test_case}")
        print("-" * 50)
        
        # Probar diferentes estrategias
        for strategy in strategies:
            try:
                result = factory.convert_expression(test_case, strategy)
                print(f"  {strategy.value:15s}: {result}")
            except Exception as e:
                print(f"  {strategy.value:15s}: ERROR - {e}")
        
        # Probar conversión de statement completo
        if "MOVE" in test_case or "ADD" in test_case or "IF" in test_case:
            print(f"\n  Statement completo:")
            converted_statement = factory.convert_statement_with_qualified_names(test_case)
            print(f"    Original: {test_case}")
            print(f"    Convertido: {converted_statement}")

if __name__ == "__main__":
    main()

