#!/usr/bin/env python3
"""
Example usage of the Windows Recycle Bin Analyzer

This script demonstrates how to use the analyzer programmatically
and shows different export options.
"""

import json
from src.analyzer import RecycleBinAnalyzer
from src.reporting import display_results, export_to_csv, export_to_json
from src.sid import get_all_user_sids
import sys


def main():
    """Example usage of the Recycle Bin Analyzer."""
    
    print("Windows Recycle Bin Analyzer - Example Usage")
    print("=" * 50)
    
    # Create analyzer instance
    analyzer = RecycleBinAnalyzer()
    
    # Show current user SID
    if analyzer.current_user_sid:
        print(f"Current user SID: {analyzer.current_user_sid}")
    else:
        print("Could not determine current user SID")
    
    # Run analysis
    print("Running analysis...")
    files_info = analyzer.analyze()
    
    if not files_info:
        print("No deleted files found in the Recycle Bin.")
        return
    
    print(f"\nFound {len(files_info)} deleted files")
    
    # Example 1: Display results
    print("\n1. Displaying results:")
    display_results(files_info, show_content=False)
    
    # Example 2: Export to CSV
    print("\n2. Exporting to CSV:")
    export_to_csv(files_info, "example_analysis.csv")
    
    # Example 3: Export to JSON
    print("\n3. Exporting to JSON:")
    export_to_json(files_info, "example_analysis.json")
    
    # Example 4: Load and process JSON data
    print("\n4. Loading JSON data for processing:")
    try:
        with open("example_analysis.json", 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print(f"Analysis timestamp: {json_data['analysis_info']['timestamp']}")
        print(f"Total files: {json_data['analysis_info']['total_files']}")
        
        # Process files programmatically
        total_size = sum(file_info['file_size'] for file_info in json_data['files'])
        print(f"Total size of deleted files: {total_size:,} bytes")
        
        # Find text files
        text_files = [f for f in json_data['files'] if f['can_read_content']]
        print(f"Text files that can be read: {len(text_files)}")
        
        # Show largest files
        largest_files = sorted(json_data['files'], key=lambda x: x['file_size'], reverse=True)[:3]
        print("\nLargest deleted files:")
        for i, file_info in enumerate(largest_files, 1):
            print(f"  {i}. {file_info['original_name']} ({file_info['file_size']:,} bytes)")
            print(f"     User: {file_info['username']} (SID: {file_info['sid_folder']})")
            
    except Exception as e:
        print(f"Error processing JSON data: {e}")
    
    print("\nExample usage complete!")


if __name__ == "__main__":
    # Check if running on Windows
    if sys.platform != 'win32':
        print("This example is designed for Windows systems only.")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1) 