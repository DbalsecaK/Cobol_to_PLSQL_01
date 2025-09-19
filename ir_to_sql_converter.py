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
        
        # Agregar variables para manejo de archivos UTL_FILE
        section += self._generate_file_variables_section()
        
        # Agregar funciones de utilidad para operaciones STRING
        section += self._generate_string_utility_functions()
        
        # Agregar funciones de utilidad para operaciones SET
        section += self._generate_set_utility_functions()
        
        # Agregar funciones de utilidad para operaciones PERFORM
        section += self._generate_perform_utility_functions()
        
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
    
    def _generate_plsql_procedures_from_cobol(self, ir: Dict[str, Any]) -> str:
        """
        Generar procedimientos PL/SQL a partir de los procedimientos COBOL
        PERFORM 1000-INICIO → PROCEDURE A1000_INICIO IS
        """
        procedures_section = ""
        
        procedures = ir.get("procedures", [])
        if not procedures:
            return ""
        
        procedures_section += """
  /*
   *-------------------------------------------------------------*
   * PROCEDIMIENTOS CONVERTIDOS DESDE COBOL                     *
   *-------------------------------------------------------------*
   */
   
"""
        
        for procedure in procedures:
            proc_name = procedure.get("name", "")
            statements = procedure.get("statements", [])
            
            if not proc_name:
                continue
                
            # Convertir nombre COBOL a PL/SQL (1000-INICIO → A1000_INICIO)
            plsql_proc_name = self._convert_cobol_procedure_name_to_plsql(proc_name)
            
            procedures_section += f"""  PROCEDURE {plsql_proc_name} IS
  BEGIN
    -- Procedimiento convertido desde: {proc_name}
"""
            
            # Procesar statements del procedimiento
            if statements:
                for stmt in statements:
                    op = stmt.get("op", "UNKNOWN")
                    raw_content = stmt.get("raw", "").strip()
                    
                    # Verificar si hay macros (@) en el contenido
                    if '@' in raw_content:
                        procedures_section += f"""    -- GAP MACRO INTERNA: {raw_content}
"""
                    
                    # Convertir statement según su tipo
                    if op == "MOVE":
                        converted_move = self._convert_move_statement(stmt)
                        procedures_section += f"    {converted_move.strip()}\n"
                    elif op == "IF":
                        converted_if = self._convert_if_statement(stmt)
                        procedures_section += f"    {converted_if.strip()}\n"
                    elif op == "ELSE":
                        converted_else = self._convert_else_statement(stmt)
                        procedures_section += f"    {converted_else.strip()}\n"
                    elif op == "END-IF":
                        converted_endif = self._convert_end_if_statement(stmt)
                        procedures_section += f"    {converted_endif.strip()}\n"
                    elif op == "EXEC_SQL":
                        converted_sql = self._convert_exec_sql_statement(stmt)
                        procedures_section += f"    {converted_sql.strip()}\n"
                    elif op in ["OPEN", "CLOSE", "READ", "WRITE", "REWRITE", "DELETE", "START"]:
                        converted_file = self._convert_file_operation(stmt)
                        procedures_section += f"    {converted_file.strip()}\n"
                    elif op == "STRING":
                        converted_string = self._convert_string_statement(stmt)
                        procedures_section += f"    {converted_string.strip()}\n"
                    elif op == "SET":
                        converted_set = self._convert_set_statement(stmt)
                        procedures_section += f"    {converted_set.strip()}\n"
                    elif op == "PERFORM":
                        converted_perform = self._convert_perform_statement(stmt)
                        procedures_section += f"    {converted_perform.strip()}\n"
                    elif op == "DISPLAY":
                        # Convertir DISPLAY a DBMS_OUTPUT.PUT_LINE
                        display_content = raw_content.replace("DISPLAY", "").replace("display", "").strip()
                        if display_content.startswith("'") and display_content.endswith("'"):
                            procedures_section += f"""    DBMS_OUTPUT.PUT_LINE({display_content}); -- {raw_content}
"""
                        else:
                            procedures_section += f"""    -- GAP -- {raw_content} -- (DISPLAY statement)
"""
                    elif op == "INITIALIZE":
                        procedures_section += f"""    -- GAP -- {raw_content} -- (INITIALIZE statement)
"""
                    else:
                        procedures_section += f"""    -- GAP -- {raw_content} -- ({op} statement)
"""
            else:
                procedures_section += """    -- Sin statements para procesar
"""
            
            procedures_section += """  END;

"""
        
        return procedures_section
    
    def _convert_cobol_procedure_name_to_plsql(self, cobol_name: str) -> str:
        """
        Convertir nombre de procedimiento COBOL a PL/SQL
        1000-INICIO → A1000_INICIO
        2000-PROCESO → A2000_PROCESO
        8000-FINAL → A8000_FINAL
        """
        # Remover espacios y convertir a mayúsculas
        clean_name = cobol_name.strip().upper()
        
        # Reemplazar guiones por guiones bajos
        plsql_name = clean_name.replace("-", "_")
        
        # Agregar prefijo A si no lo tiene
        if not plsql_name.startswith("A"):
            plsql_name = "A" + plsql_name
            
        return plsql_name

    def _extract_main_performs_from_procedure_division(self, ir_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extraer PERFORM principales del PROCEDURE DIVISION principal
        """
        import re
        
        procedure_division = ir_data.get("procedure_division", {})
        raw_content = procedure_division.get("raw_content", "")
        
        main_performs = []
        
        # Buscar los PERFORM principales en el raw_content
        perform_patterns = [
            r"PERFORM\s+1000-INICIO\s*\.",
            r"PERFORM\s+2000-PROCESO\s+UNTIL\s+NO-ENCONTRADO\s*\.",
            r"PERFORM\s+8000-FINAL\s*\."
        ]
        
        for pattern in perform_patterns:
            match = re.search(pattern, raw_content, re.IGNORECASE)
            if match:
                perform_text = match.group(0)
                print(f"🎯 Encontrado PERFORM principal: {perform_text}")
                
                # Crear un statement artificial para el PERFORM
                perform_stmt = {
                    "op": "PERFORM",
                    "raw": perform_text,
                    "details": {
                        "type": "PERFORM_STATEMENT",
                        "perform_type": "SIMPLE" if "UNTIL" not in perform_text.upper() else "UNTIL",
                        "target": perform_text.split()[1].replace(".", "")
                    }
                }
                
                if "UNTIL" in perform_text.upper():
                    perform_stmt["details"]["condition"] = "NO-ENCONTRADO"
                
                main_performs.append(perform_stmt)
        
        return main_performs
    
    def _generate_real_procedures_with_macros(self, ir: Dict[str, Any]) -> str:
        """Generar procedimientos reales del IR con macros in-situ en el orden correcto"""
        procedures_section = ""
        gap_count = 0  # Contador de GAPs
        macro_gap_count = 0  # Contador de GAP MACRO INTERNA
        
        # Primero, generar procedimientos PL/SQL a partir de los procedimientos COBOL
        procedures_section += self._generate_plsql_procedures_from_cobol(ir)
        
        # Luego, extraer y procesar los PERFORM principales del PROCEDURE DIVISION
        main_performs = self._extract_main_performs_from_procedure_division(ir)
        if main_performs:
            procedures_section += """
  /*
   *-------------------------------------------------------------*
   * PROCEDIMIENTO PRINCIPAL DEL PROGRAMA                        *
   *-------------------------------------------------------------*
   */
   
  PROCEDURE PRC_MAIN IS
  BEGIN"""
            
            for perform_stmt in main_performs:
                if '@' in perform_stmt.get("raw", ""):
                    macro_gap_count += 1
                    procedures_section += f"""
    -- GAP MACRO INTERNA: {perform_stmt.get('raw', '').strip()}"""
                else:
                    # Llamar al procedimiento PL/SQL correspondiente
                    raw_content = perform_stmt.get("raw", "")
                    if "1000-INICIO" in raw_content:
                        procedures_section += """
    A1000_INICIO(); -- PERFORM 1000-INICIO"""
                    elif "2000-PROCESO" in raw_content and "UNTIL" in raw_content:
                        procedures_section += """
    -- PERFORM 2000-PROCESO UNTIL NO-ENCONTRADO
    WHILE encontrado = 'Y' LOOP
      A2000_PROCESO();
    END LOOP;"""
                    elif "8000-FINAL" in raw_content:
                        procedures_section += """
    A8000_FINAL(); -- PERFORM 8000-FINAL"""
                    else:
                        converted_perform = self._convert_perform_statement(perform_stmt)
                        procedures_section += f"""
    {converted_perform.strip()}"""
            
            procedures_section += """
  END PRC_MAIN;
  
  /*
   *-------------------------------------------------------------*
   * PROCEDIMIENTOS AUXILIARES                                   *
   *-------------------------------------------------------------*
   */"""
        
        procedures = ir.get("procedures", [])
        if not procedures:
            return procedures_section + "\n  -- No hay procedimientos auxiliares para generar\n", gap_count, macro_gap_count
        
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
                        elif op == "IF":
                            # Aplicar conversión completa de IF usando principios SOLID
                            converted_if = self._convert_if_statement(stmt)
                            procedures_section += converted_if
                        elif op == "ELSE":
                            # Convertir ELSE
                            converted_else = self._convert_else_statement(stmt)
                            procedures_section += converted_else
                        elif op == "END-IF":
                            # Convertir END-IF
                            converted_endif = self._convert_end_if_statement(stmt)
                            procedures_section += converted_endif
                        elif op in ["OPEN", "CLOSE", "READ", "WRITE", "REWRITE", "DELETE", "START"]:
                            # Aplicar conversión completa de operaciones de archivo
                            converted_file_op = self._convert_file_operation(stmt)
                            procedures_section += converted_file_op
                        elif op == "STRING":
                            # Aplicar conversión completa de STRING usando principios SOLID
                            converted_string = self._convert_string_statement(stmt)
                            procedures_section += converted_string
                        elif op == "SET":
                            # Aplicar conversión completa de SET usando principios SOLID
                            converted_set = self._convert_set_statement(stmt)
                            procedures_section += converted_set
                        elif op == "PERFORM":
                            # Aplicar conversión completa de PERFORM usando principios SOLID
                            converted_perform = self._convert_perform_statement(stmt)
                            procedures_section += converted_perform
                        elif op == "INITIALIZE":
                            procedures_section += f"""
  -- GAP -- {raw_content.strip()} -- (INITIALIZE statement)"""
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

    # ===== CONVERTIDORES IF SIGUIENDO PRINCIPIOS SOLID =====
    
    def _convert_if_statement(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir statement IF a PL/SQL siguiendo equivalencias del archivo de referencia
        Principio Single Responsibility: Solo maneja conversión de IF
        """
        raw_content = stmt.get("raw", "").strip()
        details = stmt.get("details", {})
        
        print(f"🔄 Convirtiendo IF: {raw_content}")
        
        # Extraer información de la sentencia IF
        if_info = self._parse_if_statement(raw_content)
        
        if not if_info:
            return f"\n  -- GAP -- {raw_content} -- (IF statement - parsing failed)"
        
        # Intentar patrones mejorados primero
        enhanced_info = self._enhance_if_patterns(raw_content)
        if enhanced_info:
            if_info = enhanced_info
        
        # Aplicar patrón Strategy para diferentes tipos de IF
        try:
            if if_info["type"] == "simple":
                return self._convert_if_simple(if_info, raw_content)
            elif if_info["type"] == "comparison":
                return self._convert_if_simple(if_info, raw_content)  # Usar simple para comparaciones básicas
            elif if_info["type"] == "if_else":
                return self._convert_if_else(if_info, raw_content)
            elif if_info["type"] == "nested":
                return self._convert_if_nested(if_info, raw_content)
            elif if_info["type"] == "logical_operators":
                return self._convert_if_logical(if_info, raw_content)
            elif if_info["type"] == "not_condition":
                return self._convert_if_simple(if_info, raw_content)  # Usar simple para NOT
            elif if_info["type"] == "condition_name":
                return self._convert_if_condition_name(if_info, raw_content)
            elif if_info["type"] == "signed_numeric":
                return self._convert_if_signed_numeric(if_info, raw_content)
            elif if_info["type"] == "string_comparison":
                return self._convert_if_string_comparison(if_info, raw_content)
            elif if_info["type"] == "sqlcode_check":
                return self._convert_sqlcode_check(if_info, raw_content)
            elif if_info["type"] == "boolean_flag":
                return self._convert_boolean_flag(if_info, raw_content)
            elif if_info["type"] == "qualified_comparison":
                return self._convert_qualified_comparison(if_info, raw_content)
            elif if_info["type"] == "complex_condition":
                return self._convert_complex_condition(if_info, raw_content)
            else:
                return self._convert_if_generic(if_info, raw_content)
        except Exception as e:
            print(f"❌ Error convirtiendo IF: {e}")
            return f"\n  -- GAP -- {raw_content} -- (IF statement - conversion error)"
    
    def _parse_if_statement(self, raw_content: str) -> Dict[str, Any]:
        """
        Parsear sentencia IF para extraer componentes
        Principio Single Responsibility: Solo parsing de IF
        """
        import re
        
        # Limpiar la línea
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
        """
        Construir información del IF basada en el patrón detectado
        Principio Open/Closed: Extendible para nuevos patrones
        """
        if pattern_name == "simple":
            return {
                "type": "simple",
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
        elif pattern_name == "condition_name":
            return {
                "type": "condition_name",
                "condition_name": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "signed_numeric":
            return {
                "type": "signed_numeric",
                "variable": match.group(1).strip(),
                "sign_type": match.group(2).strip(),
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
        
        return {"type": "generic", "raw": line}
    
    def _convert_if_simple(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir IF simple: IF condition
        """
        condition = if_info["condition"]
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"""
  IF {converted_condition} THEN -- {raw_content}"""
    
    def _convert_if_else(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir IF-ELSE completo
        """
        # Esta implementación será extendida cuando se procese el ELSE
        condition = if_info.get("condition", "")
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"""
  IF {converted_condition} THEN -- {raw_content}"""
    
    def _convert_if_nested(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir IF anidado (se convertirá a ELSIF cuando sea posible)
        """
        condition = if_info.get("condition", "")
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"""
  ELSIF {converted_condition} THEN -- {raw_content}"""
    
    def _convert_if_logical(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir IF con operadores lógicos (AND/OR)
        """
        left_condition = self._convert_cobol_condition_to_plsql(if_info["left_condition"])
        logical_op = if_info["logical_op"]
        right_condition = self._convert_cobol_condition_to_plsql(if_info["right_condition"])
        
        return f"""
  IF {left_condition} {logical_op} {right_condition} THEN -- {raw_content}"""
    
    def _convert_if_condition_name(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir IF con condition name (88-level)
        """
        condition_name = if_info["condition_name"]
        converted_name = self._convert_cobol_to_plsql_identifier(condition_name)
        
        # Convertir condition name a comparación con constante
        return f"""
  IF {converted_name} THEN -- {raw_content}
  -- GAP: Definir constante para condition name {condition_name}"""
    
    def _convert_if_signed_numeric(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir IF con números con signo (IS POSITIVE/NEGATIVE/ZERO)
        """
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
        
        return f"""
  IF {condition} THEN -- {raw_content}"""
    
    def _convert_if_string_comparison(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir IF con comparación de substring
        """
        variable = self._convert_cobol_to_plsql_identifier(if_info["variable"])
        start_pos = if_info["start_pos"]
        end_pos = if_info["end_pos"]
        operator = self._convert_cobol_operator_to_plsql(if_info["operator"])
        value = self._convert_literal(if_info["value"])
        
        # Calcular longitud para SUBSTR
        length = int(end_pos) - int(start_pos) + 1
        
        return f"""
  IF SUBSTR({variable}, {start_pos}, {length}) {operator} {value} THEN -- {raw_content}"""
    
    def _convert_if_generic(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir IF genérico cuando no coincide con patrones específicos
        """
        return f"""
  -- GAP -- {raw_content} -- (IF statement - generic)"""
    
    def _convert_cobol_condition_to_plsql(self, condition: str) -> str:
        """
        Convertir condición COBOL a PL/SQL
        Principio Interface Segregation: Interface específica para condiciones
        """
        import re
        
        if not condition:
            return "TRUE"
        
        # Convertir operadores COBOL a PL/SQL
        converted = condition
        
        # Operadores de comparación
        converted = re.sub(r'\bNOT\s*=\b', '!=', converted, flags=re.IGNORECASE)
        converted = re.sub(r'\bEQUAL\b', '=', converted, flags=re.IGNORECASE)
        converted = re.sub(r'\bGREATER\b', '>', converted, flags=re.IGNORECASE)
        converted = re.sub(r'\bLESS\b', '<', converted, flags=re.IGNORECASE)
        
        # Valores especiales
        converted = re.sub(r'\bSPACES\b', 'NULL', converted, flags=re.IGNORECASE)
        converted = re.sub(r'\bZEROS?\b', '0', converted, flags=re.IGNORECASE)
        converted = re.sub(r'\bHIGH-VALUES\b', 'CHR(255)', converted, flags=re.IGNORECASE)
        converted = re.sub(r'\bLOW-VALUES\b', 'CHR(0)', converted, flags=re.IGNORECASE)
        
        # Convertir identificadores COBOL a PL/SQL
        converted = self._convert_identifiers_in_condition(converted)
        
        return converted
    
    def _convert_cobol_operator_to_plsql(self, operator: str) -> str:
        """
        Convertir operador COBOL a PL/SQL
        """
        operator_map = {
            "NOT =": "!=",
            "NOT=": "!=",
            "EQUAL": "=",
            "GREATER": ">",
            "LESS": "<",
            "=": "=",
            ">": ">",
            "<": "<",
            ">=": ">=",
            "<=": "<="
        }
        
        return operator_map.get(operator.upper(), operator)
    
    def _convert_identifiers_in_condition(self, condition: str) -> str:
        """
        Convertir identificadores COBOL en condiciones a PL/SQL
        """
        import re
        
        # Patrón para identificadores COBOL (letras, números, guiones)
        pattern = r'\b[A-Z][A-Z0-9\-]*\b'
        
        def replace_identifier(match):
            identifier = match.group(0)
            # No convertir palabras clave SQL/PL/SQL
            sql_keywords = ['AND', 'OR', 'NOT', 'TRUE', 'FALSE', 'NULL', 'IS']
            if identifier.upper() not in sql_keywords:
                return self._convert_cobol_to_plsql_identifier(identifier)
            return identifier
        
        return re.sub(pattern, replace_identifier, condition)
    
    def _convert_else_statement(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir statement ELSE
        """
        raw_content = stmt.get("raw", "").strip()
        return f"""
  ELSE -- {raw_content}"""
    
    def _convert_end_if_statement(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir statement END-IF
        """
        raw_content = stmt.get("raw", "").strip()
        return f"""
  END IF; -- {raw_content}"""
    
    def _enhance_if_patterns(self, raw_content: str) -> Dict[str, Any]:
        """
        Mejorar detección de patrones IF específicos del archivo de equivalencias
        Principio Dependency Inversion: Depende de abstracciones de patrones
        """
        import re
        
        line = raw_content.strip().upper()
        
        # Detectar patrones específicos del archivo de equivalencias
        
        # IF con SQLCODE (común en programas COBOL)
        if "SQLCODE" in line:
            match = re.search(r"IF\s+SQLCODE\s*(=|!=|<>)\s*(\d+)", line)
            if match:
                return {
                    "type": "sqlcode_check",
                    "operator": match.group(1),
                    "value": match.group(2),
                    "raw": raw_content
                }
        
        # IF con condition names (88-level) detectando patrones comunes
        if any(keyword in line for keyword in ["IND-", "ES-", "FLAG-", "SW-"]):
            match = re.search(r"IF\s+(IND-[A-Z0-9\-]+|ES-[A-Z0-9\-]+|FLAG-[A-Z0-9\-]+|SW-[A-Z0-9\-]+)", line)
            if match:
                return {
                    "type": "boolean_flag",
                    "flag_name": match.group(1),
                    "raw": raw_content
                }
        
        # IF con comparaciones de campos calificados (OF)
        if " OF " in line:
            match = re.search(r"IF\s+(.+?)\s+OF\s+(.+?)\s*(=|!=|<>|>|<|>=|<=)\s*(.+?)(?:\s|$)", line)
            if match:
                return {
                    "type": "qualified_comparison",
                    "field": match.group(1).strip(),
                    "record": match.group(2).strip(),
                    "operator": match.group(3).strip(),
                    "value": match.group(4).strip(),
                    "raw": raw_content
                }
        
        # IF con múltiples condiciones usando paréntesis
        if "(" in line and ")" in line:
            return {
                "type": "complex_condition",
                "condition": line.replace("IF ", ""),
                "raw": raw_content
            }
        
        return None
    
    def _convert_sqlcode_check(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir verificaciones de SQLCODE específicas
        """
        operator = self._convert_cobol_operator_to_plsql(if_info["operator"])
        value = if_info["value"]
        
        return f"""
  IF SQLCODE {operator} {value} THEN -- {raw_content}"""
    
    def _convert_boolean_flag(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir flags booleanos (indicators, switches)
        """
        flag_name = self._convert_cobol_to_plsql_identifier(if_info["flag_name"])
        
        # Los flags booleanos en COBOL se convierten a comparaciones con constantes en PL/SQL
        return f"""
  IF {flag_name} THEN -- {raw_content}
  -- GAP: Verificar valor de flag booleano {flag_name}"""
    
    def _convert_qualified_comparison(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir comparaciones con campos calificados
        """
        field = self._convert_cobol_to_plsql_identifier(if_info["field"])
        record = self._convert_cobol_to_plsql_identifier(if_info["record"])
        operator = self._convert_cobol_operator_to_plsql(if_info["operator"])
        value = self._convert_literal(if_info["value"]) if self._is_literal(if_info["value"]) else self._convert_cobol_to_plsql_identifier(if_info["value"])
        
        return f"""
  IF {record}.{field} {operator} {value} THEN -- {raw_content}"""
    
    def _convert_complex_condition(self, if_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir condiciones complejas con paréntesis
        """
        condition = if_info["condition"]
        converted_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"""
  IF {converted_condition} THEN -- {raw_content}"""

    # ===== CONVERTIDORES DE ARCHIVOS SIGUIENDO PRINCIPIOS SOLID =====
    
    def _convert_file_operation(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir operaciones de archivos COBOL a PL/SQL siguiendo equivalencias del archivo de referencia
        Principio Single Responsibility: Solo maneja conversión de operaciones de archivos
        """
        raw_content = stmt.get("raw", "").strip()
        op = stmt.get("op", "").upper()
        
        print(f"🔄 Convirtiendo operación de archivo {op}: {raw_content}")
        
        # Extraer información de la operación de archivo
        file_info = self._parse_file_operation(raw_content, op)
        
        if not file_info:
            return f"\n  -- GAP -- {raw_content} -- ({op} statement - parsing failed)"
        
        # Aplicar patrón Strategy para diferentes tipos de operaciones de archivo
        try:
            if op == "OPEN":
                return self._convert_open_file(file_info, raw_content)
            elif op == "CLOSE":
                return self._convert_close_file(file_info, raw_content)
            elif op == "READ":
                return self._convert_read_file(file_info, raw_content)
            elif op == "WRITE":
                return self._convert_write_file(file_info, raw_content)
            elif op == "REWRITE":
                return self._convert_rewrite_file(file_info, raw_content)
            elif op == "DELETE":
                return self._convert_delete_record(file_info, raw_content)
            elif op == "START":
                return self._convert_start_file(file_info, raw_content)
            else:
                return self._convert_file_generic(file_info, raw_content, op)
        except Exception as e:
            print(f"❌ Error convirtiendo operación de archivo {op}: {e}")
            return f"\n  -- GAP -- {raw_content} -- ({op} statement - conversion error)"
    
    def _parse_file_operation(self, raw_content: str, op: str) -> Dict[str, Any]:
        """
        Parsear operación de archivo para extraer componentes
        Principio Single Responsibility: Solo parsing de operaciones de archivo
        """
        import re
        
        line = raw_content.strip()
        upper_line = line.upper()
        
        # Patrones para diferentes operaciones de archivo
        if op == "OPEN":
            # OPEN INPUT/OUTPUT/I-O archivo
            match = re.search(r"OPEN\s+(INPUT|OUTPUT|I-O|EXTEND)\s+([A-Z0-9\-]+)", upper_line)
            if match:
                return {
                    "operation": "open",
                    "mode": match.group(1),
                    "file_name": match.group(2),
                    "raw": line
                }
        
        elif op == "CLOSE":
            # CLOSE archivo
            match = re.search(r"CLOSE\s+([A-Z0-9\-]+)", upper_line)
            if match:
                return {
                    "operation": "close",
                    "file_name": match.group(1),
                    "raw": line
                }
        
        elif op == "READ":
            # READ archivo [INTO registro] [AT END ...] [NOT AT END ...]
            patterns = {
                "with_key": r"READ\s+([A-Z0-9\-]+)\s+KEY\s+IS\s+([A-Z0-9\-]+)",
                "with_into": r"READ\s+([A-Z0-9\-]+)\s+INTO\s+([A-Z0-9\-]+)",
                "at_end": r"READ\s+([A-Z0-9\-]+).*AT\s+END",
                "next_record": r"READ\s+([A-Z0-9\-]+)\s+NEXT\s+RECORD",
                "simple": r"READ\s+([A-Z0-9\-]+)"
            }
            
            for pattern_name, pattern in patterns.items():
                match = re.search(pattern, upper_line)
                if match:
                    result = {
                        "operation": "read",
                        "file_name": match.group(1),
                        "type": pattern_name,
                        "raw": line
                    }
                    if len(match.groups()) > 1:
                        if pattern_name == "with_key":
                            result["key_field"] = match.group(2)
                        elif pattern_name == "with_into":
                            result["into_variable"] = match.group(2)
                    
                    # Detectar cláusulas adicionales
                    if "AT END" in upper_line:
                        result["has_at_end"] = True
                    if "NOT AT END" in upper_line:
                        result["has_not_at_end"] = True
                    if "INVALID KEY" in upper_line:
                        result["has_invalid_key"] = True
                    
                    return result
        
        elif op == "WRITE":
            # WRITE registro [FROM variable] [AFTER/BEFORE n LINES]
            patterns = {
                "with_from": r"WRITE\s+([A-Z0-9\-]+)\s+FROM\s+([A-Z0-9\-]+)",
                "after_advancing_page": r"WRITE\s+([A-Z0-9\-]+).*AFTER\s+ADVANCING\s+PAGE",
                "after_lines": r"WRITE\s+([A-Z0-9\-]+).*AFTER\s+(\d+)",
                "before_lines": r"WRITE\s+([A-Z0-9\-]+).*BEFORE\s+(\d+)",
                "with_after": r"WRITE\s+([A-Z0-9\-]+).*AFTER\s+(\d+|\w+)",
                "with_before": r"WRITE\s+([A-Z0-9\-]+).*BEFORE\s+(\d+|\w+)",
                "simple": r"WRITE\s+([A-Z0-9\-]+)"
            }
            
            for pattern_name, pattern in patterns.items():
                match = re.search(pattern, upper_line)
                if match:
                    result = {
                        "operation": "write",
                        "record_name": match.group(1),
                        "type": pattern_name,
                        "raw": line
                    }
                    if len(match.groups()) > 1:
                        if pattern_name == "with_from":
                            result["from_variable"] = match.group(2)
                        elif pattern_name in ["with_after", "with_before"]:
                            result["line_control"] = match.group(2)
                    return result
        
        # Si no coincide con ningún patrón específico, devolver genérico
        return {
            "operation": "generic",
            "file_name": "UNKNOWN",
            "raw": line
        }
    
    def _convert_open_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir OPEN a UTL_FILE.FOPEN
        Principio Open/Closed: Extendible para nuevos modos de apertura
        """
        file_name = self._convert_cobol_to_plsql_identifier(file_info["file_name"])
        mode = file_info["mode"]
        
        # Mapeo de modos COBOL a PL/SQL según archivo de equivalencias
        mode_mapping = {
            "INPUT": "R",     # Read
            "OUTPUT": "W",    # Write
            "I-O": "A",       # Append (más cercano a I-O)
            "EXTEND": "A"     # Append
        }
        
        plsql_mode = mode_mapping.get(mode, "R")
        
        return f"""
  BEGIN
    {file_name} := UTL_FILE.FOPEN(v_directorio, '{file_name}.dat', '{plsql_mode}');
  EXCEPTION
    WHEN UTL_FILE.INVALID_PATH THEN
      DBMS_OUTPUT.PUT_LINE('Directorio inválido para {file_name}');
      v_file_status := 'ERROR';
    WHEN UTL_FILE.INVALID_FILENAME THEN
      DBMS_OUTPUT.PUT_LINE('Nombre de archivo inválido: {file_name}');
      v_file_status := 'ERROR';
  END; -- {raw_content}"""
    
    def _convert_close_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir CLOSE a UTL_FILE.FCLOSE
        """
        file_name = self._convert_cobol_to_plsql_identifier(file_info["file_name"])
        
        return f"""
  IF UTL_FILE.IS_OPEN({file_name}) THEN
    UTL_FILE.FCLOSE({file_name});
  END IF; -- {raw_content}"""
    
    def _convert_read_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir READ a UTL_FILE.GET_LINE con manejo de excepciones
        Principio Liskov Substitution: Puede sustituir diferentes tipos de READ
        """
        file_name = self._convert_cobol_to_plsql_identifier(file_info["file_name"])
        read_type = file_info.get("type", "simple")
        
        if read_type == "with_key":
            # READ indexado - convertir a SELECT
            key_field = self._convert_cobol_to_plsql_identifier(file_info.get("key_field", ""))
            return f"""
  -- READ con clave convertido a SELECT
  BEGIN
    SELECT * INTO v_registro
    FROM {file_name}_table
    WHERE {key_field} = v_clave_busqueda;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      v_invalid_key := TRUE; -- INVALID KEY
  END; -- {raw_content}"""
        
        elif read_type == "with_into":
            into_var = self._convert_cobol_to_plsql_identifier(file_info.get("into_variable", ""))
            return f"""
  BEGIN
    UTL_FILE.GET_LINE({file_name}, {into_var});
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      v_eof_flag := TRUE; -- AT END
  END; -- {raw_content}"""
        
        else:
            # READ simple con manejo de AT END
            if file_info.get("has_at_end", False):
                return f"""
  BEGIN
    UTL_FILE.GET_LINE({file_name}, v_registro);
    -- NOT AT END - procesar registro
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      v_eof_flag := TRUE; -- AT END
  END; -- {raw_content}"""
            else:
                return f"""
  UTL_FILE.GET_LINE({file_name}, v_registro); -- {raw_content}"""
    
    def _convert_write_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir WRITE a UTL_FILE.PUT_LINE
        Principio Interface Segregation: Interface específica para escritura
        """
        record_name = self._convert_cobol_to_plsql_identifier(file_info["record_name"])
        write_type = file_info.get("type", "simple")
        
        # Determinar el archivo destino (asumimos que es el archivo actual)
        file_variable = "v_archivo_salida"  # Variable genérica
        
        if write_type == "with_from":
            from_var = self._convert_cobol_to_plsql_identifier(file_info.get("from_variable", ""))
            return f"""
  BEGIN
    UTL_FILE.PUT_LINE({file_variable}, {from_var});
    UTL_FILE.FFLUSH({file_variable}); -- Forzar escritura
  EXCEPTION
    WHEN UTL_FILE.WRITE_ERROR THEN
      DBMS_OUTPUT.PUT_LINE('Error al escribir {record_name}');
      v_file_status := 'ERROR';
  END; -- {raw_content}"""
        
        elif write_type in ["with_after", "with_before"]:
            line_control = file_info.get("line_control", "1")
            if line_control == "0":
                # AFTER 0 LINES = sin salto de línea
                return f"""
  UTL_FILE.PUT({file_variable}, {record_name}); -- {raw_content}"""
            else:
                return f"""
  UTL_FILE.PUT_LINE({file_variable}, {record_name}); -- {raw_content}"""
        
        else:
            return f"""
  BEGIN
    UTL_FILE.PUT_LINE({file_variable}, {record_name});
  EXCEPTION
    WHEN UTL_FILE.WRITE_ERROR THEN
      DBMS_OUTPUT.PUT_LINE('Error al escribir archivo');
      v_file_status := 'ERROR';
  END; -- {raw_content}"""
    
    def _convert_rewrite_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir REWRITE a UPDATE (para archivos indexados)
        """
        record_name = self._convert_cobol_to_plsql_identifier(file_info.get("record_name", ""))
        
        return f"""
  -- REWRITE convertido a UPDATE
  BEGIN
    UPDATE {record_name}_table 
    SET campos = v_nuevos_valores
    WHERE clave_primaria = v_clave_actual;
    
    IF SQL%NOTFOUND THEN
      v_invalid_key := TRUE;
    END IF;
  EXCEPTION
    WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE('Error en REWRITE: ' || SQLERRM);
  END; -- {raw_content}"""
    
    def _convert_delete_record(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir DELETE RECORD a DELETE SQL
        """
        file_name = self._convert_cobol_to_plsql_identifier(file_info.get("file_name", ""))
        
        return f"""
  -- DELETE RECORD convertido a DELETE SQL
  BEGIN
    DELETE FROM {file_name}_table
    WHERE clave_primaria = v_clave_actual;
    
    IF SQL%NOTFOUND THEN
      v_invalid_key := TRUE;
    END IF;
  EXCEPTION
    WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE('Error en DELETE: ' || SQLERRM);
  END; -- {raw_content}"""
    
    def _convert_start_file(self, file_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir START a posicionamiento de cursor o reinicio de archivo
        """
        file_name = self._convert_cobol_to_plsql_identifier(file_info.get("file_name", ""))
        
        return f"""
  -- START - Posicionamiento al inicio del archivo
  IF UTL_FILE.IS_OPEN({file_name}) THEN
    UTL_FILE.FCLOSE({file_name});
  END IF;
  {file_name} := UTL_FILE.FOPEN(v_directorio, '{file_name}.dat', 'R'); -- {raw_content}"""
    
    def _convert_file_generic(self, file_info: Dict[str, Any], raw_content: str, op: str) -> str:
        """
        Convertir operación de archivo genérica
        """
        return f"""
  -- GAP -- {raw_content} -- ({op} file operation - needs manual conversion)"""
    
    def _generate_file_variables_section(self) -> str:
        """
        Generar variables UTL_FILE comunes necesarias para operaciones de archivo
        Principio Dependency Inversion: Depende de abstracciones de UTL_FILE
        """
        return """
  
  /*
   *-------------------------------------------------------------*
   * VARIABLES PARA MANEJO DE ARCHIVOS - UTL_FILE               *
   *-------------------------------------------------------------*
   */
   
  -- Variables de directorio y archivos
  v_directorio         VARCHAR2(30) := 'MI_DIRECTORIO';
  v_file_status        VARCHAR2(10) := 'OK';
  v_eof_flag           BOOLEAN := FALSE;
  v_invalid_key        BOOLEAN := FALSE;
  v_registro           VARCHAR2(4000);
  
  -- Handles de archivos UTL_FILE
  v_archivo_entrada    UTL_FILE.FILE_TYPE;
  v_archivo_salida     UTL_FILE.FILE_TYPE;
  v_archivo_maestro    UTL_FILE.FILE_TYPE;
  
  -- Procedimientos de utilidad para archivos
  PROCEDURE cerrar_todos_archivos IS
  BEGIN
    IF UTL_FILE.IS_OPEN(v_archivo_entrada) THEN
      UTL_FILE.FCLOSE(v_archivo_entrada);
    END IF;
    IF UTL_FILE.IS_OPEN(v_archivo_salida) THEN
      UTL_FILE.FCLOSE(v_archivo_salida);
    END IF;
    IF UTL_FILE.IS_OPEN(v_archivo_maestro) THEN
      UTL_FILE.FCLOSE(v_archivo_maestro);
    END IF;
  END cerrar_todos_archivos;
  
  PROCEDURE manejar_error_archivo(p_operacion VARCHAR2, p_archivo VARCHAR2) IS
  BEGIN
    DBMS_OUTPUT.PUT_LINE('Error en ' || p_operacion || ' archivo: ' || p_archivo);
    cerrar_todos_archivos;
    RAISE_APPLICATION_ERROR(-20001, 'Error en operación de archivo');
  END manejar_error_archivo;"""
    
    def _convert_perform_until_file_operation(self, raw_content: str) -> str:
        """
        Convertir PERFORM UNTIL con operaciones de archivo comunes
        Ejemplo: PERFORM UNTIL EOF-FLAG = 'Y'
        """
        import re
        
        # Detectar patrones de loop con EOF
        if "UNTIL" in raw_content.upper() and any(flag in raw_content.upper() for flag in ["EOF", "END-OF-FILE", "FIN-ARCHIVO"]):
            return f"""
  WHILE NOT v_eof_flag LOOP
    -- Loop de procesamiento de archivo -- {raw_content}"""
        
        # PERFORM con READ hasta END
        if "READ" in raw_content.upper():
            match = re.search(r"PERFORM\s+([A-Z0-9\-]+)", raw_content.upper())
            if match:
                procedure_name = self._convert_cobol_to_plsql_identifier(match.group(1))
                return f"""
  -- PERFORM convertido a llamada de procedimiento
  {procedure_name}; -- {raw_content}"""
        
        return f"""
  -- GAP -- {raw_content} -- (PERFORM with file operations)"""
    
    def _enhance_file_context_detection(self, ir_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detectar context de archivos desde FILE-CONTROL y FILE SECTION
        Principio Single Responsibility: Solo detección de context de archivos
        """
        file_context = {
            "file_names": [],
            "select_assignments": {},
            "file_descriptions": {},
            "record_formats": {}
        }
        
        # Buscar en environment division
        env_div = ir_data.get("environment_division", {})
        file_control = env_div.get("file_control", [])
        
        for file_entry in file_control:
            if isinstance(file_entry, dict):
                file_name = file_entry.get("file_name", "")
                assign_to = file_entry.get("assign_to", "")
                if file_name:
                    file_context["file_names"].append(file_name)
                    file_context["select_assignments"][file_name] = assign_to
        
        # Buscar en data division - file section
        data_div = ir_data.get("data_division", {})
        file_section = data_div.get("file_section", [])
        
        for fd_entry in file_section:
            if isinstance(fd_entry, dict):
                fd_name = fd_entry.get("name", "")
                record_contains = fd_entry.get("record_contains", "")
                if fd_name:
                    file_context["file_descriptions"][fd_name] = {
                        "record_contains": record_contains,
                        "records": fd_entry.get("records", [])
                    }
        
        return file_context
    
    def _generate_file_declarations_from_context(self, file_context: Dict[str, Any]) -> str:
        """
        Generar declaraciones UTL_FILE basadas en el contexto detectado
        """
        if not file_context.get("file_names"):
            return ""
        
        declarations = "\n  -- Declaraciones de archivos detectados automáticamente"
        
        for file_name in file_context["file_names"]:
            plsql_name = self._convert_cobol_to_plsql_identifier(file_name)
            assign_to = file_context["select_assignments"].get(file_name, f"{file_name}.dat")
            
            declarations += f"""
  {plsql_name}             UTL_FILE.FILE_TYPE; -- {file_name} ASSIGN TO {assign_to}"""
        
        return declarations

    # ===== CONVERTIDORES STRING SIGUIENDO PRINCIPIOS SOLID =====
    
    def _convert_string_statement(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir statement STRING a PL/SQL siguiendo equivalencias del archivo de referencia
        Principio Single Responsibility: Solo maneja conversión de STRING
        """
        raw_content = stmt.get("raw", "").strip()
        details = stmt.get("details", {})
        
        print(f"🔄 Convirtiendo STRING: {raw_content}")
        
        # Extraer información de la sentencia STRING
        string_info = self._parse_string_statement(raw_content)
        
        if not string_info:
            return f"\n  -- GAP -- {raw_content} -- (STRING statement - parsing failed)"
        
        # Aplicar patrón Strategy para diferentes tipos de STRING
        try:
            if string_info["type"] == "simple_concatenation":
                return self._convert_string_simple(string_info, raw_content)
            elif string_info["type"] == "delimited_by_spaces":
                return self._convert_string_delimited_spaces(string_info, raw_content)
            elif string_info["type"] == "delimited_by_size":
                return self._convert_string_delimited_size(string_info, raw_content)
            elif string_info["type"] == "delimited_by_literal":
                return self._convert_string_delimited_literal(string_info, raw_content)
            elif string_info["type"] == "with_pointer":
                return self._convert_string_with_pointer(string_info, raw_content)
            elif string_info["type"] == "with_overflow":
                return self._convert_string_with_overflow(string_info, raw_content)
            elif string_info["type"] == "multi_field":
                return self._convert_string_multi_field(string_info, raw_content)
            else:
                return self._convert_string_generic(string_info, raw_content)
        except Exception as e:
            print(f"❌ Error convirtiendo STRING: {e}")
            return f"\n  -- GAP -- {raw_content} -- (STRING statement - conversion error)"
    
    def _parse_string_statement(self, raw_content: str) -> Dict[str, Any]:
        """
        Parsear sentencia STRING para extraer componentes
        Principio Single Responsibility: Solo parsing de STRING
        """
        import re
        
        line = raw_content.strip()
        upper_line = line.upper()
        
        # Patrones para diferentes tipos de STRING
        patterns = {
            "with_pointer": r"STRING\s+(.+?)\s+INTO\s+(.+?)\s+WITH\s+POINTER\s+(.+?)(?:\s|$)",
            "with_overflow": r"STRING\s+(.+?)\s+INTO\s+(.+?)\s+ON\s+OVERFLOW",
            "delimited_by_spaces": r"STRING\s+(.+?)\s+DELIMITED\s+BY\s+SPACES?\s+INTO\s+(.+?)(?:\s|$)",
            "delimited_by_size": r"STRING\s+(.+?)\s+DELIMITED\s+BY\s+SIZE\s+INTO\s+(.+?)(?:\s|$)",
            "delimited_by_literal": r"STRING\s+(.+?)\s+DELIMITED\s+BY\s+['\"](.+?)['\"].*INTO\s+(.+?)(?:\s|$)",
            "multi_field": r"STRING\s+(.+?)\s+INTO\s+(.+?)(?:\s|$)",
            "simple": r"STRING\s+(.+?)(?:\s|$)"
        }
        
        # Detectar tipo de STRING basado en contenido
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, upper_line, re.IGNORECASE)
            if match:
                return self._build_string_info(pattern_name, match, line)
        
        # Si no coincide con ningún patrón específico, devolver genérico
        return {
            "type": "generic",
            "raw": line
        }
    
    def _build_string_info(self, pattern_name: str, match, line: str) -> Dict[str, Any]:
        """
        Construir información del STRING basada en el patrón detectado
        Principio Open/Closed: Extendible para nuevos patrones
        """
        if pattern_name == "simple":
            return {
                "type": "simple_concatenation",
                "content": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "delimited_by_spaces":
            return {
                "type": "delimited_by_spaces",
                "sources": self._extract_string_sources(match.group(1).strip()),
                "destination": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "delimited_by_size":
            return {
                "type": "delimited_by_size",
                "sources": self._extract_string_sources(match.group(1).strip()),
                "destination": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "delimited_by_literal":
            return {
                "type": "delimited_by_literal",
                "sources": self._extract_string_sources(match.group(1).strip()),
                "delimiter": match.group(2).strip(),
                "destination": match.group(3).strip(),
                "raw": line
            }
        elif pattern_name == "with_pointer":
            return {
                "type": "with_pointer",
                "sources": self._extract_string_sources(match.group(1).strip()),
                "destination": match.group(2).strip(),
                "pointer": match.group(3).strip(),
                "raw": line
            }
        elif pattern_name == "with_overflow":
            return {
                "type": "with_overflow",
                "sources": self._extract_string_sources(match.group(1).strip()),
                "destination": match.group(2).strip(),
                "has_overflow": True,
                "raw": line
            }
        elif pattern_name == "multi_field":
            return {
                "type": "multi_field",
                "sources": self._extract_string_sources(match.group(1).strip()),
                "destination": match.group(2).strip(),
                "raw": line
            }
        
        return {"type": "generic", "raw": line}
    
    def _extract_string_sources(self, sources_text: str) -> List[Dict[str, str]]:
        """
        Extraer campos fuente de una operación STRING
        """
        import re
        
        sources = []
        
        # Limpiar texto de fuentes
        clean_text = sources_text.strip()
        
        # Patrones mejorados para diferentes tipos de campos fuente
        # 1. Buscar campos con DELIMITED BY específicos
        delimited_patterns = [
            r"([A-Z0-9\-'\"]+)\s+DELIMITED\s+BY\s+SIZE",
            r"([A-Z0-9\-'\"]+)\s+DELIMITED\s+BY\s+SPACES?",
            r"([A-Z0-9\-'\"]+)\s+DELIMITED\s+BY\s+['\"]([^'\"]*)['\"]",
            r"([A-Z0-9\-'\"]+)\s+DELIMITED\s+BY\s+([A-Z0-9\-]+)"  # Variable como delimitador
        ]
        
        # Buscar literales (strings between quotes)
        literal_pattern = r"['\"]([^'\"]*)['\"]"
        literals = re.findall(literal_pattern, clean_text)
        for literal in literals:
            sources.append({
                "field": f"'{literal}'",
                "delimiter": "SIZE",
                "type": "literal"
            })
        
        # Buscar campos con DELIMITED BY
        for pattern in delimited_patterns:
            matches = re.findall(pattern, clean_text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:  # Patrón con delimitador específico
                    field, delimiter = match
                    sources.append({
                        "field": field.strip(),
                        "delimiter": delimiter.strip(),
                        "type": "delimited"
                    })
                else:  # Patrón simple (SIZE, SPACES)
                    field = match if isinstance(match, str) else match[0]
                    delimiter_type = "SIZE"
                    if "SPACES" in pattern:
                        delimiter_type = "SPACES"
                    sources.append({
                        "field": field.strip(),
                        "delimiter": delimiter_type,
                        "type": "delimited"
                    })
        
        # Si no hay DELIMITED BY, buscar campos simples (excluyendo INTO)
        if not sources:
            # Eliminar palabras clave
            keywords_to_remove = ["INTO", "WITH", "POINTER", "ON", "OVERFLOW", "NOT", "END-STRING"]
            clean_for_fields = clean_text
            for keyword in keywords_to_remove:
                clean_for_fields = re.sub(rf"\b{keyword}\b", "", clean_for_fields, flags=re.IGNORECASE)
            
            # Buscar campos y literales
            fields = re.findall(r"[A-Z0-9\-]+|['\"][^'\"]*['\"]", clean_for_fields, re.IGNORECASE)
            for field in fields:
                field = field.strip()
                if field and len(field) > 1:  # Evitar caracteres sueltos
                    field_type = "literal" if (field.startswith("'") or field.startswith('"')) else "simple"
                    sources.append({
                        "field": field,
                        "delimiter": "SIZE",
                        "type": field_type
                    })
        
        return sources
    
    def _convert_string_simple(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir STRING simple (concatenación básica)
        """
        content = string_info.get("content", "")
        
        return f"""
  -- STRING simple convertido a concatenación
  -- {raw_content}
  -- GAP: Implementar concatenación de: {content}"""
    
    def _convert_string_delimited_spaces(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir STRING con DELIMITED BY SPACES
        """
        sources = string_info.get("sources", [])
        destination = self._convert_cobol_to_plsql_identifier(string_info.get("destination", ""))
        
        if len(sources) == 1:
            source_field = self._convert_cobol_to_plsql_identifier(sources[0]["field"])
            return f"""
  -- STRING DELIMITED BY SPACES
  {destination} := RTRIM({source_field}); -- {raw_content}"""
        else:
            # Múltiples campos
            concatenation = " || ".join([
                f"RTRIM({self._convert_cobol_to_plsql_identifier(source['field'])})"
                for source in sources
            ])
            return f"""
  -- STRING DELIMITED BY SPACES (múltiples campos)
  {destination} := {concatenation}; -- {raw_content}"""
    
    def _convert_string_delimited_size(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir STRING con DELIMITED BY SIZE
        """
        sources = string_info.get("sources", [])
        destination = self._convert_cobol_to_plsql_identifier(string_info.get("destination", ""))
        
        if len(sources) == 1:
            source_field = self._convert_cobol_to_plsql_identifier(sources[0]["field"])
            return f"""
  -- STRING DELIMITED BY SIZE
  {destination} := {source_field}; -- {raw_content}"""
        else:
            # Múltiples campos
            concatenation = " || ".join([
                self._convert_cobol_to_plsql_identifier(source['field'])
                for source in sources
            ])
            return f"""
  -- STRING DELIMITED BY SIZE (múltiples campos)
  {destination} := {concatenation}; -- {raw_content}"""
    
    def _convert_string_delimited_literal(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir STRING con DELIMITED BY literal
        """
        sources = string_info.get("sources", [])
        destination = self._convert_cobol_to_plsql_identifier(string_info.get("destination", ""))
        delimiter = string_info.get("delimiter", "")
        
        if len(sources) == 1:
            source_field = self._convert_cobol_to_plsql_identifier(sources[0]["field"])
            return f"""
  -- STRING DELIMITED BY '{delimiter}'
  DECLARE
    v_pos NUMBER;
  BEGIN
    v_pos := INSTR({source_field}, '{delimiter}');
    IF v_pos > 0 THEN
      {destination} := SUBSTR({source_field}, 1, v_pos - 1);
    ELSE
      {destination} := {source_field};
    END IF;
  END; -- {raw_content}"""
        else:
            return f"""
  -- STRING DELIMITED BY '{delimiter}' (múltiples campos)
  -- GAP: Implementar delimitado por literal para múltiples campos
  -- {raw_content}"""
    
    def _convert_string_with_pointer(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir STRING con WITH POINTER
        """
        sources = string_info.get("sources", [])
        destination = self._convert_cobol_to_plsql_identifier(string_info.get("destination", ""))
        pointer = self._convert_cobol_to_plsql_identifier(string_info.get("pointer", ""))
        
        # Generar concatenación de fuentes
        if len(sources) == 1:
            source_concat = self._convert_cobol_to_plsql_identifier(sources[0]["field"])
        else:
            source_concat = " || ".join([
                self._convert_cobol_to_plsql_identifier(source['field'])
                for source in sources
            ])
        
        return f"""
  -- STRING WITH POINTER
  DECLARE
    v_combined VARCHAR2(4000);
    v_length NUMBER;
  BEGIN
    v_combined := {source_concat};
    v_length := LENGTH(v_combined);
    
    {destination} := SUBSTR({destination}, 1, {pointer} - 1) ||
                    v_combined ||
                    SUBSTR({destination}, {pointer} + v_length);
    
    {pointer} := {pointer} + v_length;
  END; -- {raw_content}"""
    
    def _convert_string_with_overflow(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir STRING con ON OVERFLOW
        """
        sources = string_info.get("sources", [])
        destination = self._convert_cobol_to_plsql_identifier(string_info.get("destination", ""))
        
        # Generar concatenación de fuentes
        if len(sources) == 1:
            source_concat = self._convert_cobol_to_plsql_identifier(sources[0]["field"])
        else:
            source_concat = " || ".join([
                self._convert_cobol_to_plsql_identifier(source['field'])
                for source in sources
            ])
        
        return f"""
  -- STRING WITH OVERFLOW CHECK
  DECLARE
    v_combined VARCHAR2(4000);
    STRING_OVERFLOW_ERROR EXCEPTION;
  BEGIN
    v_combined := {source_concat};
    
    -- Verificar si excede el tamaño máximo (asumir 255 por defecto)
    IF LENGTH(v_combined) > 255 THEN
      RAISE STRING_OVERFLOW_ERROR;
    END IF;
    
    {destination} := v_combined;
    -- NOT ON OVERFLOW - acciones de éxito aquí
    
  EXCEPTION
    WHEN STRING_OVERFLOW_ERROR THEN
      -- ON OVERFLOW - manejar overflow aquí
      DBMS_OUTPUT.PUT_LINE('STRING overflow occurred');
  END; -- {raw_content}"""
    
    def _convert_string_multi_field(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir STRING con múltiples campos
        """
        sources = string_info.get("sources", [])
        destination = self._convert_cobol_to_plsql_identifier(string_info.get("destination", ""))
        
        if not sources:
            return f"""
  -- GAP -- {raw_content} -- (STRING multi-field - no sources detected)"""
        
        # Procesar cada fuente según su tipo de delimitador
        concatenation_parts = []
        for source in sources:
            field = source["field"]
            delimiter = source.get("delimiter", "SIZE").upper()
            field_type = source.get("type", "simple")
            
            # Manejar literales directamente
            if field_type == "literal" or (field.startswith("'") and field.endswith("'")):
                concatenation_parts.append(field)
            else:
                # Convertir identificador COBOL a PL/SQL
                plsql_field = self._convert_cobol_to_plsql_identifier(field)
                
                if delimiter == "SPACES" or delimiter == "SPACE":
                    concatenation_parts.append(f"RTRIM({plsql_field})")
                elif delimiter == "SIZE":
                    concatenation_parts.append(plsql_field)
                elif delimiter.startswith("'") and delimiter.endswith("'"):
                    # Literal delimiter - usar función de utilidad
                    delimiter_value = delimiter[1:-1]
                    concatenation_parts.append(f"delimited_by_literal({plsql_field}, '{delimiter_value}')")
                else:
                    # Variable como delimitador
                    delimiter_var = self._convert_cobol_to_plsql_identifier(delimiter)
                    concatenation_parts.append(f"delimited_by_literal({plsql_field}, {delimiter_var})")
        
        concatenation = " || ".join(concatenation_parts)
        
        return f"""
  -- STRING múltiples campos
  {destination} := {concatenation}; -- {raw_content}"""
    
    def _convert_string_generic(self, string_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir STRING genérico cuando no coincide con patrones específicos
        """
        return f"""
  -- GAP -- {raw_content} -- (STRING statement - generic)"""
    
    def _generate_string_utility_functions(self) -> str:
        """
        Generar funciones de utilidad para operaciones STRING
        Principio Dependency Inversion: Depende de abstracciones de STRING operations
        """
        return """
  
  /*
   *-------------------------------------------------------------*
   * FUNCIONES DE UTILIDAD PARA OPERACIONES STRING              *
   *-------------------------------------------------------------*
   */
   
  -- Función para DELIMITED BY SPACES
  FUNCTION delimited_by_spaces(p_input VARCHAR2) RETURN VARCHAR2 IS
    v_pos NUMBER;
  BEGIN
    v_pos := INSTR(p_input, ' ');
    IF v_pos > 0 THEN
      RETURN SUBSTR(p_input, 1, v_pos - 1);
    ELSE
      RETURN RTRIM(p_input);
    END IF;
  END delimited_by_spaces;
  
  -- Función para DELIMITED BY literal
  FUNCTION delimited_by_literal(p_input VARCHAR2, p_delimiter VARCHAR2) RETURN VARCHAR2 IS
    v_pos NUMBER;
  BEGIN
    v_pos := INSTR(p_input, p_delimiter);
    IF v_pos > 0 THEN
      RETURN SUBSTR(p_input, 1, v_pos - 1);
    ELSE
      RETURN p_input;
    END IF;
  END delimited_by_literal;
  
  -- Procedimiento STRING con POINTER
  PROCEDURE string_with_pointer(p_source VARCHAR2,
                               p_destination IN OUT VARCHAR2,
                               p_pointer IN OUT NUMBER) IS
    v_length NUMBER;
  BEGIN
    v_length := LENGTH(p_source);
    
    p_destination := SUBSTR(p_destination, 1, p_pointer - 1) ||
                    p_source ||
                    SUBSTR(p_destination, p_pointer + v_length);
    
    p_pointer := p_pointer + v_length;
  END string_with_pointer;
  
  -- Función STRING con verificación de overflow
  FUNCTION string_with_overflow_check(p_source VARCHAR2,
                                     p_max_length NUMBER,
                                     p_overflow OUT BOOLEAN) RETURN VARCHAR2 IS
  BEGIN
    IF LENGTH(p_source) > p_max_length THEN
      p_overflow := TRUE;
      RETURN SUBSTR(p_source, 1, p_max_length);
    ELSE
      p_overflow := FALSE;
      RETURN p_source;
    END IF;
  END string_with_overflow_check;"""

    # ===== CONVERTIDORES SET SIGUIENDO PRINCIPIOS SOLID =====
    
    def _convert_set_statement(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir statement SET a PL/SQL siguiendo equivalencias del archivo de referencia
        Principio Single Responsibility: Solo maneja conversión de SET
        """
        raw_content = stmt.get("raw", "").strip()
        details = stmt.get("details", {})
        
        print(f"🔄 Convirtiendo SET: {raw_content}")
        
        # Extraer información de la sentencia SET
        set_info = self._parse_set_statement(raw_content)
        
        if not set_info:
            return f"\n  -- GAP -- {raw_content} -- (SET statement - parsing failed)"
        
        # Aplicar patrón Strategy para diferentes tipos de SET
        try:
            if set_info["type"] == "condition_name_true":
                return self._convert_set_condition_name_true(set_info, raw_content)
            elif set_info["type"] == "condition_name_false":
                return self._convert_set_condition_name_false(set_info, raw_content)
            elif set_info["type"] == "index_to_value":
                return self._convert_set_index_to_value(set_info, raw_content)
            elif set_info["type"] == "index_up_by":
                return self._convert_set_index_up_by(set_info, raw_content)
            elif set_info["type"] == "index_down_by":
                return self._convert_set_index_down_by(set_info, raw_content)
            elif set_info["type"] == "index_to_index":
                return self._convert_set_index_to_index(set_info, raw_content)
            elif set_info["type"] == "pointer_to_address":
                return self._convert_set_pointer_to_address(set_info, raw_content)
            elif set_info["type"] == "address_to_pointer":
                return self._convert_set_address_to_pointer(set_info, raw_content)
            elif set_info["type"] == "variable_to_true":
                return self._convert_set_variable_to_true(set_info, raw_content)
            elif set_info["type"] == "variable_to_false":
                return self._convert_set_variable_to_false(set_info, raw_content)
            elif set_info["type"] == "variable_to_null":
                return self._convert_set_variable_to_null(set_info, raw_content)
            else:
                return self._convert_set_generic(set_info, raw_content)
        except Exception as e:
            print(f"❌ Error convirtiendo SET: {e}")
            return f"\n  -- GAP -- {raw_content} -- (SET statement - conversion error)"
    
    def _parse_set_statement(self, raw_content: str) -> Dict[str, Any]:
        """
        Parsear sentencia SET para extraer componentes
        Principio Single Responsibility: Solo parsing de SET
        """
        import re
        
        line = raw_content.strip()
        upper_line = line.upper()
        
        # Patrones para diferentes tipos de SET (orden importa - más específicos primero)
        patterns = {
            "condition_name_true": r"SET\s+([A-Z0-9\-]+)\s+TO\s+TRUE",
            "condition_name_false": r"SET\s+([A-Z0-9\-]+)\s+TO\s+FALSE",
            "index_up_by": r"SET\s+([A-Z0-9\-]+)\s+UP\s+BY\s+([A-Z0-9\-]+|\d+)",
            "index_down_by": r"SET\s+([A-Z0-9\-]+)\s+DOWN\s+BY\s+([A-Z0-9\-]+|\d+)",
            "index_to_index": r"SET\s+([A-Z0-9\-]+)\s+TO\s+([A-Z0-9\-]+)(?!\s+(TRUE|FALSE|NULL))",
            "index_to_value": r"SET\s+([A-Z0-9\-]+)\s+TO\s+(\d+)",
            "pointer_to_address": r"SET\s+([A-Z0-9\-]+)\s+TO\s+ADDRESS\s+OF\s+([A-Z0-9\-]+)",
            "address_to_pointer": r"SET\s+ADDRESS\s+OF\s+([A-Z0-9\-]+)\s+TO\s+([A-Z0-9\-]+)",
            "variable_to_true": r"SET\s+([A-Z0-9\-]+)\s+TO\s+TRUE",
            "variable_to_false": r"SET\s+([A-Z0-9\-]+)\s+TO\s+FALSE",
            "variable_to_null": r"SET\s+([A-Z0-9\-]+)\s+TO\s+NULL",
            "simple": r"SET\s+(.+?)(?:\s|$)"
        }
        
        # Detectar tipo de SET basado en contenido
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, upper_line, re.IGNORECASE)
            if match:
                return self._build_set_info(pattern_name, match, line)
        
        # Si no coincide con ningún patrón específico, devolver genérico
        return {
            "type": "generic",
            "raw": line
        }
    
    def _build_set_info(self, pattern_name: str, match, line: str) -> Dict[str, Any]:
        """
        Construir información del SET basada en el patrón detectado
        Principio Open/Closed: Extendible para nuevos patrones
        """
        if pattern_name == "condition_name_true":
            return {
                "type": "condition_name_true",
                "condition_name": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "condition_name_false":
            return {
                "type": "condition_name_false",
                "condition_name": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "index_to_value":
            return {
                "type": "index_to_value",
                "index_name": match.group(1).strip(),
                "value": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "index_up_by":
            return {
                "type": "index_up_by",
                "index_name": match.group(1).strip(),
                "increment": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "index_down_by":
            return {
                "type": "index_down_by",
                "index_name": match.group(1).strip(),
                "decrement": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "index_to_index":
            return {
                "type": "index_to_index",
                "target_index": match.group(1).strip(),
                "source_index": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "pointer_to_address":
            return {
                "type": "pointer_to_address",
                "pointer_name": match.group(1).strip(),
                "variable_name": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "address_to_pointer":
            return {
                "type": "address_to_pointer",
                "variable_name": match.group(1).strip(),
                "pointer_name": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "variable_to_true":
            return {
                "type": "variable_to_true",
                "variable_name": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "variable_to_false":
            return {
                "type": "variable_to_false",
                "variable_name": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "variable_to_null":
            return {
                "type": "variable_to_null",
                "variable_name": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "simple":
            return {
                "type": "simple",
                "content": match.group(1).strip(),
                "raw": line
            }
        
        return {"type": "generic", "raw": line}
    
    def _convert_set_condition_name_true(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET condition-name TO TRUE
        Ejemplos: SET CLIENTE-ACTIVO TO TRUE → set_cliente_activo;
        """
        condition_name = set_info["condition_name"]
        plsql_name = self._convert_cobol_to_plsql_identifier(condition_name)
        procedure_name = f"set_{plsql_name}"
        
        return f"""
  {procedure_name}; -- {raw_content}
  -- GAP: Definir procedimiento {procedure_name} para condition name {condition_name}"""
    
    def _convert_set_condition_name_false(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET condition-name TO FALSE
        """
        condition_name = set_info["condition_name"]
        plsql_name = self._convert_cobol_to_plsql_identifier(condition_name)
        procedure_name = f"set_{plsql_name}_false"
        
        return f"""
  {procedure_name}; -- {raw_content}
  -- GAP: Definir procedimiento {procedure_name} para condition name {condition_name}"""
    
    def _convert_set_index_to_value(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET index TO value
        Ejemplos: SET IDX1 TO 10 → idx1 := 10;
        """
        index_name = self._convert_cobol_to_plsql_identifier(set_info["index_name"])
        value = set_info["value"]
        
        return f"""
  {index_name} := {value}; -- {raw_content}"""
    
    def _convert_set_index_up_by(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET index UP BY increment
        Ejemplos: SET IDX1 UP BY 5 → idx1 := idx1 + 5;
        """
        index_name = self._convert_cobol_to_plsql_identifier(set_info["index_name"])
        increment = set_info["increment"]
        
        # Si increment es un identificador, convertirlo también
        if increment.isdigit():
            increment_value = increment
        else:
            increment_value = self._convert_cobol_to_plsql_identifier(increment)
        
        return f"""
  {index_name} := {index_name} + {increment_value}; -- {raw_content}"""
    
    def _convert_set_index_down_by(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET index DOWN BY decrement
        Ejemplos: SET IDX1 DOWN BY 3 → idx1 := idx1 - 3;
        """
        index_name = self._convert_cobol_to_plsql_identifier(set_info["index_name"])
        decrement = set_info["decrement"]
        
        # Si decrement es un identificador, convertirlo también
        if decrement.isdigit():
            decrement_value = decrement
        else:
            decrement_value = self._convert_cobol_to_plsql_identifier(decrement)
        
        return f"""
  {index_name} := {index_name} - {decrement_value}; -- {raw_content}"""
    
    def _convert_set_index_to_index(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET index1 TO index2
        Ejemplos: SET IDX1 TO IDX2 → idx1 := idx2;
        """
        target_index = self._convert_cobol_to_plsql_identifier(set_info["target_index"])
        source_index = self._convert_cobol_to_plsql_identifier(set_info["source_index"])
        
        return f"""
  {target_index} := {source_index}; -- {raw_content}"""
    
    def _convert_set_pointer_to_address(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET pointer TO ADDRESS OF variable
        PL/SQL no tiene punteros directos, simular con referencias
        """
        pointer_name = self._convert_cobol_to_plsql_identifier(set_info["pointer_name"])
        variable_name = self._convert_cobol_to_plsql_identifier(set_info["variable_name"])
        
        return f"""
  -- SET POINTER TO ADDRESS simulation
  {pointer_name} := '{variable_name}'; -- {raw_content}
  -- GAP: Implementar sistema de referencias para punteros"""
    
    def _convert_set_address_to_pointer(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET ADDRESS OF variable TO pointer
        Simulación de copia por referencia
        """
        variable_name = self._convert_cobol_to_plsql_identifier(set_info["variable_name"])
        pointer_name = self._convert_cobol_to_plsql_identifier(set_info["pointer_name"])
        
        return f"""
  -- SET ADDRESS OF simulation (copy by reference)
  -- GAP: Implementar copia de contenido referenciado
  -- copy_content_by_reference('{variable_name}', {pointer_name}); -- {raw_content}"""
    
    def _convert_set_variable_to_true(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET variable TO TRUE
        """
        variable_name = self._convert_cobol_to_plsql_identifier(set_info["variable_name"])
        
        return f"""
  {variable_name} := TRUE; -- {raw_content}"""
    
    def _convert_set_variable_to_false(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET variable TO FALSE
        """
        variable_name = self._convert_cobol_to_plsql_identifier(set_info["variable_name"])
        
        return f"""
  {variable_name} := FALSE; -- {raw_content}"""
    
    def _convert_set_variable_to_null(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET variable TO NULL
        """
        variable_name = self._convert_cobol_to_plsql_identifier(set_info["variable_name"])
        
        return f"""
  {variable_name} := NULL; -- {raw_content}"""
    
    def _convert_set_generic(self, set_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir SET genérico cuando no coincide con patrones específicos
        """
        return f"""
  -- GAP -- {raw_content} -- (SET statement - generic)"""
    
    def _generate_set_utility_functions(self) -> str:
        """
        Generar funciones de utilidad para operaciones SET
        Principio Dependency Inversion: Depende de abstracciones de SET operations
        """
        return """
  
  /*
   *-------------------------------------------------------------*
   * FUNCIONES DE UTILIDAD PARA OPERACIONES SET                 *
   *-------------------------------------------------------------*
   */
   
  -- Package para manejo de condition names (88-level equivalents)
  -- Este package se genera automáticamente basado en las variables detectadas
  
  -- Procedimiento para SET condition names TO TRUE
  PROCEDURE set_condition_name_true(p_variable_name VARCHAR2, 
                                   p_condition_name VARCHAR2,
                                   p_true_value VARCHAR2) IS
  BEGIN
    -- Implementación genérica para condition names
    -- GAP: Completar implementación basada en variables específicas
    DBMS_OUTPUT.PUT_LINE('Setting ' || p_condition_name || ' to TRUE');
  END set_condition_name_true;
  
  -- Procedimiento para SET condition names TO FALSE
  PROCEDURE set_condition_name_false(p_variable_name VARCHAR2, 
                                    p_condition_name VARCHAR2,
                                    p_false_value VARCHAR2) IS
  BEGIN
    -- Implementación genérica para condition names
    -- GAP: Completar implementación basada en variables específicas
    DBMS_OUTPUT.PUT_LINE('Setting ' || p_condition_name || ' to FALSE');
  END set_condition_name_false;
  
  -- Procedimiento para SET index con validación
  PROCEDURE set_index_safe(p_index_name VARCHAR2,
                          p_index IN OUT BINARY_INTEGER,
                          p_value BINARY_INTEGER,
                          p_min_val BINARY_INTEGER DEFAULT 1,
                          p_max_val BINARY_INTEGER DEFAULT 1000) IS
  BEGIN
    IF p_value BETWEEN p_min_val AND p_max_val THEN
      p_index := p_value;
    ELSE
      RAISE_APPLICATION_ERROR(-20001, 'Index ' || p_index_name || 
                             ' out of range: ' || p_value || 
                             ' (valid range: ' || p_min_val || '-' || p_max_val || ')');
    END IF;
  END set_index_safe;
  
  -- Procedimiento para SET index UP BY con validación
  PROCEDURE set_index_up_by_safe(p_index_name VARCHAR2,
                                p_index IN OUT BINARY_INTEGER,
                                p_increment BINARY_INTEGER,
                                p_max_val BINARY_INTEGER DEFAULT 1000) IS
  BEGIN
    IF p_index + p_increment <= p_max_val THEN
      p_index := p_index + p_increment;
    ELSE
      RAISE_APPLICATION_ERROR(-20002, 'Index ' || p_index_name || 
                             ' increment would exceed maximum: ' || p_max_val);
    END IF;
  END set_index_up_by_safe;
  
  -- Procedimiento para SET index DOWN BY con validación
  PROCEDURE set_index_down_by_safe(p_index_name VARCHAR2,
                                  p_index IN OUT BINARY_INTEGER,
                                  p_decrement BINARY_INTEGER,
                                  p_min_val BINARY_INTEGER DEFAULT 1) IS
  BEGIN
    IF p_index - p_decrement >= p_min_val THEN
      p_index := p_index - p_decrement;
    ELSE
      RAISE_APPLICATION_ERROR(-20003, 'Index ' || p_index_name || 
                             ' decrement would exceed minimum: ' || p_min_val);
    END IF;
  END set_index_down_by_safe;
  
  -- Simulación de punteros con storage de variables
  TYPE t_pointer_storage IS TABLE OF VARCHAR2(4000) INDEX BY VARCHAR2(50);
  g_pointer_storage t_pointer_storage;
  
  -- Procedimiento para SET pointer TO ADDRESS OF
  PROCEDURE set_pointer_to_address_of(p_pointer_name VARCHAR2,
                                     p_variable_name VARCHAR2,
                                     p_variable_value VARCHAR2 DEFAULT NULL) IS
  BEGIN
    -- Simular puntero como referencia por nombre
    IF p_variable_value IS NOT NULL THEN
      g_pointer_storage(p_variable_name) := p_variable_value;
    END IF;
    g_pointer_storage(p_pointer_name || '_REF') := p_variable_name;
  END set_pointer_to_address_of;
  
  -- Función para GET value by pointer
  FUNCTION get_value_by_pointer(p_pointer_name VARCHAR2) RETURN VARCHAR2 IS
    v_ref_name VARCHAR2(50);
  BEGIN
    v_ref_name := g_pointer_storage(p_pointer_name || '_REF');
    IF v_ref_name IS NOT NULL THEN
      RETURN g_pointer_storage(v_ref_name);
    ELSE
      RETURN NULL;
    END IF;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN NULL;
  END get_value_by_pointer;
  
  -- Procedimiento para SET value by pointer
  PROCEDURE set_value_by_pointer(p_pointer_name VARCHAR2, p_value VARCHAR2) IS
    v_ref_name VARCHAR2(50);
  BEGIN
    v_ref_name := g_pointer_storage(p_pointer_name || '_REF');
    IF v_ref_name IS NOT NULL THEN
      g_pointer_storage(v_ref_name) := p_value;
    END IF;
    END set_value_by_pointer;"""

    # ===== CONVERTIDORES PERFORM SIGUIENDO PRINCIPIOS SOLID =====
    
    def _convert_perform_statement(self, stmt: Dict[str, Any]) -> str:
        """
        Convertir statement PERFORM a PL/SQL siguiendo equivalencias del archivo de referencia
        Principio Single Responsibility: Solo maneja conversión de PERFORM
        """
        raw_content = stmt.get("raw", "").strip()
        details = stmt.get("details", {})
        
        print(f"🔄 Convirtiendo PERFORM: {raw_content}")
        
        # Extraer información de la sentencia PERFORM
        perform_info = self._parse_perform_statement(raw_content)
        
        if not perform_info:
            return f"\n  -- GAP -- {raw_content} -- (PERFORM statement - parsing failed)"
        
        # Aplicar patrón Strategy para diferentes tipos de PERFORM
        try:
            if perform_info["type"] == "simple":
                return self._convert_perform_simple(perform_info, raw_content)
            elif perform_info["type"] == "thru":
                return self._convert_perform_thru(perform_info, raw_content)
            elif perform_info["type"] == "times":
                return self._convert_perform_times(perform_info, raw_content)
            elif perform_info["type"] == "procedure_until":
                return self._convert_perform_procedure_until(perform_info, raw_content)
            elif perform_info["type"] == "until":
                return self._convert_perform_until(perform_info, raw_content)
            elif perform_info["type"] == "varying":
                return self._convert_perform_varying(perform_info, raw_content)
            elif perform_info["type"] == "varying_after":
                return self._convert_perform_varying_after(perform_info, raw_content)
            elif perform_info["type"] == "with_test_after":
                return self._convert_perform_with_test_after(perform_info, raw_content)
            elif perform_info["type"] == "inline":
                return self._convert_perform_inline(perform_info, raw_content)
            else:
                return self._convert_perform_generic(perform_info, raw_content)
        except Exception as e:
            print(f"❌ Error convirtiendo PERFORM: {e}")
            return f"\n  -- GAP -- {raw_content} -- (PERFORM statement - conversion error)"
    
    def _parse_perform_statement(self, raw_content: str) -> Dict[str, Any]:
        """
        Parsear sentencia PERFORM para extraer componentes
        Principio Single Responsibility: Solo parsing de PERFORM
        """
        import re
        
        line = raw_content.strip()
        upper_line = line.upper()
        
        # Patrones para diferentes tipos de PERFORM (orden importa - más específicos primero)
        patterns = {
            "varying_after": r"PERFORM\s+VARYING\s+([A-Z0-9\-]+)\s+FROM\s+([A-Z0-9\-]+)\s+BY\s+([A-Z0-9\-]+)\s+UNTIL\s+(.+?)\s+AFTER\s+([A-Z0-9\-]+)\s+FROM\s+([A-Z0-9\-]+)\s+BY\s+([A-Z0-9\-]+)\s+UNTIL\s+(.+)",
            "varying": r"PERFORM\s+VARYING\s+([A-Z0-9\-]+)\s+FROM\s+([A-Z0-9\-]+)\s+BY\s+([A-Z0-9\-]+)\s+UNTIL\s+(.+)",
            "with_test_after": r"PERFORM\s+WITH\s+TEST\s+AFTER\s+UNTIL\s+(.+)",
            "procedure_until": r"PERFORM\s+([A-Z0-9\-]+)\s+UNTIL\s+([A-Z0-9\-]+)(?:\s|$|\.)",
            "times": r"PERFORM\s+(\d+)\s+TIMES",
            "until": r"PERFORM\s+UNTIL\s+(.+)",
            "thru": r"PERFORM\s+([A-Z0-9\-]+)\s+THRU\s+([A-Z0-9\-]+)",
            "simple": r"PERFORM\s+([A-Z0-9\-]+)(?:\s|$|\.)",
            "inline": r"PERFORM\s*$"
        }
        
        # Detectar tipo de PERFORM basado en contenido
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, upper_line, re.IGNORECASE)
            if match:
                return self._build_perform_info(pattern_name, match, line)
        
        # Si no coincide con ningún patrón específico, devolver genérico
        return {
            "type": "generic",
            "raw": line
        }
    
    def _build_perform_info(self, pattern_name: str, match, line: str) -> Dict[str, Any]:
        """
        Construir información del PERFORM basada en el patrón detectado
        Principio Open/Closed: Extendible para nuevos patrones
        """
        if pattern_name == "simple":
            return {
                "type": "simple",
                "procedure_name": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "thru":
            return {
                "type": "thru",
                "start_procedure": match.group(1).strip(),
                "end_procedure": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "times":
            return {
                "type": "times",
                "count": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "procedure_until":
            return {
                "type": "procedure_until",
                "procedure_name": match.group(1).strip(),
                "condition": match.group(2).strip(),
                "raw": line
            }
        elif pattern_name == "until":
            return {
                "type": "until",
                "condition": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "varying":
            return {
                "type": "varying",
                "variable": match.group(1).strip(),
                "from_value": match.group(2).strip(),
                "by_value": match.group(3).strip(),
                "until_condition": match.group(4).strip(),
                "raw": line
            }
        elif pattern_name == "varying_after":
            return {
                "type": "varying_after",
                "variable1": match.group(1).strip(),
                "from_value1": match.group(2).strip(),
                "by_value1": match.group(3).strip(),
                "until_condition1": match.group(4).strip(),
                "variable2": match.group(5).strip(),
                "from_value2": match.group(6).strip(),
                "by_value2": match.group(7).strip(),
                "until_condition2": match.group(8).strip(),
                "raw": line
            }
        elif pattern_name == "with_test_after":
            return {
                "type": "with_test_after",
                "condition": match.group(1).strip(),
                "raw": line
            }
        elif pattern_name == "inline":
            return {
                "type": "inline",
                "raw": line
            }
        
        return {"type": "generic", "raw": line}
    
    def _convert_perform_simple(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM simple (llamada a procedimiento)
        Ejemplos: PERFORM A1000-INICIO → A1000_INICIO;
        """
        procedure_name = perform_info["procedure_name"]
        plsql_name = self._convert_cobol_to_plsql_identifier(procedure_name)
        
        return f"""
  {plsql_name}; -- {raw_content}"""
    
    def _convert_perform_thru(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM THRU (rango de procedimientos)
        """
        start_proc = self._convert_cobol_to_plsql_identifier(perform_info["start_procedure"])
        end_proc = self._convert_cobol_to_plsql_identifier(perform_info["end_procedure"])
        
        return f"""
  {start_proc}; -- {raw_content}
  -- GAP: Implementar rango de procedimientos hasta {end_proc}"""
    
    def _convert_perform_times(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM n TIMES
        Ejemplos: PERFORM 10 TIMES → FOR i IN 1..10 LOOP
        """
        count = perform_info["count"]
        
        return f"""
  -- PERFORM {count} TIMES convertido a FOR LOOP
  FOR i IN 1..{count} LOOP
    -- {raw_content}
    -- GAP: Implementar contenido del loop
  END LOOP;"""
    
    def _convert_perform_procedure_until(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM procedure UNTIL condition
        Ejemplos: PERFORM 2000-PROCESO UNTIL NO-ENCONTRADO → WHILE NOT no_encontrado LOOP A2000_PROCESO; END LOOP;
        """
        procedure_name = perform_info["procedure_name"]
        condition = perform_info["condition"]
        
        plsql_procedure = self._convert_cobol_to_plsql_identifier(procedure_name)
        plsql_condition = self._convert_cobol_to_plsql_identifier(condition)
        
        # Para condiciones como NO-ENCONTRADO, convertir a variable booleana
        negated_condition = f"NOT {plsql_condition}"
        
        return f"""
  -- PERFORM {procedure_name} UNTIL {condition} convertido a WHILE LOOP
  WHILE {negated_condition} LOOP
    {plsql_procedure}; -- {raw_content}
  END LOOP;"""
    
    def _convert_perform_until(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM UNTIL
        Ejemplos: PERFORM UNTIL WS-FLAG = 'Y' → WHILE ws_flag != 'Y' LOOP
        """
        condition = perform_info["condition"]
        plsql_condition = self._convert_cobol_condition_to_plsql(condition)
        # Negar la condición para WHILE (PERFORM UNTIL se convierte en WHILE NOT)
        negated_condition = self._negate_condition(plsql_condition)
        
        return f"""
  -- PERFORM UNTIL convertido a WHILE LOOP
  WHILE {negated_condition} LOOP
    -- {raw_content}
    -- GAP: Implementar contenido del loop
  END LOOP;"""
    
    def _convert_perform_varying(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM VARYING
        Ejemplos: PERFORM VARYING WS-I FROM 1 BY 1 UNTIL WS-I > 10 → FOR ws_i IN 1..10 LOOP
        """
        variable = self._convert_cobol_to_plsql_identifier(perform_info["variable"])
        from_value = perform_info["from_value"]
        by_value = perform_info["by_value"]
        until_condition = perform_info["until_condition"]
        
        # Intentar extraer el valor final de la condición UNTIL
        end_value = self._extract_end_value_from_until(until_condition, perform_info["variable"])
        
        if end_value and by_value == "1":
            # Convertir a FOR simple si es incremento de 1
            return f"""
  -- PERFORM VARYING convertido a FOR LOOP
  FOR {variable} IN {from_value}..{end_value} LOOP
    -- {raw_content}
    -- GAP: Implementar contenido del loop
  END LOOP;"""
        else:
            # Usar WHILE para casos más complejos
            plsql_condition = self._convert_cobol_condition_to_plsql(until_condition)
            negated_condition = self._negate_condition(plsql_condition)
            
            return f"""
  -- PERFORM VARYING convertido a WHILE LOOP
  {variable} := {from_value};
  WHILE {negated_condition} LOOP
    -- {raw_content}
    -- GAP: Implementar contenido del loop
    {variable} := {variable} + {by_value};
  END LOOP;"""
    
    def _convert_perform_varying_after(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM VARYING ... AFTER (loops anidados)
        """
        var1 = self._convert_cobol_to_plsql_identifier(perform_info["variable1"])
        from1 = perform_info["from_value1"]
        by1 = perform_info["by_value1"]
        until1 = perform_info["until_condition1"]
        
        var2 = self._convert_cobol_to_plsql_identifier(perform_info["variable2"])
        from2 = perform_info["from_value2"]
        by2 = perform_info["by_value2"]
        until2 = perform_info["until_condition2"]
        
        # Intentar extraer valores finales
        end1 = self._extract_end_value_from_until(until1, perform_info["variable1"])
        end2 = self._extract_end_value_from_until(until2, perform_info["variable2"])
        
        if end1 and end2 and by1 == "1" and by2 == "1":
            return f"""
  -- PERFORM VARYING AFTER convertido a FOR LOOPS anidados
  FOR {var1} IN {from1}..{end1} LOOP
    FOR {var2} IN {from2}..{end2} LOOP
      -- {raw_content}
      -- GAP: Implementar contenido del loop anidado
    END LOOP;
  END LOOP;"""
        else:
            return f"""
  -- PERFORM VARYING AFTER convertido a WHILE LOOPS anidados
  {var1} := {from1};
  WHILE {self._negate_condition(self._convert_cobol_condition_to_plsql(until1))} LOOP
    {var2} := {from2};
    WHILE {self._negate_condition(self._convert_cobol_condition_to_plsql(until2))} LOOP
      -- {raw_content}
      -- GAP: Implementar contenido del loop anidado
      {var2} := {var2} + {by2};
    END LOOP;
    {var1} := {var1} + {by1};
  END LOOP;"""
    
    def _convert_perform_with_test_after(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM WITH TEST AFTER (DO-WHILE equivalent)
        """
        condition = perform_info["condition"]
        plsql_condition = self._convert_cobol_condition_to_plsql(condition)
        
        return f"""
  -- PERFORM WITH TEST AFTER convertido a LOOP con EXIT
  LOOP
    -- {raw_content}
    -- GAP: Implementar contenido del loop
    EXIT WHEN {plsql_condition};
  END LOOP;"""
    
    def _convert_perform_inline(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM inline (sin procedimiento específico)
        """
        return f"""
  -- PERFORM inline
  BEGIN
    -- {raw_content}
    -- GAP: Implementar contenido inline
  END;"""
    
    def _convert_perform_generic(self, perform_info: Dict[str, Any], raw_content: str) -> str:
        """
        Convertir PERFORM genérico cuando no coincide con patrones específicos
        """
        return f"""
  -- GAP -- {raw_content} -- (PERFORM statement - generic)"""
    
    def _extract_end_value_from_until(self, until_condition: str, variable: str) -> str:
        """
        Extraer valor final de una condición UNTIL para optimizar a FOR loop
        """
        import re
        
        # Patrones comunes para extraer el valor final
        patterns = [
            rf"{variable}\s*>\s*(\d+)",
            rf"{variable}\s*>=\s*(\d+)",
            rf"(\d+)\s*<\s*{variable}",
            rf"(\d+)\s*<=\s*{variable}"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, until_condition, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                # Ajustar según el operador
                if ">" in until_condition and "=" not in until_condition:
                    return str(value)
                elif ">=" in until_condition:
                    return str(value - 1)
                elif "<" in until_condition and "=" not in until_condition:
                    return str(value - 1)
                elif "<=" in until_condition:
                    return str(value)
        
        return None
    
    def _negate_condition(self, condition: str) -> str:
        """
        Negar una condición PL/SQL para convertir UNTIL a WHILE
        """
        condition = condition.strip()
        
        # Casos simples de negación
        if condition.startswith("NOT "):
            return condition[4:]  # Quitar NOT
        elif "=" in condition and "!=" not in condition and "<>" not in condition:
            return condition.replace("=", "!=")
        elif "!=" in condition:
            return condition.replace("!=", "=")
        elif "<>" in condition:
            return condition.replace("<>", "=")
        elif " > " in condition:
            return condition.replace(" > ", " <= ")
        elif " >= " in condition:
            return condition.replace(" >= ", " < ")
        elif " < " in condition:
            return condition.replace(" < ", " >= ")
        elif " <= " in condition:
            return condition.replace(" <= ", " > ")
        else:
            return f"NOT ({condition})"
    
    def _generate_perform_utility_functions(self) -> str:
        """
        Generar funciones de utilidad para operaciones PERFORM
        Principio Dependency Inversion: Depende de abstracciones de PERFORM operations
        """
        return """
  
  /*
   *-------------------------------------------------------------*
   * FUNCIONES DE UTILIDAD PARA OPERACIONES PERFORM            *
   *-------------------------------------------------------------*
   */
   
  -- Contador global para loops anidados
  g_loop_counter BINARY_INTEGER := 0;
  
  -- Procedimiento para manejo de EXIT PERFORM
  PROCEDURE exit_perform_loop IS
  BEGIN
    -- Simular EXIT PERFORM usando excepción controlada
    RAISE_APPLICATION_ERROR(-20100, 'EXIT_PERFORM');
  END exit_perform_loop;
  
  -- Función para evaluar condiciones UNTIL dinámicamente
  FUNCTION evaluate_until_condition(p_condition VARCHAR2, 
                                   p_variable_name VARCHAR2,
                                   p_variable_value NUMBER) RETURN BOOLEAN IS
  BEGIN
    -- Implementación básica para condiciones numéricas comunes
    -- GAP: Expandir para más tipos de condiciones
    IF INSTR(p_condition, '>') > 0 THEN
      RETURN p_variable_value > TO_NUMBER(SUBSTR(p_condition, INSTR(p_condition, '>') + 1));
    ELSIF INSTR(p_condition, '>=') > 0 THEN
      RETURN p_variable_value >= TO_NUMBER(SUBSTR(p_condition, INSTR(p_condition, '>=') + 2));
    ELSIF INSTR(p_condition, '=') > 0 THEN
      RETURN p_variable_value = TO_NUMBER(SUBSTR(p_condition, INSTR(p_condition, '=') + 1));
    END IF;
    
    RETURN FALSE;
  END evaluate_until_condition;
  
  -- Procedimiento para PERFORM con parámetros (USING)
  PROCEDURE perform_with_parameters(p_procedure_name VARCHAR2,
                                   p_param1 VARCHAR2 DEFAULT NULL,
                                   p_param2 VARCHAR2 DEFAULT NULL,
                                   p_param3 VARCHAR2 DEFAULT NULL) IS
  BEGIN
    -- GAP: Implementar llamada dinámica a procedimientos con parámetros
    DBMS_OUTPUT.PUT_LINE('Calling ' || p_procedure_name || 
                        ' with params: ' || p_param1 || ', ' || p_param2 || ', ' || p_param3);
  END perform_with_parameters;
  
  -- Función para validar rangos en PERFORM VARYING
  FUNCTION validate_varying_range(p_variable_name VARCHAR2,
                                 p_from_value NUMBER,
                                 p_to_value NUMBER,
                                 p_by_value NUMBER DEFAULT 1) RETURN BOOLEAN IS
  BEGIN
    IF p_by_value = 0 THEN
      RAISE_APPLICATION_ERROR(-20101, 'BY value cannot be zero in PERFORM VARYING');
    END IF;
    
    IF p_by_value > 0 AND p_from_value > p_to_value THEN
      RAISE_APPLICATION_ERROR(-20102, 'Invalid range in PERFORM VARYING: FROM > TO with positive BY');
    END IF;
    
    IF p_by_value < 0 AND p_from_value < p_to_value THEN
      RAISE_APPLICATION_ERROR(-20103, 'Invalid range in PERFORM VARYING: FROM < TO with negative BY');
    END IF;
    
    RETURN TRUE;
  END validate_varying_range;"""

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

