# parser/ir_visitor.py
from typing import Any, Dict, List, Optional
import re

class IRBuildingVisitor:
    def __init__(self, token_stream, full_text: str):
        self.ts = token_stream  # Puede ser None en la versión simplificada
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
            if not e or e.start() <= s.end():
                return self.text[s.end():]
            return self.text[s.end():e.start()]
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
