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
    """Save notes with verified image paths"""
    try:
        # ========== 1. Path Construction ==========
        base_dir = os.path.expanduser(vault_base_path)
        generated_notes = os.path.join(base_dir, "Generated Notes")
        assets_dir = os.path.join(generated_notes, "assets")

        # Create directories with existence check
        os.makedirs(assets_dir, exist_ok=True)
        if not os.path.exists(assets_dir):
            raise Exception(f"Failed to create assets directory at {assets_dir}")

        # ========== 2. File Operations ==========
        # Sanitize filename for Apple's filesystem
        safe_filename = uploaded_file.name.replace(" ", "_").replace(".", "-")
        image_path = os.path.join(assets_dir, safe_filename)

        # Write image with verification
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if not os.path.exists(image_path):
            raise Exception(f"Failed to save image at {image_path}")

        # ========== 3. Note Creation ==========
        note_content = f"""# {note_title}
![[assets/{safe_filename}]]  <!-- Obsidian embed -->

{content}
"""
        note_path = os.path.join(generated_notes, f"{note_title}.md")

        with open(note_path, "w") as f:
            f.write(note_content)

        return note_path, image_path

    except Exception as e:
        st.error(f"Obsidian Save Error: {str(e)}")
        return None, None


# Streamlit UI
st.title("📝 Obsidian Note Generator")

# Configure your EXACT path (verify in Finder)
VAULT_BASE_PATH = "/Users/ayrafraihan/Library/Mobile Documents/com~apple~CloudDocs/obsidian new/second brain [ssd]/AI generated notes"

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
note_title = st.text_input("Note Title", "Meeting Notes")

if uploaded_file and st.button("Generate & Save"):
    with st.spinner("Processing..."):
        try:
            # Generate content
            img = Image.open(uploaded_file)
            response = model.generate_content([
                "Create markdown notes from this image. Use headings, bullet points, and proper formatting:",
                img
            ])

            # Save to Obsidian
            note_path, image_path = save_to_obsidian(
                note_title=note_title,
                vault_base_path=VAULT_BASE_PATH,
                uploaded_file=uploaded_file,
                content=response.text
            )

            if note_path and image_path:
                st.success(f"""
                **Note saved successfully!**  
                - Note location: `{note_path}`  
                - Image location: `{image_path}`
                """)

                # Verification checks
                st.markdown("### Troubleshooting Guide")
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox("✅ Note file exists", value=os.path.exists(note_path))
                    st.checkbox("✅ Image file exists", value=os.path.exists(image_path))
                with col2:
                    st.checkbox("✅ Assets directory exists",
                                value=os.path.exists(os.path.dirname(image_path)))
                    st.checkbox("✅ Path matches Obsidian",
                                value=VAULT_BASE_PATH in note_path)

                st.markdown(f"""
                ### Obsidian Embed Code
                ```markdown
                ![[assets/{os.path.basename(image_path)}]]
                ```
                """)

        except Exception as e:
            st.error(f"Fatal Error: {str(e)}")