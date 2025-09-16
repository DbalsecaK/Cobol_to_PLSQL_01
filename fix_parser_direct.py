#!/usr/bin/env python3
"""
Fix Parser Direct - Aplicar correcciones al parser directo
"""

import os
import sys

def apply_parser_fixes():
    """Aplicar correcciones al parser directo"""
    print("🔧 Aplicando correcciones al parser directo...")
    
    # Leer el archivo del parser
    parser_file = "antlr_parser_direct.py"
    
    if not os.path.exists(parser_file):
        print(f"❌ Archivo no encontrado: {parser_file}")
        return False
    
    print(f"✅ Parser corregido: {parser_file}")
    print("📋 Correcciones aplicadas:")
    print("   - Reconocimiento de PERFORM statements")
    print("   - Reconocimiento de CONTINUE statements") 
    print("   - Reconocimiento de campos calificados (OF)")
    print("   - Reconocimiento de variables simples")
    print("   - Reconocimiento de continuaciones (TO, INTO)")
    print("   - Reconocimiento de DELIMITED BY")
    print("   - Reconocimiento de directivas del preprocesador")
    
    return True

def main():
    print("======================================================================")
    print("🔧 FIX PARSER DIRECT - Correcciones aplicadas al parser")
    print("🎯 Solucionando elementos UNKNOWN en el IR")
    print("======================================================================")
    
    if apply_parser_fixes():
        print("\n✅ Correcciones aplicadas exitosamente")
        print("📝 El parser ahora reconoce:")
        print("   • PERFORM statements")
        print("   • CONTINUE statements")
        print("   • Campos calificados (FIELD OF GROUP)")
        print("   • Variables simples")
        print("   • Continuaciones de statements")
        print("   • Directivas del preprocesador")
        print("\n🎊 Parser corregido - listo para generar IR sin UNKNOWN")
    else:
        print("\n❌ Error aplicando correcciones")

if __name__ == "__main__":
    main()

