import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader
import google.generativeai as genai

# streamlit run app_summary.py

# Configure Google Gemini API
genai.configure(api_key='AIzaSyCUAMXGwO-lHvXJmwuh4jsEKsQeZ_vwcbM')
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

def read_pdf(pdf_path):
    """Read PDF and merge text content from all pages"""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_paper_title(pdf_text):
    """Generate paper title using Google Gemini API"""
    title_prompt = f"Extract or generate the most appropriate academic paper title from the following text. Only output the title:\n\n{pdf_text[:1000]}"
    try:
        title_response = model.generate_content(title_prompt)
        return title_response.text.strip() if title_response else "Untitled Paper"
    except Exception as e:
        st.error(f"Error generating title: {e}")
        return "Untitled Paper"

def generate_paper_summary(pdf_text):
    """Generate summary and key points using Google Gemini API"""
    summary_prompt = f"Please generate a comprehensive summary of the following PDF text, including main points and key insights. Provide the summary in clear, concise language:\n\n{pdf_text[:2000]}"
    try:
        summary_response = model.generate_content(summary_prompt)
        return summary_response.text.strip() if summary_response else "Unable to generate summary."
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "An error occurred while generating the summary."

def generate_image_description(image_path):
    """Generate image description using Google Gemini API"""
    try:
        myfile = genai.upload_file(image_path)
        prompt = "Output a detailed description of this image. Focus on key context, and potential significance. Write in a clear, informative style."
        result = model.generate_content([myfile, "\n\n", prompt])
        return result.text.strip() if result else f"Unable to generate description for: {image_path}"
    except Exception as e:
        st.error(f"Error generating image description: {e}")
        return "Unable to generate image description"

def main():
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 36px;
        color: #4CAF50;
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #555;
    }
    .upload-section {
        padding: 20px;
        background: #f9f9f9;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-section {
        background: #f0f0f0;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }
    .paper-title {
        text-align: center;
        font-size: 24px;
        color: #333;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # App title and description
    st.markdown('<h1 class="main-title">Paper Helper</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Upload your PDF and images to get comprehensive insights</p>', unsafe_allow_html=True)

    # Upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Choose a PDF file", type=["pdf"])
    uploaded_images = st.file_uploader("Choose images (multiple allowed)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Generate insights button
    if uploaded_pdf and st.button("Generate Insights"):
        with st.spinner("Analyzing your document and images..."):
            # Save PDF to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(uploaded_pdf.read())
                temp_pdf_path = temp_pdf.name

            # Read PDF content and generate title and summary
            pdf_text = read_pdf(temp_pdf_path)
            paper_title = generate_paper_title(pdf_text)
            summary = generate_paper_summary(pdf_text)

            # Display paper details
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            
            # Display paper title
            st.markdown(f'<div class="paper-title" style="font-size: 28px;">Paper Title: {paper_title}</div>', unsafe_allow_html=True)
            
            # Display summary
            st.subheader("Paper Summary")
            st.write(summary)
            st.markdown('</div>', unsafe_allow_html=True)

    # Generate image descriptions
    if uploaded_images:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.subheader("Image Descriptions")
        
        # Temporary storage for image files
        image_paths = []
        for uploaded_image in uploaded_images:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
                temp_image.write(uploaded_image.read())
                image_paths.append(temp_image.name)

        # Display each image with its description
        for i, image_path in enumerate(image_paths, 1):
            st.markdown(f"### Image {i}")
            
            # Display the image
            st.image(image_path, use_container_width=True)
            
            # Generate and display description
            description = generate_image_description(image_path)
            st.write(description)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()