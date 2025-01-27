import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


def save_to_obsidian(note_title, vault_base_path, uploaded_file, content):
    """Save notes and images with exact path structure"""
    try:
        # Create full paths according to your structure
        generated_notes_dir = os.path.join(vault_base_path, "Generated Notes")
        assets_dir = os.path.join(generated_notes_dir, "assets")

        # Create directories if they don't exist
        os.makedirs(assets_dir, exist_ok=True)

        # Save image to assets
        image_path = os.path.join(assets_dir, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Create note with correct image embed path
        note_content = f"""# {note_title}\n\n{content}\n\n![[assets/{uploaded_file.name}]]\n"""

        # Save note file
        note_filename = f"{note_title}.md"
        note_path = os.path.join(generated_notes_dir, note_filename)
        with open(note_path, "w") as f:
            f.write(note_content)

        return note_path

    except Exception as e:
        st.error(f"Error saving to Obsidian: {str(e)}")
        return None


# Streamlit UI
st.title("📝 Image to Obsidian Notes")
st.write("Convert images to properly formatted Obsidian notes with perfect image links")

# Configure your exact path
VAULT_BASE_PATH = "/Users/ayrafraihan/Library/Mobile Documents/com~apple~CloudDocs/obsidian new/second brain [ssd]/AI generated notes"

# File upload
uploaded_file = st.file_uploader("Upload whiteboard/PPT image", type=["png", "jpg", "jpeg"])
note_title = st.text_input("Note Title", "Meeting Notes")

if uploaded_file:
    # Display preview
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    if st.button("Generate & Save"):
        with st.spinner("Processing..."):
            try:
                # Generate content
                response = model.generate_content([
                    "Extract text and create markdown-formatted notes from this image. Include headings and bullet points:",
                    img
                ])

                # Save to Obsidian
                note_path = save_to_obsidian(
                    note_title=note_title,
                    vault_base_path=VAULT_BASE_PATH,
                    uploaded_file=uploaded_file,
                    content=response.text
                )

                if note_path:
                    st.success(f"Note saved successfully at:\n{note_path}")
                    st.markdown("### Preview of generated notes:")
                    st.markdown(response.text)
                    st.markdown(f"### Image embedded at:\n`![[assets/{uploaded_file.name}]]`")

            except Exception as e:
                st.error(f"Processing error: {str(e)}")