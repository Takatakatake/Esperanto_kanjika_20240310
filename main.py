import streamlit as st
import re
import io
from PIL import Image
import pandas as pd


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



# サンプルファイルのパス
file_path1 = './files_needed_to_get_replacements_text/replacements_list_html_format.txt'

# ファイルを読み込む
with open(file_path1, "rb") as file:
    btn = st.download_button(
            label="下载示例文件1(HTML Format)",
            data=file,
            file_name="replacements_list_html_format.txt",
            mime="text/plain"
        )
    
# サンプルファイルのパス
file_path2 = './files_needed_to_get_replacements_text/replacements_list_parentheses_format.txt'

# ファイルを読み込む
with open(file_path2, "rb") as file:
    btn = st.download_button(
            label="下载示例文件2(Parentheses Format)",
            data=file,
            file_name="replacements_list_parentheses_format.txt",
            mime="text/plain"
        )
    
# サンプルファイルのパス
file_path3 = './files_needed_to_get_replacements_text/replacements_list_onlyhanzi_format.txt'

# ファイルを読み込む
with open(file_path3, "rb") as file:
    btn = st.download_button(
            label="下载示例文件3(Only Hanzi)",
            data=file,
            file_name="replacements_list_onlyhanzi_format.txt",
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
    with open("replacements_list_html_format.txt", 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            j = line.split(',')
            if len(j) == 3:
                old, new, place_holder = j[0], j[1], j[2]
                replacements3.append((old, new, place_holder))

text = ""

with st.form(key='profile_form'):
    letter_type = st.radio('出力文字形式', ('字上符', 'x形式', '^形式'))
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




# # コメント欄の追加
# st.sidebar.title("コメント欄")
# comments = st.sidebar.text_area("ご意見・ご感想をお聞かせください")



# # 操作方法の説明
st.title("操作方法")
st.markdown("""
自作のエスペラント語根-漢字対応表をエスペラント文の漢字変換に用いたい場合、
まず、'make replacement file'に添付されている'下载示例文件'をダウンロード・参照し、
以下の添付画像ような形式のcsvファイルを作成してください。(エスペラント語根はX形式)""")
                               
# エスペラント語根と対応する漢字の例画像を表示
image2 = Image.open('エスペラント語根-漢字対応表(csv形式)の作り方.png')
st.image(image2, caption='エスペラント語根-漢字対応表(csv形式)の作り方', use_column_width=False, width=450)  # 画像にキャプションを追加し、サイズを調整                

st.markdown("""
次に、作成したcsvファイルを'make replacement file'にアップロードし、
'replacements_list_html_format.txt'を作成、ダウンロードします。(このときに、
漢字変換の形式を、'html形式(HTML Format)','括弧形式(Parentheses Format)','漢字のみの形式(Only Hanzi)'
から選択してください。)
csvファイルをアップロードした段階で自動的に'replacements_list_html_format.txt'
の作成が始まります。作成完了まで20秒程かかります。
最後に作成された'replacements_list_html_format.txt'を'main'にアップロードし、
'出力文字形式'を選択、'世界语句子'に漢字変換したいエスペラント文を貼り付け、
'发送' ボタンを押せば、漢字変換されたエスペラント文がプレビューとして
出力され、'下载文本'ボタンを押すと、 漢字変換されたエスペラント文を
テキストファイルとしてダウンロード保存することが出来ます。
(html形式であれば、google chromeなどのウェブブラウザで開くと綺麗にふりがな
(ふりアルファベット)がついているのを見ることが出来ます。)                                                        
""")




# 画像をページの下部に配置
st.markdown("---")  # 水平線を追加して区切りを作成
image = Image.open('エスペラントの漢字化の理想図.png')
st.image(image, caption='世界语汉字化的理想图', use_column_width=False, width=450)  # 画像にキャプションを追加し、サイズを調整

# # 連絡先の追加
st.title("应用程序的github仓库")
st.markdown("https://github.com/Takatakatake/Esperanto_kanjika_20240310/tree/main")