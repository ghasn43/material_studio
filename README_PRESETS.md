# Materials Science AI with Intelligent Category Presets

Advanced AI material analyzer that **automatically detects** specialized material categories like **atmospheric water harvesting (AWH)** and **photocatalytic coatings**, then enriches the analysis with category-specific parameters, targets, and validation protocols.

## 🎯 Key Features

- **Intelligent Category Detection**: Keyword-based detection for AWH, photocatalysis, and other specialized categories
- **Preset Parameters & Targets**: Automatically includes domain-specific parameters for each detected category
- **Comprehensive Validation Plans**: Standards-aligned testing protocols (BET, SEM, XRD, TGA, microbial safety, etc.)
- **Fallback to Generic**: If no preset matches, gracefully defaults to generic material analysis
- **Professional PDF Reports**: Download detailed reports with all parameters and validation requirements
- **OpenAI-Powered**: Uses GPT-3.5-Turbo for intelligent material analysis

## 📋 Supported Preset Categories

### Atmospheric Water Harvesting Material
**Keywords**: "atmospheric water harvesting", "moisture capture", "hygroscopic salt", "water from air", etc.

**Specific Parameters**:
- Relative humidity range: 40–90% RH
- Water uptake target: 0.3–0.8 g water/g dry material
- Adsorption/desorption times and temperatures
- Cycling durability: 50–100 wet/dry cycles
- Salt leaching and water quality testing

**Validation Plan Includes**:
- BET surface area analysis
- SEM/XRD characterization
- Salt leaching tests (chloride ion measurement)
- Water quality testing (pH, TDS, conductivity, microbial count)
- Energy efficiency of regeneration

### Photocatalytic Coating
**Keywords**: "photocatalytic", "TiO2", "visible light", "UV light", "pollutant degradation", etc.

**Specific Parameters**:
- Substrate type and coating thickness
- Curing temperature and light source (wavelength)
- Target pollutant and catalyst loading
- Adhesion and leaching test methods

**Validation Plan Includes**:
- Pollutant degradation efficiency (>80% in 90 min)
- Reaction kinetics analysis
- Catalyst stability over multiple cycles
- Heavy metal leaching tests (ICP-MS)
- Characterization: SEM, XRD, FTIR, UV-Vis DRS, BET

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Steps

1. **Clone or download** the repository

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file** in the project directory:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**: Visit `http://localhost:8501`

## 💡 Usage Examples

### Example 1: Atmospheric Water Harvesting
**Prompt**:  
*"Design a low-cost porous composite for atmospheric water harvesting using activated carbon, porous silica, hygroscopic salt, stabilizers, and polymer binder."*

**Output**:
- **Category**: `atmospheric_water_harvesting_material`
- **Composition**: Activated carbon (30%), porous silica (25%), salt (20%), polymer (15%), stabilizers (10%)
- **Parameters**: RH 40–90%, water uptake 0.3–0.8 g/g, desorption 50–80°C
- **Validation**: 50–100 wet/dry cycles, salt leaching tests, water quality (pH, TDS, microbial safety)
- **PDF Report**: Includes all parameters, test methods, acceptance criteria

### Example 2: Photocatalytic Coating
**Prompt**:  
*"Photocatalytic TiO2 coating for water purification using UV light"*

**Output**:
- **Category**: `photocatalytic_coating`
- **Parameters**: Substrate (glass/ceramic), coating thickness (0.5–5 μm), light source (UV-A/B), target pollutant (dyes/VOCs)
- **Validation**: >80% degradation efficiency, reaction kinetics, 10-cycle durability, leaching tests
- **Characterization**: SEM, XRD, FTIR, UV-Vis DRS, BET

### Example 3: Generic Material (No Preset)
**Prompt**:  
*"High-performance aluminum alloy for aerospace applications"*

**Output**:
- **Category**: `other_material` (generic)
- **Basic Analysis**: Composition and application description
- **No Preset Parameters**: Falls back to AI-generated recommendations only

## 📄 PDF Reports

Each generated PDF includes:
- ✅ User request and original prompt
- ✅ Material category and target application
- ✅ Composition table with ratios and percentages
- ✅ **Category-Specific Parameters & Targets** (if preset detected)
- ✅ **Validation Plan** with test methods and criteria
- ✅ Professional formatting and disclaimer

## 🔧 Customization

### Adding New Preset Categories

Edit the `MATERIAL_PRESETS` dictionary in `app.py`:

```python
"new_category_name": {
    "display_name": "Human-Readable Name",
    "keywords": ["keyword1", "keyword2", "..."],
    "parameters": {
        "param1": "value or description",
        "param2": "value or description",
        "...": "..."
    },
    "validation_plan": {
        "test1": "criteria or method",
        "test2": "criteria or method",
        "...": "..."
    }
}
```

### Modifying System Prompt

The AI system prompt in `call_openai()` can be customized to adjust how the AI analyzes materials or prioritizes certain aspects.

## 📊 Project Structure

```
material_studio_1/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # OpenAI API key (not in repo)
├── .env.example          # Template for .env
├── .gitignore            # Git exclusions
└── README.md             # This file
```

## ⚠️ Disclaimer

This application generates **AI-powered recommendations** based on materials science knowledge. All suggestions are conditional upon:
- Experimental validation by qualified materials scientists
- Compliance with relevant industry standards
- Consultation with domain experts
- Actual laboratory testing before production use

**Do not use for safety-critical applications without proper validation.**

## 📞 Support

- **OpenAI Issues**: Check [OpenAI API documentation](https://platform.openai.com/docs/guides/gpt)
- **Streamlit Issues**: See [Streamlit docs](https://docs.streamlit.io)
- **Bug Reports**: Provide error messages and example prompts

## 📝 License

This project is provided as-is for educational and research purposes.
