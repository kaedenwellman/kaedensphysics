# Quick Reference Card - Competition Day

## 🚀 Quick Start
```bash
python projectile_predictor_v2.py
```

## 📊 19.3g Predictions (Most Common Mass)

### Quick Lookup Table
| Angle | Range (inches) | Range (feet) |
|-------|----------------|--------------|
| 140°  | 27 in          | 2.2 ft       |
| 145°  | 47 in          | 4.0 ft       |
| 150°  | 69 in          | 5.8 ft       |
| 155°  | 93 in          | 7.7 ft       |
| 160°  | 117 in         | 9.7 ft       |
| 165°  | 142 in         | 11.9 ft      |
| 170°  | 169 in         | 14.1 ft      |

## 🎯 Competition Mode (Fastest Method)
1. Start program
2. Select option **3** (Competition Mode)
3. Enter mass → get instant prediction
4. Type 'done' when finished

## 📐 Mass Predictions at 170° (Max Angle)

| Mass  | Predicted Range |
|-------|-----------------|
| 3g    | 28 in (2.4 ft)  |
| 5g    | 95 in (7.9 ft)  |
| 7g    | 142 in (11.8 ft)|
| 10g   | 173 in (14.5 ft)|
| 12.5g | 180 in (15.0 ft)|
| 15g   | 167 in (13.9 ft)|
| 19.3g | 169 in (14.1 ft)|
| 20g   | 153 in (12.8 ft)|
| 25g   | 145 in (12.1 ft)|
| 30g   | 130 in (10.8 ft)|
| 35g   | 119 in (9.9 ft) |
| 40g   | 110 in (9.2 ft) |
| 45g   | 100 in (8.4 ft) |
| 50g   | 95 in (7.9 ft)  |
| 60g   | 86 in (7.2 ft)  |
| 66.8g | 93 in (7.8 ft)  |
| 70g   | 81 in (6.7 ft)  |

## 🔧 Menu Options

| Option | Function | Use When |
|--------|----------|----------|
| 1 | Quick Prediction | Need one specific prediction |
| 2 | Full Analysis | Want table + visualization |
| 3 | Competition Mode | **FASTEST - Testing multiple masses** |
| 4 | Generate 19.3g Table | Need 19.3g reference |
| 5 | Recalibrate | Launcher has changed |
| 6 | Exit | Done |

## 📏 Formula Quick Reference

**Spring Deflection:**
```
Δθ = Cocked_Angle - 135°
```

**Approximate Range (66.8g only):**
```
Range ≈ 0.0133×(Δθ)² + 2.133×(Δθ) + 2.0 inches
```

**Velocity Scaling for Different Masses:**
```
v_new = v_ref × √(66.8 / mass_new)
```

## ⚡ Mental Math Shortcuts

### Quick Angle Conversions
- 140° → Δθ = 5°
- 145° → Δθ = 10°
- 150° → Δθ = 15°
- 155° → Δθ = 20°
- 160° → Δθ = 25°
- 165° → Δθ = 30°
- 170° → Δθ = 35° (MAX)

### Mass Categories
- **Extremely Light (3-7g)**: ~28-142" at max (drag-dominated, range DECREASES below ~12g)
- **Optimal (10-15g)**: ~167-180" at max (best range, drag vs. velocity balance)
- **Light (15-25g)**: ~145-169" at max
- **Medium (25-40g)**: ~110-145" at max
- **Medium-Heavy (40-55g)**: ~95-110" at max
- **Heavy (55-70g)**: ~81-95" at max

**Note:** Maximum range occurs around 12-13g. Lighter masses have SHORTER range due to air resistance!

## 🎓 Competition Strategy

### Step 1: Weigh Projectile
Use accurate scale (±0.1g precision if possible)

### Step 2: Verify Angle Setting
Confirm launcher is set to expected angle (typically 170° for max range)

### Step 3: Use Competition Mode
- Fastest method
- Enter mass, get range
- Can test multiple masses quickly

### Step 4: Make Prediction
Round to nearest inch for final answer

### Step 5: Record Results
Note actual vs predicted for future calibration

## ⚠️ Common Mistakes to Avoid

❌ **Using cm instead of inches** - All inputs/outputs are INCHES
❌ **Forgetting spring deflection** - It's cocked_angle - 135°, not the angle itself
❌ **Mass in kg instead of grams** - Enter mass in GRAMS
❌ **Using wrong angle** - Measure the cocked angle, not launch angle

## 📱 If Computer Fails - Manual Calculation

For 66.8g mass, use:
```
Range ≈ (Δθ)²/75 + (32/15)×Δθ + 2 inches
```

For other masses at 170°:
```
Range ≈ 93 × √(66.8/mass) × 0.85 inches
```
(The 0.85 is drag correction factor)

## 🔍 Troubleshooting

**Prediction seems way off:**
- Check mass units (should be grams)
- Verify angle (should be 135-170°)
- Confirm calibration loaded properly

**Program won't start:**
```bash
pip install numpy scipy matplotlib
```

**Need to recalibrate:**
- Select option 5
- Program will refit to built-in calibration data

## 📊 Accuracy Guide

| Mass Range | Expected Accuracy |
|------------|-------------------|
| 3-10g      | ±5-15 inches (drag effects very significant) |
| 10-30g     | ±4-6 inches       |
| 30-50g     | ±3 inches         |
| 50-70g     | ±2 inches         |

## 🎯 Optimal Settings for Maximum Range

- **Angle**: 170° (maximum deflection)
- **Optimal Mass**: 12-13g (absolute maximum range ~180")
- **Mass Note**: Going lighter than 12g REDUCES range due to drag!
- **Practical Range**: 10-25g gives good performance (167-180" range)

## 💡 Pro Tips

1. **Test the calibration mass (66.8g) first** - Verify launcher hasn't changed
2. **Bring printed prediction tables** - Backup if laptop fails
3. **Round conservatively** - Better to be slightly under than over
4. **Account for wear** - Spring weakens over time, may need recalibration
5. **Temperature matters** - Cold conditions slightly reduce range
6. **Very light masses (3-7g)** - Predictions less accurate due to high drag sensitivity; test if possible

## 📞 Emergency Backup Predictions

If all else fails, use this rule of thumb:
```
Range (feet) ≈ (Δθ in degrees) / 2.5 × √(66.8/mass)
```

Example: 19.3g at 165° (Δθ=30°):
- 30/2.5 = 12 feet × √(66.8/19.3) = 12 × 1.86 = ~22 feet
- (This is approximate!)

---

**Print this page and bring it to competition!** 📄✨

Good luck! 🚀
