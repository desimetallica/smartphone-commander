#!/usr/bin/env python3
"""
Extract band information from spectrum.php and merge it with operator data in mno_data.json.
"""

import json
import re
from bs4 import BeautifulSoup

def extract_spectrum_data(spectrum_file):
    """Extract band information from spectrum.php file."""
    
    with open(spectrum_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize a dictionary to store spectrum data by operator
    spectrum_data = {}
    
    # Get all band divs
    band_divs = soup.find_all('div', class_='band')
    
    # Process each band div to extract information
    for band_div in band_divs:
        # Get band title (if exists)
        band_title = band_div.find('h3')
        if not band_title:
            continue
        
        band_name = band_title.get_text().strip()
        
        # Skip if it's an alternative configuration
        if band_div.find('span', class_='altconf'):
            continue
        
        # Extract band pieces (operator specific allocations)
        band_pieces = band_div.find_all('div', class_=lambda x: x and any(op in x for op in 
                                                               ['tim_', 'vodafone_', 'iliad_', 'wind_']))
        
        for piece in band_pieces:
            # Determine operator from class
            classes = piece.get('class', [])
            operator = None
            technology = None
            
            for cls in classes:
                if 'tim_' in cls:
                    operator = 'TIM'
                    technology = cls.replace('tim_', '')
                elif 'vodafone_' in cls:
                    operator = 'Vodafone'
                    technology = cls.replace('vodafone_', '')
                elif 'iliad_' in cls:
                    operator = 'iliad'
                    technology = cls.replace('iliad_', '')
                elif 'wind_' in cls:
                    operator = 'WindTre'
                    technology = cls.replace('wind_', '')
            
            if not operator:
                continue
            
            # Extract detailed information from the band piece
            details = {}
            spans = piece.find_all('span')
            for span in spans:
                text = span.get_text().strip()
                
                # Extract bandwidth
                bandwidth_match = re.search(r'Bandwidth\s+(\d+)\s*MHz', text)
                if bandwidth_match:
                    details['bandwidth'] = f"{bandwidth_match.group(1)} MHz"
                
                # Extract EARFCN/ARFCN/SSB-ARFCN
                arfcn_match = re.search(r'(EARFCN|ARFCN|SSB-ARFCN)\s+(.+?)($|\s)', text)
                if arfcn_match:
                    details[arfcn_match.group(1).lower()] = arfcn_match.group(2).strip()
                
                # Extract max speed
                speed_match = re.search(r'Max Speed(?:\s*\S*)\s+(.+?)($|\s)', text)
                if speed_match:
                    details['max_speed'] = speed_match.group(1).strip()
            
            # Map technology codes to readable names
            tech_mapping = {
                'umts': 'UMTS (3G)',
                'lte': 'LTE (4G)',
                'nr': 'NR (5G)',
                'dss': 'DSS (4G/5G)'
            }
            
            if technology in tech_mapping:
                details['technology'] = tech_mapping[technology]
            else:
                details['technology'] = technology
            
            # Add band information
            details['band'] = band_name
            
            # Add to spectrum data dictionary
            if operator not in spectrum_data:
                spectrum_data[operator] = []
            
            spectrum_data[operator].append(details)
    
    return spectrum_data

def merge_with_mno_data(mno_data_file, spectrum_data):
    """Merge MNO data with spectrum data."""
    
    with open(mno_data_file, 'r', encoding='utf-8') as f:
        mno_data = json.load(f)
    
    # Create operator name mapping to handle different naming conventions
    operator_mapping = {
        'TIM': ['TIM', 'Telecom Italia', 'TIM S.p.A.'],
        'Vodafone': ['Vodafone', 'Vodafone Italia', 'Vodafone Italy'],
        'iliad': ['iliad', 'Iliad Italia', 'Iliad Italy'],
        'WindTre': ['WindTre', 'Wind Tre', 'WINDTRE', 'Wind Tre S.p.A.']
    }
    
    # Reverse mapping for lookup
    reverse_mapping = {}
    for std_name, variations in operator_mapping.items():
        for variation in variations:
            reverse_mapping[variation.lower()] = std_name
    
    # Add spectrum data to MNO data
    for record in mno_data:
        operator_name = record.get('Operator', '')
        
        # Try to match operator name
        matched_operator = None
        
        # Direct match
        if operator_name in spectrum_data:
            matched_operator = operator_name
        else:
            # Try case-insensitive match with variations
            op_lower = operator_name.lower()
            if op_lower in reverse_mapping and reverse_mapping[op_lower] in spectrum_data:
                matched_operator = reverse_mapping[op_lower]
        
        if matched_operator:
            record['spectrum_data'] = spectrum_data[matched_operator]
    
    return mno_data

def save_merged_data(data, output_file):
    """Save merged data to a JSON file."""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Merged data saved to {output_file}")

def main():
    spectrum_file = 'spectrum.php'
    mno_data_file = 'mno_data.json'
    output_file = 'mno_data_with_spectrum.json'
    
    print(f"Extracting spectrum data from {spectrum_file}...")
    spectrum_data = extract_spectrum_data(spectrum_file)
    
    print(f"Merging with MNO data from {mno_data_file}...")
    merged_data = merge_with_mno_data(mno_data_file, spectrum_data)
    
    print(f"Found spectrum data for operators: {', '.join(spectrum_data.keys())}")
    save_merged_data(merged_data, output_file)

if __name__ == "__main__":
    main()
