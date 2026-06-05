# 🔬 Materials Science AI Analyzer

A production-ready Streamlit web application that uses OpenAI's GPT models to analyze material requirements and provide intelligent classification and application suggestions.

## Features

✨ **Key Capabilities:**
- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT-3.5-Turbo (or GPT-4) to understand material requirements
- 📊 **Intelligent Classification**: Automatically categorizes materials into 7 predefined types
- 🎯 **Smart Recommendations**: Suggests the most suitable application for each material
- 🧪 **Composition Analysis**: Provides realistic material compositions with component ratios
- � **PDF Report Generation**: Creates professional, downloadable PDF reports with all analysis data
- �🛡️ **Robust Error Handling**: Gracefully handles API errors, rate limits, and connection issues
- 💻 **User-Friendly Interface**: Clean, intuitive Streamlit UI with helpful examples
- 🔐 **Secure Configuration**: Uses environment variables for API key management

## Material Categories

The AI classifies materials into one of these categories:
- **Metal**: Metallic materials (aluminum, steel, titanium, etc.)
- **Polymer**: Plastics and rubber-based materials
- **Ceramic**: Inorganic, non-metallic materials
- **Composite**: Combinations of two or more materials
- **Semiconductor**: Electronic materials (silicon, gallium arsenide, etc.)
- **Biomaterial**: Biocompatible materials for medical applications
- **Other**: Any other material type

## PDF Report Generation

📄 **Generate professional PDF reports** containing:
- **Title**: "Materials Science Recommendation Report"
- **Generation Date & Time**: Timestamp of when the report was created
- **User's Original Prompt**: The material requirement as entered
- **Material Category**: AI classification with color coding
- **Target Application**: Recommended use cases
- **Composition Table**: Component-by-component breakdown with ratios and percentages
- **Disclaimer**: Notice about AI-generated content and need for verification

**Example PDF Report Flow:**
1. User enters: "a biodegradable stent material"
2. AI analyzes and returns results
3. User clicks "Generate PDF Report"
4. App creates professional PDF with all analysis data
5. User downloads PDF with timestamp-based filename

**PDF Features:**
- ✅ Generated offline (no external API calls)
- ✅ Professional formatting with tables
- ✅ Includes all material analysis data
- ✅ Ready for sharing with engineers and stakeholders
- ✅ Downloadable with one click

## Prerequisites

- **Python 3.8 or higher** installed on your system
- **OpenAI API Key** (free trial or paid account)
- **pip** (Python package manager, usually comes with Python)

## Installation & Setup

### Step 1: Get Your OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign in (or create an account if you don't have one)
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key (you won't be able to see it again!)
6. Keep this key secure and never commit it to version control

### Step 2: Clone or Download the Project

Download the project files to a directory on your computer:
```
d:\material_studio_1\
├── app.py
├── requirements.txt
├── README.md
└── .env (you'll create this next)
```

### Step 3: Create the `.env` File

In the project root directory (`d:\material_studio_1\`), create a file named `.env` (no file extension) and add your API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

⚠️ **Important Security Notes:**
- **Never** share your API key with anyone
- **Never** commit `.env` to version control
- Add `.env` to your `.gitignore` file if using Git

### Step 4: Install Dependencies

Open a terminal/command prompt and navigate to the project directory:

**On Windows (PowerShell or Command Prompt):**
```powershell
cd d:\material_studio_1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**On macOS/Linux:**
```bash
cd /path/to/material_studio_1
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

**Dependencies installed:**
- `streamlit` - Web app framework
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests library
- `fpdf2` - PDF generation library

### Step 5: Run the Application

In the same terminal, run:

```powershell
streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501/`

If it doesn't open automatically, manually navigate to `http://localhost:8501/` in your web browser.

## Usage

1. **Enter a Material Description**: Use the text area to describe the material you need. Include:
   - Intended use case
   - Required properties (e.g., "lightweight", "heat-resistant")
   - Application context

2. **Click "Analyze Material"**: The AI will process your request

3. **Review Results**: See the AI's classification, application, and composition

4. **Generate PDF Report** (Optional): 
   - Click the "Generate PDF Report" button
   - Review the generated PDF
   - Click "Download PDF Report" to save it to your computer

5. **Download and Share**: The PDF is ready to share with engineers, stakeholders, or save for documentation

### Example Prompts

Try these to test the application:

- "A lightweight, high-strength material for aerospace applications that can withstand extreme temperatures"
- "A flexible, biocompatible material suitable for implantable medical devices"
- "An electrically conductive material with excellent thermal properties for circuit boards"
- "A durable, weather-resistant material for outdoor infrastructure"
- "A transparent, durable material for protective eyewear and barriers"
- "A biodegradable stent material for temporary cardiovascular applications"
- "A heat-resistant alloy for jet engine turbine blades"

## API Pricing & Costs

**OpenAI Pricing (as of 2026):**
- **GPT-3.5-Turbo**: ~$0.0015 per 1K input tokens, $0.002 per 1K output tokens
- **GPT-4**: ~$0.03 per 1K input tokens, $0.06 per 1K output tokens

**Cost Estimate:**
- Typical material analysis uses ~150-200 tokens total
- Average cost per analysis: $0.0003-0.0006 (using GPT-3.5-Turbo)
- 100 analyses would cost approximately $0.03-0.06

**Monitor your usage:**
- Log in to [OpenAI Platform](https://platform.openai.com/) → Usage
- Set up usage limits and alerts to control costs

## Troubleshooting

### "OpenAI API Key Not Found"
**Problem**: The app shows this error message  
**Solution**: 
- Make sure `.env` file exists in the app directory
- Check that it contains `OPENAI_API_KEY=sk-...` with your actual key
- Make sure there are no spaces around the `=` sign
- Restart the app after creating/modifying `.env`

### "Authentication failed"
**Problem**: API key is invalid or incorrect  
**Solution**:
- Verify your API key is correct by checking it at https://platform.openai.com/api-keys
- Create a new key if needed
- Update your `.env` file
- Restart the app

### "Rate limit exceeded"
**Problem**: Too many API requests  
**Solution**:
- Wait a few minutes before trying again
- OpenAI rate limits vary by plan; upgrade your account if needed
- Set up rate limiting in your `.env` or application code

### "Request timed out"
**Problem**: API call took too long  
**Solution**:
- Check your internet connection
- Try again (sometimes the API is slow)
- The app has a 30-second timeout built in

### "Invalid material category" in error message
**Problem**: AI returned an unexpected category  
**Solution**:
- This is extremely rare but indicates the AI didn't follow instructions
- Try rephrasing your material request
- Try again (AI responses can vary)

### "Error generating PDF"
**Problem**: PDF generation fails  
**Solution**:
- Ensure `fpdf2` is installed: `pip install fpdf2`
- Check that all material data (composition) is valid
- Try restarting the app
- Check terminal output for detailed error messages

### "No module named 'fpdf2'" or similar
**Problem**: PDF library not installed  
**Solution**:
```powershell
pip install fpdf2
```

## How It Works

### Prompt Engineering

The application uses carefully engineered prompts to ensure the AI returns **only valid JSON** with three key pieces of information:

1. **System Prompt**: Instructs the AI to respond ONLY with JSON, defines the required schema, and provides examples
2. **User Prompt**: Provides context about the material requirements and reminds the AI to return JSON
3. **Validation**: The response is checked for:
   - Valid JSON format
   - Required fields (material_category, target_application, composition)
   - Valid material category
   - Non-empty composition array
   - Composition ratios between 0 and 1
   - Composition ratios sum to ~1.0 (with 0.01 tolerance)

**Example AI Response:**
```json
{
  "material_category": "Composite",
  "target_application": "Lightweight, high-strength aerospace structures with excellent thermal stability",
  "composition": [
    {"component": "carbon fiber", "ratio": 0.60},
    {"component": "epoxy resin", "ratio": 0.40}
  ]
}
```

**Example Response for an Alloy:**
```json
{
  "material_category": "Metal",
  "target_application": "Decorative fixtures, plumbing fittings, and electrical components",
  "composition": [
    {"component": "copper", "ratio": 0.70},
    {"component": "zinc", "ratio": 0.30}
  ]
}
```

## Configuration Options

You can customize the application by editing `app.py`:

### Change AI Model
Open `app.py` and find this line (around line 88):
```python
model="gpt-3.5-turbo",  # Change to "gpt-4" for better quality
```

### Adjust Temperature (Creativity)
```python
temperature=0.7,  # Higher = more creative, Lower = more consistent
```

- `0.0` - Very deterministic and consistent
- `0.5` - Balanced
- `1.0` - Very creative and varied

### Modify Material Categories
Edit the `MATERIAL_CATEGORIES` list (around line 32) to add or remove categories

### Adjust Timeout
```python
timeout=30  # Increase if you get frequent timeouts
```

## Advanced Usage

### Running Headless (No Browser)
```powershell
streamlit run app.py --logger.level=info
```

### Custom Configuration
Create a `~/.streamlit/config.toml` file to customize Streamlit settings:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Batch Processing (Advanced)
Modify `app.py` to accept a CSV file for batch material analysis. This would require restructuring the UI.

## File Structure

```
material_studio_1/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # API key (create this yourself)
└── .gitignore           # (Optional) Excludes .env from Git
```

### Recommended `.gitignore` Contents
```
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Streamlit
.streamlit/cache/
.streamlit/logs/

# OS
.DS_Store
Thumbs.db
```

## Security Best Practices

1. **Never commit `.env` to version control**
   ```powershell
   git add .gitignore  # Add .env to .gitignore first
   ```

2. **Rotate your API key periodically**
   - Generate new keys at https://platform.openai.com/api-keys
   - Deactivate old keys

3. **Monitor API usage**
   - Check https://platform.openai.com/account/billing/usage
   - Set spending limits

4. **Use environment variables in production**
   - Never hardcode API keys in code
   - Use CI/CD secrets for deployment

## Performance Optimization

- **Response Time**: Usually 2-5 seconds per analysis
- **Token Usage**: ~150-200 tokens per request
- **Cost Per Request**: ~$0.0003-0.0006 (GPT-3.5-Turbo)

### Tips to Improve Speed
1. Use shorter, clearer material descriptions
2. Use GPT-3.5-Turbo instead of GPT-4 (faster and cheaper)
3. Reduce `max_tokens` parameter if needed

## Deployment Options

### Local Development
- Simply run `streamlit run app.py` as shown above
- Access at `http://localhost:8501/`

### Cloud Deployment Options

#### Streamlit Cloud (Easiest)
1. Push code to GitHub (without `.env`)
2. Connect your repo to Streamlit Cloud
3. Add `OPENAI_API_KEY` as a secret in Streamlit Cloud dashboard

#### Heroku
1. Create `Procfile`: `web: streamlit run app.py --server.port=$PORT`
2. Set `OPENAI_API_KEY` environment variable
3. Deploy using Git

#### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["streamlit", "run", "app.py"]
```

## Limitations & Future Enhancements

### Current Limitations
- ⚠️ AI responses are not verified against real material databases
- ⚠️ Cannot replace professional materials engineering consultation
- ⚠️ Limited to OpenAI's knowledge (no web search or real-time data)

### Potential Enhancements
- 🔄 Integration with materials property databases
- 📚 Add multi-language support
- 💾 Database to store analysis history
- 📊 Export results to PDF or CSV
- 🔐 User authentication and multi-user support
- 📱 Mobile app version
- 🎨 Custom material templates
- 🔬 Real materials science equations and calculations

## Support & Troubleshooting

For issues:
1. Check the **Troubleshooting** section above
2. Review your `.env` file setup
3. Verify your API key is valid
4. Check internet connectivity
5. Review Streamlit and OpenAI documentation

## License

This project is provided as-is for educational and commercial use.

## Disclaimer

This application uses AI to provide material suggestions. **AI-generated recommendations should not be used as the sole basis for material selection in production or safety-critical applications.** Always:

- ✅ Consult with qualified materials engineers
- ✅ Conduct proper testing and validation
- ✅ Follow industry standards and regulations
- ✅ Use official material property databases
- ✅ Perform fatigue, stress, and environmental testing

## Contact & Contributions

Questions or suggestions? Feel free to reach out or open an issue.

---

**Happy analyzing!** 🚀🔬

Last Updated: June 2026
