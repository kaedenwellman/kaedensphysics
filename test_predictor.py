#!/usr/bin/env python3
"""
Test script for projectile predictor - demonstrates calibration
and generates predictions for 19.3g projectiles.
"""

from projectile_predictor import TorsionSpringLauncher, print_prediction_table

def main():
    print("="*70)
    print("PROJECTILE PREDICTOR TEST & DEMONSTRATION")
    print("="*70)

    # Create launcher instance
    launcher = TorsionSpringLauncher()

    # Run calibration
    print("\n1. CALIBRATING LAUNCHER...")
    print("-"*70)
    launcher.calibrate_from_data(verbose=True)

    # Save calibration
    launcher.save_calibration()

    # Generate predictions for 19.3g projectiles
    print("\n2. GENERATING 19.3g PREDICTIONS...")
    print("-"*70)
    results = launcher.generate_prediction_table(19.3, 135, 170, 5)
    print_prediction_table(results, 19.3)

    # Also generate detailed predictions at 1-degree increments
    print("\n3. DETAILED 19.3g PREDICTIONS (1° increments)...")
    print("-"*70)
    detailed_results = launcher.generate_prediction_table(19.3, 135, 170, 1)

    # Save to file
    with open('predictions_19.3g_detailed.txt', 'w') as f:
        f.write("DETAILED PREDICTION TABLE FOR 19.3g PROJECTILE\n")
        f.write("="*70 + "\n")
        f.write(f"{'Angle':<8} {'Δθ':<6} {'Velocity':<12} "
                f"{'Range (in)':<12} {'Range (ft)':<12}\n")
        f.write("-" * 70 + "\n")
        for r in detailed_results:
            f.write(f"{r['cocked_angle_deg']:.0f}°{' ':<5} "
                   f"{r['delta_theta_deg']:.0f}°{' ':<4} "
                   f"{r['launch_velocity_ms']:.2f} m/s{' ':<4} "
                   f"{r['range_inches']:.1f}{' ':<8} "
                   f"{r['range_feet']:.2f}\n")

    print("Detailed predictions saved to predictions_19.3g_detailed.txt")

    # Test with other masses
    print("\n4. QUICK TEST WITH VARIOUS MASSES @ 170° (MAX ANGLE)...")
    print("-"*70)
    test_masses = [12.5, 19.3, 30.0, 45.0, 66.8]

    print(f"{'Mass (g)':<12} {'Range (inches)':<18} {'Range (feet)':<15}")
    print("-"*70)
    for mass in test_masses:
        result = launcher.predict_range_with_drag(170, mass)
        print(f"{mass:<12.1f} {result['range_inches']:<18.1f} "
              f"{result['range_feet']:<15.2f}")
    print("-"*70)

    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\nCalibration file saved: launcher_calibration.json")
    print("Prediction file saved: predictions_19.3g_detailed.txt")
    print("\nRun 'python projectile_predictor.py' for interactive menu.")
    print("="*70)

if __name__ == "__main__":
    main()
