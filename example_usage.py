#!/usr/bin/env python3
"""
Example usage of the Windows Recycle Bin Analyzer

This script demonstrates how to use the RecycleBinAnalyzer class programmatically
to analyze the Recycle Bin and perform custom operations on the results.
"""

from src.analyzer import RecycleBinAnalyzer
from src.reporting import export_to_csv, _display_file_content
from src.sid import get_all_user_sids
import sys


def main():
    """Example usage of the RecycleBinAnalyzer."""
    
    print("Windows Recycle Bin Analyzer - Example Usage")
    print("=" * 50)
    
    # Create analyzer instance
    analyzer = RecycleBinAnalyzer()
    
    # Show current user SID
    if analyzer.current_user_sid:
        print(f"Current user SID: {analyzer.current_user_sid}")
    else:
        print("Could not determine current user SID")
    
    # Perform analysis
    print("\nAnalyzing Recycle Bin...")
    files_info = analyzer.analyze()
    
    if not files_info:
        print("No deleted files found in the Recycle Bin.")
        return
    
    print(f"\nFound {len(files_info)} deleted files.")
    
    # Example 1: Display basic information
    print("\n1. Basic File Information:")
    print("-" * 30)
    for i, file_info in enumerate(files_info[:5], 1):  # Show first 5 files
        print(f"{i}. {file_info.get('original_name', 'Unknown')}")
        print(f"   Location: {file_info.get('original_path', 'Unknown')}")
        print(f"   Size: {file_info.get('file_size', 0):,} bytes")
        print(f"   SID Folder: {file_info.get('sid_folder', 'Unknown')}")
        print()
    
    # Example 2: Find largest files
    print("2. Largest Deleted Files:")
    print("-" * 30)
    sorted_by_size = sorted(files_info, key=lambda x: x.get('file_size', 0), reverse=True)
    for i, file_info in enumerate(sorted_by_size[:3], 1):
        print(f"{i}. {file_info.get('original_name', 'Unknown')}")
        print(f"   Size: {file_info.get('file_size', 0):,} bytes")
        print(f"   Original Path: {file_info.get('original_path', 'Unknown')}")
        print()
    
    # Example 3: Find text files that can be read
    print("3. Readable Text Files:")
    print("-" * 30)
    text_files = [f for f in files_info if f.get('can_read_content', False)]
    for i, file_info in enumerate(text_files[:3], 1):
        print(f"{i}. {file_info.get('original_name', 'Unknown')}")
        print(f"   Path: {file_info.get('original_path', 'Unknown')}")
        print(f"   Recycled Name: {file_info.get('recycled_name', 'Unknown')}")
        print()
    
    # Example 4: Custom filtering - find files from specific locations
    print("4. Files from Desktop:")
    print("-" * 30)
    desktop_files = [f for f in files_info if 'Desktop' in f.get('original_path', '')]
    for i, file_info in enumerate(desktop_files[:3], 1):
        print(f"{i}. {file_info.get('original_name', 'Unknown')}")
        print(f"   Full Path: {file_info.get('original_path', 'Unknown')}")
        print(f"   SID Folder: {file_info.get('sid_folder', 'Unknown')}")
        print()
    
    # Example 5: Group files by SID folder
    print("5. Files by SID Folder:")
    print("-" * 30)
    sid_groups = {}
    for file_info in files_info:
        sid = file_info.get('sid_folder', 'Unknown')
        if sid not in sid_groups:
            sid_groups[sid] = []
        sid_groups[sid].append(file_info)
    
    for sid, files in sid_groups.items():
        print(f"SID {sid}: {len(files)} files")
        total_size = sum(f.get('file_size', 0) for f in files)
        print(f"  Total size: {total_size:,} bytes")
        print()
    
    # Example 6: Export to custom CSV with specific fields
    print("6. Exporting to CSV...")
    export_to_csv(files_info, "example_analysis.csv")
    print("Export completed: example_analysis.csv")
    
    # Example 7: Show content preview for first readable text file
    print("\n7. Content Preview (First Readable Text File):")
    print("-" * 50)
    readable_files = [f for f in files_info if f.get('can_read_content', False)]
    if readable_files:
        first_file = readable_files[0]
        print(f"File: {first_file.get('original_name', 'Unknown')}")
        print(f"Original Path: {first_file.get('original_path', 'Unknown')}")
        if first_file.get('actual_file_path'):
            _display_file_content(first_file['actual_file_path'], 500)
    else:
        print("No readable text files found.")
    
    # Example 8: Statistics
    print("\n8. Statistics:")
    print("-" * 30)
    total_size = sum(f.get('file_size', 0) for f in files_info)
    readable_count = sum(1 for f in files_info if f.get('can_read_content', False))
    unique_sids = len(set(f.get('sid_folder', 'Unknown') for f in files_info))
    
    print(f"Total files: {len(files_info)}")
    print(f"Total size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
    print(f"Readable text files: {readable_count}")
    print(f"Binary files: {len(files_info) - readable_count}")
    print(f"Unique SID folders: {unique_sids}")
    
    # Example 9: Find recently deleted files (last 24 hours)
    print("\n9. Recently Deleted Files (Last 24 Hours):")
    print("-" * 50)
    import datetime
    now = datetime.datetime.now()
    one_day_ago = now - datetime.timedelta(days=1)
    
    recent_files = []
    for file_info in files_info:
        delete_time = file_info.get('delete_time')
        if delete_time and delete_time > one_day_ago:
            recent_files.append(file_info)
    
    for i, file_info in enumerate(recent_files[:5], 1):
        print(f"{i}. {file_info.get('original_name', 'Unknown')}")
        print(f"   Deleted: {file_info.get('delete_time', 'Unknown')}")
        print(f"   Path: {file_info.get('original_path', 'Unknown')}")
        print()


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