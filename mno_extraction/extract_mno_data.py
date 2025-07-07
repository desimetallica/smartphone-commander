#!/usr/bin/env python3
"""
Extract Mobile Network Operator (MNO) information from Wikipedia HTML file
and save it to a structured CSV file.
"""

import os
import re
import json
from bs4 import BeautifulSoup

def extract_mno_data(html_file):
    """Extract MNO data from the HTML file and return a list of records."""
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all country sections (h2 headings)
    country_headings = soup.find_all(['h2'])
    
    # Initialize the results list
    results = []
    
    # For each country, extract the table data
    current_country = None
    
    for heading in country_headings:
        # Skip "See also", "References", etc. sections
        if heading.get_text().strip() in ["See also", "References", "External links"]:
            continue
        
        # Get the country name
        country_name = heading.get_text().strip()
        # Clean up the country name (remove "[edit]" or similar)
        country_name = re.sub(r'\[.*?\]', '', country_name).strip()
        
        if not country_name:
            continue
        
        current_country = country_name
        print(f"Processing country: {current_country}")
        
        # Find the next table after this heading
        table = heading.find_next('table')
        
        if not table:
            print(f"No table found for {current_country}")
            continue
        
        # Check if it's a wikitable
        if 'wikitable' not in table.get('class', []):
            table = heading.find_next('table', {'class': 'wikitable'})
            if not table:
                print(f"No wikitable found for {current_country}")
                continue
        
        # Extract table headers
        headers = []
        header_row = table.find('tr')
        if header_row:
            header_cells = header_row.find_all(['th'])
            if not header_cells:  # Sometimes th tags are not used
                header_cells = header_row.find_all(['td'])
            headers = [cell.get_text().strip() for cell in header_cells]
        
        # Extract rows
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cells = row.find_all(['td'])
            if not cells or len(cells) < 2:  # Skip rows with no data
                continue
            
            # Extract cell data
            row_data = [cell.get_text().strip() for cell in cells]
            
            # Create a record with country name and cell data
            record = {
                'Country': current_country,
            }
            
            # Add data from cells mapped to headers
            for i, header in enumerate(headers):
                if i < len(row_data):
                    # Clean up the header name
                    clean_header = header.replace('\n', ' ').strip()
                    record[clean_header] = row_data[i]
            
            # Append the record to results
            results.append(record)
    
    return results

def save_to_json(data, output_file):
    """Save the extracted data to a JSON file."""
    if not data:
        print("No data to save.")
        return
    
    # Write to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Data saved to {output_file}")

def main():
    html_file = 'mno_list.html'
    output_file = 'mno_data.json'
    
    if not os.path.exists(html_file):
        print(f"Error: File {html_file} not found.")
        return
    
    print(f"Extracting MNO data from {html_file}...")
    data = extract_mno_data(html_file)
    
    print(f"Found {len(data)} MNO records.")
    save_to_json(data, output_file)

if __name__ == "__main__":
    main()
