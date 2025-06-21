# Windows Recycle Bin Analyzer

A comprehensive Python tool for analyzing the Windows Recycle Bin directory. This script provides detailed information about deleted files including their original names, locations, file sizes, deletion times, and content reading capabilities.

## Features

- **Complete Recycle Bin Analysis**: Scans all drives for Recycle Bin directories
- **SID-Based User Detection**: Automatically detects current user SID and prioritizes their Recycle Bin folder
- **Windows API Integration**: Uses native Windows API calls for better performance (with subprocess fallback)
- **File Information Extraction**: Retrieves original file names and locations
- **Accurate Metadata Parsing**: Properly parses $I metadata files according to Windows specifications
- **Content Reading**: Can read and display content from text files in the Recycle Bin
- **CSV Export**: Export analysis results to CSV format for further processing
- **Cross-Drive Support**: Automatically detects Recycle Bin locations on multiple drives
- **Windows Version Compatibility**: Works with both older (INFO2) and newer (SID-based) Recycle Bin formats
- **User SID Management**: Shows all user SIDs and their Recycle Bin contents

## Requirements

- Windows operating system
- Python 3.6 or higher
- **Optional**: `pywin32` package for better performance (Windows API calls instead of subprocess)

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.6+ installed
3. **Optional**: Install pywin32 for better performance:
   ```bash
   pip install pywin32
   ```
4. No additional installation required - all dependencies are part of Python's standard library

## Usage

### Basic Usage

Run the script to analyze your Recycle Bin:

```bash
python recycle_bin_analyzer.py
```

### Advanced Usage

#### Show file content previews:
```bash
python recycle_bin_analyzer.py --show-content
```

#### Customize content preview length:
```bash
python recycle_bin_analyzer.py --show-content --max-content-length 2000
```

#### Export results to CSV:
```bash
python recycle_bin_analyzer.py --export-csv my_analysis.csv
```

#### Show all user SIDs on the system:
```bash
python recycle_bin_analyzer.py --show-sids
```

#### Combine options:
```bash
python recycle_bin_analyzer.py --show-content --max-content-length 1500 --export-csv results.csv --show-sids
```

## Command Line Options

- `--show-content`: Display content preview for text files
- `--max-content-length N`: Maximum number of characters to display for content preview (default: 1000)
- `--export-csv FILENAME`: Export results to specified CSV file
- `--show-sids`: Show all user SIDs found on the system
- `-h, --help`: Show help message

## Output Information

For each deleted file, the analyzer provides:

- **Original Name**: The original filename before deletion
- **Original Location**: The full path where the file was originally located
- **File Size**: Size of the deleted file in bytes
- **Delete Time**: When the file was deleted (FILETIME format)
- **SID Folder**: Which user's Recycle Bin folder contains the file
- **Recycled Name**: The $I metadata filename in the Recycle Bin
- **Can Read Content**: Whether the file content can be read
- **Content Preview**: (Optional) Preview of text file contents

## How It Works

### Recycle Bin Structure

The Windows Recycle Bin stores deleted files in a special directory structure:

- **Location**: `C:\$Recycle.Bin` (or on other drives)
- **User Folders**: Each user has a folder identified by their SID (Security Identifier)
  - `S-1-5-18`: Built-in SYSTEM account (usually empty)
  - `S-1-5-21-XXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXX-1XXX`: User accounts (starting from 1000)
- **File Pairs**: Deleted files are stored as pairs:
  - `$I` files: Contain metadata (original name, path, deletion time, file size)
  - `$R` files: Contain the actual deleted file content (hardlinks)

### Analysis Process

1. **User SID Detection**: Uses `whoami /all` to get current user's SID
2. **Drive Detection**: Scans all available drives for Recycle Bin directories
3. **SID Folder Prioritization**: Prioritizes current user's folder, then scans others
4. **Metadata Parsing**: Reads `$I` files according to documented format
5. **Content Verification**: Checks if corresponding `$R` files exist for content reading
6. **Data Compilation**: Combines all information into a comprehensive report

### Metadata File Format

The `$I` metadata files follow this binary format:

```
0000  02 00 00 00 00 00 00 00  <-- File header (fixed)
0008  XX XX XX XX XX XX XX XX  <-- File size (8 bytes, little endian)
0010  XX XX XX XX XX XX XX XX  <-- Deletion date (FILETIME format)
0018  XX XX XX XX             <-- Path string length (4 bytes, little endian)
001C  XX XX XX XX ...         <-- Original path (UTF-16, null-terminated)
```

## Security and Privacy

⚠️ **Important Notes**:

- This tool requires appropriate permissions to access the Recycle Bin
- Some files may be inaccessible due to system permissions
- The Recycle Bin may contain sensitive information - use responsibly
- Always ensure you have authorization before analyzing Recycle Bin contents
- The tool automatically detects and prioritizes the current user's files

## Limitations

- Only works on Windows systems
- Requires appropriate file system permissions
- Some files may be corrupted or partially deleted
- Binary files cannot display content previews
- Very large files may take time to process
- Dangling SID folders (from deleted users) may appear empty

## Example Output

```
Starting Windows Recycle Bin analysis...
Scanning Recycle Bin at: C:\$Recycle.Bin
Scanning SID-based folders...
Current user SID: S-1-5-21-1234567890-1234567890-1234567890-1001
Found 2 SID folders
Scanning current user folder: S-1-5-21-1234567890-1234567890-1234567890-1001
  Found 3 deleted files in S-1-5-21-1234567890-1234567890-1234567890-1001
Scanning SID folder: S-1-5-21-1234567890-1234567890-1234567890-1000
  No deleted files found in S-1-5-21-1234567890-1234567890-1234567890-1000

Found 3 deleted files:
================================================================================

1. File Information:
   Original Name: document.txt
   Original Location: C:\Users\username\Documents\document.txt
   File Size: 1,024 bytes
   Delete Time: 2024-01-15 14:30:25
   SID Folder: S-1-5-21-1234567890-1234567890-1234567890-1001
   Recycled Name: $I123456.txt
   Can Read Content: True
   ----------------------------------------
```

## Troubleshooting

### Common Issues

1. **"Recycle Bin not found"**: Ensure you're running on Windows and have appropriate permissions
2. **"No deleted files found"**: The Recycle Bin may be empty or files may be in different SID folders
3. **Permission errors**: Run the script with appropriate user privileges
4. **Content reading errors**: Some files may be corrupted or inaccessible
5. **Empty SID folders**: Some folders may be from deleted users or system accounts

### Getting Help

If you encounter issues:

1. Check that you're running on a Windows system
2. Ensure you have appropriate file system permissions
3. Try running the script with administrator privileges if needed
4. Use `--show-sids` to see all user SIDs on your system
5. Check the console output for specific error messages

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Disclaimer

This tool is provided for educational and legitimate forensic purposes only. Always ensure you have proper authorization before analyzing Recycle Bin contents, especially in professional or legal contexts. 