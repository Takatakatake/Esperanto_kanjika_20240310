import streamlit as st
import pandas as pd
import os
from io import BytesIO

# 定数の定義
SAMPLE_CSV = "./files_needed_to_get_replacements_text/20240316世界语词根列表＿包含2个字符的世界语词根＿生成AI_upload用.csv"
SAMPLE_CSV_PATH = os.path.abspath(SAMPLE_CSV)

def download_sample_csv():
    """提供样本CSV文件的下载链接。"""
    if not os.path.exists(SAMPLE_CSV_PATH):
        st.error(f"找不到样本CSV文件: {SAMPLE_CSV_PATH}")
    else:
        with open(SAMPLE_CSV_PATH, "rb") as file:
            st.download_button(
                label="下载样本CSV文件",
                data=file,
                file_name="样本CSV文件.csv",
                mime="text/csv"
            )

def read_csv(input_file):
    """读取CSV文件，去除缺失值并转换为字符串类型。

    Args:
        input_file (str): CSV文件的路径或上传的文件。

    Returns:
        pd.DataFrame: 处理后的数据框。
    """
    try:
        df = pd.read_csv(input_file, encoding='utf-8', header=None)
        df = df.dropna().astype(str)
        return df
    except Exception as e:
        st.error(f"读取CSV文件时发生错误: {e}")
        return None

def process_data(df):
    """处理数据框并生成两个输出文本文件。

    Args:
        df (pd.DataFrame): 处理后的数据框。

    Returns:
        BytesIO, BytesIO: 生成的两个文本文件的缓冲区。
    """
    try:
        # 生成文件1
        text = "{"
        for index, row in df.iterrows():
            if len(row) >= 2:
                word, hanzi = row[0], row[1]
                if (hanzi != '') and (word != '') and ('#' not in word) and ('#' not in hanzi):
                    text += f"'{word} to {hanzi}': {{'prefix': '{word}', 'body': '{hanzi}'}},\n"
        cut_text = text[:-1] + '}'
        cut_text = cut_text.replace("'", '"')
        output1 = BytesIO()
        output1.write(cut_text.encode('utf-8'))
        output1.seek(0)

        # 生成文件2
        es_hanzi_dict = {}
        text2 = ""
        for index, row in df.iterrows():
            if len(row) >= 2:
                word, hanzi = row[0], row[1]
                if (hanzi != '') and (word != '') and ('#' not in word) and ('#' not in hanzi):
                    if hanzi not in es_hanzi_dict:
                        es_hanzi_dict[hanzi] = word
                    else:
                        es_hanzi_dict[hanzi] = es_hanzi_dict[hanzi] + ',' + word
        for i, j in es_hanzi_dict.items():
            jj = j.split(",")
            if len(jj) >= 2:
                text2 += i + ": "
                for kk in jj:
                    text2 += kk + ", "
                text2 += "\n"
        output2 = BytesIO()
        output2.write(text2.encode('utf-8'))
        output2.seek(0)

        return output1, output2
    except Exception as e:
        st.error(f"处理数据时发生错误: {e}")
        return None, None

def main():
    st.title("VS Code代码片段生成工具")
    st.markdown("使用此工具生成将世界语词根转换为汉字的VS Code代码片段。")

    # 提供样本CSV文件的下载链接
    download_sample_csv()

    # 文件上传
    uploaded_file = st.file_uploader("请上传CSV文件", type="csv")

    # 默认文件路径
    input_file = uploaded_file if uploaded_file is not None else SAMPLE_CSV_PATH

    if st.button("开始处理"):
        df = read_csv(input_file)
        if df is not None:
            output1, output2 = process_data(df)
            if output1 and output2:
                st.session_state["output1"] = output1
                st.session_state["output2"] = output2
                st.session_state["generated"] = True
                st.success("处理完成。可以下载输出文件。")

    # 生成文件后显示下载按钮
    if st.session_state.get("generated", False):
        st.download_button(
            label="下载Esperanto_hanziization_snippet_simple.txt",
            data=st.session_state["output1"],
            file_name="Esperanto_hanziization_snippet_simple.txt",
            mime="text/plain"
        )
        st.download_button(
            label="下载same_hanzi_esperanto_roots.txt",
            data=st.session_state["output2"],
            file_name="same_hanzi_esperanto_roots.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
