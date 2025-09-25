#!/usr/bin/env python3
"""
EIA API Data Processing Pipeline with AI Enhancement
Fetches, cleans, and analyzes EIA electricity data with DeepSeek AI
"""

import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from deepseek_enrichment import enrich_with_deepseek


def get_user_geographic_filter():
    """Get user input for geographic filtering.
    
    Returns:
        str: Selected filter option ('all', 'states', 'regions')
        list: List of selected states/regions or None for 'all'
    """
    print("\n🌎 Geographic Filtering Options:")
    print("1. All states (no filtering)")
    print("2. Specific states")
    print("3. Census regions")
    
    while True:
        try:
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                return 'all', None
            elif choice == '2':
                print("\nEnter state abbreviations (e.g., AL, CA, TX):")
                states = input("States (comma-separated): ").strip().upper()
                if states:
                    state_list = [s.strip() for s in states.split(',')]
                    return 'states', state_list
            elif choice == '3':
                print("\nCensus Regions:")
                print("- Northeast (CT, ME, MA, NH, NJ, NY, PA, RI, VT)")
                print("- Midwest (IL, IN, IA, KS, MI, MN, MO, NE, ND, OH, SD, WI)")
                print("- South (AL, AR, DE, FL, GA, KY, LA, MD, MS, NC, OK, SC, TN, TX, VA, WV)")
                print("- West (AK, AZ, CA, CO, HI, ID, MT, NV, NM, OR, UT, WA, WY)")
                
                region = input("Enter region name: ").strip().lower()
                regions = {
                    'northeast': ['CT', 'ME', 'MA', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT'],
                    'midwest': ['IL', 'IN', 'IA', 'KS', 'MI', 'MN', 'MO', 'NE', 'ND', 'OH', 'SD', 'WI'],
                    'south': ['AL', 'AR', 'DE', 'FL', 'GA', 'KY', 'LA', 'MD', 'MS', 'NC', 'OK', 'SC', 'TN', 'TX', 'VA', 'WV'],
                    'west': ['AK', 'AZ', 'CA', 'CO', 'HI', 'ID', 'MT', 'NV', 'NM', 'OR', 'UT', 'WA', 'WY']
                }
                
                if region in regions:
                    return 'regions', regions[region]
                else:
                    print("❌ Invalid region. Please try again.")
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\n⚠️ Using all states (no filtering)")
            return 'all', None


def apply_geographic_filter(df, filter_type, filter_list):
    """Apply geographic filtering to the dataframe.
    
    Args:
        df: pandas DataFrame with plant data
        filter_type: str ('all', 'states', 'regions')
        filter_list: list of state codes or None
        
    Returns:
        pandas.DataFrame: Filtered dataframe
    """
    if filter_type == 'all' or filter_list is None:
        return df
    
    # Create state abbreviation mapping from state descriptions
    state_mapping = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
        'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
        'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
        'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
        'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
        'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
    }
    
    # Add state abbreviation column
    df['stateAbbr'] = df['stateDescription'].map(state_mapping)
    
    # Filter by selected states
    filtered_df = df[df['stateAbbr'].isin(filter_list)].copy()
    
    print(f"\n📍 Filtered to {len(filtered_df)} plants in selected area(s)")
    print(f"States included: {', '.join(sorted(set(filtered_df['stateAbbr'].dropna())))}")
    
    return filtered_df


def get_eia_data():
    """Fetch data from EIA API and return as pandas DataFrame.

    Returns:
        pandas.DataFrame: EIA electricity generation data
    """
    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = os.getenv('EIA_API_KEY')
    if not api_key:
        return None

    # EIA API endpoint for electricity data (monthly facility-fuel data)
    url = "https://api.eia.gov/v2/electricity/facility-fuel/data/"

    # Parameters matching the specific API request
    params = {
        'api_key': api_key,
        'frequency': 'monthly',
        'data[0]': 'gross-generation',
        'start': '2025-02',
        'end': '2025-02',
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc',
        'offset': 0,
        'length': 5000
    }

    try:
        # Make the API request
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            records = data.get('response', {}).get('data', [])

            # Convert to pandas DataFrame
            df = pd.DataFrame(records)
            return df
        else:
            return None

    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None


def save_data(df, filename="eia_data.json", data_type="dataframe"):
    """Save data to a JSON file.

    Args:
        df: Data to save (DataFrame or dict)
        filename: Output filename
        data_type: Type of data being saved
    """
    if df is not None and not df.empty:
        if data_type == "dataframe":
            # Save DataFrame as JSON
            df.to_json(filename, orient='records', indent=2)
        else:
            # Save as original JSON structure
            with open(filename, 'w') as f:
                json.dump(df, f, indent=2)


def clean_data(df):
    """Clean EIA data by removing unwanted records.

    Removes aggregate records, zero generation, and plant code 99999.

    Args:
        df (pandas.DataFrame): Raw EIA data

    Returns:
        pandas.DataFrame: Cleaned data
    """
    if df is None or df.empty:
        return df

    # Convert gross-generation to numeric, handling errors
    df['gross-generation'] = pd.to_numeric(
        df['gross-generation'], errors='coerce'
    )

    # Count records to be removed
    all_mask = (df['fuel2002'] == 'ALL') | (df['primeMover'] == 'ALL')
    zero_gen_mask = (
        (df['gross-generation'].isna()) |
        (df['gross-generation'] == 0)
    )
    plant_99999_mask = (df['plantCode'] == '99999')

    # Filter out unwanted records (including plant code 99999)
    cleaned_df = df[~all_mask & ~zero_gen_mask & ~plant_99999_mask].copy()

    return cleaned_df


def aggregate_plants(df):
    """Aggregate generation data by plant code.

    Combines multiple fuel records per plant into single records.

    Args:
        df (pandas.DataFrame): Cleaned EIA data

    Returns:
        pandas.DataFrame: Aggregated plant data
    """
    if df is None or df.empty:
        return df

    # Group by plantCode and aggregate
    plant_groups = df.groupby('plantCode')

    # Create aggregated DataFrame
    aggregated_data = []

    for plant_code, group in plant_groups:
        # Get plant info (same for all rows in group)
        plant_info = group.iloc[0]

        # Aggregate generation (sum all fuel types)
        total_generation = group['gross-generation'].sum()

        # Combine fuel type descriptions (unique values)
        fuel_types = group['fuelTypeDescription'].dropna().unique()
        if len(fuel_types) > 0:
            combined_fuel_desc = ', '.join(sorted(fuel_types))
        else:
            combined_fuel_desc = 'Mixed'

        # Create detailed fuel breakdown
        fuel_breakdown = []
        for _, row in group.iterrows():
            fuel_breakdown.append({
                'fuel2002': row['fuel2002'],
                'fuelTypeDescription': row['fuelTypeDescription'],
                'primeMover': row['primeMover'],
                'generation': row['gross-generation']
            })

        # Create aggregated record
        agg_record = {
            'period': plant_info['period'],
            'plantCode': plant_code,
            'plantName': plant_info['plantName'],
            'state': plant_info['state'],
            'stateDescription': plant_info['stateDescription'],
            'fuelTypeDescription': combined_fuel_desc,
            'gross-generation': total_generation,
            'gross-generation-units': plant_info['gross-generation-units'],
            'fuelTypes': fuel_breakdown
        }

        aggregated_data.append(agg_record)

    # Convert to DataFrame and sort by generation
    aggregated_df = pd.DataFrame(aggregated_data)
    aggregated_df = aggregated_df.sort_values(
        'gross-generation', ascending=False
    ).reset_index(drop=True)

    return aggregated_df


def merge_with_csv(api_df, csv_filename="data/raw/Power_Plants.csv"):
    """Merge API data with plant database CSV.

    Adds geographic coordinates, capacity, and ownership information.

    Args:
        api_df (pandas.DataFrame): Aggregated EIA data
        csv_filename (str): Path to plant database CSV

    Returns:
        pandas.DataFrame: Merged plant data with enhanced information
    """
    try:
        # Load the CSV plant data
        csv_df = pd.read_csv(csv_filename)

        # Convert Plant_Code to string for consistent matching
        api_df['plantCode'] = api_df['plantCode'].astype(str)
        csv_df['Plant_Code'] = csv_df['Plant_Code'].astype(str)

        # Merge on plant code
        merged_df = pd.merge(
            api_df,
            csv_df,
            left_on='plantCode',
            right_on='Plant_Code',
            how='left'
        )

        # Create the final dataset
        final_data = []

        for _, row in merged_df.iterrows():
            # Create address from components
            address_parts = []
            if pd.notna(row.get('Street_Address')):
                address_parts.append(str(row['Street_Address']))
            if pd.notna(row.get('City')):
                address_parts.append(str(row['City']))
            if pd.notna(row.get('State_y')):
                address_parts.append(str(row['State_y']))
            if pd.notna(row.get('Zip')):
                address_parts.append(str(row['Zip']))

            address = ', '.join(address_parts) if address_parts else None

            # Create capacity dictionary for non-zero capacity columns
            capacity_dict = {}
            capacity_columns = [
                'Bat_MW', 'Bio_MW', 'Coal_MW', 'Geo_MW', 'Hydro_MW',
                'HydroPS_MW', 'NG_MW', 'Nuclear_MW', 'Crude_MW',
                'Solar_MW', 'Wind_MW', 'Other_MW'
            ]

            for cap_col in capacity_columns:
                cap_value = row.get(cap_col, 0)
                if pd.notna(cap_value) and float(cap_value) > 0:
                    capacity_dict[cap_col] = float(row[cap_col])

            # Determine data source
            has_csv_data = pd.notna(row.get('Plant_Name'))
            data_source = "API_CSV_Merged" if has_csv_data else "API_Only"

            # Create final record
            # Calculate capacity factor for February 2025 (28 days, 24
            # hours/day)
            capacity_factor = None
            total_mw = row.get('Total_MW')
            generation = row.get('gross-generation')

            if (pd.notna(total_mw) and pd.notna(generation) and
                    float(total_mw or 0) > 0):

                capacity_mw = float(total_mw)
                generation_mwh = float(generation)
                # 28 days in Feb 2025
                max_possible_generation = capacity_mw * 24 * 28
                capacity_factor = (
                    generation_mwh / max_possible_generation) * 100

            # Create final record with cleaner conditional assignments
            plant_name_csv = row.get('Plant_Name')
            plant_name = plant_name_csv if pd.notna(
                plant_name_csv) else row.get('plantName')

            utility_name = row.get('Utility_Name')
            utility_name = utility_name if pd.notna(utility_name) else None

            longitude = row.get('Longitude')
            longitude = float(longitude) if pd.notna(longitude) else None

            latitude = row.get('Latitude')
            latitude = float(latitude) if pd.notna(latitude) else None

            state_y = row.get('State_y')
            state = state_y if pd.notna(state_y) else row.get('state')

            total_mw_val = row.get('Total_MW')
            total_capacity = float(total_mw_val) if pd.notna(
                total_mw_val) else None

            prim_source = row.get('PrimSource')
            primary_source = prim_source if pd.notna(prim_source) else None

            source_desc = row.get('source_desc')
            source_description = source_desc if pd.notna(source_desc) else None

            final_record = {
                'plantCode': row['plantCode'],
                'plantName': plant_name,
                'utilityName': utility_name,
                'address': address,
                'longitude': longitude,
                'latitude': latitude,
                'state': state,
                'stateDescription': row.get('stateDescription'),
                'period': row['period'],
                'grossGeneration': row['gross-generation'],
                'grossGenerationUnits': row['gross-generation-units'],
                'fuelTypeDescription': row['fuelTypeDescription'],
                'fuelTypes': row['fuelTypes'],
                'totalCapacityMW': total_capacity,
                'capacityByType': capacity_dict,
                'capacityFactorPercent': capacity_factor,
                'primarySource': primary_source,
                'sourceDescription': source_description,
                'techDescription': (
                    row.get('tech_desc') if pd.notna(
                        row.get('tech_desc')) else None),
                'sectorName': (
                    row.get('sector_name') if pd.notna(
                        row.get('sector_name')) else None),
                'dataSource': data_source}

            final_data.append(final_record)

        # Convert to DataFrame and sort by generation
        final_df = pd.DataFrame(final_data)
        final_df = final_df.sort_values(
            'grossGeneration', ascending=False
        ).reset_index(drop=True)

        return final_df

    except FileNotFoundError:
        # If CSV not found, return original API data
        return api_df
    except Exception:
        # If merge fails, return original API data
        return api_df


def main():
    """Main function - Complete EIA data processing with AI enrichment.

    Fetches EIA data, cleans it, merges with plant database, and runs
    DeepSeek AI analysis for capacity factor anomaly detection.
    """
    # Get data from API as DataFrame
    df = get_eia_data()

    if df is not None and not df.empty:
        # Save raw API data
        save_data(df, "data/raw/eia_api_data.json")

        # Clean the data using pandas
        cleaned_df = clean_data(df)

        # Aggregate plants by plantCode
        aggregated_df = aggregate_plants(cleaned_df)

        # Merge with CSV plant data
        merged_df = merge_with_csv(aggregated_df)
        
        # Get user input for geographic filtering
        filter_type, filter_list = get_user_geographic_filter()
        
        # Apply geographic filtering
        if filter_type != 'all':
            print(f"\n🔍 Applying {filter_type} filter...")
            merged_df = apply_geographic_filter(merged_df, filter_type, filter_list)
        else:
            print("\n🌍 Processing all states")

        # Save final merged data to raw folder (this is our processed raw data)
        save_data(merged_df, "data/raw/merged_plant_data.json")
        
        # Run AI enrichment analysis
        print("\n🤖 Starting AI enrichment analysis...")
        enrich_with_deepseek()


if __name__ == "__main__":
    main()
