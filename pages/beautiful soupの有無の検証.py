
import streamlit as st
import pandas as pd
import io
import os
import re
from bs4 import BeautifulSoup, NavigableString
import re

def wrap_text_with_ruby(html_string, chunk_size=10):
    """
    HTML文字列内のHTMLタグに囲まれていないテキストを10文字ごとに<ruby>タグで囲む関数。
    
    :param html_string: 処理対象のHTML文字列
    :param chunk_size: テキストを分割する文字数（デフォルトは10）
    :return: 修正後のHTML文字列
    """
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(html_string, 'html.parser')
    
    def process_element(element):
        for child in list(element.children):
            if isinstance(child, NavigableString):
                text = str(child)
                # テキストが空白や改行のみの場合はスキップ
                if not text.strip():
                    continue
                # テキストをchunk_sizeごとに分割
                chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
                # 分割したチャンクごとに<ruby>タグを作成
                new_tags = []
                for chunk in chunks:
                    ruby_tag = soup.new_tag('ruby')
                    ruby_tag.string = chunk
                    new_tags.append(ruby_tag)
                # 元のテキストノードを新しいタグで置換
                child.replace_with(*new_tags)
            elif child.name.lower() in ['script', 'style']:
                # scriptやstyleタグ内のテキストは処理しない
                continue
            else:
                # 再帰的に子要素を処理
                process_element(child)
    
    # HTMLツリーのルートから処理を開始
    process_element(soup)
    
    # 修正後のHTMLを文字列として返す
    return str(soup)

# サンプルファイルのパス
file_path = './files_needed_to_get_replacements_text/20240316世界语词根列表＿包含2个字符的世界语词根＿生成AI_upload用.csv'
# ファイルを読み込む
with open(file_path, "rb") as file:
    btn = st.download_button(
            label="下载示例CSV文件1(生成AI创建的世界语词根和汉字对应列表)",
            data=file,
            file_name="sample_file.csv",
            mime="text/csv"
        )

file_path2 = './files_needed_to_get_replacements_text/Mingeo_san_hanziization.csv' 
with open(file_path2, "rb") as file:
    btn = st.download_button(
            label="下载示例CSV文件2(中国世界语者杨先生(Mingeo,知乎)创建的世界语词根和汉字对应列表)",
            data=file,
            file_name="sample_file2.csv",
            mime="text/csv"
        )

st.markdown("""如果还有其他人创建了世界语词根和汉字的对应列表,请务必在这里作为示例CSV文件上传!
            其中一个联系方式是<aisacfaraday4@gmail.com>
            (我想如果您也可以直接在github上评论,我们也可以回应)。恳请您的合作。
""")

st.markdown("""他にもエスペラント語根と漢字の対応リストを作成した方がいらっしゃれば、
            是非ここにサンプル(示例CSV文件)としてアップロードさせてください!
            連絡先の一つは、<aisacfaraday4@gmail.com>です
            (他にもgithubから直接コメントしていただいても対応させていただけると思います)。
            ご協力どうぞよろしくお願いいたします。
""")


def conversion_format(hanzi, word, format_type):
    if format_type == 'HTML Format':
        return '<ruby>{}<rt>{}</rt></ruby>'.format(hanzi, word)
    elif format_type == 'Parentheses Format':
        return '{}({})'.format(hanzi, word)
    elif format_type == 'Only Hanzi':
        return '{}'.format(hanzi)

def capitalize_rt_tag(match):
    rt_start, rt_word, rt_end = match.groups()
    return rt_start + rt_word.capitalize() + rt_end
def capitalize_according_to_condition_htmlruby(new_text):
    if new_text.startswith('<ruby>'):
        # <で始まる場合、最初の<rt>タグ内の最初の文字を大文字にする
        new_text = re.sub(r'(<rt>)(.*?)(</rt>)', capitalize_rt_tag, new_text, count=1)
    else:
        # <で始まらない場合、new_textの最初の文字を大文字にする
        new_text = new_text[0].upper() + new_text[1:]
    return new_text
def get_character_width(char):###文字の幅を取得する。全角文字は2、半角文字は1を返す。
    if unicodedata.east_asian_width(char) in 'FWA':
        return 2
    else:
        return 1
import unicodedata
def capitalize_according_to_condition_parentheses(new_text):
    if get_character_width(new_text[0])==2:
        # 漢字で始まる場合、最初の()内の最初の文字を大文字にする
        new_text = re.sub(r'(\()([^()]+)(\))', capitalize_rt_tag, new_text, count=1)
    else:
        # 漢字で始まらない場合、new_textの最初の文字を大文字にする
        new_text = new_text[0].upper() + new_text[1:]
    return new_text    


# ユーザーに出力形式を選んでもらう
format_type = st.selectbox(
    '选择输出格式:',
    ('HTML Format', 'Parentheses Format', 'Only Hanzi')
)

# 例示
hanzi = '汉字'
word = 'hanzi'
formatted_text = conversion_format(hanzi, word, format_type)
st.write('格式化文本:', formatted_text)

# Streamlitでファイルアップロード機能を追加
uploaded_file = st.file_uploader("上传你的CSV文件", type=['csv'])
if uploaded_file is not None:

    # 入力文字列（ユーザー提供の例）
    input_html = """
    <br>
    <ruby>国国<rt class="ruby-XXS_S_S">国<br>国</rt></ruby><ruby>国国国国国国国国国国</ruby>国国国国国国国国国国国国国国国国国国国国<ruby>国国国国国国国国国国</ruby>
    Some plain text that is not within any HTML tags. This text should be wrapped in <ruby> tags every 10 characters.
    """

    # 関数の呼び出し
    output_html = wrap_text_with_ruby(input_html, chunk_size=10)


    download_data = output_html
    if format_type == 'HTML Format':
        st.download_button(
        label="Download replacements_list_html_format.txt",
        data=download_data,
        file_name="replacements_list_html_format.txt",
        mime='text/plain')
    elif format_type == 'Parentheses Format':
        st.download_button(
        label="Download replacements_list_parentheses_format.txt",
        data=download_data,
        file_name="replacements_list_parentheses_format.txt",
        mime='text/plain')
    elif format_type == 'Only Hanzi':
        st.download_button(
        label="Download replacements_list_onlyhanzi_format.txt",
        data=download_data,
        file_name="replacements_list_onlyhanzi_format.txt",
        mime='text/plain')
    
    
