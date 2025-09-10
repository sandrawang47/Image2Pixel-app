import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import io

st.title("🧱 Image to Pixel Art CSV Converter")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "bmp", "tiff", "gif"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_container_width=True)
    orig_width, orig_height = image.size
    st.write(f"Original size: {orig_width} × {orig_height} pixels")

    # Canvas size mode
    size_mode = st.radio("Canvas Size Mode", ["Original Size", "Custom Size"])
    if size_mode == "Original Size":
        width, height = orig_width, orig_height
    else:
        width = st.number_input("Canvas Width", min_value=1, max_value=500, value=32)
        height = st.number_input("Canvas Height", min_value=1, max_value=500, value=32)

    # Color format
    color_format = st.selectbox("Color Format", ["HEX", "RGB", "Excel_Color"])

    # Generate pixel art
    if st.button("Generate Preview"):
        if size_mode == "Original Size":
            processed_image = image.copy()
        else:
            processed_image = image.resize((width, height), Image.NEAREST)

        # Preview (scaled up for small images)
        preview_scale = min(12, max(1, 350 // max(width, height)))
        preview_img = processed_image.resize((width * preview_scale, height * preview_scale), Image.NEAREST)
        st.image(preview_img, caption=f"Pixel Art Preview ({width}×{height})", use_container_width=True)

        # Prepare CSV data
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
