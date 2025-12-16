# Deploying to Vercel

This guide will help you deploy the Projectile Range Predictor web app to Vercel.

## 🚀 Quick Deploy (Recommended)

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Push your code to GitHub** (already done!)
   ```bash
   # Your code is already on branch: claude/projectile-range-predictor-vTPPE
   ```

2. **Sign up for Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Sign Up"
   - Choose "Continue with GitHub" (recommended)
   - Authorize Vercel to access your GitHub account

3. **Import Your Project**
   - Click "Add New..." → "Project"
   - Select your repository: `kaedenwellman/kaedensphysics`
   - Click "Import"

4. **Configure Project**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (keep default)
   - **Build Command**: Leave empty or use: `echo "No build needed"`
   - **Output Directory**: `public`
   - **Install Command**: Leave empty

5. **Deploy**
   - Click "Deploy"
   - Wait 30-60 seconds
   - Your site will be live at: `https://your-project-name.vercel.app`

### Option 2: Deploy via Vercel CLI (For Advanced Users)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd /home/user/kaedensphysics
   vercel
   ```

4. **Follow the prompts:**
   - Set up and deploy? **Y**
   - Which scope? (select your account)
   - Link to existing project? **N**
   - Project name? `projectile-predictor` (or your choice)
   - In which directory is your code located? `./`
   - Want to override settings? **N**

5. **Production Deploy**
   ```bash
   vercel --prod
   ```

## 📁 Project Structure

```
kaedensphysics/
├── public/              # Web app files (this gets deployed)
│   ├── index.html      # Main HTML page
│   ├── css/
│   │   └── styles.css  # Styling
│   └── js/
│       └── predictor.js # Prediction logic
├── vercel.json         # Vercel configuration
└── [Python files]      # Not deployed (local use only)
```

## ⚙️ Configuration Explained

The `vercel.json` file tells Vercel how to serve your site:

```json
{
  "outputDirectory": "public",  // Serve files from /public
  "cleanUrls": true,            // /about instead of /about.html
  "trailingSlash": false        // Enforce no trailing slashes
}
```

## 🌐 Custom Domain (Optional)

### Add Your Own Domain

1. **In Vercel Dashboard:**
   - Go to your project
   - Click "Settings" → "Domains"
   - Click "Add"
   - Enter your domain (e.g., `predictor.yourdomain.com`)

2. **Update DNS (at your domain registrar):**
   - Add a CNAME record:
     - Name: `predictor` (or `@` for root)
     - Value: `cname.vercel-dns.com`
   - Wait for DNS propagation (5-60 minutes)

3. **Enable HTTPS:**
   - Vercel automatically provisions SSL certificates
   - Your site will be accessible via `https://`

## 🔧 Environment Variables (Not Needed for This Project)

This project runs entirely in the browser, so no environment variables are needed.

If you want to add analytics or other features later:
1. Go to project Settings → Environment Variables
2. Add your variables
3. Redeploy

## 📊 Monitoring and Analytics

### Built-in Vercel Analytics (Free)

1. Go to your project dashboard
2. Click "Analytics" tab
3. View page views, visitors, performance metrics

### Add Google Analytics (Optional)

Add to `public/index.html` before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔄 Updating Your Deployment

### Automatic Deployments (Recommended)

Vercel automatically deploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update calculator"
git push origin claude/projectile-range-predictor-vTPPE
```

Vercel will automatically:
1. Detect the push
2. Build and deploy
3. Update your live site

### Manual Deployments

Using Vercel CLI:
```bash
vercel --prod
```

## 🧪 Preview Deployments

Every branch and pull request gets a unique preview URL:
- Main branch: `https://your-project.vercel.app`
- Feature branch: `https://your-project-git-branch.vercel.app`
- Pull request: `https://your-project-pr-123.vercel.app`

## 🐛 Troubleshooting

### Issue: "Build Failed"

**Solution:** This project doesn't need a build step. Ensure:
- Build Command is empty or: `echo "No build needed"`
- Output Directory is: `public`

### Issue: "404 Not Found"

**Solution:** Check that:
- Files are in the `/public` directory
- `vercel.json` specifies `"outputDirectory": "public"`

### Issue: JavaScript Not Working

**Solution:**
- Check browser console for errors (F12)
- Ensure files are properly linked in `index.html`
- Clear cache and hard reload (Ctrl+Shift+R)

### Issue: Styles Not Loading

**Solution:**
- Verify CSS path in HTML: `href="css/styles.css"`
- Check Network tab in browser dev tools
- Ensure CSS file is in `/public/css/`

## 📱 Testing Your Deployment

After deployment, test:

1. **Quick Prediction Tab**
   - Enter mass: 19.3g
   - Enter angle: 165°
   - Click Calculate
   - Should show: ~142.3 inches

2. **Prediction Table Tab**
   - Generate table for 19.3g
   - Should show ranges from 140° to 170°

3. **Competition Mode**
   - Add several masses
   - Verify predictions appear
   - Test CSV download

4. **Mobile Responsiveness**
   - Test on phone/tablet
   - All features should work
   - UI should adapt to screen size

## 🔒 Security

The deployed site includes security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

Plus HTTPS encryption (automatic via Vercel).

## 💰 Pricing

**Free Tier Includes:**
- Unlimited deployments
- 100GB bandwidth per month
- Automatic HTTPS
- DDoS protection
- Edge Network (CDN)

This project will easily stay within free tier limits.

## 📞 Support

- **Vercel Docs:** [vercel.com/docs](https://vercel.com/docs)
- **Vercel Support:** [vercel.com/support](https://vercel.com/support)
- **Community:** [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)

## 🎉 Success!

Once deployed, share your URL:
- `https://your-project.vercel.app`
- Or your custom domain!

The calculator is now available 24/7 from any device with internet access. Perfect for competition day!

---

**Quick Checklist:**
- [ ] Code pushed to GitHub
- [ ] Vercel account created
- [ ] Project imported and deployed
- [ ] Site loads correctly
- [ ] All tabs working
- [ ] Mobile responsive
- [ ] Custom domain added (optional)
- [ ] Shared URL with teammates
