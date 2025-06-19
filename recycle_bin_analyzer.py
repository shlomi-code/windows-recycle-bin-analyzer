#!/usr/bin/env python3
"""
Windows Recycle Bin Analyzer

This script analyzes the Windows Recycle Bin directory and provides information about
deleted files including their names, original locations, and content reading capabilities.
"""

import os
import sys
import shutil
import struct
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse


class RecycleBinAnalyzer:
    """Analyzes the Windows Recycle Bin and provides detailed information about deleted files."""
    
    def __init__(self):
        self.recycle_bin_path = self._get_recycle_bin_path()
        self.files_info = []
        
    def _get_recycle_bin_path(self) -> Path:
        """Get the path to the Windows Recycle Bin."""
        # The Recycle Bin is typically located at C:\$Recycle.Bin
        # But it might be on different drives
        drives = []
        
        # Get all available drives
        for drive in range(ord('A'), ord('Z') + 1):
            drive_letter = chr(drive) + ":\\"
            if os.path.exists(drive_letter):
                drives.append(drive_letter)
        
        # Look for $Recycle.Bin in each drive
        for drive in drives:
            recycle_bin = Path(drive) / "$Recycle.Bin"
            if recycle_bin.exists():
                return recycle_bin
                
        # Fallback to C: drive
        return Path("C:\\$Recycle.Bin")
    
    def _parse_info2_file(self, info2_path: Path) -> List[Dict]:
        """Parse the INFO2 file to get metadata about deleted files."""
        files_info = []
        
        try:
            with open(info2_path, 'rb') as f:
                # Read the header
                header = f.read(20)
                if len(header) < 20:
                    return files_info
                
                # Parse header information
                version, file_count = struct.unpack('<II', header[:8])
                
                # Read file records
                for _ in range(file_count):
                    record = f.read(280)  # Standard record size
                    if len(record) < 280:
                        break
                    
                    # Parse record fields
                    file_size = struct.unpack('<Q', record[0:8])[0]
                    delete_time = struct.unpack('<Q', record[8:16])[0]
                    
                    # Extract file name (null-terminated)
                    name_bytes = record[16:280]
                    name_end = name_bytes.find(b'\x00')
                    if name_end != -1:
                        original_name = name_bytes[:name_end].decode('utf-16le', errors='ignore')
                    else:
                        original_name = name_bytes.decode('utf-16le', errors='ignore')
                    
                    # Convert Windows file time to datetime
                    if delete_time > 0:
                        # Windows file time is in 100-nanosecond intervals since 1601-01-01
                        delete_datetime = datetime.datetime(1601, 1, 1) + \
                                        datetime.timedelta(microseconds=delete_time // 10)
                    else:
                        delete_datetime = None
                    
                    files_info.append({
                        'original_name': original_name,
                        'file_size': file_size,
                        'delete_time': delete_datetime,
                        'record_data': record
                    })
                    
        except Exception as e:
            print(f"Error parsing INFO2 file: {e}")
            
        return files_info
    
    def _scan_recycle_bin(self) -> List[Dict]:
        """Scan the Recycle Bin directory for deleted files."""
        files_info = []
        
        if not self.recycle_bin_path.exists():
            print(f"Recycle Bin not found at: {self.recycle_bin_path}")
            return files_info
        
        print(f"Scanning Recycle Bin at: {self.recycle_bin_path}")
        
        # Look for INFO2 file (older Windows versions)
        info2_path = self.recycle_bin_path / "INFO2"
        if info2_path.exists():
            files_info.extend(self._parse_info2_file(info2_path))
        
        # Scan SID folders (newer Windows versions)
        for item in self.recycle_bin_path.iterdir():
            if item.is_dir() and item.name.startswith('S-'):
                # This is a user's Recycle Bin folder
                self._scan_sid_folder(item, files_info)
        
        return files_info
    
    def _scan_sid_folder(self, sid_path: Path, files_info: List[Dict]):
        """Scan a specific user's Recycle Bin folder."""
        try:
            for item in sid_path.iterdir():
                if item.is_file():
                    # Parse the filename to get original name and location
                    file_info = self._parse_recycled_filename(item)
                    if file_info:
                        file_info['current_path'] = item
                        file_info['file_size'] = item.stat().st_size
                        file_info['delete_time'] = datetime.datetime.fromtimestamp(item.stat().st_mtime)
                        files_info.append(file_info)
        except Exception as e:
            print(f"Error scanning SID folder {sid_path}: {e}")
    
    def _parse_recycled_filename(self, file_path: Path) -> Optional[Dict]:
        """Parse the recycled filename to extract original information."""
        try:
            # Recycled files have format: $I<original_name>.<extension>
            filename = file_path.name
            
            if not filename.startswith('$I'):
                return None
            
            # Look for corresponding $R file (the actual deleted file)
            r_filename = filename.replace('$I', '$R')
            r_file_path = file_path.parent / r_filename
            
            # Try to read the $I file for metadata
            metadata = self._read_metadata_file(file_path)
            
            return {
                'original_name': metadata.get('original_name', 'Unknown'),
                'original_path': metadata.get('original_path', 'Unknown'),
                'recycled_name': filename,
                'actual_file_path': r_file_path if r_file_path.exists() else None,
                'can_read_content': r_file_path.exists() and r_file_path.is_file()
            }
            
        except Exception as e:
            print(f"Error parsing recycled filename {file_path}: {e}")
            return None
    
    def _read_metadata_file(self, metadata_path: Path) -> Dict:
        """Read metadata from a $I file."""
        metadata = {}
        
        try:
            with open(metadata_path, 'rb') as f:
                # Read header
                header = f.read(8)
                if len(header) >= 8:
                    file_size = struct.unpack('<Q', header)[0]
                    metadata['file_size'] = file_size
                
                # Read delete time
                time_data = f.read(8)
                if len(time_data) >= 8:
                    delete_time = struct.unpack('<Q', time_data)[0]
                    if delete_time > 0:
                        delete_datetime = datetime.datetime(1601, 1, 1) + \
                                        datetime.timedelta(microseconds=delete_time // 10)
                        metadata['delete_time'] = delete_datetime
                
                # Read original path length
                path_len_data = f.read(4)
                if len(path_len_data) >= 4:
                    path_len = struct.unpack('<I', path_len_data)[0]
                    
                    # Read original path
                    if path_len > 0:
                        path_data = f.read(path_len * 2)  # UTF-16
                        if len(path_data) >= path_len * 2:
                            original_path = path_data.decode('utf-16le', errors='ignore')
                            metadata['original_path'] = original_path
                            metadata['original_name'] = Path(original_path).name
                
        except Exception as e:
            print(f"Error reading metadata file {metadata_path}: {e}")
        
        return metadata
    
    def analyze(self) -> List[Dict]:
        """Perform the complete Recycle Bin analysis."""
        print("Starting Windows Recycle Bin analysis...")
        self.files_info = self._scan_recycle_bin()
        return self.files_info
    
    def display_results(self, show_content: bool = False, max_content_length: int = 1000):
        """Display the analysis results."""
        if not self.files_info:
            print("No deleted files found in the Recycle Bin.")
            return
        
        print(f"\nFound {len(self.files_info)} deleted files:")
        print("=" * 80)
        
        for i, file_info in enumerate(self.files_info, 1):
            print(f"\n{i}. File Information:")
            print(f"   Original Name: {file_info.get('original_name', 'Unknown')}")
            print(f"   Original Location: {file_info.get('original_path', 'Unknown')}")
            print(f"   File Size: {file_info.get('file_size', 0):,} bytes")
            print(f"   Delete Time: {file_info.get('delete_time', 'Unknown')}")
            print(f"   Can Read Content: {file_info.get('can_read_content', False)}")
            
            if show_content and file_info.get('can_read_content') and file_info.get('actual_file_path'):
                self._display_file_content(file_info['actual_file_path'], max_content_length)
            
            print("-" * 40)
    
    def _display_file_content(self, file_path: Path, max_length: int):
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
    
    def export_to_csv(self, output_file: str = "recycle_bin_analysis.csv"):
        """Export the analysis results to a CSV file."""
        import csv
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['original_name', 'original_path', 'file_size', 'delete_time', 'can_read_content', 'recycled_name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for file_info in self.files_info:
                    # Prepare row data
                    row = {
                        'original_name': file_info.get('original_name', ''),
                        'original_path': file_info.get('original_path', ''),
                        'file_size': file_info.get('file_size', 0),
                        'delete_time': str(file_info.get('delete_time', '')),
                        'can_read_content': file_info.get('can_read_content', False),
                        'recycled_name': file_info.get('recycled_name', '')
                    }
                    writer.writerow(row)
            
            print(f"\nAnalysis exported to: {output_file}")
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")


def main():
    """Main function to run the Recycle Bin analyzer."""
    parser = argparse.ArgumentParser(description='Windows Recycle Bin Analyzer')
    parser.add_argument('--show-content', action='store_true', 
                       help='Show content preview for text files')
    parser.add_argument('--max-content-length', type=int, default=1000,
                       help='Maximum content length to display (default: 1000)')
    parser.add_argument('--export-csv', type=str, default='',
                       help='Export results to CSV file')
    
    args = parser.parse_args()
    
    # Check if running on Windows
    if sys.platform != 'win32':
        print("This script is designed for Windows systems only.")
        sys.exit(1)
    
    # Create analyzer and run analysis
    analyzer = RecycleBinAnalyzer()
    files_info = analyzer.analyze()
    
    # Display results
    analyzer.display_results(show_content=args.show_content, 
                           max_content_length=args.max_content_length)
    
    # Export to CSV if requested
    if args.export_csv:
        analyzer.export_to_csv(args.export_csv)
    elif files_info:  # Auto-export if files found
        analyzer.export_to_csv()


if __name__ == "__main__":
    main() 