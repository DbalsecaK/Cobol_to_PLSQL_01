# rules/rules_engine.py
from typing import Dict

def declare_var(name: str, vtype: str, size: int) -> str:
    if vtype == "STRING":
        return f"{name} VARCHAR2({size});"
    # crude numeric mapping; tune for COMP-3, scale, etc.
    return f"{name} NUMBER({size});"

def apply_rule(stmt: Dict) -> str:
    op = stmt.get("op")
    if op == "MOVE":
        return f"{stmt['dst']} := {stmt['src']};"
    if op == "ADD":
        return f"{stmt['dst']} := {stmt['dst']} + {stmt['src']};"
    if op == "DISPLAY":
        return f"DBMS_OUTPUT.PUT_LINE({stmt['value']});"
    if op == "IF":
        inner = "\n    ".join(apply_rule(s) for s in stmt.get("then", []))
        return f"""IF {stmt['cond']} THEN
    {inner}
END IF;"""
    return f"-- GAP: {op} :: {stmt.get('raw','')}"
