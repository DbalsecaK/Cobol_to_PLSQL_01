# ir/package_generator.py
from typing import Dict, Tuple, List
from rules.rules_engine import declare_var, apply_rule

def generate_package(ir: Dict) -> Tuple[str, Dict]:
    program = ir.get("program", "COBOL_PROGRAM")
    vars_decl = [declare_var(v["name"], v["type"], v["size"]) for v in ir.get("variables", [])]

    coverage = {"rules":0, "gaps":0}
    lines: List[str] = []
    for proc in ir.get("procedures", []):
        for s in proc.get("statements", []):
            out = apply_rule(s)
            if out.startswith("-- GAP"):
                coverage["gaps"] += 1
            else:
                coverage["rules"] += 1
            lines.append(out)

    vars_decl_str = '\n    '.join(vars_decl)
    lines_str = '\n    '.join(lines)
    
    body = f"""CREATE OR REPLACE PACKAGE BODY {program} IS
  PROCEDURE MAIN IS
    {vars_decl_str}
  BEGIN
    {lines_str}
  END MAIN;
END {program};
/"""
    return body, coverage
