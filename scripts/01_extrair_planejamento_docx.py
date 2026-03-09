import docx
import pandas as pd
import json
import re

def extract_planning_data(docx_path):
    doc = docx.Document(docx_path)
    planning_items = []
    
    # We know table 2 (index 2) is the main one from debug_extract.py
    # But let's look for a table with specific headers to be robust
    main_table = None
    for table in doc.tables:
        if len(table.rows) > 0:
            headers = [cell.text.strip().upper() for cell in table.rows[0].cells]
            if "QUANDO SERÁ REALIZADA?" in headers or "EXPERIÊNCIAS E ATIVIDADES PLANEJADAS" in headers:
                main_table = table
                break
    
    if not main_table:
        print("Main planning table not found.")
        return []

    headers = [cell.text.strip() for cell in main_table.rows[0].cells]
    
    current_range = None
    
    for row in main_table.rows[1:]:
        cells = [cell.text.strip() for cell in row.cells]
        if not any(cells): continue
        
        # Check for new date range in first column
        if cells[0]:
            current_range = cells[0]
        
        activity = cells[1]
        subject_info = cells[2]
        
        if not activity and not subject_info: continue
        
        # Extract main subject name from column 3
        # Subjects are: Letramento, Letramento matemático, Sentido Religioso, Conhecimento de Mundo, Brincar
        subject = None
        subjects_to_match = ["LETRAMENTO MATEMÁTICO", "LETRAMENTO", "SENTIDO RELIGIOSO", "CONHECIMENTO DE MUNDO", "BRINCAR"]
        for s in subjects_to_match:
            if s.lower() in subject_info.lower():
                subject = s
                break
        
        if not subject and subject_info:
            # Fallback: take first non-empty line
            lines = [l.strip() for l in subject_info.split('\n') if l.strip()]
            if lines: subject = lines[0].upper()

        planning_items.append({
            "range": current_range,
            "activity": activity,
            "subject": subject,
            "raw_subject": subject_info
        })
    
    return planning_items

if __name__ == "__main__":
    docx_file = "PLANEJAMENTO FEVEREIRO 2026 REVISADO.docx"
    data = extract_planning_data(docx_file)
    
    # Save as JSON for easy consumption by other scripts
    with open("planning_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Extracted {len(data)} planning items to planning_data.json")
    
    # Also save as CSV for visibility
    df = pd.DataFrame(data)
    df.to_csv("planning_data.csv", index=False, encoding="utf-8-sig")
