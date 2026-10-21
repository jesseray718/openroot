import argparse
from une.une_atomic_library import unified_effective_power, unified_power_acceleration, global_grid_mass

def main():
    parser = argparse.ArgumentParser(description="UNE Unified Efficiency Framework")
    subparsers = parser.add_subparsers(dest="command")

    # power
    p = subparsers.add_parser("power", help="Calculate effective power")
    p.add_argument("--energy", type=float, required=True)
    p.add_argument("--time", type=float, default=3600)
    p.add_argument("--N", type=int, default=1)
    p.add_argument("--resonance", type=float, default=1.0)
    p.add_argument("--fractal", type=float, default=1.0)

    # accelerate
    a = subparsers.add_parser("accelerate", help="Calculate acceleration of efficiency")
    a.add_argument("--energy", type=float, required=True)
    a.add_argument("--time", type=float, default=3600)
    a.add_argument("--N", type=int, default=1)
    a.add_argument("--epochs", type=int, default=1)

    args = parser.parse_args()

    if args.command == "power":
        result = unified_effective_power(args.energy, args.time, args.N, args.resonance, args.fractal)
        print(f"Effective Power: {result:.4f}")
    elif args.command == "accelerate":
        result = unified_power_acceleration(args.energy, args.time, args.N, epochs=args.epochs)
        print(f"Power Acceleration: {result:.4f}")

if __name__ == "__main__":
    main()
