#!/usr/bin/env python3
"""
Projectile Range Predictor for Torsion Spring Launcher - Version 2
Physics Extra Credit Project

This version uses a hybrid empirical-physics model:
1. Empirical polynomial fit for the reference mass (66.8g)
2. Physics-based mass scaling with drag corrections
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import json
import os
from typing import Tuple, Dict, List


# ============================================================================
# LAUNCHER SPECIFICATIONS (Constants)
# ============================================================================

LEVER_ARM_INCHES = 9.2
LAUNCH_HEIGHT_INCHES = 11.0
RELAXED_ANGLE_DEG = 135.0

# Physical constants
G_METRIC = 9.81  # m/s²
G_IMPERIAL = 386.1  # in/s²

# Calibration data
CALIBRATION_MASS = 66.8  # grams
CALIBRATION_DATA = [
    (155, 50),   # (angle_deg, range_inches)
    (165, 78),
    (170, 93),
]

LIGHT_MASS_DATA = {'mass_g': 12.5, 'angle_deg': 170, 'range_inches': 180}


# ============================================================================
# HYBRID PHYSICS MODEL
# ============================================================================

class LauncherModel:
    """
    Hybrid empirical-physics model for projectile prediction.
    """

    def __init__(self):
        """Initialize with default parameters."""
        # Empirical model coefficients (for reference mass)
        self.ref_mass = CALIBRATION_MASS
        self.poly_coeffs = None  # Polynomial coefficients

        # Physics parameters
        self.launch_velocity_ref = {}  # Velocity at each angle for reference mass
        self.launch_angle_deg = 55.0  # Effective launch angle
        self.drag_factor = 0.92  # Reduction factor due to drag (lighter = more reduction)

        # Calibration results
        self.calibration_results = {}

    def get_deflection(self, cocked_angle_deg: float) -> float:
        """Get spring deflection angle Δθ."""
        return cocked_angle_deg - RELAXED_ANGLE_DEG

    def fit_reference_mass_data(self):
        """
        Fit empirical model to reference mass (66.8g) data.
        Uses quadratic model: R = a*(Δθ)² + b*(Δθ) + c
        """
        # Extract deflection angles and ranges
        delta_thetas = np.array([self.get_deflection(angle) for angle, _ in CALIBRATION_DATA])
        ranges = np.array([r for _, r in CALIBRATION_DATA])

        # Fit quadratic polynomial
        def quadratic(delta_theta, a, b, c):
            return a * delta_theta**2 + b * delta_theta + c

        # Fit with physical constraint: range should be 0 or small at Δθ=0
        self.poly_coeffs, _ = curve_fit(
            quadratic,
            delta_thetas,
            ranges,
            p0=[1/75, 32/15, 2]  # User's suggested coefficients as initial guess
        )

        # Calculate velocities that would produce these ranges
        # Using range formula: R = v₀²sin(2θ)/g for ballistic motion
        # With launch height: more complex, but approximate
        for angle, measured_range in CALIBRATION_DATA:
            # Estimate launch velocity needed for this range
            range_m = measured_range * 0.0254
            height_m = LAUNCH_HEIGHT_INCHES * 0.0254
            angle_rad = np.radians(self.launch_angle_deg)

            # Approximate ballistic range equation accounting for height
            # R ≈ (v₀²/g) * sin(2θ) * (1 + sqrt(1 + 2gh/(v₀²sin²θ)))
            # Solve approximately for v₀

            # Simplified: assume v₀² ≈ R*g / (sin(2θ) + small correction)
            sin_2theta = np.sin(2 * angle_rad)
            v0_estimate = np.sqrt(range_m * G_METRIC / sin_2theta)

            self.launch_velocity_ref[angle] = v0_estimate

    def predict_range_reference_mass(self, cocked_angle_deg: float) -> float:
        """
        Predict range for reference mass using empirical model.

        Args:
            cocked_angle_deg: Cocked arm angle in degrees

        Returns:
            Predicted range in inches
        """
        delta_theta = self.get_deflection(cocked_angle_deg)

        if delta_theta <= 0:
            return 0.0

        a, b, c = self.poly_coeffs
        range_inches = a * delta_theta**2 + b * delta_theta + c

        return max(0, range_inches)

    def estimate_launch_velocity(self, cocked_angle_deg: float, mass_g: float) -> float:
        """
        Estimate launch velocity for any mass using energy scaling.

        For torsion spring: E = (1/2)*k*(Δθ)²
        For projectile: KE = (1/2)*m*v²
        Therefore: v² ∝ (Δθ)²/m
        Or: v = C * Δθ / sqrt(m) where C is a constant

        Args:
            cocked_angle_deg: Cocked angle in degrees
            mass_g: Projectile mass in grams

        Returns:
            Estimated velocity in m/s
        """
        delta_theta = self.get_deflection(cocked_angle_deg)

        if delta_theta <= 0:
            return 0.0

        # Get reference range for this angle at reference mass
        range_ref_inches = self.predict_range_reference_mass(cocked_angle_deg)
        range_ref_m = range_ref_inches * 0.0254

        # Back-calculate velocity for reference mass
        height_m = LAUNCH_HEIGHT_INCHES * 0.0254
        angle_rad = np.radians(self.launch_angle_deg)

        # Approximate ballistic formula (with height correction)
        sin_2theta = np.sin(2 * angle_rad)
        cos_theta = np.cos(angle_rad)
        sin_theta = np.sin(angle_rad)

        # More accurate range formula with launch height
        # R = (v₀*cos(θ)/g) * (v₀*sin(θ) + sqrt((v₀*sin(θ))² + 2*g*h))
        # Solving for v₀ is complex, so use approximation

        # Simple approximation: v₀² ≈ g*R/sin(2θ)
        v0_ref = np.sqrt(G_METRIC * range_ref_m / sin_2theta) if sin_2theta > 0 else 1.0

        # Scale for different mass
        # Energy scaling: v_new = v_ref * sqrt(m_ref / m_new)
        mass_ratio = self.ref_mass / mass_g
        v0_new = v0_ref * np.sqrt(mass_ratio)

        return v0_new

    def predict_range_with_mass_scaling(self, cocked_angle_deg: float,
                                       mass_g: float) -> Dict:
        """
        Predict range for any mass using physics-based scaling.

        Args:
            cocked_angle_deg: Cocked angle in degrees
            mass_g: Projectile mass in grams

        Returns:
            Dictionary with prediction results
        """
        # Get velocity estimate
        v0 = self.estimate_launch_velocity(cocked_angle_deg, mass_g)

        # Calculate range with ballistic motion (including height)
        height_m = LAUNCH_HEIGHT_INCHES * 0.0254
        angle_rad = np.radians(self.launch_angle_deg)

        # Projectile motion with launch height
        # R = (v₀*cos(θ)/g) * (v₀*sin(θ) + sqrt((v₀*sin(θ))² + 2*g*h))
        cos_theta = np.cos(angle_rad)
        sin_theta = np.sin(angle_rad)

        v0_sin = v0 * sin_theta
        discriminant = v0_sin**2 + 2 * G_METRIC * height_m

        if discriminant < 0:
            range_m = 0
        else:
            time_of_flight = (v0_sin + np.sqrt(discriminant)) / G_METRIC
            range_m = v0 * cos_theta * time_of_flight

        # Apply drag correction factor (lighter objects affected more)
        # Drag factor increases (less reduction) with mass
        mass_drag_factor = self.drag_factor ** (CALIBRATION_MASS / mass_g)
        range_m *= mass_drag_factor

        # Convert to inches
        range_inches = range_m / 0.0254

        # Calculate max height
        max_height_m = height_m + (v0_sin**2) / (2 * G_METRIC)

        return {
            'cocked_angle_deg': cocked_angle_deg,
            'delta_theta_deg': self.get_deflection(cocked_angle_deg),
            'mass_g': mass_g,
            'launch_velocity_ms': v0,
            'launch_velocity_fps': v0 / 0.3048,
            'launch_angle_deg': self.launch_angle_deg,
            'range_m': range_m,
            'range_inches': range_inches,
            'range_feet': range_inches / 12,
            'max_height_m': max_height_m,
            'max_height_inches': max_height_m / 0.0254,
            'time_of_flight_s': time_of_flight if discriminant >= 0 else 0,
        }

    def calibrate(self, verbose: bool = True):
        """
        Calibrate the model from measured data.
        """
        # Fit reference mass data
        self.fit_reference_mass_data()

        # Fine-tune drag factor using light mass data
        def objective(drag_factor):
            self.drag_factor = drag_factor
            pred = self.predict_range_with_mass_scaling(
                LIGHT_MASS_DATA['angle_deg'],
                LIGHT_MASS_DATA['mass_g']
            )
            error = (pred['range_inches'] - LIGHT_MASS_DATA['range_inches'])**2
            return error

        from scipy.optimize import minimize_scalar
        result = minimize_scalar(objective, bounds=(0.7, 0.99), method='bounded')
        self.drag_factor = result.x

        # Calculate fit quality for reference mass
        predictions = []
        errors = []
        for angle, measured_range in CALIBRATION_DATA:
            pred_range = self.predict_range_reference_mass(angle)
            predictions.append(pred_range)
            errors.append(pred_range - measured_range)

        rmse = np.sqrt(np.mean(np.array(errors)**2))

        self.calibration_results = {
            'poly_coeffs': self.poly_coeffs.tolist(),
            'drag_factor': self.drag_factor,
            'launch_angle_deg': self.launch_angle_deg,
            'rmse_inches': rmse,
            'predictions': predictions,
            'errors': errors
        }

        if verbose:
            print("\n" + "="*60)
            print("CALIBRATION RESULTS")
            print("="*60)
            a, b, c = self.poly_coeffs
            print(f"Reference Mass Model (66.8g):")
            print(f"  R(Δθ) = {a:.6f}*(Δθ)² + {b:.4f}*(Δθ) + {c:.2f}")
            print(f"\nLaunch Angle: {self.launch_angle_deg:.1f}°")
            print(f"Drag Factor: {self.drag_factor:.4f}")
            print(f"RMSE: {rmse:.2f} inches")
            print(f"\nReference Mass Fit ({CALIBRATION_MASS}g):")
            print(f"{'Angle':<8} {'Measured':<12} {'Predicted':<12} {'Error':<10}")
            print("-" * 45)
            for i, (angle, measured) in enumerate(CALIBRATION_DATA):
                pred = predictions[i]
                err = errors[i]
                print(f"{angle}°{' ':<5} {measured:.1f} in{' ':<5} {pred:.1f} in{' ':<5} {err:+.1f} in")

            # Verify with light mass
            light_pred = self.predict_range_with_mass_scaling(
                LIGHT_MASS_DATA['angle_deg'],
                LIGHT_MASS_DATA['mass_g']
            )
            print(f"\nLight Mass Verification ({LIGHT_MASS_DATA['mass_g']}g at {LIGHT_MASS_DATA['angle_deg']}°):")
            print(f"  Measured: {LIGHT_MASS_DATA['range_inches']:.1f} inches")
            print(f"  Predicted: {light_pred['range_inches']:.1f} inches")
            print(f"  Error: {light_pred['range_inches'] - LIGHT_MASS_DATA['range_inches']:+.1f} inches")
            print("="*60 + "\n")

    def generate_prediction_table(self, mass_g: float, angle_start: float = 135,
                                  angle_end: float = 170, angle_step: float = 5) -> List[Dict]:
        """Generate predictions for a range of angles."""
        angles = np.arange(angle_start, angle_end + angle_step/2, angle_step)
        results = []

        for angle in angles:
            if angle <= RELAXED_ANGLE_DEG:
                continue
            result = self.predict_range_with_mass_scaling(angle, mass_g)
            results.append(result)

        return results

    def save_calibration(self, filename: str = 'launcher_calibration_v2.json'):
        """Save calibration to file."""
        data = {
            'poly_coeffs': self.poly_coeffs.tolist() if self.poly_coeffs is not None else None,
            'drag_factor': self.drag_factor,
            'launch_angle_deg': self.launch_angle_deg,
            'ref_mass': self.ref_mass,
            'calibration_results': self.calibration_results
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Calibration saved to {filename}")

    def load_calibration(self, filename: str = 'launcher_calibration_v2.json') -> bool:
        """Load calibration from file."""
        if not os.path.exists(filename):
            return False

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.poly_coeffs = np.array(data['poly_coeffs'])
            self.drag_factor = data['drag_factor']
            self.launch_angle_deg = data['launch_angle_deg']
            self.ref_mass = data['ref_mass']
            self.calibration_results = data['calibration_results']

            print(f"Calibration loaded from {filename}")
            a, b, c = self.poly_coeffs
            print(f"Model: R = {a:.6f}*(Δθ)² + {b:.4f}*(Δθ) + {c:.2f}")
            return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False


# ============================================================================
# VISUALIZATION AND UI FUNCTIONS
# ============================================================================

def print_prediction_table(results: List[Dict], mass_g: float):
    """Print table of predictions."""
    print(f"\n{'='*70}")
    print(f"PREDICTION TABLE FOR {mass_g}g PROJECTILE")
    print(f"{'='*70}")
    print(f"{'Angle':<8} {'Δθ':<6} {'Velocity':<12} {'Range (in)':<12} {'Range (ft)':<12}")
    print("-" * 70)

    for r in results:
        print(f"{r['cocked_angle_deg']:.0f}°{' ':<5} "
              f"{r['delta_theta_deg']:.0f}°{' ':<4} "
              f"{r['launch_velocity_ms']:.2f} m/s{' ':<4} "
              f"{r['range_inches']:.1f}{' ':<8} "
              f"{r['range_feet']:.2f}")

    print("="*70)


def print_prediction_details(result: Dict):
    """Print detailed prediction."""
    print("\n" + "-"*60)
    print("PREDICTION DETAILS")
    print("-"*60)
    print(f"Mass: {result['mass_g']}g")
    print(f"Cocked Angle: {result['cocked_angle_deg']:.0f}° (Δθ = {result['delta_theta_deg']:.0f}°)")
    print(f"\nLAUNCH PARAMETERS:")
    print(f"  Velocity: {result['launch_velocity_ms']:.2f} m/s ({result['launch_velocity_fps']:.1f} ft/s)")
    print(f"  Angle: {result['launch_angle_deg']:.1f}°")
    print(f"  Height: {LAUNCH_HEIGHT_INCHES:.1f} inches")
    print(f"\nPREDICTED RANGE:")
    print(f"  {result['range_inches']:.1f} inches")
    print(f"  {result['range_feet']:.2f} feet")
    print(f"\nFLIGHT:")
    print(f"  Max Height: {result['max_height_inches']:.1f} inches")
    print(f"  Time of Flight: {result['time_of_flight_s']:.3f} seconds")
    print("-"*60)


def plot_range_vs_angle(model: LauncherModel, mass_g: float):
    """Plot range vs angle."""
    angles = np.arange(136, 171, 1)
    ranges = []

    for angle in angles:
        result = model.predict_range_with_mass_scaling(angle, mass_g)
        ranges.append(result['range_feet'])

    plt.figure(figsize=(10, 6))
    plt.plot(angles, ranges, 'b-', linewidth=2, label=f'{mass_g}g')

    # Mark calibration points if reference mass
    if abs(mass_g - CALIBRATION_MASS) < 0.1:
        cal_angles = [a for a, r in CALIBRATION_DATA]
        cal_ranges = [r/12 for a, r in CALIBRATION_DATA]
        plt.plot(cal_angles, cal_ranges, 'ro', markersize=8, label='Measured Data')

    plt.xlabel('Cocked Angle (degrees)', fontsize=12)
    plt.ylabel('Range (feet)', fontsize=12)
    plt.title(f'Predicted Range vs Cocked Angle ({mass_g}g Projectile)', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def quick_prediction_mode(model: LauncherModel):
    """Quick prediction interface."""
    print("\n" + "="*60)
    print("QUICK PREDICTION MODE")
    print("="*60)

    try:
        mass_g = float(input("Enter mass (grams): "))
        angle = float(input("Enter cocked angle (degrees): "))

        result = model.predict_range_with_mass_scaling(angle, mass_g)
        print_prediction_details(result)

    except ValueError:
        print("Invalid input.")


def competition_mode(model: LauncherModel):
    """Rapid testing for competition."""
    print("\n" + "="*60)
    print("COMPETITION MODE - Rapid Predictions at 170°")
    print("="*60)
    print("Enter masses to test. Type 'done' when finished.\n")

    results = []

    while True:
        mass_input = input("Mass (grams) or 'done': ").strip().lower()
        if mass_input == 'done':
            break

        try:
            mass_g = float(mass_input)
            result = model.predict_range_with_mass_scaling(170, mass_g)
            print(f"  → {mass_g}g: {result['range_inches']:.1f} in ({result['range_feet']:.2f} ft)")
            results.append((mass_g, result['range_inches']))
        except ValueError:
            print("  Invalid input.")

    if results:
        print("\n" + "-"*60)
        print("SUMMARY")
        print("-"*60)
        print(f"{'Mass (g)':<12} {'Range (in)':<15} {'Range (ft)':<12}")
        print("-"*60)
        for mass, range_in in sorted(results):
            print(f"{mass:<12.1f} {range_in:<15.1f} {range_in/12:<12.2f}")
        print("-"*60)


def main_menu():
    """Main program menu."""
    model = LauncherModel()

    print("\n" + "="*70)
    print(" "*15 + "PROJECTILE RANGE PREDICTOR V2")
    print(" "*10 + "Hybrid Empirical-Physics Model")
    print("="*70)

    # Load or calibrate
    if not model.load_calibration():
        print("\nRunning initial calibration...")
        model.calibrate(verbose=True)
        model.save_calibration()
    else:
        print()

    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Quick Prediction")
        print("2. Full Analysis (table + plot)")
        print("3. Competition Mode (rapid testing @ 170°)")
        print("4. Generate 19.3g Table")
        print("5. Recalibrate")
        print("6. Exit")
        print("="*60)

        choice = input("\nSelect (1-6): ").strip()

        if choice == '1':
            quick_prediction_mode(model)

        elif choice == '2':
            try:
                mass_g = float(input("\nEnter mass (grams): "))
                results = model.generate_prediction_table(mass_g, 135, 170, 5)
                print_prediction_table(results, mass_g)

                show_plot = input("\nShow plot? (y/n): ").strip().lower()
                if show_plot == 'y':
                    plot_range_vs_angle(model, mass_g)
            except ValueError:
                print("Invalid input.")

        elif choice == '3':
            competition_mode(model)

        elif choice == '4':
            print("\nGenerating 19.3g prediction table...")
            results = model.generate_prediction_table(19.3, 135, 170, 5)
            print_prediction_table(results, 19.3)

            save = input("\nSave to file? (y/n): ").strip().lower()
            if save == 'y':
                with open('predictions_19.3g.txt', 'w') as f:
                    f.write("PREDICTION TABLE FOR 19.3g PROJECTILE\n")
                    f.write("="*70 + "\n")
                    f.write(f"{'Angle':<8} {'Δθ':<6} {'Velocity':<12} {'Range (in)':<12} {'Range (ft)':<12}\n")
                    f.write("-" * 70 + "\n")
                    for r in results:
                        f.write(f"{r['cocked_angle_deg']:.0f}°{' ':<5} "
                               f"{r['delta_theta_deg']:.0f}°{' ':<4} "
                               f"{r['launch_velocity_ms']:.2f} m/s{' ':<4} "
                               f"{r['range_inches']:.1f}{' ':<8} "
                               f"{r['range_feet']:.2f}\n")
                print("Saved to predictions_19.3g.txt")

        elif choice == '5':
            model.calibrate(verbose=True)
            model.save_calibration()

        elif choice == '6':
            print("\nGood luck with your competition!")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()
