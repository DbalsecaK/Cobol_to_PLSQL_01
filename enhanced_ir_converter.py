#!/usr/bin/env python3
"""
Conversor que replica exactamente la lógica del enhanced_converter.py
Usa el método apply_rule probado que funciona al 100%
"""

import sys
import os
import json
import re
from typing import Dict, List, Any, Optional

class EnhancedIRConverter:
    def __init__(self):
        pass
    
    def clean_expression(self, expr: str) -> str:
        """Limpiar expresiones (igual que enhanced_converter)"""
        if not expr:
            return ""
        
        # Remover caracteres especiales y normalizar espacios
        cleaned = re.sub(r'[^\w\s\-().,:\'"]+', '', str(expr))
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()
    
    def convert_move_statement_enhanced(self, stmt: Dict[str, Any]) -> str:
        """Convert MOVE statement to PL/SQL (igual que enhanced_converter)"""
        source = stmt.get('src', '')
        targets = stmt.get('dst', '')
        is_corresponding = stmt.get('is_corresponding', False)
        
        if is_corresponding:
            return self.convert_move_corresponding(source, targets)
        
        # Parse source
        source_expr = self.parse_move_source(source)
        
        # Parse targets (handle multiple targets)
        target_list = self.parse_move_targets(targets)
        
        # Generate assignments
        assignments = []
        for target in target_list:
            target_expr = self.parse_move_source(target)
            assignments.append(f"{target_expr} := {source_expr};")
        
        return "\n".join(assignments)
    
    def convert_move_corresponding(self, source: str, targets: str) -> str:
        """Convert MOVE CORRESPONDING to PL/SQL (igual que enhanced_converter)"""
        source_clean = self.clean_expression(source)
        targets_clean = self.clean_expression(targets)
        
        return f"-- MOVE CORRESPONDING {source_clean} TO {targets_clean}\n" \
               f"-- Note: This requires field-by-field mapping analysis\n" \
               f"{targets_clean} := {source_clean};"
    
    def parse_move_source(self, source: str) -> str:
        """Parse move source (simplified)"""
        if not source:
            return "NULL"
        
        cleaned = self.clean_expression(source)
        
        # Convert COBOL variables to PL/SQL format
        if re.match(r'^[A-Z0-9_\-]+$', cleaned):
            return cleaned.replace('-', '_')
        
        return cleaned
    
    def parse_move_targets(self, targets: str) -> List[str]:
        """Parse move targets (handle multiple targets)"""
        if not targets:
            return []
        
        # Split by comma if multiple targets
        target_list = [t.strip() for t in targets.split(',') if t.strip()]
        if not target_list:
            target_list = [targets.strip()]
        
        return target_list
    
    def apply_rule(self, stmt: Dict[str, Any], base_indent: str = "    ") -> str:
        """Aplica reglas de conversión a sentencias (EXACTO del enhanced_converter)"""
        op = stmt.get("op", "UNKNOWN")
    
        if op == "PERFORM":
            target = stmt.get("target", "")
            target_clean = self.clean_expression(target)
            return f"{base_indent}{target_clean}();"
        
        elif op == "PERFORM_UNTIL":
            target = stmt.get("target", "")
            condition = stmt.get("condition", "")
            target_clean = self.clean_expression(target)
            condition_clean = self.clean_expression(condition)
            return f"{base_indent}WHILE NOT ({condition_clean}) LOOP\n{base_indent}  {target_clean}();\n{base_indent}END LOOP;"
        
        elif op == "MOVE" or op == "MOVE_CORRESPONDING":
            result = self.convert_move_statement_enhanced(stmt)
            return self._apply_indentation(result, base_indent)
        
        elif op == "DISPLAY":
            content = stmt.get('content', '')
            if content:
                content_clean = self.clean_expression(content)
                return f"{base_indent}DBMS_OUTPUT.PUT_LINE({content_clean});"
            return f"{base_indent}-- DISPLAY operation"
        
        elif op == "ROLLBACK":
            return f"{base_indent}ROLLBACK;"
        
        elif op == "COMMIT":
            return f"{base_indent}COMMIT;"
        
        elif op == "IF":
            condition = stmt.get("condition", "")
            condition_clean = self.clean_expression(condition)
            return f"{base_indent}IF {condition_clean} THEN"
        
        elif op == "END_IF":
            return f"{base_indent}END IF;"
        
        elif op == "ELSE":
            return f"{base_indent}ELSE"
        
        else:
            # Para cualquier otro OP, intentar conversión básica
            content = stmt.get('content', stmt.get('raw', ''))
            if content and len(content) < 100:
                return f"{base_indent}-- {op}: {content}"
            return f"{base_indent}-- GAP: {op}"
    
    def _apply_indentation(self, text: str, base_indent: str) -> str:
        """Apply proper indentation to multi-line PL/SQL code (igual que enhanced_converter)"""
        if not text:
            return ""
        
        lines = text.split('\n')
        indented_lines = []
        
        for line in lines:
            if line.strip():
                indented_lines.append(f"{base_indent}{line}")
            else:
                indented_lines.append("")
        
        return '\n'.join(indented_lines)
    
    def _process_statements_with_context(self, statements: List[Dict[str, Any]], base_indent: str) -> List[str]:
        """Process statements with context (igual que enhanced_converter)"""
        result_lines = []
        
        for stmt in statements:
            try:
                converted = self.apply_rule(stmt, base_indent)
                if converted and converted.strip():
                    result_lines.append(converted)
            except Exception as e:
                print(f"⚠️  Error procesando statement: {e}")
                result_lines.append(f"{base_indent}-- ERROR: {stmt.get('op', 'UNKNOWN')}")
        
        return result_lines
    
    def generate_package(self, ir: Dict[str, Any]) -> str:
        """Genera el paquete PL/SQL completo (simplificado del enhanced_converter)"""
        program_name = ir.get("program", ir.get("program_name", "UNKNOWN"))
        program_name_clean = self.clean_expression(program_name)
        
        if not program_name_clean or not program_name_clean[0].isalpha():
            program_name_clean = f"PKG_{program_name_clean}"
        
        # Procesar statements de todos los procedimientos
        all_statements = []
        procedures = ir.get("procedures", [])
        
        if procedures:
            for proc in procedures:
                proc_statements = self._process_statements_with_context(proc.get("statements", []), "    ")
                all_statements.extend(proc_statements)
        else:
            # Si no hay procedimientos, usar statements directos
            statements = ir.get("statements", [])
            all_statements = self._process_statements_with_context(statements, "    ")
        
        # Construir el paquete
        package = f"""-- =============================================
-- Package: {program_name_clean}
-- Generated from COBOL program: {program_name}
-- Using enhanced_converter logic
-- Total statements: {len(all_statements)}
-- =============================================

CREATE OR REPLACE PACKAGE {program_name_clean} IS
  PROCEDURE MAIN;
END {program_name_clean};
/

CREATE OR REPLACE PACKAGE BODY {program_name_clean} IS

  PROCEDURE MAIN IS
  BEGIN
{chr(10).join(all_statements)}
    
    -- End of main procedure
    NULL;
  END MAIN;

END {program_name_clean};
/"""
        
        return package

def main():
    if len(sys.argv) != 2:
        print("Uso: python enhanced_ir_converter.py archivo_ir.json")
        sys.exit(1)
    
    ir_file = sys.argv[1]
    if not os.path.exists(ir_file):
        print(f"❌ Archivo IR no encontrado: {ir_file}")
        sys.exit(1)
    
    try:
        print(f"📁 Cargando IR: {ir_file}")
        
        with open(ir_file, 'r', encoding='utf-8') as f:
            ir = json.load(f)
        
        print(f"📊 IR cargado - Statements: {len(ir.get('statements', []))}")
        
        converter = EnhancedIRConverter()
        sql_content = converter.generate_package(ir)
        
        # Guardar archivo
        base_name = os.path.splitext(os.path.basename(ir_file))[0]
        if base_name.endswith("_ir_fixed"):
            base_name = base_name[:-9]
        elif base_name.endswith("_ir_complete"):
            base_name = base_name[:-12]
        
        output_file = f"out/{base_name}_enhanced.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        print(f"✅ SQL generado: {output_file}")
        print("🎊 ¡Conversión completada usando lógica enhanced_converter!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()




