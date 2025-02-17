import pdfplumber
import pandas as pd
import re

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def remove_introductory_text(text):
    """Removes introductory text before the main content."""
    intro_end = "Copyright © MEDI-T 1998"
    if intro_end in text:
        text = text.split(intro_end, 1)[-1].strip()
    return text

def split_sentences(text):
    """Splits text into sentences, ensuring bracketed text remains together."""
    sentences = []
    sentence = ""
    inside_brackets = False

    for char in text:
        if char == "(":
            inside_brackets = True
        elif char == ")":
            inside_brackets = False
        sentence += char
        if char == "." and not inside_brackets:
            sentences.append(sentence.strip())
            sentence = ""
    if sentence:
        sentences.append(sentence.strip())
    return [s for s in sentences if s]

def parse_text(text):
    """Parses the extracted text into a structured format."""
    lines = text.split("\n")
    data = []
    drug = None
    name = None
    symptoms = []
    amelioration = ""
    aggravation = ""
    skip_section = False

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip the "Relationship" section entirely until a new drug entry or empty line
        if "Relationship" in line:
            skip_section = True
            continue
        if skip_section and (not line or re.match(r'^[A-Z][a-zA-Z0-9\s-]+\.$', line)):
            skip_section = False  # Stop skipping when encountering an empty line or a new drug name

        if skip_section:
            continue  # Keep skipping lines within the "Relationship" section

        if "Keynotes by H.C. Allen" in line:
            continue

        if re.match(r'^[A-Z][a-zA-Z0-9\s-]+\.$', line):
            if drug and name:
                for symptom in symptoms:
                    data.append([drug, name, symptom, amelioration, aggravation])
                symptoms = []
                amelioration = ""
                aggravation = ""

            drug = line.strip(".")
            name = None
            continue

        if re.search(r'\(.*\)', line) and name is None:
            name = line.strip(".")
            continue

        if "Amelioration." in line:
            amelioration = line.replace("Amelioration.", "").strip()
            continue
        elif amelioration and line:
            amelioration += " " + line.strip()
            continue

        if "Aggravation." in line:
            aggravation = line.replace("Aggravation.", "").strip()
            continue
        elif aggravation and line:
            aggravation += " " + line.strip()
            continue

        if drug and name:
            sentence_list = split_sentences(line)
            symptoms.extend(sentence_list)

    if drug and name:
        for symptom in symptoms:
            data.append([drug, name, symptom, amelioration, aggravation])

    return data


def remove_unwanted_rows(df):
    """Removes rows where 'Symptoms' contains only a closing bracket, double quote, or a single letter followed by a period."""
    pattern = r'^\s*(\)|"|[a-zA-Z])\.\s*$'
    df = df[~df["Symptoms"].str.match(pattern, na=False)]
    
    # Remove rows where 'Symptoms' contains only a period `.`
    df = df[df["Symptoms"] != "."]
    
    return df

def clean_text(text):
    """Removes complete bracketed content and unclosed brackets."""
    if pd.isna(text):  # Skip NaN values
        return text
    text = re.sub(r"\(.*?\)", "", text).strip()  # Remove text inside `()`
    text = re.sub(r"\([^\)]*$", "", text).strip()  # Remove unclosed `(` and following text
    return text

def save_to_csv(data, output_path):
    """Saves cleaned data to CSV."""
    columns = ["Drug", "Name", "Symptoms", "Amelioration", "Aggravation"]
    df = pd.DataFrame(data, columns=columns)
    
    # Step 2: Remove unwanted rows
    df = remove_unwanted_rows(df)
    
    # Step 3: Remove bracketed content and unclosed brackets
    df["Symptoms"] = df["Symptoms"].apply(clean_text)

    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")

def main():
    pdf_path = "keynotes-and-characteristics-allen.pdf"  # Update with actual path
    output_csv = "cleaned_output.csv"

    # Step 1: Extract and parse text
    text = extract_text_from_pdf(pdf_path)
    text = remove_introductory_text(text)
    data = parse_text(text)

    # Step 2-3: Clean and save data
    save_to_csv(data, output_csv)

if __name__ == "__main__":
    main()
