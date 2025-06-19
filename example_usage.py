#!/usr/bin/env python3
"""
Example usage of the Windows Recycle Bin Analyzer

This script demonstrates how to use the RecycleBinAnalyzer class programmatically
to analyze the Recycle Bin and perform custom operations on the results.
"""

from recycle_bin_analyzer import RecycleBinAnalyzer
import sys


def main():
    """Example usage of the RecycleBinAnalyzer."""
    
    print("Windows Recycle Bin Analyzer - Example Usage")
    print("=" * 50)
    
    # Create analyzer instance
    analyzer = RecycleBinAnalyzer()
    
    # Perform analysis
    print("Analyzing Recycle Bin...")
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
        print()
    
    # Example 2: Find largest files
    print("2. Largest Deleted Files:")
    print("-" * 30)
    sorted_by_size = sorted(files_info, key=lambda x: x.get('file_size', 0), reverse=True)
    for i, file_info in enumerate(sorted_by_size[:3], 1):
        print(f"{i}. {file_info.get('original_name', 'Unknown')}")
        print(f"   Size: {file_info.get('file_size', 0):,} bytes")
        print()
    
    # Example 3: Find text files that can be read
    print("3. Readable Text Files:")
    print("-" * 30)
    text_files = [f for f in files_info if f.get('can_read_content', False)]
    for i, file_info in enumerate(text_files[:3], 1):
        print(f"{i}. {file_info.get('original_name', 'Unknown')}")
        print(f"   Path: {file_info.get('original_path', 'Unknown')}")
        print()
    
    # Example 4: Custom filtering - find files from specific locations
    print("4. Files from Desktop:")
    print("-" * 30)
    desktop_files = [f for f in files_info if 'Desktop' in f.get('original_path', '')]
    for i, file_info in enumerate(desktop_files[:3], 1):
        print(f"{i}. {file_info.get('original_name', 'Unknown')}")
        print(f"   Full Path: {file_info.get('original_path', 'Unknown')}")
        print()
    
    # Example 5: Export to custom CSV with specific fields
    print("5. Exporting to CSV...")
    analyzer.export_to_csv("example_analysis.csv")
    print("Export completed: example_analysis.csv")
    
    # Example 6: Show content preview for first readable text file
    print("\n6. Content Preview (First Readable Text File):")
    print("-" * 50)
    readable_files = [f for f in files_info if f.get('can_read_content', False)]
    if readable_files:
        first_file = readable_files[0]
        print(f"File: {first_file.get('original_name', 'Unknown')}")
        if first_file.get('actual_file_path'):
            analyzer._display_file_content(first_file['actual_file_path'], 500)
    else:
        print("No readable text files found.")
    
    # Example 7: Statistics
    print("\n7. Statistics:")
    print("-" * 30)
    total_size = sum(f.get('file_size', 0) for f in files_info)
    readable_count = sum(1 for f in files_info if f.get('can_read_content', False))
    
    print(f"Total files: {len(files_info)}")
    print(f"Total size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
    print(f"Readable text files: {readable_count}")
    print(f"Binary files: {len(files_info) - readable_count}")


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