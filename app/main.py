import streamlit as st
import json
import os

from app.llm.llm_service import ensure_api_key, init_llm, generate_outline
from app.utils.pptx_generator import generate_slides

JSON_FILE = "presentation_outline.json"
JSON_PATH = f"data\{JSON_FILE}"


def save_json(data, file_path):
    """
    Save Python object as a formatted JSON file.

    Args:
        data (object): Data to save.
        file_path (str): Target file path.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    st.success(f"Response JSON successfully saved to '{file_path}'.")


def load_json(file_path):
    """
    Load JSON data from a file.

    Args:
        file_path (str): Path to JSON file.

    Returns:
        object: Parsed JSON content.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def display_cards(data):
    """
    Display presentation outline as styled cards in Streamlit.

    Args:
        data (list): List of sections with 'title' and 'content'.
    """
    st.header("Presentation Outline Viewer")
    for section in data:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    background-color: #f9f9f9;
                ">
                <h3 style="margin-bottom: 10px;">{section.get('title', 'No Title')}</h3>
                <ul>
                {''.join(f'<li>{point}</li>' for point in section.get('content', []))}
                </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


def display_slide_images(image_folder):
    """
    Display slide preview images from a folder.

    Args:
        image_folder (str): Folder path containing slide images.
    """
    st.header("Preview Slides (Images)")

    if not os.path.exists(image_folder):
        st.warning(f"Image folder '{image_folder}' not found.")
        return

    image_files = sorted(
        [
            os.path.join(image_folder, f)
            for f in os.listdir(image_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
    )

    if not image_files:
        st.info("No slide images found in the folder.")
        return

    for i, img_path in enumerate(image_files, start=1):
        st.image(img_path, caption=f"Slide {i}", use_column_width=True)


def display_template_choices():
    # Dictionary of templates with image paths and their associated RGB color
    templates = {
        "White": {
            "image": "data\white.jpg",
            "color": (255, 255, 255),
        },
        "Blue": {
            "image": r"data\blue.jpg",
            "color": (1,33,74),
        },
        "Black": {
            "image": r"data\black.jpg",
            "color": (0,0,0),
        },
    }
    # Create columns to display templates side by side
    cols = st.columns(len(templates))
    for i, (name, info) in enumerate(templates.items()):
        with cols[i]:
            # Display template image
            st.image(info["image"], use_container_width=True)
            # Create a button for user to select the template
            if st.button(f"Select {name}"):
                # Save selected template name in session state
                st.session_state.selected_template = name


def main():
    """
    Streamlit app main function:
    - Input prompt to generate presentation outline from AI
    - Display outline cards
    - Generate and download PPTX slides
    """
    st.title("Presentation Outline Editor & Viewer")

    # Initialize session state flags
    if "outline_generated" not in st.session_state:
        st.session_state.outline_generated = False
    if "slides_generated" not in st.session_state:
        st.session_state.slides_generated = False
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = None

    if not st.session_state.outline_generated:
        # Input prompt area and generate outline button
        prompt_input = st.text_area(
            "Enter prompt for AI to create presentation outline:",
            height=100,
        )

        if st.button("Generate Outline"):
            if not prompt_input.strip():
                st.error("Prompt must not be empty.")
            else:
                try:
                    with st.spinner("Contacting AI and generating outline..."):
                        ensure_api_key()
                        llm = init_llm()
                        outline = generate_outline(prompt_input, llm=llm)
                    save_json(outline, JSON_PATH)
                    st.session_state.outline_generated = True
                    st.session_state.slides_generated = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate outline: {e}")

    else:
        # Outline generated: display cards and generate slides button or slides download
        try:
            data = load_json(JSON_PATH)

            if not st.session_state.slides_generated:
                # Display the outline sections as cards
                display_cards(data)

                # Show template selection header
                st.header("Choose Slide Template")
                # Display template images with selection buttons
                display_template_choices()

                # Show the selected template or prompt to select one
                if st.session_state.selected_template:
                    st.write(f"Selected template: **{st.session_state.selected_template}**")
                else:
                    st.write("Please select a template above before generating slides.")

                # Generate Slides button triggers slide creation if a template is selected
                if st.button("Generate Slides"):
                    if st.session_state.selected_template is None:
                        st.warning("Please select a template first.")
                    else:
                        st.session_state.slides_generated = True
                        st.rerun()
            else:
                ## When slides are generated, retrieve selected template's color
                selected = st.session_state.selected_template
                colors = {
                    "White": (255, 255, 255),
                    "Blue": (1,33,74),
                    "Black": (0,0,0),
                }
                selected_color = colors.get(selected, (255, 255, 255))

                font_color = (0,0,0) if selected_color==(255, 255, 255) else (255, 255, 255)

                # Call your slide generation function, passing the chosen color
                generate_slides(slide_content=data, background_color=selected_color, font_color=font_color)

                # Provide download button in Streamlit
                with open("data\presentation.pptx", "rb") as file:
                    pptx_data = file.read()

                st.download_button(
                    label="Download PPTX",
                    data=pptx_data,
                    file_name="presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )

        except Exception as e:
            st.error(f"Failed to load JSON file: {e}")
            # Reset state to allow retry
            st.session_state.outline_generated = False
            st.session_state.slides_generated = False


if __name__ == "__main__":
    main()
