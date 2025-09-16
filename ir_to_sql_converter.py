#!/usr/bin/env python3
"""
IR to SQL Converter - Versión SOLID para convertir IR completo a PL/SQL
Basado en enhanced_converter.py con arquitectura SOLID

PRINCIPIOS SOLID APLICADOS:
- S: Single Responsibility - Cada clase tiene una responsabilidad específica
- O: Open/Closed - Extensible mediante nuevos handlers
- L: Liskov Substitution - Los handlers implementan interfaces comunes
- I: Interface Segregation - Interfaces específicas para cada tipo de conversión
- D: Dependency Inversion - Depende de abstracciones, no de implementaciones

Entrada: Archivo IR JSON completo
Salida: Archivo PL/SQL package

Uso: python ir_to_sql_converter.py archivo_ir.json
"""

import sys
import os
import json
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# ===== INTERFACES ABSTRACTAS =====

class AbstractStatementConverter(ABC):
    """Clase base abstracta para convertidores de statements"""
    
    @abstractmethod
    def can_convert(self, stmt: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def convert(self, stmt: Dict[str, Any], indent: str = "    ") -> str:
        pass
    
    def clean_expression(self, expr: str) -> str:
        """Limpia expresiones COBOL para PL/SQL"""
        if not expr:
            return ""
        
        # Remover caracteres especiales de COBOL
        cleaned = re.sub(r'[^\w\s\-().,:]', '', str(expr))
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

class AbstractNodeProcessor(ABC):
    """Clase base abstracta para procesadores de nodos"""
    
    @abstractmethod
    def can_process(self, node: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def process(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

# ===== CONVERTIDORES ESPECÍFICOS =====

class MoveStatementConverter(AbstractStatementConverter):
    """Convertidor especializado para statements MOVE"""
    
    def can_convert(self, stmt: Dict[str, Any]) -> bool:
        op = stmt.get("op", "")
        content = stmt.get("content", "").upper()
        # Detectar MOVE statements más específicamente
        return (op == "MOVE" or 
                "MOVE" in content and "TO" in content or
                bool(re.search(r'\bMOVE\s+\S+\s+TO\s+\S+', content, re.IGNORECASE)))
    
    def convert(self, stmt: Dict[str, Any], indent: str = "    ") -> str:
        content = stmt.get("content", "")
        
        # Usar la lógica probada del enhanced_converter
        move_statements = []
        
        # Patterns exactos del enhanced_converter que funciona
        patterns = [
            # MOVE with CORRESPONDING
            r'^MOVE\s+CORRESPONDING\s+(.+?)\s+TO\s+(.+?)(?:\.|$)',
            # Standard MOVE pattern  
            r'^MOVE\s+(.+?)\s+TO\s+(.+?)(?:\.|$)',
            # MOVE patterns dentro de texto más largo
            r'MOVE\s+(.+?)\s+TO\s+([A-Z0-9_\-]+)',
        ]
        
        # Buscar línea por línea y en el contenido completo
        lines_to_check = content.split('\n') + [content]
        
        for line in lines_to_check:
            line = line.strip()
            if not line or len(line) < 10:
                continue
                
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    source = match.group(1).strip()
                    target = match.group(2).strip()
                    
                    # Limpiar usando la misma lógica del enhanced_converter
                    source_clean = self.parse_move_source(source)
                    target_clean = self.parse_move_source(target)
                    
                    if target_clean and source_clean:
                        move_statements.append(f"{indent}{target_clean} := {source_clean};")
        
        if move_statements:
            return "\n".join(move_statements)
        
        return ""
    
    def parse_move_source(self, expr: str) -> str:
        """Parse MOVE source/target usando lógica del enhanced_converter"""
        if not expr:
            return ""
        
        # Limpiar expresión
        cleaned = self.clean_expression(expr)
        
        # Remover caracteres especiales al final
        cleaned = re.sub(r'[^A-Z0-9_\-\'"\s].*$', '', cleaned).strip()
        
        # Si es un literal (entre comillas), mantenerlo
        if cleaned.startswith(("'", '"')):
            return cleaned
        
        # Si es una variable, limpiar más
        if re.match(r'^[A-Z0-9_\-]+$', cleaned):
            return cleaned.replace('-', '_')  # Convertir guiones para PL/SQL
        
        return cleaned if cleaned else "NULL"
    
    def _split_multiline_content(self, content: str) -> List[str]:
        """Dividir contenido que puede contener múltiples statements en una línea"""
        # Dividir por patrones comunes de separación de statements
        lines = []
        
        # Primero dividir por líneas reales
        raw_lines = content.split('\n')
        
        for raw_line in raw_lines:
            # Dividir líneas muy largas por keywords de COBOL
            if len(raw_line) > 100:
                # Dividir por MOVE, PERFORM, IF, etc.
                parts = re.split(r'(?=\b(?:MOVE|PERFORM|IF|DISPLAY|ADD|COMPUTE)\b)', raw_line, flags=re.IGNORECASE)
                lines.extend([p.strip() for p in parts if p.strip()])
            else:
                lines.append(raw_line)
        
        return lines

class DisplayStatementConverter(AbstractStatementConverter):
    """Convertidor especializado para statements DISPLAY"""
    
    def can_convert(self, stmt: Dict[str, Any]) -> bool:
        op = stmt.get("op", "")
        content = stmt.get("content", "").upper()
        return op == "DISPLAY" or "DISPLAY" in content
    
    def convert(self, stmt: Dict[str, Any], indent: str = "    ") -> str:
        content = stmt.get("content", "")
        
        # Usar la lógica exacta del enhanced_converter
        display_statements = []
        
        # Buscar línea por línea y en el contenido completo
        lines_to_check = content.split('\n') + [content]
        
        for line in lines_to_check:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Handle DISP * DISPLAY pattern (del enhanced_converter)
            if line.upper().startswith('DISP *') and 'DISPLAY' in line.upper():
                display_part = line[line.upper().find('DISPLAY'):]
                display_match = re.match(r'^DISPLAY\s+(.+)$', display_part, re.IGNORECASE)
                if display_match:
                    content_part = display_match.group(1).strip()
                    display_statements.append(f"{indent}DBMS_OUTPUT.PUT_LINE({content_part});")
                continue
            
            # Standard DISPLAY parsing (del enhanced_converter)
            display_match = re.match(r'^DISPLAY\s+(.+)$', line, re.IGNORECASE)
            if display_match:
                content_part = display_match.group(1).strip()
                
                # Patterns específicos del enhanced_converter
                if "'Informar Protesto'" in line:
                    display_statements.append(f"{indent}DBMS_OUTPUT.PUT_LINE('Informar Protesto');")
                elif "'Error llamada servicio de Protesto'" in line:
                    display_statements.append(f"{indent}DBMS_OUTPUT.PUT_LINE('Error llamada servicio de Protesto');")
                elif content_part:
                    # Limpiar content_part
                    content_clean = self.clean_expression(content_part)
                    if content_clean:
                        display_statements.append(f"{indent}DBMS_OUTPUT.PUT_LINE({content_clean});")
        
        if display_statements:
            return "\n".join(display_statements)
        
        return ""
    
    def _split_multiline_content(self, content: str) -> List[str]:
        """Dividir contenido que puede contener múltiples statements en una línea"""
        # Dividir por patrones comunes de separación de statements
        lines = []
        
        # Primero dividir por líneas reales
        raw_lines = content.split('\n')
        
        for raw_line in raw_lines:
            # Dividir líneas muy largas por keywords de COBOL
            if len(raw_line) > 100:
                # Dividir por MOVE, PERFORM, IF, etc.
                parts = re.split(r'(?=\b(?:MOVE|PERFORM|IF|DISPLAY|ADD|COMPUTE)\b)', raw_line, flags=re.IGNORECASE)
                lines.extend([p.strip() for p in parts if p.strip()])
            else:
                lines.append(raw_line)
        
        return lines

class PerformStatementConverter(AbstractStatementConverter):
    """Convertidor especializado para statements PERFORM"""
    
    def can_convert(self, stmt: Dict[str, Any]) -> bool:
        op = stmt.get("op", "")
        content = stmt.get("content", "").upper()
        return op == "PERFORM" or "PERFORM" in content
    
    def convert(self, stmt: Dict[str, Any], indent: str = "    ") -> str:
        content = stmt.get("content", "")
        
        # Usar la lógica exacta del enhanced_converter
        perform_statements = []
        
        # Patterns del enhanced_converter que funciona
        patterns = [
            r'PERFORM\s+([A-Z0-9-]+)\.?',  # PERFORM simple
            r'PERFORM\s+([A-Z0-9-]+)\s+UNTIL\s+(.+)',  # PERFORM UNTIL
        ]
        
        # Buscar línea por línea y en el contenido completo
        lines_to_check = content.split('\n') + [content]
        
        for line in lines_to_check:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # PERFORM simple
            perform_match = re.search(r'PERFORM\s+([A-Z0-9-]+)\.?', line, re.IGNORECASE)
            if perform_match:
                target = perform_match.group(1).strip()
                target_clean = target.replace('-', '_')  # Convertir para PL/SQL
                if target_clean:
                    perform_statements.append(f"{indent}{target_clean}();")
                continue
            
            # PERFORM UNTIL
            perform_until_match = re.search(r'PERFORM\s+([A-Z0-9-]+)\s+UNTIL\s+(.+)', line, re.IGNORECASE)
            if perform_until_match:
                target = perform_until_match.group(1).strip()
                condition = perform_until_match.group(2).strip()
                target_clean = target.replace('-', '_')
                perform_statements.append(f"{indent}WHILE NOT ({condition}) LOOP")
                perform_statements.append(f"{indent}    {target_clean}();")
                perform_statements.append(f"{indent}END LOOP;")
        
        if perform_statements:
            return "\n".join(perform_statements)
        
        return ""
    
    def _split_multiline_content(self, content: str) -> List[str]:
        """Dividir contenido que puede contener múltiples statements en una línea"""
        # Dividir por patrones comunes de separación de statements
        lines = []
        
        # Primero dividir por líneas reales
        raw_lines = content.split('\n')
        
        for raw_line in raw_lines:
            # Dividir líneas muy largas por keywords de COBOL
            if len(raw_line) > 100:
                # Dividir por MOVE, PERFORM, IF, etc.
                parts = re.split(r'(?=\b(?:MOVE|PERFORM|IF|DISPLAY|ADD|COMPUTE)\b)', raw_line, flags=re.IGNORECASE)
                lines.extend([p.strip() for p in parts if p.strip()])
            else:
                lines.append(raw_line)
        
        return lines

class IfStatementConverter(AbstractStatementConverter):
    """Convertidor especializado para statements IF"""
    
    def can_convert(self, stmt: Dict[str, Any]) -> bool:
        op = stmt.get("op", "")
        content = stmt.get("content", "").upper()
        return op == "IF" or content.startswith("IF")
    
    def convert(self, stmt: Dict[str, Any], indent: str = "    ") -> str:
        content = stmt.get("content", "")
        
        # Parsear IF statement básico
        if_match = re.search(r'IF\s+(.+)', content, re.IGNORECASE)
        if if_match:
            condition = self.clean_expression(if_match.group(1))
            return f"{indent}IF {condition} THEN"
        
        return f"{indent}-- IF: {content}"

class GenericStatementConverter(AbstractStatementConverter):
    """Convertidor genérico para statements no especializados"""
    
    def can_convert(self, stmt: Dict[str, Any]) -> bool:
        return True  # Acepta cualquier statement como fallback
    
    def convert(self, stmt: Dict[str, Any], indent: str = "    ") -> str:
        op = stmt.get("op", "UNKNOWN")
        content = stmt.get("content", "")
        
        if not content.strip():
            return ""
        
        # Filtrar contenido irrelevante (definiciones de datos, secciones, etc.)
        content_upper = content.upper()
        
        # Omitir declaraciones de datos COBOL
        if any(pattern in content_upper for pattern in [
            'WORKING-STORAGE', 'FILE SECTION', 'DATA DIVISION', 
            'IDENTIFICATION DIVISION', 'PROCEDURE DIVISION',
            'PIC ', 'VALUE ', 'REDEFINES', 'FILLER'
        ]):
            return ""
        
        # Omitir texto muy largo (probablemente declaraciones)
        if len(content) > 500:
            return ""
        
        # Convertir statements de control específicos
        if "END-IF" in content_upper:
            return f"{indent}END IF;"
        elif content_upper.strip() == "ELSE":
            return f"{indent}ELSE"
        elif "STOP RUN" in content_upper:
            return f"{indent}-- Program termination"
        elif "EXIT" in content_upper:
            return f"{indent}RETURN;"
        elif content_upper.startswith("IF "):
            # Convertir IF statements básicos
            condition = content[3:].strip()
            if condition:
                return f"{indent}IF {condition} THEN"
        
        # Para el resto, omitir si es muy largo o poco útil
        if len(content) > 100:
            return ""
        
        # Solo incluir contenido corto y potencialmente útil
        return f"{indent}-- {content[:50]}{'...' if len(content) > 50 else ''}"

# ===== PROCESADORES DE NODOS =====

class MoveNodeProcessor(AbstractNodeProcessor):
    """Procesador especializado para nodos MOVE del árbol ANTLR"""
    
    def can_process(self, node: Dict[str, Any]) -> bool:
        node_type = node.get("node_type", "")
        text = node.get("text", "").upper()
        return "MOVE" in node_type or ("MOVE" in text and "TO" in text)
    
    def process(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        text = node.get("text", "")
        
        # Extraer MOVE statement del nodo
        move_match = re.search(r'MOVE\s+(.+?)\s+TO\s+(.+)', text, re.IGNORECASE)
        if move_match:
            return {
                "op": "MOVE",
                "source": move_match.group(1).strip(),
                "target": move_match.group(2).strip(),
                "content": text,
                "raw": text,
                "node_type": node.get("node_type", ""),
                "node_id": node.get("node_id", 0)
            }
        
        return None

class DisplayNodeProcessor(AbstractNodeProcessor):
    """Procesador especializado para nodos DISPLAY del árbol ANTLR"""
    
    def can_process(self, node: Dict[str, Any]) -> bool:
        node_type = node.get("node_type", "")
        text = node.get("text", "").upper()
        return "DISPLAY" in node_type or "DISPLAY" in text
    
    def process(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        text = node.get("text", "")
        
        # Extraer DISPLAY statement del nodo
        display_match = re.search(r'DISPLAY\s+(.+)', text, re.IGNORECASE)
        if display_match:
            return {
                "op": "DISPLAY",
                "arguments": display_match.group(1).strip(),
                "content": text,
                "raw": text,
                "node_type": node.get("node_type", ""),
                "node_id": node.get("node_id", 0)
            }
        
        return None

class GenericNodeProcessor(AbstractNodeProcessor):
    """Procesador genérico para nodos no especializados"""
    
    def can_process(self, node: Dict[str, Any]) -> bool:
        return True  # Acepta cualquier nodo como fallback
    
    def process(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        text = node.get("text", "").strip()
        node_type = node.get("node_type", "")
        
        # Solo procesar nodos con contenido significativo
        if len(text) < 5 or not re.search(r'[A-Z]', text):
            return None
        
        # Determinar tipo de statement
        text_upper = text.upper()
        if "PERFORM" in text_upper:
            op = "PERFORM"
        elif "IF" in text_upper and text_upper.startswith("IF"):
            op = "IF"
        elif "END-IF" in text_upper:
            op = "END_IF"
        elif "ELSE" in text_upper:
            op = "ELSE"
        else:
            op = "STATEMENT"
        
        return {
            "op": op,
            "content": text,
            "raw": text,
            "node_type": node_type,
            "node_id": node.get("node_id", 0)
        }

# ===== FACTORIES =====

class StatementConverterFactory:
    """Factory para crear convertidores de statements"""
    
    @staticmethod
    def create_converters() -> List[AbstractStatementConverter]:
        """Crear lista de convertidores en orden de prioridad"""
        return [
            MoveStatementConverter(),
            DisplayStatementConverter(),
            PerformStatementConverter(),
            IfStatementConverter(),
            GenericStatementConverter()  # Siempre último como fallback
        ]

class NodeProcessorFactory:
    """Factory para crear procesadores de nodos"""
    
    @staticmethod
    def create_processors() -> List[AbstractNodeProcessor]:
        """Crear lista de procesadores en orden de prioridad"""
        return [
            MoveNodeProcessor(),
            DisplayNodeProcessor(),
            GenericNodeProcessor()  # Siempre último como fallback
        ]

# ===== CONVERSOR PRINCIPAL =====

class IRToSQLConverter:
    """Conversor principal que lee IR completo y genera PL/SQL"""
    
    def __init__(self):
        self.statement_converters = StatementConverterFactory.create_converters()
        self.node_processors = NodeProcessorFactory.create_processors()
        self.statistics = {
            "total_statements": 0,
            "converted_statements": 0,
            "skipped_statements": 0,
            "total_nodes": 0,
            "processed_nodes": 0
        }
    
    def load_ir_from_file(self, ir_file_path: str) -> Dict[str, Any]:
        """Cargar IR desde archivo JSON - Versión optimizada para archivos grandes"""
        print(f"📁 Cargando IR desde: {ir_file_path}")
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(ir_file_path)
        print(f"📊 Tamaño del archivo: {file_size / (1024*1024):.1f} MB")
        
        if file_size > 10 * 1024 * 1024:  # > 10MB
            print("⚠️  Archivo IR muy grande, cargando con optimizaciones...")
        
        try:
            with open(ir_file_path, 'r', encoding='utf-8') as f:
                ir_data = json.load(f)
            
            print(f"✅ IR cargado exitosamente")
            
            # Mostrar estadísticas del IR
            if 'statements' in ir_data:
                print(f"   📋 Statements: {len(ir_data['statements'])}")
            
            if 'complete_tree' in ir_data:
                tree_info = self._analyze_tree_structure(ir_data['complete_tree'])
                print(f"   🌳 Nodos en árbol: {tree_info['total_nodes']}")
                print(f"   📏 Profundidad máxima: {tree_info['max_depth']}")
            
            return ir_data
            
        except MemoryError:
            print("❌ Error de memoria cargando IR. Archivo demasiado grande.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error decodificando JSON: {e}")
            sys.exit(1)
    
    def convert_ir_to_sql(self, ir: Dict[str, Any]) -> str:
        """Convertir IR completo a PL/SQL"""
        print("🔧 Convirtiendo IR completo a PL/SQL...")
        
        program_name = ir.get("program_name", "UNKNOWN")
        
        # Procesar statements existentes
        statements = ir.get("statements", [])
        converted_statements = self._convert_statements(statements)
        
        # Extraer statements de procedimientos
        procedure_statements = self._extract_statements_from_procedures(ir.get("procedures", []))
        converted_procedure_statements = self._convert_statements(procedure_statements)
        
        # Procesar árbol completo para extraer statements adicionales
        complete_tree = ir.get("complete_tree", {})
        additional_statements = self._extract_statements_from_tree(complete_tree)
        
        # Combinar statements
        all_statements = converted_statements + converted_procedure_statements + additional_statements
        
        # Generar package PL/SQL
        package = self._generate_plsql_package(program_name, all_statements, ir)
        
        return package
    
    def _convert_statements(self, statements: List[Dict[str, Any]]) -> List[str]:
        """Convertir lista de statements a PL/SQL"""
        converted = []
        debug_counters = {"MOVE": 0, "DISPLAY": 0, "PERFORM": 0, "IF": 0, "GENERIC": 0}
        
        print(f"🔧 Convirtiendo {len(statements)} statements desde IR...")
        
        for i, stmt in enumerate(statements):
            self.statistics["total_statements"] += 1
            
            # Buscar convertidor apropiado
            converted_stmt = None
            converter_used = "NONE"
            
            for converter in self.statement_converters:
                if converter.can_convert(stmt):
                    try:
                        converted_stmt = converter.convert(stmt)
                        if converted_stmt and converted_stmt.strip():
                            self.statistics["converted_statements"] += 1
                            converter_used = converter.__class__.__name__
                            break
                    except Exception as e:
                        print(f"⚠️  Error convirtiendo statement: {e}")
                        continue
            
            # Contar por tipo de convertidor
            if "Move" in converter_used:
                debug_counters["MOVE"] += 1
            elif "Display" in converter_used:
                debug_counters["DISPLAY"] += 1
            elif "Perform" in converter_used:
                debug_counters["PERFORM"] += 1
            elif "If" in converter_used:
                debug_counters["IF"] += 1
            else:
                debug_counters["GENERIC"] += 1
            
            if converted_stmt and converted_stmt.strip():
                converted.append(converted_stmt)
            else:
                self.statistics["skipped_statements"] += 1
        
        print(f"   📊 Conversiones por tipo: {debug_counters}")
        return converted
    
    def _extract_statements_from_tree(self, tree_node: Dict[str, Any]) -> List[str]:
        """Extraer statements adicionales del árbol completo - Versión optimizada"""
        extracted = []
        max_nodes = 5000  # Limitar procesamiento para evitar bucles infinitos
        processed_count = 0
        
        print(f"🌳 Procesando árbol ANTLR (máximo {max_nodes} nodos)...")
        
        def walk_tree(node, depth=0):
            nonlocal processed_count
            
            # Limitar profundidad y cantidad de nodos procesados
            if depth > 20 or processed_count >= max_nodes:
                return
                
            processed_count += 1
            self.statistics["total_nodes"] += 1
            
            # Mostrar progreso cada 1000 nodos
            if processed_count % 1000 == 0:
                print(f"   📊 Procesados {processed_count} nodos...")
            
            # Intentar procesar el nodo solo si tiene contenido significativo
            node_text = node.get("text", "").strip()
            if len(node_text) > 3 and any(keyword in node_text.upper() for keyword in 
                                         ["MOVE", "DISPLAY", "PERFORM", "IF", "ELSE", "END-IF"]):
                
                for processor in self.node_processors:
                    if processor.can_process(node):
                        try:
                            processed = processor.process(node)
                            if processed:
                                # Convertir statement procesado
                                for converter in self.statement_converters:
                                    if converter.can_convert(processed):
                                        converted = converter.convert(processed)
                                        if converted and converted.strip():
                                            extracted.append(converted)
                                            self.statistics["processed_nodes"] += 1
                                            break
                                break
                        except Exception as e:
                            print(f"⚠️  Error procesando nodo: {e}")
                            continue
            
            # Procesar hijos recursivamente con límite
            children = node.get("children", [])
            if children and depth < 15:  # Limitar profundidad recursiva
                for child in children[:10]:  # Limitar a primeros 10 hijos por nodo
                    walk_tree(child, depth + 1)
        
        try:
            walk_tree(tree_node)
            print(f"✅ Procesamiento del árbol completado: {processed_count} nodos procesados")
        except RecursionError:
            print(f"⚠️  Límite de recursión alcanzado. Procesados {processed_count} nodos.")
        except Exception as e:
            print(f"⚠️  Error durante procesamiento del árbol: {e}")
        
        return extracted
    
    def _extract_statements_from_procedures(self, procedures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extraer todos los statements de los procedimientos"""
        all_statements = []
        
        for procedure in procedures:
            procedure_name = procedure.get("name", "UNKNOWN")
            statements = procedure.get("statements", [])
            
            # Agregar metadata del procedimiento a cada statement
            for stmt in statements:
                stmt["procedure_name"] = procedure_name
                all_statements.append(stmt)
        
        print(f"📋 Extraídos {len(all_statements)} statements de {len(procedures)} procedimientos")
        return all_statements
    
    def _analyze_tree_structure(self, tree_node: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar estructura del árbol para obtener estadísticas"""
        stats = {"total_nodes": 0, "max_depth": 0}
        
        def analyze_node(node, depth=0):
            stats["total_nodes"] += 1
            stats["max_depth"] = max(stats["max_depth"], depth)
            
            # Limitar análisis para evitar bucles infinitos
            if depth < 10 and stats["total_nodes"] < 1000:
                for child in node.get("children", []):
                    analyze_node(child, depth + 1)
        
        try:
            analyze_node(tree_node)
        except:
            # Si hay error, usar estimación
            stats["total_nodes"] = "Unknown (large)"
            stats["max_depth"] = "Unknown"
        
        return stats
    
    def _generate_plsql_package(self, program_name: str, statements: List[str], ir: Dict[str, Any]) -> str:
        """Generar package PL/SQL completo"""
        program_name_clean = self._clean_identifier(program_name)
        
        # Extraer información del environment
        environment = ir.get("environment", {})
        file_control = environment.get("input_output_section", {}).get("file_control", [])
        
        # Generar declaraciones de variables
        variables_section = self._generate_variables_section(ir)
        
        # Generar declaraciones de archivos
        files_section = self._generate_files_section(file_control)
        
        # Filtrar statements vacíos
        filtered_statements = [stmt for stmt in statements if stmt.strip()]
        
        # Generar package spec
        package_spec = f"""-- =============================================
-- Package: {program_name_clean}
-- Generated from COBOL program: {program_name}
-- Total statements converted: {len(filtered_statements)}
-- =============================================

CREATE OR REPLACE PACKAGE {program_name_clean} IS
  -- Public procedures
  PROCEDURE MAIN;
END {program_name_clean};
/"""
        
        # Generar package body
        package_body = f"""CREATE OR REPLACE PACKAGE BODY {program_name_clean} IS

{variables_section}

{files_section}

  PROCEDURE MAIN IS
  BEGIN
    -- Main program logic
{chr(10).join(filtered_statements)}
    
    -- End of main procedure
    NULL;
  END MAIN;

END {program_name_clean};
/"""
        
        return f"{package_spec}\n\n{package_body}"
    
    def _generate_variables_section(self, ir: Dict[str, Any]) -> str:
        """Generar sección de variables"""
        variables = ir.get("variables", [])
        
        if not variables:
            return "  -- No variables found in IR"
        
        var_lines = ["  -- Variable declarations"]
        for var in variables[:10]:  # Limitar a primeras 10 para ejemplo
            var_name = var.get("name", "UNKNOWN")
            var_level = var.get("level", "01")
            var_lines.append(f"  -- {var_level} {var_name}")
        
        if len(variables) > 10:
            var_lines.append(f"  -- ... and {len(variables) - 10} more variables")
        
        return "\n".join(var_lines)
    
    def _generate_files_section(self, file_control: List[Dict[str, Any]]) -> str:
        """Generar sección de archivos"""
        if not file_control:
            return "  -- No file control entries found"
        
        file_lines = ["  -- File declarations"]
        for file_entry in file_control:
            file_name = file_entry.get("file_name", "UNKNOWN")
            organization = file_entry.get("organization", "SEQUENTIAL")
            file_lines.append(f"  -- FILE: {file_name} ({organization})")
        
        return "\n".join(file_lines)
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador para PL/SQL"""
        if not identifier:
            return "UNKNOWN"
        
        # Remover caracteres especiales y convertir a mayúsculas
        cleaned = re.sub(r'[^A-Z0-9_]', '', identifier.upper())
        
        # Asegurar que comience con letra
        if not cleaned or not cleaned[0].isalpha():
            cleaned = f"PKG_{cleaned}"
        
        return cleaned
    
    def generate_conversion_report(self) -> Dict[str, Any]:
        """Generar reporte de conversión"""
        success_rate = 0
        if self.statistics["total_statements"] > 0:
            success_rate = (self.statistics["converted_statements"] / self.statistics["total_statements"]) * 100
        
        return {
            "conversion_summary": {
                "total_statements": self.statistics["total_statements"],
                "converted_statements": self.statistics["converted_statements"],
                "skipped_statements": self.statistics["skipped_statements"],
                "success_rate": round(success_rate, 2),
                "total_nodes": self.statistics["total_nodes"],
                "processed_nodes": self.statistics["processed_nodes"]
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": "IR_TO_SQL_SOLID"
        }

# ===== FUNCIONES AUXILIARES =====

def get_timestamp():
    """Obtener timestamp con milisegundos"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def format_duration(start_time, end_time):
    """Formatear duración"""
    duration = end_time - start_time
    if duration < 1:
        return f"{duration*1000:.1f} ms"
    elif duration < 60:
        return f"{duration:.3f}s"
    else:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.3f}s"

# ===== FUNCIÓN PRINCIPAL =====

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python ir_to_sql_converter.py archivo_ir.json")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    
    if not os.path.exists(ir_file):
        print(f"❌ Error: Archivo IR no encontrado: {ir_file}")
        sys.exit(1)
    
    # Configurar nombres de archivos de salida
    base_name = os.path.splitext(os.path.basename(ir_file))[0]
    if base_name.endswith("_ir_complete"):
        base_name = base_name[:-12]  # Remover "_ir_complete"
    
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    
    sql_output = os.path.join(output_dir, f"{base_name}_solid.sql")
    report_output = os.path.join(output_dir, f"{base_name}_conversion_report_solid.json")
    
    print("======================================================================")
    print("🔧 IR to SQL Converter SOLID - Conversión de IR completo a PL/SQL")
    print(f"📁 Archivo IR: {ir_file}")
    print(f"⏰ Inicio: {get_timestamp()}")
    print("🎯 Aplicando principios SOLID en la conversión")
    print("======================================================================")
    
    try:
        # Cargar IR
        start_time = time.time()
        converter = IRToSQLConverter()
        ir = converter.load_ir_from_file(ir_file)
        load_time = time.time()
        
        print(f"✅ IR cargado exitosamente")
        print(f"   📊 Statements en IR: {len(ir.get('statements', []))}")
        print(f"   🌳 Nodos en árbol: {ir.get('metadata', {}).get('total_nodes', 0)}")
        
        # Convertir a SQL
        sql_content = converter.convert_ir_to_sql(ir)
        conversion_time = time.time()
        
        # Guardar SQL
        with open(sql_output, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        # Generar reporte
        report = converter.generate_conversion_report()
        with open(report_output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        save_time = time.time()
        
        print("✅ Archivos generados:")
        print(f"   📄 SQL: {sql_output}")
        print(f"   📊 Reporte: {report_output}")
        
        # Mostrar resumen
        print("======================================================================")
        print("📊 RESUMEN DE CONVERSIÓN SOLID")
        print("======================================================================")
        print("🎯 CONVERSIÓN:")
        print(f"   📋 Programa: {ir.get('program_name', 'UNKNOWN')}")
        print(f"   📄 Total statements: {report['conversion_summary']['total_statements']}")
        print(f"   ✅ Convertidos: {report['conversion_summary']['converted_statements']}")
        print(f"   ⏭️  Omitidos: {report['conversion_summary']['skipped_statements']}")
        print(f"   📈 Tasa éxito: {report['conversion_summary']['success_rate']}%")
        print(f"   🌳 Nodos procesados: {report['conversion_summary']['processed_nodes']}")
        
        print("⏰ RENDIMIENTO:")
        print(f"   🕐 Inicio: {get_timestamp()}")
        print(f"   🕐 Fin: {get_timestamp()}")
        print(f"   ⏱️  Carga IR: {format_duration(0, load_time - start_time)}")
        print(f"   ⏱️  Conversión: {format_duration(0, conversion_time - load_time)}")
        print(f"   ⏱️  Guardado: {format_duration(0, save_time - conversion_time)}")
        print(f"   ⏱️  Total: {format_duration(0, save_time - start_time)}")
        
        print("======================================================================")
        print("🎊 ¡ÉXITO! Conversión SOLID completada")
        print("✅ Conversión completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

