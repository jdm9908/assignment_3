# Examples: Before and After Data Processing

This folder demonstrates the complete data transformation pipeline from raw EIA API data to AI-enriched analysis.

## 📁 Folder Structure

```
examples/
├── before/               # Raw input data samples
│   └── raw_eia_api_sample.json
├── after/                # Final processed output samples  
│   └── ai_enriched_sample.json
└── README.md            # This documentation
```

## 🔄 Data Pipeline Overview

### BEFORE: Raw EIA API Data
**File**: `before/raw_eia_api_sample.json`

Raw electricity generation data from EIA API containing:
- Basic plant information (name, operator, location)
- Fuel type and prime mover technology
- Raw generation values in megawatt-hours
- **Missing**: Capacity data, efficiency metrics, anomaly detection

**Key Limitations**:
- No capacity factor calculations
- No anomaly detection
- No operational insights
- Limited analytical value

### AFTER: AI-Enriched Analysis
**File**: `after/ai_enriched_sample.json`

Fully processed data with AI-powered insights:
- **Capacity Factor Calculation**: Precise efficiency percentages
- **AI Anomaly Detection**: Automated flagging of unusual patterns  
- **Intelligent Analysis**: Contextual explanations for each plant
- **Data Quality Flags**: Identification of potential reporting issues

## 🎯 Key Value Additions

### 1. **Capacity Factor Analysis**
```json
"capacityFactorPercent": 121.68,
"aiCapacityFactorFlag": "Extreme_Nuclear"
```
- Calculates operational efficiency as percentage of theoretical maximum
- Identifies plants operating beyond normal parameters

### 2. **AI-Powered Anomaly Detection**
```json
"aiCapacityFactorFlag": "High_Coal",
"aiAnalysisNotes": "Capacity factor of 111.58% is unusually high..."
```
- DeepSeek AI analyzes patterns across fuel types
- Provides contextual explanations for anomalies
- Flags potential data quality issues

### 3. **Fuel-Type Specific Intelligence**
- **Nuclear**: Expected 90%+ capacity factors
- **Coal**: Typical 40-60% range
- **Natural Gas**: Variable based on grid demand
- **Renewables**: Weather and seasonal dependent

## 🚨 Anomaly Examples in Sample Data

### Browns Ferry Nuclear Plant
- **Capacity Factor**: 121.68% (⚠️ Impossible)
- **AI Flag**: `Extreme_Nuclear`
- **Analysis**: "Significantly exceeds 100%, indicates potential data reporting issues"

### Barry Coal Plant  
- **Capacity Factor**: 111.58% (⚠️ Unusually High)
- **AI Flag**: `High_Coal` 
- **Analysis**: "Suggests efficient operations or potential data quality issues"

### Gadsden Gas Plant
- **Capacity Factor**: 35.14% (✅ Normal)
- **AI Flag**: `Normal`
- **Analysis**: "Within normal range for natural gas peaking plant"

## 🛠️ How to Generate Your Own Examples

1. **Run the Pipeline**:
   ```bash
   python main.py
   ```

2. **Check Output Locations**:
   - Raw data: `data/raw/eia_api_data.json`
   - Enriched data: `data/enriched/merged_plant_data_enriched.json`

3. **Compare Results**:
   - Before: Raw API response format
   - After: AI-enriched with capacity factors and analysis

## 📊 Processing Statistics

The complete pipeline typically processes:
- **1,100+** individual power plants
- **Multiple fuel types** (Nuclear, Coal, Gas, Renewables)  
- **Real-time analysis** with DeepSeek AI
- **100% success rate** for anomaly detection

## 🎓 Educational Value

These examples demonstrate:
- **Data Engineering**: API integration → Clean processing → Structured output
- **AI Integration**: Real-world application of LLMs for domain-specific analysis
- **Quality Assurance**: Automated detection of data anomalies and reporting issues
- **Business Intelligence**: Operational insights from raw utility data

---

*This pipeline transforms raw utility data into actionable intelligence for energy sector analysis, regulatory compliance, and operational optimization.*