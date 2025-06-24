import os
from pathlib import Path
from typing import List, Dict

from src import sid
from src import parsers

class RecycleBinAnalyzer:
    """Analyzes the Windows Recycle Bin and provides detailed information about deleted files."""
    
    def __init__(self):
        self.recycle_bin_path = self._get_recycle_bin_path()
        self.files_info: List[Dict] = []
        self.current_user_sid = sid.get_current_user_sid()
        self.sid_cache = {}  # Cache for SID to username resolution
        
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
    
    def _get_sid_display_name(self, sid_string: str) -> str:
        """Get a user-friendly display name for a SID."""
        if sid_string not in self.sid_cache:
            sid_info = sid.get_sid_info(sid_string)
            if sid_info['username']:
                if sid_info['description']:
                    self.sid_cache[sid_string] = f"{sid_info['username']} ({sid_info['description']})"
                else:
                    self.sid_cache[sid_string] = f"{sid_info['username']} ({sid_string})"
            else:
                self.sid_cache[sid_string] = sid_string
        return self.sid_cache[sid_string]
    
    def analyze(self) -> List[Dict]:
        """Perform the complete Recycle Bin analysis."""
        print("Starting Windows Recycle Bin analysis...")
        self.files_info = self._scan_recycle_bin()
        return self.files_info
    
    def _scan_recycle_bin(self) -> List[Dict]:
        """Scan the Recycle Bin directory for deleted files."""
        files_info: List[Dict] = []
        
        if not self.recycle_bin_path.exists():
            print(f"Recycle Bin not found at: {self.recycle_bin_path}")
            return files_info
        
        print(f"Scanning Recycle Bin at: {self.recycle_bin_path}")
        
        # Look for INFO2 file (older Windows versions)
        info2_path = self.recycle_bin_path / "INFO2"
        if info2_path.exists():
            print("Found INFO2 file (older Windows format)")
            files_info.extend(parsers.parse_info2_file(info2_path))
        
        # Scan SID folders (newer Windows versions)
        print("Scanning SID-based folders...")
        if self.current_user_sid:
            current_user_display = self._get_sid_display_name(self.current_user_sid)
            print(f"Current user: {current_user_display}")
        
        # Get all SID folders
        sid_folders = []
        for item in self.recycle_bin_path.iterdir():
            if item.is_dir() and item.name.startswith('S-'):
                sid_folders.append(item)
        
        print(f"Found {len(sid_folders)} SID folders")
        
        # Prioritize current user's folder, then scan others
        if self.current_user_sid:
            current_user_folder = self.recycle_bin_path / self.current_user_sid
            if current_user_folder.exists():
                current_user_display = self._get_sid_display_name(self.current_user_sid)
                print(f"Scanning current user folder: {current_user_display}")
                self._scan_sid_folder(current_user_folder, files_info)
        
        # Scan other SID folders
        for sid_folder in sid_folders:
            if not self.current_user_sid or sid_folder.name != self.current_user_sid:
                sid_display = self._get_sid_display_name(sid_folder.name)
                print(f"Scanning SID folder: {sid_display}")
                self._scan_sid_folder(sid_folder, files_info)
        
        return files_info
    
    def _scan_sid_folder(self, sid_path: Path, files_info: List[Dict]):
        """Scan a specific user's Recycle Bin folder."""
        try:
            # Look for $I files (metadata files)
            i_files = [f for f in sid_path.iterdir() if f.is_file() and f.name.startswith('$I')]
            
            if not i_files:
                sid_display = self._get_sid_display_name(sid_path.name)
                print(f"  No deleted files found in {sid_display}")
                return
            
            sid_display = self._get_sid_display_name(sid_path.name)
            print(f"  Found {len(i_files)} deleted files in {sid_display}")
            
            for i_file in i_files:
                # Parse the metadata file
                file_info = parsers.parse_metadata_file(i_file)
                if file_info:
                    file_info['sid_folder'] = sid_path.name
                    file_info['sid_display'] = sid_display
                    files_info.append(file_info)
                    
        except Exception as e:
            print(f"Error scanning SID folder {sid_path}: {e}") 