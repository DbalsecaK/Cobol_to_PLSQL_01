#!/usr/bin/env python3
"""
Analizar sentencias EXEC SQL en el IR
"""
import json
import sys

def analyze_exec_sql(ir_file):
    """Analizar sentencias EXEC SQL"""
    
    print(f"🔍 Analizando EXEC SQL en: {ir_file}")
    
    try:
        with open(ir_file, 'r', encoding='utf-8') as f:
            ir = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo IR: {e}")
        return
    
    print("\n📊 ANÁLISIS DE SENTENCIAS EXEC SQL:")
    print("=" * 70)
    
    # Analizar Data Division para INCLUDE statements
    data_division = ir.get("data_division", {})
    exec_sql_includes = data_division.get("exec_sql", [])
    
    print(f"📋 EXEC SQL en Data Division: {len(exec_sql_includes)} statements")
    
    # Categorizar INCLUDE statements
    includes = []
    cursors = []
    others = []
    
    for exec_sql in exec_sql_includes:
        sql_statement = exec_sql.get("sql_statement", "")
        sql_type = exec_sql.get("sql_type", "")
        
        if "INCLUDE" in sql_statement.upper():
            includes.append(exec_sql)
        elif "DECLARE" in sql_statement.upper() and "CURSOR" in sql_statement.upper():
            cursors.append(exec_sql)
        else:
            others.append(exec_sql)
    
    print(f"\n📂 CATEGORIZACIÓN DATA DIVISION:")
    print(f"   INCLUDE statements: {len(includes)}")
    print(f"   CURSOR declarations: {len(cursors)}")
    print(f"   Otros: {len(others)}")
    
    print(f"\n📝 INCLUDE STATEMENTS:")
    for i, inc in enumerate(includes):
        table = inc.get("sql_statement", "").replace("INCLUDE ", "")
        print(f"   {i+1:2d}. INCLUDE {table}")
    
    print(f"\n📝 CURSOR DECLARATIONS:")
    for i, cursor in enumerate(cursors):
        sql = cursor.get("sql_statement", "")
        cursor_name = ""
        if "DECLARE" in sql:
            parts = sql.split()
            if len(parts) > 1:
                cursor_name = parts[1]
        print(f"   {i+1:2d}. CURSOR {cursor_name}")
    
    # Analizar Procedure Division para EXEC SQL statements
    procedures = ir.get("procedures", [])
    procedure_exec_sql = []
    
    for proc in procedures:
        proc_name = proc.get("name", "")
        statements = proc.get("statements", [])
        
        for stmt in statements:
            if stmt.get("type") == "EXEC_SQL":
                stmt["procedure"] = proc_name
                procedure_exec_sql.append(stmt)
    
    print(f"\n📋 EXEC SQL en Procedure Division: {len(procedure_exec_sql)} statements")
    
    # Categorizar por tipo SQL
    selects = []
    commits = []
    opens = []
    fetches = []
    closes = []
    proc_others = []
    
    for exec_sql in procedure_exec_sql:
        sql_type = exec_sql.get("sql_type", "")
        
        if sql_type == "SELECT":
            selects.append(exec_sql)
        elif sql_type == "COMMIT":
            commits.append(exec_sql)
        elif sql_type == "OPEN":
            opens.append(exec_sql)
        elif sql_type == "FETCH":
            fetches.append(exec_sql)
        elif sql_type == "CLOSE":
            closes.append(exec_sql)
        else:
            proc_others.append(exec_sql)
    
    print(f"\n📂 CATEGORIZACIÓN PROCEDURE DIVISION:")
    print(f"   SELECT statements: {len(selects)}")
    print(f"   COMMIT statements: {len(commits)}")
    print(f"   OPEN CURSOR: {len(opens)}")
    print(f"   FETCH CURSOR: {len(fetches)}")
    print(f"   CLOSE CURSOR: {len(closes)}")
    print(f"   Otros: {len(proc_others)}")
    
    # Mostrar ejemplos
    print(f"\n📝 EJEMPLOS DE SELECT STATEMENTS:")
    for i, select in enumerate(selects[:3]):
        proc = select.get("procedure", "")
        sql = select.get("sql_statement", "")[:100] + "..." if len(select.get("sql_statement", "")) > 100 else select.get("sql_statement", "")
        print(f"   {i+1}. En {proc}: {sql}")
    
    print(f"\n📝 EJEMPLOS DE CURSOR OPERATIONS:")
    for i, op in enumerate(opens[:3]):
        proc = op.get("procedure", "")
        sql = op.get("sql_statement", "")
        print(f"   {i+1}. OPEN en {proc}: {sql}")
    
    # Resumen total
    total_exec_sql = len(exec_sql_includes) + len(procedure_exec_sql)
    
    print(f"\n🎯 RESUMEN TOTAL:")
    print(f"   EXEC SQL Data Division: {len(exec_sql_includes)}")
    print(f"   EXEC SQL Procedure Division: {len(procedure_exec_sql)}")
    print(f"   TOTAL EXEC SQL STATEMENTS: {total_exec_sql}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    ir_file = "out/C1040_ir_clean.json"
    analyze_exec_sql(ir_file)



