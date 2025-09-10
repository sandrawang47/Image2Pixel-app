import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import cv2
from PIL import Image
import csv
import os
import pandas as pd

st.title("🧱 Image to Pixel Art CSV Converter")

class Converter():
    def __init__(self) -> None:
        self.color_dict = {}

    def mosaic(self, img, ratio=0.1):
        small = cv2.resize(img, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
        return cv2.resize(small, img.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)

    def read_csv(self, path):
        with open(path) as f:
            reader = csv.reader(f)
            color = [[int(v) for v in row] for row in reader]
            return color

    def color_change(self, r, g, b, color_pallet):
        if (r, g, b) in self.color_dict:
            return self.color_dict[(r, g, b)]
        # 最も近い色を見つける
        min_distance = float('inf')
        color_name = None
        for color in color_pallet:
            distance = (int(r) - color[0]) ** 2 + (int(g) - color[1]) ** 2 + (int(b) - color[2]) ** 2
            if distance < min_distance:
                min_distance = distance
                color_name = color
        self.color_dict[(r, g, b)] = color_name
        return color_name

    def convert(self, img, option, custom=None):
        w, h = img.shape[:2]
        changed = img.copy()
        # 選択されたcsvファイルを読み込む
        color_pallet = []
        if option != "Custom":
            color_pallet = self.read_csv("./color/"+option+".csv")
        else:
            if custom == [] or custom == None:
                return
            color_pallet = custom

        for height in range(h):
            for width in range(w):
                color = self.color_change(img[width][height][0], img[width][height][1], img[width][height][2], color_pallet)
                changed[width][height][0] = color[0]  # 赤
                changed[width][height][1] = color[1]  # 緑
                changed[width][height][2] = color[2]  # 青
        return changed

    def decreaseColor(self, img):
        dst = img.copy()

        idx = np.where((0 <= img) & (64 > img))
        dst[idx] = 32
        idx = np.where((64 <= img) & (128 > img))
        dst[idx] = 96
        idx = np.where((128 <= img) & (192 > img))
        dst[idx] = 160
        idx = np.where((192 <= img) & (256 > img))
        dst[idx] = 224

        return dst

    def anime_filter(self, img, th1=50, th2=150):
        # アルファチャンネルを分離
        bgr = img[:, :, :3]
        if len(img[0][0]) == 4:
            alpha = img[:, :, 3]

        # グレースケール変換
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        # ぼかしでノイズ低減
        edge = cv2.blur(gray, (3, 3))

        # Cannyアルゴリズムで輪郭抽出
        edge = cv2.Canny(edge, th1, th2, apertureSize=3)

        # 輪郭画像をRGB色空間に変換
        edge = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)

        # 差分を返す
        result = cv2.subtract(bgr, edge)

        # アルファチャンネルを結合して返す
        if len(img[0][0]) == 4:
            return np.dstack([result, alpha])
        else:
            return result

class Web():
    def __init__(self) -> None:
        self.draw_text()

    def draw_text(self):
        st.set_page_config(
            page_title="Pixelart-Converter",
            page_icon="🖼️",
            layout="centered",
            initial_sidebar_state="expanded",
        )
        st.title("PixelArt-Converter")
        self.upload = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png', 'webp'])
        self.color = st.selectbox("Select color palette", ("cold","gold"))
        self.ratio = st.slider('Select ratio', 0.01, 1.0, 0.3, 0.01)
        self.original, self.converted = st.columns(2)
        self.original.title("original img")
        self.converted.title("convert img")
        self.more_options()

    def more_options(self):
        with st.expander("More Options", True):
            self.no_convert = st.checkbox('no color convert')
            self.decrease = st.checkbox('decrease color')
            self.edge_filter = st.checkbox('anime filter')

if __name__ == "__main__":
    web = Web()
    converter = Converter()
    if web.upload != None:
        img = Image.open(web.upload)
        img = np.array(img)
        web.original.image(web.upload)
        img = converter.mosaic(img, web.ratio)
        if web.no_convert == False:
            img = converter.convert(img, web.color)
        if web.decrease:
            img = converter.decreaseColor(img)
        if web.edge_filter:
            img = converter.anime_filter(img)
        web.converted.image(img)
