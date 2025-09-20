#!/usr/bin/env python3
"""
Analizar código funcional vs comentarios en CS63.sql
"""

import re

def analyze_functional_code():
    """Analiza la funcionalidad real del código SQL generado"""
    
    try:
        with open('out/CS63.sql', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ No se encontró out/CS63.sql")
        return
    
    lines = content.split('\n')
    
    stats = {
        'total_lines': len(lines),
        'gap_comments': 0,
        'functional_code': 0,
        'plsql_statements': 0,
        'sql_statements': 0,
        'assignments': 0,
        'conditions': 0,
        'procedures': 0,
        'empty_or_comments': 0
    }
    
    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('--'):
            if '-- GAP:' in line:
                stats['gap_comments'] += 1
            else:
                stats['empty_or_comments'] += 1
        else:
            stats['functional_code'] += 1
            
            # Clasificar tipos de código funcional
            if any(keyword in line.upper() for keyword in ['DBMS_OUTPUT', 'PUT_LINE']):
                stats['plsql_statements'] += 1
            elif any(keyword in line.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'VALUES', 'WHERE']):
                stats['sql_statements'] += 1
            elif ':=' in line or '=' in line:
                stats['assignments'] += 1
            elif any(keyword in line.upper() for keyword in ['IF', 'THEN', 'ELSE', 'END IF', 'CASE', 'WHEN']):
                stats['conditions'] += 1
            elif any(keyword in line.upper() for keyword in ['PROCEDURE', 'FUNCTION', 'BEGIN', 'END']):
                stats['procedures'] += 1
    
    # Calcular porcentajes
    functional_percentage = (stats['functional_code'] / stats['total_lines']) * 100
    gap_percentage = (stats['gap_comments'] / stats['total_lines']) * 100
    
    print("📊 ANÁLISIS DE FUNCIONALIDAD CS63.SQL")
    print("=" * 50)
    print(f"📄 Total líneas: {stats['total_lines']}")
    print(f"💬 Comentarios GAP: {stats['gap_comments']} ({gap_percentage:.1f}%)")
    print(f"⚙️  Código funcional: {stats['functional_code']} ({functional_percentage:.1f}%)")
    print(f"📝 Comentarios/vacías: {stats['empty_or_comments']}")
    
    print(f"\n🔧 DESGLOSE CÓDIGO FUNCIONAL:")
    print(f"   • PL/SQL statements: {stats['plsql_statements']}")
    print(f"   • SQL statements: {stats['sql_statements']}")
    print(f"   • Asignaciones: {stats['assignments']}")
    print(f"   • Condiciones: {stats['conditions']}")
    print(f"   • Procedures/Functions: {stats['procedures']}")
    print(f"   • Otros: {stats['functional_code'] - stats['plsql_statements'] - stats['sql_statements'] - stats['assignments'] - stats['conditions'] - stats['procedures']}")
    
    # Calcular mejora de funcionalidad
    gaps_with_code = 0
    gap_lines = [line for line in lines if '-- GAP:' in line]
    
    for i, line in enumerate(lines):
        if '-- GAP:' in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not next_line.startswith('--'):
                gaps_with_code += 1
    
    gap_code_percentage = (gaps_with_code / len(gap_lines)) * 100 if gap_lines else 0
    
    print(f"\n✅ MEJORA EN GAPS:")
    print(f"   • GAPs totales: {len(gap_lines)}")
    print(f"   • GAPs con código: {gaps_with_code}")
    print(f"   • Porcentaje mejorado: {gap_code_percentage:.1f}%")
    
    print(f"\n🎯 RESUMEN FINAL:")
    print(f"   • Funcionalidad total: {functional_percentage:.1f}%")
    print(f"   • GAPs resueltos: {gap_code_percentage:.1f}%")
    print(f"   • Estado: {'✅ EXCELENTE' if functional_percentage > 80 else '⚠️ BUENO' if functional_percentage > 60 else '❌ NECESITA MEJORA'}")

if __name__ == "__main__":
    analyze_functional_code()










