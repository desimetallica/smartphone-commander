#!/usr/bin/env python3
"""
Enhance the merged MNO and spectrum data to create a more comprehensive dataset.
"""

import json
import re
from collections import defaultdict

def enhance_mno_spectrum_data(input_file, output_file):
    """Enhance the merged MNO and spectrum data."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create a mapping of operator names to their spectrum data
    operator_spectrum = defaultdict(list)
    for record in data:
        if 'spectrum_data' in record:
            operator_name = record.get('Operator', '')
            country = record.get('Country', '')
            
            # Add country info to each spectrum entry
            for spectrum_entry in record['spectrum_data']:
                spectrum_entry['country'] = country
            
            operator_spectrum[operator_name].extend(record['spectrum_data'])
    
    # Organize data by country
    country_data = defaultdict(list)
    for record in data:
        country = record.get('Country', '')
        if country:
            # Remove spectrum_data from individual records as we'll consolidate it
            if 'spectrum_data' in record:
                del record['spectrum_data']
            
            country_data[country].append(record)
    
    # Create enhanced data structure
    enhanced_data = {
        "operators_by_country": dict(country_data),
        "spectrum_by_operator": dict(operator_spectrum),
        "band_statistics": {}
    }
    
    # Calculate band statistics
    band_stats = defaultdict(lambda: defaultdict(int))
    technology_count = defaultdict(int)
    
    for operator, spectrum_entries in operator_spectrum.items():
        for entry in spectrum_entries:
            band = entry.get('band', '')
            if band:
                # Extract band number
                band_number = re.search(r'Band\s+(\d+)', band)
                if band_number:
                    band_number = band_number.group(1)
                    band_stats[band_number]['total'] += 1
                    
                    # Count by technology
                    tech = entry.get('technology', '')
                    if tech:
                        band_stats[band_number][tech] += 1
                        technology_count[tech] += 1
    
    enhanced_data['band_statistics'] = {
        'by_band': dict(band_stats),
        'by_technology': dict(technology_count)
    }
    
    # Save enhanced data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, indent=4, ensure_ascii=False)
    
    print(f"Enhanced data saved to {output_file}")

def main():
    input_file = 'mno_data_with_spectrum.json'
    output_file = 'enhanced_mno_spectrum.json'
    
    print(f"Enhancing data from {input_file}...")
    enhance_mno_spectrum_data(input_file, output_file)

if __name__ == "__main__":
    main()
