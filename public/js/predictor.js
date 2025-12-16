/**
 * Projectile Range Predictor - JavaScript Implementation
 * Ported from Python hybrid empirical-physics model
 */

// Constants
const LAUNCHER = {
    LEVER_ARM_INCHES: 9.2,
    LAUNCH_HEIGHT_INCHES: 11.0,
    RELAXED_ANGLE_DEG: 135.0,
    LAUNCH_ANGLE_DEG: 55.0,  // Calibrated effective launch angle
    DRAG_FACTOR: 0.8246,      // Calibrated drag correction factor
    REF_MASS: 66.8,           // Reference calibration mass (grams)
    G_METRIC: 9.81,           // Gravity (m/s²)
    INCHES_TO_METERS: 0.0254
};

// Polynomial coefficients for reference mass (66.8g)
// R(Δθ) = a*(Δθ)² + b*(Δθ) + c
const POLY_COEFFS = {
    a: 0.013333333,
    b: 2.133333333,
    c: 2.0
};

/**
 * Calculate spring deflection angle
 */
function getDeflection(cockedAngleDeg) {
    return cockedAngleDeg - LAUNCHER.RELAXED_ANGLE_DEG;
}

/**
 * Predict range for reference mass (66.8g) using empirical polynomial
 */
function predictRangeReferenceMass(cockedAngleDeg) {
    const deltaTheta = getDeflection(cockedAngleDeg);

    if (deltaTheta <= 0) return 0;

    const range = POLY_COEFFS.a * deltaTheta * deltaTheta +
                  POLY_COEFFS.b * deltaTheta +
                  POLY_COEFFS.c;

    return Math.max(0, range);
}

/**
 * Estimate launch velocity for any mass using energy scaling
 */
function estimateLaunchVelocity(cockedAngleDeg, massGrams) {
    // Get reference range at this angle
    const rangeRefInches = predictRangeReferenceMass(cockedAngleDeg);
    const rangeRefMeters = rangeRefInches * LAUNCHER.INCHES_TO_METERS;

    // Convert to radians
    const angleRad = LAUNCHER.LAUNCH_ANGLE_DEG * Math.PI / 180;
    const heightMeters = LAUNCHER.LAUNCH_HEIGHT_INCHES * LAUNCHER.INCHES_TO_METERS;

    // Back-calculate velocity for reference mass using ballistic formula
    // Approximation: v₀² ≈ g*R/sin(2θ)
    const sin2Theta = Math.sin(2 * angleRad);
    const v0Ref = sin2Theta > 0 ? Math.sqrt(LAUNCHER.G_METRIC * rangeRefMeters / sin2Theta) : 1.0;

    // Scale for different mass using energy conservation
    // v_new = v_ref * sqrt(m_ref / m_new)
    const massRatio = LAUNCHER.REF_MASS / massGrams;
    const v0New = v0Ref * Math.sqrt(massRatio);

    return v0New;
}

/**
 * Predict range for any mass using physics-based scaling
 */
function predictRange(cockedAngleDeg, massGrams) {
    const deltaTheta = getDeflection(cockedAngleDeg);

    if (deltaTheta <= 0) {
        return {
            cockedAngle: cockedAngleDeg,
            deltaTheta: deltaTheta,
            mass: massGrams,
            velocity: 0,
            velocityFps: 0,
            velocityKmh: 0,
            rangeMeters: 0,
            rangeCentimeters: 0,
            rangeInches: 0,
            rangeFeet: 0,
            maxHeightMeters: 0,
            maxHeightCentimeters: 0,
            maxHeightInches: 0,
            timeOfFlight: 0
        };
    }

    // Get launch velocity
    const v0 = estimateLaunchVelocity(cockedAngleDeg, massGrams);

    // Calculate range with ballistic motion including launch height
    const angleRad = LAUNCHER.LAUNCH_ANGLE_DEG * Math.PI / 180;
    const heightMeters = LAUNCHER.LAUNCH_HEIGHT_INCHES * LAUNCHER.INCHES_TO_METERS;

    const cosTheta = Math.cos(angleRad);
    const sinTheta = Math.sin(angleRad);
    const v0Sin = v0 * sinTheta;

    // Projectile motion with launch height
    // R = (v₀*cos(θ)/g) * (v₀*sin(θ) + sqrt((v₀*sin(θ))² + 2*g*h))
    const discriminant = v0Sin * v0Sin + 2 * LAUNCHER.G_METRIC * heightMeters;

    let rangeMeters = 0;
    let timeOfFlight = 0;

    if (discriminant >= 0) {
        timeOfFlight = (v0Sin + Math.sqrt(discriminant)) / LAUNCHER.G_METRIC;
        rangeMeters = v0 * cosTheta * timeOfFlight;
    }

    // Apply drag correction (lighter objects affected more)
    const massDragFactor = Math.pow(LAUNCHER.DRAG_FACTOR, LAUNCHER.REF_MASS / massGrams);
    rangeMeters *= massDragFactor;

    // Convert to inches
    const rangeInches = rangeMeters / LAUNCHER.INCHES_TO_METERS;

    // Calculate max height
    const maxHeightMeters = heightMeters + (v0Sin * v0Sin) / (2 * LAUNCHER.G_METRIC);

    return {
        cockedAngle: cockedAngleDeg,
        deltaTheta: deltaTheta,
        mass: massGrams,
        velocity: v0,
        velocityFps: v0 / 0.3048,
        velocityKmh: v0 * 3.6,
        rangeMeters: rangeMeters,
        rangeCentimeters: rangeMeters * 100,
        rangeInches: rangeInches,
        rangeFeet: rangeInches / 12,
        maxHeightMeters: maxHeightMeters,
        maxHeightCentimeters: maxHeightMeters * 100,
        maxHeightInches: maxHeightMeters / LAUNCHER.INCHES_TO_METERS,
        timeOfFlight: timeOfFlight
    };
}

/**
 * Generate prediction table for a range of angles
 */
function generatePredictionTable(massGrams, startAngle, endAngle, step) {
    const results = [];

    for (let angle = startAngle; angle <= endAngle; angle += step) {
        if (angle <= LAUNCHER.RELAXED_ANGLE_DEG) continue;

        const prediction = predictRange(angle, massGrams);
        results.push(prediction);
    }

    return results;
}

// ============================================================================
// UI Functions
// ============================================================================

/**
 * Show selected tab
 */
function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));

    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

/**
 * Quick prediction mode
 */
function quickPredict() {
    const mass = parseFloat(document.getElementById('quick-mass').value);
    const angle = parseFloat(document.getElementById('quick-angle').value);

    // Validation
    if (isNaN(mass) || mass < 3 || mass > 100) {
        alert('Please enter a valid mass between 3 and 100 grams');
        return;
    }

    if (isNaN(angle) || angle <= LAUNCHER.RELAXED_ANGLE_DEG || angle > 170) {
        alert(`Please enter a valid angle between ${LAUNCHER.RELAXED_ANGLE_DEG + 1}° and 170°`);
        return;
    }

    // Calculate prediction
    const result = predictRange(angle, mass);

    // Display results
    document.getElementById('result-mass').textContent = `${mass.toFixed(1)}g`;
    document.getElementById('result-angle').textContent = `${angle.toFixed(0)}°`;
    document.getElementById('result-deflection').textContent = `${result.deltaTheta.toFixed(0)}°`;
    document.getElementById('result-range-imperial').textContent =
        `${result.rangeInches.toFixed(1)} in (${result.rangeFeet.toFixed(2)} ft)`;
    document.getElementById('result-range-metric').textContent =
        `${result.rangeCentimeters.toFixed(1)} cm (${result.rangeMeters.toFixed(2)} m)`;
    document.getElementById('result-velocity').textContent =
        `${result.velocity.toFixed(2)} m/s (${result.velocityKmh.toFixed(1)} km/h)`;

    document.getElementById('quick-result').style.display = 'block';

    // Smooth scroll to results
    document.getElementById('quick-result').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Generate prediction table
 */
function generateTable() {
    const mass = parseFloat(document.getElementById('table-mass').value);
    const startAngle = parseInt(document.getElementById('table-start').value);
    const endAngle = parseInt(document.getElementById('table-end').value);
    const step = parseInt(document.getElementById('table-step').value);

    // Validation
    if (isNaN(mass) || mass < 3 || mass > 100) {
        alert('Please enter a valid mass between 3 and 100 grams');
        return;
    }

    if (startAngle >= endAngle) {
        alert('Start angle must be less than end angle');
        return;
    }

    // Generate predictions
    const results = generatePredictionTable(mass, startAngle, endAngle, step);

    // Update table
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';

    results.forEach(result => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${result.cockedAngle.toFixed(0)}°</td>
            <td>${result.deltaTheta.toFixed(0)}°</td>
            <td>${result.velocity.toFixed(2)} m/s<br><small>${result.velocityKmh.toFixed(1)} km/h</small></td>
            <td>${result.rangeInches.toFixed(1)} in<br><small>${result.rangeFeet.toFixed(2)} ft</small></td>
            <td>${result.rangeCentimeters.toFixed(1)} cm<br><small>${result.rangeMeters.toFixed(2)} m</small></td>
        `;
    });

    document.getElementById('table-mass-display').textContent = mass.toFixed(1);
    document.getElementById('table-result').style.display = 'block';

    // Store results for download
    window.currentTableResults = results;
    window.currentTableMass = mass;
}

/**
 * Download table as CSV
 */
function downloadTable() {
    if (!window.currentTableResults) {
        alert('No table data to download');
        return;
    }

    let csv = 'Angle (deg),Delta Theta (deg),Velocity (m/s),Velocity (km/h),Range (in),Range (ft),Range (cm),Range (m)\n';

    window.currentTableResults.forEach(result => {
        csv += `${result.cockedAngle},${result.deltaTheta},${result.velocity.toFixed(2)},${result.velocityKmh.toFixed(1)},${result.rangeInches.toFixed(1)},${result.rangeFeet.toFixed(2)},${result.rangeCentimeters.toFixed(1)},${result.rangeMeters.toFixed(2)}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `predictions_${window.currentTableMass}g.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Competition mode - add prediction
 */
let competitionResults = [];

function addCompetitionPrediction() {
    const mass = parseFloat(document.getElementById('comp-mass').value);

    // Validation
    if (isNaN(mass) || mass < 3 || mass > 100) {
        alert('Please enter a valid mass between 3 and 100 grams');
        return;
    }

    // Check for duplicates
    if (competitionResults.some(r => Math.abs(r.mass - mass) < 0.01)) {
        alert('This mass has already been added');
        return;
    }

    // Calculate prediction at max angle (170°)
    const result = predictRange(170, mass);
    competitionResults.push(result);

    // Sort by mass
    competitionResults.sort((a, b) => a.mass - b.mass);

    // Update table
    updateCompetitionTable();

    // Clear input
    document.getElementById('comp-mass').value = '';
}

function updateCompetitionTable() {
    const tbody = document.getElementById('competition-body');
    tbody.innerHTML = '';

    if (competitionResults.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="5">No predictions yet. Add masses above to start.</td></tr>';
        return;
    }

    competitionResults.forEach((result, index) => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${result.mass.toFixed(1)}</td>
            <td>${result.rangeInches.toFixed(1)} in<br><small>${result.rangeFeet.toFixed(2)} ft</small></td>
            <td>${result.rangeCentimeters.toFixed(1)} cm<br><small>${result.rangeMeters.toFixed(2)} m</small></td>
            <td>${result.velocity.toFixed(2)} m/s<br><small>${result.velocityKmh.toFixed(1)} km/h</small></td>
            <td><button class="btn-remove" onclick="removeCompetitionResult(${index})">Remove</button></td>
        `;
    });
}

function removeCompetitionResult(index) {
    competitionResults.splice(index, 1);
    updateCompetitionTable();
}

function clearCompetition() {
    if (competitionResults.length === 0) return;

    if (confirm('Clear all competition results?')) {
        competitionResults = [];
        updateCompetitionTable();
    }
}

/**
 * Allow Enter key to submit
 */
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('quick-mass').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') quickPredict();
    });

    document.getElementById('quick-angle').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') quickPredict();
    });

    document.getElementById('comp-mass').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') addCompetitionPrediction();
    });
});
