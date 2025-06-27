#!/usr/bin/env python3
"""
Windows Recycle Bin Analyzer

This script analyzes the Windows Recycle Bin directory and provides information about
deleted files including their names, original locations, and content reading capabilities.
"""

import sys
import argparse

from src.analyzer import RecycleBinAnalyzer
from src.reporting import display_results, export_to_csv, export_to_json, export_to_html
from src.sid import get_all_user_sids, get_sid_info, WINDOWS_API_AVAILABLE


def main():
    """Main function to run the Recycle Bin analyzer."""
    parser = argparse.ArgumentParser(
        description='Windows Recycle Bin Analyzer',
        epilog=f"Windows API available: {WINDOWS_API_AVAILABLE} (requires pywin32)"
    )
    parser.add_argument('--show-content', action='store_true', 
                       help='Show content preview for text files')
    parser.add_argument('--max-content-length', type=int, default=1000,
                       help='Maximum content length to display (default: 1000)')
    parser.add_argument('--export-csv', type=str, default='',
                       help='Export results to CSV file')
    parser.add_argument('--export-json', type=str, default='',
                       help='Export results to JSON file')
    parser.add_argument('--export-html', type=str, default='',
                       help='Export results to HTML file with sortable table')
    parser.add_argument('--show-sids', action='store_true',
                       help='Show all user SIDs found on the system')
    
    args = parser.parse_args()
    
    # Check if running on Windows
    if sys.platform != 'win32':
        print("This script is designed for Windows systems only.")
        sys.exit(1)
    
    # Check if pywin32 is available (required)
    if not WINDOWS_API_AVAILABLE:
        print("Error: pywin32 package is required but not available.")
        print("Please install it using: pip install pywin32")
        sys.exit(1)
    
    # Create analyzer and run analysis
    analyzer = RecycleBinAnalyzer()
    
    # Show SIDs if requested
    if args.show_sids:
        print("User SIDs on this system:")
        print("-" * 50)
        sids = get_all_user_sids()
        for sid in sids:
            sid_info = get_sid_info(sid)
            if sid_info['username']:
                if sid_info['description']:
                    print(f"  {sid_info['username']} ({sid_info['description']})")
                else:
                    print(f"  {sid_info['username']} ({sid})")
            else:
                print(f"  {sid}")
        print()
    
    files_info = analyzer.analyze()
    
    # Display results
    display_results(files_info, 
                    show_content=args.show_content, 
                    max_content_length=args.max_content_length)
    
    # Export to CSV if requested
    if args.export_csv:
        export_to_csv(files_info, args.export_csv)
    
    # Export to JSON if requested
    if args.export_json:
        export_to_json(files_info, args.export_json)
    
    # Export to HTML if requested or as default
    if args.export_html:
        export_to_html(files_info, args.export_html)
    elif files_info:  # Auto-export HTML as default if files found
        export_to_html(files_info)


if __name__ == "__main__":
    main() 