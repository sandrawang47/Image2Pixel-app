import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import io
from streamlit.components.v1 import html
st.title("🧱 Image to Pixel Art CSV Converter")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "bmp", "tiff", "gif"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_container_width=True)
    orig_width, orig_height = image.size
    st.write(f"Original size: {orig_width} × {orig_height} pixels")

    
    # Only allow custom pixel size
    st.write("Canvas Size Mode: Custom Pixel Size")
    pixel_size = st.slider("Select pixel size (number of pixels for width)", min_value=4, max_value=min(orig_width, 128), value=32, step=1)
    # Maintain aspect ratio
    aspect_ratio = orig_height / orig_width
    width = pixel_size
    height = max(1, int(pixel_size * aspect_ratio))
    st.write(f"Pixelated size: {width} × {height}")


    color_format = st.selectbox("Color Format", ["HEX", "RGB", "Excel_Color"])

    if st.button("Generate Preview"):
        processed_image = image.copy() if image.resize((width, height), Image.NEAREST) else 
        preview_scale = min(12, max(1, 350 // max(width, height)))
        preview_img = processed_image.resize((width * preview_scale, height * preview_scale), Image.NEAREST)
        st.image(preview_img, caption=f"Pixel Art Preview ({width}×{height})", use_container_width=True)

        img_array = np.array(processed_image)
        data = []
        if color_format == "RGB":
            for y in range(height):
                row = [f"{r},{g},{b}" for r, g, b in img_array[y]]
                data.append(row)
        elif color_format == "HEX":
            for y in range(height):
                row = [f"#{r:02X}{g:02X}{b:02X}" for r, g, b in img_array[y]]
                data.append(row)
        elif color_format == "Excel_Color":
            def rgb_to_excel_color(r, g, b):
                return b << 16 | g << 8 | r
            for y in range(height):
                row = [str(rgb_to_excel_color(r, g, b)) for r, g, b in img_array[y]]
                data.append(row)

        df = pd.DataFrame(data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, header=False)
        csv_bytes = csv_buffer.getvalue().encode()

        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=f"pixelart_{width}x{height}_{color_format.lower()}.csv",
            mime="text/csv"
        )

button = """
<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="wang47" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
"""

html(button, height=70, width=220)

st.markdown(
    """
    <style>
        iframe[width="220"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
