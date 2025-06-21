import struct
import datetime
from pathlib import Path
from typing import List, Dict, Optional

def parse_info2_file(info2_path: Path) -> List[Dict]:
    """Parse the INFO2 file to get metadata about deleted files (older Windows versions)."""
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

def parse_metadata_file(metadata_path: Path) -> Optional[Dict]:
    """Parse a $I metadata file according to the documented format."""
    try:
        with open(metadata_path, 'rb') as f:
            # Skip any junk bytes (FF FE) before header
            while True:
                pos = f.tell()
                header = f.read(8)
                if len(header) < 8:
                    return None
                
                # Check if this is the correct header (02 00 00 00 00 00 00 00)
                if header == b'\x02\x00\x00\x00\x00\x00\x00\x00':
                    break
                elif header.startswith(b'\xff\xfe'):
                    # Skip BOM and continue
                    continue
                else:
                    # Try next byte
                    f.seek(pos + 1)
                    if f.tell() > pos + 100:  # Limit search
                        return None
            
            # Read file size (8 bytes, little endian)
            size_data = f.read(8)
            if len(size_data) < 8:
                return None
            file_size = struct.unpack('<Q', size_data)[0]
            
            # Read deletion date (8 bytes, FILETIME format)
            time_data = f.read(8)
            if len(time_data) < 8:
                return None
            delete_time = struct.unpack('<Q', time_data)[0]
            
            # Convert FILETIME to datetime
            if delete_time > 0:
                # FILETIME is 100-nanosecond intervals since 1601-01-01
                delete_datetime = datetime.datetime(1601, 1, 1) + \
                                datetime.timedelta(microseconds=delete_time // 10)
            else:
                delete_datetime = None
            
            # Read path length (4 bytes, little endian)
            path_len_data = f.read(4)
            if len(path_len_data) < 4:
                return None
            path_len = struct.unpack('<I', path_len_data)[0]
            
            # Read original path (UTF-16, null-terminated)
            if path_len > 0:
                path_data = f.read(path_len * 2)  # UTF-16 = 2 bytes per character
                if len(path_data) >= path_len * 2:
                    # Remove null terminator if present
                    if path_data.endswith(b'\x00\x00'):
                        path_data = path_data[:-2]
                    original_path = path_data.decode('utf-16le', errors='ignore')
                    original_name = Path(original_path).name
                else:
                    original_path = "Unknown"
                    original_name = "Unknown"
            else:
                original_path = "Unknown"
                original_name = "Unknown"
            
            # Look for corresponding $R file (the actual deleted file)
            r_filename = metadata_path.name.replace('$I', '$R')
            r_file_path = metadata_path.parent / r_filename
            
            return {
                'original_name': original_name,
                'original_path': original_path,
                'file_size': file_size,
                'delete_time': delete_datetime,
                'recycled_name': metadata_path.name,
                'actual_file_path': r_file_path if r_file_path.exists() else None,
                'can_read_content': r_file_path.exists() and r_file_path.is_file(),
                'metadata_file': metadata_path
            }
            
    except Exception as e:
        print(f"Error parsing metadata file {metadata_path}: {e}")
        return None 