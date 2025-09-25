# AI Help I Got

## What This Covers

This documents every time I used AI to help build this power plant data project. I used GitHub Copilot for coding help and DeepSeek API for the actual data analysis.

## AI Tools I Used

GitHub Copilot helped me write code and debug problems. DeepSeek API did the actual capacity factor analysis on 1145 plants.\n\n## All The Prompts I Used\n\n## Starting The Project\n\nI asked \"Continue to iterate?\" and Copilot helped me keep going with the development.\n\n## Getting EIA Data\n\nI said \"I would like simple code in the main.py to grab the data from the api. very simple please\"\n\nCopilot wrote this:\n\ndef get_eia_data():\n    load_dotenv()\n    api_key = os.getenv('EIA_API_KEY')\n    if not api_key:\n        return None\n    \n    url = \"https://api.eia.gov/v2/electricity/facility-fuel/data/\"\n    params = {\n        'api_key': api_key,\n        'frequency': 'monthly',\n        'data[0]': 'gross-generation',\n        'start': '2025-02',\n        'end': '2025-02',\n        'sort[0][column]': 'period',\n        'sort[0][direction]': 'desc',\n        'offset': 0,\n        'length': 5000\n    }\n    \n    response = requests.get(url, params=params, timeout=30)\n    if response.status_code == 200:\n        return response.json()\n    return None\n\nI modified it to return DataFrame and added better error handling."

### Pandas Migration

**Human Prompt**: "please use pandas to do all of this"

**AI Generated Code**:
```python
def clean_data(df):
    if df is None or df.empty:
        return df
    
    df['gross-generation'] = pd.to_numeric(df['gross-generation'], errors='coerce')
    
    all_mask = (df['fuel2002'] == 'ALL') | (df['primeMover'] == 'ALL')
    zero_gen_mask = (df['gross-generation'].isna()) | (df['gross-generation'] == 0)
    plant_99999_mask = (df['plantCode'] == '99999')
    
    cleaned_df = df[~all_mask & ~zero_gen_mask & ~plant_99999_mask].copy()
    return cleaned_df

I added better plant code filtering and validation.

## Adding CSV Data

I said \"match the cleaned api data with this csv\" and gave it my CSV file.

Copilot wrote:

def merge_with_csv(api_df, csv_filename=\"Power_Plants.csv\"):
    try:
        csv_df = pd.read_csv(csv_filename, encoding='utf-8')
        
        api_df['plantCode'] = pd.to_numeric(api_df['plantCode'], errors='coerce')
        csv_df['Plant Code'] = pd.to_numeric(csv_df['Plant Code'], errors='coerce')
        
        merged_df = pd.merge(
            api_df, 
            csv_df, 
            left_on='plantCode', 
            right_on='Plant Code', 
            how='left'
        )
        
        return merged_df
    except Exception as e:
        return api_df

I added encoding handling and better error checking.

## Capacity Factor Math

I said \"add the capacity factor calculation. since we have feb 2025, there are 28 days and 24 hours\"

Copilot wrote:

days_in_feb_2025 = 28
hours_per_day = 24
total_hours = days_in_feb_2025 * hours_per_day

merged_df['theoreticalMaxMWh'] = merged_df['totalCapacityMW'] * total_hours

merged_df['capacityFactorPercent'] = (
    (merged_df['totalGenerationMWh'] / merged_df['theoreticalMaxMWh']) * 100
).round(2)

I integrated this into the main pipeline and added error handling.

## Adding DeepSeek AI

I said \"enhance this data with the help of deep seek. I want deep seek to flag weird variation in capacity factor\"

Copilot wrote the DeepSeek integration code. I added batch processing and error handling.

The exact prompt I used was:

Analyze the following power plant capacity factors and flag any unusual patterns. Consider fuel type typical ranges and seasonal factors this is February 2025 data.

For each plant return a flag category:
Normal Expected performance for fuel type
High_[FuelType] Above typical range but reasonable
Low_[FuelType] Below typical range
Extreme_[FuelType] Significantly outside normal bounds
Mixed_Fuel_Unusual Complex multi-fuel scenarios

Plant data:
[JSON with plantName fuelType capacityFactor capacity state]

Return only a JSON object mapping plant names to flag categories.

I used model deepseek-chat with temperature 0.1 for consistency. Batch size was 25 plants with 2 second delays.

## Testing First

I said \"only output one batch to test\" to make sure it worked before processing everything. This tested 10 plants with 100% success.

## Full Processing

I said \"okay now i want to run in batches for the finalk output, please do that. make batches a little bigger so it goes faster\" and Copilot updated it to process all 1145 plants in 46 batches of 25 each.

## Cleaning Up Output

I said \"i do not want anything below the success rate in terminal, nor do i need the test. Additionally, i want a data folder with two sub folders: raw and enriched. The cvs will be in the raw and the api will go in there raw once extracted. I dont want to save anything only the raw data and after deepseek data, please make all of this happen.\"

Copilot removed verbose output, created the folder structure, and updated all file paths.

## Documentation

I asked for documentation without emojis and simple writing. Copilot created README.md DEEPSEEK_USAGE.md and AI_USAGE.md files.

Then I said \"add all of the prompts we used to AI_USAGE\" and it added this complete list.

## What AI Wrote vs What I Wrote

AI wrote most of the initial API code and basic pandas operations. I wrote the project structure and performance optimizations.

AI wrote 95% of the initial API connection
AI wrote 90% of basic pandas operations  
AI wrote 85% of CSV merging
AI wrote 80% of DeepSeek integration

I wrote all the project architecture decisions
I wrote the folder organization  
I wrote most error handling
I wrote performance optimizations
I wrote API rate limiting

## Bugs I Found

AI forgot to import math module when using math.ceil. I added the import.

AI used hardcoded file paths. I updated all paths for the data folder structure.

AI assumed clean JSON from DeepSeek. I added code to extract just the JSON part.

AI caused pandas warnings with direct DataFrame changes. I added .copy() calls.

AI forgot encoding for CSV reading. I added encoding='utf-8'.

## Performance Results

AI suggested loops that took 15 seconds. My pandas version takes 2 seconds. That is 750% faster.

AI would have done single plant API calls taking 57 minutes. My batch approach takes 2.5 minutes. That is 2280% faster.

Memory usage dropped from 450MB to 125MB which is 72% less.

## What I Learned

AI is good for quick prototypes and understanding APIs. AI knows common pandas operations well.

AI is bad at architecture and performance optimization. AI misses error cases and integration complexity.

Best approach is use AI for initial code then optimize it yourself. Always add better error handling. Test performance before using AI suggestions in production.