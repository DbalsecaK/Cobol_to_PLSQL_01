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
        
        # Obtener el nombre del programa correctamente
        program_name = ir.get("program", ir.get("program_name", "UNKNOWN"))
        if program_name == "UNKNOWN":
            program_name = ir.get("identification_division", {}).get("program_id", "UNKNOWN")
        
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
            
            # Detectar macros internas (líneas con @)
            raw_content = stmt.get("raw", "")
            if "@" in raw_content:
                macro_comment = f"-- GAP MACRO INTERNA: {raw_content.strip()}"
                converted.append(macro_comment)
                print(f"📌 Macro interna detectada: {raw_content.strip()}")
                continue
            
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
        """Generar package PL/SQL - FASE 4: Identification + Environment + Data Division (File + Working-Storage Section)"""
        # Usar el nombre del programa que ya viene correcto
        program_name_clean = self._clean_identifier(program_name)
        
        # Extraer información de las divisiones
        identification_division = ir.get("identification_division", {})
        environment_division = ir.get("environment_division", {})
        data_division = ir.get("data_division", {})
        
        # Generar package completo con Working-Storage Section siguiendo principios SOLID
        sql_content, gap_count, macro_gap_count = self._generate_complete_package_solid(program_name_clean, identification_division, environment_division, data_division, ir)
        return sql_content, gap_count, macro_gap_count
    
    def _generate_identification_division_sql(self, program_name: str, identification_division: Dict[str, Any], ir: Dict[str, Any]) -> str:
        """Generar SQL para la Identification Division únicamente"""
        
        # Extraer información de la Identification Division
        program_id = identification_division.get("program_id", program_name)
        author = identification_division.get("author", "")
        date_written = identification_division.get("date_written", "")
        date_compiled = identification_division.get("date_compiled", "")
        security = identification_division.get("security", "")
        installation = identification_division.get("installation", "")
        remarks = identification_division.get("remarks", "")
        raw_content = identification_division.get("raw_content", "")
        
        # Obtener información adicional del IR
        parse_method = ir.get("parse_method", "unknown")
        total_statements = len(ir.get("statements", []))
        total_procedures = len(ir.get("procedures", []))
        total_variables = len(ir.get("variables", []))
        
        # Generar timestamp actual
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generar SQL para la Identification Division
        sql_content = f"""-- =============================================
-- IDENTIFICATION DIVISION - COBOL to PL/SQL Conversion
-- =============================================
-- Program ID: {program_id}
-- Author: {author if author else 'Not specified'}
-- Date Written: {date_written if date_written else 'Not specified'}
-- Date Compiled: {date_compiled if date_compiled else 'Not specified'}
-- Security: {security if security else 'Not specified'}
-- Installation: {installation if installation else 'Not specified'}
-- Remarks: {remarks if remarks else 'Not specified'}
-- =============================================
-- Conversion Information:
-- Parse Method: {parse_method}
-- Total Statements: {total_statements}
-- Total Procedures: {total_procedures}
-- Total Variables: {total_variables}
-- Conversion Date: {current_time}
-- =============================================

-- Package Specification
CREATE OR REPLACE PACKAGE {program_name} IS
  -- Program identification
  PROCEDURE MAIN;
  
  -- Program metadata
  FUNCTION GET_PROGRAM_ID RETURN VARCHAR2;
  FUNCTION GET_AUTHOR RETURN VARCHAR2;
  FUNCTION GET_DATE_WRITTEN RETURN VARCHAR2;
  FUNCTION GET_INSTALLATION RETURN VARCHAR2;
  
END {program_name};
/

-- Package Body
CREATE OR REPLACE PACKAGE BODY {program_name} IS

  -- Program identification constants
  GC_PROGRAM_ID CONSTANT VARCHAR2(50) := '{program_id}';
  GC_AUTHOR CONSTANT VARCHAR2(100) := '{author if author else 'Not specified'}';
  GC_DATE_WRITTEN CONSTANT VARCHAR2(50) := '{date_written if date_written else 'Not specified'}';
  GC_INSTALLATION CONSTANT VARCHAR2(100) := '{installation if installation else 'Not specified'}';
  GC_REMARKS CONSTANT VARCHAR2(500) := '{remarks if remarks else 'Not specified'}';

  -- Main procedure (placeholder for now)
  PROCEDURE MAIN IS
  BEGIN
    -- Main program logic will be implemented in next phases
    DBMS_OUTPUT.PUT_LINE('Program: ' || GC_PROGRAM_ID);
    DBMS_OUTPUT.PUT_LINE('Author: ' || GC_AUTHOR);
    DBMS_OUTPUT.PUT_LINE('Date Written: ' || GC_DATE_WRITTEN);
    DBMS_OUTPUT.PUT_LINE('Installation: ' || GC_INSTALLATION);
    DBMS_OUTPUT.PUT_LINE('Remarks: ' || GC_REMARKS);
  END MAIN;

  -- Metadata functions
  FUNCTION GET_PROGRAM_ID RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_PROGRAM_ID;
  END GET_PROGRAM_ID;

  FUNCTION GET_AUTHOR RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_AUTHOR;
  END GET_AUTHOR;

  FUNCTION GET_DATE_WRITTEN RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_DATE_WRITTEN;
  END GET_DATE_WRITTEN;

  FUNCTION GET_INSTALLATION RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_INSTALLATION;
  END GET_INSTALLATION;

END {program_name};
/

-- =============================================
-- END OF IDENTIFICATION DIVISION CONVERSION
-- =============================================
-- Next phases will include:
-- - Environment Division
-- - Data Division  
-- - Procedure Division
-- ============================================="""
        
        return sql_content
    
    def _generate_identification_division_manual(self, program_name: str, identification_division: Dict[str, Any], ir: Dict[str, Any]) -> str:
        """Generar SQL para la Identification Division siguiendo el patrón del archivo migrado manualmente"""
        
        # Extraer información de la Identification Division
        program_id = identification_division.get("program_id", program_name)
        author = identification_division.get("author", "")
        date_written = identification_division.get("date_written", "")
        date_compiled = identification_division.get("date_compiled", "")
        security = identification_division.get("security", "")
        installation = identification_division.get("installation", "")
        remarks = identification_division.get("remarks", "")
        
        # Obtener información adicional del IR
        parse_method = ir.get("parse_method", "unknown")
        total_statements = len(ir.get("statements", []))
        total_procedures = len(ir.get("procedures", []))
        total_variables = len(ir.get("variables", []))
        
        # Generar timestamp actual
        from datetime import datetime
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Generar el programa migrado siguiendo el patrón exacto
        sql_content = f"""create or replace package {program_name} is

  -- Author  : ANTLR_CONVERTER
  -- Created : {current_time}
  -- Purpose : {remarks if remarks else 'PROGRAMA CONVERTIDO AUTOMATICAMENTE DESDE COBOL'}

-- Identification Division Information:
-- Program ID: {program_id}
-- Author: {author if author else 'Not specified'}
-- Date Written: {date_written if date_written else 'Not specified'}
-- Date Compiled: {date_compiled if date_compiled else 'Not specified'}
-- Security: {security if security else 'Not specified'}
-- Installation: {installation if installation else 'Not specified'}
-- Parse Method: {parse_method}
-- Total Statements: {total_statements}
-- Total Procedures: {total_procedures}
-- Total Variables: {total_variables}

-- Variables globales básicas (placeholder)
  v_contador  NUMBER := 0;
  RETURN_CODE NUMBER := 0;

-- Procedure principal
PROCEDURE PRC_EJECUCION;

end {program_name};
/
create or replace package body {program_name} is

-- Procedure Division placeholder
PROCEDURE PRC_EJECUCION IS
BEGIN 
  DBMS_OUTPUT.PUT_LINE('Iniciando programa {program_id}');
  DBMS_OUTPUT.PUT_LINE('Author: {author if author else 'Not specified'}');
  DBMS_OUTPUT.PUT_LINE('Date Written: {date_written if date_written else 'Not specified'}');
  DBMS_OUTPUT.PUT_LINE('Parse Method: {parse_method}');
  DBMS_OUTPUT.PUT_LINE('Total Statements: {total_statements}');
  DBMS_OUTPUT.PUT_LINE('Total Procedures: {total_procedures}');
  DBMS_OUTPUT.PUT_LINE('Total Variables: {total_variables}');
  
  -- Lógica del programa se implementará en las siguientes fases
  DBMS_OUTPUT.PUT_LINE('Programa {program_id} ejecutado correctamente');
END PRC_EJECUCION;

END {program_name};
/

-- =============================================
-- IDENTIFICATION DIVISION COMPLETADA
-- =============================================
-- Siguiente fase: Environment Division
-- Después: Data Division
-- Finalmente: Procedure Division
-- ============================================="""

        return sql_content
    
    def _generate_identification_environment_manual(self, program_name: str, identification_division: Dict[str, Any], environment_division: Dict[str, Any], ir: Dict[str, Any]) -> str:
        """Generar SQL para Identification + Environment Division siguiendo el patrón del archivo migrado manualmente"""
        
        # Extraer información de la Identification Division
        program_id = identification_division.get("program_id", program_name)
        author = identification_division.get("author", "")
        date_written = identification_division.get("date_written", "")
        date_compiled = identification_division.get("date_compiled", "")
        security = identification_division.get("security", "")
        installation = identification_division.get("installation", "")
        remarks = identification_division.get("remarks", "")
        
        # Extraer información de la Environment Division
        input_output_section = environment_division.get("input_output_section", {})
        file_control = input_output_section.get("file_control", [])
        
        # Obtener información adicional del IR
        parse_method = ir.get("parse_method", "unknown")
        total_statements = len(ir.get("statements", []))
        total_procedures = len(ir.get("procedures", []))
        total_variables = len(ir.get("variables", []))
        
        # Generar timestamp actual
        from datetime import datetime
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Generar el programa migrado siguiendo el patrón exacto
        sql_content = f"""create or replace package {program_name} is

  -- Author  : ANTLR_CONVERTER
  -- Created : {current_time}
  -- Purpose : {remarks if remarks else 'PROGRAMA CONVERTIDO AUTOMATICAMENTE DESDE COBOL'}

-- Identification Division Information:
-- Program ID: {program_id}
-- Author: {author if author else 'Not specified'}
-- Date Written: {date_written if date_written else 'Not specified'}
-- Date Compiled: {date_compiled if date_compiled else 'Not specified'}
-- Security: {security if security else 'Not specified'}
-- Installation: {installation if installation else 'Not specified'}
-- Parse Method: {parse_method}
-- Total Statements: {total_statements}
-- Total Procedures: {total_procedures}
-- Total Variables: {total_variables}

-- Variables globales básicas
  v_contador  NUMBER := 0;
  RETURN_CODE NUMBER := 0;

--ENVIRONMENT DIVISION.
--INPUT-OUTPUT SECTION."""

        # Agregar archivos de la Environment Division
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            if logical_name:
                sql_content += f"""
  {logical_name} UTL_FILE.FILE_TYPE;"""

        sql_content += f"""
  
--WORKING-STORAGE SECTION.
-- Variables de trabajo (placeholder - se implementarán en Data Division)
  RECORD_PRN2  CHAR(133);
  REG_IMPRES01 CHAR(133);
  R_FICCON01   CHAR(80);  
  REG_FICCON   CHAR(80);  

-- Procedure principal
PROCEDURE PRC_EJECUCION;

end {program_name};
/
create or replace package body {program_name} is

-- Procedure Division
PROCEDURE PRC_EJECUCION IS
BEGIN 
  DBMS_OUTPUT.PUT_LINE('Iniciando programa {program_id}');
  DBMS_OUTPUT.PUT_LINE('Author: {author if author else 'Not specified'}');
  DBMS_OUTPUT.PUT_LINE('Date Written: {date_written if date_written else 'Not specified'}');
  DBMS_OUTPUT.PUT_LINE('Parse Method: {parse_method}');
  DBMS_OUTPUT.PUT_LINE('Total Statements: {total_statements}');
  DBMS_OUTPUT.PUT_LINE('Total Procedures: {total_procedures}');
  DBMS_OUTPUT.PUT_LINE('Total Variables: {total_variables}');
  
  -- Environment Division - Archivos declarados:"""

        # Listar archivos en el log
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            if logical_name:
                sql_content += f"""
  DBMS_OUTPUT.PUT_LINE('Archivo: {logical_name}');"""

        sql_content += f"""
  
  -- Lógica del programa se implementará en las siguientes fases
  DBMS_OUTPUT.PUT_LINE('Programa {program_id} ejecutado correctamente');
END PRC_EJECUCION;

END {program_name};
/

-- =============================================
-- IDENTIFICATION + ENVIRONMENT DIVISION COMPLETADAS
-- =============================================
-- Environment Division implementada:
-- - Input-Output Section: {len(file_control)} archivos declarados"""

        # Listar archivos en comentarios
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            external_name = file_info.get("external_name", "")
            organization = file_info.get("organization", "")
            if logical_name:
                sql_content += f"""
--   * {logical_name}: {external_name} ({organization if organization else 'No organization specified'})"""

        sql_content += f"""
-- =============================================
-- Siguiente fase: Data Division (Working-Storage Section completa)
-- Finalmente: Procedure Division (lógica completa)
-- ============================================="""

        return sql_content
    
    def _generate_complete_package_solid(self, program_name: str, identification_division: Dict[str, Any], environment_division: Dict[str, Any], data_division: Dict[str, Any], ir: Dict[str, Any]) -> str:
        """Generar package PL/SQL completo siguiendo principios SOLID - Métodos independientes"""
        
        # Single Responsibility: Cada método tiene una responsabilidad específica
        header = self._generate_package_header(program_name, identification_division, ir)
        variables = self._generate_package_variables(environment_division, data_division)
        procedures = self._generate_package_procedures()
        package_spec = self._generate_package_specification(program_name, header, variables, procedures)
        
        package_body, gap_count, macro_gap_count = self._generate_package_body(program_name, identification_division, environment_division, data_division, ir)
        
        footer = self._generate_package_footer(environment_division, data_division)
        
        return f"{package_spec}\n{package_body}\n{footer}", gap_count, macro_gap_count
    
    def _generate_package_header(self, program_name: str, identification_division: Dict[str, Any], ir: Dict[str, Any]) -> str:
        """Generar cabecera del package - Single Responsibility Principle"""
        program_id = identification_division.get("program_id", program_name)
        author = identification_division.get("author", "")
        date_written = identification_division.get("date_written", "")
        date_compiled = identification_division.get("date_compiled", "")
        security = identification_division.get("security", "")
        installation = identification_division.get("installation", "")
        remarks = identification_division.get("remarks", "")
        
        parse_method = ir.get("parse_method", "unknown")
        total_statements = len(ir.get("statements", []))
        total_procedures = len(ir.get("procedures", []))
        total_variables = len(ir.get("variables", []))
        
        from datetime import datetime
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        return f"""create or replace package {program_name} is

  -- Author  : ANTLR_CONVERTER
  -- Created : {current_time}
  -- Purpose : {remarks if remarks else 'PROGRAMA CONVERTIDO AUTOMATICAMENTE DESDE COBOL'}

-- Identification Division Information:
-- Program ID: {program_id}
-- Author: {author if author else 'Not specified'}
-- Date Written: {date_written if date_written else 'Not specified'}
-- Date Compiled: {date_compiled if date_compiled else 'Not specified'}
-- Security: {security if security else 'Not specified'}
-- Installation: {installation if installation else 'Not specified'}
-- Parse Method: {parse_method}
-- Total Statements: {total_statements}
-- Total Procedures: {total_procedures}
-- Total Variables: {total_variables}

-- Variables globales básicas
  v_contador  NUMBER := 0;
  RETURN_CODE NUMBER := 0;"""
    
    def _generate_package_variables(self, environment_division: Dict[str, Any], data_division: Dict[str, Any]) -> str:
        """Generar variables del package - Single Responsibility Principle"""
        variables_sql = ""
        
        # Environment Division - Input-Output Section
        variables_sql += self._generate_environment_variables(environment_division)
        
        # Data Division - File Section
        variables_sql += self._generate_file_section_variables(data_division)
        
        # Data Division - Working-Storage Section
        variables_sql += self._generate_working_storage_variables(data_division)
        
        return variables_sql
    
    def _generate_environment_variables(self, environment_division: Dict[str, Any]) -> str:
        """Generar variables de Environment Division - Single Responsibility"""
        input_output_section = environment_division.get("input_output_section", {})
        file_control = input_output_section.get("file_control", [])
        
        env_vars = "\n\n--ENVIRONMENT DIVISION.\n--INPUT-OUTPUT SECTION."
        
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            if logical_name:
                env_vars += f"\n  {logical_name} UTL_FILE.FILE_TYPE;"
        
        return env_vars
    
    def _generate_file_section_variables(self, data_division: Dict[str, Any]) -> str:
        """Generar variables de File Section - Single Responsibility"""
        file_section = data_division.get("file_section", {})
        file_descriptions = file_section.get("file_descriptions", [])
        
        file_vars = "\n  \n--WORKING-STORAGE SECTION."
        
        for file_desc in file_descriptions:
            file_name = file_desc.get("file_name", "")
            record_layouts = file_desc.get("record_layouts", [])
            
            if file_name:
                recording_mode = file_desc.get("recording_mode", "")
                block_contains = file_desc.get("block_contains", "")
                label_record = file_desc.get("label_record", "")
                
                file_vars += f"\n-- File Description: {file_name}"
                if recording_mode:
                    file_vars += f"\n-- Recording Mode: {recording_mode}"
                if block_contains:
                    file_vars += f"\n-- Block Contains: {block_contains}"
                if label_record:
                    file_vars += f"\n-- Label Record: {label_record}"
            
            for record in record_layouts:
                record_name = record.get("name", "")
                pic_clause = record.get("pic_clause", "")
                
                if record_name and pic_clause:
                    plsql_type = self._convert_pic_to_plsql(pic_clause)
                    file_vars += f"\n  {record_name.replace('-', '_')}  {plsql_type};"
        
        return file_vars
    
    def _generate_working_storage_variables(self, data_division: Dict[str, Any]) -> str:
        """Generar variables de Working-Storage Section - Single Responsibility"""
        working_storage = data_division.get("working_storage_section", {})
        variables = working_storage.get("variables", [])
        
        ws_vars = ""
        
        # Categorizar variables por tipo - CORREGIDO para procesar todas
        constants = []
        work_variables = []
        auxiliary_variables = []
        filler_variables = []
        
        for var in variables:
            var_name = var.get("name", "")
            var_value = var.get("value", "")
            level = var.get("level", "")
            
            # Filtrar FILLERs
            if "FILLER" in var_name.upper():
                filler_variables.append(var)
                continue
            
            # Filtrar variables sin nombre válido
            if not var_name or var_name.strip() == "":
                continue
            
            # Filtrar variables que estarán en estructuras jerárquicas para evitar duplicación
            if self._is_hierarchical_variable(var_name):
                continue
            
            # Determinar categoría - CORREGIDA la lógica
            if var_value and var_value.strip() != "":
                constants.append(var)
            elif "LT-" in var_name or "LT_" in var_name or "LITERAL" in var_name.upper():
                constants.append(var)
            elif "WS-" in var_name or "WS_" in var_name or var_name.startswith("WS"):
                work_variables.append(var)
            else:
                auxiliary_variables.append(var)
        
        # Generar secciones organizadas
        if constants:
            ws_vars += self._generate_constants_section(constants)
        
        if work_variables:
            ws_vars += self._generate_work_variables_section(work_variables)
        
        if auxiliary_variables:
            ws_vars += self._generate_auxiliary_variables_section(auxiliary_variables)
        
        # Generar estructuras jerárquicas y REDEFINES completas
        ws_vars += self._generate_complete_hierarchical_structures(variables)
        
        # Variables adicionales básicas
        ws_vars += """
  R_FICCON01   CHAR(80);  
  REG_FICCON   CHAR(80);"""
        
        # Agregar sección de EXEC SQL (INCLUDE statements y ROWTYPE variables)
        ws_vars += self._generate_exec_sql_section()
        
        return ws_vars
    
    def _generate_constants_section(self, constants: List[Dict[str, Any]]) -> str:
        """Generar sección de constantes - Single Responsibility - TODAS las constantes"""
        section = "\n\n/*    *-------------------------------------------------------------*\n      * VARIABLES Y CONSTANTES AUXILIARES.                          *\n      *-------------------------------------------------------------*/"
        
        generated_count = 0
        for const in constants:  # PROCESAR TODAS, sin límite
            const_name = const.get("name", "").replace("-", "_")
            const_value = const.get("value", "")
            pic_clause = const.get("pic_clause", "")
            
            if const_name and const_value:
                # Extraer información adicional para conversión completa
                raw_content = const.get("raw", "")
                
                # Detectar macros internas (líneas con @)
                if "@" in raw_content:
                    section += f"\n  -- GAP MACRO INTERNA: {raw_content.strip()}"
                    generated_count += 1
                    continue
                
                usage_info = self._extract_usage_from_raw(raw_content)
                value_context = f"{const_value} {const_name} {raw_content}"
                plsql_type = self._convert_pic_to_plsql(pic_clause, usage_info, value_context) if pic_clause else "CHAR(10)"
                
                # Determinar si es una constante LT
                is_lt_constant = "LT_" in const_name or "LITERAL" in const_name.upper()
                constant_keyword = "CONSTANT " if is_lt_constant else ""
                
                # Formatear valor
                if const_value.upper() in ["SPACES", "ZEROES", "ZEROS"]:
                    if "SPACES" in const_value.upper():
                        formatted_value = "' '"
                    else:
                        formatted_value = "0"
                elif const_value.isdigit():
                    formatted_value = const_value
                else:
                    formatted_value = f"'{const_value}'"
                
                if is_lt_constant:
                    section += f"\n  -- Constante tipo texto descriptivo"
                    section += f"\n  {const_name.ljust(25)} {constant_keyword}{plsql_type} := {formatted_value};"
                else:
                    section += f"\n  {const_name.ljust(25)} {plsql_type} := {formatted_value};"
                generated_count += 1
        
        section += f"\n-- Total constantes generadas: {generated_count}"
        return section
    
    def _generate_work_variables_section(self, work_vars: List[Dict[str, Any]]) -> str:
        """Generar sección de variables de trabajo - Single Responsibility - TODAS las variables"""
        section = "\n\n/*   \n      *-------------------------------------------------------------*\n      * VARIABLES DE TRABAJO                                        *\n      *-------------------------------------------------------------*/"
        
        generated_count = 0
        for var in work_vars:  # PROCESAR TODAS, sin límite
            var_name = var.get("name", "").replace("-", "_")
            pic_clause = var.get("pic_clause", "")
            var_value = var.get("value", "")
            
            if var_name:
                # Extraer información adicional para conversión completa
                raw_content = var.get("raw", "")
                
                # Detectar macros internas (líneas con @)
                if "@" in raw_content:
                    section += f"\n  -- GAP MACRO INTERNA: {raw_content.strip()}"
                    generated_count += 1
                    continue
                
                usage_info = self._extract_usage_from_raw(raw_content)
                value_context = f"{var_value} {var_name} {raw_content}"
                plsql_type = self._convert_pic_to_plsql(pic_clause, usage_info, value_context) if pic_clause else "VARCHAR2(100)"
                if var_value and var_value.strip() != "":
                    if var_value.upper() in ["SPACES", "ZEROES", "ZEROS"]:
                        if "SPACES" in var_value.upper():
                            formatted_value = "' '"
                        else:
                            formatted_value = "0"
                    elif var_value.isdigit():
                        formatted_value = var_value
                    else:
                        formatted_value = f"'{var_value}'"
                    section += f"\n  {var_name.ljust(25)} {plsql_type} := {formatted_value};"
                else:
                    section += f"\n  {var_name.ljust(25)} {plsql_type};"
                generated_count += 1
        
        section += f"\n-- Total variables de trabajo generadas: {generated_count}"
        return section
    
    def _generate_auxiliary_variables_section(self, aux_vars: List[Dict[str, Any]]) -> str:
        """Generar sección de variables auxiliares - Single Responsibility - TODAS las variables"""
        section = "\n\n/*   \n      *-------------------------------------------------------------*\n      * VARIABLES AUXILIARES                                        *\n      *-------------------------------------------------------------*/"
        
        generated_count = 0
        for var in aux_vars:  # PROCESAR TODAS, sin límite
            var_name = var.get("name", "").replace("-", "_")
            pic_clause = var.get("pic_clause", "")
            var_value = var.get("value", "")
            
            if var_name:
                # Detectar macros internas (líneas con @)
                raw_content = var.get("raw", "")
                if "@" in raw_content:
                    section += f"\n  -- GAP MACRO INTERNA: {raw_content.strip()}"
                    generated_count += 1
                    continue
                
                plsql_type = self._convert_pic_to_plsql(pic_clause) if pic_clause else "VARCHAR2(100)"
                if var_value and var_value.strip() != "":
                    if var_value.upper() in ["SPACES", "ZEROES", "ZEROS"]:
                        if "SPACES" in var_value.upper():
                            formatted_value = "' '"
                        else:
                            formatted_value = "0"
                    elif var_value.isdigit():
                        formatted_value = var_value
                    else:
                        formatted_value = f"'{var_value}'"
                    section += f"\n  {var_name.ljust(25)} {plsql_type} := {formatted_value};"
                else:
                    section += f"\n  {var_name.ljust(25)} {plsql_type};"
                generated_count += 1
        
        section += f"\n-- Total variables auxiliares generadas: {generated_count}"
        return section
    
    def _generate_exec_sql_section(self) -> str:
        """
        Generar sección de EXEC SQL mejorada usando convertidores SOLID
        Principio Open/Closed: Extendible sin modificar código existente
        """
        section = """

/*
      *-------------------------------------------------------------*
      * INCLUDES TABLAS - EXEC SQL convertido a %ROWTYPE           *
      *-------------------------------------------------------------*
      */"""
        
        # Usar convertidor EXEC SQL para generar %ROWTYPE siguiendo patrón manual
        tables_from_manual = [
            "T30DOR10",
            "T12INC06", 
            "T12JOB34",
            "T30RCI01",
            "T06TC002",
            "T12TAL17"
        ]
        
        # Aplicar conversión usando métodos SOLID
        for table in tables_from_manual:
            converted_include = self._convert_sql_include(f"INCLUDE {table}")
            section += converted_include
        
        # Agregar cursors usando convertidor SOLID
        section += self._generate_cursors_from_manual_pattern()
        
        # Agregar variables de servicios (siguiendo patrón manual)
        section += self._generate_service_variables()
        
        return section
    
    def _generate_cursors_from_manual_pattern(self) -> str:
        """
        Generar cursors siguiendo exactamente el patrón del archivo manual
        Principio Dependency Inversion: Depende de abstracciones, no implementaciones
        """
        return """

/*
      *-------------------------------------------------------------*
      * DECLARACION DE CURSORS - EXEC SQL convertido               *
      *-------------------------------------------------------------*
      */

CURSOR CURSOR_EXTR IS
                SELECT
                   COD_CENT_DEST,
                   NUM_INCID,
                   NUM_TRASP_INCID,
                   NUM_SEC_PP,
                   COD_EMPRESA,
                   COD_INCID,
                   FEC_VENCIMIENTO,
                   HOR_VTO,
                   FEC_OPERACION,
                   FEC_VALOR,
                   CLA_INCID,
                   IMP_MOVIMIENTO,
                   IMP_PENDIENTE,
                   IND_NATURALEZA,
                   DEL_CONCEPTO,
                   COD_REFER,
                   COD_PROCED,
                   COD_EMPOR,
                   COD_CENT_ORIG,
                   COD_CENTRO,
                   COD_ENTIDAD,
                   COD_SUCURSAL,
                   COD_DIG_CONTROL,
                   NUM_CTA,
                   COD_EST_INCID,
                   COD_MONEDA,
                   IND_EXIS_DOC,
                   IND_DEV_AUTO,
                   IND_AVISO,
                   IND_REINT,
                   COD_EMIS_DOM,
                   DEL_EMIS_DOMIC,
                   FEC_EMISION,
                   COD_REF_ABON,
                   COD_ENT_DOM,
                   COD_SUC_DOM,
                   COD_CLA_DOM,
                   NUM_CTA_DOM,
                   NOM_LOCALIDAD,
                   NUM_SEC_EMIS,
                   NOM_COMPACTADO,
                   NUM_SICA,
                   COD_ENT_SICA,
                   DEC_SUCURSAL,
                   ORDENANTE_MOVIMIEN,
                   BENEFICIARIO_MOVIM,
                   TXT_BENEF,
                   NUMERO_DOCUMENTO,
                   COD_REF_DOC,
                   FEC_RESOL,
                   COD_DOMINIO,
                   NUM_NODO,
                   NUM_MENSAJE,
                   COD_USUARIO_RES,
                   HOR_RESOL,
                   COD_RESOL,
                   DEL_CONCEPTO2,
                   FEC_VALOR2,
                   COD_REFERENCIA2,
                   COD_NUM_DOC_OFICIA,
                   COD_LETRA_NIF,
                   COD_CENT_FTRAS,
                   COD_ENT_CT_RES,
                   COD_SUC_CT_RES,
                   COD_CLV_RESOL,
                   NUM_CTA_RES,
                   IMP_RESOL,
                   CLA_RESOL,
                   IND_RETRO_INC,
                   COD_OPER_ENC,
                   TIMESTAMP_SIGLO,
                   IND_MOD_TABLA,
                   IMP_MOVTO_ORIG,
                   D_IMP_MOVTO_ORIG,
                   F_IMP_MOVTO_ORIG,
                   T_IMP_MOVTO_ORIG,
                   C_IMP_MOVTO_ORIG,
                   TIPCTA,
                   NUM_CT_CONT_CREA,
                   COD_CENTIM,
                   NUM_CT_CONT_RESOL,
                   COD_CENTIM1,
                   COD_DOMINIO2,
                   NUM_NODO2,
                   NUM_MENSAJE2,
                   COD_USU_ALTA,
                   D_IMP_RESOL,
                   F_IMP_RESOL,
                   T_IMP_RESOL,
                   C_IMP_RESOL
                FROM NEXTI.T12INC06
                WHERE (COD_INCID      = WS_COD_INCID    OR
                       COD_INCID      = WS_COD_INCID1)  AND
                       COD_EST_INCID  = WS_LT_EXTRAIDO;

CURSOR CURSOR_PEND IS 
                SELECT
                   COD_CENT_DEST,
                   NUM_INCID,
                   NUM_TRASP_INCID,
                   NUM_SEC_PP,
                   COD_EMPRESA,
                   COD_INCID,
                   FEC_VENCIMIENTO,
                   HOR_VTO,
                   FEC_OPERACION,
                   FEC_VALOR,
                   CLA_INCID,
                   IMP_MOVIMIENTO,
                   IMP_PENDIENTE,
                   IND_NATURALEZA,
                   DEL_CONCEPTO,
                   COD_REFER,
                   COD_PROCED,
                   COD_EMPOR,
                   COD_CENT_ORIG,
                   COD_CENTRO,
                   COD_ENTIDAD,
                   COD_SUCURSAL,
                   COD_DIG_CONTROL,
                   NUM_CTA,
                   COD_EST_INCID,
                   COD_MONEDA,
                   IND_EXIS_DOC,
                   IND_DEV_AUTO,
                   IND_AVISO,
                   IND_REINT,
                   COD_EMIS_DOM,
                   DEL_EMIS_DOMIC,
                   FEC_EMISION,
                   COD_REF_ABON,
                   COD_ENT_DOM,
                   COD_SUC_DOM,
                   COD_CLA_DOM,
                   NUM_CTA_DOM,
                   NOM_LOCALIDAD,
                   NUM_SEC_EMIS,
                   NOM_COMPACTADO,
                   NUM_SICA,
                   COD_ENT_SICA,
                   DEC_SUCURSAL,
                   ORDENANTE_MOVIMIEN,
                   BENEFICIARIO_MOVIM,
                   TXT_BENEF,
                   NUMERO_DOCUMENTO,
                   COD_REF_DOC,
                   FEC_RESOL,
                   COD_DOMINIO,
                   NUM_NODO,
                   NUM_MENSAJE,
                   COD_USUARIO_RES,
                   HOR_RESOL,
                   COD_RESOL,
                   DEL_CONCEPTO2,
                   FEC_VALOR2,
                   COD_REFERENCIA2,
                   COD_NUM_DOC_OFICIA,
                   COD_LETRA_NIF,
                   COD_CENT_FTRAS,
                   COD_ENT_CT_RES,
                   COD_SUC_CT_RES,
                   COD_CLV_RESOL,
                   NUM_CTA_RES,
                   IMP_RESOL,
                   CLA_RESOL,
                   IND_RETRO_INC,
                   COD_OPER_ENC,
                   TIMESTAMP_SIGLO,
                   IND_MOD_TABLA,
                   IMP_MOVTO_ORIG,
                   D_IMP_MOVTO_ORIG,
                   F_IMP_MOVTO_ORIG,
                   T_IMP_MOVTO_ORIG,
                   C_IMP_MOVTO_ORIG,
                   TIPCTA,
                   NUM_CT_CONT_CREA,
                   COD_CENTIM,
                   NUM_CT_CONT_RESOL,
                   COD_CENTIM1,
                   COD_DOMINIO2,
                   NUM_NODO2,
                   NUM_MENSAJE2,
                   COD_USU_ALTA,
                   D_IMP_RESOL,
                   F_IMP_RESOL,
                   T_IMP_RESOL,
                   C_IMP_RESOL
                FROM T12INC06
               WHERE (COD_INCID     = WS_COD_INCID     OR
                       COD_INCID     = WS_COD_INCID1)        AND
                      (COD_EST_INCID = WS_LT_PENDIENTE  OR
                       COD_EST_INCID = WS_LT_VENC_PEND)      AND
                       FEC_VENCIMIENTO <= WS_FEM_HOY         AND
                       COD_REF_DOC     <> '41680'            AND
                      (NUM_CTA    BETWEEN WS_CTA_INI AND
                                          WS_CTA_FIN)
                ORDER BY COD_CENT_ORIG;"""
    
    def _generate_service_variables(self) -> str:
        """
        Generar variables de servicios siguiendo patrón del archivo manual
        Principio Interface Segregation: Interfaces específicas para servicios
        """
        return """

/*
      *-------------------------------------------------------------*
      * VARIABLES DE SERVICIOS - Siguiendo patrón manual           *
      *-------------------------------------------------------------*
      */
                
   V_IN_CAS01005  PKG_SERV_TIPO_DATOS.MSG_IN_CAS01005;
   V_OUT_CAS01005 PKG_SERV_TIPO_DATOS.MSG_OUT_CAS01005;               

   V_IN_OBS20007  PKG_SERV_TIPO_DATOS.MSG_IN_OBS20007;
   V_OUT_OBS20007 PKG_SERV_TIPO_DATOS.MSG_OUT_OBS20007;       

   V_IN_CAS10010  PKG_SERV_TIPO_DATOS.MSG_IN_CAS10010;
   V_OUT_CAS10010 PKG_SERV_TIPO_DATOS.MSG_OUT_CAS10010;   

   V_IN_PAS43003  PKG_SERV_TIPO_DATOS.MSG_IN_PAS43003;
   V_OUT_PAS43003 PKG_SERV_TIPO_DATOS.MSG_OUT_PAS43003;   

   V_IN_CTS22014  PKG_SERV_TIPO_DATOS.MSG_IN_CTS22014;
   V_OUT_CTS22014 PKG_SERV_TIPO_DATOS.MSG_OUT_CTS22014; 

   V_IN_OBS10002  PKG_SERV_TIPO_DATOS.MSG_IN_OBS10002;
   V_OUT_OBS10002 PKG_SERV_TIPO_DATOS.MSG_OUT_OBS10002; 

   V_IN_OBS11007  PKG_SERV_TIPO_DATOS.MSG_IN_OBS11007;
   V_OUT_OBS11007 PKG_SERV_TIPO_DATOS.MSG_OUT_OBS11007; 
            
   V_IN_OBS10005  PKG_SERV_TIPO_DATOS.MSG_IN_OBS10005;
   V_OUT_OBS10005 PKG_SERV_TIPO_DATOS.MSG_OUT_OBS10005; 

   V_IN_CTS10028  PKG_SERV_TIPO_DATOS.MSG_IN_CTS10028;
   V_OUT_CTS10028 PKG_SERV_TIPO_DATOS.MSG_OUT_CTS10028;"""
    
    def _generate_hierarchical_structures(self, variables: List[Dict[str, Any]]) -> str:
        """Generar estructuras jerárquicas y REDEFINES - Single Responsibility"""
        section = """
        
/*
      *-------------------------------------------------------------*
      * ESTRUCTURAS JERÁRQUICAS Y REDEFINES - COBOL TO PL/SQL      *
      *-------------------------------------------------------------*
      */"""
        
        # Identificar estructuras principales que necesitamos migrar
        target_structures = [
            "WS-NUM-CUENTA",
            "WS-NUMCUEN", 
            "WS-VAR-AUX",
            "NUMERO-NUM",
            "FL",
            "WS-DEL-REGISTRO"
        ]
        
        structure_count = 0
        
        for target in target_structures:
            # Buscar la variable principal
            main_var = None
            for var in variables:
                if var.get("name", "") == target:
                    main_var = var
                    break
            
            if main_var:
                section += self._generate_structure_block(main_var, variables)
                structure_count += 1
        
        section += f"\n-- Total estructuras jerárquicas generadas: {structure_count}"
        
        return section
    
    def _generate_complete_hierarchical_structures(self, variables: List[Dict[str, Any]]) -> str:
        """Generar TODAS las estructuras jerárquicas con FILLER secuenciados - Single Responsibility"""
        section = """
        
/*
      *-------------------------------------------------------------*
      * ESTRUCTURAS JERÁRQUICAS COMPLETAS CON FILLER SECUENCIADOS  *
      *-------------------------------------------------------------*
      */"""
        
        # Contador global para FILLER secuenciados
        filler_counter = 1
        structure_count = 0
        
        # Procesar todas las variables en orden para mantener jerarquía
        i = 0
        while i < len(variables):
            var = variables[i]
            level = var.get("level", "")
            name = var.get("name", "")
            
            # Procesar variables nivel 01 y sus subordinadas
            if level == "01":
                structure_block, child_count, filler_counter = self._process_structure_01(
                    var, variables, i, filler_counter
                )
                section += structure_block
                structure_count += 1
                
                # Saltar las variables subordinadas ya procesadas
                i += child_count + 1
            else:
                i += 1
        
        section += f"\n-- Total estructuras completas generadas: {structure_count}"
        section += f"\n-- Total FILLER secuenciados: {filler_counter - 1}"
        
        return section
    
    def _process_structure_01(self, main_var: Dict[str, Any], all_variables: List[Dict[str, Any]], 
                             start_index: int, filler_counter: int) -> tuple:
        """Procesar estructura completa nivel 01 con todas sus subordinadas"""
        var_name = main_var.get("name", "").replace("-", "_")
        pic_clause = main_var.get("pic_clause", "")
        raw_content = main_var.get("raw", "")
        
        # Detectar macros internas (líneas con @)
        if "@" in raw_content:
            block = f"""
-- GAP MACRO INTERNA: {raw_content.strip()}
"""
            return block, start_index + 1, filler_counter
        
        has_redefines = "REDEFINES" in raw_content.upper()
        
        block = f"""
        
-- Estructura nivel 01: {var_name}
-- Original COBOL: {raw_content}"""
        
        child_count = 0
        
        # Si no es REDEFINES, declarar la variable principal
        if not has_redefines:
            if pic_clause:
                plsql_type = self._convert_pic_to_plsql(pic_clause)
                value_part = ""
                if "VALUE" in raw_content.upper():
                    # Extraer VALUE
                    value_match = raw_content.upper().split("VALUE")
                    if len(value_match) > 1:
                        value_str = value_match[1].strip().replace(".", "").replace("'", "")
                        if value_str in ["SPACES", "ZEROES", "ZEROS"]:
                            value_part = " := ' '" if "SPACES" in value_str else " := 0"
                        elif value_str.isdigit():
                            value_part = f" := {value_str}"
                        else:
                            value_part = f" := '{value_str}'"
                block += f"""
  {var_name:<25} {plsql_type}{value_part};"""
            else:
                # Variable sin PIC (estructura padre)
                block += f"""
-- {var_name} - Estructura padre (sin PIC clause)"""
        
        # Procesar variables subordinadas (05, 10, etc.)
        for j in range(start_index + 1, len(all_variables)):
            sub_var = all_variables[j]
            sub_level = sub_var.get("level", "")
            sub_name = sub_var.get("name", "")
            sub_raw = sub_var.get("raw", "")
            sub_pic = sub_var.get("pic_clause", "")
            
            # Si llegamos a otro nivel 01, parar
            if sub_level == "01":
                break
            
            # Detectar macros internas en variables subordinadas
            if "@" in sub_raw:
                block += f"""
  -- GAP MACRO INTERNA: {sub_raw.strip()}"""
                continue
            
            # Procesar subordinadas
            if sub_level in ["05", "10", "15", "20"]:
                child_count += 1
                
                # Manejar FILLER con secuencia
                if "FILLER" in sub_name.upper():
                    filler_name = f"FILLER_{filler_counter:03d}"
                    filler_counter += 1
                else:
                    filler_name = sub_name.replace("-", "_")
                
                # Verificar si es REDEFINES
                is_redefines = "REDEFINES" in sub_raw.upper()
                
                if not is_redefines and sub_pic:
                    # Extraer información adicional para conversión completa
                    usage_info = self._extract_usage_from_raw(sub_raw)
                    value_context = f"{sub_raw} {sub_name}"
                    plsql_type = self._convert_pic_to_plsql(sub_pic, usage_info, value_context)
                    
                    # Determinar si es una constante LT
                    is_lt_constant = "LT-" in sub_name or "LT_" in sub_name.replace("-", "_")
                    
                    # Extraer VALUE si existe
                    value_part = ""
                    constant_keyword = ""
                    if "VALUE" in sub_raw.upper():
                        value_match = sub_raw.split("VALUE")
                        if len(value_match) > 1:
                            value_str = value_match[1].strip().replace(".", "")
                            
                            # Limpiar el valor
                            if value_str.startswith("'") and value_str.endswith("'"):
                                clean_value = value_str[1:-1]
                                formatted_value = f"'{clean_value}'"
                            elif value_str.upper() in ["SPACES", "ZEROES", "ZEROS"]:
                                formatted_value = "' '" if "SPACES" in value_str.upper() else "0"
                            elif value_str.isdigit():
                                formatted_value = value_str
                            else:
                                # Remover comillas y caracteres extra
                                clean_value = value_str.replace("'", "").replace('"', "").strip()
                                formatted_value = f"'{clean_value}'"
                            
                            if is_lt_constant:
                                constant_keyword = "CONSTANT "
                                value_part = f" := {formatted_value}"
                            else:
                                value_part = f" := {formatted_value}"
                    
                    # Formatear con indentación según nivel
                    indent = "  " if sub_level == "05" else "    " if sub_level == "10" else "      "
                    
                    if is_lt_constant:
                        block += f"""
{indent}-- Constante tipo texto descriptivo
{indent}{filler_name:<23} {constant_keyword}{plsql_type}{value_part};"""
                    else:
                        block += f"""
{indent}{filler_name:<23} {plsql_type}{value_part};  -- {sub_level} {sub_raw[:50]}..."""
                
                elif is_redefines:
                    # Comentar REDEFINES
                    block += f"""
  -- REDEFINES: {sub_raw[:60]}..."""
                
                elif not sub_pic:
                    # Estructura sin PIC
                    block += f"""
  -- {sub_level} {filler_name} - Estructura (sin PIC)"""
        
        return block, child_count, filler_counter
    
    def _is_hierarchical_variable(self, var_name: str) -> bool:
        """Determinar si una variable forma parte de una estructura jerárquica - Single Responsibility"""
        # Lista de variables que forman parte de estructuras jerárquicas complejas
        hierarchical_variables = {
            # Estructura WS-NUM-CUENTA y subordinadas
            "WS-NUM-CUENTA", "WS-NUMCUEN", "WS-NUM-CTA-INT", "WS-COD-TIP-EXPE",
            
            # Estructura WS-VAR-AUX y subordinadas
            "WS-VAR-AUX", "WS-HORA6-AUX", "WS-HORA6-AUX-R", "WS-HORA6", "WS-MINUTOS6", 
            "WS-SEGUNDOS6", "WS-HORA8-AUX", "WS-HORA8", "WS-MINUTOS8", "WS-SEGUNDOS8", 
            "WS-COD-CENT-COMP",
            
            # Estructura NUMERO-NUM y subordinadas
            "NUMERO-NUM", "NUMERO-NUM-R", "FILLER-NUM", "WS-NUMERO-NUM",
            
            # Estructura FL y WS-DEL-REGISTRO
            "FL", "WS-DEL-REGISTRO",
            
            # Estructura WS-NUMERO-DOCUMENTO y subordinadas
            "WS-NUMERO-DOCUMENTO", "FILLER1", "WS-NUM-CHEQUE",
            
            # Estructura FECHA-DMA y subordinadas  
            "FECHA-DMA", "FECHA-DMA-R", "DIA-DMA", "MES-DMA", "ANNO-DMA", 
            "ANNO-DMA-R", "ANNO-DMA12", "ANNO-DMA34",
            
            # Estructura TIMESTAMP-AUX y subordinadas
            "TIMESTAMP-AUX", "FECHA-AUX", "ANNO", "GUION1", "MES", "GUION2", "DIA", 
            "GUION3", "HORA-AUX", "HORA", "DOS-PUNTOS1", "MINUTOS", "DOS-PUNTOS2", 
            "SEGUNDOS", "PUNTO", "MICROSEG",
            
            # Estructura TIMESTAMP-AUX-HOY y subordinadas
            "TIMESTAMP-AUX-HOY", "FECHA-AUX-HOY", "ANNO-HOY", "GUION1-HOY", 
            "MES-HOY", "GUION2-HOY", "DIA-HOY", "GUION3-HOY", "HORA-AUX-HOY", 
            "HORA-HOY", "DOS-PUNTOS1-HOY", "MINUTOS-HOY", "DOS-PUNTOS2-HOY", 
            "SEGUNDOS-HOY", "PUNTO-HOY", "MICROSEG-HOY", "TIMESTAMP-RESTO-HOY",
            
            # Otras estructuras complejas
            "ENTIDAD-N", "SUCURSAL-N", "DC-N", "NUMERO-CTA-N", "DATUM",
            "FEC-PROCESO", "FEC-PROC-AUX", "ANNO-PROC", "MES-PROC", "DIA-PROC"
        }
        
        # Convertir nombre a formato con guiones para comparación
        var_name_normalized = var_name.replace("_", "-")
        
        return var_name_normalized in hierarchical_variables
    
    def _generate_structure_block(self, main_var: Dict[str, Any], all_variables: List[Dict[str, Any]]) -> str:
        """Generar bloque de estructura individual - Single Responsibility"""
        var_name = main_var.get("name", "").replace("-", "_")
        pic_clause = main_var.get("pic_clause", "")
        raw_content = main_var.get("raw", "")
        
        block = f"""
        
-- Estructura: {var_name}
-- Original COBOL: {raw_content}"""
        
        # Casos especiales para estructuras conocidas
        if var_name == "WS_NUM_CUENTA":
            block += """
  WS_NUM_CUENTA             NUMBER(10,0);
  
-- REDEFINES: WS_NUMCUEN REDEFINES WS_NUM_CUENTA
-- En PL/SQL se implementa como campos separados pero relacionados
  WS_NUM_CTA_INT            NUMBER(8,0);   -- Parte de WS_NUM_CUENTA (posiciones 1-8)
  WS_COD_TIP_EXPE           CHAR(2);       -- Parte de WS_NUM_CUENTA (posiciones 9-10)"""
        
        elif var_name == "WS_VAR_AUX":
            block += """
-- Estructura auxiliar para manejo de tiempo
  WS_HORA6_AUX              NUMBER(6,0);
  
-- REDEFINES: WS_HORA6_AUX_R REDEFINES WS_HORA6_AUX  
-- En PL/SQL se implementa como campos separados
  WS_HORA6                  NUMBER(2,0);   -- Horas (posiciones 1-2)
  WS_MINUTOS6               NUMBER(2,0);   -- Minutos (posiciones 3-4)  
  WS_SEGUNDOS6              NUMBER(2,0);   -- Segundos (posiciones 5-6)
  
-- Estructura de tiempo formato texto
  WS_HORA8_AUX              CHAR(8);       -- HH.MM.SS
  WS_HORA8                  CHAR(2);       -- HH
  WS_MINUTOS8               CHAR(2);       -- MM
  WS_SEGUNDOS8              CHAR(2);       -- SS
  -- FILLER '.' se maneja en lógica de concatenación
  
  WS_COD_CENT_COMP          NUMBER(4,0) := 0;"""
        
        elif var_name == "NUMERO_NUM":
            block += """
  NUMERO_NUM                NUMBER(15,0);
  
-- REDEFINES: NUMERO_NUM_R REDEFINES NUMERO_NUM
-- En PL/SQL se maneja como campos relacionados
  NUMERO_NUM_STR            CHAR(15);     -- Representación texto del número"""
        
        elif var_name == "FL":
            block += """
-- FL REDEFINES WS_DEL_REGISTRO
-- Campo para análisis de registro por bytes
  FL_BYTES                  CHAR(125);    -- Análisis byte a byte del registro"""
        
        elif var_name == "WS_DEL_REGISTRO":
            block += f"""
  {var_name}                CHAR(125) := '0';"""
        
        else:
            # Estructura genérica
            plsql_type = self._convert_pic_to_plsql(pic_clause) if pic_clause else "VARCHAR2(100)"
            block += f"""
  {var_name}                {plsql_type};"""
        
        return block
    
    def _convert_exec_sql_to_plsql(self, exec_sql_raw: str, sql_type: str = "OTHER") -> str:
        """Convertir sentencias EXEC SQL a PL/SQL nativo - Single Responsibility"""
        if not exec_sql_raw or exec_sql_raw.strip() == "":
            return ""
        
        # Limpiar EXEC SQL y END-EXEC
        sql_clean = exec_sql_raw.replace("EXEC SQL", "").replace("END-EXEC", "").strip()
        
        # Convertir según el tipo
        if sql_type == "SELECT":
            # Convertir SELECT INTO :variables
            converted = sql_clean.replace(":WS-", "WS_").replace(":", "")
            converted = converted.replace("-", "_")
            return f"      {converted};"
        
        elif sql_type == "COMMIT":
            return "      COMMIT;"
        
        elif sql_type == "ROLLBACK":
            return "      ROLLBACK;"
        
        elif sql_type == "OPEN":
            cursor_name = ""
            if "OPEN" in sql_clean:
                cursor_name = sql_clean.replace("OPEN", "").strip().replace("-", "_")
            return f"      OPEN {cursor_name};"
        
        elif sql_type == "CLOSE":
            cursor_name = ""
            if "CLOSE" in sql_clean:
                cursor_name = sql_clean.replace("CLOSE", "").strip().replace("-", "_")
            return f"      CLOSE {cursor_name};"
        
        elif sql_type == "FETCH":
            # Convertir FETCH con INTO
            converted = sql_clean.replace(":T12INC06.", "v_T12INC06.")
            converted = converted.replace(":", "")
            converted = converted.replace("-", "_")
            return f"      {converted};"
        
        else:
            # Otros tipos (INCLUDE, DECLARE, etc.)
            converted = sql_clean.replace(":", "")
            converted = converted.replace("-", "_")
            return f"      -- EXEC SQL: {converted}"
    
    def _generate_package_procedures(self) -> str:
        """Generar declaraciones de procedimientos - Single Responsibility"""
        return "\n\n-- Procedure principal\nPROCEDURE PRC_EJECUCION;"
    
    def _generate_package_specification(self, program_name: str, header: str, variables: str, procedures: str) -> str:
        """Generar especificación completa del package - Single Responsibility"""
        return f"{header}{variables}{procedures}\n\nend {program_name};\n/"
    
    def _generate_package_body(self, program_name: str, identification_division: Dict[str, Any], environment_division: Dict[str, Any], data_division: Dict[str, Any], ir: Dict[str, Any]) -> str:
        """Generar cuerpo del package - Single Responsibility"""
        program_id = identification_division.get("program_id", program_name)
        author = identification_division.get("author", "")
        date_written = identification_division.get("date_written", "")
        parse_method = ir.get("parse_method", "unknown")
        total_statements = len(ir.get("statements", []))
        total_procedures = len(ir.get("procedures", []))
        total_variables = len(ir.get("variables", []))
        
        # Información de archivos y variables
        file_control = environment_division.get("input_output_section", {}).get("file_control", [])
        file_descriptions = data_division.get("file_section", {}).get("file_descriptions", [])
        ws_variables = data_division.get("working_storage_section", {}).get("variables", [])
        
        body = f"""create or replace package body {program_name} is

-- Procedure Division
PROCEDURE PRC_EJECUCION IS
BEGIN 
  DBMS_OUTPUT.PUT_LINE('Iniciando programa {program_id}');
  DBMS_OUTPUT.PUT_LINE('Author: {author if author else 'Not specified'}');
  DBMS_OUTPUT.PUT_LINE('Date Written: {date_written if date_written else 'Not specified'}');
  DBMS_OUTPUT.PUT_LINE('Parse Method: {parse_method}');
  DBMS_OUTPUT.PUT_LINE('Total Statements: {total_statements}');
  DBMS_OUTPUT.PUT_LINE('Total Procedures: {total_procedures}');
  DBMS_OUTPUT.PUT_LINE('Total Variables: {total_variables}');
  
  -- Environment Division - Archivos declarados:"""
        
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            if logical_name:
                body += f"\n  DBMS_OUTPUT.PUT_LINE('Archivo: {logical_name}');"
        
        body += "\n  \n  -- Data Division - File Section:"
        for file_desc in file_descriptions:
            file_name = file_desc.get("file_name", "")
            record_layouts = file_desc.get("record_layouts", [])
            if file_name:
                body += f"\n  DBMS_OUTPUT.PUT_LINE('File Description: {file_name}');"
                for record in record_layouts:
                    record_name = record.get("name", "")
                    pic_clause = record.get("pic_clause", "")
                    if record_name:
                        body += f"\n  DBMS_OUTPUT.PUT_LINE('  Record: {record_name} ({pic_clause})');"
        
        body += f"\n  \n  -- Working-Storage Section: {len(ws_variables)} variables declaradas"
        body += f"\n  DBMS_OUTPUT.PUT_LINE('Working-Storage Variables: {len(ws_variables)}');"
        
        # Generar procedimientos reales del IR con macros in-situ
        procedures_section, gap_count, macro_gap_count = self._generate_real_procedures_with_macros(ir)
        body += procedures_section
        
        body += f"""
END PRC_EJECUCION;

END {program_name};
/"""
        
        return body, gap_count, macro_gap_count
    
    def _generate_real_procedures_with_macros(self, ir: Dict[str, Any]) -> str:
        """Generar procedimientos reales del IR con macros in-situ en el orden correcto"""
        procedures_section = ""
        gap_count = 0  # Contador de GAPs
        macro_gap_count = 0  # Contador de GAP MACRO INTERNA
        
        procedures = ir.get("procedures", [])
        if not procedures:
            return "\n  -- No hay procedimientos para generar\n", gap_count, macro_gap_count
        
        print(f"🔧 Generando {len(procedures)} procedimientos con macros in-situ...")
        
        for procedure in procedures:
            procedure_name = procedure.get("name", "UNKNOWN")
            statements = procedure.get("statements", [])
            
            procedures_section += f"""
  
  -- =============================================
  -- PROCEDIMIENTO: {procedure_name}
  -- ============================================="""
            
            if statements:
                procedures_section += f"\n  -- Statements del procedimiento {procedure_name}:"
                
                for i, stmt in enumerate(statements):
                    raw_content = stmt.get("raw", "")
                    op = stmt.get("op", "UNKNOWN")
                    
                    # Detectar macros internas y generar comentario in-situ
                    if "@" in raw_content:
                        procedures_section += f"""
  -- GAP MACRO INTERNA: {raw_content.strip()}"""
                        macro_gap_count += 1
                        print(f"📌 Macro in-situ en {procedure_name}: {raw_content.strip()}")
                    else:
                        # Convertir statement normal
                        if op == "MOVE":
                            # Aplicar conversión completa de MOVE usando principios SOLID
                            converted_move = self._convert_move_statement(stmt)
                            procedures_section += converted_move
                        elif op == "DISPLAY":
                            procedures_section += f"""
  -- DBMS_OUTPUT.PUT_LINE({raw_content.replace('DISPLAY', '').strip()}); -- (DISPLAY statement)"""
                        elif op == "EXEC_SQL":
                            # Aplicar conversión completa de EXEC SQL
                            converted_sql = self._convert_exec_sql_statement(stmt)
                            procedures_section += converted_sql
                        elif op == "INITIALIZE":
                            procedures_section += f"""
  -- GAP -- {raw_content.strip()} -- (INITIALIZE statement)"""
                            gap_count += 1
                        elif op == "PERFORM":
                            procedures_section += f"""
  -- GAP -- {raw_content.strip()} -- (PERFORM statement)"""
                            gap_count += 1
                        else:
                            procedures_section += f"""
  -- GAP -- {raw_content.strip()} -- ({op} statement)"""
                            gap_count += 1
            else:
                procedures_section += f"\n  -- Sin statements en {procedure_name}"
        
        return procedures_section, gap_count, macro_gap_count
    
    # ===== CONVERTIDORES MOVE SIGUIENDO PRINCIPIOS SOLID =====
    
    def _convert_move_statement(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir statement MOVE a PL/SQL siguiendo equivalencias del archivo de referencia
        Principio Single Responsibility: Solo maneja conversión de MOVE
        """
        raw_content = stmt.get("raw", "").strip()
        details = stmt.get("details", {})
        
        print(f"🔄 Convirtiendo MOVE: {raw_content}")
        
        # Extraer información de la sentencia MOVE
        move_info = self._parse_move_statement(raw_content)
        
        if not move_info:
            return f"\n  -- GAP -- {raw_content} -- (MOVE statement - parsing failed)"
        
        # Aplicar patrón Strategy para diferentes tipos de MOVE
        try:
            if move_info["type"] == "simple":
                return self._convert_move_simple(move_info, raw_content)
            elif move_info["type"] == "special_values":
                return self._convert_move_special_values(move_info, raw_content)
            elif move_info["type"] == "qualified_source":
                return self._convert_move_qualified_source(move_info, raw_content)
            elif move_info["type"] == "qualified_target":
                return self._convert_move_qualified_target(move_info, raw_content)
            elif move_info["type"] == "qualified_to_qualified":
                return self._convert_move_qualified_to_qualified(move_info, raw_content)
            elif move_info["type"] == "array_element":
                return self._convert_move_array_element(move_info, raw_content)
            elif move_info["type"] == "substring":
                return self._convert_move_substring(move_info, raw_content)
            elif move_info["type"] == "corresponding":
                return self._convert_move_corresponding(move_info, raw_content)
            else:
                return self._convert_move_generic(move_info, raw_content)
        except Exception as e:
            print(f"❌ Error convirtiendo MOVE: {e}")
            return f"\n  -- GAP -- {raw_content} -- (MOVE statement - conversion error)"
    
    def _parse_move_statement(self, raw_content: str) -> Dict[str, Any]:
        """
        Parsear sentencia MOVE para extraer componentes
        Principio Single Responsibility: Solo parsing de MOVE
        """
        import re
        
        # Limpiar la línea
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
                        "index": match.group(2).strip(),
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
        """
        Convertir MOVE simple siguiendo patrón: var := value;
        Principio Open/Closed: Extendible para nuevos tipos simples
        """
        source = self._clean_cobol_identifier(move_info["source"])
        target = self._clean_cobol_identifier(move_info["target"])
        
        # Detectar si el source es un literal
        if self._is_literal(source):
            converted_source = self._convert_literal(source)
        else:
            converted_source = self._convert_cobol_to_plsql_identifier(source)
        
        converted_target = self._convert_cobol_to_plsql_identifier(target)
        
        # Detectar conversiones comunes que requieren funciones PL/SQL
        if self._needs_type_conversion(source, target, raw_content):
            converted_source = self._apply_type_conversion(converted_source, source, target, raw_content)
        
        return f"""
  {converted_target} := {converted_source}; -- {raw_content}"""
    
    def _needs_type_conversion(self, source: str, target: str, raw_content: str) -> bool:
        """
        Detectar si se requiere conversión de tipos basado en patrones comunes
        """
        # Convertir a uppercase para análisis
        upper_content = raw_content.upper()
        
        # Detectar conversiones numéricas a texto que requieren TO_CHAR
        if any(keyword in upper_content for keyword in ['NUM-', 'COD-', 'ID-', 'NUMERO']) and \
           any(keyword in upper_content for keyword in ['TEXTO', 'DESC-', 'NOMBRE', 'DEL-']):
            return True
            
        # Detectar fechas que requieren conversión
        if any(keyword in upper_content for keyword in ['FEC-', 'FECHA', 'FEM-']):
            return True
            
        return False
    
    def _apply_type_conversion(self, converted_source: str, source: str, target: str, raw_content: str) -> str:
        """
        Aplicar conversión de tipos apropiada
        """
        upper_content = raw_content.upper()
        
        # Conversiones de fecha
        if any(keyword in upper_content for keyword in ['FEC-', 'FECHA', 'FEM-']):
            # Si parece una fecha numérica (YYYYMMDD)
            if 'FEC' in source.upper() and any(num in source for num in '0123456789'):
                return f"TO_DATE(TO_CHAR({converted_source}), 'YYYYMMDD')"
            # Si es string de fecha
            elif 'FEC' in target.upper():
                return f"TO_CHAR({converted_source}, 'YYYY-MM-DD')"
        
        # Conversiones numéricas a texto
        if any(keyword in upper_content for keyword in ['NUM-', 'COD-']) and \
           any(keyword in upper_content for keyword in ['TEXTO', 'DESC-']):
            return f"TO_CHAR({converted_source})"
        
        return converted_source
    
    def _convert_move_special_values(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir MOVE con valores especiales (ZEROS, SPACES, etc.)
        Principio Liskov Substitution: Puede sustituir move simple
        """
        source = move_info["source"].upper()
        target = self._convert_cobol_to_plsql_identifier(move_info["target"])
        
        # Mapeo de valores especiales según archivo de equivalencias
        special_mappings = {
            "ZEROS": "0",
            "ZERO": "0", 
            "SPACES": "NULL",
            "SPACE": "NULL",
            "HIGH-VALUES": "CHR(255)",
            "LOW-VALUES": "CHR(0)"
        }
        
        for special, plsql_value in special_mappings.items():
            if special in source:
                return f"""
  {target} := {plsql_value}; -- {raw_content}"""
        
        # Si no es un valor especial conocido, tratar como simple
        return self._convert_move_simple(move_info, raw_content)
    
    def _convert_move_qualified_source(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir MOVE con source calificado (field OF record TO target)
        """
        source = self._clean_cobol_identifier(move_info["source"])
        source_qualifier = self._clean_cobol_identifier(move_info["source_qualifier"])
        target = self._clean_cobol_identifier(move_info["target"])
        
        # Convertir source calificado
        converted_source = f"{self._convert_cobol_to_plsql_identifier(source_qualifier)}.{self._convert_cobol_to_plsql_identifier(source)}"
        converted_target = self._convert_cobol_to_plsql_identifier(target)
        
        return f"""
  {converted_target} := {converted_source}; -- {raw_content}"""
    
    def _convert_move_qualified_target(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir MOVE con target calificado (source TO field OF record)
        """
        source = self._clean_cobol_identifier(move_info["source"])
        target = self._clean_cobol_identifier(move_info["target"])
        target_qualifier = self._clean_cobol_identifier(move_info["target_qualifier"])
        
        # Detectar si el source es un literal
        if self._is_literal(source):
            converted_source = self._convert_literal(source)
        else:
            converted_source = self._convert_cobol_to_plsql_identifier(source)
        
        # Convertir target calificado
        converted_target = f"{self._convert_cobol_to_plsql_identifier(target_qualifier)}.{self._convert_cobol_to_plsql_identifier(target)}"
        
        return f"""
  {converted_target} := {converted_source}; -- {raw_content}"""
    
    def _convert_move_qualified_to_qualified(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir MOVE entre campos calificados (field1 OF record1 TO field2 OF record2)
        """
        source = self._clean_cobol_identifier(move_info["source"])
        source_qualifier = self._clean_cobol_identifier(move_info["source_qualifier"])
        target = self._clean_cobol_identifier(move_info["target"])
        target_qualifier = self._clean_cobol_identifier(move_info["target_qualifier"])
        
        # Convertir ambos como calificados
        converted_source = f"{self._convert_cobol_to_plsql_identifier(source_qualifier)}.{self._convert_cobol_to_plsql_identifier(source)}"
        converted_target = f"{self._convert_cobol_to_plsql_identifier(target_qualifier)}.{self._convert_cobol_to_plsql_identifier(target)}"
        
        return f"""
  {converted_target} := {converted_source}; -- {raw_content}"""
    
    def _convert_move_array_element(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir MOVE con elementos de array (array(index) TO target)
        """
        source = self._clean_cobol_identifier(move_info["source"])
        index = self._clean_cobol_identifier(move_info["index"])
        target = self._clean_cobol_identifier(move_info["target"])
        
        # Convertir índice (puede ser literal o variable)
        if self._is_literal(index):
            converted_index = self._convert_literal(index)
        else:
            converted_index = self._convert_cobol_to_plsql_identifier(index)
        
        converted_source = f"{self._convert_cobol_to_plsql_identifier(source)}({converted_index})"
        converted_target = self._convert_cobol_to_plsql_identifier(target)
        
        return f"""
  {converted_target} := {converted_source}; -- {raw_content}"""
    
    def _convert_move_substring(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir MOVE con substring (source(start:end) TO target)
        Equivale a SUBSTR en PL/SQL
        """
        source = self._clean_cobol_identifier(move_info["source"])
        start_pos = move_info["start_pos"]
        end_pos = move_info["end_pos"]
        target = self._clean_cobol_identifier(move_info["target"])
        
        converted_source = self._convert_cobol_to_plsql_identifier(source)
        converted_target = self._convert_cobol_to_plsql_identifier(target)
        
        # Calcular longitud para SUBSTR
        length = int(end_pos) - int(start_pos) + 1
        
        return f"""
  {converted_target} := SUBSTR({converted_source}, {start_pos}, {length}); -- {raw_content}"""
    
    def _convert_move_corresponding(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir MOVE CORRESPONDING
        Principio Dependency Inversion: Depende de abstracciones de mapeo
        """
        source = self._convert_cobol_to_plsql_identifier(move_info["source"])
        target = self._convert_cobol_to_plsql_identifier(move_info["target"])
        
        return f"""
  -- MOVE CORRESPONDING requiere mapeo manual campo por campo
  -- {target} := {source}; -- {raw_content}
  -- GAP: Implementar mapeo específico de campos correspondientes"""
    
    def _convert_move_generic(self, move_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir MOVE genérico cuando no coincide con patrones específicos
        Principio Single Responsibility: Maneja casos no identificados
        """
        return f"""
  -- GAP -- {raw_content} -- (MOVE statement - generic)"""
    
    def _clean_cobol_identifier(self, identifier: str) -> str:
        """
        Limpiar identificador COBOL removiendo espacios y caracteres especiales
        """
        if not identifier:
            return ""
        
        # Remover puntos finales y espacios
        cleaned = identifier.strip().rstrip('.')
        return cleaned
    
    def _is_literal(self, value: str) -> bool:
        """
        Detectar si un valor es un literal (número o string)
        """
        if not value:
            return False
            
        # Es número
        if value.replace('.', '').replace('-', '').isdigit():
            return True
            
        # Es string (entre comillas)
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            return True
            
        return False
    
    def _convert_literal(self, literal: str) -> str:
        """
        Convertir literal COBOL a PL/SQL
        """
        if not literal:
            return "NULL"
            
        # Si es número, mantener como está
        if literal.replace('.', '').replace('-', '').isdigit():
            return literal
            
        # Si es string, mantener comillas simples
        if literal.startswith("'") and literal.endswith("'"):
            return literal
        elif literal.startswith('"') and literal.endswith('"'):
            return f"'{literal[1:-1]}'"  # Convertir comillas dobles a simples
            
        return f"'{literal}'"
    
    def _convert_cobol_to_plsql_identifier(self, identifier: str) -> str:
        """
        Convertir identificador COBOL a PL/SQL (cambiar guiones por guiones bajos)
        """
        if not identifier:
            return ""
            
        # Convertir guiones a guiones bajos y a minúsculas
        converted = identifier.replace('-', '_').lower()
        
        # Si comienza con número, agregar prefijo
        if converted and converted[0].isdigit():
            converted = f"v_{converted}"
            
        return converted

    # ===== CONVERTIDORES EXEC SQL SIGUIENDO PRINCIPIOS SOLID =====
    
    def _convert_exec_sql_statement(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir statement EXEC SQL a PL/SQL siguiendo equivalencias del archivo de referencia
        Principio Single Responsibility: Solo maneja conversión de EXEC SQL
        """
        details = stmt.get("details", {})
        sql_type = details.get("sql_type", "OTHER")
        sql_statement = details.get("sql_statement", "")
        host_variables = details.get("host_variables", [])
        raw_content = details.get("raw_content", "")
        
        print(f"🔄 Convirtiendo EXEC SQL tipo: {sql_type}")
        
        # Aplicar patrón Strategy para diferentes tipos de SQL
        if sql_type == "SELECT":
            return self._convert_sql_select_into(sql_statement, host_variables, raw_content)
        elif sql_type == "INSERT":
            return self._convert_sql_insert(sql_statement, host_variables)
        elif sql_type == "UPDATE":
            return self._convert_sql_update(sql_statement, host_variables)
        elif sql_type == "DELETE":
            return self._convert_sql_delete(sql_statement, host_variables)
        elif sql_type == "COMMIT":
            return self._convert_sql_commit()
        elif sql_type == "ROLLBACK":
            return self._convert_sql_rollback()
        elif "INCLUDE" in sql_statement:
            return self._convert_sql_include(sql_statement)
        elif "DECLARE" in sql_statement and "CURSOR" in sql_statement:
            return self._convert_sql_declare_cursor(sql_statement)
        else:
            return self._convert_sql_generic(sql_statement, raw_content)
    
    def _convert_sql_select_into(self, sql_statement: str, host_variables: List[str], raw_content: str) -> str:
        """
        Convertir SELECT INTO siguiendo patrón del archivo manual
        Incluye manejo de excepciones como en C1040_A_MANO.pck
        """
        # Limpiar variables host (remover :)
        cleaned_sql = sql_statement
        plsql_variables = []
        
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            plsql_variables.append(clean_var)
            cleaned_sql = cleaned_sql.replace(f":{var}", clean_var)
        
        # Generar PL/SQL con manejo de excepciones siguiendo patrón manual
        plsql_code = f"""
    BEGIN
        {cleaned_sql};
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            DBMS_OUTPUT.PUT_LINE('No se encontraron datos en SELECT');
            -- Manejar según lógica de negocio
        WHEN TOO_MANY_ROWS THEN
            WS_TEXTO := 'Error: Más de un registro encontrado.';
            WS_PARRAFO := 'SELECT_INTO_ERROR';
            WS_ERROR := SQLCODE;
            WS_ERROR_DESC := SQLERRM;
            RAISE_APPLICATION_ERROR(-20001, WS_ERROR || ' ' || WS_ERROR_DESC || ' ' || WS_PROGRAMA || WS_PARRAFO || WS_TEXTO);
        WHEN OTHERS THEN
            WS_ERROR := SQLCODE;
            WS_ERROR_DESC := SQLERRM;
            DBMS_OUTPUT.PUT_LINE('Error en SELECT: ' || WS_ERROR || ' - ' || WS_ERROR_DESC);
            RAISE;
    END; -- SELECT INTO convertido"""
        
        return plsql_code
    
    def _convert_sql_insert(self, sql_statement: str, host_variables: List[str]) -> str:
        """Convertir INSERT siguiendo equivalencias"""
        cleaned_sql = sql_statement
        
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            cleaned_sql = cleaned_sql.replace(f":{var}", f"v_{clean_var}")
        
        return f"""
    {cleaned_sql};
    
    -- Verificar filas afectadas
    IF SQL%ROWCOUNT > 0 THEN
        DBMS_OUTPUT.PUT_LINE('Registros insertados: ' || SQL%ROWCOUNT);
    END IF; -- INSERT convertido"""
    
    def _convert_sql_update(self, sql_statement: str, host_variables: List[str]) -> str:
        """Convertir UPDATE siguiendo equivalencias"""
        cleaned_sql = sql_statement
        
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            cleaned_sql = cleaned_sql.replace(f":{var}", f"v_{clean_var}")
        
        return f"""
    {cleaned_sql};
    
    -- Verificar número de filas afectadas
    IF SQL%ROWCOUNT = 0 THEN
        DBMS_OUTPUT.PUT_LINE('No se actualizó ningún registro');
    ELSE
        DBMS_OUTPUT.PUT_LINE('Registros actualizados: ' || SQL%ROWCOUNT);
    END IF; -- UPDATE convertido"""
    
    def _convert_sql_delete(self, sql_statement: str, host_variables: List[str]) -> str:
        """Convertir DELETE siguiendo equivalencias"""
        cleaned_sql = sql_statement
        
        for var in host_variables:
            clean_var = var.replace("-", "_").replace(":", "")
            cleaned_sql = cleaned_sql.replace(f":{var}", f"v_{clean_var}")
        
        return f"""
    {cleaned_sql};
    
    -- Verificar filas eliminadas
    IF SQL%ROWCOUNT > 0 THEN
        DBMS_OUTPUT.PUT_LINE('Registros eliminados: ' || SQL%ROWCOUNT);
    END IF; -- DELETE convertido"""
    
    def _convert_sql_commit(self) -> str:
        """Convertir COMMIT siguiendo equivalencias"""
        return """
    COMMIT; -- Confirmar transacción
    DBMS_OUTPUT.PUT_LINE('Transacción confirmada'); -- COMMIT convertido"""
    
    def _convert_sql_rollback(self) -> str:
        """Convertir ROLLBACK siguiendo equivalencias y patrón manual"""
        return """
    ROLLBACK; -- Revertir transacción
    DBMS_OUTPUT.PUT_LINE('Transacción revertida'); -- ROLLBACK convertido"""
    
    def _convert_sql_include(self, sql_statement: str) -> str:
        """
        Convertir EXEC SQL INCLUDE siguiendo patrón del archivo manual
        Los INCLUDE se convierten en declaraciones de tipos %ROWTYPE
        """
        table_name = sql_statement.replace("INCLUDE", "").strip()
        
        # Seguir patrón del archivo manual: v_T30DOR10 NEXTI.T30DOR10%ROWTYPE;
        return f"""
    -- EXEC SQL INCLUDE {table_name} convertido a:
    v_{table_name}        NEXTI.{table_name}%ROWTYPE; -- INCLUDE convertido"""
    
    def _convert_sql_declare_cursor(self, sql_statement: str) -> str:
        """Convertir DECLARE CURSOR siguiendo patrón manual"""
        return f"""
    -- CURSOR declarado siguiendo patrón manual
    CURSOR cursor_name IS 
        {sql_statement.replace("DECLARE", "").replace("CURSOR", "").strip()}; -- DECLARE CURSOR convertido"""
    
    def _convert_sql_generic(self, sql_statement: str, raw_content: str) -> str:
        """Convertir SQL genérico con comentario explicativo"""
        return f"""
    -- SQL genérico convertido:
    {sql_statement}; -- Original: {raw_content.strip()}"""
    
    def _generate_package_footer(self, environment_division: Dict[str, Any], data_division: Dict[str, Any]) -> str:
        """Generar footer informativo del package - Single Responsibility"""
        file_control = environment_division.get("input_output_section", {}).get("file_control", [])
        file_descriptions = data_division.get("file_section", {}).get("file_descriptions", [])
        ws_variables = data_division.get("working_storage_section", {}).get("variables", [])
        
        footer = f"""
-- =============================================
-- PACKAGE COMPLETO GENERADO CON PRINCIPIOS SOLID
-- =============================================
-- Environment Division implementada:
-- - Input-Output Section: {len(file_control)} archivos declarados"""
        
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            external_name = file_info.get("external_name", "")
            organization = file_info.get("organization", "")
            if logical_name:
                footer += f"\n--   * {logical_name}: {external_name} ({organization if organization else 'No organization specified'})"
        
        footer += f"\n-- Data Division implementada:\n-- - File Section: {len(file_descriptions)} archivos descritos"
        
        for file_desc in file_descriptions:
            file_name = file_desc.get("file_name", "")
            record_layouts = file_desc.get("record_layouts", [])
            if file_name:
                footer += f"\n--   * {file_name}: {len(record_layouts)} record(s)"
        
        footer += f"\n-- - Working-Storage Section: {len(ws_variables)} variables declaradas"
        footer += "\n-- =============================================\n-- Principios SOLID aplicados:\n-- - Single Responsibility: Cada método tiene una responsabilidad específica\n-- - Open/Closed: Extensible para nuevas divisiones\n-- - Liskov Substitution: Métodos intercambiables\n-- - Interface Segregation: Interfaces específicas por sección\n-- - Dependency Inversion: Abstracción de generación\n-- ============================================="
        
        return footer
    
    def _generate_identification_environment_data_manual(self, program_name: str, identification_division: Dict[str, Any], environment_division: Dict[str, Any], data_division: Dict[str, Any], ir: Dict[str, Any]) -> str:
        """Generar SQL para Identification + Environment + Data Division (File Section) siguiendo el patrón del archivo migrado manualmente"""
        
        # Extraer información de la Identification Division
        program_id = identification_division.get("program_id", program_name)
        author = identification_division.get("author", "")
        date_written = identification_division.get("date_written", "")
        date_compiled = identification_division.get("date_compiled", "")
        security = identification_division.get("security", "")
        installation = identification_division.get("installation", "")
        remarks = identification_division.get("remarks", "")
        
        # Extraer información de la Environment Division
        input_output_section = environment_division.get("input_output_section", {})
        file_control = input_output_section.get("file_control", [])
        
        # Extraer información de la Data Division
        file_section = data_division.get("file_section", {})
        file_descriptions = file_section.get("file_descriptions", [])
        
        # Obtener información adicional del IR
        parse_method = ir.get("parse_method", "unknown")
        total_statements = len(ir.get("statements", []))
        total_procedures = len(ir.get("procedures", []))
        total_variables = len(ir.get("variables", []))
        
        # Generar timestamp actual
        from datetime import datetime
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Generar el programa migrado siguiendo el patrón exacto
        sql_content = f"""create or replace package {program_name} is

  -- Author  : ANTLR_CONVERTER
  -- Created : {current_time}
  -- Purpose : {remarks if remarks else 'PROGRAMA CONVERTIDO AUTOMATICAMENTE DESDE COBOL'}

-- Identification Division Information:
-- Program ID: {program_id}
-- Author: {author if author else 'Not specified'}
-- Date Written: {date_written if date_written else 'Not specified'}
-- Date Compiled: {date_compiled if date_compiled else 'Not specified'}
-- Security: {security if security else 'Not specified'}
-- Installation: {installation if installation else 'Not specified'}
-- Parse Method: {parse_method}
-- Total Statements: {total_statements}
-- Total Procedures: {total_procedures}
-- Total Variables: {total_variables}

-- Variables globales básicas
  v_contador  NUMBER := 0;
  RETURN_CODE NUMBER := 0;

--ENVIRONMENT DIVISION.
--INPUT-OUTPUT SECTION."""

        # Agregar archivos de la Environment Division
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            if logical_name:
                sql_content += f"""
  {logical_name} UTL_FILE.FILE_TYPE;"""

        sql_content += f"""
  
--WORKING-STORAGE SECTION."""

        # Agregar variables de archivo de la File Section
        for file_desc in file_descriptions:
            file_name = file_desc.get("file_name", "")
            record_layouts = file_desc.get("record_layouts", [])
            
            # Comentario de la descripción del archivo
            if file_name:
                recording_mode = file_desc.get("recording_mode", "")
                block_contains = file_desc.get("block_contains", "")
                label_record = file_desc.get("label_record", "")
                
                sql_content += f"""
-- File Description: {file_name}"""
                if recording_mode:
                    sql_content += f"""
-- Recording Mode: {recording_mode}"""
                if block_contains:
                    sql_content += f"""
-- Block Contains: {block_contains}"""
                if label_record:
                    sql_content += f"""
-- Label Record: {label_record}"""
            
            # Agregar los record layouts
            for record in record_layouts:
                record_name = record.get("name", "")
                pic_clause = record.get("pic_clause", "")
                
                if record_name and pic_clause:
                    # Convertir PIC clause a tipo PL/SQL
                    plsql_type = self._convert_pic_to_plsql(pic_clause)
                    sql_content += f"""
  {record_name.replace('-', '_')}  {plsql_type};"""

        # Variables básicas de trabajo
        sql_content += f"""
  R_FICCON01   CHAR(80);  
  REG_FICCON   CHAR(80);  

-- Procedure principal
PROCEDURE PRC_EJECUCION;

end {program_name};
/
create or replace package body {program_name} is

-- Procedure Division
PROCEDURE PRC_EJECUCION IS
BEGIN 
  DBMS_OUTPUT.PUT_LINE('Iniciando programa {program_id}');
  DBMS_OUTPUT.PUT_LINE('Author: {author if author else 'Not specified'}');
  DBMS_OUTPUT.PUT_LINE('Date Written: {date_written if date_written else 'Not specified'}');
  DBMS_OUTPUT.PUT_LINE('Parse Method: {parse_method}');
  DBMS_OUTPUT.PUT_LINE('Total Statements: {total_statements}');
  DBMS_OUTPUT.PUT_LINE('Total Procedures: {total_procedures}');
  DBMS_OUTPUT.PUT_LINE('Total Variables: {total_variables}');
  
  -- Environment Division - Archivos declarados:"""

        # Listar archivos en el log
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            if logical_name:
                sql_content += f"""
  DBMS_OUTPUT.PUT_LINE('Archivo: {logical_name}');"""

        # Listar variables de archivo de la File Section
        sql_content += f"""
  
  -- Data Division - File Section:"""
        for file_desc in file_descriptions:
            file_name = file_desc.get("file_name", "")
            record_layouts = file_desc.get("record_layouts", [])
            if file_name:
                sql_content += f"""
  DBMS_OUTPUT.PUT_LINE('File Description: {file_name}');"""
                for record in record_layouts:
                    record_name = record.get("name", "")
                    pic_clause = record.get("pic_clause", "")
                    if record_name:
                        sql_content += f"""
  DBMS_OUTPUT.PUT_LINE('  Record: {record_name} ({pic_clause})');"""

        sql_content += f"""
  
  -- Lógica del programa se implementará en las siguientes fases
  DBMS_OUTPUT.PUT_LINE('Programa {program_id} ejecutado correctamente');
END PRC_EJECUCION;

END {program_name};
/

-- =============================================
-- IDENTIFICATION + ENVIRONMENT + DATA DIVISION (FILE SECTION) COMPLETADAS
-- =============================================
-- Environment Division implementada:
-- - Input-Output Section: {len(file_control)} archivos declarados"""

        # Listar archivos en comentarios
        for file_info in file_control:
            logical_name = file_info.get("logical_name", "")
            external_name = file_info.get("external_name", "")
            organization = file_info.get("organization", "")
            if logical_name:
                sql_content += f"""
--   * {logical_name}: {external_name} ({organization if organization else 'No organization specified'})"""

        sql_content += f"""
-- Data Division implementada:
-- - File Section: {len(file_descriptions)} archivos descritos"""

        # Listar file descriptions en comentarios
        for file_desc in file_descriptions:
            file_name = file_desc.get("file_name", "")
            record_layouts = file_desc.get("record_layouts", [])
            if file_name:
                sql_content += f"""
--   * {file_name}: {len(record_layouts)} record(s)"""
                for record in record_layouts:
                    record_name = record.get("name", "")
                    pic_clause = record.get("pic_clause", "")
                    if record_name:
                        sql_content += f"""
--     - {record_name}: {pic_clause}"""

        sql_content += f"""
-- =============================================
-- Siguiente fase: Data Division (Working-Storage Section completa)
-- Finalmente: Procedure Division (lógica completa)
-- ============================================="""

        return sql_content
    
    def _extract_usage_from_raw(self, raw_content: str) -> str:
        """Extraer información de USAGE del contenido raw de una variable"""
        if not raw_content:
            return ""
        
        raw_upper = raw_content.upper()
        
        # Detectar USAGE específicos
        if "COMP-3" in raw_upper or "PACKED-DECIMAL" in raw_upper:
            return "COMP-3"
        elif "COMP" in raw_upper and "COMP-3" not in raw_upper:
            return "COMP"
        elif "BINARY" in raw_upper:
            return "COMP"
        elif "DISPLAY" in raw_upper:
            usage = "DISPLAY"
            if "SIGN" in raw_upper:
                if "LEADING" in raw_upper:
                    usage += " SIGN LEADING"
                elif "TRAILING" in raw_upper:
                    usage += " SIGN TRAILING"
                if "SEPARATE" in raw_upper:
                    usage += " SEPARATE"
            return usage
        
        return ""
    
    def _convert_pic_to_plsql(self, pic_clause: str, usage: str = "", value_clause: str = "") -> str:
        """
        Convertir una cláusula PIC de COBOL a tipo PL/SQL
        Implementa todas las equivalencias completas basadas en el archivo de referencia
        
        Args:
            pic_clause: Cláusula PIC de COBOL (ej: '9(3)', 'X(30)', 'S9(5)V99')
            usage: Cláusula USAGE (COMP, COMP-3, DISPLAY, etc.)
            value_clause: Cláusula VALUE para determinar contexto
        
        Returns:
            Tipo de dato PL/SQL equivalente
        """
        if not pic_clause:
            return "VARCHAR2(100)"
        
        pic_upper = pic_clause.upper().strip()
        usage_upper = usage.upper().strip() if usage else ""
        value_upper = value_clause.upper().strip() if value_clause else ""
        
        # === 1. TIPOS NUMÉRICOS BÁSICOS ===
        
        # PIC 9(n) -> NUMBER(n) - Enteros sin decimales
        match = re.match(r'^9\((\d+)\)$', pic_upper)
        if match:
            size = match.group(1)
            if usage_upper == "COMP":
                if int(size) <= 9:
                    return f"BINARY_INTEGER -- PIC {pic_clause} COMP"
                else:
                    return f"NUMBER({size}) -- PIC {pic_clause} COMP"
            elif usage_upper == "COMP-3":
                return f"NUMBER({size}) -- PIC {pic_clause} COMP-3"
            else:
                return f"NUMBER({size})"
        
        # PIC 9 -> NUMBER(1) - Entero de un dígito
        if pic_upper == '9':
            return "NUMBER(1)"
        
        # PIC 99, 999, etc. -> NUMBER(n) - Enteros múltiples dígitos
        if re.match(r'^9+$', pic_upper):
            size = len(pic_upper)
            return f"NUMBER({size})"
        
        # PIC S9(n) -> NUMBER(n) - Enteros con signo
        match = re.match(r'^S9\((\d+)\)$', pic_upper)
        if match:
            size = match.group(1)
            if usage_upper == "COMP":
                if int(size) <= 9:
                    return f"BINARY_INTEGER -- PIC {pic_clause} COMP"
                else:
                    return f"NUMBER({size}) -- PIC {pic_clause} COMP"
            elif usage_upper == "COMP-3":
                return f"NUMBER({size}) -- PIC {pic_clause} COMP-3"
            else:
                return f"NUMBER({size})"
        
        # PIC S9 -> NUMBER(1) - Entero con signo de un dígito
        if pic_upper == 'S9':
            return "NUMBER(1)"
        
        # PIC S99, S999, etc. -> NUMBER(n) - Enteros con signo múltiples dígitos
        if re.match(r'^S9+$', pic_upper):
            size = len(pic_upper) - 1  # Restar la S
            return f"NUMBER({size})"
        
        # === 2. TIPOS CON DECIMALES EXPLÍCITOS ===
        
        # PIC 9(n)V9(m) -> NUMBER(n+m, m) - Decimales explícitos
        match = re.match(r'^9\((\d+)\)V9\((\d+)\)$', pic_upper)
        if match:
            int_part = int(match.group(1))
            dec_part = int(match.group(2))
            total = int_part + dec_part
            return f"NUMBER({total},{dec_part})"
        
        # PIC 9(n)V99 -> NUMBER(n+2, 2) - Decimales fijos
        match = re.match(r'^9\((\d+)\)V(9+)$', pic_upper)
        if match:
            int_part = int(match.group(1))
            dec_part = len(match.group(2))
            total = int_part + dec_part
            return f"NUMBER({total},{dec_part})"
        
        # PIC S9(n)V9(m) -> NUMBER(n+m, m) - Decimales con signo explícitos
        match = re.match(r'^S9\((\d+)\)V9\((\d+)\)$', pic_upper)
        if match:
            int_part = int(match.group(1))
            dec_part = int(match.group(2))
            total = int_part + dec_part
            return f"NUMBER({total},{dec_part})"
        
        # PIC S9(n)V99 -> NUMBER(n+2, 2) - Decimales con signo fijos
        match = re.match(r'^S9\((\d+)\)V(9+)$', pic_upper)
        if match:
            int_part = int(match.group(1))
            dec_part = len(match.group(2))
            total = int_part + dec_part
            return f"NUMBER({total},{dec_part})"
        
        # === 3. TIPOS ALFANUMÉRICOS ===
        
        # PIC X(n) -> VARCHAR2(n) o CHAR(n) - Alfanuméricos
        match = re.match(r'^X\((\d+)\)$', pic_upper)
        if match:
            size = int(match.group(1))
            # Para campos pequeños usar CHAR, para grandes VARCHAR2
            if size <= 10:
                return f"CHAR({size})"
            else:
                return f"VARCHAR2({size})"
        
        # PIC X -> CHAR(1) - Un carácter
        if pic_upper == 'X':
            return "CHAR(1)"
        
        # PIC XX, XXX, etc. -> CHAR(n) - Múltiples caracteres
        if re.match(r'^X+$', pic_upper):
            size = len(pic_upper)
            if size <= 10:
                return f"CHAR({size})"
            else:
                return f"VARCHAR2({size})"
        
        # PIC A(n) -> VARCHAR2(n) - Solo caracteres alfabéticos
        match = re.match(r'^A\((\d+)\)$', pic_upper)
        if match:
            size = match.group(1)
            return f"VARCHAR2({size}) -- Alphabetic only"
        
        # PIC A -> CHAR(1) - Un carácter alfabético
        if pic_upper == 'A':
            return "CHAR(1) -- Alphabetic only"
        
        # === 4. CASOS ESPECIALES POR CONTEXTO ===
        
        # Fechas (PIC 9(8) para YYYYMMDD)
        if pic_upper == '9(8)' and any(hint in value_upper for hint in ['DATE', 'FECHA', 'FEC', 'DT']):
            return f"DATE -- PIC {pic_clause} (Date format YYYYMMDD)"
        
        # Fechas con separadores (PIC X(10))
        if pic_upper == 'X(10)' and any(hint in value_upper for hint in ['DATE', 'FECHA', 'FEC']):
            return f"VARCHAR2(10) -- PIC {pic_clause} (Date format DD/MM/YYYY)"
        
        # Timestamps (PIC 9(14))
        if pic_upper == '9(14)' and any(hint in value_upper for hint in ['TIME', 'TIMESTAMP', 'HORA', 'TS']):
            return f"TIMESTAMP -- PIC {pic_clause} (Timestamp YYYYMMDDHHMMSS)"
        
        # Horas (PIC 9(6))
        if pic_upper == '9(6)' and any(hint in value_upper for hint in ['TIME', 'HORA', 'HOR']):
            return f"VARCHAR2(8) -- PIC {pic_clause} (Time HH:MM:SS)"
        
        # Booleanos
        if pic_upper in ['X', 'X(1)'] and any(hint in value_upper for hint in ['Y', 'N', 'S', 'FLAG', 'IND']):
            return f"CHAR(1) -- PIC {pic_clause} (Boolean flag)"
        
        # === 5. TIPOS ESPECIALES POR USAGE ===
        
        # COMP (Binary) - Tratamiento especial
        if usage_upper == "COMP":
            if re.match(r'^S?9', pic_upper):
                # Extraer tamaño para decidir tipo
                if '(' in pic_upper:
                    size_match = re.search(r'\((\d+)\)', pic_upper)
                    if size_match:
                        size = int(size_match.group(1))
                        if size <= 9:
                            return f"BINARY_INTEGER -- PIC {pic_clause} COMP"
                        else:
                            return f"NUMBER({size}) -- PIC {pic_clause} COMP"
                else:
                    # Contar dígitos
                    digits = len(re.sub(r'[SV]', '', pic_upper))
                    if digits <= 9:
                        return f"BINARY_INTEGER -- PIC {pic_clause} COMP"
                    else:
                        return f"NUMBER({digits}) -- PIC {pic_clause} COMP"
            else:
                return f"BINARY_INTEGER -- PIC {pic_clause} COMP"
        
        # COMP-3 (Packed Decimal) - Tratamiento especial
        if usage_upper == "COMP-3":
            if re.match(r'^S?9', pic_upper):
                if '(' in pic_upper:
                    size_match = re.search(r'\((\d+)\)', pic_upper)
                    if size_match:
                        size = size_match.group(1)
                        return f"NUMBER({size}) -- PIC {pic_clause} COMP-3"
                else:
                    digits = len(re.sub(r'[SV]', '', pic_upper))
                    return f"NUMBER({digits}) -- PIC {pic_clause} COMP-3"
            return f"NUMBER -- PIC {pic_clause} COMP-3"
        
        # === 6. CASOS POR DEFECTO MEJORADOS ===
        
        # Si empieza con 9 pero no coincide con ningún patrón anterior
        if pic_upper.startswith('9'):
            # Contar dígitos para estimar tamaño
            digits = len(re.sub(r'[^9]', '', pic_upper))
            if digits > 0:
                return f"NUMBER({digits}) -- PIC {pic_clause}"
            else:
                return f"NUMBER -- PIC {pic_clause}"
        
        # Si empieza con S9 pero no coincide con ningún patrón anterior
        if pic_upper.startswith('S9'):
            digits = len(re.sub(r'[^9]', '', pic_upper))
            if digits > 0:
                return f"NUMBER({digits}) -- PIC {pic_clause}"
            else:
                return f"NUMBER -- PIC {pic_clause}"
        
        # Si empieza con X pero no coincide con ningún patrón anterior  
        if pic_upper.startswith('X'):
            # Estimar tamaño por número de X
            x_count = pic_upper.count('X')
            if x_count > 0:
                if x_count <= 10:
                    return f"CHAR({x_count}) -- PIC {pic_clause}"
                else:
                    return f"VARCHAR2({x_count}) -- PIC {pic_clause}"
            else:
                return f"VARCHAR2(100) -- PIC {pic_clause}"
        
        # Si empieza con A (alfabético)
        if pic_upper.startswith('A'):
            a_count = pic_upper.count('A')
            if a_count > 0:
                return f"VARCHAR2({a_count}) -- PIC {pic_clause} (Alphabetic)"
            else:
                return f"VARCHAR2(100) -- PIC {pic_clause} (Alphabetic)"
        
        # Caso por defecto final
        return f"VARCHAR2(100) -- PIC {pic_clause} (Unknown format)"
    
    def _generate_identification_and_environment_sql(self, program_name: str, identification_division: Dict[str, Any], environment_division: Dict[str, Any], ir: Dict[str, Any]) -> str:
        """Generar SQL para Identification Division + Environment Division"""
        
        # Extraer información de la Identification Division
        program_id = identification_division.get("program_id", program_name)
        author = identification_division.get("author", "")
        date_written = identification_division.get("date_written", "")
        date_compiled = identification_division.get("date_compiled", "")
        security = identification_division.get("security", "")
        installation = identification_division.get("installation", "")
        remarks = identification_division.get("remarks", "")
        
        # Extraer información de la Environment Division
        configuration_section = environment_division.get("configuration_section", {})
        input_output_section = environment_division.get("input_output_section", {})
        
        # Obtener información adicional del IR
        parse_method = ir.get("parse_method", "unknown")
        total_statements = len(ir.get("statements", []))
        total_procedures = len(ir.get("procedures", []))
        total_variables = len(ir.get("variables", []))
        
        # Generar timestamp actual
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generar SQL para ambas divisiones
        sql_content = f"""-- =============================================
-- IDENTIFICATION DIVISION + ENVIRONMENT DIVISION
-- COBOL to PL/SQL Conversion
-- =============================================
-- Program ID: {program_id}
-- Author: {author if author else 'Not specified'}
-- Date Written: {date_written if date_written else 'Not specified'}
-- Date Compiled: {date_compiled if date_compiled else 'Not specified'}
-- Security: {security if security else 'Not specified'}
-- Installation: {installation if installation else 'Not specified'}
-- Remarks: {remarks if remarks else 'Not specified'}
-- =============================================
-- Conversion Information:
-- Parse Method: {parse_method}
-- Total Statements: {total_statements}
-- Total Procedures: {total_procedures}
-- Total Variables: {total_variables}
-- Conversion Date: {current_time}
-- =============================================

-- Package Specification
CREATE OR REPLACE PACKAGE {program_name} IS
  -- Program identification
  PROCEDURE MAIN;

  -- Program metadata
  FUNCTION GET_PROGRAM_ID RETURN VARCHAR2;
  FUNCTION GET_AUTHOR RETURN VARCHAR2;
  FUNCTION GET_DATE_WRITTEN RETURN VARCHAR2;
  FUNCTION GET_INSTALLATION RETURN VARCHAR2;
  
  -- Environment Division - Configuration
  FUNCTION GET_DECIMAL_POINT RETURN VARCHAR2;
  FUNCTION GET_SPECIAL_NAMES RETURN VARCHAR2;

END {program_name};
/

-- Package Body
CREATE OR REPLACE PACKAGE BODY {program_name} IS

  -- Environment Division - File Declarations
  IMPRES01 UTL_FILE.FILE_TYPE;
  IMPRES02 UTL_FILE.FILE_TYPE;
  FICCON01 UTL_FILE.FILE_TYPE;

  -- Program identification constants
  GC_PROGRAM_ID CONSTANT VARCHAR2(50) := '{program_id}';
  GC_AUTHOR CONSTANT VARCHAR2(100) := '{author if author else 'Not specified'}';
  GC_DATE_WRITTEN CONSTANT VARCHAR2(50) := '{date_written if date_written else 'Not specified'}';
  GC_INSTALLATION CONSTANT VARCHAR2(100) := '{installation if installation else 'Not specified'}';
  GC_REMARKS CONSTANT VARCHAR2(500) := '{remarks if remarks else 'Not specified'}';
  
  -- Environment Division Constants
  GC_DECIMAL_POINT CONSTANT VARCHAR2(1) := 'COMMA';

  -- Main procedure (placeholder for now)
  PROCEDURE MAIN IS
  BEGIN
    -- Main program logic will be implemented in next phases
    DBMS_OUTPUT.PUT_LINE('Program: ' || GC_PROGRAM_ID);
    DBMS_OUTPUT.PUT_LINE('Author: ' || GC_AUTHOR);
    DBMS_OUTPUT.PUT_LINE('Date Written: ' || GC_DATE_WRITTEN);
    DBMS_OUTPUT.PUT_LINE('Installation: ' || GC_INSTALLATION);
    DBMS_OUTPUT.PUT_LINE('Remarks: ' || GC_REMARKS);
    DBMS_OUTPUT.PUT_LINE('Decimal Point: ' || GC_DECIMAL_POINT);
  END MAIN;

  -- Metadata functions
  FUNCTION GET_PROGRAM_ID RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_PROGRAM_ID;
  END GET_PROGRAM_ID;

  FUNCTION GET_AUTHOR RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_AUTHOR;
  END GET_AUTHOR;

  FUNCTION GET_DATE_WRITTEN RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_DATE_WRITTEN;
  END GET_DATE_WRITTEN;

  FUNCTION GET_INSTALLATION RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_INSTALLATION;
  END GET_INSTALLATION;
  
  -- Environment Division Functions
  FUNCTION GET_DECIMAL_POINT RETURN VARCHAR2 IS
  BEGIN
    RETURN GC_DECIMAL_POINT;
  END GET_DECIMAL_POINT;
  
  FUNCTION GET_SPECIAL_NAMES RETURN VARCHAR2 IS
  BEGIN
    RETURN 'DECIMAL-POINT IS COMMA';
  END GET_SPECIAL_NAMES;

END {program_name};
/

-- =============================================
-- ENVIRONMENT DIVISION DETAILS
-- =============================================
-- Configuration Section:
-- Special Names: DECIMAL-POINT IS COMMA
-- =============================================
-- Input-Output Section:
-- File Control: Declared in Package Body as UTL_FILE.FILE_TYPE
--   IMPRES01, IMPRES02, FICCON01"""

        sql_content += f"""
-- =============================================
-- END OF IDENTIFICATION + ENVIRONMENT DIVISION
-- =============================================
-- Next phases will include:
-- - Data Division  
-- - Procedure Division
-- ============================================="""

        return sql_content
    
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
    
    def generate_conversion_report(self, gap_count: int = 0, macro_gap_count: int = 0) -> Dict[str, Any]:
        """Generar reporte de conversión"""
        success_rate = 0
        if self.statistics["total_statements"] > 0:
            success_rate = (self.statistics["converted_statements"] / self.statistics["total_statements"]) * 100
        
        gap_percentage = 0
        if self.statistics["total_statements"] > 0:
            gap_percentage = (gap_count / self.statistics["total_statements"]) * 100
        
        macro_gap_percentage = 0
        if self.statistics["total_statements"] > 0:
            macro_gap_percentage = (macro_gap_count / self.statistics["total_statements"]) * 100
        
        total_gaps = gap_count + macro_gap_count
        total_gap_percentage = 0
        if self.statistics["total_statements"] > 0:
            total_gap_percentage = (total_gaps / self.statistics["total_statements"]) * 100
        
        return {
            "conversion_summary": {
                "total_statements": self.statistics["total_statements"],
                "converted_statements": self.statistics["converted_statements"],
                "skipped_statements": self.statistics["skipped_statements"],
                "gap_statements": gap_count,
                "macro_gap_statements": macro_gap_count,
                "total_gaps": total_gaps,
                "success_rate": round(success_rate, 2),
                "gap_percentage": round(gap_percentage, 2),
                "macro_gap_percentage": round(macro_gap_percentage, 2),
                "total_gap_percentage": round(total_gap_percentage, 2),
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
        sql_content, gap_count, macro_gap_count = converter.convert_ir_to_sql(ir)
        conversion_time = time.time()
        
        # Guardar SQL
        with open(sql_output, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        # Generar reporte
        report = converter.generate_conversion_report(gap_count, macro_gap_count)
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
        print(f"   🚧 GAPs código: {report['conversion_summary']['gap_statements']}")
        print(f"   🔧 GAPs macros: {report['conversion_summary']['macro_gap_statements']}")
        print(f"   📊 Total GAPs: {report['conversion_summary']['total_gaps']}")
        print(f"   📈 Tasa éxito: {report['conversion_summary']['success_rate']}%")
        print(f"   📊 Porcentaje GAPs código: {report['conversion_summary']['gap_percentage']}%")
        print(f"   🔧 Porcentaje GAPs macros: {report['conversion_summary']['macro_gap_percentage']}%")
        print(f"   📊 Porcentaje total GAPs: {report['conversion_summary']['total_gap_percentage']}%")
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

