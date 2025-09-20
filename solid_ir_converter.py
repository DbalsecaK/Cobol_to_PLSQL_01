#!/usr/bin/env python3
"""
SOLID IR Converter - Conversor IR a PL/SQL con principios SOLID
Arquitectura modular con convertidores independientes por sentencia

PRINCIPIOS SOLID APLICADOS:
- S: Single Responsibility - Cada clase tiene una responsabilidad específica
- O: Open/Closed - Extensible mediante nuevos convertidores
- L: Liskov Substitution - Los convertidores implementan interfaces comunes
- I: Interface Segregation - Interfaces específicas para cada tipo de conversión
- D: Dependency Inversion - Depende de abstracciones, no de implementaciones

Uso: python solid_ir_converter.py archivo_ir.json
"""

import sys
import os
import json
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# ===== INTERFACES ABSTRACTAS (ISP - Interface Segregation Principle) =====

class IStatementConverter(ABC):
    """Interface para convertidores de statements específicos"""
    
    @abstractmethod
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si puede convertir este statement"""
        pass
    
    @abstractmethod
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir statement a PL/SQL"""
        pass

class IContextProvider(ABC):
    """Interface para proveedores de contexto"""
    
    @abstractmethod
    def get_variables(self) -> List[Dict[str, Any]]:
        """Obtener variables disponibles"""
        pass
    
    @abstractmethod
    def get_procedures(self) -> List[Dict[str, Any]]:
        """Obtener procedimientos disponibles"""
        pass

# ===== CONVERTIDORES ESPECÍFICOS (SRP - Single Responsibility Principle) =====

class MoveStatementConverter(IStatementConverter):
    """Convertidor específico para sentencias MOVE (SRP) - HOMOLOGADO"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una sentencia MOVE"""
        raw = statement.get("raw", "").strip().upper()
        return raw.startswith("MOVE")
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir MOVE a PL/SQL con todas las variaciones del conversor anterior"""
        raw = statement.get("raw", "").strip()
        
        # Parsear la sentencia MOVE
        move_info = self._parse_move_statement(raw)
        
        if not move_info:
            return f"    -- GAP -- {raw} -- (MOVE statement - parsing failed)"
        
        # Aplicar conversión según el tipo
        try:
            if move_info["type"] == "simple":
                return self._convert_move_simple(move_info, raw)
            elif move_info["type"] == "special_values":
                return self._convert_move_special_values(move_info, raw)
            elif move_info["type"] == "qualified_source":
                return self._convert_move_qualified_source(move_info, raw)
            elif move_info["type"] == "qualified_target":
                return self._convert_move_qualified_target(move_info, raw)
            elif move_info["type"] == "qualified_to_qualified":
                return self._convert_move_qualified_to_qualified(move_info, raw)
            elif move_info["type"] == "array_element":
                return self._convert_move_array_element(move_info, raw)
            elif move_info["type"] == "substring":
                return self._convert_move_substring(move_info, raw)
            elif move_info["type"] == "corresponding":
                return self._convert_move_corresponding(move_info, raw)
            else:
                return self._convert_move_generic(move_info, raw)
        except Exception as e:
            return f"    -- GAP -- {raw} -- (MOVE statement - conversion error: {e})"
    
    def _parse_move_statement(self, raw_content: str) -> Dict[str, Any]:
        """Parsear sentencia MOVE para extraer componentes"""
        line = raw_content.strip()
        
        # Patrones para diferentes tipos de MOVE (orden importa - más específicos primero)
        patterns = {
            "corresponding": r"MOVE\s+CORRESPONDING\s+(.+?)\s+TO\s+(.+?)(?:\.|$)",
            "qualified_to_qualified": r"MOVE\s+(.+?)\s+OF\s+(.+?)\s+TO\s+(.+?)\s+OF\s+(.+?)(?:\.|$)",
            "qualified_source": r"MOVE\s+(.+?)\s+OF\s+(.+?)\s+TO\s+(.+?)(?:\.|$)",
            "qualified_target": r"MOVE\s+(.+?)\s+TO\s+(.+?)\s+OF\s+(.+?)(?:\.|$)",
            "array_element": r"MOVE\s+(.+?)\s*\((.+?)\)\s+TO\s+(.+?)(?:\.|$)",
            "substring": r"MOVE\s+(.+?)\s*\((\d+):(\d+)\)\s+TO\s+(.+?)(?:\.|$)",
            "simple": r"MOVE\s+(.+?)\s+TO\s+(.+?)(?:\.|$)",
        }
        
        # Detectar valores especiales
        special_values = ["ZEROS", "ZERO", "SPACES", "SPACE", "HIGH-VALUES", "LOW-VALUES"]
        
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if pattern_name == "simple":
                    source = match.group(1).strip()
                    target = match.group(2).strip()
                    
                    # Detectar si es valor especial
                    if any(sv in source.upper() for sv in special_values):
                        return {
                            "type": "special_values",
                            "source": source,
                            "target": target,
                            "raw": line
                        }
                    else:
                        return {
                            "type": "simple",
                            "source": source,
                            "target": target,
                            "raw": line
                        }
                elif pattern_name == "corresponding":
                    return {
                        "type": "corresponding",
                        "source": match.group(1).strip(),
                        "target": match.group(2).strip(),
                        "raw": line
                    }
                elif pattern_name == "qualified_source":
                    return {
                        "type": "qualified_source",
                        "source": match.group(1).strip(),
                        "source_qualifier": match.group(2).strip(),
                        "target": match.group(3).strip(),
                        "raw": line
                    }
                elif pattern_name == "qualified_target":
                    return {
                        "type": "qualified_target",
                        "source": match.group(1).strip(),
                        "target": match.group(2).strip(),
                        "target_qualifier": match.group(3).strip(),
                        "raw": line
                    }
                elif pattern_name == "qualified_to_qualified":
                    return {
                        "type": "qualified_to_qualified",
                        "source": match.group(1).strip(),
                        "source_qualifier": match.group(2).strip(),
                        "target": match.group(3).strip(),
                        "target_qualifier": match.group(4).strip(),
                        "raw": line
                    }
                elif pattern_name == "array_element":
                    return {
                        "type": "array_element",
                        "source": match.group(1).strip(),
                        "array_index": match.group(2).strip(),
                        "target": match.group(3).strip(),
                        "raw": line
                    }
                elif pattern_name == "substring":
                    return {
                        "type": "substring",
                        "source": match.group(1).strip(),
                        "start_pos": match.group(2).strip(),
                        "end_pos": match.group(3).strip(),
                        "target": match.group(4).strip(),
                        "raw": line
                    }
        
        # Si no coincide con ningún patrón específico, devolver genérico
        return {
            "type": "generic",
            "raw": line
        }
    
    def _convert_move_simple(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE simple"""
        source = move_info["source"]
        target = move_info["target"]
        
        source_clean = self._clean_identifier(source)
        target_clean = self._clean_identifier(target)
        
        # Detectar si el source es un literal
        if self._is_literal(source_clean):
            converted_source = self._convert_literal(source_clean)
        else:
            converted_source = self._convert_cobol_to_plsql_identifier(source_clean)
        
        converted_target = self._convert_cobol_to_plsql_identifier(target_clean)
        
        return f"    {converted_target} := {converted_source}; -- {raw_content}"
    
    def _convert_move_special_values(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE con valores especiales"""
        source = move_info["source"].upper()
        target = self._convert_cobol_to_plsql_identifier(move_info["target"])
        
        # Mapeo de valores especiales
        special_mappings = {
            "ZEROS": "0",
            "ZERO": "0",
            "SPACES": "NULL",
            "SPACE": "NULL",
            "HIGH-VALUES": "CHR(255)",
            "LOW-VALUES": "CHR(0)"
        }
        
        converted_value = special_mappings.get(source, f"-- GAP: Valor especial no mapeado: {source}")
        
        return f"    {target} := {converted_value}; -- {raw_content}"
    
    def _convert_move_qualified_source(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE con source calificado"""
        source = self._clean_identifier(move_info["source"])
        source_qualifier = self._clean_identifier(move_info["source_qualifier"])
        target = self._clean_identifier(move_info["target"])
        
        return f"    {target} := {source_qualifier}.{source}; -- {raw_content}"
    
    def _convert_move_qualified_target(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE con target calificado"""
        source = self._clean_identifier(move_info["source"])
        target = self._clean_identifier(move_info["target"])
        target_qualifier = self._clean_identifier(move_info["target_qualifier"])
        
        return f"    {target_qualifier}.{target} := {source}; -- {raw_content}"
    
    def _convert_move_qualified_to_qualified(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE calificado a calificado"""
        source = self._clean_identifier(move_info["source"])
        source_qualifier = self._clean_identifier(move_info["source_qualifier"])
        target = self._clean_identifier(move_info["target"])
        target_qualifier = self._clean_identifier(move_info["target_qualifier"])
        
        return f"    {target_qualifier}.{target} := {source_qualifier}.{source}; -- {raw_content}"
    
    def _convert_move_array_element(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE con elemento de array"""
        source = self._clean_identifier(move_info["source"])
        array_index = self._clean_identifier(move_info["array_index"])
        target = self._clean_identifier(move_info["target"])
        
        return f"    {target} := {source}({array_index}); -- {raw_content}"
    
    def _convert_move_substring(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE con substring"""
        source = self._clean_identifier(move_info["source"])
        start_pos = move_info["start_pos"]
        end_pos = move_info["end_pos"]
        target = self._clean_identifier(move_info["target"])
        
        return f"    {target} := SUBSTR({source}, {start_pos}, {end_pos}); -- {raw_content}"
    
    def _convert_move_corresponding(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE CORRESPONDING"""
        source = self._clean_identifier(move_info["source"])
        target = self._clean_identifier(move_info["target"])
        
        return f"    -- MOVE CORRESPONDING {source} TO {target}\n    -- GAP: Implementar lógica de campos correspondientes -- {raw_content}"
    
    def _convert_move_generic(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir MOVE genérico"""
        return f"    -- GAP -- {raw_content} -- (MOVE statement)"
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador para PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()
    
    def _is_literal(self, value: str) -> bool:
        """Verificar si es un literal"""
        return value.startswith("'") or value.startswith('"') or value.isdigit()
    
    def _convert_literal(self, literal: str) -> str:
        """Convertir literal a PL/SQL"""
        if literal.startswith("'") or literal.startswith('"'):
            return literal
        elif literal.isdigit():
            return literal
        else:
            return f"'{literal}'"
    
    def _convert_cobol_to_plsql_identifier(self, identifier: str) -> str:
        """Convertir identificador COBOL a PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()

class IfStatementConverter(IStatementConverter):
    """Convertidor específico para sentencias IF (SRP) - HOMOLOGADO AVANZADO"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una sentencia IF"""
        raw = statement.get("raw", "").strip().upper()
        return raw.startswith("IF")
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir IF a PL/SQL con todas las variaciones avanzadas del conversor anterior"""
        raw = statement.get("raw", "").strip()
        
        # Parsear la sentencia IF
        if_info = self._parse_if_statement(raw)
        
        if not if_info:
            return f"    -- GAP -- {raw} -- (IF statement - parsing failed)"
        
        # Convertir según el tipo
        try:
            if if_info["type"] == "simple":
                return self._convert_if_simple(if_info, raw)
            elif if_info["type"] == "comparison":
                return self._convert_if_simple(if_info, raw)
            elif if_info["type"] == "if_else":
                return self._convert_if_else(if_info, raw)
            elif if_info["type"] == "nested":
                return self._convert_if_nested(if_info, raw)
            elif if_info["type"] == "logical_operators":
                return self._convert_if_logical(if_info, raw)
            elif if_info["type"] == "not_condition":
                return self._convert_if_simple(if_info, raw)
            elif if_info["type"] == "condition_name":
                return self._convert_if_condition_name(if_info, raw)
            elif if_info["type"] == "signed_numeric":
                return self._convert_if_signed_numeric(if_info, raw)
            elif if_info["type"] == "string_comparison":
                return self._convert_if_string_comparison(if_info, raw)
            elif if_info["type"] == "sqlcode_check":
                return self._convert_sqlcode_check(if_info, raw)
            elif if_info["type"] == "boolean_flag":
                return self._convert_boolean_flag(if_info, raw)
            elif if_info["type"] == "qualified_comparison":
                return self._convert_qualified_comparison(if_info, raw)
            elif if_info["type"] == "complex_condition":
                return self._convert_complex_condition(if_info, raw)
            else:
                return self._convert_if_generic(if_info, raw)
        except Exception as e:
            return f"    -- GAP -- {raw} -- (IF statement - conversion error: {e})"
    
    def _parse_if_statement(self, raw_content: str) -> Dict[str, Any]:
        """Parsear sentencia IF para extraer componentes"""
        line = raw_content.strip()
        upper_line = line.upper()
        
        # Patrones para diferentes tipos de IF (orden importa - más específicos primero)
        patterns = {
            "signed_numeric": r"IF\s+(.+?)\s+IS\s+(POSITIVE|NEGATIVE|ZERO)(?:\s|$)",
            "condition_name": r"IF\s+([A-Z][-A-Z0-9]*)\s*(?:$|\.)",
            "string_comparison": r"IF\s+(.+?)\s*\((\d+):(\d+)\)\s*(=|NOT\s*=|>|<|>=|<=)\s*(.+?)(?:\s|$)",
            "logical_operators": r"IF\s+(.+?)\s+(AND|OR)\s+(.+?)(?:\s|$)",
            "not_condition": r"IF\s+NOT\s+(.+?)(?:\s|$)",
            "comparison": r"IF\s+(.+?)\s*(=|NOT\s*=|>|<|>=|<=|EQUAL|GREATER|LESS)\s*(.+?)(?:\s|$)",
            "simple": r"IF\s+(.+?)(?:\s|$)",
        }
        
        # Detectar tipo de IF basado en contenido
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, upper_line, re.IGNORECASE)
            if match:
                return self._build_if_info(pattern_name, match, line)
        
        # Si no coincide con ningún patrón específico, devolver genérico
        return {
            "type": "generic",
            "raw": line
        }
    
    def _build_if_info(self, pattern_name: str, match, line: str) -> Dict[str, Any]:
        """Construir información de IF basada en el patrón"""
        if pattern_name == "signed_numeric":
            return {
                "type": "signed_numeric",
                "variable": match.group(1).strip(),
                "sign_type": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "condition_name":
            return {
                "type": "condition_name",
                "condition_name": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "string_comparison":
            return {
                "type": "string_comparison",
                "variable": match.group(1).strip(),
                "start_pos": match.group(2).strip(),
                "end_pos": match.group(3).strip(),
                "operator": match.group(4).strip(),
                "value": match.group(5).strip(),
                "raw": line
            }
        elif pattern_name == "logical_operators":
            return {
                "type": "logical_operators",
                "left_condition": match.group(1).strip(),
                "logical_op": match.group(2).strip(),
                "right_condition": match.group(3).strip(),
                "raw": line
            }
        elif pattern_name == "not_condition":
            return {
                "type": "not_condition",
                "condition": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "comparison":
            return {
                "type": "comparison",
                "left_operand": match.group(1).strip(),
                "operator": match.group(2).strip(),
                "right_operand": match.group(3).strip(),
                "raw": line
            }
        elif pattern_name == "simple":
            return {
                "type": "simple",
                "condition": match.group(1).strip(),
                "raw": line
            }
        
        return {"type": "generic", "raw": line}
    
    def _convert_if_simple(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF simple"""
        condition = if_info.get("condition", if_info.get("left_operand", ""))
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"    IF {converted_condition} THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}"
    
    def _convert_if_else(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF-ELSE completo"""
        condition = if_info.get("condition", "")
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"    IF {converted_condition} THEN\n        -- GAP: Implementar lógica THEN\n    ELSE\n        -- GAP: Implementar lógica ELSE\n    END IF; -- {raw_content}"
    
    def _convert_if_nested(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF anidado"""
        condition = if_info.get("condition", "")
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"    ELSIF {converted_condition} THEN\n        -- GAP: Implementar lógica ELSIF\n    -- {raw_content}"
    
    def _convert_if_logical(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF con operadores lógicos (AND/OR)"""
        left_condition = self._convert_cobol_condition_to_plsql(if_info["left_condition"])
        logical_op = if_info["logical_op"]
        right_condition = self._convert_cobol_condition_to_plsql(if_info["right_condition"])
        
        return f"    IF {left_condition} {logical_op} {right_condition} THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}"
    
    def _convert_if_condition_name(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF con condition name (88-level)"""
        condition_name = if_info["condition_name"]
        converted_name = self._convert_cobol_to_plsql_identifier(condition_name)
        
        return f"    IF {converted_name} THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}\n    -- GAP: Definir constante para condition name {condition_name}"
    
    def _convert_if_signed_numeric(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF con números con signo (IS POSITIVE/NEGATIVE/ZERO)"""
        variable = self._convert_cobol_to_plsql_identifier(if_info["variable"])
        sign_type = if_info["sign_type"].upper()
        
        # Mapeo según archivo de equivalencias
        if sign_type == "POSITIVE":
            condition = f"{variable} > 0"
        elif sign_type == "NEGATIVE":
            condition = f"{variable} < 0"
        elif sign_type == "ZERO":
            condition = f"{variable} = 0"
        else:
            condition = f"{variable} IS {sign_type}"
        
        return f"    IF {condition} THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}"
    
    def _convert_if_string_comparison(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF con comparación de substring"""
        variable = self._convert_cobol_to_plsql_identifier(if_info["variable"])
        start_pos = if_info["start_pos"]
        end_pos = if_info["end_pos"]
        operator = self._convert_cobol_operator_to_plsql(if_info["operator"])
        value = self._convert_literal(if_info["value"])
        
        # Calcular longitud para SUBSTR
        length = int(end_pos) - int(start_pos) + 1
        
        return f"    IF SUBSTR({variable}, {start_pos}, {length}) {operator} {value} THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}"
    
    def _convert_sqlcode_check(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF con verificación de SQLCODE"""
        return f"    IF SQLCODE = 0 THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}"
    
    def _convert_boolean_flag(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF con flag booleano"""
        condition = if_info.get("condition", "")
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"    IF {converted_condition} THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}"
    
    def _convert_qualified_comparison(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF con comparación calificada"""
        condition = if_info.get("condition", "")
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"    IF {converted_condition} THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}"
    
    def _convert_complex_condition(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF con condición compleja"""
        condition = if_info.get("condition", "")
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"    IF {converted_condition} THEN\n        -- GAP: Implementar lógica THEN\n    END IF; -- {raw_content}"
    
    def _convert_if_generic(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir IF genérico"""
        return f"    -- GAP -- {raw_content} -- (IF statement - generic)"
    
    def _convert_cobol_condition_to_plsql(self, condition: str) -> str:
        """Convertir condición COBOL a PL/SQL"""
        # Limpiar y convertir identificadores
        condition = self._convert_identifiers_in_condition(condition)
        
        # Convertir operadores COBOL a PL/SQL
        condition = self._convert_cobol_operator_to_plsql(condition)
        
        return condition
    
    def _convert_identifiers_in_condition(self, condition: str) -> str:
        """Convertir identificadores en condición"""
        # Convertir nombres calificados
        condition = re.sub(r'([A-Z][-A-Z0-9]*)\s+OF\s+([A-Z][-A-Z0-9]*)', r'\2.\1', condition, flags=re.IGNORECASE)
        
        # Limpiar identificadores
        condition = re.sub(r'([A-Z][-A-Z0-9]*)', lambda m: self._convert_cobol_to_plsql_identifier(m.group(1)), condition, flags=re.IGNORECASE)
        
        return condition
    
    def _convert_cobol_operator_to_plsql(self, condition: str) -> str:
        """Convertir operadores COBOL a PL/SQL"""
        operator_mapping = {
            "EQUAL": "=",
            "GREATER": ">",
            "LESS": "<",
            "NOT EQUAL": "!=",
            "NOT =": "!=",
            "GREATER THAN": ">",
            "LESS THAN": "<",
            "GREATER THAN OR EQUAL": ">=",
            "LESS THAN OR EQUAL": "<="
        }
        
        for cobol_op, plsql_op in operator_mapping.items():
            condition = condition.replace(cobol_op, plsql_op)
        
        return condition
    
    def _convert_literal(self, literal: str) -> str:
        """Convertir literal a PL/SQL"""
        if literal.startswith("'") or literal.startswith('"'):
            return literal
        elif literal.isdigit():
            return literal
        else:
            return f"'{literal}'"
    
    def _convert_cobol_to_plsql_identifier(self, identifier: str) -> str:
        """Convertir identificador COBOL a PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()
    
    def _clean_condition(self, condition: str) -> str:
        """Limpiar condición para PL/SQL"""
        return condition.replace('-', '_').replace(' ', '').upper()
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador para PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()

class PerformStatementConverter(IStatementConverter):
    """Convertidor específico para sentencias PERFORM (SRP)"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una sentencia PERFORM"""
        raw = statement.get("raw", "").strip().upper()
        return raw.startswith("PERFORM")
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir PERFORM a PL/SQL"""
        raw = statement.get("raw", "").strip()
        
        # Patrones de PERFORM
        patterns = [
            r'PERFORM\s+([A-Z0-9-]+)\s+UNTIL\s+(.+?)(?:\.|$)',
            r'PERFORM\s+([A-Z0-9-]+)(?:\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw, re.IGNORECASE)
            if match:
                procedure = self._clean_identifier(match.group(1).strip())
                
                if len(match.groups()) > 1:
                    condition = self._clean_condition(match.group(2).strip())
                    return f"    WHILE NOT ({condition}) LOOP\n        {procedure}();\n    END LOOP; -- {raw}"
                else:
                    return f"    {procedure}(); -- {raw}"
        
        return f"    -- GAP -- {raw} -- (PERFORM statement)"
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador para PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()
    
    def _clean_condition(self, condition: str) -> str:
        """Limpiar condición para PL/SQL"""
        return condition.replace('-', '_').replace(' ', '').upper()

class DisplayStatementConverter(IStatementConverter):
    """Convertidor específico para sentencias DISPLAY (SRP)"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una sentencia DISPLAY"""
        raw = statement.get("raw", "").strip().upper()
        return raw.startswith("DISPLAY")
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir DISPLAY a PL/SQL"""
        raw = statement.get("raw", "").strip()
        
        # Extraer contenido del DISPLAY
        match = re.search(r'DISPLAY\s+(.+?)(?:\.|$)', raw, re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            return f"    DBMS_OUTPUT.PUT_LINE({content}); -- {raw}"
        
        return f"    -- GAP -- {raw} -- (DISPLAY statement)"

class SetStatementConverter(IStatementConverter):
    """Convertidor específico para sentencias SET (SRP)"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una sentencia SET"""
        raw = statement.get("raw", "").strip().upper()
        return raw.startswith("SET")
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir SET a PL/SQL"""
        raw = statement.get("raw", "").strip()
        
        # Patrones de SET
        patterns = [
            r'SET\s+([A-Z0-9-]+)\s+TO\s+(TRUE|FALSE)(?:\.|$)',
            r'SET\s+([A-Z0-9-]+)\s+TO\s+([0-9]+)(?:\.|$)',
            r'SET\s+([A-Z0-9-]+)\s+UP\s+BY\s+([0-9]+)(?:\.|$)',
            r'SET\s+([A-Z0-9-]+)\s+DOWN\s+BY\s+([0-9]+)(?:\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw, re.IGNORECASE)
            if match:
                variable = self._clean_identifier(match.group(1).strip())
                value = match.group(2).strip()
                
                if value.upper() in ['TRUE', 'FALSE']:
                    return f"    {variable} := {value.upper()}; -- {raw}"
                elif 'UP BY' in raw.upper():
                    return f"    {variable} := {variable} + {value}; -- {raw}"
                elif 'DOWN BY' in raw.upper():
                    return f"    {variable} := {variable} - {value}; -- {raw}"
                else:
                    return f"    {variable} := {value}; -- {raw}"
        
        return f"    -- GAP -- {raw} -- (SET statement)"
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador para PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()

class FileOperationConverter(IStatementConverter):
    """Convertidor específico para operaciones de archivos (SRP) - HOMOLOGADO"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una operación de archivo"""
        raw = statement.get("raw", "").strip().upper()
        file_operations = ["OPEN", "CLOSE", "READ", "WRITE", "REWRITE", "DELETE", "START"]
        return any(raw.startswith(op) for op in file_operations)
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir operación de archivo a PL/SQL"""
        raw = statement.get("raw", "").strip()
        op = self._detect_file_operation(raw)
        
        if not op:
            return f"    -- GAP -- {raw} -- (File operation - unknown)"
        
        # Parsear la operación
        file_info = self._parse_file_operation(raw, op)
        
        if not file_info:
            return f"    -- GAP -- {raw} -- ({op} statement - parsing failed)"
        
        # Convertir según el tipo
        try:
            if op == "OPEN":
                return self._convert_open_file(file_info, raw)
            elif op == "CLOSE":
                return self._convert_close_file(file_info, raw)
            elif op == "READ":
                return self._convert_read_file(file_info, raw)
            elif op == "WRITE":
                return self._convert_write_file(file_info, raw)
            elif op == "REWRITE":
                return self._convert_rewrite_file(file_info, raw)
            elif op == "DELETE":
                return self._convert_delete_record(file_info, raw)
            elif op == "START":
                return self._convert_start_file(file_info, raw)
            else:
                return f"    -- GAP -- {raw} -- ({op} statement)"
        except Exception as e:
            return f"    -- GAP -- {raw} -- ({op} statement - conversion error: {e})"
    
    def _detect_file_operation(self, raw_content: str) -> str:
        """Detectar tipo de operación de archivo"""
        upper_content = raw_content.upper()
        file_operations = ["OPEN", "CLOSE", "READ", "WRITE", "REWRITE", "DELETE", "START"]
        
        for op in file_operations:
            if upper_content.startswith(op):
                return op
        return None
    
    def _parse_file_operation(self, raw_content: str, op: str) -> Dict[str, Any]:
        """Parsear operación de archivo"""
        line = raw_content.strip()
        upper_line = line.upper()
        
        # Patrones para diferentes operaciones
        if op == "OPEN":
            match = re.search(r'OPEN\s+(INPUT|OUTPUT|I-O|EXTEND)\s+(.+?)(?:\.|$)', upper_line)
            if match:
                return {
                    "mode": match.group(1),
                    "file_name": match.group(2).strip(),
                    "raw": line
                }
        elif op == "CLOSE":
            match = re.search(r'CLOSE\s+(.+?)(?:\s+WITH\s+NO\s+REWIND)?(?:\.|$)', upper_line)
            if match:
                return {
                    "file_name": match.group(1).strip(),
                    "raw": line
                }
        elif op == "READ":
            match = re.search(r'READ\s+(.+?)(?:\s+INTO\s+(.+?))?(?:\s+AT\s+END\s+(.+?))?(?:\.|$)', upper_line)
            if match:
                return {
                    "file_name": match.group(1).strip(),
                    "into_record": match.group(2).strip() if match.group(2) else None,
                    "at_end_action": match.group(3).strip() if match.group(3) else None,
                    "raw": line
                }
        elif op == "WRITE":
            match = re.search(r'WRITE\s+(.+?)(?:\s+FROM\s+(.+?))?(?:\s+AFTER\s+ADVANCING\s+(.+?))?(?:\.|$)', upper_line)
            if match:
                return {
                    "file_name": match.group(1).strip(),
                    "from_record": match.group(2).strip() if match.group(2) else None,
                    "after_advancing": match.group(3).strip() if match.group(3) else None,
                    "raw": line
                }
        elif op == "REWRITE":
            match = re.search(r'REWRITE\s+(.+?)(?:\s+FROM\s+(.+?))?(?:\.|$)', upper_line)
            if match:
                return {
                    "file_name": match.group(1).strip(),
                    "from_record": match.group(2).strip() if match.group(2) else None,
                    "raw": line
                }
        elif op == "DELETE":
            match = re.search(r'DELETE\s+(.+?)(?:\s+RECORD\s+INVALID\s+(.+?))?(?:\.|$)', upper_line)
            if match:
                return {
                    "file_name": match.group(1).strip(),
                    "invalid_action": match.group(2).strip() if match.group(2) else None,
                    "raw": line
                }
        elif op == "START":
            match = re.search(r'START\s+(.+?)(?:\s+KEY\s+(IS\s+)?(?:>|>=|=|<=|<)\s+(.+?))?(?:\.|$)', upper_line)
            if match:
                return {
                    "file_name": match.group(1).strip(),
                    "key_condition": match.group(3).strip() if match.group(3) else None,
                    "raw": line
                }
        
        return None
    
    def _convert_open_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir OPEN file"""
        file_name = self._clean_identifier(file_info["file_name"])
        mode = file_info["mode"]
        
        # Mapeo de modos COBOL a UTL_FILE
        mode_mapping = {
            "INPUT": "'R'",
            "OUTPUT": "'W'",
            "I-O": "'A'",
            "EXTEND": "'A'"
        }
        
        utl_mode = mode_mapping.get(mode, "'R'")
        
        return f"""    {file_name} := UTL_FILE.FOPEN('NEXTI_DIR', '{file_name}.TXT', {utl_mode});
    IF UTL_FILE.IS_OPEN({file_name}) THEN
        DBMS_OUTPUT.PUT_LINE('Archivo {file_name}.TXT abierto correctamente.');
    ELSE
        DBMS_OUTPUT.PUT_LINE('Error abriendo archivo {file_name}.TXT');
    END IF; -- {raw_content}"""
    
    def _convert_close_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir CLOSE file"""
        file_name = self._clean_identifier(file_info["file_name"])
        
        return f"""    IF UTL_FILE.IS_OPEN({file_name}) THEN
        UTL_FILE.FCLOSE({file_name});
        DBMS_OUTPUT.PUT_LINE('Archivo {file_name}.TXT cerrado correctamente.');
    END IF; -- {raw_content}"""
    
    def _convert_read_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir READ file"""
        file_name = self._clean_identifier(file_info["file_name"])
        into_record = file_info.get("into_record")
        at_end_action = file_info.get("at_end_action")
        
        result = f"""    BEGIN
        UTL_FILE.GET_LINE({file_name}, {into_record or 'line_buffer'});"""
        
        if at_end_action:
            result += f"""
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            {at_end_action};"""
        
        result += f"""
    END; -- {raw_content}"""
        
        return result
    
    def _convert_write_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir WRITE file"""
        file_name = self._clean_identifier(file_info["file_name"])
        from_record = file_info.get("from_record")
        
        return f"""    UTL_FILE.PUT_LINE({file_name}, {from_record or 'output_line'}); -- {raw_content}"""
    
    def _convert_rewrite_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir REWRITE file"""
        file_name = self._clean_identifier(file_info["file_name"])
        from_record = file_info.get("from_record")
        
        return f"""    -- REWRITE: Actualizar registro en archivo
    UTL_FILE.PUT_LINE({file_name}, {from_record or 'updated_record'}); -- {raw_content}"""
    
    def _convert_delete_record(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir DELETE record"""
        file_name = self._clean_identifier(file_info["file_name"])
        
        return f"""    -- DELETE: Eliminar registro del archivo
    -- GAP: Implementar lógica de eliminación de registro -- {raw_content}"""
    
    def _convert_start_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir START file"""
        file_name = self._clean_identifier(file_info["file_name"])
        key_condition = file_info.get("key_condition")
        
        return f"""    -- START: Posicionar en archivo
    -- GAP: Implementar posicionamiento con condición {key_condition} -- {raw_content}"""
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador para PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()

class StringStatementConverter(IStatementConverter):
    """Convertidor específico para sentencias STRING (SRP) - HOMOLOGADO"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una sentencia STRING"""
        raw = statement.get("raw", "").strip().upper()
        return raw.startswith("STRING")
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir STRING a PL/SQL"""
        raw = statement.get("raw", "").strip()
        
        # Parsear la sentencia STRING
        string_info = self._parse_string_statement(raw)
        
        if not string_info:
            return f"    -- GAP -- {raw} -- (STRING statement - parsing failed)"
        
        # Convertir según el tipo
        try:
            if string_info["type"] == "simple":
                return self._convert_string_simple(string_info, raw)
            elif string_info["type"] == "delimited_spaces":
                return self._convert_string_delimited_spaces(string_info, raw)
            elif string_info["type"] == "delimited_size":
                return self._convert_string_delimited_size(string_info, raw)
            elif string_info["type"] == "with_pointer":
                return self._convert_string_with_pointer(string_info, raw)
            elif string_info["type"] == "with_overflow":
                return self._convert_string_with_overflow(string_info, raw)
            else:
                return self._convert_string_generic(string_info, raw)
        except Exception as e:
            return f"    -- GAP -- {raw} -- (STRING statement - conversion error: {e})"
    
    def _parse_string_statement(self, raw_content: str) -> Dict[str, Any]:
        """Parsear sentencia STRING"""
        line = raw_content.strip()
        upper_line = line.upper()
        
        # Patrones para diferentes tipos de STRING
        patterns = {
            "delimited_spaces": r'STRING\s+(.+?)\s+DELIMITED\s+BY\s+SIZE\s+INTO\s+(.+?)(?:\s+WITH\s+POINTER\s+(.+?))?(?:\s+ON\s+OVERFLOW\s+(.+?))?(?:\.|$)',
            "delimited_size": r'STRING\s+(.+?)\s+DELIMITED\s+BY\s+(.+?)\s+INTO\s+(.+?)(?:\s+WITH\s+POINTER\s+(.+?))?(?:\s+ON\s+OVERFLOW\s+(.+?))?(?:\.|$)',
            "simple": r'STRING\s+(.+?)\s+INTO\s+(.+?)(?:\.|$)',
        }
        
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, upper_line)
            if match:
                if pattern_name == "delimited_spaces":
                    return {
                        "type": "delimited_spaces",
                        "sources": match.group(1).strip(),
                        "target": match.group(2).strip(),
                        "pointer": match.group(3).strip() if match.group(3) else None,
                        "overflow_action": match.group(4).strip() if match.group(4) else None,
                        "raw": line
                    }
                elif pattern_name == "delimited_size":
                    return {
                        "type": "delimited_size",
                        "sources": match.group(1).strip(),
                        "delimiter": match.group(2).strip(),
                        "target": match.group(3).strip(),
                        "pointer": match.group(4).strip() if match.group(4) else None,
                        "overflow_action": match.group(5).strip() if match.group(5) else None,
                        "raw": line
                    }
                elif pattern_name == "simple":
                    return {
                        "type": "simple",
                        "sources": match.group(1).strip(),
                        "target": match.group(2).strip(),
                        "raw": line
                    }
        
        return None
    
    def _convert_string_simple(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir STRING simple"""
        sources = string_info["sources"]
        target = self._clean_identifier(string_info["target"])
        
        # Extraer fuentes y concatenar
        sources_list = self._extract_string_sources(sources)
        concatenated = " || ".join([self._clean_identifier(s) for s in sources_list])
        
        return f"    {target} := {concatenated}; -- {raw_content}"
    
    def _convert_string_delimited_spaces(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir STRING DELIMITED BY SIZE"""
        sources = string_info["sources"]
        target = self._clean_identifier(string_info["target"])
        pointer = string_info.get("pointer")
        overflow_action = string_info.get("overflow_action")
        
        sources_list = self._extract_string_sources(sources)
        concatenated = " || ".join([self._clean_identifier(s) for s in sources_list])
        
        result = f"    {target} := {concatenated};"
        
        if pointer:
            result += f"\n    {self._clean_identifier(pointer)} := LENGTH({target});"
        
        if overflow_action:
            result += f"\n    -- ON OVERFLOW: {overflow_action}"
        
        result += f" -- {raw_content}"
        return result
    
    def _convert_string_delimited_size(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir STRING DELIMITED BY literal"""
        sources = string_info["sources"]
        delimiter = string_info["delimiter"]
        target = self._clean_identifier(string_info["target"])
        
        sources_list = self._extract_string_sources(sources)
        concatenated = " || ".join([self._clean_identifier(s) for s in sources_list])
        
        return f"    {target} := {concatenated}; -- {raw_content}"
    
    def _convert_string_with_pointer(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir STRING WITH POINTER"""
        return self._convert_string_delimited_spaces(string_info, raw_content)
    
    def _convert_string_with_overflow(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir STRING ON OVERFLOW"""
        return self._convert_string_delimited_spaces(string_info, raw_content)
    
    def _convert_string_generic(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir STRING genérico"""
        return f"    -- GAP -- {raw_content} -- (STRING statement)"
    
    def _extract_string_sources(self, sources: str) -> List[str]:
        """Extraer fuentes de STRING"""
        # Simplificado - en implementación real sería más complejo
        return [s.strip() for s in sources.split(' ') if s.strip()]
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador para PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()

class ExecSqlStatementConverter(IStatementConverter):
    """Convertidor específico para sentencias EXEC SQL (SRP) - HOMOLOGADO"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una sentencia EXEC SQL"""
        op = statement.get("op", "")
        raw = statement.get("raw", "").strip().upper()
        details = statement.get("details", {})
        sql_type = details.get("type", "")
        
        # Verificar por operación, tipo o contenido
        return (op == "EXEC_SQL" or 
                sql_type == "EXEC_SQL" or 
                raw.startswith("EXEC SQL") or 
                "EXEC SQL" in raw)
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir EXEC SQL a PL/SQL"""
        raw = statement.get("raw", "").strip()
        details = statement.get("details", {})
        
        sql_type = details.get("sql_type", "OTHER")
        sql_statement = details.get("sql_statement", "")
        host_variables = details.get("host_variables", [])
        
        # Si no hay sql_statement, extraer del raw
        if not sql_statement and raw:
            sql_statement = self._extract_sql_from_raw(raw)
        
        # Convertir según el tipo
        try:
            if sql_type == "SELECT" or "SELECT" in sql_statement.upper():
                return self._convert_sql_select_into(sql_statement, host_variables, raw)
            elif sql_type == "INSERT" or "INSERT" in sql_statement.upper():
                return self._convert_sql_insert(sql_statement, host_variables, raw)
            elif sql_type == "UPDATE" or "UPDATE" in sql_statement.upper():
                return self._convert_sql_update(sql_statement, host_variables, raw)
            elif sql_type == "DELETE" or "DELETE" in sql_statement.upper():
                return self._convert_sql_delete(sql_statement, host_variables, raw)
            elif sql_type == "COMMIT" or "COMMIT" in sql_statement.upper():
                return self._convert_sql_commit(raw)
            elif sql_type == "ROLLBACK" or "ROLLBACK" in sql_statement.upper():
                return self._convert_sql_rollback(raw)
            elif "INCLUDE" in sql_statement.upper():
                return self._convert_sql_include(sql_statement, raw)
            elif "DECLARE" in sql_statement.upper() and "CURSOR" in sql_statement.upper():
                return self._convert_sql_declare_cursor(sql_statement, raw)
            elif "OPEN" in sql_statement.upper():
                return self._convert_sql_open_cursor(sql_statement, raw)
            elif "FETCH" in sql_statement.upper():
                return self._convert_sql_fetch(sql_statement, host_variables, raw)
            elif "CLOSE" in sql_statement.upper():
                return self._convert_sql_close_cursor(sql_statement, raw)
            else:
                return self._convert_sql_generic(sql_statement, raw)
        except Exception as e:
            return f"    -- GAP -- {raw} -- (EXEC SQL - conversion error: {e})"
    
    def _extract_sql_from_raw(self, raw_content: str) -> str:
        """Extraer SQL statement del contenido raw"""
        lines = raw_content.split('\n')
        sql_lines = []
        in_sql = False
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith('EXEC SQL'):
                in_sql = True
                continue
            elif line.upper().startswith('END-EXEC'):
                break
            elif in_sql and line:
                sql_lines.append(line)
        
        return '\n'.join(sql_lines)
    
    def _convert_sql_select_into(self, sql_statement: str, host_variables: List[str], raw_content: str) -> str:
        """Convertir SELECT INTO"""
        # Limpiar variables host (remover :)
        cleaned_sql = sql_statement
        plsql_variables = []
        
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            plsql_variables.append(clean_var)
            cleaned_sql = cleaned_sql.replace(f":{var}", clean_var)
        
        # Generar PL/SQL con manejo de excepciones
        plsql_code = f"""    BEGIN
        {cleaned_sql};
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            -- GAP: Manejar NO_DATA_FOUND
            NULL;
        WHEN TOO_MANY_ROWS THEN
            -- GAP: Manejar TOO_MANY_ROWS
            NULL;
        WHEN OTHERS THEN
            -- GAP: Manejar otros errores
            NULL;
    END; -- {raw_content}"""
        
        return plsql_code
    
    def _convert_sql_insert(self, sql_statement: str, host_variables: List[str], raw_content: str) -> str:
        """Convertir INSERT"""
        # Limpiar variables host
        cleaned_sql = sql_statement
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            cleaned_sql = cleaned_sql.replace(f":{var}", clean_var)
        
        return f"    {cleaned_sql}; -- {raw_content}"
    
    def _convert_sql_update(self, sql_statement: str, host_variables: List[str], raw_content: str) -> str:
        """Convertir UPDATE"""
        # Limpiar variables host
        cleaned_sql = sql_statement
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            cleaned_sql = cleaned_sql.replace(f":{var}", clean_var)
        
        return f"    {cleaned_sql}; -- {raw_content}"
    
    def _convert_sql_delete(self, sql_statement: str, host_variables: List[str], raw_content: str) -> str:
        """Convertir DELETE"""
        # Limpiar variables host
        cleaned_sql = sql_statement
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            cleaned_sql = cleaned_sql.replace(f":{var}", clean_var)
        
        return f"    {cleaned_sql}; -- {raw_content}"
    
    def _convert_sql_commit(self, raw_content: str) -> str:
        """Convertir COMMIT"""
        return f"    COMMIT; -- {raw_content}"
    
    def _convert_sql_rollback(self, raw_content: str) -> str:
        """Convertir ROLLBACK"""
        return f"    ROLLBACK; -- {raw_content}"
    
    def _convert_sql_include(self, sql_statement: str, raw_content: str) -> str:
        """Convertir INCLUDE"""
        return f"    -- INCLUDE: {sql_statement} -- (Convertido a comentario en PL/SQL) -- {raw_content}"
    
    def _convert_sql_declare_cursor(self, sql_statement: str, raw_content: str) -> str:
        """Convertir DECLARE CURSOR"""
        return f"    -- CURSOR: {sql_statement} -- (Mover a sección de declaraciones) -- {raw_content}"
    
    def _convert_sql_open_cursor(self, sql_statement: str, raw_content: str) -> str:
        """Convertir OPEN CURSOR"""
        # Extraer nombre del cursor
        cursor_name = sql_statement.replace("OPEN", "").strip()
        return f"    OPEN {cursor_name}; -- {raw_content}"
    
    def _convert_sql_fetch(self, sql_statement: str, host_variables: List[str], raw_content: str) -> str:
        """Convertir FETCH"""
        # Limpiar variables host
        cleaned_sql = sql_statement
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            cleaned_sql = cleaned_sql.replace(f":{var}", clean_var)
        
        return f"    {cleaned_sql}; -- {raw_content}"
    
    def _convert_sql_close_cursor(self, sql_statement: str, raw_content: str) -> str:
        """Convertir CLOSE CURSOR"""
        # Extraer nombre del cursor
        cursor_name = sql_statement.replace("CLOSE", "").strip()
        return f"    CLOSE {cursor_name}; -- {raw_content}"
    
    def _convert_sql_generic(self, sql_statement: str, raw_content: str) -> str:
        """Convertir SQL genérico"""
        if not sql_statement:
            return f"    -- GAP -- {raw_content} -- (EXEC SQL - generic)"
        
        # Limpiar variables host básicas
        cleaned_sql = sql_statement
        cleaned_sql = re.sub(r':([A-Z][-A-Z0-9]*)', r'\1', cleaned_sql)
        cleaned_sql = cleaned_sql.replace("-", "_")
        
        return f"    {cleaned_sql}; -- {raw_content}"

class EvaluateStatementConverter(IStatementConverter):
    """Convertidor específico para sentencias EVALUATE (SRP) - HOMOLOGADO"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Verificar si es una sentencia EVALUATE"""
        raw = statement.get("raw", "").strip().upper()
        op = statement.get("op", "").strip().upper()
        statement_type = statement.get("statement_type", "").strip().upper()
        return (raw.startswith("EVALUATE") or 
                op == "EVALUATE" or 
                statement_type == "EVALUATE")
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir EVALUATE a PL/SQL"""
        raw = statement.get("raw", "").strip()
        
        # Parsear la sentencia EVALUATE
        evaluate_info = self._parse_evaluate_statement(raw)
        
        if not evaluate_info:
            return f"    -- GAP -- {raw} -- (EVALUATE statement - parsing failed)"
        
        # Convertir según el tipo
        try:
            if evaluate_info["type"] == "simple":
                return self._convert_evaluate_simple(evaluate_info, raw)
            elif evaluate_info["type"] == "range":
                return self._convert_evaluate_range(evaluate_info, raw)
            elif evaluate_info["type"] == "true":
                return self._convert_evaluate_true(evaluate_info, raw)
            elif evaluate_info["type"] == "multiple_subjects":
                return self._convert_evaluate_multiple_subjects(evaluate_info, raw)
            else:
                return self._convert_evaluate_generic(evaluate_info, raw)
        except Exception as e:
            return f"    -- GAP -- {raw} -- (EVALUATE statement - conversion error: {e})"
    
    def _parse_evaluate_statement(self, raw_content: str) -> Dict[str, Any]:
        """Parsear sentencia EVALUATE"""
        line = raw_content.strip()
        upper_line = line.upper()
        
        # Patrones para diferentes tipos de EVALUATE (orden importa - más específicos primero)
        patterns = {
            "true": r"EVALUATE\s+TRUE\s*(?:\.|$)",
            "range": r"EVALUATE\s+(.+?)\s+ALSO\s+(.+?)(?:\.|$)",
            "simple": r"EVALUATE\s+([A-Z][-A-Z0-9]*)\s*(?:\.|$)",  # Solo variables, no TRUE
        }
        
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, upper_line, re.IGNORECASE)
            if match:
                if pattern_name == "true":
                    return {
                        "type": "true",
                        "raw": line
                    }
                elif pattern_name == "range":
                    return {
                        "type": "range",
                        "subject1": match.group(1).strip(),
                        "subject2": match.group(2).strip(),
                        "raw": line
                    }
                elif pattern_name == "simple":
                    return {
                        "type": "simple",
                        "subject": match.group(1).strip(),
                        "raw": line
                    }
        
        return None
    
    def _convert_evaluate_simple(self, evaluate_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir EVALUATE simple"""
        subject = self._clean_identifier(evaluate_info["subject"])
        
        return f"    -- EVALUATE {subject}\n    -- GAP: Implementar lógica WHEN -- {raw_content}"
    
    def _convert_evaluate_range(self, evaluate_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir EVALUATE con rangos"""
        subject1 = self._clean_identifier(evaluate_info["subject1"])
        subject2 = self._clean_identifier(evaluate_info["subject2"])
        
        return f"    -- EVALUATE {subject1} ALSO {subject2}\n    -- GAP: Implementar lógica WHEN -- {raw_content}"
    
    def _convert_evaluate_true(self, evaluate_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir EVALUATE TRUE"""
        return f"    -- EVALUATE TRUE\n    -- GAP: Implementar lógica WHEN -- {raw_content}"
    
    def _convert_evaluate_multiple_subjects(self, evaluate_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir EVALUATE con múltiples sujetos"""
        return f"    -- EVALUATE múltiples sujetos\n    -- GAP: Implementar lógica WHEN -- {raw_content}"
    
    def _convert_evaluate_generic(self, evaluate_info: Dict[str, Any], raw_content: str) -> str:
        """Convertir EVALUATE genérico"""
        return f"    -- GAP -- {raw_content} -- (EVALUATE statement)"
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador para PL/SQL"""
        return identifier.replace('-', '_').replace(' ', '').upper()

class GenericStatementConverter(IStatementConverter):
    """Convertidor genérico para statements no reconocidos (SRP)"""
    
    def can_convert(self, statement: Dict[str, Any]) -> bool:
        """Siempre puede convertir (fallback)"""
        return True
    
    def convert(self, statement: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Convertir genéricamente"""
        raw = statement.get("raw", "").strip()
        return f"    -- GAP -- {raw} -- (Generic statement)"

# ===== FACTORY PATTERN (OCP - Open/Closed Principle) =====

class ConverterFactory:
    """Factory para crear convertidores (OCP)"""
    
    def __init__(self):
        self.converters = [
            MoveStatementConverter(),
            IfStatementConverter(),
            PerformStatementConverter(),
            DisplayStatementConverter(),
            SetStatementConverter(),
            FileOperationConverter(),
            StringStatementConverter(),
            ExecSqlStatementConverter(),
            EvaluateStatementConverter(),
            GenericStatementConverter(),  # Siempre último como fallback
        ]
    
    def get_converter(self, statement: Dict[str, Any]) -> IStatementConverter:
        """Obtener el convertidor apropiado para el statement"""
        for converter in self.converters:
            if converter.can_convert(statement):
                return converter
        return self.converters[-1]  # Fallback al genérico

# ===== CONTEXTO Y ESTADÍSTICAS (SRP) =====

class ConversionContext:
    """Contexto de conversión con variables y procedimientos (SRP)"""
    
    def __init__(self, ir_data: Dict[str, Any]):
        self.variables = ir_data.get("variables", [])
        self.procedures = ir_data.get("procedures", [])
        self.program_name = ir_data.get("program", "UNKNOWN")
        self.statistics = {
            "total_statements": 0,
            "converted_statements": 0,
            "gap_statements": 0,
            "macro_statements": 0,
        }
    
    def get_variables(self) -> List[Dict[str, Any]]:
        """Obtener variables disponibles"""
        return self.variables
    
    def get_procedures(self) -> List[Dict[str, Any]]:
        """Obtener procedimientos disponibles"""
        return self.procedures

# ===== CONVERSOR PRINCIPAL (SRP + DIP) =====

class SolidIRConverter:
    """Conversor principal que coordina la conversión (SRP + DIP)"""
    
    def __init__(self):
        self.converter_factory = ConverterFactory()
    
    def convert_ir_to_plsql(self, ir_file: str):
        """Convertir IR completo a PL/SQL"""
        print("🔧 SOLID IR Converter - Iniciando conversión...")
        
        # Cargar IR
        with open(ir_file, 'r', encoding='utf-8') as f:
            ir_data = json.load(f)
        
        # Crear contexto
        context = ConversionContext(ir_data)
        
        # Procesar statements principales (incluyendo EVALUATE)
        self._process_main_statements(ir_data, context)
        
        # Generar package PL/SQL
        plsql_content = self._generate_package_header(context, ir_data)
        plsql_content += self._generate_variables_section(context)
        plsql_content += self._generate_procedures_section(context, ir_data)
        plsql_content += self._generate_package_footer(context)
        
        return plsql_content, context.statistics
    
    def _get_identification_info(self, context: ConversionContext) -> Dict[str, str]:
        """Obtener información de IDENTIFICATION DIVISION"""
        # Buscar información de IDENTIFICATION DIVISION en el IR
        identification_division = getattr(context, 'identification_division', {})
        
        return {
            'program_id': identification_division.get('program_id', context.program_name),
            'author': identification_division.get('author', 'Not specified'),
            'date_written': identification_division.get('date_written', 'Not specified'),
            'date_compiled': identification_division.get('date_compiled', 'Not specified'),
            'security': identification_division.get('security', 'Not specified'),
            'installation': identification_division.get('installation', 'Not specified'),
            'remarks': identification_division.get('remarks', 'Not specified')
        }
    
    def _process_main_statements(self, ir_data: Dict[str, Any], context: ConversionContext):
        """Procesar statements principales del IR (incluyendo EVALUATE)"""
        main_statements = ir_data.get("cobol_statements", [])
        
        print(f"🔍 Procesando {len(main_statements)} statements principales...")
        
        for stmt in main_statements:
            context.statistics["total_statements"] += 1
            
            # Detectar macros internas
            raw = stmt.get("raw", "")
            if "@" in raw:
                context.statistics["macro_statements"] += 1
                continue
            
            # Convertir statement
            converter = self.converter_factory.get_converter(stmt)
            converted = converter.convert(stmt, context.__dict__)
            
            if "-- GAP --" in converted:
                context.statistics["gap_statements"] += 1
            else:
                context.statistics["converted_statements"] += 1
            
            # Debug para EVALUATE
            if stmt.get("statement_type") == "EVALUATE" or stmt.get("op") == "EVALUATE":
                print(f"✅ EVALUATE detectado y procesado: {raw}")
    
    def _generate_package_header(self, context: ConversionContext, ir_data: Dict[str, Any]) -> str:
        """Generar header del package PL/SQL con IDENTIFICATION DIVISION"""
        program_name = context.program_name
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Obtener información de IDENTIFICATION DIVISION
        identification_info = self._get_identification_info(context)
        
        return f"""CREATE OR REPLACE PACKAGE {program_name} IS

-- =============================================
-- IDENTIFICATION DIVISION - COBOL to PL/SQL Conversion
-- =============================================
-- Program ID: {identification_info['program_id']}
-- Author: {identification_info['author']}
-- Date Written: {identification_info['date_written']}
-- Date Compiled: {identification_info['date_compiled']}
-- Security: {identification_info['security']}
-- Installation: {identification_info['installation']}
-- Remarks: {identification_info['remarks']}
-- =============================================
-- Conversion Information:
-- Generated: {timestamp}
-- Program: {program_name}
-- Converter: SOLID_IR_CONVERTER
-- =============================================

{self._generate_cursors_section(ir_data)}

{self._generate_variables_section(context)}

{self._generate_procedures_section(context, ir_data)}"""
    
    def _generate_variables_section(self, context: ConversionContext) -> str:
        """Generar sección de variables con migración completa"""
        variables = context.get_variables()
        
        if not variables:
            return "  -- No variables found\n"
        
        var_section = "  -- WORKING-STORAGE SECTION - Variables globales\n"
        
        # Procesar todas las variables con migración completa
        for var in variables:
            converted_var = self._convert_cobol_variable_to_plsql(var)
            if converted_var:
                var_section += converted_var + "\n"
        
        return var_section + "\n"
    
    def _generate_cursors_section(self, ir_data: Dict[str, Any]) -> str:
        """Generar sección de cursores desde las declaraciones EXEC SQL"""
        cursors_section = "  -- CURSORES - Declaraciones de cursores\n"
        
        # Buscar declaraciones de cursores en el IR
        cursor_declarations = self._extract_cursor_declarations(ir_data)
        
        if not cursor_declarations:
            return "  -- No cursors found\n"
        
        for cursor_decl in cursor_declarations:
            converted_cursor = self._convert_cursor_declaration_to_plsql(cursor_decl)
            if converted_cursor:
                cursors_section += converted_cursor + "\n"
        
        return cursors_section + "\n"
    
    def _extract_cursor_declarations(self, ir_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extraer declaraciones de cursores del IR"""
        cursor_declarations = []
        
        # Buscar en el array principal del IR (no en un sub-array "statements")
        # Las declaraciones de cursores están en el nivel raíz del IR
        for key, value in ir_data.items():
            if isinstance(value, list):
                for item in value:
                    if (isinstance(item, dict) and
                        item.get("type") == "EXEC_SQL" and 
                        item.get("sql_type") == "DECLARE" and
                        "DECLARE" in item.get("sql_statement", "").upper() and
                        "CURSOR" in item.get("sql_statement", "").upper()):
                        cursor_declarations.append(item)
        
        return cursor_declarations
    
    def _convert_cursor_declaration_to_plsql(self, cursor_decl: Dict[str, Any]) -> str:
        """Convertir declaración de cursor COBOL a PL/SQL"""
        sql_statement = cursor_decl.get("sql_statement", "")
        host_variables = cursor_decl.get("host_variables", [])
        raw_content = cursor_decl.get("raw_content", "")
        
        # Limpiar variables host
        cleaned_sql = sql_statement
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            cleaned_sql = cleaned_sql.replace(f":{var}", clean_var)
        
        # Convertir DECLARE CURSOR a PL/SQL
        # En PL/SQL, los cursores se declaran como: CURSOR cursor_name IS SELECT ...
        plsql_cursor = cleaned_sql.replace("DECLARE ", "CURSOR ").replace(" CURSOR WITH HOLD FOR", " IS")
        
        # Agregar comentario con información original
        cursor_declaration = f"  {plsql_cursor}; -- {raw_content}"
        
        return cursor_declaration
    
    def _convert_cobol_variable_to_plsql(self, var: Dict[str, Any]) -> str:
        """Convertir variable COBOL a PL/SQL con migración completa"""
        var_name = var.get("name", "UNKNOWN").replace('-', '_')
        level = var.get("level", "01")
        pic_clause = var.get("pic_clause", "")
        value = var.get("value", "")
        var_type = var.get("type", "STRING")
        size = var.get("size", 0)
        section = var.get("section", "WORKING-STORAGE")
        raw = var.get("raw", "")
        
        # Determinar tipo PL/SQL basado en PIC clause
        plsql_type = self._convert_pic_to_plsql_type(pic_clause, size)
        
        # Generar declaración PL/SQL
        declaration = f"  {var_name} {plsql_type}"
        
        # Agregar valor inicial si existe
        if value:
            converted_value = self._convert_cobol_value_to_plsql(value, pic_clause)
            declaration += f" := {converted_value}"
        
        # Agregar comentario con información original
        declaration += f"; -- {raw}"
        
        return declaration
    
    def _convert_pic_to_plsql_type(self, pic_clause: str, size: int) -> str:
        """Convertir cláusula PIC COBOL a tipo PL/SQL"""
        if not pic_clause:
            return "VARCHAR2(100)"  # Default
        
        pic_upper = pic_clause.upper()
        
        # Patrones PIC comunes
        if "X(" in pic_upper:
            # PIC X(n) - Alphanumeric
            return f"VARCHAR2({size})"
        elif "9(" in pic_upper:
            # PIC 9(n) - Numeric
            if "V" in pic_upper or "P" in pic_upper:
                return "NUMBER"  # Decimal
            else:
                return f"NUMBER({size})"
        elif "S9(" in pic_upper:
            # PIC S9(n) - Signed numeric
            return "NUMBER"
        elif "A(" in pic_upper:
            # PIC A(n) - Alphabetic
            return f"VARCHAR2({size})"
        elif pic_upper == "X":
            # PIC X - Single character
            return "VARCHAR2(1)"
        elif pic_upper == "9":
            # PIC 9 - Single digit
            return "NUMBER(1)"
        elif pic_upper == "S9":
            # PIC S9 - Signed single digit
            return "NUMBER"
        else:
            # Default basado en tamaño
            if size > 0:
                return f"VARCHAR2({size})"
            else:
                return "VARCHAR2(100)"
    
    def _convert_cobol_value_to_plsql(self, value: str, pic_clause: str) -> str:
        """Convertir valor COBOL a PL/SQL"""
        if not value:
            return "NULL"
        
        # Limpiar comillas si existen
        clean_value = value.strip().strip("'\"")
        
        # Determinar si es numérico basado en PIC
        if pic_clause and ("9" in pic_clause.upper() or "S9" in pic_clause.upper()):
            # Es numérico
            if clean_value.isdigit() or (clean_value.startswith('-') and clean_value[1:].isdigit()):
                return clean_value
            else:
                return f"'{clean_value}'"  # Fallback a string
        else:
            # Es alfanumérico
            return f"'{clean_value}'"
    
    def _generate_procedures_section(self, context: ConversionContext, ir_data: Dict[str, Any]) -> str:
        """Generar sección de procedimientos"""
        procedures = context.get_procedures()
        
        if not procedures:
            return "  -- No procedures found\n"
        
        proc_section = "  -- Procedimientos principales\n"
        for proc in procedures:
            proc_name = proc.get("name", "UNKNOWN").replace('-', '_')
            proc_section += f"  PROCEDURE {proc_name};\n"
        
        return proc_section + f"\nEND {context.program_name};\n/\n\nCREATE OR REPLACE PACKAGE BODY {context.program_name} IS\n\n" + self._generate_procedure_bodies(context)
    
    def _generate_procedure_bodies(self, context: ConversionContext) -> str:
        """Generar cuerpos de los procedimientos"""
        procedures = context.get_procedures()
        
        if not procedures:
            return "  -- No procedure bodies to generate\n"
        
        bodies = []
        for proc in procedures:
            proc_name = proc.get("name", "UNKNOWN").replace('-', '_')
            statements = proc.get("statements", [])
            
            body = f"  PROCEDURE {proc_name} IS\n"
            body += "  BEGIN\n"
            
            if statements:
                converted_statements = self._convert_statements_in_procedure(proc, context)
                body += converted_statements
            else:
                body += "    -- No statements in procedure\n"
            
            body += "  END {proc_name};\n\n"
            bodies.append(body)
        
        return "".join(bodies)
    
    def _generate_package_footer(self, context: ConversionContext) -> str:
        """Generar footer del package"""
        return f"""END {context.program_name};
/
"""
    
    def _convert_statements_in_procedure(self, procedure: Dict[str, Any], context: ConversionContext) -> str:
        """Convertir statements dentro de un procedimiento"""
        statements = procedure.get("statements", [])
        
        if not statements:
            return "    -- No statements in procedure\n"
        
        converted_statements = []
        for stmt in statements:
            context.statistics["total_statements"] += 1
            
            # Detectar macros internas
            raw = stmt.get("raw", "")
            if "@" in raw:
                context.statistics["macro_statements"] += 1
                converted_statements.append(f"    -- GAP MACRO INTERNA: {raw.strip()}")
                continue
            
            # Convertir statement
            converter = self.converter_factory.get_converter(stmt)
            converted = converter.convert(stmt, context.__dict__)
            
            if "-- GAP --" in converted:
                context.statistics["gap_statements"] += 1
            else:
                context.statistics["converted_statements"] += 1
            
            converted_statements.append(converted)
        
        return "\n".join(converted_statements)

# ===== FUNCIÓN PRINCIPAL =====

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python solid_ir_converter.py archivo_ir.json")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    
    if not os.path.exists(ir_file):
        print(f"❌ Error: Archivo IR no encontrado: {ir_file}")
        sys.exit(1)
    
    try:
        # Crear conversor
        converter = SolidIRConverter()
        
        # Convertir
        plsql_content, statistics = converter.convert_ir_to_plsql(ir_file)
        
        # Guardar resultado
        base_name = os.path.splitext(os.path.basename(ir_file))[0]
        output_file = f"out/{base_name}_solid_converter.sql"
        
        os.makedirs("out", exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(plsql_content)
        
        # Generar reporte JSON detallado
        report_data = {
            "conversion_summary": {
                "program_name": base_name,
                "timestamp": datetime.now().isoformat(),
                "total_statements": statistics['total_statements'],
                "converted_statements": statistics['converted_statements'],
                "gap_statements": statistics['gap_statements'],
                "macro_statements": statistics['macro_statements'],
                "conversion_percentage": round((statistics['converted_statements'] / statistics['total_statements'] * 100), 2) if statistics['total_statements'] > 0 else 0,
                "gap_percentage": round((statistics['gap_statements'] / statistics['total_statements'] * 100), 2) if statistics['total_statements'] > 0 else 0,
                "macro_percentage": round((statistics['macro_statements'] / statistics['total_statements'] * 100), 2) if statistics['total_statements'] > 0 else 0,
                "migration_status": "COMPLETED" if statistics['gap_statements'] == 0 else "PARTIAL"
            },
            "detailed_statistics": {
                "total_statements": statistics['total_statements'],
                "converted_statements": statistics['converted_statements'],
                "gap_statements": statistics['gap_statements'],
                "macro_statements": statistics['macro_statements'],
                "remaining_gaps": statistics['gap_statements'],
                "remaining_macro_gaps": statistics['macro_statements'],
                "conversion_rate": f"{round((statistics['converted_statements'] / statistics['total_statements'] * 100), 2)}%" if statistics['total_statements'] > 0 else "0%",
                "gap_rate": f"{round((statistics['gap_statements'] / statistics['total_statements'] * 100), 2)}%" if statistics['total_statements'] > 0 else "0%",
                "macro_rate": f"{round((statistics['macro_statements'] / statistics['total_statements'] * 100), 2)}%" if statistics['total_statements'] > 0 else "0%"
            },
            "files_generated": {
                "sql_file": output_file,
                "report_file": f"out/{base_name}_conversion_report_solid.json"
            }
        }
        
        # Guardar reporte JSON
        report_file = f"out/{base_name}_conversion_report_solid.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Mostrar estadísticas
        print("✅ Conversión completada exitosamente!")
        print(f"📄 Archivo generado: {output_file}")
        print(f"📊 Reporte JSON: {report_file}")
        print(f"📊 Estadísticas:")
        print(f"   Total statements: {statistics['total_statements']}")
        print(f"   Convertidos: {statistics['converted_statements']} ({report_data['conversion_summary']['conversion_percentage']}%)")
        print(f"   GAPs: {statistics['gap_statements']} ({report_data['conversion_summary']['gap_percentage']}%)")
        print(f"   Macros: {statistics['macro_statements']} ({report_data['conversion_summary']['macro_percentage']}%)")
        print(f"   Estado migración: {report_data['conversion_summary']['migration_status']}")
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
