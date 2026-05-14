import argparse
import pandas as pd
import json
import re

def main():
    parser = argparse.ArgumentParser(description="Generate MAGport HTML report")
    parser.add_argument("--summary", required=True, help="Input summary TSV file")
    parser.add_argument("--template", required=True, help="Input HTML template file")
    parser.add_argument("--output", required=True, help="Output HTML report file")
    parser.add_argument("--title", required=False, default="MAGport Report", help="Title of the report")
    parser.add_argument("--input-dir", required=False, default="Input Directory", help="Input directory of MAGs (for display)")
    args = parser.parse_args()

    # 1. Read summary.tsv and convert to json format
    df = pd.read_csv(args.summary, sep='\t')
    
    # Replace pd.NA and NaNs with None for JSON serialization
    df = df.where(pd.notnull(df), None)
    
    data_json = df.to_dict(orient='records')
    n_mag = len(data_json)
    
    # 2. Insert data into HTML report template and generate report.html
    with open(args.template, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    js_payload = f"""// Data injected by MAGport
const page_title = "{args.title}";
const n_mag = {n_mag};
const input_dir = "{args.input_dir}";
const data = {json.dumps(data_json)};
// End"""

    # Use regex to find the mock data block and replace it
    pattern = re.compile(r'// Mock data for testing.*?// End', re.DOTALL)
    
    if pattern.search(html_content):
        new_html = pattern.sub(js_payload, html_content)
        print(f"Successfully injected {n_mag} records into HTML template.")
    else:
        print("Warning: Could not find '// Mock data for testing' ... '// End' in template.")
        new_html = html_content + f"\n<script>\n{js_payload}\n</script>"
        
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Report saved to {args.output}")

if __name__ == "__main__":
    main()