# Windows Recycle Bin Analyzer

A comprehensive Python tool for analyzing the Windows Recycle Bin directory. This script provides detailed information about deleted files including their original names, locations, file sizes, deletion times, and content reading capabilities.

## Features

- **Complete Recycle Bin Analysis**: Scans all drives for Recycle Bin directories
- **File Information Extraction**: Retrieves original file names and locations
- **Metadata Parsing**: Extracts file sizes, deletion times, and other metadata
- **Content Reading**: Can read and display content from text files in the Recycle Bin
- **CSV Export**: Export analysis results to CSV format for further processing
- **Cross-Drive Support**: Automatically detects Recycle Bin locations on multiple drives
- **Windows Version Compatibility**: Works with both older (INFO2) and newer (SID-based) Recycle Bin formats

## Requirements

- Windows operating system
- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.6+ installed
3. No additional installation required - all dependencies are part of Python's standard library

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

#### Combine options:
```bash
python recycle_bin_analyzer.py --show-content --max-content-length 1500 --export-csv results.csv
```

## Command Line Options

- `--show-content`: Display content preview for text files
- `--max-content-length N`: Maximum number of characters to display for content preview (default: 1000)
- `--export-csv FILENAME`: Export results to specified CSV file
- `-h, --help`: Show help message

## Output Information

For each deleted file, the analyzer provides:

- **Original Name**: The original filename before deletion
- **Original Location**: The full path where the file was originally located
- **File Size**: Size of the deleted file in bytes
- **Delete Time**: When the file was deleted
- **Can Read Content**: Whether the file content can be read
- **Content Preview**: (Optional) Preview of text file contents

## How It Works

### Recycle Bin Structure

The Windows Recycle Bin stores deleted files in a special directory structure:

- **Location**: `C:\$Recycle.Bin` (or on other drives)
- **User Folders**: Each user has a folder identified by their SID (Security Identifier)
- **File Pairs**: Deleted files are stored as pairs:
  - `$I` files: Contain metadata (original name, path, deletion time)
  - `$R` files: Contain the actual deleted file content

### Analysis Process

1. **Drive Detection**: Scans all available drives for Recycle Bin directories
2. **SID Folder Scanning**: Searches through user-specific Recycle Bin folders
3. **Metadata Parsing**: Reads `$I` files to extract original file information
4. **Content Verification**: Checks if corresponding `$R` files exist for content reading
5. **Data Compilation**: Combines all information into a comprehensive report

## Security and Privacy

⚠️ **Important Notes**:

- This tool requires appropriate permissions to access the Recycle Bin
- Some files may be inaccessible due to system permissions
- The Recycle Bin may contain sensitive information - use responsibly
- Always ensure you have authorization before analyzing Recycle Bin contents

## Limitations

- Only works on Windows systems
- Requires appropriate file system permissions
- Some files may be corrupted or partially deleted
- Binary files cannot display content previews
- Very large files may take time to process

## Example Output

```
Starting Windows Recycle Bin analysis...
Scanning Recycle Bin at: C:\$Recycle.Bin

Found 3 deleted files:
================================================================================

1. File Information:
   Original Name: document.txt
   Original Location: C:\Users\username\Documents\document.txt
   File Size: 1,024 bytes
   Delete Time: 2024-01-15 14:30:25
   Can Read Content: True
   Content Preview (200 chars):
   'This is the content of the deleted document...'
   ----------------------------------------

2. File Information:
   Original Name: image.jpg
   Original Location: C:\Users\username\Pictures\image.jpg
   File Size: 2,048,000 bytes
   Delete Time: 2024-01-14 09:15:10
   Can Read Content: False
   ----------------------------------------
```

## Troubleshooting

### Common Issues

1. **"Recycle Bin not found"**: Ensure you're running on Windows and have appropriate permissions
2. **"No deleted files found"**: The Recycle Bin may be empty or files may be in different locations
3. **Permission errors**: Run the script with appropriate user privileges
4. **Content reading errors**: Some files may be corrupted or inaccessible

### Getting Help

If you encounter issues:

1. Check that you're running on a Windows system
2. Ensure you have appropriate file system permissions
3. Try running the script with administrator privileges if needed
4. Check the console output for specific error messages

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Disclaimer

This tool is provided for educational and legitimate forensic purposes only. Always ensure you have proper authorization before analyzing Recycle Bin contents, especially in professional or legal contexts. 