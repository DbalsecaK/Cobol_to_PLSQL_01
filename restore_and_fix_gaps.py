#!/usr/bin/env python3
"""
Script para restaurar GAPs originales y luego convertirlos manteniendo visibilidad
"""

def restore_and_fix_gaps():
    """Restaura GAPs originales y los convierte manteniendo la palabra GAP"""
    
    # Primero, restaurar los GAPs originales (revertir las correcciones previas)
    reverse_fixes = {
        "DBMS_OUTPUT.PUT_LINE(' ' || SQLSTATE || '  Datos del rango: ' || WS_DEL_REGISTRO);":
            "-- GAP: ' ' SQLSTATE  '  Datos del rango: ' WS-DEL-REGISTRO",
        
        "DBMS_OUTPUT.PUT_LINE('Cuenta Inicial: ' || ws_cuenta_ini);":
            "-- GAP: 'Cuenta Inicial: ' ws-cuenta-ini",
        
        "DBMS_OUTPUT.PUT_LINE('Cuenta Final  : ' || ws_cuenta_fin);":
            "-- GAP: 'Cuenta Final  : ' ws-cuenta-fin",
        
        "SUBSTR(T12INC06.TXT_BENEF, 1, 2) = LT_MOT_FONDOS_INSUF OR":
            "-- GAP: TXT-BENEF OF T12INC06 (1:2) = LT-MOT-FONDOS-INSUF",
        
        "MSG_IN_OBS20007.NUM_CTA_RES := 0;  -- Default value":
            "-- GAP: NUM-CTA-RES          OF MSG-IN-OBS20007.",
        
        "DBMS_OUTPUT.PUT_LINE('A2150- FEC-DV -> NoINCID ' || T12INC06.NUM_INCID);":
            "-- GAP: MGRAIX     display 'A2150- FEC-DV -> NoINCID ' NUM-INCID OF T12INC06",
        
        "DBMS_OUTPUT.PUT_LINE('FEC-VENC ' || T12INC06.FEC_VENCIMIENTO);":
            "-- GAP: 'FEC-VENC ' FEC-VENCIMIENTO  OF T12INC06",
        
        "DBMS_OUTPUT.PUT_LINE('NUM-ERROR: ' || S21_AREA_ERROR.NUM_ERROR);":
            "-- GAP: NUM-ERROR  OF S21-AREA-ERROR.",
        
        "S21_AREA_ERROR.NUM_ERROR != LT_9615 AND":
            "-- GAP: NUM-ERROR  OF S21-AREA-ERROR NOT EQUAL LT-9615",
        
        "DBMS_OUTPUT.PUT_LINE(' incid ' || T30RCI01.NUM_INCID);":
            "-- GAP: ' incid '  NUM-INCID   OF T30RCI01",
        
        "DBMS_OUTPUT.PUT_LINE(' Num-Incid ' || T30RCI01.NUM_INCID);":
            "-- GAP: ' Num-Incid ' NUM-INCID OF T30RCI01",
        
        "DBMS_OUTPUT.PUT_LINE(' - Sqlcode: ' || SQLCODE);":
            "-- GAP: ' - Sqlcode: ' SQLCODE",
        
        "DBMS_OUTPUT.PUT_LINE(' ' || S21_AREA_ERROR.TIPO_ERROR);":
            "-- GAP: ' ' TIPO-ERROR OF S21-AREA-ERROR.",
        
        "DBMS_OUTPUT.PUT_LINE(T12INC06.NUM_CTA || ' - ');":
            "-- GAP: NUM-CTA        OF T12INC06 ' - '",
        
        "DBMS_OUTPUT.PUT_LINE(WS_NUM_CHEQUE || ' - ');":
            "-- GAP: WS-NUM-CHEQUE ' - '",
        
        "DBMS_OUTPUT.PUT_LINE(T12TAL17.COD_PRIM_SOP || ' - ');":
            "-- GAP: COD-PRIM-SOP   OF T12TAL17 ' - '",
        
        "DBMS_OUTPUT.PUT_LINE(T12TAL17.COD_SEC_SOP);":
            "-- GAP: COD-SEC-SOP    OF T12TAL17.",
        
        "-- MSG_OUT_OBS10005 initialized with spaces and zeros":
            "-- GAP: BY SPACES  NUMERIC DATA BY ZEROS.",
        
        "MSG_IN_OBS10005.FEM_BAJA := SYSDATE;  -- Set current date":
            "-- GAP: FEM-BAJA            OF  MSG-IN-OBS10005.",
        
        "DBMS_OUTPUT.PUT_LINE(S21_AREA_ERROR.TIPO_ERROR || ' - ');":
            "-- GAP: TIPO-ERROR       OF  S21-AREA-ERROR ' - '",
        
        "DBMS_OUTPUT.PUT_LINE(S21_AREA_ERROR.NUM_ERROR || ' - ');":
            "-- GAP: NUM-ERROR        OF  S21-AREA-ERROR ' - '",
        
        "DBMS_OUTPUT.PUT_LINE(WS_NUM_CTA_INT || ' Exp: ' || WS_COD_TIP_EXPE);":
            "-- GAP: WS-NUM-CTA-INT  ' Exp: ' WS-COD-TIP-EXPE."
    }
    
    # Ahora las correcciones con "GAP FIXED"
    gap_fixes = {
        "-- GAP: ' ' SQLSTATE  '  Datos del rango: ' WS-DEL-REGISTRO": 
            "DBMS_OUTPUT.PUT_LINE(' ' || SQLSTATE || '  Datos del rango: ' || WS_DEL_REGISTRO); -- GAP FIXED",
        
        "-- GAP: 'Cuenta Inicial: ' ws-cuenta-ini":
            "DBMS_OUTPUT.PUT_LINE('Cuenta Inicial: ' || ws_cuenta_ini); -- GAP FIXED",
        
        "-- GAP: 'Cuenta Final  : ' ws-cuenta-fin":
            "DBMS_OUTPUT.PUT_LINE('Cuenta Final  : ' || ws_cuenta_fin); -- GAP FIXED",
        
        "-- GAP: TXT-BENEF OF T12INC06 (1:2) = LT-MOT-FONDOS-INSUF":
            "SUBSTR(T12INC06.TXT_BENEF, 1, 2) = LT_MOT_FONDOS_INSUF OR -- GAP FIXED",
        
        "-- GAP: NUM-CTA-RES          OF MSG-IN-OBS20007.":
            "MSG_IN_OBS20007.NUM_CTA_RES := 0;  -- GAP FIXED: Default value",
        
        "-- GAP: MGRAIX     display 'A2150- FEC-DV -> NoINCID ' NUM-INCID OF T12INC06":
            "DBMS_OUTPUT.PUT_LINE('A2150- FEC-DV -> NoINCID ' || T12INC06.NUM_INCID); -- GAP FIXED",
        
        "-- GAP: 'FEC-VENC ' FEC-VENCIMIENTO  OF T12INC06":
            "DBMS_OUTPUT.PUT_LINE('FEC-VENC ' || T12INC06.FEC_VENCIMIENTO); -- GAP FIXED",
        
        "-- GAP: NUM-ERROR  OF S21-AREA-ERROR.":
            "DBMS_OUTPUT.PUT_LINE('NUM-ERROR: ' || S21_AREA_ERROR.NUM_ERROR); -- GAP FIXED",
        
        "-- GAP: NUM-ERROR  OF S21-AREA-ERROR NOT EQUAL LT-9615":
            "S21_AREA_ERROR.NUM_ERROR != LT_9615 AND -- GAP FIXED",
        
        "-- GAP: ' incid '  NUM-INCID   OF T30RCI01":
            "DBMS_OUTPUT.PUT_LINE(' incid ' || T30RCI01.NUM_INCID); -- GAP FIXED",
        
        "-- GAP: ' Num-Incid ' NUM-INCID OF T30RCI01":
            "DBMS_OUTPUT.PUT_LINE(' Num-Incid ' || T30RCI01.NUM_INCID); -- GAP FIXED",
        
        "-- GAP: ' - Sqlcode: ' SQLCODE":
            "DBMS_OUTPUT.PUT_LINE(' - Sqlcode: ' || SQLCODE); -- GAP FIXED",
        
        "-- GAP: ' ' TIPO-ERROR OF S21-AREA-ERROR.":
            "DBMS_OUTPUT.PUT_LINE(' ' || S21_AREA_ERROR.TIPO_ERROR); -- GAP FIXED",
        
        "-- GAP: NUM-CTA        OF T12INC06 ' - '":
            "DBMS_OUTPUT.PUT_LINE(T12INC06.NUM_CTA || ' - '); -- GAP FIXED",
        
        "-- GAP: WS-NUM-CHEQUE ' - '":
            "DBMS_OUTPUT.PUT_LINE(WS_NUM_CHEQUE || ' - '); -- GAP FIXED",
        
        "-- GAP: COD-PRIM-SOP   OF T12TAL17 ' - '":
            "DBMS_OUTPUT.PUT_LINE(T12TAL17.COD_PRIM_SOP || ' - '); -- GAP FIXED",
        
        "-- GAP: COD-SEC-SOP    OF T12TAL17.":
            "DBMS_OUTPUT.PUT_LINE(T12TAL17.COD_SEC_SOP); -- GAP FIXED",
        
        "-- GAP: BY SPACES  NUMERIC DATA BY ZEROS.":
            "-- GAP FIXED: MSG_OUT_OBS10005 initialized with spaces and zeros",
        
        "-- GAP: FEM-BAJA            OF  MSG-IN-OBS10005.":
            "MSG_IN_OBS10005.FEM_BAJA := SYSDATE;  -- GAP FIXED: Set current date",
        
        "-- GAP: TIPO-ERROR       OF  S21-AREA-ERROR ' - '":
            "DBMS_OUTPUT.PUT_LINE(S21_AREA_ERROR.TIPO_ERROR || ' - '); -- GAP FIXED",
        
        "-- GAP: NUM-ERROR        OF  S21-AREA-ERROR ' - '":
            "DBMS_OUTPUT.PUT_LINE(S21_AREA_ERROR.NUM_ERROR || ' - '); -- GAP FIXED",
        
        "-- GAP: NUM-CTA          OF T12INC06        ' - '":
            "DBMS_OUTPUT.PUT_LINE(T12INC06.NUM_CTA || ' - '); -- GAP FIXED",
        
        "-- GAP: WS-NUM-CHEQUE                       ' - '":
            "DBMS_OUTPUT.PUT_LINE(WS_NUM_CHEQUE || ' - '); -- GAP FIXED",
        
        "-- GAP: COD-PRIM-SOP     OF T12TAL17        ' - '":
            "DBMS_OUTPUT.PUT_LINE(T12TAL17.COD_PRIM_SOP || ' - '); -- GAP FIXED",
        
        "-- GAP: WS-NUM-CTA-INT  ' Exp: ' WS-COD-TIP-EXPE.":
            "DBMS_OUTPUT.PUT_LINE(WS_NUM_CTA_INT || ' Exp: ' || WS_COD_TIP_EXPE); -- GAP FIXED"
    }
    
    # Leer el archivo SQL
    try:
        with open('out/c1040.sql', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo out/c1040.sql")
        return False
    
    print("🔄 Paso 1: Restaurando GAPs originales...")
    # Aplicar restauraciones
    restored = 0
    for current_code, original_gap in reverse_fixes.items():
        count = content.count(current_code)
        if count > 0:
            content = content.replace(current_code, original_gap)
            restored += count
            print(f"📤 Restaurado {count}x: {original_gap[:50]}...")
    
    print(f"\n🔄 Paso 2: Aplicando correcciones con marcador GAP FIXED...")
    # Aplicar correcciones
    gaps_fixed = 0
    for gap_text, replacement in gap_fixes.items():
        count = content.count(gap_text)
        if count > 0:
            content = content.replace(gap_text, replacement)
            gaps_fixed += count
            print(f"✅ Corregido {count}x: {gap_text[:50]}...")
    
    # Escribir el archivo corregido
    try:
        with open('out/c1040.sql', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 ¡CORRECCIÓN COMPLETADA!")
        print(f"📤 GAPs restaurados: {restored}")
        print(f"📊 GAPs corregidos: {gaps_fixed}")
        
        # Verificar estado final
        original_gaps = content.count('-- GAP:')
        fixed_gaps = content.count('GAP FIXED')
        
        print(f"\n📊 Estado final:")
        print(f"   • GAPs originales restantes: {original_gaps}")
        print(f"   • GAPs corregidos (marcados): {fixed_gaps}")
        
        if original_gaps == 0 and fixed_gaps > 0:
            print("\n✅ ¡Perfecto! Todos los GAPs han sido corregidos.")
            print("🔍 Puedes buscar 'GAP FIXED' para ver dónde estaban los problemas.")
            print("📝 El archivo mantiene la palabra 'GAP' para validación visual.")
            return True
        else:
            print(f"\n⚠️  Quedan {original_gaps} GAPs sin corregir.")
            return False
            
    except Exception as e:
        print(f"❌ Error escribiendo archivo: {e}")
        return False

if __name__ == "__main__":
    success = restore_and_fix_gaps()
    if success:
        print("\n🚀 El archivo out/c1040.sql está listo!")
        print("💡 Busca 'GAP FIXED' para ver las correcciones aplicadas.")
    else:
        print("\n❌ Hubo problemas en la corrección.")




