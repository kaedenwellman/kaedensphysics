# CLAUDE.md - AI Assistant Guide for kaedensphysics

## Project Overview

**kaedensphysics** is a physics computation and simulation repository. This document provides comprehensive guidance for AI assistants working with this codebase.

### Project Status
- **Current State**: Initial setup phase
- **Primary Language**: To be determined (Python, Julia, C++, or other)
- **Purpose**: Physics simulations, calculations, and educational materials

## Repository Structure

```
kaedensphysics/
├── src/                    # Source code for physics simulations
│   ├── mechanics/         # Classical mechanics modules
│   ├── electromagnetism/  # EM field calculations
│   ├── quantum/           # Quantum mechanics simulations
│   ├── thermodynamics/    # Thermodynamic calculations
│   └── utils/             # Utility functions and helpers
├── notebooks/             # Jupyter notebooks for demonstrations
├── tests/                 # Unit and integration tests
├── docs/                  # Documentation and theory notes
├── data/                  # Input data and datasets
├── examples/              # Example scripts and use cases
├── scripts/               # Automation and build scripts
├── requirements.txt       # Python dependencies (if using Python)
├── package.json          # Node dependencies (if using JavaScript/TypeScript)
├── Cargo.toml            # Rust dependencies (if using Rust)
├── README.md             # Project documentation
└── CLAUDE.md             # This file
```

## Development Workflows

### Initial Setup

When setting up the development environment:

1. **Identify the primary language** based on project requirements
2. **Install dependencies** using the appropriate package manager
3. **Set up virtual environments** (for Python) or equivalent isolation
4. **Configure linters and formatters** for code quality

### Making Changes

1. **Always read existing code** before making modifications
2. **Run tests** before and after changes
3. **Follow physics conventions** (see below)
4. **Document equations and algorithms** with references
5. **Validate numerical accuracy** for computational changes

### Testing Strategy

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test complete simulations
- **Numerical validation**: Compare with known solutions or analytical results
- **Physical validation**: Ensure conservation laws are respected (energy, momentum, etc.)

## Key Conventions

### Physics-Specific Guidelines

#### 1. Units and Dimensions
- **Always specify units** in comments or docstrings
- **Use SI units** unless otherwise specified
- **Consider using unit libraries** (e.g., `pint` for Python, `Unitful.jl` for Julia)
- **Document unit conversions** explicitly

```python
# Good example (Python)
def calculate_kinetic_energy(mass, velocity):
    """
    Calculate kinetic energy.

    Args:
        mass (float): Mass in kilograms [kg]
        velocity (float): Velocity in meters per second [m/s]

    Returns:
        float: Kinetic energy in joules [J]
    """
    return 0.5 * mass * velocity**2
```

#### 2. Numerical Precision
- **Use appropriate data types** (float64 for most physics calculations)
- **Be aware of floating-point errors** in iterative calculations
- **Document numerical methods** (Euler, Runge-Kutta, etc.)
- **Include convergence criteria** for iterative solvers

#### 3. Physical Constants
- **Use established libraries** for physical constants (e.g., `scipy.constants`)
- **Never hardcode constants** without clear documentation
- **Specify precision** when needed for high-accuracy calculations

```python
# Good example
from scipy.constants import speed_of_light, gravitational_constant

# Bad example
c = 299792458  # What are the units? Where did this come from?
```

#### 4. Mathematical Notation
- **Use descriptive variable names** that match standard physics notation
- **Document symbols** in docstrings or comments
- **Reference equations** from textbooks or papers when applicable

```python
# Good example
def lorentz_factor(velocity, c=speed_of_light):
    """
    Calculate the Lorentz factor γ (gamma).

    γ = 1 / sqrt(1 - v²/c²)

    Reference: Jackson, "Classical Electrodynamics", 3rd ed., Eq. 11.3
    """
    beta = velocity / c
    return 1.0 / np.sqrt(1.0 - beta**2)
```

#### 5. Conservation Laws
- **Always verify** energy, momentum, and other conserved quantities
- **Include validation functions** that check conservation
- **Raise warnings** when conservation is violated beyond tolerance

### Code Quality Standards

#### Documentation
- **Every physics function** must have a docstring explaining:
  - The physical concept being calculated
  - Input parameters with units
  - Return values with units
  - Assumptions and limitations
  - References to textbooks or papers

#### Comments
- **Explain the physics**, not just the code
- **Document approximations** and their validity ranges
- **Note numerical stability concerns**

#### Error Handling
- **Validate physical constraints** (e.g., mass > 0, 0 ≤ probability ≤ 1)
- **Check for numerical issues** (division by zero, overflow)
- **Provide meaningful error messages** with physical context

```python
# Good example
if mass <= 0:
    raise ValueError(f"Mass must be positive, got {mass} kg")

if abs(velocity) >= speed_of_light:
    raise ValueError(
        f"Velocity {velocity} m/s exceeds speed of light. "
        "Use relativistic calculations."
    )
```

### Version Control

#### Commit Messages
- Use clear, descriptive commit messages
- Reference physical equations or concepts when relevant
- Format: `<type>: <description>`

Types:
- `feat`: New physics simulation or calculation
- `fix`: Bug fix in calculation or algorithm
- `docs`: Documentation updates
- `test`: Adding or updating tests
- `refactor`: Code restructuring without changing behavior
- `perf`: Performance improvements

Examples:
```
feat: Add relativistic momentum calculation
fix: Correct sign error in electric field gradient
docs: Add derivation notes for Maxwell equations solver
test: Add validation against analytical solution for harmonic oscillator
perf: Optimize matrix operations in quantum state evolution
```

#### Branch Naming
- Feature branches: `feature/<physics-topic>` (e.g., `feature/quantum-harmonic-oscillator`)
- Bug fixes: `fix/<issue-description>` (e.g., `fix/energy-conservation-violation`)
- Experiments: `experiment/<topic>` (e.g., `experiment/monte-carlo-integration`)

## Common Physics Patterns

### 1. Simulation Structure

```python
class PhysicsSimulation:
    """Base class for physics simulations."""

    def __init__(self, initial_conditions, parameters):
        """Initialize simulation with initial conditions and parameters."""
        self.state = initial_conditions
        self.params = parameters
        self.time = 0.0
        self.history = []

    def step(self, dt):
        """Advance simulation by one time step dt."""
        raise NotImplementedError

    def run(self, total_time, dt):
        """Run simulation for total_time with time step dt."""
        steps = int(total_time / dt)
        for _ in range(steps):
            self.step(dt)
            self.history.append(self.state.copy())
            self.time += dt
        return self.history

    def validate(self):
        """Validate physical constraints (conservation laws, etc.)."""
        raise NotImplementedError
```

### 2. Vector and Tensor Operations
- **Use established libraries** (NumPy, SymPy, Eigen, etc.)
- **Avoid manual indexing** when library functions are available
- **Document coordinate systems** (Cartesian, spherical, etc.)

### 3. Differential Equations
- **State the order** of the differential equation
- **Document the method** used (Euler, RK4, etc.)
- **Include stability analysis** for complex systems

## Testing Guidelines

### Unit Tests
```python
def test_kinetic_energy_at_rest():
    """Test that kinetic energy is zero when velocity is zero."""
    mass = 1.0  # kg
    velocity = 0.0  # m/s
    expected = 0.0  # J
    assert calculate_kinetic_energy(mass, velocity) == expected

def test_energy_conservation_in_free_fall():
    """Test that total energy is conserved during free fall."""
    sim = FreeFallSimulation(height=10.0)  # meters
    sim.run(time=1.5, dt=0.01)  # seconds

    initial_energy = sim.history[0].total_energy()
    final_energy = sim.history[-1].total_energy()

    assert abs(final_energy - initial_energy) < 1e-6  # Joules
```

### Validation Tests
- **Compare with analytical solutions** when available
- **Test limiting cases** (classical limit, non-relativistic limit, etc.)
- **Verify dimensional analysis**
- **Check symmetries** (rotational invariance, time reversal, etc.)

## Performance Considerations

### Optimization Guidelines
1. **Profile before optimizing** - identify actual bottlenecks
2. **Vectorize operations** using NumPy/similar libraries
3. **Consider parallelization** for independent calculations
4. **Use compiled extensions** (Cython, Numba, C++) for critical loops
5. **Cache expensive calculations** when appropriate

### Memory Management
- **Be mindful of large arrays** in simulations
- **Use generators** for large datasets when possible
- **Clear history periodically** in long-running simulations

## Dependencies and Tools

### Recommended Python Libraries
- **NumPy**: Numerical arrays and operations
- **SciPy**: Scientific computing, ODE solvers, constants
- **SymPy**: Symbolic mathematics
- **Matplotlib**: Plotting and visualization
- **Jupyter**: Interactive notebooks
- **pytest**: Testing framework
- **Black**: Code formatting
- **pylint/flake8**: Code linting

### Recommended Julia Libraries
- **DifferentialEquations.jl**: ODE/PDE solving
- **Plots.jl**: Visualization
- **Unitful.jl**: Physical units
- **StaticArrays.jl**: Fast small arrays

### Recommended C++ Libraries
- **Eigen**: Linear algebra
- **Boost**: Various utilities
- **GSL**: GNU Scientific Library

## Documentation Requirements

### Code Documentation
- **All functions**: Must have docstrings/comments
- **All classes**: Must document purpose and usage
- **Complex algorithms**: Must include derivation notes or references

### External Documentation
- **README.md**: Project overview and quick start
- **Theory notes**: Mathematical derivations in `docs/`
- **Examples**: Well-commented example scripts
- **API reference**: Auto-generated from docstrings

## AI Assistant Guidelines

### When Reading Code
1. **Understand the physics first** before suggesting code changes
2. **Check units** in all calculations
3. **Verify mathematical correctness** of equations
4. **Look for conservation law violations**
5. **Check boundary conditions** and initial conditions

### When Writing Code
1. **Never modify physics equations** without understanding them
2. **Always include units** in documentation
3. **Add validation tests** for physical correctness
4. **Reference sources** for equations and algorithms
5. **Consider numerical stability** of methods
6. **Avoid over-engineering** - keep it simple and clear

### When Debugging
1. **Check dimensional analysis** first
2. **Verify limiting cases** (e.g., v→0, c→∞)
3. **Plot intermediate results** to identify issues
4. **Check for numerical instabilities**
5. **Validate conservation laws**

### Red Flags to Watch For
- Hardcoded physical constants without units or references
- Missing validation of input constraints (e.g., negative mass)
- Lack of references for complex equations
- Numerical methods without stability analysis
- Missing error propagation in measurements
- Unitless calculations where units matter
- Violation of conservation laws without justification

## Common Commands

### Python Projects
```bash
# Setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Testing
pytest tests/
pytest tests/ -v  # Verbose output
pytest tests/ --cov=src  # With coverage

# Linting and formatting
black src/
flake8 src/
pylint src/

# Running simulations
python examples/example_simulation.py

# Jupyter notebooks
jupyter notebook
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-simulation

# Regular workflow
git add <files>
git commit -m "feat: Add new simulation"
git push -u origin feature/new-simulation

# Keep branch updated
git fetch origin
git rebase origin/main
```

## Resources and References

### Classic Textbooks
- Griffiths, "Introduction to Quantum Mechanics"
- Goldstein, "Classical Mechanics"
- Jackson, "Classical Electrodynamics"
- Landau & Lifshitz, "Course of Theoretical Physics" series

### Numerical Methods
- Press et al., "Numerical Recipes"
- Hairer et al., "Solving Ordinary Differential Equations"

### Online Resources
- [arXiv.org](https://arxiv.org) - Physics preprints
- [SciPy Documentation](https://docs.scipy.org)
- [NumPy Documentation](https://numpy.org/doc/)

## Project-Specific Notes

### Current Focus Areas
- TBD based on initial implementation

### Known Limitations
- TBD as project develops

### Future Enhancements
- TBD based on requirements

---

**Last Updated**: 2025-12-16
**Repository**: kaedenwellman/kaedensphysics
**Maintained By**: Kaeden Wellman

---

## Changelog

### 2025-12-16
- Initial creation of CLAUDE.md
- Established project structure and conventions
- Added comprehensive guidelines for physics calculations
