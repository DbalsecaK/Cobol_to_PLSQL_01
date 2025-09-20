#!/usr/bin/env python3
"""
ENHANCED IF/EVALUATE CONVERTER - Conversor mejorado de IF y EVALUATE statements

Basado en el catálogo de variaciones IF/EVALUATE de COBOL y siguiendo principios SOLID.
Este módulo maneja todas las variaciones identificadas en el catálogo de referencia.

PRINCIPIOS SOLID APLICADOS:
- Single Responsibility: Cada clase/método tiene una responsabilidad específica
- Open/Closed: Extensible para nuevos patrones sin modificar código existente  
- Liskov Substitution: Conversores intercambiables
- Interface Segregation: Interfaces específicas por tipo de statement
- Dependency Inversion: Abstracción de patrones de conversión
"""

import re
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

class IfEvaluatePattern:
    """Clase de datos para patrones de IF/EVALUATE"""
    def __init__(self, pattern_type: str, regex: str, description: str):
        self.pattern_type = pattern_type
        self.regex = regex
        self.description = description

class IStatementConverter(ABC):
    """Interface para conversores de statements - Interface Segregation Principle"""
    
    @abstractmethod
    def convert(self, raw_content: str, details: Dict[str, Any] = None) -> str:
        """Convertir statement a PL/SQL"""
        pass
    
    @abstractmethod
    def can_handle(self, raw_content: str) -> bool:
        """Verificar si puede manejar este statement"""
        pass

class IConditionParser(ABC):
    """Interface para parseadores de condiciones"""
    
    @abstractmethod
    def parse_condition(self, condition: str) -> Dict[str, Any]:
        """Parsear condición COBOL a estructura"""
        pass

class CobolConditionParser(IConditionParser):
    """Parser de condiciones COBOL basado en el catálogo de variaciones"""
    
    def __init__(self):
        # Patrones de condiciones relacionales (1.8)
        self.relational_patterns = {
            'EQUAL': [r'=', r'EQUAL\s+TO', r'IS\s+EQUAL\s+TO'],
            'NOT_EQUAL': [r'<>', r'NOT\s*=', r'NOT\s+EQUAL\s+TO', r'IS\s+NOT\s+EQUAL\s+TO'],
            'GREATER': [r'>', r'GREATER\s+THAN', r'IS\s+GREATER\s+THAN'],
            'GREATER_EQUAL': [r'>=', r'GREATER\s+THAN\s+OR\s+EQUAL\s+TO', r'IS\s+GREATER\s+THAN\s+OR\s+EQUAL\s+TO'],
            'LESS': [r'<', r'LESS\s+THAN', r'IS\s+LESS\s+THAN'],
            'LESS_EQUAL': [r'<=', r'LESS\s+THAN\s+OR\s+EQUAL\s+TO', r'IS\s+LESS\s+THAN\s+OR\s+EQUAL\s+TO']
        }
        
        # Patrones de condiciones de clase (1.10)
        self.class_patterns = {
            'NUMERIC': r'IS\s+(NOT\s+)?NUMERIC',
            'ALPHABETIC': r'IS\s+(NOT\s+)?ALPHABETIC',
            'ALPHABETIC_LOWER': r'IS\s+(NOT\s+)?ALPHABETIC-LOWER',
            'ALPHABETIC_UPPER': r'IS\s+(NOT\s+)?ALPHABETIC-UPPER'
        }
        
        # Patrones de condiciones de signo (1.11)
        self.sign_patterns = {
            'POSITIVE': r'IS\s+(NOT\s+)?POSITIVE',
            'NEGATIVE': r'IS\s+(NOT\s+)?NEGATIVE', 
            'ZERO': r'IS\s+(NOT\s+)?ZERO'
        }
    
    def parse_condition(self, condition: str) -> Dict[str, Any]:
        """Parsear condición COBOL completa"""
        condition = condition.strip()
        
        # Detectar condiciones abreviadas (1.9)
        if self._is_abbreviated_condition(condition):
            return self._parse_abbreviated_condition(condition)
        
        # Detectar condiciones de clase (1.10)
        class_result = self._parse_class_condition(condition)
        if class_result:
            return class_result
        
        # Detectar condiciones de signo (1.11)
        sign_result = self._parse_sign_condition(condition)
        if sign_result:
            return sign_result
        
        # Detectar condiciones relacionales (1.8)
        relational_result = self._parse_relational_condition(condition)
        if relational_result:
            return relational_result
        
        # Detectar nombres-condición (nivel 88) (1.12)
        if self._is_condition_name(condition):
            return {
                'type': 'condition_name',
                'condition_name': condition,
                'raw': condition
            }
        
        # Condición compleja con AND/OR (1.14)
        if re.search(r'\b(AND|OR)\b', condition, re.IGNORECASE):
            return self._parse_complex_condition(condition)
        
        # Condición genérica
        return {
            'type': 'generic',
            'condition': condition,
            'raw': condition
        }
    
    def _is_abbreviated_condition(self, condition: str) -> bool:
        """Detectar condiciones abreviadas (1.9)"""
        # A = B OR = C, A NOT = B OR = C, etc.
        abbreviated_patterns = [
            r'\w+\s*=\s*\w+\s+(OR|AND)\s*=\s*\w+',
            r'\w+\s*(NOT\s*)?[<>=]+\s*\w+\s+(OR|AND)\s*[<>=]+\s*\w+',
        ]
        return any(re.search(pattern, condition, re.IGNORECASE) for pattern in abbreviated_patterns)
    
    def _parse_abbreviated_condition(self, condition: str) -> Dict[str, Any]:
        """Parsear condiciones abreviadas (1.9)"""
        # Ejemplo: A = B OR = C -> (A = B) OR (A = C)
        match = re.match(r'(\w+)\s*([<>=!]+)\s*(\w+)\s+(OR|AND)\s*([<>=!]+)\s*(\w+)', condition, re.IGNORECASE)
        if match:
            subject = match.group(1)
            op1 = match.group(2)
            value1 = match.group(3)
            logical_op = match.group(4).upper()
            op2 = match.group(5)
            value2 = match.group(6)
            
            return {
                'type': 'abbreviated',
                'subject': subject,
                'operator1': op1,
                'value1': value1,
                'logical_operator': logical_op,
                'operator2': op2,
                'value2': value2,
                'raw': condition
            }
        
        return None
    
    def _parse_class_condition(self, condition: str) -> Optional[Dict[str, Any]]:
        """Parsear condiciones de clase (1.10)"""
        for class_type, pattern in self.class_patterns.items():
            match = re.search(r'(\w+)\s+' + pattern, condition, re.IGNORECASE)
            if match:
                variable = match.group(1)
                is_not = match.group(2) is not None if match.lastindex >= 2 else False
                return {
                    'type': 'class',
                    'variable': variable,
                    'class_type': class_type,
                    'is_not': is_not,
                    'raw': condition
                }
        return None
    
    def _parse_sign_condition(self, condition: str) -> Optional[Dict[str, Any]]:
        """Parsear condiciones de signo (1.11)"""
        for sign_type, pattern in self.sign_patterns.items():
            match = re.search(r'(\w+)\s+' + pattern, condition, re.IGNORECASE)
            if match:
                variable = match.group(1)
                is_not = match.group(2) is not None if match.lastindex >= 2 else False
                return {
                    'type': 'sign',
                    'variable': variable,
                    'sign_type': sign_type,
                    'is_not': is_not,
                    'raw': condition
                }
        return None
    
    def _parse_relational_condition(self, condition: str) -> Optional[Dict[str, Any]]:
        """Parsear condiciones relacionales (1.8)"""
        # Patrón general: variable operador valor
        for op_type, patterns in self.relational_patterns.items():
            for pattern in patterns:
                match = re.search(rf'(\w+(?:\s+OF\s+\w+)*)\s+{pattern}\s+(.+)', condition, re.IGNORECASE)
                if match:
                    left_operand = match.group(1).strip()
                    right_operand = match.group(2).strip()
                    return {
                        'type': 'relational',
                        'left_operand': left_operand,
                        'operator': op_type,
                        'right_operand': right_operand,
                        'raw': condition
                    }
        return None
    
    def _is_condition_name(self, condition: str) -> bool:
        """Verificar si es un nombre-condición (nivel 88) (1.12)"""
        # Nombres-condición son identificadores simples sin operadores
        return re.match(r'^[A-Z][A-Z0-9\-]*$', condition.strip(), re.IGNORECASE) is not None
    
    def _parse_complex_condition(self, condition: str) -> Dict[str, Any]:
        """Parsear condiciones complejas con AND/OR (1.14)"""
        # Simplificado: dividir por AND/OR principales
        logical_operators = re.findall(r'\b(AND|OR)\b', condition, re.IGNORECASE)
        parts = re.split(r'\b(?:AND|OR)\b', condition, flags=re.IGNORECASE)
        
        return {
            'type': 'complex',
            'parts': [part.strip() for part in parts],
            'operators': [op.upper() for op in logical_operators],
            'raw': condition
        }

class EnhancedIfConverter(IStatementConverter):
    """Conversor mejorado de IF statements basado en el catálogo de variaciones"""
    
    def __init__(self):
        self.condition_parser = CobolConditionParser()
        
        # Patrones de IF basados en el catálogo (Sección 1)
        self.if_patterns = [
            IfEvaluatePattern('simple_imperative', r'IF\s+(.+?)\s+(.+?)\.', 'IF simple con acción imperativa (1.1)'),
            IfEvaluatePattern('simple_with_end', r'IF\s+(.+?)\s+(.*?)\s+END-IF', 'IF con END-IF (1.2)'),
            IfEvaluatePattern('if_else_end', r'IF\s+(.+?)\s+(.*?)\s+ELSE\s+(.*?)\s+END-IF', 'IF...ELSE...END-IF (1.3)'),
            IfEvaluatePattern('nested_if', r'IF\s+(.+?)\s+IF\s+(.+)', 'IF anidados (1.5)'),
            IfEvaluatePattern('if_continue', r'IF\s+(.+?)\s+CONTINUE', 'IF con CONTINUE (1.6)'),
            IfEvaluatePattern('if_next_sentence', r'IF\s+(.+?)\s+NEXT\s+SENTENCE', 'IF con NEXT SENTENCE (1.7)'),
            IfEvaluatePattern('simple_condition', r'IF\s+(.+)', 'Condición simple (genérico)')
        ]
    
    def can_handle(self, raw_content: str) -> bool:
        """Verificar si puede manejar este statement"""
        return raw_content.strip().upper().startswith('IF ')
    
    def convert(self, raw_content: str, details: Dict[str, Any] = None) -> str:
        """Convertir IF statement a PL/SQL"""
        try:
            # Determinar tipo de IF
            if_info = self._parse_if_statement(raw_content)
            
            # Strategy Pattern: seleccionar conversor apropiado
            if if_info['pattern_type'] == 'simple_imperative':
                return self._convert_simple_imperative(if_info)
            elif if_info['pattern_type'] == 'simple_with_end':
                return self._convert_simple_with_end(if_info)
            elif if_info['pattern_type'] == 'if_else_end':
                return self._convert_if_else_end(if_info)
            elif if_info['pattern_type'] == 'nested_if':
                return self._convert_nested_if(if_info)
            elif if_info['pattern_type'] == 'if_continue':
                return self._convert_if_continue(if_info)
            elif if_info['pattern_type'] == 'if_next_sentence':
                return self._convert_if_next_sentence(if_info)
            else:
                return self._convert_generic_if(if_info)
                
        except Exception as e:
            return f"  -- GAP -- {raw_content} -- (IF statement - enhanced conversion error: {e})"
    
    def _parse_if_statement(self, raw_content: str) -> Dict[str, Any]:
        """Parsear IF statement para determinar patrón"""
        clean_content = raw_content.strip()
        
        # Buscar patrón que coincida
        for pattern in self.if_patterns:
            match = re.search(pattern.regex, clean_content, re.IGNORECASE | re.DOTALL)
            if match:
                condition_text = match.group(1) if match.lastindex >= 1 else ""
                condition_info = self.condition_parser.parse_condition(condition_text)
                
                return {
                    'pattern_type': pattern.pattern_type,
                    'raw': clean_content,
                    'condition': condition_info,
                    'match': match,
                    'description': pattern.description
                }
        
        # Patrón genérico
        condition_match = re.search(r'IF\s+(.+)', clean_content, re.IGNORECASE)
        condition_text = condition_match.group(1) if condition_match else ""
        condition_info = self.condition_parser.parse_condition(condition_text)
        
        return {
            'pattern_type': 'simple_condition',
            'raw': clean_content,
            'condition': condition_info,
            'match': condition_match,
            'description': 'Condición simple (genérico)'
        }
    
    def _convert_simple_imperative(self, if_info: Dict[str, Any]) -> str:
        """Convertir IF simple con acción imperativa (1.1)"""
        match = if_info['match']
        condition = match.group(1)
        action = match.group(2)
        
        plsql_condition = self._convert_condition_to_plsql(if_info['condition'])
        plsql_action = self._convert_action_to_plsql(action)
        
        return f"  IF {plsql_condition} THEN\n    {plsql_action};\n  END IF;"
    
    def _convert_simple_with_end(self, if_info: Dict[str, Any]) -> str:
        """Convertir IF con END-IF (1.2)"""
        match = if_info['match']
        condition = match.group(1)
        action = match.group(2) if match.lastindex >= 2 else ""
        
        plsql_condition = self._convert_condition_to_plsql(if_info['condition'])
        plsql_action = self._convert_action_to_plsql(action) if action.strip() else "NULL"
        
        return f"  IF {plsql_condition} THEN\n    {plsql_action};\n  END IF;"
    
    def _convert_if_else_end(self, if_info: Dict[str, Any]) -> str:
        """Convertir IF...ELSE...END-IF (1.3)"""
        match = if_info['match']
        condition = match.group(1)
        then_action = match.group(2)
        else_action = match.group(3)
        
        plsql_condition = self._convert_condition_to_plsql(if_info['condition'])
        plsql_then = self._convert_action_to_plsql(then_action)
        plsql_else = self._convert_action_to_plsql(else_action)
        
        return f"""  IF {plsql_condition} THEN
    {plsql_then};
  ELSE
    {plsql_else};
  END IF;"""
    
    def _convert_nested_if(self, if_info: Dict[str, Any]) -> str:
        """Convertir IF anidados (1.5)"""
        # Para IFs anidados, usar conversión genérica por ahora
        return self._convert_generic_if(if_info)
    
    def _convert_if_continue(self, if_info: Dict[str, Any]) -> str:
        """Convertir IF con CONTINUE (1.6)"""
        condition = if_info['match'].group(1)
        plsql_condition = self._convert_condition_to_plsql(if_info['condition'])
        
        return f"  IF {plsql_condition} THEN\n    NULL; -- CONTINUE\n  END IF;"
    
    def _convert_if_next_sentence(self, if_info: Dict[str, Any]) -> str:
        """Convertir IF con NEXT SENTENCE (1.7)"""
        condition = if_info['match'].group(1)
        plsql_condition = self._convert_condition_to_plsql(if_info['condition'])
        
        return f"  IF {plsql_condition} THEN\n    GOTO next_sentence; -- NEXT SENTENCE\n  END IF;"
    
    def _convert_generic_if(self, if_info: Dict[str, Any]) -> str:
        """Convertir IF genérico"""
        plsql_condition = self._convert_condition_to_plsql(if_info['condition'])
        return f"  IF {plsql_condition} THEN\n    NULL; -- Acción pendiente\n  END IF;"
    
    def _convert_condition_to_plsql(self, condition_info: Dict[str, Any]) -> str:
        """Convertir condición COBOL a PL/SQL"""
        if condition_info['type'] == 'relational':
            return self._convert_relational_condition(condition_info)
        elif condition_info['type'] == 'class':
            return self._convert_class_condition(condition_info)
        elif condition_info['type'] == 'sign':
            return self._convert_sign_condition(condition_info)
        elif condition_info['type'] == 'condition_name':
            return self._convert_condition_name(condition_info)
        elif condition_info['type'] == 'abbreviated':
            return self._convert_abbreviated_condition(condition_info)
        elif condition_info['type'] == 'complex':
            return self._convert_complex_condition(condition_info)
        else:
            # Condición genérica
            return self._clean_cobol_condition(condition_info.get('condition', condition_info.get('raw', '')))
    
    def _convert_relational_condition(self, condition_info: Dict[str, Any]) -> str:
        """Convertir condición relacional"""
        left = self._clean_identifier(condition_info['left_operand'])
        right = self._clean_identifier(condition_info['right_operand'])
        
        # Mapeo de operadores COBOL a PL/SQL
        operator_map = {
            'EQUAL': '=',
            'NOT_EQUAL': '<>',
            'GREATER': '>',
            'GREATER_EQUAL': '>=',
            'LESS': '<',
            'LESS_EQUAL': '<='
        }
        
        op = operator_map.get(condition_info['operator'], '=')
        return f"{left} {op} {right}"
    
    def _convert_class_condition(self, condition_info: Dict[str, Any]) -> str:
        """Convertir condición de clase"""
        variable = self._clean_identifier(condition_info['variable'])
        class_type = condition_info['class_type']
        is_not = condition_info['is_not']
        not_prefix = 'NOT ' if is_not else ''
        
        if class_type == 'NUMERIC':
            return f"{not_prefix}REGEXP_LIKE({variable}, '^[0-9]+$')"
        elif class_type == 'ALPHABETIC':
            return f"{not_prefix}REGEXP_LIKE({variable}, '^[A-Za-z]+$')"
        elif class_type == 'ALPHABETIC_LOWER':
            return f"{not_prefix}REGEXP_LIKE({variable}, '^[a-z]+$')"
        elif class_type == 'ALPHABETIC_UPPER':
            return f"{not_prefix}REGEXP_LIKE({variable}, '^[A-Z]+$')"
        else:
            return f"{not_prefix}({variable} IS OF CLASS {class_type})"
    
    def _convert_sign_condition(self, condition_info: Dict[str, Any]) -> str:
        """Convertir condición de signo"""
        variable = self._clean_identifier(condition_info['variable'])
        sign_type = condition_info['sign_type']
        is_not = condition_info['is_not']
        not_prefix = 'NOT ' if is_not else ''
        
        if sign_type == 'POSITIVE':
            return f"{not_prefix}({variable} > 0)"
        elif sign_type == 'NEGATIVE':
            return f"{not_prefix}({variable} < 0)"
        elif sign_type == 'ZERO':
            return f"{not_prefix}({variable} = 0)"
        else:
            return f"{not_prefix}({variable} IS {sign_type})"
    
    def _convert_condition_name(self, condition_info: Dict[str, Any]) -> str:
        """Convertir nombre-condición (nivel 88)"""
        condition_name = self._clean_identifier(condition_info['condition_name'])
        return f"{condition_name} = TRUE"
    
    def _convert_abbreviated_condition(self, condition_info: Dict[str, Any]) -> str:
        """Convertir condición abreviada (1.9)"""
        subject = self._clean_identifier(condition_info['subject'])
        op1 = condition_info['operator1']
        value1 = self._clean_identifier(condition_info['value1'])
        logical_op = condition_info['logical_operator']
        op2 = condition_info['operator2']
        value2 = self._clean_identifier(condition_info['value2'])
        
        # Expandir condición abreviada: A = B OR = C -> (A = B) OR (A = C)
        return f"({subject} {op1} {value1}) {logical_op} ({subject} {op2} {value2})"
    
    def _convert_complex_condition(self, condition_info: Dict[str, Any]) -> str:
        """Convertir condición compleja con AND/OR"""
        parts = condition_info['parts']
        operators = condition_info['operators']
        
        # Convertir cada parte individualmente
        converted_parts = []
        for part in parts:
            part_info = self.condition_parser.parse_condition(part)
            converted_part = self._convert_condition_to_plsql(part_info)
            converted_parts.append(f"({converted_part})")
        
        # Combinar con operadores
        result = converted_parts[0] if converted_parts else ""
        for i, op in enumerate(operators):
            if i + 1 < len(converted_parts):
                result += f" {op} {converted_parts[i + 1]}"
        
        return result
    
    def _convert_action_to_plsql(self, action: str) -> str:
        """Convertir acción COBOL a PL/SQL"""
        action = action.strip()
        if not action:
            return "NULL"
        
        # Conversiones básicas de acciones comunes
        if action.upper().startswith('PERFORM'):
            proc_name = re.search(r'PERFORM\s+([A-Z0-9\-]+)', action.upper())
            if proc_name:
                return f"{self._clean_identifier(proc_name.group(1))}()"
        elif action.upper().startswith('MOVE'):
            return f"{action.lower()}" # Simplificado por ahora
        elif action.upper().startswith('GO TO'):
            label = re.search(r'GO\s+TO\s+([A-Z0-9\-]+)', action.upper())
            if label:
                return f"GOTO {self._clean_identifier(label.group(1))}"
        
        return f"-- {action}"
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador COBOL para PL/SQL"""
        if not identifier:
            return identifier
        
        # Remover comillas y espacios extra
        clean_id = identifier.strip().strip("'\"")
        
        # Convertir guiones a guiones bajos
        clean_id = clean_id.replace('-', '_')
        
        # Manejar referencias cualificadas (OF)
        if ' OF ' in clean_id.upper():
            parts = re.split(r'\s+OF\s+', clean_id, flags=re.IGNORECASE)
            if len(parts) == 2:
                return f"{parts[1].lower()}.{parts[0].lower()}"
        
        return clean_id.lower()
    
    def _clean_cobol_condition(self, condition: str) -> str:
        """Limpiar condición COBOL genérica"""
        # Reemplazos básicos
        condition = condition.replace('-', '_')
        condition = re.sub(r'\s+', ' ', condition)
        return condition.strip()

class EvaluateConverter(IStatementConverter):
    """Conversor de EVALUATE statements basado en el catálogo (Sección 2)"""
    
    def __init__(self):
        self.condition_parser = CobolConditionParser()
    
    def can_handle(self, raw_content: str) -> bool:
        """Verificar si puede manejar este statement"""
        return raw_content.strip().upper().startswith('EVALUATE ')
    
    def convert(self, raw_content: str, details: Dict[str, Any] = None) -> str:
        """Convertir EVALUATE statement a PL/SQL"""
        try:
            evaluate_info = self._parse_evaluate_statement(raw_content)
            
            if evaluate_info['type'] == 'simple':
                return self._convert_simple_evaluate(evaluate_info)
            elif evaluate_info['type'] == 'with_ranges':
                return self._convert_evaluate_with_ranges(evaluate_info)
            elif evaluate_info['type'] == 'evaluate_true':
                return self._convert_evaluate_true(evaluate_info)
            elif evaluate_info['type'] == 'multiple_subjects':
                return self._convert_multiple_subjects_evaluate(evaluate_info)
            else:
                return self._convert_generic_evaluate(evaluate_info)
                
        except Exception as e:
            return f"  -- GAP -- {raw_content} -- (EVALUATE statement - conversion error: {e})"
    
    def _parse_evaluate_statement(self, raw_content: str) -> Dict[str, Any]:
        """Parsear EVALUATE statement"""
        # Simplificado: detectar tipo básico
        if 'THRU' in raw_content.upper() or 'THROUGH' in raw_content.upper():
            return {'type': 'with_ranges', 'raw': raw_content}
        elif 'EVALUATE TRUE' in raw_content.upper():
            return {'type': 'evaluate_true', 'raw': raw_content}
        elif 'ALSO' in raw_content.upper():
            return {'type': 'multiple_subjects', 'raw': raw_content}
        else:
            return {'type': 'simple', 'raw': raw_content}
    
    def _convert_simple_evaluate(self, evaluate_info: Dict[str, Any]) -> str:
        """Convertir EVALUATE simple (2.1)"""
        return f"  -- GAP -- {evaluate_info['raw']} -- (EVALUATE simple - pending implementation)"
    
    def _convert_evaluate_with_ranges(self, evaluate_info: Dict[str, Any]) -> str:
        """Convertir EVALUATE con rangos (2.2)"""
        return f"  -- GAP -- {evaluate_info['raw']} -- (EVALUATE with ranges - pending implementation)"
    
    def _convert_evaluate_true(self, evaluate_info: Dict[str, Any]) -> str:
        """Convertir EVALUATE TRUE (2.3)"""
        return f"  -- GAP -- {evaluate_info['raw']} -- (EVALUATE TRUE - pending implementation)"
    
    def _convert_multiple_subjects_evaluate(self, evaluate_info: Dict[str, Any]) -> str:
        """Convertir EVALUATE con múltiples sujetos (2.4)"""
        return f"  -- GAP -- {evaluate_info['raw']} -- (EVALUATE multiple subjects - pending implementation)"
    
    def _convert_generic_evaluate(self, evaluate_info: Dict[str, Any]) -> str:
        """Convertir EVALUATE genérico"""
        return f"  -- GAP -- {evaluate_info['raw']} -- (EVALUATE generic - pending implementation)"

class IfEvaluateConverterFactory:
    """Factory para crear conversores apropiados - Dependency Inversion Principle"""
    
    def __init__(self):
        self.converters = [
            EnhancedIfConverter(),
            EvaluateConverter()
        ]
    
    def get_converter(self, raw_content: str) -> Optional[IStatementConverter]:
        """Obtener conversor apropiado para el statement"""
        for converter in self.converters:
            if converter.can_handle(raw_content):
                return converter
        return None
    
    def convert_statement(self, raw_content: str, details: Dict[str, Any] = None) -> str:
        """Convertir statement usando el conversor apropiado"""
        converter = self.get_converter(raw_content)
        if converter:
            return converter.convert(raw_content, details)
        else:
            return f"  -- GAP -- {raw_content} -- (No suitable converter found)"

# Ejemplo de uso
def main():
    """Función de prueba"""
    factory = IfEvaluateConverterFactory()
    
    # Ejemplos de IF statements del catálogo
    test_cases = [
        "IF X = 1 MOVE 'A' TO Y.",  # 1.1
        "IF X = 1 MOVE 'A' TO Y END-IF.",  # 1.2
        "IF A > 0 PERFORM P1 ELSE PERFORM P2 END-IF.",  # 1.3
        "IF FLAG-OK CONTINUE ELSE PERFORM HANDLE-ERROR END-IF.",  # 1.6
        "IF ERROR-FLAG NEXT SENTENCE ELSE PERFORM PROCESS END-IF.",  # 1.7
        "IF A = B OR = C PERFORM CASE-AC END-IF.",  # 1.9
        "IF Var IS NUMERIC PERFORM NUMERIC-PROC END-IF.",  # 1.10
        "IF Amt IS POSITIVE PERFORM CREDIT-PROC END-IF.",  # 1.11
        "IF OK PERFORM CONTINUE-FLOW END-IF.",  # 1.12
        "EVALUATE OPC WHEN 1 PERFORM CASE-1 WHEN OTHER PERFORM DEFAULT-CASE END-EVALUATE.",  # 2.1
        "EVALUATE TRUE WHEN X > 0 AND Y > 0 PERFORM QUADRANT-1 WHEN OTHER PERFORM DEFAULT END-EVALUATE."  # 2.3
    ]
    
    print("🧪 PRUEBAS DEL CONVERSOR MEJORADO IF/EVALUATE")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: {test_case}")
        result = factory.convert_statement(test_case)
        print(f"🔄 Resultado:\n{result}")
        print("-" * 40)

if __name__ == "__main__":
    main()

