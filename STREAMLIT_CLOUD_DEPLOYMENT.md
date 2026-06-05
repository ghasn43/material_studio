# Streamlit Cloud Deployment Guide

## Materials Science AI - Deployment Instructions

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)
- Anthropic API key (from https://console.anthropic.com)

### Step 1: Prepare Your Repository

The code is already pushed to GitHub at: https://github.com/ghasn43/material_studio

Make sure the repository includes:
- `app.py` (main Streamlit app)
- `category_registry.py` (materials science data and classification logic)
- `requirements.txt` (Python dependencies)

### Step 2: Deploy to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select:
   - **Repository:** ghasn43/material_studio
   - **Branch:** master
   - **Main file path:** app.py
4. Click "Deploy"

The app will now be building and should be live in a few minutes.

### Step 3: Add Your API Key (CRITICAL)

Once the app is deployed:

1. Go to your deployed app
2. Click the hamburger menu (☰) in the top right
3. Select **"Settings"**
4. Click on **"Secrets"** tab
5. Paste the following in the text area:
   ```
   ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```
   Replace with your actual Anthropic API key from https://console.anthropic.com

6. Click "Save"
7. The app will automatically rerun with the API key

### Step 4: Verify It Works

1. Return to your app (it should now be running)
2. Try submitting a material request, e.g.:
   ```
   Oil and gas produced water pre-treatment media for ADNOC operations in UAE Gulf conditions
   ```
3. If you see category classification, composition table, and parameters, it's working! ✅

### Environment Variables Supported

The app supports API keys from multiple sources (in order of priority):

1. **Streamlit Secrets** (recommended for Streamlit Cloud)
   - Set via app Settings → Secrets panel
   
2. **Environment Variables** (for local development)
   - Set via `.env` file or system environment
   - Format: `ANTHROPIC_API_KEY=sk-ant-...`

### Troubleshooting

**"Anthropic API Key Not Found" error:**
- Make sure you added the secret to the Secrets panel
- Verify the key is correct (starts with `sk-ant-`)
- Wait a moment and refresh the page

**"API Request Failed" error:**
- Check that your Anthropic API key is valid
- Verify you have account credits on Anthropic Console
- Check the app logs in Streamlit Cloud dashboard

**Composition validation or category not working:**
- Ensure `category_registry.py` is present in the repository
- Check the app logs for Python import errors

### Local Testing

To test locally with Streamlit Cloud secrets format:

1. Create `.streamlit/secrets.toml`:
   ```
   ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

2. Run:
   ```bash
   streamlit run app.py
   ```

3. The app will use the secrets.toml file for API key

### Features

Once deployed, the app provides:

- 🎯 **14 Material Categories** with intelligent classification
  - Fabric oil stain removal
  - Roof waterproofing
  - **Oil & Gas Produced-Water Pre-Treatment** (optimized for UAE/ADNOC)
  - Desalination pre-treatment
  - Membrane water treatment
  - CO2 capture materials
  - And 8 more specialized categories

- 🧪 **Composition Validation**
  - Automatic detection and removal of invalid substrate items
  - Ensures formulations contain only active components

- 📊 **AI-Powered Analysis**
  - Claude API integration for material analysis
  - Confidence scoring and category recommendations
  - Conflict detection for misclassifications

- 📋 **Comprehensive Reports**
  - Material composition with percentages
  - Category-specific parameters and targets
  - Validation plan and testing procedures
  - Processing method and safety guidelines
  - PDF export capability

### Support

For issues with:
- **Streamlit Cloud:** Check the Streamlit documentation
- **This App:** See README.md and test files in the repository
- **Anthropic API:** Visit https://support.anthropic.com
