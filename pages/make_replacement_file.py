
import streamlit as st
import pandas as pd
import io
import os
import re


# サンプルファイルのパス
file_path = './files_needed_to_get_replacements_text/20240316世界语词根列表＿包含2个字符的世界语词根.csv'
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
    # Streamlitの環境でファイルを読み込むために必要な変更
    dataframe = pd.read_csv(uploaded_file)
    dataframe.to_csv("./files_needed_to_get_replacements_text/20240316世界语词根列表＿包含2个字符的世界语词根.csv", index=False)


    result = []
    # ファイルを読み込み
    with open("./files_needed_to_get_replacements_text/检查世界语所有单词的结尾是否被正确切除(result).txt", "r", encoding='utf-8') as file:##世界语全部单词_大约44100个(原pejvo.txt)をここまで成形したものから使う。
        for line in file:
            # 改行文字を除去し、カンマで分割
            parts = line.rstrip().split(',')##lstripはしない
            # 分割されたデータが2つの要素を持つことを確認
            if len(parts) >= 2:
                result.append((parts[0], parts[1]))



    ##上の作業で抽出した、'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リストを作成していく。
    ##"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換し終えたリスト"こそが最終的な漢字置換リストの大元になる。
    ##'既に完全に語根分解された状態の単語'が対象であれば、文字数の多い語根順に漢字置換するだけで完璧な精度の漢字置換ができる!
    ##ただし、その完璧な漢字置換のためにはあらかじめ"世界语全部单词_大约44100个(原pejvo.txt).txt"から"从世界语全部单词_大约44100个(原pejvo.txt).txt中提取并输出世界语所有词根_大约11360个.txt_带中文日文注释.ipynb"を用いてエスペラントの全語根を抽出しておく必要がある。

    replacements_dict={}##一旦辞書型を使う。(後で内容(value)を更新するため)
    with open("./files_needed_to_get_replacements_text/世界语所有词根_大约11222个_20240621.txt", 'r', encoding='utf-8') as file:
        ##"世界语所有词根_大约11360个.txt"は"世界语全部单词_大约44100个(原pejvo.txt).txt"から"从世界语全部单词_大约44100个(原pejvo.txt).txt中提取并输出世界语所有词根_大约11360个.txt_带中文日文注释.ipynb"を用いて抽出したエスペラントの全語根である。
        roots = file.readlines()
        for root in roots:
            root = root.strip()
            if not root.isdigit():##混入していた数字の'10'と'7'を削除
                replacements_dict[root]=[root,len(root)]##各エスペラント語根に対する'置換後の単語'(この作業では元の置換対象の語根のまま)と、その置換順序として、'置換対象の語根の文字数'を設定。　置換順序の数字が大きい('置換対象の語根の文字数が多い')ほど、先に置換される仕組みにする。


    ##上の作業に引き続き、"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リスト"を作成していく。　
    ##ここでは自分で作成したエスペラント語根の漢字化リストを反映させる。

    input_file="./files_needed_to_get_replacements_text/20240316世界语词根列表＿包含2个字符的世界语词根.csv"
    # input_file="世界语汉字表格_20240312.csv"
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            j = line.split(',')
            if len(j)==2:
                word,hanzi=j[0],j[1]
                if (hanzi!='') and (word!='') and ('#' not in word):
                    replacements_dict[word]=[conversion_format(hanzi,word,format_type),len(word)]#辞書式配列では要素(key)に対する値(value)を後から更新できることを利用している。

    ##"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リスト"を置換順序の数字の大きさ順にソート。
    pre_replacements=[]
    for old,new in replacements_dict.items():
        pre_replacements.append((old,new[0],new[1]))
    pre_replacements3 = sorted(pre_replacements, key=lambda x: x[2], reverse=True)


    ##"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リスト"の各置換に対して'place holder'を追加し、'replacements'リストとして完成させた。
    ##'place holder'法とは、既に置換を終えた文字列が後続の置換によって重複して置換されてしまうことを避けるために、その置換を終えた部分に一時的に無関係な文字列(place holder)を置いておいて、
    ##全ての置換が終わった後に、改めてその'無関係な文字列(place holder)'から'目的の置換後文字列'に変換していく手法である。

    with open('./files_needed_to_get_replacements_text/No.10000_500000.txt', 'r', encoding='utf-8') as file:##漢字置換時に用いる"place holder"ファイルを予め読み込んでおく。
        loaded_strings = [line.strip() for line in file]

    replacements=[]
    for kk in range(len(pre_replacements3)):
        replacements.append([pre_replacements3[kk][0],pre_replacements3[kk][1],loaded_strings[kk]])


    ##置換に用いる関数。正規表現、C++など様々な形式の置換を試したが、pythonで'place holder'を用いる形式の置換が、最も処理が高速であった。(しかも大変シンプルでわかりやすい。)
    def safe_replace(text, replacements):
        valid_replacements = {}
        # 置換対象(old)を'place holder'に一時的に置換
        for old, new, placeholder in replacements:
            if old in text:
                text = text.replace(old, placeholder)
                valid_replacements[placeholder] = new# 後で置換後の文字列(new)に置換し直す必要がある'place holder'を辞書(valid_replacements)に記録しておく。
        #'place holder'を置換後の文字列(new)に置換)
        for placeholder, new in valid_replacements.items():
            text = text.replace(placeholder, new)
        return text

    # '単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)の要素を全て結合して、一つの文字列にしてから漢字置換を実施すれば
    #高速化できるのではないかと試してみたが、大して速くならなかった。
    # combined = "#%".join([entry[0] for entry in result])
    # (safe_replace(combined, replacements)).split("#%")[:20]  

    ##'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を実際にreplacementsリスト(漢字置換リストの完成版)によって漢字置換。　
    ##ここで作成される、"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換し終えたリスト(辞書型)"(SS)が最終的な漢字置換リストの大元になる。

    SS={}
    for j in result:##20秒ほどかかる。　先にリストの要素を全て結合して、一つの文字列にしてから漢字置換する方法を試しても(上述)、さほど高速化しなかった。
        if len(j)==2:##(j[0]がエスペラント語根、j[1]が品詞。)
            if len(j[0])>=2:##2文字以上のエスペラント語根のみが対象
                if j[0] in SS:
                    if j[1] not in SS[j[0]][1]:
                        SS[j[0]] = [SS[j[0]][0],SS[j[0]][1] + ', ' + j[1]]
                else:
                    SS[j[0]]=[safe_replace(j[0], replacements),j[1]]


    QQ={}
    for i,j in SS.items():##(iが置換対象の単語、j[0]が漢字置換後の単語、j[1]が品詞。)
        if i==j[0]:##漢字化しない単語
            QQ[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000-2500]##漢字化しない単語は優先順位を下げる
        else:
            QQ[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000]


    ### 基本的には動詞に対してのみ活用語尾を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)
    noun_prefix_2l={}
    noun_suffix_2l={}
    adj_prefix_2l={}
    adj_suffix_2l={}
    adv_prefix_2l={}
    adv_suffix_2l={}
    verb_prefix_2l={}
    verb_suffix_2l={'as':'as', 'is':'is', 'os':'os', 'us':'us','at':'at','it':'it','ot':'ot', 'ad':'ad','igx':'igx','ant':'ant','int':'int','ont':'ont'}
    ##接頭辞接尾時の追加については、主に動詞が対象である。

    noun_prefix_2l_2={}
    for d1,d2 in noun_prefix_2l.items():
        noun_prefix_2l_2[d1]=safe_replace(d2, replacements)
    noun_suffix_2l_2={}
    for d1,d2 in noun_suffix_2l.items():
        noun_suffix_2l_2[d1]=safe_replace(d2, replacements)
    adj_prefix_2l_2={}
    for d1,d2 in adj_prefix_2l.items():
        adj_prefix_2l_2[d1]=safe_replace(d2, replacements)
    adj_suffix_2l_2={}
    for d1,d2 in adj_suffix_2l.items():
        adj_suffix_2l_2[d1]=safe_replace(d2, replacements)
    adv_prefix_2l_2={}
    for d1,d2 in adv_prefix_2l.items():
        adv_prefix_2l_2[d1]=safe_replace(d2, replacements)
    adv_suffix_2l_2={}
    for d1,d2 in adv_suffix_2l.items():
        adv_suffix_2l_2[d1]=safe_replace(d2, replacements)
    verb_prefix_2l_2={}
    for d1,d2 in verb_prefix_2l.items():
        verb_prefix_2l_2[d1]=safe_replace(d2, replacements)
    verb_suffix_2l_2={}
    for d1,d2 in verb_suffix_2l.items():
        verb_suffix_2l_2[d1]=safe_replace(d2, replacements)

    ###一番の工夫ポイント(如何にして置換の優先順位を定め、置換精度を向上させるか。)
    ##基本は単語の文字数が多い順に置換していくことになるが、
    ##例えば、"置換対象の単語に接頭辞、接尾辞を追加し、単語の文字数を増やし、置換の優先順位を上げたものを、置換対象の単語として新たに追加する。"などが、置換精度を上げる方策として考えられる。
    ##しかし、いろいろ試した結果、動詞に対してのみ活用語尾を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)のが、ベストに近いことがわかった。

    RR={}
    # 辞書をコピーする
    QQ_copy = QQ.copy()
    for i,j in QQ_copy.items():##j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
        if (j[1] == "名詞") and (len(i)<=6) and not(j[2]==60000 or j[2]==50000 or j[2]==40000 or j[2]==30000 or j[2]==20000):##名詞だけで、6文字以下で、漢字化しないやつ  ##置換ミスを防ぐための条件(20240614) altajo 固有名詞対策  意味ふりがなのときは再検討
            for k1,k2 in noun_prefix_2l.items():
                if not k1+i in QQ_copy:
                    RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]#既存でないものは優先順位を大きく下げる
            for k1,k2 in noun_suffix_2l.items():##"obl","on","op"現在はなし
                if not i+k1 in QQ_copy:
                    RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]#既存でないものは優先順位を大きく下げる
            for k in ["o"]:
                if not i+k in QQ_copy:
                    RR[i+k]=[j[0]+k,j[2]+1*10000-5000]#既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
            QQ.pop(i, None)

    for i,j in QQ.items():##j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
        # if len(i)<=2 and i==j[0]:##2文字以下の語根で漢字化されないものは削除 もしくは2文字以下の語根すべてを削除するのも有りかもしれない。
        if len(i)<=2:##1文字は存在しないはずではある。
            ##基本的に非動詞の2文字の語根単体を以て漢字置換することはない。　ただし、世界语全部单词_大约44100个(原pejvo.txt).txtに最初から含まれている2文字の語根は既に漢字化されており、実際の漢字置換にも反映されることになる。
            ##2文字の語根でも、動詞については活用語尾を追加することで、自動的に+2文字以上できるので追加した。
            if "名詞" in j[1]:
                for k in ["o","on",'oj','ojn']:
                    if not i+k in QQ:
                        RR[' '+i+k+' ']=[' '+j[0]+k+' ',j[2]+len(k)*10000-2000]
            if "形容詞" in j[1]:
                for k in ["a","aj","ajn",'an']:
                    if not i+k in QQ:
                        RR[' '+i+k+' ']=[' '+j[0]+k+' ',j[2]+len(k)*10000-2000]
            if "副詞" in j[1]:
                for k in ["e",'en']:
                    if not i+k in QQ:
                        RR[' '+i+k+' ']=[' '+j[0]+k+' ',j[2]+len(k)*10000-2000]
            if "動詞" in j[1]:
                for k1,k2 in verb_prefix_2l.items():
                    if not k1+i in QQ:
                        RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]
                for k1,k2 in verb_suffix_2l.items():
                    if not i+k1 in QQ:
                        RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]
                for k in ["u ","u!","i "]:##動詞の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                    if not i+k in QQ:
                        RR[i+k]=[j[0]+k,j[2]+2*10000-5000]
            continue

        else:
            RR[i]=[j[0],j[2]]##品詞情報はここで用いるためにあった。以後は不要なので省いていく。
            if "名詞" in j[1] and (len(i)<=6) :##名詞については形容詞、副詞と違い、漢字化しないものにもoをつける。
                for k1,k2 in noun_prefix_2l.items():
                    if not k1+i in QQ:
                        RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]#既存でないものは優先順位を大きく下げる
                for k1,k2 in noun_suffix_2l.items():##"obl","on","op",
                    if not i+k1 in QQ:
                        RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]#既存でないものは優先順位を大きく下げる
                for k in ["o"]:
                    if not i+k in QQ:
                        RR[i+k]=[j[0]+k,j[2]+1*10000-5000]#既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
            if j[2]==50000 or j[2]==40000 or j[2]==30000 or j[2]==20000:##文字数が比較的少なく(<=5)、実際に漢字化するエスペラント語根(文字数×10000)のみを対象とする 
                if "形容詞" in j[1]:
                    for k1,k2 in adj_prefix_2l.items():
                        if not k1+i in QQ:
                            RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]
                    for k1,k2 in adj_suffix_2l.items():
                        if not i+k1 in QQ:
                            RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]
                    for k in ["a"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+1*10000-5000] 
                if "副詞" in j[1]:
                    for k1,k2 in adv_prefix_2l.items():
                        if not k1+i in QQ:
                            RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]
                    for k1,k2 in adv_suffix_2l.items():
                        if not i+k1 in QQ:
                            RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]
                    for k in ["e"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+1*10000-5000]  
                if "動詞" in j[1]:
                    for k1,k2 in verb_prefix_2l.items():
                        if not k1+i in QQ:
                            RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]
                    for k1,k2 in verb_suffix_2l.items():
                        if not i+k1 in QQ:
                            RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]
                    for k in ["u ","u!","i "]:##動詞の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+2*10000-5000]
            # if (j[1] == "名詞") and (len(i)<=6) and not(j[2]==60000 or j[2]==50000 or j[2]==40000 or j[2]==30000 or j[2]==20000):##名詞だけで、6文字以下で、漢字化しないやつ  ##置換ミスを防ぐための条件(20240614) altajo 固有名詞対策  意味ふりがなのときは再検討
            #     RR.pop(i, None)  最初に消すべきと判断
                    
    ##in QQで良かったっけ？ →　辞書ではキーの完全一致が必要なため、部分的な一致では True を得ることはできないので大丈夫。


    ##RRの編集(主に置換の優先順位の変更) ここでも置換の仕方の変更ができないことはないが、品詞の種類に応じて接尾辞や接頭辞を追加するところをスキップすることになってしまう。
    # def conversion_format(hanzi,word):##変換形式を決める。
    #     return '<ruby>{}<rt>{}</rt></ruby>'.format(hanzi,word)

    never_used_as_roots_only=["vin","lin","sin","min"]
    for i in never_used_as_roots_only:
        RR[i]=[i,len(i)*10000+2500]##これらについては数字の大きさはそこまで重要ではない
    # QQ[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000-2500]##漢字化しない単語は優先順位を下げる
    # conversion_format(hanzi,word)





    RR['amas']=['<ruby>爱<rt>am</rt></ruby>as',len('amas')*10000+2500]##漢字化しない語根単体については上記で、うまく処理できているはずだが、amasoは群oと漢字化するので。
    RR['farigx'][1]=len('farigx')*10000+27500##優先順位だけ変更

    x='mondo/n'
    RR[x.replace('/', '')]=[safe_replace(x,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len(x.replace('/', ''))*10000+2500]


    ##以下は完全手作業
    RR['dat/um/i'.replace('/', '')]=[safe_replace('dat/um/i',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('dat/um/i'.replace('/', ''))*10000+2500]
    RR['dat/um/u'.replace('/', '')]=[safe_replace('dat/um/u',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('dat/um/u'.replace('/', ''))*10000+2500]
    RR['dat/um/u!'.replace('/', '')]=[safe_replace('dat/um/u!',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('dat/um/u!'.replace('/', ''))*10000+2500]
    #dat/um/u  dat/um/u!
    RR['tra/met/i'.replace('/', '')]=[safe_replace('tra/met/i',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('tra/met/i'.replace('/', ''))*10000+2500]
    RR['tra/met/u'.replace('/', '')]=[safe_replace('tra/met/u',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('tra/met/u'.replace('/', ''))*10000+2500]
    RR['tra/met/u!'.replace('/', '')]=[safe_replace('tra/met/u!',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('tra/met/u!'.replace('/', ''))*10000+2500]

    # RR['trametu!']=['<ruby>通<rt>tra</rt></ruby><ruby>置<rt>met</rt></ruby>u!',len('trametu!')*10000+2500]

    TT=[]
    for old,new in  RR.items():
        if isinstance(new[1], int):
            TT.append((old,new[0],new[1]))
    # print(len(TT),len(RR))

    pre_replacements3= sorted(TT, key=lambda x: x[2], reverse=True)##(置換順序の数字の大きさ順にソート!)

    ##'エスペラント語根'、'置換漢字'、'place holder'の順に並べ、最終的な置換に用いる"replacements"リストを作成。
    replacements=[]
    for kk in range(len(pre_replacements3)):
        if len(pre_replacements3[kk][0])>1:
            replacements.append([pre_replacements3[kk][0],pre_replacements3[kk][1],loaded_strings[kk]])

    replacements2=[]
    for old,new,place_holder in replacements:
        replacements2.append((old,new,place_holder))
        replacements2.append((old.upper(),new.upper(),place_holder[:-1]+'up$'))##place holderを少し変更する必要があった。
        if old[0]==' ':
            replacements2.append((old[0] + old[1].upper() + old[2:],new[0] + new[1].upper() + new[2:],place_holder[:-1]+'cap$'))##new[0] + new[1].upper() + new[2:]は本当は怪しいが。。  
        else:
            replacements2.append((old.capitalize(),new.capitalize(),place_holder[:-1]+'cap$'))

    #"replacements2"リストの内容を確認
    with open("./files_needed_to_get_replacements_text/replacements_list_anytype.txt", 'w', encoding='utf-8') as file:
        for old,new,place_holder in replacements2:
            file.write(f'{old},{new},{place_holder}\n')
    
    # 最終的な置換リストをファイルとしてダウンロード
    with open("./files_needed_to_get_replacements_text/replacements_list_anytype.txt", 'r', encoding='utf-8') as file:
        download_data = file.read()

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
