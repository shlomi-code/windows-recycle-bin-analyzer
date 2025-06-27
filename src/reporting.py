from pathlib import Path
from typing import List, Dict
import csv
import json
from datetime import datetime

def display_results(files_info: List[Dict], show_content: bool = False, max_content_length: int = 1000):
    """Display the analysis results."""
    if not files_info:
        print("No deleted files found in the Recycle Bin.")
        return
    
    print(f"\nFound {len(files_info)} deleted files:")
    print("=" * 80)
    
    for i, file_info in enumerate(files_info, 1):
        print(f"\n{i}. File Information:")
        print(f"   Original Name: {file_info.get('original_name', 'Unknown')}")
        print(f"   Original Location: {file_info.get('original_path', 'Unknown')}")
        print(f"   File Size: {file_info.get('file_size', 0):,} bytes")
        print(f"   Delete Time: {file_info.get('delete_time', 'Unknown')}")
        
        # Display user-friendly SID information
        sid_display = file_info.get('sid_display', file_info.get('sid_folder', 'Unknown'))
        print(f"   User: {sid_display}")
        
        print(f"   Recycled Name: {file_info.get('recycled_name', 'Unknown')}")
        print(f"   Can Read Content: {file_info.get('can_read_content', False)}")
        
        if show_content and file_info.get('can_read_content') and file_info.get('actual_file_path'):
            _display_file_content(file_info['actual_file_path'], max_content_length)
        
        print("-" * 40)

def _display_file_content(file_path: Path, max_length: int):
    """Display file content if it's a text file."""
    try:
        # Check if it's likely a text file
        text_extensions = {'.txt', '.log', '.csv', '.json', '.xml', '.html', '.htm', '.css', '.js', '.py', '.java', '.cpp', '.c', '.h', '.md', '.rst'}
        
        if file_path.suffix.lower() in text_extensions:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_length)
                print(f"   Content Preview ({len(content)} chars):")
                print(f"   {repr(content[:200])}...")
                if len(content) > 200:
                    print(f"   ... (truncated, max {max_length} chars)")
        else:
            print(f"   Content: Binary file (extension: {file_path.suffix})")
            
    except Exception as e:
        print(f"   Content: Error reading file - {e}")

def export_to_csv(files_info: List[Dict], output_file: str = "recycle_bin_analysis.csv"):
    """Export the analysis results to a CSV file."""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['original_name', 'original_path', 'file_size', 'delete_time', 'sid_folder', 'username', 'recycled_name', 'can_read_content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for file_info in files_info:
                # Prepare row data
                row = {
                    'original_name': file_info.get('original_name', ''),
                    'original_path': file_info.get('original_path', ''),
                    'file_size': file_info.get('file_size', 0),
                    'delete_time': str(file_info.get('delete_time', '')),
                    'sid_folder': file_info.get('sid_folder', ''),
                    'username': file_info.get('sid_display', ''),
                    'recycled_name': file_info.get('recycled_name', ''),
                    'can_read_content': file_info.get('can_read_content', False)
                }
                writer.writerow(row)
        
        print(f"\nAnalysis exported to: {output_file}")
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

def export_to_json(files_info: List[Dict], output_file: str = "recycle_bin_analysis.json"):
    """Export the analysis results to a JSON file."""
    try:
        # Prepare data for JSON export
        json_data = {
            'analysis_info': {
                'timestamp': datetime.now().isoformat(),
                'total_files': len(files_info),
                'export_format': 'json'
            },
            'files': []
        }
        
        for file_info in files_info:
            # Convert file_info to JSON-serializable format
            json_file_info = {
                'original_name': file_info.get('original_name', ''),
                'original_path': str(file_info.get('original_path', '')),
                'file_size': file_info.get('file_size', 0),
                'delete_time': str(file_info.get('delete_time', '')),
                'sid_folder': file_info.get('sid_folder', ''),
                'username': file_info.get('sid_display', ''),
                'recycled_name': file_info.get('recycled_name', ''),
                'can_read_content': file_info.get('can_read_content', False),
                'actual_file_path': str(file_info.get('actual_file_path', '')) if file_info.get('actual_file_path') else None
            }
            json_data['files'].append(json_file_info)
        
        # Write to JSON file with proper formatting
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"\nAnalysis exported to JSON: {output_file}")
        
    except Exception as e:
        print(f"Error exporting to JSON: {e}") 