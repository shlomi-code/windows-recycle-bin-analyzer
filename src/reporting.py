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
        
        # Format delete time properly
        delete_time_obj = file_info.get('delete_time', 'Unknown')
        if delete_time_obj and hasattr(delete_time_obj, 'strftime'):
            delete_time_str = delete_time_obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            delete_time_str = str(delete_time_obj)
        print(f"   Delete Time: {delete_time_str}")
        
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
                # Format delete time properly
                delete_time_obj = file_info.get('delete_time', '')
                if delete_time_obj and hasattr(delete_time_obj, 'strftime'):
                    delete_time_str = delete_time_obj.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    delete_time_str = str(delete_time_obj) if delete_time_obj else ''
                
                row = {
                    'original_name': file_info.get('original_name', ''),
                    'original_path': file_info.get('original_path', ''),
                    'file_size': file_info.get('file_size', 0),
                    'delete_time': delete_time_str,
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
            # Format delete time properly
            delete_time_obj = file_info.get('delete_time', '')
            if delete_time_obj and hasattr(delete_time_obj, 'strftime'):
                delete_time_str = delete_time_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                delete_time_str = str(delete_time_obj) if delete_time_obj else ''
            
            json_file_info = {
                'original_name': file_info.get('original_name', ''),
                'original_path': str(file_info.get('original_path', '')),
                'file_size': file_info.get('file_size', 0),
                'delete_time': delete_time_str,
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
            '#475569', '#64748b', '#94a3b8', '#cbd5e1', '#e2e8f0',
            '#334155', '#1e293b', '#f1f5f9', '#94a3b8', '#64748b'
        ]
        
        # HTML template with embedded CSS and JavaScript
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windows Recycle Bin Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
            padding: 20px;
            color: #1e293b;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }}
        
        .header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 300;
            position: relative;
            z-index: 1;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .analysis-info {{
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #475569;
            box-shadow: 0 8px 25px rgba(71, 85, 105, 0.15);
        }}
        
        .analysis-info h2 {{
            color: #1e293b;
            font-size: 1.3rem;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .analysis-info p {{
            margin: 8px 0;
            color: #334155;
            font-weight: 500;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(135deg, #475569 0%, #64748b 100%);
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        }}
        
        .stat-icon {{
            font-size: 2rem;
            margin-bottom: 15px;
            color: #475569;
        }}
        
        .stat-label {{
            font-weight: 600;
            color: #64748b;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .stat-value {{
            color: #1e293b;
            font-size: 1.8rem;
            font-weight: 700;
        }}
        
        .charts-section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title i {{
            color: #475569;
        }}
        
        .charts-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
        }}
        
        .chart-title {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            width: 100%;
        }}
        
        .controls-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
        }}
        
        .search-container {{
            position: relative;
            margin-bottom: 20px;
        }}
        
        .search-box {{
            width: 100%;
            padding: 15px 20px 15px 50px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #f8fafc;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #475569;
            background: white;
            box-shadow: 0 0 0 3px rgba(71, 85, 105, 0.1);
        }}
        
        .search-icon {{
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: #a0aec0;
            font-size: 18px;
        }}
        
        .export-buttons {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .export-btn {{
            background: linear-gradient(135deg, #475569 0%, #64748b 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .export-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(71, 85, 105, 0.3);
        }}
        
        .table-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
            overflow: hidden;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            font-size: 14px;
        }}
        
        th {{
            background: linear-gradient(135deg, #475569 0%, #64748b 100%);
            color: white;
            padding: 18px 12px;
            text-align: left;
            cursor: pointer;
            user-select: none;
            position: relative;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        th:hover {{
            background: linear-gradient(135deg, #334155 0%, #475569 100%);
        }}
        
        th::after {{
            content: '↕';
            position: absolute;
            right: 12px;
            opacity: 0.7;
            font-size: 12px;
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
            padding: 16px 12px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: top;
            transition: background-color 0.2s ease;
        }}
        
        tr:hover {{
            background-color: #f8fafc;
        }}
        
        tr:nth-child(even) {{
            background-color: #fafbfc;
        }}
        
        tr:nth-child(even):hover {{
            background-color: #f1f5f9;
        }}
        
        .file-size {{
            text-align: right;
            font-weight: 500;
            color: #64748b;
        }}
        
        .can-read {{
            text-align: center;
        }}
        
        .can-read.true {{
            color: #38a169;
            font-weight: 600;
        }}
        
        .can-read.false {{
            color: #e53e3e;
            font-weight: 500;
        }}
        
        .path-cell {{
            max-width: 300px;
            word-wrap: break-word;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            color: #64748b;
        }}
        
        .no-data {{
            text-align: center;
            color: #a0aec0;
            font-style: italic;
            padding: 60px;
            font-size: 1.1rem;
        }}
        
        .extension-list {{
            margin-top: 15px;
            font-size: 0.9em;
            color: #64748b;
        }}
        
        .extension-item {{
            display: flex;
            justify-content: space-between;
            margin: 4px 0;
            padding: 4px 0;
            border-bottom: 1px solid #f1f5f9;
        }}
        
        .extension-item:last-child {{
            border-bottom: none;
        }}
        
        .extension-name {{
            font-weight: 500;
        }}
        
        .extension-count {{
            color: #475569;
            font-weight: 600;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 20px 15px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .charts-container {{
                grid-template-columns: 1fr;
            }}
            
            .export-buttons {{
                flex-direction: column;
            }}
            
            .export-btn {{
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-trash-alt"></i> Windows Recycle Bin Analysis</h1>
            <div class="subtitle">Comprehensive Analysis Report</div>
        </div>
        
        <div class="content">
            <div class="analysis-info">
                <h2><i class="fas fa-info-circle"></i> Analysis Information</h2>
                <p><strong>Analysis Timestamp:</strong> {timestamp}</p>
                <p><strong>Total Files Analyzed:</strong> {total_files}</p>
                <p><strong>Report Format:</strong> Professional HTML Report</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-hdd"></i></div>
                    <div class="stat-label">Total Size</div>
                    <div class="stat-value">{total_size}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-users"></i></div>
                    <div class="stat-label">Unique Users</div>
                    <div class="stat-value">{unique_users}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-file-alt"></i></div>
                    <div class="stat-label">File Types</div>
                    <div class="stat-value">{file_types_count}</div>
                </div>
            </div>

            <div class="charts-section">
                <h2 class="section-title"><i class="fas fa-chart-pie"></i> File Distribution Analysis</h2>
                <div class="charts-container">
                    <div class="chart-card">
                        <div class="chart-title">File Extensions Distribution</div>
                        <div class="chart-container">
                            <canvas id="extensionChart"></canvas>
                        </div>
                        <div class="extension-list">
                            {extension_list}
                        </div>
                    </div>
                </div>
            </div>

            <div class="controls-section">
                <div class="search-container">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" id="searchBox" class="search-box" placeholder="Search files by name, path, or user...">
                </div>
                <div class="export-buttons">
                    <button class="export-btn" onclick="exportToCSV()">
                        <i class="fas fa-file-csv"></i> Export CSV
                    </button>
                    <button class="export-btn" onclick="exportToJSON()">
                        <i class="fas fa-file-code"></i> Export JSON
                    </button>
                    <button class="export-btn" onclick="printReport()">
                        <i class="fas fa-print"></i> Print Report
                    </button>
                </div>
            </div>

            <div class="table-section">
                <h2 class="section-title"><i class="fas fa-table"></i> Detailed File Information</h2>
                <div class="table-wrapper">
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
            </div>
        </div>
    </div>

    <script>
        let currentSort = {{ column: -1, direction: 'asc' }};
        let originalData = [];
        let filteredData = [];

        // Initialize the table
        document.addEventListener('DOMContentLoaded', function() {{
            // Store original data for filtering
            const tbody = document.querySelector('#dataTable tbody');
            const rows = tbody.querySelectorAll('tr');
            originalData = Array.from(rows).map(row => row.innerHTML);
            filteredData = [...originalData];
            
            // Add search functionality
            document.getElementById('searchBox').addEventListener('input', filterTable);
            
            // Initialize chart
            initializeChart();
            
            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {{
                if (e.ctrlKey && e.key === 'f') {{
                    e.preventDefault();
                    document.getElementById('searchBox').focus();
                }}
            }});
        }});

        function initializeChart() {{
            const ctx = document.getElementById('extensionChart').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: {chart_labels},
                    datasets: [{{
                        data: {chart_data},
                        backgroundColor: {chart_colors},
                        borderWidth: 3,
                        borderColor: '#fff',
                        hoverBorderWidth: 4,
                        hoverBorderColor: '#475569'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '50%',
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 15,
                                usePointStyle: true,
                                font: {{
                                    size: 12,
                                    weight: '500'
                                }},
                                color: '#64748b'
                            }}
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#475569',
                            borderWidth: 1,
                            cornerRadius: 8,
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}} files (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }},
                    animation: {{
                        animateRotate: true,
                        animateScale: true,
                        duration: 1000
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
            
            filteredData = [];
            rows.forEach((row, index) => {{
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {{
                    row.style.display = '';
                    filteredData.push(row.innerHTML);
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            // Update result count
            updateResultCount();
        }}

        function updateResultCount() {{
            const visibleRows = document.querySelectorAll('#dataTable tbody tr:not([style*="display: none"])');
            const totalRows = document.querySelectorAll('#dataTable tbody tr').length;
            
            // You could add a result counter here if desired
            console.log(`Showing ${{visibleRows.length}} of ${{totalRows}} files`);
        }}

        function exportToCSV() {{
            const table = document.getElementById('dataTable');
            const rows = Array.from(table.querySelectorAll('tr:not([style*="display: none"])'));
            
            let csv = [];
            rows.forEach(row => {{
                const cells = Array.from(row.querySelectorAll('th, td'));
                const rowData = cells.map(cell => {{
                    let text = cell.textContent.trim();
                    // Escape quotes and wrap in quotes if contains comma
                    if (text.includes(',') || text.includes('"') || text.includes('\\n')) {{
                        text = '"' + text.replace(/"/g, '""') + '"';
                    }}
                    return text;
                }});
                csv.push(rowData.join(','));
            }});
            
            const csvContent = csv.join('\\n');
            downloadFile(csvContent, 'recycle_bin_analysis.csv', 'text/csv');
        }}

        function exportToJSON() {{
            const table = document.getElementById('dataTable');
            const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
            const rows = Array.from(table.querySelectorAll('tbody tr:not([style*="display: none"])'));
            
            const jsonData = {{
                exportInfo: {{
                    timestamp: new Date().toISOString(),
                    totalFiles: rows.length,
                    exportType: 'filtered_data'
                }},
                files: rows.map(row => {{
                    const cells = Array.from(row.querySelectorAll('td'));
                    const fileData = {{}};
                    headers.forEach((header, index) => {{
                        fileData[header.toLowerCase().replace(/\\s+/g, '_')] = cells[index] ? cells[index].textContent.trim() : '';
                    }});
                    return fileData;
                }})
            }};
            
            downloadFile(JSON.stringify(jsonData, null, 2), 'recycle_bin_analysis.json', 'application/json');
        }}

        function printReport() {{
            // Create a print-friendly version
            const printWindow = window.open('', '_blank');
            const originalContent = document.querySelector('.container').innerHTML;
            
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Recycle Bin Analysis Report</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ background: #1e293b; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        @media print {{ 
                            body {{ margin: 0; }}
                            .export-buttons {{ display: none; }}
                        }}
                    </style>
                </head>
                <body>
                    ${{originalContent}}
                </body>
                </html>
            `);
            
            printWindow.document.close();
            printWindow.print();
        }}

        function downloadFile(content, filename, mimeType) {{
            const blob = new Blob([content], {{ type: mimeType }});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }}

        function formatFileSize(bytes) {{
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            if (bytes === 0) return '0 B';
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
        }}

        // Add smooth scrolling for better UX
        function smoothScrollTo(element) {{
            element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}

        // Add loading animation
        function showLoading() {{
            const loader = document.createElement('div');
            loader.id = 'loader';
            loader.innerHTML = '<div class="spinner"></div>';
            loader.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            `;
            document.body.appendChild(loader);
        }}

        function hideLoading() {{
            const loader = document.getElementById('loader');
            if (loader) {{
                loader.remove();
            }}
        }}
    </script>
</body>
</html>"""

        # Calculate statistics
        total_size = sum(file_info.get('file_size', 0) for file_info in files_info)
        unique_users = len(set(file_info.get('sid_display', '') for file_info in files_info))
        file_types_count = len(extension_stats)

        # Generate extension list for display
        extension_list_html = ""
        for ext, count in top_extensions:
            percentage = (count / total_files * 100) if total_files > 0 else 0
            extension_list_html += f'<div class="extension-item"><span class="extension-name">{ext}</span><span class="extension-count">{count} ({percentage:.1f}%)</span></div>'

        # Generate table rows
        table_rows = ""
        for file_info in files_info:
            # Format file size
            file_size = file_info.get('file_size', 0)
            formatted_size = f"{file_size:,} bytes"
            
            # Format delete time with proper formatting
            delete_time_obj = file_info.get('delete_time', '')
            if delete_time_obj and hasattr(delete_time_obj, 'strftime'):
                delete_time = delete_time_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                delete_time = str(delete_time_obj) if delete_time_obj else ''
            
            # Format can_read_content
            can_read = file_info.get('can_read_content', False)
            can_read_class = "true" if can_read else "false"
            can_read_text = "Yes" if can_read else "No"
            
            # Extract username only (remove SID if present)
            username = file_info.get('sid_display', '')
            if username and '(' in username and ')' in username:
                # Extract username from format like "username (SID)"
                username = username.split('(')[0].strip()
            
            row = f"""
                <tr>
                    <td>{file_info.get('original_name', '')}</td>
                    <td class="path-cell">{file_info.get('original_path', '')}</td>
                    <td class="file-size">{formatted_size}</td>
                    <td>{delete_time}</td>
                    <td class="path-cell">{file_info.get('sid_folder', '')}</td>
                    <td>{username}</td>
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