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

def export_to_html(files_info: List[Dict], output_file: str = "recycle_bin_analysis.html"):
    """Export the analysis results to an HTML file with sortable table."""
    try:
        # Calculate file extension statistics
        extension_stats = {}
        total_files = len(files_info)
        
        for file_info in files_info:
            original_name = file_info.get('original_name', '')
            if original_name:
                # Extract file extension
                if '.' in original_name:
                    extension = original_name.split('.')[-1].lower()
                    if extension:
                        extension_stats[extension] = extension_stats.get(extension, 0) + 1
                else:
                    # Files without extension
                    extension_stats['No Extension'] = extension_stats.get('No Extension', 0) + 1
            else:
                # Unknown files
                extension_stats['Unknown'] = extension_stats.get('Unknown', 0) + 1
        
        # Sort extensions by count (descending) and limit to top 10
        sorted_extensions = sorted(extension_stats.items(), key=lambda x: x[1], reverse=True)
        top_extensions = sorted_extensions[:10]
        
        # Prepare chart data
        chart_labels = [ext for ext, count in top_extensions]
        chart_data = [count for ext, count in top_extensions]
        chart_colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ]
        
        # HTML template with embedded CSS and JavaScript
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windows Recycle Bin Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }}
        .analysis-info {{
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #2196F3;
        }}
        .analysis-info p {{
            margin: 5px 0;
            color: #333;
        }}
        .stats {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-radius: 4px;
            margin: 5px;
            border-left: 3px solid #2196F3;
        }}
        .stat-label {{
            font-weight: bold;
            color: #333;
        }}
        .stat-value {{
            color: #666;
        }}
        .charts-container {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .chart-wrapper {{
            flex: 1;
            min-width: 300px;
            max-width: 400px;
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            text-align: center;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}
        .chart-container {{
            position: relative;
            height: 200px;
            width: 100%;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #2196F3;
            color: white;
            padding: 12px 8px;
            text-align: left;
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        th:hover {{
            background-color: #1976D2;
        }}
        th::after {{
            content: '↕';
            position: absolute;
            right: 8px;
            opacity: 0.7;
        }}
        th.sort-asc::after {{
            content: '↑';
            opacity: 1;
        }}
        th.sort-desc::after {{
            content: '↓';
            opacity: 1;
        }}
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #ddd;
            vertical-align: top;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .file-size {{
            text-align: right;
            font-family: monospace;
        }}
        .can-read {{
            text-align: center;
        }}
        .can-read.true {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .can-read.false {{
            color: #f44336;
        }}
        .path-cell {{
            max-width: 300px;
            word-wrap: break-word;
            font-family: monospace;
            font-size: 0.9em;
        }}
        .no-data {{
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }}
        .search-box {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
            font-size: 14px;
        }}
        .extension-list {{
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
        }}
        .extension-item {{
            display: flex;
            justify-content: space-between;
            margin: 2px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Windows Recycle Bin Analysis</h1>
        
        <div class="analysis-info">
            <p><strong>Analysis Timestamp:</strong> {timestamp}</p>
            <p><strong>Total Files:</strong> {total_files}</p>
            <p><strong>Export Format:</strong> HTML</p>
        </div>

        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">Total Size:</div>
                <div class="stat-value">{total_size}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Text Files:</div>
                <div class="stat-value">{text_files}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Binary Files:</div>
                <div class="stat-value">{binary_files}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Unique Users:</div>
                <div class="stat-value">{unique_users}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">File Types:</div>
                <div class="stat-value">{file_types_count}</div>
            </div>
        </div>

        <div class="charts-container">
            <div class="chart-wrapper">
                <div class="chart-title">File Extensions Distribution</div>
                <div class="chart-container">
                    <canvas id="extensionChart" width="300" height="200"></canvas>
                </div>
                <div class="extension-list">
                    {extension_list}
                </div>
            </div>
        </div>

        <input type="text" id="searchBox" class="search-box" placeholder="Search files... (type to filter)">

        <table id="dataTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Original Name</th>
                    <th onclick="sortTable(1)">Original Path</th>
                    <th onclick="sortTable(2)">File Size</th>
                    <th onclick="sortTable(3)">Delete Time</th>
                    <th onclick="sortTable(4)">SID Folder</th>
                    <th onclick="sortTable(5)">Username</th>
                    <th onclick="sortTable(6)">Recycled Name</th>
                    <th onclick="sortTable(7)">Can Read Content</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <script>
        let currentSort = {{ column: -1, direction: 'asc' }};
        let originalData = [];

        // Initialize the table
        document.addEventListener('DOMContentLoaded', function() {{
            // Store original data for filtering
            const tbody = document.querySelector('#dataTable tbody');
            const rows = tbody.querySelectorAll('tr');
            originalData = Array.from(rows).map(row => row.innerHTML);
            
            // Add search functionality
            document.getElementById('searchBox').addEventListener('input', filterTable);
            
            // Initialize chart
            initializeChart();
        }});

        function initializeChart() {{
            const ctx = document.getElementById('extensionChart').getContext('2d');
            new Chart(ctx, {{
                type: 'pie',
                data: {{
                    labels: {chart_labels},
                    datasets: [{{
                        data: {chart_data},
                        backgroundColor: {chart_colors},
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 10,
                                usePointStyle: true,
                                font: {{
                                    size: 11
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}} (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        function sortTable(columnIndex) {{
            const table = document.getElementById('dataTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const header = table.querySelector('thead tr').children[columnIndex];
            
            // Clear previous sort indicators
            table.querySelectorAll('th').forEach(th => {{
                th.classList.remove('sort-asc', 'sort-desc');
            }});
            
            // Determine sort direction
            let direction = 'asc';
            if (currentSort.column === columnIndex && currentSort.direction === 'asc') {{
                direction = 'desc';
            }}
            
            // Update sort indicator
            header.classList.add(direction === 'asc' ? 'sort-asc' : 'sort-desc');
            currentSort = {{ column: columnIndex, direction: direction }};
            
            // Sort rows
            rows.sort((a, b) => {{
                let aValue = a.children[columnIndex].textContent.trim();
                let bValue = b.children[columnIndex].textContent.trim();
                
                // Handle different data types
                if (columnIndex === 2) {{ // File Size
                    aValue = parseInt(aValue.replace(/[^0-9]/g, '')) || 0;
                    bValue = parseInt(bValue.replace(/[^0-9]/g, '')) || 0;
                    return direction === 'asc' ? aValue - bValue : bValue - aValue;
                }} else if (columnIndex === 3) {{ // Delete Time
                    aValue = new Date(aValue);
                    bValue = new Date(bValue);
                    return direction === 'asc' ? aValue - bValue : bValue - aValue;
                }} else {{ // String values
                    aValue = aValue.toLowerCase();
                    bValue = bValue.toLowerCase();
                    if (aValue < bValue) return direction === 'asc' ? -1 : 1;
                    if (aValue > bValue) return direction === 'asc' ? 1 : -1;
                    return 0;
                }}
            }});
            
            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        }}

        function filterTable() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const tbody = document.querySelector('#dataTable tbody');
            const rows = tbody.querySelectorAll('tr');
            
            rows.forEach((row, index) => {{
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}

        function formatFileSize(bytes) {{
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            if (bytes === 0) return '0 B';
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
        }}
    </script>
</body>
</html>"""

        # Calculate statistics
        total_size = sum(file_info.get('file_size', 0) for file_info in files_info)
        text_files = sum(1 for file_info in files_info if file_info.get('can_read_content', False))
        binary_files = len(files_info) - text_files
        unique_users = len(set(file_info.get('sid_display', '') for file_info in files_info))
        file_types_count = len(extension_stats)

        # Generate extension list for display
        extension_list_html = ""
        for ext, count in top_extensions:
            percentage = (count / total_files * 100) if total_files > 0 else 0
            extension_list_html += f'<div class="extension-item"><span>{ext}</span><span>{count} ({percentage:.1f}%)</span></div>'

        # Generate table rows
        table_rows = ""
        for file_info in files_info:
            # Format file size
            file_size = file_info.get('file_size', 0)
            formatted_size = f"{file_size:,} bytes"
            
            # Format delete time
            delete_time = str(file_info.get('delete_time', ''))
            
            # Format can_read_content
            can_read = file_info.get('can_read_content', False)
            can_read_class = "true" if can_read else "false"
            can_read_text = "Yes" if can_read else "No"
            
            row = f"""
                <tr>
                    <td>{file_info.get('original_name', '')}</td>
                    <td class="path-cell">{file_info.get('original_path', '')}</td>
                    <td class="file-size">{formatted_size}</td>
                    <td>{delete_time}</td>
                    <td class="path-cell">{file_info.get('sid_folder', '')}</td>
                    <td>{file_info.get('sid_display', '')}</td>
                    <td>{file_info.get('recycled_name', '')}</td>
                    <td class="can-read {can_read_class}">{can_read_text}</td>
                </tr>"""
            table_rows += row

        if not table_rows:
            table_rows = '<tr><td colspan="8" class="no-data">No deleted files found in the Recycle Bin.</td></tr>'

        # Format total size
        formatted_total_size = f"{total_size:,} bytes ({total_size / (1024*1024):.2f} MB)"

        # Generate HTML content
        html_content = html_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_files=len(files_info),
            total_size=formatted_total_size,
            text_files=text_files,
            binary_files=binary_files,
            unique_users=unique_users,
            file_types_count=file_types_count,
            chart_labels=chart_labels,
            chart_data=chart_data,
            chart_colors=chart_colors,
            extension_list=extension_list_html,
            table_rows=table_rows
        )

        # Write to HTML file
        with open(output_file, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)

        print(f"\nAnalysis exported to HTML: {output_file}")

    except Exception as e:
        print(f"Error exporting to HTML: {e}") 