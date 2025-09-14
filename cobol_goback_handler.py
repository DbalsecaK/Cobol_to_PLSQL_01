"""
COBOL GOBACK Handler - Implementación con principios SOLID
Maneja la conversión de GOBACK de COBOL a PL/SQL
"""

from typing import Optional, Dict, Any
import re


class GOBACKHandler:
    """
    Clase para manejar la conversión de GOBACK de COBOL a PL/SQL
    Implementa principios SOLID:
    - SRP: Solo maneja GOBACK
    - OCP: Abierto para extensión, cerrado para modificación
    - LSP: Intercambiable con otros handlers
    - ISP: Interfaz específica para GOBACK
    - DIP: Depende de abstracciones
    """
    
    def __init__(self):
        """Inicializa el handler de GOBACK"""
        self.goback_patterns = [
            r'^\s*GOBACK\s*\.?\s*$',  # GOBACK.
            r'^\s*GO\s+BACK\s*\.?\s*$',  # GO BACK.
            r'^\s*EXIT\s+PROGRAM\s*\.?\s*$',  # EXIT PROGRAM.
        ]
    
    def can_handle(self, line: str) -> bool:
        """
        Verifica si la línea puede ser manejada por este handler
        Args:
            line: Línea de código COBOL
        Returns:
            bool: True si puede manejar la línea
        """
        line_clean = line.strip().upper()
        return any(re.match(pattern, line_clean, re.IGNORECASE) for pattern in self.goback_patterns)
    
    def parse_goback(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parsea una línea de GOBACK
        Args:
            line: Línea de código COBOL
        Returns:
            Dict con información del GOBACK o None si no es válido
        """
        if not self.can_handle(line):
            return None
        
        line_clean = line.strip().upper()
        
        # Determinar el tipo de GOBACK
        goback_type = "STANDARD"
        if "EXIT PROGRAM" in line_clean:
            goback_type = "EXIT_PROGRAM"
        elif "GO BACK" in line_clean:
            goback_type = "GO_BACK"
        
        return {
            'op': 'GOBACK',
            'type': goback_type,
            'raw': line.strip()
        }
    
    def convert_goback(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """
        Convierte GOBACK a PL/SQL
        Args:
            stmt: Declaración parseada de GOBACK
            base_indent: Indentación base
        Returns:
            str: Código PL/SQL equivalente
        """
        goback_type = stmt.get('type', 'STANDARD')
        
        if goback_type == "EXIT_PROGRAM":
            return f"{base_indent}RETURN; -- EXIT PROGRAM"
        elif goback_type == "GO_BACK":
            return f"{base_indent}RETURN; -- GO BACK"
        else:
            return f"{base_indent}RETURN; -- GOBACK"


class GOBACKHandlerFactory:
    """
    Factory para crear handlers de GOBACK
    Implementa el patrón Factory con principios SOLID
    """
    
    @staticmethod
    def create_standard_handler() -> GOBACKHandler:
        """
        Crea un handler estándar de GOBACK
        Returns:
            GOBACKHandler: Handler configurado
        """
        return GOBACKHandler()
    
    @staticmethod
    def create_custom_handler(patterns: list) -> GOBACKHandler:
        """
        Crea un handler personalizado de GOBACK
        Args:
            patterns: Lista de patrones personalizados
        Returns:
            GOBACKHandler: Handler con patrones personalizados
        """
        handler = GOBACKHandler()
        handler.goback_patterns = patterns
        return handler
