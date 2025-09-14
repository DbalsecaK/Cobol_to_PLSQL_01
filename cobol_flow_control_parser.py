"""
COBOL Flow Control Parser - Módulo independiente para manejar instrucciones de control de flujo
Maneja STOP RUN, EXIT PROGRAM, GO TO, etc. sin afectar el código principal
Sigue principios SOLID: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
"""

import re
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class FlowControlInstruction(ABC):
    """Abstract base class for flow control instructions (Interface Segregation Principle)"""
    
    @abstractmethod
    def parse(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse the instruction from COBOL line"""
        pass
    
    @abstractmethod
    def convert(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """Convert the instruction to PL/SQL"""
        pass


class StopRunInstruction(FlowControlInstruction):
    """Handles STOP RUN instruction (Single Responsibility Principle)"""
    
    def parse(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse STOP RUN instruction"""
        line = line.strip()
        
        # Pattern for STOP RUN
        stop_run_pattern = r'^STOP\s+RUN\.?$'
        match = re.match(stop_run_pattern, line, re.IGNORECASE)
        
        if match:
            return {
                'op': 'STOP_RUN',
                'raw': line
            }
        
        return None
    
    def convert(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """Convert STOP RUN to PL/SQL"""
        return f"{base_indent}RETURN; -- STOP RUN"


class ExitProgramInstruction(FlowControlInstruction):
    """Handles EXIT PROGRAM instruction (Single Responsibility Principle)"""
    
    def parse(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse EXIT PROGRAM instruction"""
        line = line.strip()
        
        # Pattern for EXIT PROGRAM
        exit_program_pattern = r'^EXIT\s+PROGRAM\.?$'
        match = re.match(exit_program_pattern, line, re.IGNORECASE)
        
        if match:
            return {
                'op': 'EXIT_PROGRAM',
                'raw': line
            }
        
        return None
    
    def convert(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """Convert EXIT PROGRAM to PL/SQL"""
        return f"{base_indent}RETURN; -- EXIT PROGRAM"


class GoToInstruction(FlowControlInstruction):
    """Handles GO TO instruction (Single Responsibility Principle)"""
    
    def parse(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse GO TO instruction"""
        line = line.strip()
        
        # Pattern for GO TO
        go_to_pattern = r'^GO\s+TO\s+([A-Z0-9_-]+)\.?$'
        match = re.match(go_to_pattern, line, re.IGNORECASE)
        
        if match:
            return {
                'op': 'GO_TO',
                'target': match.group(1),
                'raw': line
            }
        
        return None
    
    def convert(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """Convert GO TO to PL/SQL"""
        target = stmt.get('target', '')
        target_clean = target.replace('-', '_')
        return f"{base_indent}GOTO {target_clean}; -- GO TO {target}"


class CobolFlowControlParser:
    """
    Main parser for COBOL flow control instructions
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(self):
        # Dependency Inversion Principle - depends on abstractions, not concretions
        self.instructions: List[FlowControlInstruction] = [
            StopRunInstruction(),
            ExitProgramInstruction(),
            GoToInstruction()
        ]
    
    def add_instruction(self, instruction: FlowControlInstruction) -> None:
        """Add new instruction handler (Open/Closed Principle)"""
        self.instructions.append(instruction)
    
    def parse_flow_control(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse flow control instruction from COBOL line
        Uses Strategy pattern with Liskov Substitution Principle
        """
        for instruction in self.instructions:
            result = instruction.parse(line)
            if result:
                return result
        
        return None
    
    def convert_flow_control(self, stmt: Dict[str, Any], base_indent: str) -> str:
        """
        Convert flow control instruction to PL/SQL
        Uses Strategy pattern with Liskov Substitution Principle
        """
        op = stmt.get('op', '')
        
        for instruction in self.instructions:
            # Check if this instruction can handle the operation
            if hasattr(instruction, 'parse'):
                # Create a dummy line to test if this instruction can parse it
                test_line = stmt.get('raw', '')
                if instruction.parse(test_line):
                    return instruction.convert(stmt, base_indent)
        
        # Fallback for unknown operations
        return f"{base_indent}-- GAP: {stmt.get('raw', 'UNKNOWN FLOW CONTROL')}"
    
    def detect_flow_control(self, line: str) -> bool:
        """Detect if line contains flow control instruction"""
        return self.parse_flow_control(line) is not None


# Factory class for creating flow control parsers (Factory Pattern)
class FlowControlParserFactory:
    """Factory for creating flow control parsers with different configurations"""
    
    @staticmethod
    def create_standard_parser() -> CobolFlowControlParser:
        """Create standard flow control parser with common instructions"""
        return CobolFlowControlParser()
    
    @staticmethod
    def create_extended_parser() -> CobolFlowControlParser:
        """Create extended flow control parser with additional instructions"""
        parser = CobolFlowControlParser()
        # Can add more instructions here in the future
        return parser


# Test function to verify the parser works correctly
def test_cobol_flow_control_parser():
    """Test the COBOL flow control parser"""
    parser = FlowControlParserFactory.create_standard_parser()
    
    test_cases = [
        {
            'input': 'STOP RUN.',
            'expected_op': 'STOP_RUN',
            'expected_output': 'RETURN; -- STOP RUN'
        },
        {
            'input': 'EXIT PROGRAM.',
            'expected_op': 'EXIT_PROGRAM',
            'expected_output': 'RETURN; -- EXIT PROGRAM'
        },
        {
            'input': 'GO TO A1000-PROCESS.',
            'expected_op': 'GO_TO',
            'expected_output': 'GOTO A1000_PROCESS; -- GO TO A1000-PROCESS'
        }
    ]
    
    print("Testing COBOL Flow Control Parser:")
    for i, test in enumerate(test_cases, 1):
        # Test parsing
        parsed = parser.parse_flow_control(test['input'])
        parse_success = parsed is not None and parsed.get('op') == test['expected_op']
        
        # Test conversion
        if parsed:
            converted = parser.convert_flow_control(parsed, '    ')
            convert_success = converted.strip() == test['expected_output']
        else:
            convert_success = False
        
        status = "✅ PASS" if parse_success and convert_success else "❌ FAIL"
        print(f"Test {i}: {status}")
        print(f"  Input:    {test['input']}")
        print(f"  Expected: {test['expected_output']}")
        if parsed:
            print(f"  Got:      {converted.strip()}")
        else:
            print(f"  Got:      Failed to parse")
        print()


if __name__ == "__main__":
    test_cobol_flow_control_parser()
