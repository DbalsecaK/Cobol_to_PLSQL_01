"""
COBOL Condition Parser - Módulo independiente para manejar condiciones COBOL complejas
Maneja condiciones con múltiples valores OR/AND sin afectar el código principal
"""

import re
from typing import Dict, List, Optional, Any


class CobolConditionParser:
    """Parser especializado para condiciones COBOL complejas"""
    
    def __init__(self):
        self.operator_map = {
            'EQUAL': '=',
            '=': '=',
            'NOT EQUAL': '!=',
            'NOT =': '!=',
            'GREATER': '>',
            '>': '>',
            'LESS': '<',
            '<': '<',
            'GREATER OR EQUAL': '>=',
            '>=': '>=',
            'LESS OR EQUAL': '<=',
            '<=': '<='
        }
    
    def clean_expression(self, expression: str) -> str:
        """Clean COBOL expression to PL/SQL format"""
        if not expression:
            return ""
        
        # Convert hyphens to underscores
        expression = expression.replace('-', '_')
        
        # Handle qualified names (OF)
        if ' OF ' in expression.upper():
            parts = expression.split(' OF ')
            if len(parts) == 2:
                field = parts[0].strip().replace('-', '_')
                group = parts[1].strip().replace('-', '_')
                return f"{group}.{field}"
        
        # Handle subscripted variables
        if '(' in expression and ')' in expression:
            match = re.match(r'^([A-Z0-9_-]+)\(([A-Z0-9_-]+)\)', expression, re.IGNORECASE)
            if match:
                var_name = match.group(1).replace('-', '_')
                index = match.group(2).replace('-', '_')
                return f"{var_name}({index})"
        
        return expression.replace('-', '_')
    
    def parse_multiple_or_condition(self, condition: str) -> str:
        """
        Parse COBOL condition with multiple OR values
        Example: 'C' OR 'D' OR 'F' OR 'G' -> 'C' OR 'D' OR 'F' OR 'G'
        """
        condition = condition.strip()
        
        # Split by OR to get individual values
        or_parts = [part.strip() for part in condition.split(' OR ')]
        
        if len(or_parts) <= 1:
            return condition
        
        # Clean each part
        cleaned_parts = []
        for part in or_parts:
            cleaned_part = self.clean_expression(part)
            cleaned_parts.append(cleaned_part)
        
        return ' OR '.join(cleaned_parts)
    
    def parse_equality_with_multiple_values(self, condition: str) -> str:
        """
        Parse COBOL equality condition with multiple values
        Example: VAR EQUAL 'C' OR 'D' OR 'F' OR 'G' 
        -> VAR = 'C' OR VAR = 'D' OR VAR = 'F' OR VAR = 'G'
        """
        condition = condition.strip()
        
        # Pattern to match: VARIABLE EQUAL value OR value OR value...
        equality_patterns = [
            r'^([A-Z0-9_-]+(?:\s+OF\s+[A-Z0-9_-]+)?)\s+(EQUAL|NOT\s+EQUAL|=|!=)\s+(.+)$',
            r'^([A-Z0-9_-]+(?:\s+OF\s+[A-Z0-9_-]+)?)\s+(GREATER|LESS|>|<)\s+(.+)$'
        ]
        
        for pattern in equality_patterns:
            match = re.match(pattern, condition, re.IGNORECASE)
            if match:
                variable = match.group(1).strip()
                operator = match.group(2).strip()
                values_part = match.group(3).strip()
                
                # Clean variable name
                variable_clean = self.clean_expression(variable)
                
                # Get PL/SQL operator
                plsql_operator = self.operator_map.get(operator.upper(), operator)
                
                # Parse multiple values
                if ' OR ' in values_part.upper():
                    # Multiple values with OR
                    values = [v.strip() for v in values_part.split(' OR ')]
                    conditions = []
                    for value in values:
                        value_clean = self.clean_expression(value)
                        conditions.append(f"{variable_clean} {plsql_operator} {value_clean}")
                    return f"({' OR '.join(conditions)})"
                else:
                    # Single value
                    value_clean = self.clean_expression(values_part)
                    return f"{variable_clean} {plsql_operator} {value_clean}"
        
        return condition
    
    def parse_complex_condition(self, condition: str) -> str:
        """
        Parse complex COBOL condition with multiple OR/AND values
        Main entry point for complex condition parsing
        """
        condition = condition.strip()
        
        # First try to parse equality with multiple values
        result = self.parse_equality_with_multiple_values(condition)
        if result != condition:
            return result
        
        # If not an equality condition, try multiple OR parsing
        result = self.parse_multiple_or_condition(condition)
        if result != condition:
            return result
        
        # If no special parsing needed, return cleaned condition
        return self.clean_expression(condition)
    
    def detect_complex_condition(self, condition: str) -> bool:
        """
        Detect if a condition needs complex parsing
        Returns True if the condition has multiple OR/AND values
        """
        condition = condition.strip().upper()
        
        # Check for multiple OR values (like 'C' OR 'D' OR 'F' OR 'G')
        or_count = condition.count(' OR ')
        if or_count > 1:
            return True
        
        # Check for equality with multiple values
        if ('EQUAL' in condition or '=' in condition) and or_count > 0:
            return True
        
        return False


# Test function to verify the parser works correctly
def test_cobol_condition_parser():
    """Test the COBOL condition parser"""
    parser = CobolConditionParser()
    
    test_cases = [
        {
            'input': "COD-TIPO-SEGURO OF T10PSE65 EQUAL 'C' OR 'D' OR 'F' OR 'G'",
            'expected': "T10PSE65.COD_TIPO_SEGURO = 'C' OR T10PSE65.COD_TIPO_SEGURO = 'D' OR T10PSE65.COD_TIPO_SEGURO = 'F' OR T10PSE65.COD_TIPO_SEGURO = 'G'"
        },
        {
            'input': "WS-VAR EQUAL 'A' OR 'B'",
            'expected': "WS_VAR = 'A' OR WS_VAR = 'B'"
        },
        {
            'input': "WS-COUNT GREATER 0",
            'expected': "WS_COUNT > 0"
        }
    ]
    
    print("Testing COBOL Condition Parser:")
    for i, test in enumerate(test_cases, 1):
        result = parser.parse_complex_condition(test['input'])
        status = "✅ PASS" if result == test['expected'] else "❌ FAIL"
        print(f"Test {i}: {status}")
        print(f"  Input:    {test['input']}")
        print(f"  Expected: {test['expected']}")
        print(f"  Got:      {result}")
        print()


if __name__ == "__main__":
    test_cobol_condition_parser()
