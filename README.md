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
- **JSON Export**: Export analysis results to JSON format for programmatic access
- **HTML Export**: Export analysis results to HTML format with interactive sortable table
- **Cross-Drive Support**: Automatically detects Recycle Bin locations on multiple drives
- **Windows Version Compatibility**: Works with both older (INFO2) and newer (SID-based) Recycle Bin formats
- **User SID Management**: Shows all user SIDs and their Recycle Bin contents
- **Username Resolution**: Resolves SIDs to human-readable usernames using Windows API

## Requirements

- Windows operating system
- Python 3.6 or higher
- **Required**: `pywin32` package for Windows API access

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.6+ installed
3. **Required**: Install pywin32 for Windows API access:
   ```bash
   pip install pywin32
   ```
4. No additional installation required - all other dependencies are part of Python's standard library

## Usage

### Basic Usage

Run the script to analyze your Recycle Bin:

```bash
python recycle_bin_analyzer.py
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--show-content` | Display content preview for text files | False |
| `--max-content-length N` | Maximum number of characters to display for content preview | 1000 |
| `--export-csv FILENAME` | Export results to specified CSV file | Auto-export if files found |
| `--export-json FILENAME` | Export results to specified JSON file | Auto-export if files found |
| `--export-html FILENAME` | Export results to specified HTML file with sortable table | Auto-export if files found |
| `--show-sids` | Show all user SIDs found on the system | False |
| `-h, --help` | Show help message | - |

### Advanced Usage Examples

#### Show file content previews:
```bash
python recycle_bin_analyzer.py --show-content
```

#### Customize content preview length:
```bash
python recycle_bin_analyzer.py --show-content --max-content-length 2000
```

#### Export results to specific CSV file:
```bash
python recycle_bin_analyzer.py --export-csv my_analysis.csv
```

#### Export results to specific JSON file:
```bash
python recycle_bin_analyzer.py --export-json my_analysis.json
```

#### Export results to specific HTML file:
```bash
python recycle_bin_analyzer.py --export-html my_analysis.html
```

#### Show all user SIDs on the system:
```bash
python recycle_bin_analyzer.py --show-sids
```

#### Combine multiple options:
```bash
python recycle_bin_analyzer.py --show-content --max-content-length 1500 --export-html results.html --show-sids
```

#### Get help:
```bash
python recycle_bin_analyzer.py --help
```

## Output Information

For each deleted file, the analyzer provides:

- **Original Name**: The original filename before deletion
- **Original Location**: The full path where the file was originally located
- **File Size**: Size of the deleted file in bytes
- **Delete Time**: When the file was deleted (local timezone)
- **SID Folder**: Which user's Recycle Bin folder contains the file
- **Username**: Human-readable username associated with the SID
- **Recycled Name**: The $I metadata filename in the Recycle Bin
- **Can Read Content**: Whether the file content can be read
- **Content Preview**: (Optional) Preview of text file contents

## Export Formats

### CSV Export

The CSV export includes the following columns:

| Column | Description |
|--------|-------------|
| `original_name` | Original filename before deletion |
| `original_path` | Full original file path |
| `file_size` | File size in bytes |
| `delete_time` | Deletion timestamp |
| `sid_folder` | SID (Security Identifier) of the user |
| `username` | Human-readable username |
| `recycled_name` | $I metadata filename in Recycle Bin |
| `can_read_content` | Whether file content can be read |

### JSON Export

The JSON export provides structured data with the following file attributes:

- `original_name`: Original filename before deletion
- `original_path`: Full original file path
- `file_size`: File size in bytes
- `delete_time`: Deletion timestamp
- `sid_folder`: SID (Security Identifier) of the user
- `username`: Human-readable username
- `recycled_name`: $I metadata filename in Recycle Bin
- `can_read_content`: Whether file content can be read
- `actual_file_path`: Full path to the $R file in Recycle Bin

The JSON format provides:
- **analysis_info**: Metadata about the analysis run
- **files**: Array of file objects with complete information
- **Structured data**: Easy to parse programmatically
- **UTF-8 encoding**: Proper handling of international characters

### HTML Export Format

The HTML export creates an interactive web page with a sortable table and search functionality:

![HTML Report Example](html_report_example.png)
*Screenshot of an example HTML report generated by the tool*

**Features:**
- **Sortable Columns**: Click any column header to sort by that field
- **Search Functionality**: Real-time filtering of results
- **Statistics Dashboard**: Summary statistics at the top
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional appearance with hover effects

**Interactive Elements:**
- **Column Sorting**: Click column headers to sort ascending/descending
- **Search Box**: Type to filter results across all fields
- **Visual Indicators**: Sort arrows and hover effects
- **Color Coding**: Green for readable files, red for binary files

**Statistics Displayed:**
- Total file size (bytes and MB)
- Number of text files vs binary files
- Number of unique users
- Analysis timestamp

The HTML file is self-contained with embedded CSS and JavaScript, making it easy to share and view in any web browser.

### Show All User SIDs
```bash
python recycle_bin_analyzer.py --show-sids
```

**Output:**
```
Windows Recycle Bin Analyzer
Windows API available: True (requires pywin32)

User SIDs on this system:
--------------------------------------------------
  username (S-1-5-21-1234567890-1234567890-1234567890-1001)
  Administrator (S-1-5-21-1234567890-1234567890-1234567890-500)
  SYSTEM (S-1-5-18)
  NETWORK SERVICE (S-1-5-20)
  LOCAL SERVICE (S-1-5-19)

Starting Windows Recycle Bin analysis...
[rest of analysis output...]
```

### Help Output
```bash
python recycle_bin_analyzer.py --help
```

**Output:**
```
usage: recycle_bin_analyzer.py [-h] [--show-content] [--max-content-length MAX_CONTENT_LENGTH] [--export-csv EXPORT_CSV] [--export-json EXPORT_JSON] [--export-html EXPORT_HTML] [--show-sids]

Windows Recycle Bin Analyzer

options:
  -h, --help            show this help message and exit
  --show-content        Show content preview for text files
  --max-content-length MAX_CONTENT_LENGTH
                        Maximum content length to display (default: 1000)
  --export-csv EXPORT_CSV
                        Export results to CSV file
  --export-json EXPORT_JSON
                        Export results to JSON file
  --export-html EXPORT_HTML
                        Export results to HTML file with sortable table
  --show-sids           Show all user SIDs found on the system

Windows API available: True (requires pywin32)
```

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

## Bibliography

- [Stack Overflow: How to parse Windows Recycle Bin $I files](https://stackoverflow.com/questions/14720557/how-to-parse-windows-recycle-bin-i-files)

## Disclaimer

This tool is provided for educational and legitimate forensic purposes only. Always ensure you have proper authorization before analyzing Recycle Bin contents, especially in professional or legal contexts. 