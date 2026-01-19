# 🚀 Web Demo Deployment Guide

This guide will help you deploy the RAN Network Optimizer web demo to Streamlit Cloud for committee presentation.

## 📋 Quick Start (Local Testing)

### 1. Install Dependencies
```bash
cd RAN_Optimizer_Agent
pip install -r requirements.txt
```

### 2. Run Locally
```bash
streamlit run web_demo.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 🌐 Deploy to Streamlit Cloud (Get Shareable Link)

### Prerequisites
- GitHub account
- Git installed on your computer

### Step 1: Create GitHub Repository

1. **Initialize Git repository** (if not already done):
```bash
cd RAN_Optimizer_Agent
git init
git add .
git commit -m "Initial commit - RAN Optimizer Web Demo"
```

2. **Create a new repository on GitHub**:
   - Go to https://github.com/new
   - Repository name: `RAN-Network-Optimizer`
   - Description: "AI-Powered RAN Network Optimization Demo"
   - Make it **Public** (required for free Streamlit Cloud)
   - Don't initialize with README (we already have files)
   - Click "Create repository"

3. **Push your code**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/RAN-Network-Optimizer.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://streamlit.io/cloud

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Fill in the deployment form**:
   - **Repository**: YOUR_USERNAME/RAN-Network-Optimizer
   - **Branch**: main
   - **Main file path**: web_demo.py
   - **App URL**: Choose a custom URL (e.g., ran-optimizer-demo)

5. **Click "Deploy"**

6. **Wait 2-5 minutes** for deployment

7. **Get your shareable link**:
   - Format: `https://YOUR_APP_NAME.streamlit.app`
   - Example: `https://ran-optimizer-demo.streamlit.app`

### Step 3: Share with Committee

Your demo link will be:
```
https://[your-app-name].streamlit.app
```

**Features available:**
- ✅ Executive Summary dashboard
- ✅ Live training demonstration
- ✅ Network topology visualization
- ✅ ROI calculator
- ✅ Technical documentation
- ✅ No installation required for viewers
- ✅ Works on any device (desktop, tablet, mobile)

---

## 🔧 Alternative Deployment Options

### Option 2: Deploy to Hugging Face Spaces

1. **Create account**: https://huggingface.co/join
2. **Create new Space**: https://huggingface.co/new-space
3. **Choose Streamlit** as SDK
4. **Upload files** via web interface or git
5. **Your link**: `https://huggingface.co/spaces/YOUR_USERNAME/ran-optimizer`

### Option 3: Deploy to Render

1. **Create account**: https://render.com
2. **New Web Service** → Connect GitHub repo
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `streamlit run web_demo.py --server.port=$PORT --server.address=0.0.0.0`
5. **Free tier available** (with sleep after inactivity)

### Option 4: Use ngrok (Temporary Link)

For quick testing or short presentations:

```bash
# Install ngrok
# Download from: https://ngrok.com/download

# Run Streamlit locally
streamlit run web_demo.py &

# Create public tunnel
ngrok http 8501
```

You'll get a temporary public URL like: `https://abc123.ngrok.io`

**Note**: This link expires when you close ngrok.

---

## 🎯 Demo Preparation Checklist

Before your committee presentation:

### Technical Setup
- [ ] Deploy to Streamlit Cloud
- [ ] Test the shareable link on different devices
- [ ] Verify all visualizations load correctly
- [ ] Test the training demo (should complete in 2-3 minutes)
- [ ] Check mobile responsiveness

### Presentation Prep
- [ ] Bookmark the demo link for easy access
- [ ] Have backup slides ready (in case of internet issues)
- [ ] Test on presentation room WiFi/computer
- [ ] Prepare talking points for each page
- [ ] Know your ROI numbers

### Demo Flow (Recommended 10-minute presentation)

1. **Executive Summary** (2 min)
   - Show key benefits and improvements
   - Highlight automation and cost savings

2. **Live Demo** (4 min)
   - Click "Start Optimization"
   - Show network topology
   - Explain AI learning process
   - Display before/after results

3. **ROI Calculator** (2 min)
   - Show financial benefits
   - Explain payback period
   - Highlight recurring savings

4. **Technical Details** (2 min)
   - Quick overview of architecture
   - Mention integration capabilities
   - Address any technical questions

---

## 📱 Accessing the Demo

### For Committee Members

Share this message:

```
RAN Network Optimizer - AI Demo

View the live demo at: [YOUR_LINK]

No installation required - works in any browser.

Recommended browsers: Chrome, Firefox, Safari, Edge
Works on: Desktop, Laptop, Tablet, Mobile
```

### Tips for Best Experience

1. **Use a modern browser** (Chrome recommended)
2. **Stable internet connection** (demo loads data in real-time)
3. **Allow 2-3 minutes** for training demonstration
4. **Expand to fullscreen** for better visualization

---

## 🐛 Troubleshooting

### Issue: App won't start on Streamlit Cloud

**Solution:**
- Check `requirements.txt` is present
- Verify all imports are available
- Check Streamlit Cloud logs for errors

### Issue: Training is too slow

**Solution:**
- Reduce number of cells (sidebar: 5-10 cells)
- Reduce training episodes (sidebar: 20-50 episodes)
- Streamlit Cloud has limited CPU resources

### Issue: "Module not found" error

**Solution:**
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push
```

Streamlit Cloud will automatically redeploy.

### Issue: App crashes during training

**Solution:**
- Reduce complexity in sidebar settings
- Check memory usage (Streamlit Cloud: 1GB limit)
- Consider using pre-trained model for demo

---

## 🔒 Security Notes

### For Public Deployment

- ✅ No sensitive data in code
- ✅ Simulated network data only
- ✅ No real network connections
- ✅ No authentication required (demo only)

### For Production Deployment

If deploying for actual network use:
- 🔐 Add authentication (Streamlit auth or OAuth)
- 🔐 Use HTTPS only
- 🔐 Connect to real network via secure APIs
- 🔐 Implement role-based access control
- 🔐 Add audit logging
- 🔐 Comply with telecom security standards

---

## 💡 Customization Tips

### Change App Appearance

Edit in `web_demo.py`:
```python
st.set_page_config(
    page_title="Your Company - RAN Optimizer",
    page_icon="📡",  # Change icon
    layout="wide"
)
```

### Add Company Logo

```python
st.sidebar.image("logo.png", use_column_width=True)
```

### Modify Training Parameters

In sidebar configuration:
```python
num_cells = st.sidebar.slider("Number of Cells", 5, 20, 10)
num_episodes = st.sidebar.slider("Training Episodes", 20, 200, 50)
```

### Add Custom Metrics

In ROI calculator section, add your own business calculations.

---

## 📞 Support

For issues or questions:
1. Check Streamlit documentation: https://docs.streamlit.io
2. Review error logs in Streamlit Cloud console
3. Test locally first: `streamlit run web_demo.py`

---

## 🎉 Success Checklist

You're ready when you can:
- ✅ Access the demo via shareable link
- ✅ Navigate all 5 pages smoothly
- ✅ Run the training demo successfully
- ✅ See visualizations render correctly
- ✅ Calculate ROI with different scenarios
- ✅ View on mobile device
- ✅ Share link with colleagues

---

**Built with Streamlit** | **Powered by Deep Reinforcement Learning** | **Ready for Production**
