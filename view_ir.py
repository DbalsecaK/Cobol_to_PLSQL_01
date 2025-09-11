#!/usr/bin/env python3
"""
Script para visualizar la Representación Intermedia (IR) generada durante la conversión
"""
import sys
import os
import json
from typing import Any, Dict, List, Optional

# Imports de ANTLR
from antlr4 import FileStream, CommonTokenStream
from Cobol85Lexer import Cobol85Lexer
from Cobol85Parser import Cobol85Parser

# ===== IR VISITOR =====
class IRBuildingVisitor:
    def __init__(self, token_stream, full_text: str):
        self.ts = token_stream
        self.text = full_text
        self.program_name: str = "COBOL_PROGRAM"
        self.variables: List[Dict[str, Any]] = []
        self.statements: List[Dict[str, Any]] = []

    def build_ir(self, entry) -> Dict[str, Any]:
        self.program_name = self._find_program_id(entry) or self.program_name
        self.variables = self._extract_variables(entry)
        self.statements = self._extract_statements(entry)
        return {
            "program": self.program_name,
            "variables": self.variables,
            "procedures": [
                {"name": "MAIN", "statements": self.statements}
            ]
        }

    def _find_program_id(self, entry) -> Optional[str]:
        import re
        m = re.search(r'PROGRAM-ID\.\s*([A-Z0-9_-]+)\.', self.text, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        return None

    def _extract_section_text(self, start_marker: str, end_marker: Optional[str]=None) -> str:
        import re
        s = re.search(start_marker, self.text, flags=re.IGNORECASE)
        if not s:
            return ""
        if end_marker:
            e = re.search(end_marker, self.text, flags=re.IGNORECASE)
            if e and e.start() > s.end():
                return self.text[s.end():e.start()]
            return self.text[s.end():]
        return self.text[s.end():]

    def _extract_variables(self, entry) -> List[Dict[str, Any]]:
        import re
        ws_text = self._extract_section_text(r'WORKING-STORAGE SECTION', r'PROCEDURE DIVISION')
        vars_found: List[Dict[str, Any]] = []
        for name, pic in re.findall(r'^\s*01\s+([A-Z0-9_-]+)\s+PIC\s+([XS9]\(\d+\))', ws_text, flags=re.MULTILINE | re.IGNORECASE):
            name = name.upper()
            pic_u = pic.upper()
            size = int(re.findall(r'\((\d+)\)', pic_u)[0])
            vtype = 'STRING' if pic_u.startswith('X(') else 'NUMERIC'
            vars_found.append({"name": name, "type": vtype, "size": size})
        return vars_found

    def _extract_statements(self, entry) -> List[Dict[str, Any]]:
        import re
        proc_text = self._extract_section_text(r'PROCEDURE DIVISION', r'STOP RUN\.')
        if not proc_text:
            proc_text = self._extract_section_text(r'PROCEDURE DIVISION')
        lines = [ln.strip() for ln in proc_text.splitlines() if ln.strip()]
        stmts: List[Dict[str, Any]] = []

        i = 0
        while i < len(lines):
            ln = lines[i]
            
            # MOVE statement
            m = re.search(r'^MOVE\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.?', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": ln})
                i += 1
                continue

            # ADD with GIVING
            m = re.search(r'^ADD\s+([A-Z0-9_-]+)\s+TO\s+([A-Z0-9_-]+)\s+GIVING\s+([A-Z0-9_-]+)\.?', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"ADD_GIVING", "src1": m.group(1).upper(), "src2": m.group(2).upper(), "dst": m.group(3).upper(), "raw": ln})
                i += 1
                continue

            # ADD simple
            m = re.search(r'^ADD\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.?', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"ADD", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": ln})
                i += 1
                continue

            # IF-ELSE-END-IF block
            m = re.search(r'^IF\s+(.+?)(?:\s+THEN)?$', ln, re.IGNORECASE)
            if m:
                condition = m.group(1).strip()
                then_stmts = []
                else_stmts = []
                i += 1
                
                # Parse THEN block
                while i < len(lines) and not re.search(r'^ELSE', lines[i], re.IGNORECASE) and not re.search(r'^END-IF', lines[i], re.IGNORECASE):
                    then_ln = lines[i]
                    m = re.search(r'^MOVE\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.?', then_ln, re.IGNORECASE)
                    if m:
                        then_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": then_ln})
                    elif re.search(r'^DISPLAY\s+(.+?)\.?', then_ln, re.IGNORECASE):
                        m = re.search(r'^DISPLAY\s+(.+?)\.?', then_ln, re.IGNORECASE)
                        then_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": then_ln})
                    i += 1
                
                # Check for ELSE
                if i < len(lines) and re.search(r'^ELSE', lines[i], re.IGNORECASE):
                    i += 1
                    # Parse ELSE block
                    while i < len(lines) and not re.search(r'^END-IF', lines[i], re.IGNORECASE):
                        else_ln = lines[i]
                        m = re.search(r'^MOVE\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.?', else_ln, re.IGNORECASE)
                        if m:
                            else_stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": else_ln})
                        elif re.search(r'^DISPLAY\s+(.+?)\.?', else_ln, re.IGNORECASE):
                            m = re.search(r'^DISPLAY\s+(.+?)\.?', else_ln, re.IGNORECASE)
                            else_stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": else_ln})
                        i += 1
                
                # Skip END-IF
                if i < len(lines) and re.search(r'^END-IF', lines[i], re.IGNORECASE):
                    i += 1
                
                stmts.append({"op":"IF_ELSE", "cond": condition, "then": then_stmts, "else": else_stmts, "raw": f"IF {condition} ... END-IF"})
                continue

            # Simple IF statement (legacy)
            m = re.search(r'^IF\s+([^D]+?)\s+DISPLAY\s+(.+?)\.?', ln, re.IGNORECASE)
            if m:
                condition = m.group(1).strip()
                value = m.group(2).strip()
                stmts.append({"op":"IF", "cond": condition, "then":[{"op":"DISPLAY","value": value}], "raw": ln})
                i += 1
                continue

            # DISPLAY statement
            m = re.search(r'^DISPLAY\s+(.+?)\.?', ln, re.IGNORECASE)
            if m:
                value = m.group(1).strip()
                if re.match(r'^[A-Z0-9_-]+$', value, re.IGNORECASE):
                    stmts.append({"op":"DISPLAY_VAR", "variable": value.upper(), "raw": ln})
                else:
                    stmts.append({"op":"DISPLAY", "value": value, "raw": ln})
                i += 1
                continue

            # Skip simple dots or empty lines
            if ln.strip() in ['.', '']:
                i += 1
                continue
                
            stmts.append({"op":"UNKNOWN", "raw": ln})
            i += 1
        return stmts

def parse_cobol_to_ir(file_path: str):
    """Función para parsear COBOL a IR usando ANTLR"""
    print(f"🔍 Parseando archivo COBOL: {file_path}")
    
    input_stream = FileStream(file_path, encoding='utf-8')
    lexer = Cobol85Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Cobol85Parser(stream)
    
    # Parsear usando la gramática
    tree = parser.program()
    print("✅ Parsing ANTLR exitoso!")
    
    visitor = IRBuildingVisitor(token_stream=stream, full_text=input_stream.strdata)
    return visitor.build_ir(tree)

def display_ir(ir: Dict[str, Any]):
    """Función para mostrar la IR de forma legible"""
    print("\n" + "="*60)
    print("📊 REPRESENTACIÓN INTERMEDIA (IR)")
    print("="*60)
    
    print(f"\n🏷️  PROGRAMA: {ir['program']}")
    
    print(f"\n📋 VARIABLES ({len(ir['variables'])} encontradas):")
    for i, var in enumerate(ir['variables'], 1):
        print(f"   {i}. {var['name']} ({var['type']}, tamaño: {var['size']})")
    
    print(f"\n🔧 PROCEDIMIENTOS ({len(ir['procedures'])} encontrados):")
    for proc in ir['procedures']:
        print(f"\n   📝 {proc['name']}:")
        print(f"      Sentencias: {len(proc['statements'])}")
        
        for i, stmt in enumerate(proc['statements'], 1):
            op = stmt.get('op', 'UNKNOWN')
            raw = stmt.get('raw', '')
            
            if op == 'MOVE':
                src = stmt.get('src', '')
                dst = stmt.get('dst', '')
                print(f"      {i}. MOVE: {src} → {dst}")
                
            elif op == 'ADD':
                src = stmt.get('src', '')
                dst = stmt.get('dst', '')
                print(f"      {i}. ADD: {src} + {dst}")
                
            elif op == 'ADD_GIVING':
                src1 = stmt.get('src1', '')
                src2 = stmt.get('src2', '')
                dst = stmt.get('dst', '')
                print(f"      {i}. ADD_GIVING: {src1} + {src2} → {dst}")
                
            elif op == 'DISPLAY':
                value = stmt.get('value', '')
                print(f"      {i}. DISPLAY: {value}")
                
            elif op == 'DISPLAY_VAR':
                variable = stmt.get('variable', '')
                print(f"      {i}. DISPLAY_VAR: {variable}")
                
            elif op == 'IF':
                cond = stmt.get('cond', '')
                then_stmts = stmt.get('then', [])
                print(f"      {i}. IF: {cond}")
                for j, then_stmt in enumerate(then_stmts, 1):
                    print(f"         THEN {j}: {then_stmt.get('op', 'UNKNOWN')}")
                    
            elif op == 'IF_ELSE':
                cond = stmt.get('cond', '')
                then_stmts = stmt.get('then', [])
                else_stmts = stmt.get('else', [])
                print(f"      {i}. IF_ELSE: {cond}")
                print(f"         THEN: {len(then_stmts)} sentencias")
                print(f"         ELSE: {len(else_stmts)} sentencias")
                
            else:
                print(f"      {i}. {op}: {raw}")

def save_ir_to_file(ir: Dict[str, Any], output_file: str):
    """Función para guardar la IR en un archivo JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ir, f, indent=2, ensure_ascii=False)
    print(f"\n💾 IR guardada en: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python view_ir.py <archivo.cob> [--save]")
        print("\nEjemplos:")
        print("  python view_ir.py samples/demo1.cob")
        print("  python view_ir.py samples/demo2.cob --save")
        print("  python view_ir.py samples/demo3.cob")
        sys.exit(1)

    cob_path = sys.argv[1]
    save_to_file = "--save" in sys.argv
    
    try:
        print(f"🚀 Visualizador de Representación Intermedia (IR)")
        print(f"📁 Archivo: {cob_path}")
        print("=" * 60)
        
        # Parsear COBOL a IR
        ir = parse_cobol_to_ir(cob_path)
        
        # Mostrar IR en consola
        display_ir(ir)
        
        # Guardar IR en archivo si se solicita
        if save_to_file:
            program_name = ir['program']
            output_file = f"out/{program_name}_ir.json"
            save_ir_to_file(ir, output_file)
        
        print(f"\n✅ Proceso completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
