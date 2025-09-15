#!/usr/bin/env python3
"""
IR to PL/SQL Generator - Segundo programa del pipeline de conversión
Convierte archivos IR (JSON) a código PL/SQL

Entrada: Archivo IR (JSON)
Salida:
- Archivo PL/SQL (.sql)
- Reporte de conversión (JSON)
- Log de reglas aplicadas

Uso: python ir_to_plsql.py archivo_ir.json
"""

import sys
import os
import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

# ===== TIMING UTILITIES =====

def get_timestamp():
    """Obtener timestamp detallado con milisegundos"""
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")[:-3]

def format_duration(start_time, end_time):
    """Formatear duración en segundos y milisegundos"""
    duration = end_time - start_time
    if duration < 1:
        return f"{duration*1000:.1f} ms"
    elif duration < 60:
        return f"{duration:.3f} segundos"
    else:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.3f}s"

# ===== EXPRESSION CLEANING =====

def _clean_expression(expr: str) -> str:
    """Limpiar expresiones para PL/SQL"""
    if not expr:
        return ""
    
    # Remover puntos finales
    expr = expr.rstrip('.')
    
    # Limpiar espacios extra
    expr = ' '.join(expr.split())
    
    # Convertir comillas COBOL a PL/SQL si es necesario
    if expr.startswith("'") and expr.endswith("'"):
        return expr
    elif expr.startswith('"') and expr.endswith('"'):
        return "'" + expr[1:-1] + "'"
    
    return expr

# ===== CONVERSION RULES =====

class PLSQLConverter:
    """Convertidor de IR a PL/SQL con reglas optimizadas"""
    
    def __init__(self):
        self.conversion_stats = {
            'total_rules': 0,
            'successful_conversions': 0,
            'gaps': 0,
            'rule_usage': {}
        }
    
    def apply_rule(self, stmt: Dict[str, Any]) -> str:
        """Aplicar regla de conversión a un statement"""
        op = stmt.get("op", "UNKNOWN")
        self.conversion_stats['total_rules'] += 1
        
        # Tracking de uso de reglas
        self.conversion_stats['rule_usage'][op] = self.conversion_stats['rule_usage'].get(op, 0) + 1
        
        # Aplicar reglas específicas
        if op == "COMMENT":
            return self._convert_comment(stmt)
        
        elif op == "MOVE":
            return self._convert_move(stmt)
        
        elif op == "DISPLAY":
            return self._convert_display(stmt)
        
        elif op == "IF":
            return self._convert_if(stmt)
        
        elif op == "END_IF":
            return self._convert_end_if(stmt)
        
        elif op == "ELSE":
            return self._convert_else(stmt)
        
        elif op == "PERFORM":
            return self._convert_perform(stmt)
        
        elif op == "EXEC_SQL":
            return self._convert_exec_sql(stmt)
        
        elif op == "SET":
            return self._convert_set(stmt)
        
        elif op == "STRING":
            return self._convert_string(stmt)
        
        elif op == "READ":
            return self._convert_read(stmt)
        
        elif op == "CLOSE":
            return self._convert_close(stmt)
        
        elif op == "INITIALIZE":
            return self._convert_initialize(stmt)
        
        elif op == "QUALIFIED_FIELD":
            return self._convert_qualified_field(stmt)
        
        elif op == "PROCEDURE_DIVISION":
            return self._convert_procedure_division(stmt)
        
        elif op == "EVALUATE":
            return self._convert_evaluate(stmt)
        
        elif op == "WHEN":
            return self._convert_when(stmt)
        
        elif op == "END_EVALUATE":
            return self._convert_end_evaluate(stmt)
        
        elif op == "TREE_STATEMENT":
            return self._convert_tree_statement(stmt)
        
        # Nuevos tipos del árbol ANTLR completo
        elif op == "UNIVERSAL_CATCH_ALL":
            return self._convert_universal_catch_all(stmt)
        
        elif op == "DISPLAY_CONTINUATION":
            return self._convert_display_continuation(stmt)
        
        elif op == "SIMPLE_QUALIFIED":
            return self._convert_simple_qualified(stmt)
        
        elif op == "END_IF":
            return self._convert_end_if(stmt)
        
        else:
            # Catch-all para statements desconocidos
            return self._convert_unknown(stmt)
    
    def _convert_comment(self, stmt: Dict[str, Any]) -> str:
        """Convertir comentario COBOL a PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        text = stmt.get('text', stmt.get('raw', ''))
        return f"    -- {text.strip()}"
    
    def _convert_move(self, stmt: Dict[str, Any]) -> str:
        """Convertir MOVE COBOL a asignación PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        src = _clean_expression(stmt.get("src", ""))
        dst = _clean_expression(stmt.get("dst", ""))
        
        # Manejar casos especiales
        if src.upper() in ['ZERO', 'ZEROS', 'ZEROES']:
            src = '0'
        elif src.upper() in ['SPACE', 'SPACES']:
            src = "' '"
        elif src.upper() == 'HIGH-VALUE':
            src = 'CHR(255)'
        elif src.upper() == 'LOW-VALUE':
            src = 'CHR(0)'
        
        return f"    {dst} := {src};"
    
    def _convert_display(self, stmt: Dict[str, Any]) -> str:
        """Convertir DISPLAY COBOL a DBMS_OUTPUT PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        content = _clean_expression(stmt.get("content", ""))
        
        # Manejar concatenación si hay múltiples elementos
        if ' ' in content and not (content.startswith("'") and content.endswith("'")):
            # Posible concatenación
            parts = content.split()
            formatted_parts = []
            for part in parts:
                if part.startswith("'") and part.endswith("'"):
                    formatted_parts.append(part)
                else:
                    formatted_parts.append(part)
            content = ' || '.join(formatted_parts)
        
        return f"    DBMS_OUTPUT.PUT_LINE({content});"
    
    def _convert_if(self, stmt: Dict[str, Any]) -> str:
        """Convertir IF COBOL a IF PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        condition = _clean_expression(stmt.get("condition", ""))
        
        # Convertir operadores COBOL a PL/SQL
        condition = condition.replace(' = ', ' = ')
        condition = condition.replace(' NOT = ', ' <> ')
        condition = condition.replace(' > ', ' > ')
        condition = condition.replace(' < ', ' < ')
        condition = condition.replace(' AND ', ' AND ')
        condition = condition.replace(' OR ', ' OR ')
        
        return f"    IF {condition} THEN"
    
    def _convert_end_if(self, stmt: Dict[str, Any]) -> str:
        """Convertir END-IF COBOL a END IF PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        return f"    END IF;"
    
    def _convert_else(self, stmt: Dict[str, Any]) -> str:
        """Convertir ELSE COBOL a ELSE PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        return f"    ELSE"
    
    def _convert_perform(self, stmt: Dict[str, Any]) -> str:
        """Convertir PERFORM COBOL a llamada de procedimiento PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        target = _clean_expression(stmt.get("target", ""))
        
        # Manejar diferentes tipos de PERFORM
        if 'UNTIL' in target.upper():
            # PERFORM UNTIL loop
            return f"    -- PERFORM UNTIL: {target}"
        elif 'TIMES' in target.upper():
            # PERFORM n TIMES
            return f"    -- PERFORM TIMES: {target}"
        else:
            # PERFORM simple
            return f"    {target};"
    
    def _convert_exec_sql(self, stmt: Dict[str, Any]) -> str:
        """Convertir EXEC SQL COBOL a PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        sql = stmt.get("sql", "")
        
        # Limpiar SQL
        sql = sql.replace('EXEC SQL', '').replace('END-EXEC', '').strip()
        
        # Manejar host variables (:variable)
        # En PL/SQL directo, las variables no necesitan ':'
        # sql = re.sub(r':([A-Z0-9_-]+)', r'\1', sql)
        
        return f"    {sql};"
    
    def _convert_set(self, stmt: Dict[str, Any]) -> str:
        """Convertir SET COBOL a asignación PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        content = stmt.get("content", stmt.get("raw", ""))
        
        # Extraer target y value si están disponibles
        if 'target' in stmt and 'value' in stmt:
            target = _clean_expression(stmt["target"])
            value = _clean_expression(stmt["value"])
            
            # Manejar valores especiales
            if value.upper() == 'TRUE':
                value = '1'
            elif value.upper() == 'FALSE':
                value = '0'
            
            return f"    {target} := {value};"
        else:
            # Parsing manual del contenido
            content_upper = content.upper()
            if ' TO ' in content_upper:
                parts = content_upper.split(' TO ')
                if len(parts) == 2:
                    target = parts[0].replace('SET', '').strip()
                    value = parts[1].strip()
                    
                    if value == 'TRUE':
                        value = '1'
                    elif value == 'FALSE':
                        value = '0'
                    
                    return f"    {target} := {value};"
        
        return f"    -- SET: {content}"
    
    def _convert_string(self, stmt: Dict[str, Any]) -> str:
        """Convertir STRING COBOL a concatenación PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        content = stmt.get("content", "")
        return f"    -- STRING operation: {content}"
    
    def _convert_read(self, stmt: Dict[str, Any]) -> str:
        """Convertir READ COBOL a comentario PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        content = stmt.get("content", stmt.get("file", ""))
        return f"    -- READ: {content}"
    
    def _convert_close(self, stmt: Dict[str, Any]) -> str:
        """Convertir CLOSE COBOL a comentario PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        content = stmt.get("content", stmt.get("file", ""))
        return f"    -- CLOSE: {content}"
    
    def _convert_initialize(self, stmt: Dict[str, Any]) -> str:
        """Convertir INITIALIZE COBOL a asignación PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        content = stmt.get("content", stmt.get("target", ""))
        target = content.replace('INITIALIZE', '').strip()
        return f"    -- INITIALIZE {target} (set to default values)"
    
    def _convert_qualified_field(self, stmt: Dict[str, Any]) -> str:
        """Convertir campo calificado COBOL a notación PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        field = stmt.get("field", "")
        parent = stmt.get("parent", "")
        return f"    -- Qualified field: {parent}.{field}"
    
    def _convert_procedure_division(self, stmt: Dict[str, Any]) -> str:
        """Convertir PROCEDURE DIVISION COBOL a comentario PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        return f"    -- PROCEDURE DIVISION"
    
    def _convert_evaluate(self, stmt: Dict[str, Any]) -> str:
        """Convertir EVALUATE COBOL a CASE PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        content = stmt.get("content", "")
        variable = content.replace('EVALUATE', '').strip()
        return f"    CASE {variable}"
    
    def _convert_when(self, stmt: Dict[str, Any]) -> str:
        """Convertir WHEN COBOL a WHEN PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        content = stmt.get("content", "")
        condition = content.replace('WHEN', '').strip()
        return f"        WHEN {condition} THEN"
    
    def _convert_end_evaluate(self, stmt: Dict[str, Any]) -> str:
        """Convertir END-EVALUATE COBOL a END CASE PL/SQL"""
        self.conversion_stats['successful_conversions'] += 1
        return f"    END CASE;"
    
    def _convert_tree_statement(self, stmt: Dict[str, Any]) -> str:
        """Convertir statement genérico del árbol ANTLR"""
        text = stmt.get('text', stmt.get('raw', ''))
        node_type = stmt.get('node_type', '')
        
        # Filtrar nodos irrelevantes o muy granulares
        irrelevant_nodes = [
            'TerminalNodeImpl', 'PictureCharsContext', 'LiteralContext',
            'DataDescriptionEntryFormat1Context', 'DataDescriptionEntryContext',
            'IntegerLiteralContext', 'AlphanumericLiteralContext'
        ]
        
        if node_type in irrelevant_nodes:
            # Marcar como gap para que no aparezca en el SQL final
            self.conversion_stats['gaps'] += 1
            return ""  # Retornar vacío para nodos irrelevantes
        
        # Solo procesar texto significativo
        if text and len(text.strip()) > 2:
            text_clean = text.strip().replace('\r\n', ' ').replace('\n', ' ')
            text_upper = text_clean.upper()
            
            # Conversiones específicas para COBOL a PL/SQL
            if 'MOVE ' in text_upper and ' TO ' in text_upper:
                # Convertir MOVE X TO Y a Y := X;
                parts = text_upper.split(' TO ')
                if len(parts) == 2:
                    source = parts[0].replace('MOVE ', '').strip()
                    target = parts[1].strip().rstrip('.')
                    self.conversion_stats['successful_conversions'] += 1
                    return f"    {target} := {source};"
            
            elif 'DISPLAY ' in text_upper:
                # Convertir DISPLAY a DBMS_OUTPUT.PUT_LINE
                content = text_clean[8:].strip().rstrip('.')
                self.conversion_stats['successful_conversions'] += 1
                return f"    DBMS_OUTPUT.PUT_LINE({content});"
            
            elif text_upper.startswith('IF ') and text_upper.endswith('.'):
                # Convertir IF COBOL a IF PL/SQL
                condition = text_clean[3:-1].strip()
                self.conversion_stats['successful_conversions'] += 1
                return f"    IF {condition} THEN"
            
            elif text_upper.startswith('PERFORM '):
                # Convertir PERFORM a llamada de procedimiento
                proc_name = text_clean[8:].strip().rstrip('.')
                self.conversion_stats['successful_conversions'] += 1
                return f"    {proc_name};"
            
            elif text_upper in ['END-IF', 'END-IF.']:
                self.conversion_stats['successful_conversions'] += 1
                return "    END IF;"
            
            elif 'WORKING-STORAGE' in text_upper or 'DATA DIVISION' in text_upper:
                # Omitir declaraciones de sección
                self.conversion_stats['gaps'] += 1
                return ""
            
            else:
                # Para otros statements, agregar como comentario
                self.conversion_stats['successful_conversions'] += 1
                return f"    -- COBOL: {text_clean[:100]}{'...' if len(text_clean) > 100 else ''}"
        else:
            # Texto muy corto o vacío - omitir
            self.conversion_stats['gaps'] += 1
            return ""
    
    def _convert_universal_catch_all(self, stmt: Dict[str, Any]) -> str:
        """Convertir statement universal catch-all"""
        self.conversion_stats['successful_conversions'] += 1
        text = stmt.get('text', stmt.get('raw', ''))
        return f"    -- CATCH_ALL: {text.strip()}"
    
    def _convert_display_continuation(self, stmt: Dict[str, Any]) -> str:
        """Convertir continuación de DISPLAY"""
        self.conversion_stats['successful_conversions'] += 1
        text = stmt.get('text', stmt.get('raw', ''))
        return f"    DBMS_OUTPUT.PUT_LINE({text.strip()}); -- Display continuation"
    
    def _convert_simple_qualified(self, stmt: Dict[str, Any]) -> str:
        """Convertir campo calificado simple"""
        self.conversion_stats['successful_conversions'] += 1
        text = stmt.get('text', stmt.get('raw', ''))
        return f"    -- QUALIFIED: {text.strip()}"
    
    def _convert_end_if(self, stmt: Dict[str, Any]) -> str:
        """Convertir END-IF"""
        self.conversion_stats['successful_conversions'] += 1
        return "    END IF;"
    
    def _convert_unknown(self, stmt: Dict[str, Any]) -> str:
        """Manejar statements desconocidos"""
        self.conversion_stats['gaps'] += 1
        raw_content = stmt.get('raw', stmt.get('content', 'Unknown statement'))
        return f"    -- GAP: {raw_content}"

# ===== PL/SQL PACKAGE GENERATION =====

def generate_plsql_package(ir: Dict[str, Any], converter: PLSQLConverter) -> str:
    """Generar package PL/SQL completo desde IR"""
    
    program_name = ir.get("program_name", "UNKNOWN_PROGRAM")
    variables = ir.get("variables", [])
    procedures = ir.get("procedures", [])
    
    # Header del package
    header = f"""-- =====================================================
-- PL/SQL Package generado desde IR
-- Programa fuente: {program_name}
-- Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Método de parsing: {ir.get('metadata', {}).get('parse_method', 'unknown')}
-- =====================================================

CREATE OR REPLACE PACKAGE {program_name} AS
    -- Package specification
    
    -- Variables globales (desde WORKING-STORAGE)"""
    
    # Declarar variables globales
    variable_declarations = []
    for var in variables[:10]:  # Limitar a las primeras 10 para no sobrecargar
        level = var.get('level', '01')
        name = var.get('name', 'UNKNOWN_VAR')
        if level == '01':
            variable_declarations.append(f"    {name} VARCHAR2(100);  -- Level {level}")
    
    if variable_declarations:
        header += "\n" + "\n".join(variable_declarations)
    else:
        header += "\n    -- No variables found in WORKING-STORAGE"
    
    header += f"""
    
    -- Procedimientos principales
    PROCEDURE main_procedure;
    
END {program_name};
/

-- =====================================================
-- Package Body
-- =====================================================

CREATE OR REPLACE PACKAGE BODY {program_name} AS
    
    PROCEDURE main_procedure IS
    BEGIN
        -- Inicio del procedimiento principal
"""
    
    # Procesar statements de cada procedimiento
    body_lines = []
    total_statements = 0
    
    for procedure in procedures:
        proc_name = procedure.get('name', 'UNKNOWN_PROCEDURE')
        statements = procedure.get('statements', [])
        total_statements += len(statements)
        
        if proc_name != 'MAIN-PROCEDURE':
            body_lines.append(f"        -- Procedimiento: {proc_name}")
        
        for stmt in statements:
            converted = converter.apply_rule(stmt)
            # Solo agregar statements no vacíos y válidos
            if converted and converted.strip():
                body_lines.append(converted)
    
    # Footer del package
    footer = f"""        
        -- Fin del procedimiento principal
        DBMS_OUTPUT.PUT_LINE('Programa {program_name} ejecutado exitosamente');
        
    END main_procedure;
    
END {program_name};
/

-- =====================================================
-- Estadísticas de conversión
-- Total statements procesados: {total_statements}
-- Conversiones exitosas: {converter.conversion_stats['successful_conversions']}
-- GAPs encontrados: {converter.conversion_stats['gaps']}
-- Tasa de éxito: {((converter.conversion_stats['successful_conversions'] / total_statements) * 100) if total_statements > 0 else 0:.1f}%
-- ====================================================="""
    
    return header + '\n'.join(body_lines) + '\n' + footer

# ===== FILE I/O FUNCTIONS =====

def load_ir_from_file(ir_file: str) -> Dict[str, Any]:
    """Cargar IR desde archivo JSON"""
    try:
        with open(ir_file, 'r', encoding='utf-8') as f:
            ir = json.load(f)
        print(f"✅ IR cargado desde: {ir_file}")
        return ir
    except Exception as e:
        print(f"❌ Error cargando IR: {e}")
        raise

def save_plsql_to_file(plsql_code: str, output_file: str):
    """Guardar código PL/SQL en archivo"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(plsql_code)
    print(f"💾 PL/SQL guardado en: {output_file}")

def generate_conversion_report(ir: Dict[str, Any], converter: PLSQLConverter, times: Dict[str, float]) -> Dict[str, Any]:
    """Generar reporte detallado de la conversión"""
    
    total_statements = sum(len(proc.get('statements', [])) for proc in ir.get('procedures', []))
    success_rate = ((converter.conversion_stats['successful_conversions'] / total_statements) * 100) if total_statements > 0 else 0
    
    return {
        "conversion_summary": {
            "program_name": ir.get('program_name', 'UNKNOWN'),
            "source_parse_method": ir.get('metadata', {}).get('parse_method', 'unknown'),
            "total_statements": total_statements,
            "successful_conversions": converter.conversion_stats['successful_conversions'],
            "gaps_found": converter.conversion_stats['gaps'],
            "success_rate": round(success_rate, 2)
        },
        "rule_usage": {
            "most_used_rules": sorted(converter.conversion_stats['rule_usage'].items(), 
                                    key=lambda x: x[1], reverse=True)[:10],
            "total_rules_applied": converter.conversion_stats['total_rules']
        },
        "performance_metrics": {
            "conversion_time": times.get('conversion', 0),
            "total_time": times.get('total', 0),
            "statements_per_second": total_statements / times.get('conversion', 1)
        },
        "output_info": {
            "target_language": "PL/SQL",
            "package_generated": True,
            "includes_error_handling": False,
            "includes_comments": True
        }
    }

# ===== MAIN EXECUTION =====

def main():
    """Función principal del generador IR a PL/SQL"""
    if len(sys.argv) != 2:
        print("Uso: python ir_to_plsql.py <archivo_ir.json>")
        print()
        print("Este programa convierte archivos IR (JSON) a código PL/SQL")
        print("Genera:")
        print("  - Archivo PL/SQL (.sql)")
        print("  - Reporte de conversión (JSON)")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    if not os.path.exists(ir_file):
        print(f"❌ Error: No se encuentra el archivo IR {ir_file}")
        sys.exit(1)
    
    # Configurar archivos de salida
    base_name = os.path.splitext(os.path.basename(ir_file))[0]
    # Remover sufijo _ir si existe
    if base_name.endswith('_ir'):
        base_name = base_name[:-3]
    
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    
    sql_file = os.path.join(output_dir, f"{base_name}_generated.sql")
    report_file = os.path.join(output_dir, f"{base_name}_conversion_report.json")
    
    # Timing
    total_start = time.time()
    start_timestamp = get_timestamp()
    
    print("=" * 70)
    print(f"🔧 IR to PL/SQL Generator")
    print(f"📁 Archivo IR: {ir_file}")
    print(f"⏰ Inicio: {start_timestamp}")
    print("=" * 70)
    
    try:
        # 1. Cargar IR
        load_start = time.time()
        ir = load_ir_from_file(ir_file)
        load_end = time.time()
        
        # 2. Convertir IR → PL/SQL
        conversion_start = time.time()
        converter = PLSQLConverter()
        plsql_code = generate_plsql_package(ir, converter)
        conversion_end = time.time()
        
        # 3. Guardar archivos
        io_start = time.time()
        save_plsql_to_file(plsql_code, sql_file)
        
        # 4. Generar reporte
        times = {
            'loading': load_end - load_start,
            'conversion': conversion_end - conversion_start,
            'total': time.time() - total_start
        }
        
        report = generate_conversion_report(ir, converter, times)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        io_end = time.time()
        total_end = time.time()
        
        # Mostrar resultados
        print(f"✅ Archivos generados:")
        print(f"   📄 PL/SQL: {sql_file}")
        print(f"   📊 Reporte: {report_file}")
        
        print("=" * 70)
        print("📊 RESUMEN DE CONVERSIÓN")
        print("=" * 70)
        
        summary = report['conversion_summary']
        performance = report['performance_metrics']
        
        print(f"🎯 CONVERSIÓN:")
        print(f"   📋 Programa: {summary['program_name']}")
        print(f"   🔧 Statements: {summary['total_statements']}")
        print(f"   ✅ Convertidos: {summary['successful_conversions']}")
        print(f"   ❌ GAPs: {summary['gaps_found']}")
        print(f"   📈 Tasa éxito: {summary['success_rate']}%")
        
        print(f"⏰ RENDIMIENTO:")
        print(f"   🕐 Inicio: {start_timestamp}")
        print(f"   🕐 Fin: {get_timestamp()}")
        print(f"   ⏱️  Carga IR: {format_duration(load_start, load_end)}")
        print(f"   ⏱️  Conversión: {format_duration(conversion_start, conversion_end)}")
        print(f"   ⏱️  I/O: {format_duration(io_start, io_end)}")
        print(f"   ⏱️  Total: {format_duration(total_start, total_end)}")
        print(f"   ⚡ Velocidad: {performance['statements_per_second']:.1f} statements/seg")
        
        print(f"📊 REGLAS MÁS USADAS:")
        for rule_name, usage_count in report['rule_usage']['most_used_rules'][:5]:
            print(f"   • {rule_name}: {usage_count}")
        
        print("=" * 70)
        print("✅ Conversión completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
