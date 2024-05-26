import streamlit as st
import re
import io
from PIL import Image




# 置換用の辞書
esperanto_to_x = {
    "ĉ": "cx", "ĝ": "gx", "ĥ": "hx", "ĵ": "jx", "ŝ": "sx", "ŭ": "ux",
    "Ĉ": "Cx", "Ĝ": "Gx", "Ĥ": "Hx", "Ĵ": "Jx", "Ŝ": "Sx", "Ŭ": "Ux",
    "c^": "cx", "g^": "gx", "h^": "hx", "j^": "jx", "s^": "sx", "u^": "ux",
    "C^": "Cx", "G^": "Gx", "H^": "Hx", "J^": "Jx", "S^": "Sx", "U^": "Ux"
}
x_to_jijofu = {'cx': 'ĉ', 'gx': 'ĝ', 'hx': 'ĥ', 'jx': 'ĵ', 'sx': 'ŝ', 'ux': 'ŭ', 'Cx': 'Ĉ',
               'Gx': 'Ĝ', 'Hx': 'Ĥ', 'Jx': 'Ĵ', 'Sx': 'Ŝ', 'Ux': 'Ŭ'}
x_to_hat = {'cx': 'c^', 'gx': 'g^', 'hx': 'h^', 'jx': 'j^', 'sx': 's^', 'ux': 'u^', 'Cx': 'C^',
            'Gx': 'G^', 'Hx': 'H^', 'Jx': 'J^', 'Sx': 'S^', 'Ux': 'U^'}

def replace_esperanto_chars(text, letter_dictionary):
    for esperanto_char, x_char in letter_dictionary.items():
        text = text.replace(esperanto_char, x_char)
    return text

def safe_replace(text, replacements):
    valid_replacements = {}
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements[placeholder] = new
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    return text

st.title("世界语汉字化")
st.caption('这是一个将世界语文本转换成汉字符号的网络应用程序。')



# 画像
image = Image.open('エスペラントの漢字化の理想図.png')
st.image(image)


# サンプルファイルのパス
file_path1 = './files_needed_to_get_replacements_text/replacements2_list_html.txt'

# ファイルを読み込む
with open(file_path1, "rb") as file:
    btn = st.download_button(
            label="サンプルファイル1をダウンロード",
            data=file,
            file_name="replacements2_list_html.txt",
            mime="text/plain"
        )
    
# サンプルファイルのパス
file_path2 = './files_needed_to_get_replacements_text/replacements2_list_parenthesis.txt'

# ファイルを読み込む
with open(file_path2, "rb") as file:
    btn = st.download_button(
            label="サンプルファイル2をダウンロード",
            data=file,
            file_name="replacements2_list_parenthesis.txt",
            mime="text/plain"
        )


uploaded_file = st.file_uploader("Upload your replacements file", type=['txt'])
if uploaded_file is not None:
    replacements3 = []
    for line in uploaded_file:
        decoded_line = line.decode('utf-8').strip()
        parts = decoded_line.split(',')
        if len(parts) == 3:
            replacements3.append((parts[0], parts[1], parts[2]))
else:
    replacements3 = []
    with open("replacements2_list_html.txt", 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            j = line.split(',')
            if len(j) == 3:
                old, new, place_holder = j[0], j[1], j[2]
                replacements3.append((old, new, place_holder))

text = ""

with st.form(key='profile_form'):
    letter_type = st.radio('文字形式', ('字上符', 'x形式', '^形式'))
    sentence = st.text_area('世界语句子')

    submit_btn = st.form_submit_button('发送')
    cancel_btn = st.form_submit_button('取消')
    if submit_btn:
        replaced_text = replace_esperanto_chars(sentence, esperanto_to_x)
        text = safe_replace(replaced_text, replacements3)
        if letter_type == '字上符':
            text = replace_esperanto_chars(text, x_to_jijofu)
        elif letter_type == '^形式':
            text = replace_esperanto_chars(text, x_to_hat)
        st.text_area("转换后的文本预览", text, height=300)

if text:
    to_download = io.BytesIO(text.encode('utf-8'))
    to_download.seek(0)
    st.download_button(
        label="下载文本",
        data=to_download,
        file_name="processed_text.html",
        mime="text/plain"
    )

