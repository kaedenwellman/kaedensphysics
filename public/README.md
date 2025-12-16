# Projectile Range Predictor - Web App

A browser-based physics calculator for predicting projectile landing distances from a torsion spring launcher.

## 🌐 Live Demo

Visit the live app: [Your Vercel URL here after deployment]

## 🚀 Features

- **Quick Prediction**: Enter mass and angle for instant range calculation
- **Prediction Table**: Generate comprehensive range tables
- **Competition Mode**: Rapid testing for multiple masses
- **Fully Client-Side**: No server needed, works offline
- **Mobile Responsive**: Works on phones, tablets, and desktops
- **CSV Export**: Download prediction tables

## 📊 Accuracy

Based on empirical calibration:
- Reference mass (66.8g): ±0-2 inches
- Similar masses (50-80g): ±2-4 inches
- Light masses (10-30g): ±3-6 inches

## 🧪 Testing

Open `test.html` in your browser to run the test suite and verify predictions.

## 💻 Local Development

### Using Python (Built-in)

```bash
python -m http.server 8000 --directory public
# Then visit: http://localhost:8000
```

### Using Node.js

```bash
npm start
# Then visit: http://localhost:8000
```

### Using any HTTP server

```bash
cd public
# Then use your preferred HTTP server
```

## 📁 Structure

```
public/
├── index.html          # Main application
├── test.html           # Test suite
├── css/
│   └── styles.css      # Styling
└── js/
    └── predictor.js    # Prediction logic
```

## 🔬 Physics Model

**Empirical Model for 66.8g:**
```
R(Δθ) = 0.0133×(Δθ)² + 2.133×(Δθ) + 2.0
```

**Mass Scaling:**
- Launch velocity: v ∝ √(m_ref/m_new)
- Drag correction: 0.8246 factor calibrated from data
- Ballistic trajectory with 11" launch height

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎯 Usage Tips

1. **For Competition Day:**
   - Use Competition Mode (Tab 3)
   - Enter masses as you receive them
   - Predictions appear instantly

2. **For Analysis:**
   - Use Prediction Table (Tab 2)
   - Generate full range tables
   - Export to CSV for documentation

3. **For Quick Checks:**
   - Use Quick Prediction (Tab 1)
   - Single mass + angle → instant result

## 🐛 Troubleshooting

**JavaScript not working:**
- Check browser console (F12) for errors
- Ensure JavaScript is enabled
- Try hard refresh (Ctrl+Shift+R)

**Incorrect predictions:**
- Verify mass is in grams (not kg or lb)
- Confirm angle is between 136° and 170°
- Check that Δθ calculation is correct

## 📄 License

MIT - Free to use for educational purposes

## 🤝 Contributing

Found a bug? Have a suggestion?
- Open an issue on GitHub
- Submit a pull request
- Contact the author

## 🎓 Educational Use

This calculator is designed for:
- Physics competitions
- Educational demonstrations
- Engineering design projects
- Catapult optimization

## ⚡ Performance

- Instant predictions (no server latency)
- Works offline after first load
- Lightweight (~50KB total)
- No dependencies required

---

**Made for physics extra credit projects** 🎯🚀
