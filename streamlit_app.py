import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import re
import docx
import zipfile
import os
from io import BytesIO
import tempfile  # Import the python-docx module


# Define the function to extract text from a docx file
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Update the extract function to handle PDFs and docx files
def extract_text(file, file_type):
    if file_type == "pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    elif file_type == "docx":
        return extract_text_from_docx(file)

def extract_emails(text):
    return re.findall(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+', text)

def extract_phone_numbers(text):
    return re.findall(r'\b\d{10}\b', text)

st.title('CV Information Extractor')

# Allow PDF and docx file uploads
uploaded_file = st.file_uploader("Upload a PDF or Word file", type=['pdf', 'docx'])
if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1].lower()
    text = extract_text(uploaded_file, file_type)
    emails = extract_emails(text)
    phones = extract_phone_numbers(text)

    # Present the extracted information neatly
    st.subheader("Extracted Information")
    st.write(f"**Filename:** {uploaded_file.name}")
    st.write(f"**Emails:** {', '.join(emails)}")
    st.write(f"**Phone Numbers:** {', '.join(phones)}")

    # Optional: Create a button to show/hide the full extracted text
    if st.button('Show Full Text'):
        st.subheader("Full Text")
        st.text_area("Extracted Text", text, height=250)
def process_zip(uploaded_zip):
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

          # This list will hold all the extracted data
        for root, dirs, files in os.walk(temp_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_type = filename.split('.')[-1].lower()
                if file_type in ['pdf', 'docx']:
                    with open(file_path, "rb") as file:
                        text = extract_text(file, file_type)
                        emails = extract_emails(text)
                        phones = extract_phone_numbers(text)
                        extracted_info.append({
                            "Filename": filename,
                            "Emails": ', '.join(emails),
                            "Phone Numbers": ', '.join(phones),
                            "Extracted Text": text  # Consider using text[:500] if the text is too long
                        })
        return extracted_info 

# Add a function to convert the extracted data to an Excel file
def convert_to_excel(extracted_data):
    df = pd.DataFrame(extracted_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

st.title('CV Folder Information Extractor')
extracted_info = []
# File uploader for ZIP files
uploaded_zip = st.file_uploader("Upload a ZIP file containing the CVs", type='zip')
if uploaded_zip:
    extracted_info = process_zip(uploaded_zip)
    excel_data = convert_to_excel(extracted_info)
    st.download_button(
        label="Download Excel file with extracted data",
        data=excel_data,
        file_name="extracted_cv_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# You can also display the DataFrame in the Streamlit app if you wish
st.dataframe(extracted_info)