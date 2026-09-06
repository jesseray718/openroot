#!/data/data/com.termux/files/usr/bin/python3
"""UNE Resolver v0.1 — 36-symbol base, exponential layers, permaculture axioms"""
import argparse, json, hashlib, sys
from datetime import datetime

SYMBOLS = {
    # Layer 0: Fundamental (0-9)
    '0': 'void', '1': 'unity', '2': 'duality', '3': 'trinity', '4': 'quaternion',
    '5': 'quintessence', '6': 'hexad', '7': 'heptad', '8': 'ogdoad', '9': 'ennead',
    # Layer 1: Forces (A-Z)
    'A': 'light', 'B': 'biomass', 'C': 'cascade', 'D': 'desiccant', 'E': 'energy',
    'F': 'flow', 'G': 'growth', 'H': 'heat', 'I': 'ion', 'J': 'junction',
    'K': 'kingdom', 'L': 'labyrinth', 'M': 'mesh', 'N': 'node', 'O': 'oscillation',
    'P': 'permaculture', 'Q': 'quantum', 'R': 'radiation', 'S': 'solvent', 'T': 'thermal',
    'U': 'universal', 'V': 'vesica', 'W': 'work', 'X': 'xerophyte', 'Y': 'yield', 'Z': 'zenith',
    # Layer 2: Modifiers (0-9 alpha)
    'a': 'active', 'b': 'biological', 'c': 'coupled', 'd': 'digital', 'e': 'emissive',
    'f': 'fluid', 'g': 'gaseous', 'h': 'hybrid', 'i': 'inert', 'j': 'junction',
}

def parse_une(code):
    """Parse UNE code: DV.GEN.TH.AE01 -> domain.genus.taxon.instance"""
    parts = code.split('.')
    result = {'code': code, 'parsed': []}
    for p in parts:
        sym_breakdown = []
        for c in p:
            sym_breakdown.append({'symbol': c, 'meaning': SYMBOLS.get(c, '?')})
        result['parsed'].append({'segment': p, 'symbols': sym_breakdown})
    result['hash'] = hashlib.sha256(code.encode()).hexdigest()[:16]
    result['layer'] = len(parts)
    return result

def validate_une(code):
    """Validate UNE against structure rules"""
    if not all(c in SYMBOLS or c == '.' for c in code):
        return {'valid': False, 'error': f'Invalid symbol in {code}'}
    parts = code.split('.')
    if len(parts) < 2 or len(parts) > 4:
        return {'valid': False, 'error': f'UNE must have 2-4 segments, got {len(parts)}'}
    return {'valid': True, 'segments': len(parts), 'code': code}

def main():
    parser = argparse.ArgumentParser(description='UNE Resolver — Universal Nomenclature Engine')
    parser.add_argument('code', nargs='?', help='UNE code (e.g., DV.GEN.TH.AE01)')
    parser.add_argument('-v', '--validate', action='store_true', help='Validate UNE structure')
    parser.add_argument('-p', '--parse', action='store_true', help='Parse and explain UNE')
    parser.add_argument('-j', '--json', action='store_true', help='JSON output')
    args = parser.parse_args()

    if not args.code:
        parser.print_help()
        sys.exit(1)

    if args.validate:
        result = validate_une(args.code)
    else:
        result = parse_une(args.code)

    if args.json:
        print(json.dumps(result))
    else:
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
