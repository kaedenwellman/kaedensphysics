#!/usr/bin/env python3
"""
Projectile Range Predictor for Torsion Spring Launcher
Physics Extra Credit Project

This program predicts landing distances for projectiles launched from a
mousetrap-style torsion spring catapult, accounting for mass variations
and air resistance effects.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, fsolve
from scipy.integrate import odeint
import json
import os
from typing import Tuple, Dict, List, Optional


# ============================================================================
# LAUNCHER SPECIFICATIONS (Constants)
# ============================================================================

LEVER_ARM_INCHES = 9.2          # Distance from pivot to projectile cup
LAUNCH_HEIGHT_INCHES = 11.0     # Center of ball at release above ground
RELAXED_ANGLE_DEG = 135.0       # Natural arm position from horizontal
ARM_VERTICAL_AT_DEG = 90.0      # When arm is straight up

# Convert to SI units (meters)
LEVER_ARM = LEVER_ARM_INCHES * 0.0254  # 0.23368 m
LAUNCH_HEIGHT = LAUNCH_HEIGHT_INCHES * 0.0254  # 0.2794 m

# Physical constants
G = 9.81  # Gravity (m/s²)
AIR_DENSITY = 1.225  # kg/m³ at sea level


# ============================================================================
# CALIBRATION DATA
# ============================================================================

# Primary calibration mass (grams) and its range measurements
CALIBRATION_MASS = 66.8  # grams

# Format: (cocked_angle_deg, range_inches)
CALIBRATION_DATA = [
    (155, 50),   # Δθ = 20°
    (165, 78),   # Δθ = 30°
    (170, 93),   # Δθ = 35°
]

# Additional mass data point for drag calibration
LIGHT_MASS_DATA = {
    'mass_g': 12.5,
    'cocked_angle_deg': 170,
    'range_inches': 180
}


# ============================================================================
# PHYSICS MODEL CLASS
# ============================================================================

class TorsionSpringLauncher:
    """
    Models the physics of a torsion spring launcher.

    The launcher stores energy as: E = (1/2) * k_torsion * (Δθ)²
    where Δθ is the angular deflection from the relaxed position.
    """

    def __init__(self):
        """Initialize launcher with default parameters."""
        self.k_torsion = None  # Torsion spring constant (N⋅m/rad²)
        self.launch_angle_deg = None  # Calibrated effective launch angle
        self.drag_coefficient = 0.47  # Sphere drag coefficient
        self.projectile_diameter_m = 0.025  # Estimated 25mm diameter (ping pong ball size)
        self.energy_efficiency = 0.7  # Mechanical efficiency factor
        self.calibration_results = {}

    def get_spring_deflection(self, cocked_angle_deg: float) -> float:
        """
        Calculate spring deflection angle.

        Args:
            cocked_angle_deg: Cocked arm angle in degrees

        Returns:
            Deflection angle Δθ in degrees
        """
        return cocked_angle_deg - RELAXED_ANGLE_DEG

    def calculate_launch_angle(self, cocked_angle_deg: float) -> float:
        """
        Calculate actual launch angle from arm geometry.

        For this launcher, the effective launch angle is relatively constant
        and is calibrated from experimental data. The arm releases the projectile
        at an optimal angle for range.

        Args:
            cocked_angle_deg: Cocked arm angle from horizontal

        Returns:
            Launch angle in degrees from horizontal
        """
        # Use calibrated launch angle if available, otherwise estimate
        if self.launch_angle_deg is not None:
            return self.launch_angle_deg

        # Default estimate for optimal range (typically 40-45° for projectile motion)
        # Torsion spring launchers tend to release around 50-60° due to arm geometry
        return 55.0

    def calculate_stored_energy(self, cocked_angle_deg: float) -> float:
        """
        Calculate energy stored in torsion spring.

        Args:
            cocked_angle_deg: Cocked arm angle in degrees

        Returns:
            Stored energy in Joules
        """
        if self.k_torsion is None:
            raise ValueError("Spring constant not calibrated. Run calibration first.")

        delta_theta_deg = self.get_spring_deflection(cocked_angle_deg)
        delta_theta_rad = np.radians(delta_theta_deg)

        # E = (1/2) * k * (Δθ)²
        energy = 0.5 * self.k_torsion * delta_theta_rad**2

        return energy

    def calculate_launch_velocity_no_drag(self, cocked_angle_deg: float,
                                         mass_g: float) -> float:
        """
        Calculate launch velocity assuming no energy losses.

        Args:
            cocked_angle_deg: Cocked arm angle in degrees
            mass_g: Projectile mass in grams

        Returns:
            Launch velocity in m/s
        """
        energy = self.calculate_stored_energy(cocked_angle_deg)
        mass_kg = mass_g / 1000.0

        # (1/2) * m * v² = E
        # v = sqrt(2E/m)
        velocity = np.sqrt(2 * energy / mass_kg)

        return velocity

    def trajectory_with_drag(self, v0: float, angle_deg: float, mass_g: float,
                            t_max: float = 5.0, dt: float = 0.001) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate trajectory with air resistance using numerical integration.

        Args:
            v0: Initial velocity (m/s)
            angle_deg: Launch angle (degrees from horizontal)
            mass_g: Projectile mass (grams)
            t_max: Maximum simulation time (seconds)
            dt: Time step (seconds)

        Returns:
            Tuple of (time_array, x_array, y_array) in SI units
        """
        mass_kg = mass_g / 1000.0
        angle_rad = np.radians(angle_deg)

        # Projectile cross-sectional area (assume sphere)
        area = np.pi * (self.projectile_diameter_m / 2)**2

        # Drag force coefficient: F_drag = (1/2) * ρ * Cd * A * v²
        k_drag = 0.5 * AIR_DENSITY * self.drag_coefficient * area

        def derivatives(state, t):
            """
            Calculate derivatives for ODE solver.
            state = [x, y, vx, vy]
            """
            x, y, vx, vy = state

            # Velocity magnitude
            v = np.sqrt(vx**2 + vy**2)

            # Drag force (opposes velocity)
            if v > 0:
                F_drag = k_drag * v**2
                ax = -(F_drag / mass_kg) * (vx / v)
                ay = -G - (F_drag / mass_kg) * (vy / v)
            else:
                ax = 0
                ay = -G

            return [vx, vy, ax, ay]

        # Initial conditions
        vx0 = v0 * np.cos(angle_rad)
        vy0 = v0 * np.sin(angle_rad)
        state0 = [0, LAUNCH_HEIGHT, vx0, vy0]

        # Time array
        t = np.arange(0, t_max, dt)

        # Solve ODE
        solution = odeint(derivatives, state0, t)

        x = solution[:, 0]
        y = solution[:, 1]

        # Find where projectile hits ground (y = 0)
        ground_idx = np.where(y <= 0)[0]
        if len(ground_idx) > 0:
            idx = ground_idx[0]
            t = t[:idx+1]
            x = x[:idx+1]
            y = y[:idx+1]

        return t, x, y

    def predict_range_with_drag(self, cocked_angle_deg: float, mass_g: float) -> Dict:
        """
        Predict landing range including air resistance effects.

        Args:
            cocked_angle_deg: Cocked arm angle in degrees
            mass_g: Projectile mass in grams

        Returns:
            Dictionary with prediction results
        """
        # Calculate launch parameters
        v0 = self.calculate_launch_velocity_no_drag(cocked_angle_deg, mass_g)
        launch_angle = self.calculate_launch_angle(cocked_angle_deg)

        # Simulate trajectory with drag
        t, x, y = self.trajectory_with_drag(v0, launch_angle, mass_g)

        # Extract results
        range_m = x[-1]
        range_inches = range_m / 0.0254
        max_height_m = np.max(y)
        time_of_flight = t[-1]

        return {
            'range_m': range_m,
            'range_inches': range_inches,
            'range_feet': range_inches / 12,
            'launch_velocity_ms': v0,
            'launch_velocity_fps': v0 / 0.3048,
            'launch_angle_deg': launch_angle,
            'max_height_m': max_height_m,
            'max_height_inches': max_height_m / 0.0254,
            'time_of_flight_s': time_of_flight,
            'trajectory': (t, x, y)
        }

    def calibrate_from_data(self, verbose: bool = True) -> Dict:
        """
        Calibrate spring constant and launch parameters from measured range data.

        Uses the three calibration shots with 66.8g mass to determine
        the torsion spring constant and effective launch angle that best
        matches observed ranges. Also calibrates drag using 12.5g data.

        Args:
            verbose: Print calibration results

        Returns:
            Dictionary with calibration results
        """
        def objective(params):
            """
            Objective function: sum of squared errors between predicted
            and measured ranges for both calibration masses.
            """
            k_torsion, launch_angle, drag_coeff = params
            self.k_torsion = k_torsion
            self.launch_angle_deg = launch_angle
            self.drag_coefficient = drag_coeff

            total_error = 0

            # Weight the primary calibration data more heavily
            for cocked_angle, measured_range in CALIBRATION_DATA:
                predicted = self.predict_range_with_drag(cocked_angle, CALIBRATION_MASS)
                error = (predicted['range_inches'] - measured_range)**2
                total_error += error * 3.0  # Weight factor

            # Include light mass data point
            light_pred = self.predict_range_with_drag(
                LIGHT_MASS_DATA['cocked_angle_deg'],
                LIGHT_MASS_DATA['mass_g']
            )
            error = (light_pred['range_inches'] - LIGHT_MASS_DATA['range_inches'])**2
            total_error += error

            return total_error

        # Initial guesses
        k_initial = 8.0  # N⋅m/rad²
        angle_initial = 50.0  # degrees
        drag_initial = 0.5

        # Optimize with bounds
        from scipy.optimize import minimize
        result = minimize(
            objective,
            [k_initial, angle_initial, drag_initial],
            bounds=[(0.5, 30), (35, 65), (0.3, 0.8)],
            method='L-BFGS-B'
        )

        self.k_torsion = result.x[0]
        self.launch_angle_deg = result.x[1]
        self.drag_coefficient = result.x[2]

        # Calculate fit quality
        predictions = []
        errors = []
        for cocked_angle, measured_range in CALIBRATION_DATA:
            pred = self.predict_range_with_drag(cocked_angle, CALIBRATION_MASS)
            predictions.append(pred['range_inches'])
            errors.append(pred['range_inches'] - measured_range)

        rmse = np.sqrt(np.mean(np.array(errors)**2))

        self.calibration_results = {
            'k_torsion': self.k_torsion,
            'launch_angle_deg': self.launch_angle_deg,
            'drag_coefficient': self.drag_coefficient,
            'rmse_inches': rmse,
            'predictions': predictions,
            'errors': errors,
            'calibration_mass_g': CALIBRATION_MASS
        }

        if verbose:
            print("\n" + "="*60)
            print("CALIBRATION RESULTS")
            print("="*60)
            print(f"Spring Constant: k = {self.k_torsion:.4f} N⋅m/rad²")
            print(f"Launch Angle: θ = {self.launch_angle_deg:.2f}°")
            print(f"Drag Coefficient: Cd = {self.drag_coefficient:.3f}")
            print(f"Projectile Diameter: {self.projectile_diameter_m*1000:.1f} mm")
            print(f"RMSE: {rmse:.2f} inches")
            print(f"\nCalibration Mass: {CALIBRATION_MASS} g")
            print("\nFit Quality:")
            print(f"{'Angle':<8} {'Measured':<12} {'Predicted':<12} {'Error':<10}")
            print("-" * 45)
            for i, (angle, measured) in enumerate(CALIBRATION_DATA):
                pred = predictions[i]
                err = errors[i]
                print(f"{angle}°{' ':<5} {measured:.1f} in{' ':<5} {pred:.1f} in{' ':<5} {err:+.1f} in")

        # Verify with light mass data
        light_pred = self.predict_range_with_drag(
            LIGHT_MASS_DATA['cocked_angle_deg'],
            LIGHT_MASS_DATA['mass_g']
        )

        if verbose:
            print(f"\nLight Mass Verification ({LIGHT_MASS_DATA['mass_g']} g at {LIGHT_MASS_DATA['cocked_angle_deg']}°):")
            print(f"  Measured: {LIGHT_MASS_DATA['range_inches']:.1f} inches")
            print(f"  Predicted: {light_pred['range_inches']:.1f} inches")
            print(f"  Error: {light_pred['range_inches'] - LIGHT_MASS_DATA['range_inches']:+.1f} inches")
            print("="*60 + "\n")

        return self.calibration_results

    def generate_prediction_table(self, mass_g: float,
                                  angle_start: float = 135,
                                  angle_end: float = 170,
                                  angle_step: float = 5) -> List[Dict]:
        """
        Generate predictions for a range of cocking angles.

        Args:
            mass_g: Projectile mass in grams
            angle_start: Starting cocked angle
            angle_end: Ending cocked angle
            angle_step: Angle increment

        Returns:
            List of prediction dictionaries
        """
        angles = np.arange(angle_start, angle_end + angle_step/2, angle_step)
        results = []

        for angle in angles:
            if angle <= RELAXED_ANGLE_DEG:
                continue  # Skip angles at or below relaxed position

            pred = self.predict_range_with_drag(angle, mass_g)
            pred['cocked_angle_deg'] = angle
            pred['delta_theta_deg'] = angle - RELAXED_ANGLE_DEG
            results.append(pred)

        return results

    def save_calibration(self, filename: str = 'launcher_calibration.json'):
        """Save calibration data to file."""
        if self.k_torsion is None:
            print("No calibration data to save. Run calibration first.")
            return

        data = {
            'k_torsion': self.k_torsion,
            'launch_angle_deg': self.launch_angle_deg,
            'drag_coefficient': self.drag_coefficient,
            'projectile_diameter_m': self.projectile_diameter_m,
            'energy_efficiency': self.energy_efficiency,
            'calibration_results': self.calibration_results
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Calibration saved to {filename}")

    def load_calibration(self, filename: str = 'launcher_calibration.json') -> bool:
        """
        Load calibration data from file.

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(filename):
            return False

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.k_torsion = data['k_torsion']
            self.launch_angle_deg = data.get('launch_angle_deg', 50.0)
            self.drag_coefficient = data['drag_coefficient']
            self.projectile_diameter_m = data['projectile_diameter_m']
            self.energy_efficiency = data.get('energy_efficiency', 0.7)
            self.calibration_results = data.get('calibration_results', {})

            print(f"Calibration loaded from {filename}")
            print(f"Spring constant: k = {self.k_torsion:.4f} N⋅m/rad²")
            print(f"Launch angle: θ = {self.launch_angle_deg:.2f}°")
            return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_trajectory(launcher: TorsionSpringLauncher, cocked_angle_deg: float,
                   mass_g: float, save_fig: bool = False):
    """
    Plot projectile trajectory.

    Args:
        launcher: TorsionSpringLauncher instance
        cocked_angle_deg: Cocked arm angle
        mass_g: Projectile mass
        save_fig: Save figure to file
    """
    result = launcher.predict_range_with_drag(cocked_angle_deg, mass_g)
    t, x, y = result['trajectory']

    # Convert to inches for display
    x_inches = x / 0.0254
    y_inches = y / 0.0254

    plt.figure(figsize=(12, 6))
    plt.plot(x_inches, y_inches, 'b-', linewidth=2, label='Trajectory')
    plt.axhline(y=0, color='brown', linestyle='--', linewidth=1, label='Ground')
    plt.axhline(y=LAUNCH_HEIGHT_INCHES, color='gray', linestyle=':',
                linewidth=1, alpha=0.5, label='Launch Height')

    # Mark landing point
    plt.plot(result['range_inches'], 0, 'ro', markersize=10, label='Landing')

    plt.xlabel('Horizontal Distance (inches)', fontsize=12)
    plt.ylabel('Height (inches)', fontsize=12)
    plt.title(f'Projectile Trajectory: {mass_g}g at {cocked_angle_deg}° '
              f'(Range: {result["range_inches"]:.1f} in = {result["range_feet"]:.2f} ft)',
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right')
    plt.tight_layout()

    if save_fig:
        plt.savefig(f'trajectory_{mass_g}g_{cocked_angle_deg}deg.png', dpi=150)
        print(f"Trajectory plot saved to trajectory_{mass_g}g_{cocked_angle_deg}deg.png")

    plt.show()


def plot_range_vs_angle(launcher: TorsionSpringLauncher, mass_g: float,
                       save_fig: bool = False):
    """
    Plot range vs cocked angle.

    Args:
        launcher: TorsionSpringLauncher instance
        mass_g: Projectile mass
        save_fig: Save figure to file
    """
    angles = np.arange(135, 171, 1)
    ranges_inches = []

    for angle in angles:
        if angle <= RELAXED_ANGLE_DEG:
            ranges_inches.append(0)
        else:
            result = launcher.predict_range_with_drag(angle, mass_g)
            ranges_inches.append(result['range_inches'])

    ranges_feet = np.array(ranges_inches) / 12

    plt.figure(figsize=(10, 6))
    plt.plot(angles, ranges_feet, 'b-', linewidth=2, label=f'{mass_g}g projectile')

    # Mark calibration points if this is calibration mass
    if abs(mass_g - CALIBRATION_MASS) < 0.1:
        cal_angles = [a for a, r in CALIBRATION_DATA]
        cal_ranges = [r/12 for a, r in CALIBRATION_DATA]
        plt.plot(cal_angles, cal_ranges, 'ro', markersize=8,
                label='Calibration Data', zorder=5)

    plt.xlabel('Cocked Arm Angle (degrees)', fontsize=12)
    plt.ylabel('Range (feet)', fontsize=12)
    plt.title(f'Predicted Range vs Cocked Angle for {mass_g}g Projectile',
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    if save_fig:
        plt.savefig(f'range_vs_angle_{mass_g}g.png', dpi=150)
        print(f"Range plot saved to range_vs_angle_{mass_g}g.png")

    plt.show()


# ============================================================================
# USER INTERFACE FUNCTIONS
# ============================================================================

def print_header():
    """Print program header."""
    print("\n" + "="*70)
    print(" "*15 + "PROJECTILE RANGE PREDICTOR")
    print(" "*10 + "Torsion Spring Launcher Physics Model")
    print("="*70)


def print_prediction_details(result: Dict):
    """Print detailed prediction results."""
    print("\n" + "-"*60)
    print("PREDICTION RESULTS")
    print("-"*60)
    print(f"Cocked Angle: {result['cocked_angle_deg']:.0f}°  "
          f"(Δθ = {result['delta_theta_deg']:.0f}°)")
    print(f"\nLAUNCH PARAMETERS:")
    print(f"  Velocity: {result['launch_velocity_ms']:.2f} m/s "
          f"({result['launch_velocity_fps']:.1f} ft/s)")
    print(f"  Angle: {result['launch_angle_deg']:.1f}° from horizontal")
    print(f"  Height: {LAUNCH_HEIGHT_INCHES:.1f} inches above ground")
    print(f"\nFLIGHT CHARACTERISTICS:")
    print(f"  Maximum Height: {result['max_height_inches']:.1f} inches "
          f"({result['max_height_inches']/12:.2f} ft)")
    print(f"  Time of Flight: {result['time_of_flight_s']:.3f} seconds")
    print(f"\nPREDICTED RANGE:")
    print(f"  {result['range_inches']:.1f} inches")
    print(f"  {result['range_feet']:.2f} feet")
    print("-"*60)


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


def quick_prediction_mode(launcher: TorsionSpringLauncher):
    """Quick prediction: enter mass and angle, get range."""
    print("\n" + "="*60)
    print("QUICK PREDICTION MODE")
    print("="*60)

    try:
        mass_g = float(input("Enter projectile mass (grams): "))
        angle = float(input("Enter cocked arm angle (degrees): "))

        if angle <= RELAXED_ANGLE_DEG:
            print(f"\nError: Cocked angle must be greater than {RELAXED_ANGLE_DEG}°")
            return

        result = launcher.predict_range_with_drag(angle, mass_g)
        result['cocked_angle_deg'] = angle
        result['delta_theta_deg'] = angle - RELAXED_ANGLE_DEG

        print_prediction_details(result)

        # Ask if user wants visualization
        show_plot = input("\nShow trajectory plot? (y/n): ").strip().lower()
        if show_plot == 'y':
            plot_trajectory(launcher, angle, mass_g)

    except ValueError:
        print("\nInvalid input. Please enter numeric values.")
    except Exception as e:
        print(f"\nError: {e}")


def competition_mode(launcher: TorsionSpringLauncher):
    """Competition mode: rapid predictions for multiple masses."""
    print("\n" + "="*60)
    print("COMPETITION MODE - Rapid Testing")
    print("="*60)
    print("Enter multiple masses to test. Type 'done' when finished.")
    print("(All predictions at maximum angle: 170°)")
    print()

    masses_tested = []

    while True:
        mass_input = input("Enter mass (grams) or 'done': ").strip().lower()

        if mass_input == 'done':
            break

        try:
            mass_g = float(mass_input)
            result = launcher.predict_range_with_drag(170, mass_g)

            print(f"  → {mass_g}g: {result['range_inches']:.1f} in "
                  f"({result['range_feet']:.2f} ft)")

            masses_tested.append((mass_g, result['range_inches']))

        except ValueError:
            print("  Invalid input, please enter a number.")

    if masses_tested:
        print("\n" + "-"*60)
        print("COMPETITION SUMMARY (at 170° max angle)")
        print("-"*60)
        print(f"{'Mass (g)':<12} {'Range (inches)':<18} {'Range (feet)':<15}")
        print("-"*60)
        for mass, range_in in sorted(masses_tested):
            print(f"{mass:<12.1f} {range_in:<18.1f} {range_in/12:<15.2f}")
        print("-"*60)


def full_analysis_mode(launcher: TorsionSpringLauncher):
    """Full analysis with table and plots."""
    print("\n" + "="*60)
    print("FULL ANALYSIS MODE")
    print("="*60)

    try:
        mass_g = float(input("Enter projectile mass (grams): "))

        print(f"\nGenerating predictions for {mass_g}g projectile...")

        # Generate table (135° to 170° in 5° steps)
        results = launcher.generate_prediction_table(mass_g, 135, 170, 5)
        print_prediction_table(results, mass_g)

        # Ask about plots
        show_plots = input("\nGenerate plots? (y/n): ").strip().lower()
        if show_plots == 'y':
            plot_range_vs_angle(launcher, mass_g)

            # Pick a representative angle for trajectory
            angle = float(input("\nEnter angle for trajectory plot (e.g., 165): "))
            plot_trajectory(launcher, angle, mass_g)

    except ValueError:
        print("\nInvalid input.")
    except Exception as e:
        print(f"\nError: {e}")


def main_menu():
    """Main program menu."""
    launcher = TorsionSpringLauncher()

    print_header()

    # Try to load existing calibration
    if not launcher.load_calibration():
        print("\nNo existing calibration found. Running initial calibration...")
        launcher.calibrate_from_data(verbose=True)
        launcher.save_calibration()
    else:
        print()

    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Quick Prediction (enter mass and angle)")
        print("2. Full Analysis (prediction table + plots)")
        print("3. Competition Mode (rapid multiple-mass testing)")
        print("4. Recalibrate System")
        print("5. Generate 19.3g Prediction Table")
        print("6. Exit")
        print("="*60)

        choice = input("\nSelect option (1-6): ").strip()

        if choice == '1':
            quick_prediction_mode(launcher)

        elif choice == '2':
            full_analysis_mode(launcher)

        elif choice == '3':
            competition_mode(launcher)

        elif choice == '4':
            print("\nRecalibrating...")
            launcher.calibrate_from_data(verbose=True)
            launcher.save_calibration()

        elif choice == '5':
            # Generate 19.3g table as requested
            print("\nGenerating prediction table for 19.3g projectiles...")
            results = launcher.generate_prediction_table(19.3, 135, 170, 5)
            print_prediction_table(results, 19.3)

            save = input("\nSave to file? (y/n): ").strip().lower()
            if save == 'y':
                with open('predictions_19.3g.txt', 'w') as f:
                    f.write("PREDICTION TABLE FOR 19.3g PROJECTILE\n")
                    f.write("="*70 + "\n")
                    f.write(f"{'Angle':<8} {'Δθ':<6} {'Velocity':<12} "
                           f"{'Range (in)':<12} {'Range (ft)':<12}\n")
                    f.write("-" * 70 + "\n")
                    for r in results:
                        f.write(f"{r['cocked_angle_deg']:.0f}°{' ':<5} "
                               f"{r['delta_theta_deg']:.0f}°{' ':<4} "
                               f"{r['launch_velocity_ms']:.2f} m/s{' ':<4} "
                               f"{r['range_inches']:.1f}{' ':<8} "
                               f"{r['range_feet']:.2f}\n")
                print("Predictions saved to predictions_19.3g.txt")

        elif choice == '6':
            print("\nExiting program. Good luck with your competition!")
            break

        else:
            print("\nInvalid choice. Please select 1-6.")


# ============================================================================
# MAIN PROGRAM ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main_menu()
