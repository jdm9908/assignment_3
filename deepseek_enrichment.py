#!/usr/bin/env python3
"""
DeepSeek AI Enhancement for Power Plant Capacity Factor Analysis
Processes merged plant data to flag unusual capacity factor variations
"""

import json
import math
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv


def flag_basic_capacity_factor(row):
    """Basic capacity factor flagging without AI (fallback).

    Args:
        row: DataFrame row containing plant data

    Returns:
        str: Flag indicating normal or unusual capacity factor
    """
    if pd.isna(row.get('capacityFactorPercent')):
        return 'No_Data'

    cf = row.get('capacityFactorPercent', 0)
    fuel_desc = str(row.get('fuelTypeDescription', '')).lower()

    # Basic rules based on fuel type expectations
    if 'nuclear' in fuel_desc:
        if cf < 70 or cf > 110:
            return 'Unusual_Nuclear'
    elif any(fuel in fuel_desc for fuel in ['natural gas', 'gas', 'coal']):
        if cf < 20 or cf > 90:
            return 'Unusual_Fossil'
    elif any(fuel in fuel_desc for fuel in ['hydro', 'water']):
        if cf < 10 or cf > 80:
            return 'Unusual_Hydro'
    elif any(fuel in fuel_desc for fuel in ['wind']):
        if cf < 5 or cf > 60:
            return 'Unusual_Wind'
    elif any(fuel in fuel_desc for fuel in ['solar', 'sun']):
        if cf < 5 or cf > 50:
            return 'Unusual_Solar'

    return 'Normal'


def analyze_batch_with_deepseek(batch_data, api_key):
    """Analyze a batch of plants with DeepSeek AI.

    Args:
        batch_data: List of plant data dictionaries
        api_key: DeepSeek API key for authentication

    Returns:
        list: Analysis results for each plant in batch
    """
    try:
        # Create analysis prompt
        prompt = f"""
Analyze these power plants' capacity factors for February 2025.
Flag unusual variations based on these typical ranges:

- Nuclear plants: 90%+ (highest)
- Natural gas: 50-70%
- Coal: 40-60%
- Hydroelectric: 30-60%
- Wind: 20-40% (intermittent)
- Solar PV: 20-30% (intermittent)

Plants to analyze:
{json.dumps(batch_data, indent=2)}

For each plant, respond with ONLY a JSON object mapping plant names to flags:
- "Normal" - within expected range
- "High_[FuelType]" - unusually high for fuel type
- "Low_[FuelType]" - unusually low for fuel type
- "Extreme_[FuelType]" - extremely unusual
- "Mixed_Fuel_Unusual" - for mixed fuel plants with odd performance

Example response format:
{{"Plant Name 1": "Normal", "Plant Name 2": "High_Nuclear",
"Plant Name 3": "Low_Solar"}}
"""

        # Call DeepSeek API
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']

            # Parse JSON response
            try:
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    flags = json.loads(json_match.group())
                    return flags, True  # Success
                else:
                    return {}, False  # Failed to parse
            except json.JSONDecodeError:
                return {}, False  # Failed to parse
        else:
            return {}, False  # API failed

    except Exception:
        return {}, False  # Error occurred


def enrich_with_deepseek():
    """Main function to enrich merged plant data with DeepSeek AI analysis.

    Processes merged plant data and adds AI-generated capacity factor flags.
    """

    # Load environment variables
    load_dotenv()
    deepseek_api_key = os.getenv('DS_API_KEY')

    if not deepseek_api_key:
        print("❌ Error: DS_API_KEY not found in .env file")
        print("Please add your DeepSeek API key to .env file:")
        print("DS_API_KEY=your_key_here")
        return

    try:
        # Load merged plant data
        print("📁 Loading merged plant data...")
        df = pd.read_json("data/raw/merged_plant_data.json")
        print(f"✅ Loaded {len(df)} plant records")

        # Start with basic flags for all plants
        print("🔧 Applying basic capacity factor rules...")
        df['capacityFactorFlag'] = df.apply(
            lambda row: flag_basic_capacity_factor(row), axis=1
        )

        # Prepare data for AI analysis
        analysis_data = []
        for _, row in df.iterrows():
            has_capacity_factor = pd.notna(row.get('capacityFactorPercent'))
            has_fuel_type = pd.notna(row.get('fuelTypeDescription'))
            if has_capacity_factor and has_fuel_type:
                analysis_data.append({
                    'plantName': row.get('plantName', 'Unknown'),
                    'fuelType': row.get('fuelTypeDescription', 'Unknown'),
                    'capacityFactor': row.get('capacityFactorPercent'),
                    'capacity': row.get('totalCapacityMW'),
                    'state': row.get('state', 'Unknown')
                })

        print(f"📊 Prepared {len(analysis_data)} plants for AI analysis")

        # Process all data in larger batches for faster processing
        batch_size = 25
        total_batches = math.ceil(len(analysis_data) / batch_size)
        flagged_plants = {}
        successful_ai_analyses = 0
        failed_ai_analyses = 0

        print(f"🔄 Processing all {len(analysis_data)} plants in batches "
              f"of {batch_size} ({total_batches} total batches)...")

        # Process all plants in batches
        for i in range(0, len(analysis_data), batch_size):
            batch_num = (i // batch_size) + 1
            batch = analysis_data[i:i + batch_size]

            print(f"⏳ Processing batch {batch_num}/{total_batches} "
                  f"({len(batch)} plants)...")

            # Analyze batch with DeepSeek
            flags, success = analyze_batch_with_deepseek(
                batch, deepseek_api_key)

            if success and flags:
                flagged_plants.update(flags)
                successful_ai_analyses += len(batch)
                print(f"✅ Batch {batch_num} completed successfully")
            else:
                failed_ai_analyses += len(batch)
                print(f"⚠️  Batch {batch_num} failed - using basic flags")
                # Use basic flags for failed batch
                for plant in batch:
                    basic_flag = flag_basic_capacity_factor({
                        'capacityFactorPercent': plant['capacityFactor'],
                        'fuelTypeDescription': plant['fuelType']
                    })
                    flagged_plants[plant['plantName']] = basic_flag

            # Small delay to avoid hitting rate limits
            time.sleep(2)

        # Update DataFrame with AI flags
        print("🔄 Updating plant records with AI analysis...")
        for plant_name, flag in flagged_plants.items():
            mask = df['plantName'] == plant_name
            if mask.any():
                df.loc[mask, 'capacityFactorFlag'] = f"AI_{flag}"

        # Save enriched data
        print("💾 Saving AI-enriched data...")
        df.to_json(
            'data/enriched/merged_plant_data_enriched.json',
            orient='records',
            indent=2)

        # Summary statistics
        print("\n📈 AI Analysis Summary:")
        print(f"Total plants analyzed: {len(analysis_data)}")
        print(f"Successful AI analyses: {successful_ai_analyses}")
        print(f"Failed AI analyses: {failed_ai_analyses}")
        success_rate = (successful_ai_analyses / len(analysis_data) * 100)
        print(f"Success rate: {success_rate:.1f}%")

        enhanced_file = "data/enriched/merged_plant_data_enriched.json"
        print(
            f"\n✅ Analysis complete! Enhanced data saved to: {enhanced_file}")

    except FileNotFoundError:
        print("❌ Error: data/raw/merged_plant_data.json not found")
        print("Please run main.py first to generate the merged plant data")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")


if __name__ == "__main__":
    enrich_with_deepseek()
