import pandas as pd
import json
from datetime import datetime
import os

def apply_ai_remap():
    distribution_file = "ai_distribution_map.json"
    xlsx_file = "diary_schedule.xlsx"
    
    if not os.path.exists(distribution_file):
        print(f"Error: {distribution_file} not found.")
        return
    
    if not os.path.exists(xlsx_file):
        print(f"Error: {xlsx_file} not found.")
        return

    # Load AI distribution map
    with open(distribution_file, "r", encoding="utf-8") as f:
        ai_map = json.load(f)
    
    # Load the schedule
    df = pd.read_excel(xlsx_file)
    
    # Ensure Conteúdo column exists and is object type (string) to avoid float assignment errors
    if "Conteúdo" not in df.columns:
        df["Conteúdo"] = ""
    else:
        df["Conteúdo"] = df["Conteúdo"].astype(object)
    
    updated_count = 0
    
    for idx, row in df.iterrows():
        # Handle date formatting
        date_val = row["Data"]
        if isinstance(date_val, datetime):
            date_str = date_val.strftime("%d/%m/%Y")
        elif isinstance(date_val, str):
            date_str = date_val
        else:
            continue
            
        aula_id = str(int(row["Aula"]))
        
        # Check if we have a summary for this date and aula
        if date_str in ai_map and aula_id in ai_map[date_str]:
            new_content = ai_map[date_str][aula_id]
            df.at[idx, "Conteúdo"] = new_content
            updated_count += 1
    
    # Save back to XLSX
    df.to_excel(xlsx_file, index=False)
    # Also save a CSV version for easy checking
    df.to_csv("diary_schedule_ai_final.csv", index=False, encoding="utf-8-sig")
    
    print(f"Applied {updated_count} AI-enhanced summaries to {xlsx_file}")

if __name__ == "__main__":
    apply_ai_remap()
