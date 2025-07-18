import pandas as pd
import ast
import os

def clean_and_format_text_sheets(data):
    if isinstance(data, str) and data.strip():
        try:
            items = ast.literal_eval(data)
            if isinstance(items, list) and all(isinstance(i, dict) for i in items):
                formatted_entries = []
                for entry in items:
                    formatted_entry = "\n".join(
                        [f"- {key}: {value}" for key, value in entry.items() if value]
                    )
                    formatted_entries.append(formatted_entry)
                return "\n\n".join(formatted_entries)
            else:
                return data.strip()
        except (SyntaxError, ValueError):
            return data.strip()
    return "N/A"

def clean_scraped_data(input_path="Data/Linkedin_SCU_Alumni_2025.csv",
                       output_path="Data/Scraping Result/Cleaned_Linkedin_SCU_Alumni_2025.csv"):

    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return None

    df = pd.read_csv(input_path)

    for column in ["Experience", "Education", "Licenses & Certifications"]:
        if column in df.columns:
            df[column] = df[column].apply(clean_and_format_text_sheets)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned data saved to: {output_path}")
    return output_path
