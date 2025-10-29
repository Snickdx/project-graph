"""
Excel to JSON Converter for Project Graph
==========================================
This script parses the Excel file containing the project graph data
and exports it to a structured JSON format for easy data interchange.
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class ProjectGraphExcelParser:
    """Parse Excel file and convert to structured JSON format"""
    
    def __init__(self, excel_file: str = "graph_model_sample.xlsx"):
        """
        Initialize the parser
        
        Args:
            excel_file: Path to the Excel file to parse
        """
        self.excel_file = excel_file
        self.sheets_data = {}
        self.parsed_data = {}
        
    def load_excel_data(self) -> bool:
        """Load all sheets from the Excel file"""
        try:
            if not os.path.exists(self.excel_file):
                print(f"❌ Excel file not found: {self.excel_file}")
                return False
                
            print(f"📖 Loading Excel file: {self.excel_file}")
            
            # Read all sheets
            xls = pd.ExcelFile(self.excel_file)
            self.sheets_data = {}
            
            for sheet_name in xls.sheet_names:
                print(f"   📄 Reading sheet: {sheet_name}")
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                
                # Clean the data - replace NaN with empty strings
                df = df.fillna("")
                
                # Convert to records (list of dictionaries)
                records = df.to_dict('records')
                
                # Filter out completely empty rows
                records = [record for record in records if any(str(v).strip() for v in record.values())]
                
                self.sheets_data[sheet_name] = {
                    'count': len(records),
                    'columns': list(df.columns),
                    'data': records
                }
                
                print(f"      ✅ {len(records)} records loaded")
            
            print(f"✅ Successfully loaded {len(self.sheets_data)} sheets")
            return True
            
        except Exception as e:
            print(f"❌ Error loading Excel file: {e}")
            return False
    
    def parse_to_structured_format(self) -> Dict[str, Any]:
        """Parse the sheets data into a structured project graph format"""
        print("🔄 Parsing data into structured format...")
        
        # Initialize the structured data
        self.parsed_data = {
            "metadata": {
                "source_file": self.excel_file,
                "export_timestamp": datetime.now().isoformat(),
                "total_sheets": len(self.sheets_data),
                "sheet_names": list(self.sheets_data.keys())
            },
            "nodes": {},
            "relationships": [],
            "raw_sheets": self.sheets_data,
            "statistics": {}
        }
        
        # Parse each sheet as node types
        node_sheets = [
            "Project", "Stakeholder", "Role", "Feature", "Functional_Requirement",
            "Domain_Knowledge", "Budget", "Line_Item", "Client", "Constraint",
            "Goal", "Task", "Artifact", "Decision", "Qual_Scenario",
            "Goal_Quotation", "Priority_Level", "KPI", "Evaluation",
            "Timeline", "Milestone", "Context", "Business", "Technical",
            "Adjacent_System", "Input_From_Product", "Output_From_Product"
        ]
        
        # Process node sheets
        for sheet_name in node_sheets:
            if sheet_name in self.sheets_data:
                self.parsed_data["nodes"][sheet_name] = self.sheets_data[sheet_name]["data"]
        
        # Process relationships sheet if it exists
        if "Relationships" in self.sheets_data:
            self.parsed_data["relationships"] = self.sheets_data["Relationships"]["data"]
        
        # Generate statistics
        self._generate_statistics()
        
        print("✅ Data parsing completed")
        return self.parsed_data
    
    def _generate_statistics(self):
        """Generate statistics about the parsed data"""
        stats = {
            "node_counts": {},
            "total_nodes": 0,
            "total_relationships": len(self.parsed_data.get("relationships", [])),
            "sheets_with_data": 0,
            "empty_sheets": []
        }
        
        # Count nodes by type
        for node_type, nodes in self.parsed_data["nodes"].items():
            count = len(nodes) if nodes else 0
            stats["node_counts"][node_type] = count
            stats["total_nodes"] += count
            
            if count > 0:
                stats["sheets_with_data"] += 1
            else:
                stats["empty_sheets"].append(node_type)
        
        # Additional analysis
        stats["node_types_with_data"] = [
            node_type for node_type, count in stats["node_counts"].items() if count > 0
        ]
        
        self.parsed_data["statistics"] = stats
    
    def export_to_json(self, output_file: str = None, pretty_print: bool = True) -> str:
        """
        Export the parsed data to JSON format
        
        Args:
            output_file: Output JSON file path (auto-generated if None)
            pretty_print: Whether to format JSON with indentation
            
        Returns:
            Path to the exported JSON file
        """
        if not self.parsed_data:
            print("❌ No data to export. Please load and parse data first.")
            return None
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(self.excel_file)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{base_name}_export_{timestamp}.json"
        
        try:
            print(f"💾 Exporting data to: {output_file}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if pretty_print:
                    json.dump(self.parsed_data, f, indent=2, ensure_ascii=False, default=str)
                else:
                    json.dump(self.parsed_data, f, ensure_ascii=False, default=str)
            
            # Get file size
            file_size = os.path.getsize(output_file)
            print(f"✅ Export completed successfully!")
            print(f"   📁 File: {output_file}")
            print(f"   📊 Size: {file_size:,} bytes")
            
            return output_file
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
            return None
    
    def export_summary_report(self, output_file: str = None) -> str:
        """Export a summary report of the parsed data"""
        if not self.parsed_data:
            print("❌ No data to summarize. Please load and parse data first.")
            return None
        
        if output_file is None:
            base_name = os.path.splitext(self.excel_file)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{base_name}_summary_{timestamp}.json"
        
        # Create summary data
        summary = {
            "metadata": self.parsed_data["metadata"],
            "statistics": self.parsed_data["statistics"],
            "data_quality": self._analyze_data_quality(),
            "schema_analysis": self._analyze_schema()
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"📋 Summary report exported: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Error exporting summary: {e}")
            return None
    
    def _analyze_data_quality(self) -> Dict[str, Any]:
        """Analyze data quality issues"""
        quality_report = {
            "missing_ids": [],
            "duplicate_ids": [],
            "empty_required_fields": [],
            "data_type_issues": []
        }
        
        # Check for missing IDs and duplicates
        for node_type, nodes in self.parsed_data["nodes"].items():
            if not nodes:
                continue
                
            ids_seen = set()
            for i, node in enumerate(nodes):
                node_id = node.get("id", "")
                
                # Check for missing ID
                if not str(node_id).strip():
                    quality_report["missing_ids"].append({
                        "sheet": node_type,
                        "row": i + 1,
                        "issue": "Missing ID"
                    })
                
                # Check for duplicate ID
                elif node_id in ids_seen:
                    quality_report["duplicate_ids"].append({
                        "sheet": node_type,
                        "id": node_id,
                        "issue": "Duplicate ID"
                    })
                else:
                    ids_seen.add(node_id)
        
        return quality_report
    
    def _analyze_schema(self) -> Dict[str, Any]:
        """Analyze the schema structure"""
        schema_analysis = {
            "common_columns": [],
            "unique_columns_by_sheet": {},
            "column_frequency": {}
        }
        
        all_columns = []
        sheet_columns = {}
        
        # Collect all columns
        for sheet_name, sheet_info in self.sheets_data.items():
            columns = sheet_info.get("columns", [])
            sheet_columns[sheet_name] = columns
            all_columns.extend(columns)
        
        # Count column frequency
        from collections import Counter
        column_counts = Counter(all_columns)
        schema_analysis["column_frequency"] = dict(column_counts)
        
        # Find common columns (appear in multiple sheets)
        schema_analysis["common_columns"] = [
            col for col, count in column_counts.items() if count > 1
        ]
        
        # Find unique columns per sheet
        for sheet_name, columns in sheet_columns.items():
            unique_cols = [col for col in columns if column_counts[col] == 1]
            if unique_cols:
                schema_analysis["unique_columns_by_sheet"][sheet_name] = unique_cols
        
        return schema_analysis
    
    def print_summary(self):
        """Print a summary of the parsed data"""
        if not self.parsed_data:
            print("❌ No data loaded. Please load and parse data first.")
            return
        
        stats = self.parsed_data["statistics"]
        
        print("\n" + "="*60)
        print("📊 PROJECT GRAPH DATA SUMMARY")
        print("="*60)
        
        print(f"📁 Source file: {self.parsed_data['metadata']['source_file']}")
        print(f"⏰ Parsed at: {self.parsed_data['metadata']['export_timestamp']}")
        print(f"📄 Total sheets: {stats['total_relationships']}")
        print(f"🏗️  Total nodes: {stats['total_nodes']}")
        print(f"🔗 Total relationships: {stats['total_relationships']}")
        
        print(f"\n📋 Node counts by type:")
        for node_type, count in sorted(stats["node_counts"].items()):
            status = "✅" if count > 0 else "📭"
            print(f"   {status} {node_type}: {count}")
        
        if stats["empty_sheets"]:
            print(f"\n📭 Empty sheets: {', '.join(stats['empty_sheets'])}")
        
        print("\n" + "="*60)

def main():
    """Main function to run the Excel parser"""
    print("📊 Excel to JSON Project Graph Parser")
    print("=" * 50)
    
    # Check if Excel file exists
    excel_files = [
        "graph_model_sample.xlsx",
        "project_graph.xlsx"  # Alternative name user mentioned
    ]
    
    excel_file = None
    for file in excel_files:
        if os.path.exists(file):
            excel_file = file
            break
    
    if not excel_file:
        print("❌ Excel file not found. Looking for:")
        for file in excel_files:
            print(f"   - {file}")
        
        # Ask user for custom file
        custom_file = input("\nEnter Excel file path (or press Enter to exit): ").strip()
        if custom_file and os.path.exists(custom_file):
            excel_file = custom_file
        else:
            print("Exiting...")
            return
    
    # Initialize parser
    parser = ProjectGraphExcelParser(excel_file)
    
    # Load and parse data
    if not parser.load_excel_data():
        return
    
    parser.parse_to_structured_format()
    parser.print_summary()
    
    # Export options
    print("\nExport options:")
    print("1. Export full JSON")
    print("2. Export summary report only")
    print("3. Export both")
    print("4. Skip export")
    
    choice = input("Choose option (1-4): ").strip()
    
    if choice in ["1", "3"]:
        json_file = parser.export_to_json()
        if json_file:
            print(f"✅ Full data exported to: {json_file}")
    
    if choice in ["2", "3"]:
        summary_file = parser.export_summary_report()
        if summary_file:
            print(f"✅ Summary exported to: {summary_file}")
    
    print("\n🎉 Processing completed!")

if __name__ == "__main__":
    main()