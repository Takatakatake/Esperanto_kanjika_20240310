import streamlit as st

st.title("サプーアプリ")
st.caption('これはサプーの動画用のテストアプリです。')

st.subheader('自己紹介')
st.text('webページの作り方')


code = '''
import streamlit as st
'''
st.code(code,language='python')


#画像
from PIL import Image

image = Image.open('ダウンロード.jpeg')
st.image(image, width=200)
##動画も可能

with st.form(key='profile_form'):
    # テキストボックス
    name = st.text_input('名前')
    address = st.text_input('住所')
    # ラジオボタン
    age_category = st.radio('年齢層',('子供','大人'))###select_boxでもいい
    # 複数選択
    hobby = st.multiselect('趣味',('スポーツ','読書','プログラミング','アニメ・映画'))
    
    
    # ボタン
    submit_btn = st.form_submit_button('送信')
    cancel_btn = st.form_submit_button('キャンセル')
    if submit_btn:
        st.text(f'ようこそ{name}さん！{address}に書籍を贈りました')
        st.text(f'年齢層: {age_category}')
        st.text(f'趣味: {", ".join(hobby)}')
    
# print(name)

