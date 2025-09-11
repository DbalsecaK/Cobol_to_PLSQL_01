# main.py
import sys, os, json

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Imports directos
from parser.antlr_driver import parse_cobol_to_ir
from ir.package_generator import generate_package

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <archivo.cob>")
        sys.exit(1)

    cob_path = sys.argv[1]
    ir = parse_cobol_to_ir(cob_path)
    plsql, coverage = generate_package(ir)

    out_dir = os.path.join(os.path.dirname(__file__), "out")
    os.makedirs(out_dir, exist_ok=True)
    pkg_path = os.path.join(out_dir, f"{ir['program']}.sql")
    with open(pkg_path, "w", encoding="utf-8") as f:
        f.write(plsql)

    rep_path = os.path.join(out_dir, "report.json")
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump({"program": ir["program"], "coverage": coverage}, f, indent=2)

    print("✅ Generado:")
    print(" -", pkg_path)
    print(" -", rep_path)

if __name__ == "__main__":
    main()
