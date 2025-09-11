#!/usr/bin/env python3
"""
Convertidor COBOL a PL/SQL simplificado - sin paquetes
"""
import sys
import os
import json
import re
from typing import Any, Dict, List, Optional

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
        m = re.search(r'PROGRAM-ID\.\s*([A-Z0-9_-]+)\.', self.text, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        return None

    def _extract_section_text(self, start_marker: str, end_marker: Optional[str]=None) -> str:
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
        proc_text = self._extract_section_text(r'PROCEDURE DIVISION', r'STOP RUN\.')
        if not proc_text:
            proc_text = self._extract_section_text(r'PROCEDURE DIVISION')
        lines = [ln.strip() for ln in proc_text.splitlines() if ln.strip()]
        stmts: List[Dict[str, Any]] = []

        for ln in lines:
            m = re.search(r'^MOVE\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"MOVE", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": ln})
                continue

            m = re.search(r'^ADD\s+(.+?)\s+TO\s+([A-Z0-9_-]+)\.', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"ADD", "src": m.group(1).strip(), "dst": m.group(2).upper(), "raw": ln})
                continue

            m = re.search(r'^IF\s+(.+?)\s+DISPLAY\s+(.+?)\.', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"IF", "cond": m.group(1).strip(), "then":[{"op":"DISPLAY","value": m.group(2).strip()}], "raw": ln})
                continue

            m = re.search(r'^DISPLAY\s+(.+?)\.', ln, re.IGNORECASE)
            if m:
                stmts.append({"op":"DISPLAY", "value": m.group(1).strip(), "raw": ln})
                continue

            stmts.append({"op":"UNKNOWN", "raw": ln})
        return stmts

# ===== RULES ENGINE =====
def declare_var(name: str, vtype: str, size: int) -> str:
    if vtype == 'STRING':
        return f"  {name} VARCHAR2({size});"
    else:
        return f"  {name} NUMBER({size});"

def apply_rule(stmt: Dict[str, Any]) -> str:
    op = stmt.get("op", "UNKNOWN")
    
    if op == "MOVE":
        src = stmt.get("src", "")
        dst = stmt.get("dst", "")
        return f"    {dst} := {src};"
    
    elif op == "ADD":
        src = stmt.get("src", "")
        dst = stmt.get("dst", "")
        return f"    {dst} := {dst} + {src};"
    
    elif op == "DISPLAY":
        value = stmt.get("value", "")
        return f"    DBMS_OUTPUT.PUT_LINE({value});"
    
    elif op == "IF":
        cond = stmt.get("cond", "")
        then_stmts = stmt.get("then", [])
        then_code = "\n".join([apply_rule(t) for t in then_stmts])
        return f"    IF {cond} THEN\n{then_code}\n    END IF;"
    
    else:
        return f"    -- GAP: {stmt.get('raw', 'Unknown statement')}"

# ===== PACKAGE GENERATOR =====
def generate_package(ir: Dict) -> tuple:
    program = ir.get("program", "COBOL_PROGRAM")
    vars_decl = [declare_var(v["name"], v["type"], v["size"]) for v in ir.get("variables", [])]

    coverage = {"rules":0, "gaps":0}
    lines: List[str] = []
    for proc in ir.get("procedures", []):
        for s in proc.get("statements", []):
            out = apply_rule(s)
            if out.startswith("    -- GAP"):
                coverage["gaps"] += 1
            else:
                coverage["rules"] += 1
            lines.append(out)

    vars_decl_str = '\n'.join(vars_decl)
    lines_str = '\n'.join(lines)
    
    body = f"""CREATE OR REPLACE PACKAGE BODY {program} IS
  PROCEDURE MAIN IS
{vars_decl_str}
  BEGIN
{lines_str}
  END MAIN;
END {program};
/"""
    return body, coverage

# ===== MAIN FUNCTION =====
def parse_cobol_to_ir(file_path: str):
    """Función para parsear COBOL a IR"""
    with open(file_path, 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    class MockEntry:
        def __init__(self, text):
            self.text = text
    
    entry = MockEntry(full_text)
    visitor = IRBuildingVisitor(token_stream=None, full_text=full_text)
    return visitor.build_ir(entry)

def main():
    if len(sys.argv) < 2:
        print("Uso: python simple_converter.py <archivo.cob>")
        sys.exit(1)

    cob_path = sys.argv[1]
    
    try:
        print(f"🔄 Procesando archivo: {cob_path}")
        ir = parse_cobol_to_ir(cob_path)
        print(f"📋 IR generado para programa: {ir['program']}")
        print(f"📊 Variables encontradas: {len(ir['variables'])}")
        print(f"📊 Sentencias encontradas: {len(ir['procedures'][0]['statements'])}")
        
        plsql, coverage = generate_package(ir)
        
        out_dir = os.path.join(os.path.dirname(__file__), "out")
        os.makedirs(out_dir, exist_ok=True)
        pkg_path = os.path.join(out_dir, f"{ir['program']}.sql")
        
        with open(pkg_path, "w", encoding="utf-8") as f:
            f.write(plsql)

        rep_path = os.path.join(out_dir, "report.json")
        with open(rep_path, "w", encoding="utf-8") as f:
            json.dump({"program": ir["program"], "coverage": coverage}, f, indent=2)

        print("✅ Archivos generados:")
        print(f"   📄 {pkg_path}")
        print(f"   📊 {rep_path}")
        print(f"📈 Cobertura: {coverage['rules']} reglas aplicadas, {coverage['gaps']} gaps")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
