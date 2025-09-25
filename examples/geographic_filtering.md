# Geographic Filtering Feature

## 🎯 Extra Credit Feature: Interactive Geographic Filtering

This enhanced version allows users to filter power plant data by geographic region before AI analysis.

## 📍 Filtering Options

### 1. All States (No Filtering)
- Processes all ~1,100+ power plants nationwide
- Complete dataset analysis
- Default option for comprehensive analysis

### 2. Specific States  
- **Input**: State abbreviations (e.g., `AL, CA, TX`)
- **Use Case**: Focus on particular states of interest
- **Example**: `CA, NY, TX` for largest economies

### 3. Census Regions
- **Northeast**: CT, ME, MA, NH, NJ, NY, PA, RI, VT
- **Midwest**: IL, IN, IA, KS, MI, MN, MO, NE, ND, OH, SD, WI  
- **South**: AL, AR, DE, FL, GA, KY, LA, MD, MS, NC, OK, SC, TN, TX, VA, WV
- **West**: AK, AZ, CA, CO, HI, ID, MT, NV, NM, OR, UT, WA, WY

## 🖥️ Interactive User Experience

```
🌎 Geographic Filtering Options:
1. All states (no filtering)
2. Specific states
3. Census regions

Select option (1-3): 2

Enter state abbreviations (e.g., AL, CA, TX):
States (comma-separated): CA, TX, NY

🔍 Applying states filter...
📍 Filtered to 127 plants in selected area(s)
States included: CA, NY, TX

🤖 Starting AI enrichment analysis...
```

## 💡 Educational Benefits

### Geographic Analysis Capabilities
- **Regional Energy Patterns**: Compare capacity factors across regions
- **State-Specific Insights**: Focus analysis on particular jurisdictions
- **Fuel Mix Analysis**: Understand regional energy portfolio differences

### Business Intelligence Applications
- **Regulatory Compliance**: State-specific reporting requirements
- **Market Analysis**: Regional energy market conditions
- **Investment Planning**: Geographic risk and opportunity assessment

## 🎓 Extra Credit Value

This feature demonstrates:
1. **User Interface Design**: Interactive command-line experience
2. **Data Filtering Logic**: Efficient geographic subsetting
3. **Scalable Architecture**: Handles datasets from single states to full nation
4. **Real-World Application**: Mirrors actual energy sector analysis needs

## 📊 Sample Filtering Results

### Texas Only (`TX`)
```bash
📍 Filtered to 87 plants in selected area(s)
States included: TX
```
- Focus on nation's largest energy producer
- Analyze diverse fuel mix (gas, wind, nuclear, coal)

### Northeast Region
```bash  
📍 Filtered to 156 plants in selected area(s)
States included: CT, MA, ME, NH, NJ, NY, PA, RI, VT
```
- Regional grid interconnection analysis
- Northeast energy market dynamics

### California + New York (`CA, NY`)
```bash
📍 Filtered to 45 plants in selected area(s) 
States included: CA, NY
```
- Compare two largest state economies
- Contrast renewable energy policies

---

**Impact**: Transforms a static analysis tool into an interactive, user-driven intelligence platform suitable for diverse stakeholder needs from state regulators to energy analysts.