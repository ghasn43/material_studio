# Quick Start Guide

## 5-Minute Setup

### 1. Get API Key (2 minutes)
- Go to https://platform.openai.com/api-keys
- Click "Create new secret key"
- Copy it (you won't see it again!)

### 2. Create `.env` File (1 minute)
Create a file named `.env` in the project folder with:
```
OPENAI_API_KEY=sk-paste-your-key-here
```

### 3. Install & Run (2 minutes)
```powershell
pip install -r requirements.txt
python -m streamlit run app.py
```

Done! Browser opens automatically. 🎉

---

## Using the App

### Step 1: Write a Material Description
Example: "I need a lightweight, waterproof material for boat hulls that has good UV resistance"

### Step 2: Click "Analyze Material"
Wait 2-5 seconds for AI to think and analyze...

### Step 3: Review Results
- **Material Category**: AI's classification (Metal, Polymer, Ceramic, etc.)
- **Target Application**: Recommended uses for the material
- **Composition**: The constituent materials and their ratios (e.g., 70% copper + 30% zinc for brass)

### Step 4 (Optional): Generate PDF Report
- Click "Generate PDF Report" button
- Review the professional PDF preview
- Click "Download PDF Report" to save it to your computer
- Share with engineers or save for documentation

---

## PDF Report Contents 📄

The generated PDF includes:
- ✅ Material category
- ✅ Target application
- ✅ Composition table with percentages
- ✅ Original prompt you entered
- ✅ Generation date and time
- ✅ Professional formatting
- ✅ Disclaimer about AI-generated content

---

## Common Issues & Quick Fixes

| Problem | Solution |
|---------|----------|
| "API Key Not Found" | Make sure `.env` file exists with your key |
| "Authentication failed" | Double-check your API key at openai.com |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Connection error" | Check internet, try again |
| Takes too long | Normal (2-5 sec), check internet speed |

---

## Switching to GPT-4 (Better Quality)

Edit `app.py` line 88:
```python
model="gpt-4",  # Change from gpt-3.5-turbo
```

**Note**: GPT-4 is ~20x more expensive but better quality.

---

## Where to Get Help

- **API Key Issues**: https://platform.openai.com/account/billing/overview
- **Streamlit Docs**: https://docs.streamlit.io
- **OpenAI Docs**: https://platform.openai.com/docs
- **Check `.env`**: Most common issue!

---

## Cost Estimate

- Typical analysis: $0.0003-0.0006 (GPT-3.5-Turbo)
- 100 analyses: ~$0.05
- 1000 analyses: ~$0.50

Monitor at: https://platform.openai.com/account/billing/usage

---

## Next Steps

1. ✅ Setup complete!
2. 🧪 Try the example prompts in the app
3. 📚 Read `README.md` for detailed docs
4. 🚀 Deploy to cloud (Streamlit Cloud, Heroku, etc.)
5. 🔧 Customize for your needs

---

**Happy analyzing!** 🔬
