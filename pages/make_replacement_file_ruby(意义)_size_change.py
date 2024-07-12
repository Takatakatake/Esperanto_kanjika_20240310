
import streamlit as st
import pandas as pd
import io
import os
import re


# サンプルファイルのパス
file_path1 = './files_needed_to_get_replacements_text/Ruby格式＿中文.csv'
# ファイルを読み込む
with open(file_path1, "rb") as file:
    btn = st.download_button(
            label="下载示例CSV文件1(Ruby格式＿中文)",
            data=file,
            file_name="sample_file_ruby_中文.csv",
            mime="text/csv"
        )
# サンプルファイルのパス
file_path2 = './files_needed_to_get_replacements_text/Ruby形式＿日本語.csv'
# ファイルを読み込む
with open(file_path2, "rb") as file:
    btn = st.download_button(
            label="下载示例CSV文件2(Ruby形式＿日本語)",
            data=file,
            file_name="sample_file_ruby_日本語.csv",
            mime="text/csv"
        )

def capitalize_rt_tag(match):
    rt_start, rt_word, rt_end = match.groups()
    return rt_start + rt_word.capitalize() + rt_end
def capitalize_according_to_condition_htmlruby(new_text):
    if new_text.startswith('<ruby>'):
        # <で始まる場合、最初の<rt>タグ内の最初の文字を大文字にする
        new_text = re.sub(r'(<ruby>)(.*?)(<rt)', capitalize_rt_tag, new_text, count=1)
    else:
        # <で始まらない場合、new_textの最初の文字を大文字にする
        new_text = new_text[0].upper() + new_text[1:]
    
    return new_text

# file_path2 = './files_needed_to_get_replacements_text/Mingeo_san_hanziization.csv' 
# with open(file_path2, "rb") as file:
#     btn = st.download_button(
#             label="下载示例CSV文件2(中国世界语者杨先生(Mingeo,知乎)创建的世界语词根和汉字对应列表)",
#             data=file,
#             file_name="sample_file2.csv",
#             mime="text/csv"
#         )
import unicodedata

def get_character_width(char):
    """
    文字の幅を取得する。
    全角文字は2、半角文字は1を返す。
    """
    if unicodedata.east_asian_width(char) in 'FWA':
        return 2
    else:
        return 1

def get_string_width(s):
    """
    文字列の全体幅を取得する。
    全角文字は2、半角文字は1として計算する。
    """
    return sum(get_character_width(char) for char in s)

# # テスト用文字列
# test_string = "半角abc全角あいう123"

# # 文字列の幅を計算
# width = get_string_width(test_string)

# print(f"文字列の幅: {width}")


def conversion_format(hanzi, word, format_type):
    if format_type == 'HTML Format':
        if get_string_width(word)/get_string_width(hanzi)<(9/25):
            return '<ruby>{}<rt class="ruby-S_S_S">{}</rt></ruby>'.format(word, hanzi)
        elif  get_string_width(word)/get_string_width(hanzi)<(21/40):
            return '<ruby>{}<rt class="ruby-M_M_M">{}</rt></ruby>'.format(word, hanzi)
        elif  get_string_width(word)/get_string_width(hanzi)<(7/8):
            return '<ruby>{}<rt class="ruby-L_L_L">{}</rt></ruby>'.format(word, hanzi)
        else:
            return '<ruby>{}<rt class="ruby-X_X_X">{}</rt></ruby>'.format(word, hanzi)
    elif format_type == 'Parentheses Format':
        return '{}({})'.format(word, hanzi)

# ユーザーに出力形式を選んでもらう
format_type = st.selectbox(
    '选择输出格式:',
    ('HTML Format', 'Parentheses Format')
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
    dataframe.to_csv("./files_needed_to_get_replacements_text/世界语词根列表＿user.csv", index=False)


    result = []
    # ファイルを読み込み
    with open("./files_needed_to_get_replacements_text/检查世界语所有单词的结尾是否被正确切除(result).txt", "r", encoding='utf-8') as file:##世界语全部单词_大约44100个(原pejvo.txt)をここまで成形したものから使う。
        for line in file:
            # 改行文字を除去し、カンマで分割
            parts = line.strip().split(',')
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

    input_file="./files_needed_to_get_replacements_text/世界语词根列表＿user.csv"
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
    keys_to_remove = ['domen', 'teren','post/e/n']
    for key in keys_to_remove:
        SS.pop(key, None)  # 'None' はキーが存在しない場合に返すデフォルト
    
    QQ={}
    for i,j in SS.items():##(iが置換対象の単語、j[0]が漢字置換後の単語、j[1]が品詞。)
        if i==j[0]:##漢字化しない単語
            QQ[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000-3000]##漢字化しない単語は優先順位を下げる
        else:
            QQ[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000]
            # '<ruby>{}<rt class="ruby-m_M_m">{}</rt></ruby>'.format(word, hanzi)
    
    ### 基本的には動詞に対してのみ活用語尾を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)

    verb_suffix_2l={'as':'as', 'is':'is', 'os':'os', 'us':'us','at':'at','it':'it','ot':'ot', 'ad':'ad','igx':'igx','ig':'ig','ant':'ant','int':'int','ont':'ont'}
    ##接頭辞接尾時の追加については、主に動詞が対象である。
    verb_suffix_2l_2={}
    for d1,d2 in verb_suffix_2l.items():
        verb_suffix_2l_2[d1]=safe_replace(d2, replacements)

    ###一番の工夫ポイント(如何にして置換の優先順位を定め、置換精度を向上させるか。)
    ##基本は単語の文字数が多い順に置換していくことになるが、
    ##例えば、"置換対象の単語に接頭辞、接尾辞を追加し、単語の文字数を増やし、置換の優先順位を上げたものを、置換対象の単語として新たに追加する。"などが、置換精度を上げる方策として考えられる。
    ##しかし、いろいろ試した結果、動詞に対してのみ活用語尾を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)のが、ベストに近いことがわかった。

    ### RR内での重複の検査
    RR={}
    # 辞書をコピーする
    QQ_copy = QQ.copy()##これがあるので、2回繰り返しするときは数個前のセルに戻ってQQを作り直してからでないといけない。
    for i,j in QQ_copy.items():##j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
        if (j[1] == "名詞") and (len(i)<=6) and not(j[2]==60000 or j[2]==50000 or j[2]==40000 or j[2]==30000 or j[2]==20000):##名詞だけで、6文字以下で、漢字化しないやつ  ##置換ミスを防ぐための条件(20240614) altajo,aviso,malm,abes 固有名詞対策  意味ふりがなのときは再検討
            for k in ["o"]:##4 ['buro', 'haloo', 'tauxro', 'unesko']
                if not i+k in QQ_copy:##if not ありのままで良い。
                    RR[i+k]=[j[0]+k,j[2]+len(k)*10000-2000]#実質5000 #既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
            QQ.pop(i, None)

    for i,j in QQ.items():##j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
        if j[2]==20000:##2文字で漢字化するやつ##len(i)<=2:#1文字は存在しないはずではある。
            ##基本的に非動詞の2文字の語根単体を以て漢字置換することはない。　ただし、世界语全部单词_大约44100个(原pejvo.txt).txtに最初から含まれている2文字の語根は既に漢字化されており、実際の漢字置換にも反映されることになる。
            ##2文字の語根でも、動詞については活用語尾を追加することで、自動的に+2文字以上できるので追加した。
            if "名詞" in j[1]:
                for k in ["o","on",'oj']:##"ojn"は不要か
                    if not i+k in QQ:
                        RR[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
            if "形容詞" in j[1]:
                for k in ["a","aj",'an']:##"ajn"は不要か  ##sia pian ,'an 'も不要
                    # if not i+k in QQ:##if not なしのほうが良い
                    RR[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
            if "副詞" in j[1]:
                for k in ["e"]:##ege   エーゲ海を意味するegeoを元の辞書に追加
                    # if not i+k in QQ:##if not なしのほうが良い
                    RR[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
            if "動詞" in j[1]:
                for k1,k2 in verb_suffix_2l_2.items():
                    if not i+k1 in QQ:
                        RR[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]
                for k in ["u ","i ","u","i"]:##動詞の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                    if not i+k in QQ:
                        RR[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]

        else:
            RR[i]=[j[0],j[2]]##品詞情報はここで用いるためにあった。以後は不要なので省いていく。
            if j[2]==60000 or j[2]==50000 or j[2]==40000 or j[2]==30000:##文字数が比較的少なく(<=5)、実際に漢字化するエスペラント語根(文字数×10000)のみを対象とする 
                if "名詞" in j[1]:##名詞については形容詞、副詞と違い、漢字化しないものにもoをつける。
                    for k in ["o","on",'oj']:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]#既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
                if "形容詞" in j[1]:
                    for k in ["a","aj",'an']:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                if "副詞" in j[1]:
                    for k in ["e"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                if "動詞" in j[1]:
                    for k1,k2 in verb_suffix_2l_2.items():
                        if not i+k1 in QQ:
                            RR[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]
                    for k in ["u ","i ","u","i"]:##動詞の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]          
            elif len(i)>=3 and len(i)<=6:##3文字から6文字の語根で漢字化しないもの　　結局2文字の語根で漢字化しないものについては、完全に除外している。
                if "名詞" in j[1]:##名詞については形容詞、副詞と違い、漢字化しないものにもoをつける。
                    for k in ["o"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]#実質3000#既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
                if "形容詞" in j[1]:
                    for k in ["a"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]
                if "副詞" in j[1]:
                    for k in ["e"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]

    AN=[['dietan', '/diet/an/', '/diet/an'], ['afrikan', '/afrik/an/', '/afrik/an'], ['movadan', '/mov/ad/an/', '/mov/ad/an'], ['akcian', '/akci/an/', '/akci/an'], ['montaran', '/mont/ar/an/', '/mont/ar/an'], ['amerikan', '/amerik/an/', '/amerik/an'], ['regnan', '/regn/an/', '/regn/an'], ['dezertan', '/dezert/an/', '/dezert/an'], ['asocian', '/asoci/an/', '/asoci/an'], ['insulan', '/insul/an/', '/insul/an'], ['azian', '/azi/an/', '/azi/an'], ['sxtatan', '/sxtat/an/', '/sxtat/an'], ['doman', '/dom/an/', '/dom/an'], ['montan', '/mont/an/', '/mont/an'], ['familian', '/famili/an/', '/famili/an'], ['urban', '/urb/an/', '/urb/an'], ['popolan', '/popol/an/', '/popol/an'], ['dekan', '/dekan/', '/dek/an'], ['partian', '/parti/an/', '/parti/an'], ['lokan', '/lok/an/', '/lok/an'], ['sxipan', '/sxip/an/', '/sxip/an'], ['eklezian', '/eklezi/an/', '/eklezi/an'], ['landan', '/land/an/', '/land/an'], ['orientan', '/orient/an/', '/orient/an'], ['lernejan', '/lern/ej/an/', '/lern/ej/an'], ['enlandan', '/en/land/an/', '/en/land/an'], ['kalkan', '/kalkan/', '/kalk/an'], ['estraran', '/estr/ar/an/', '/estr/ar/an'], ['etnan', '/etn/an/', '/etn/an'], ['euxropan', '/euxrop/an/', '/euxrop/an'], ['fazan', '/fazan/', '/faz/an'], ['polican', '/polic/an/', '/polic/an'], ['socian', '/soci/an/', '/soci/an'], ['societan', '/societ/an/', '/societ/an'], ['grupan', '/grup/an/', '/grup/an'], ['ligan', '/lig/an/', '/lig/an'], ['nacian', '/naci/an/', '/naci/an'], ['koran', '/koran/', '/kor/an'], ['religian', '/religi/an/', '/religi/an'], ['kuban', '/kub/an/', '/kub/an'], ['majoran', '/major/an/', '/major/an'], ['marian', 'marian', '/mari/an'], ['nordan', '/nord/an/', '/nord/an'], ['paran', 'paran', '/par/an'], ['parizan', '/pariz/an/', '/pariz/an'], ['parokan', '/parok/an/', '/parok/an'], ['podian', '/podi/an/', '/podi/an'], ['rusian', '/rus/i/an/', '/rus/ian'], ['satan', '/satan/', '/sat/an'], ['sektan', '/sekt/an/', '/sekt/an'], ['senatan', '/senat/an/', '/senat/an'], ['skisman', '/skism/an/', '/skism/an'], ['sudan', 'sudan', '/sud/an'], ['utopian', '/utopi/an/', '/utopi/an'], ['vilagxan', '/vilagx/an/', '/vilagx/an']]
    ON=[['duon', '/du/on/', '/du/on'], ['okon', '/ok/on/', '/ok/on'], ['nombron', '/nombr/on/', '/nombr/on'], ['patron', '/patron/', '/patr/on'], ['karbon', '/karbon/', '/karb/on'], ['ciklon', '/ciklon/', '/cikl/on'], ['aldon', '/al/don/', '/ald/on'], ['balon', '/balon/', '/bal/on'], ['baron', '/baron/', '/bar/on'], ['baston', '/baston/', '/bast/on'], ['magneton', '/magnet/on/', '/magnet/on'], ['beton', 'beton', '/bet/on'], ['bombon', '/bombon/', '/bomb/on'], ['breton', 'breton', '/bret/on'], ['burgxon', '/burgxon/', '/burgx/on'], ['centon', '/cent/on/', '/cent/on'], ['milon', '/mil/on/', '/mil/on'], ['kanton', '/kanton/', '/kant/on'], ['citron', '/citron/', '/citr/on'], ['platon', 'platon', '/plat/on'], ['dekon', '/dek/on/', '/dek/on'], ['kvaron', '/kvar/on/', '/kvar/on'], ['kvinon', '/kvin/on/', '/kvin/on'], ['seson', '/ses/on/', '/ses/on'], ['trion', '/tri/on/', '/tri/on'], ['karton', '/karton/', '/kart/on'], ['foton', '/fot/on/', '/fot/on'], ['peron', '/peron/', '/per/on'], ['elektron', '/elektr/on/', '/elektr/on'], ['drakon', 'drakon', '/drak/on'], ['mondon', '/mon/don/', '/mond/on'], ['pension', '/pension/', '/pensi/on'], ['ordon', '/ordon/', '/ord/on'], ['eskadron', 'eskadron', '/eskadr/on'], ['senton', '/sen/ton/', '/sent/on'], ['eston', 'eston', '/est/on'], ['fanfaron', '/fanfaron/', '/fanfar/on'], ['feston', '/feston/', '/fest/on'], ['flegmon', 'flegmon', '/flegm/on'], ['fronton', '/fronton/', '/front/on'], ['galon', '/galon/', '/gal/on'], ['mason', '/mason/', '/mas/on'], ['helikon', 'helikon', '/helik/on'], ['kanon', '/kanon/', '/kan/on'], ['kapon', '/kapon/', '/kap/on'], ['kokon', '/kokon/', '/kok/on'], ['kolon', '/kolon/', '/kol/on'], ['komision', '/komision/', '/komisi/on'], ['salon', '/salon/', '/sal/on'], ['ponton', '/ponton/', '/pont/on'], ['koton', '/koton/', '/kot/on'], ['kripton', 'kripton', '/kript/on'], ['kupon', '/kupon/', '/kup/on'], ['lakon', 'lakon', '/lak/on'], ['ludon', '/lu/don/', '/lud/on'], ['melon', '/melon/', '/mel/on'], ['menton', '/menton/', '/ment/on'], ['milion', '/milion/', '/mili/on'], ['milionon', '/milion/on/', '/milion/on'], ['nauxon', '/naux/on/', '/naux/on'], ['violon', '/violon/', '/viol/on'], ['trombon', '/trombon/', '/tromb/on'], ['senson', '/sen/son/', '/sens/on'], ['sepon', '/sep/on/', '/sep/on'], ['skadron', 'skadron', '/skadr/on'], ['stadion', '/stadion/', '/stadi/on'], ['tetraon', 'tetraon', '/tetra/on'], ['timon', '/timon/', '/tim/on'], ['valon', 'valon', '/val/on']]
    AT=[['agat', '/agat/', '/ag/at/'], ['sonat', '/sonat/', '/son/at/'], ['format', '/format/', '/form/at/'], ['kantat', '/kantat/', '/kant/at/'], ['diplomat', '/diplomat/', '/diplom/at/'], ['salat', '/salat/', '/sal/at/'], ['legat', '/legat/', '/leg/at/'], ['predikat', '/predikat/', '/predik/at/'], ['rabat', '/rabat/', '/rab/at/'], ['sendat', '/sen/dat/', '/send/at/'], ['traktat', '/traktat/', '/trakt/at/']]
    IT=[['agit', '/agit/', '/ag/it/'], ['irit', 'irit', '/ir/it/'], ['gravit', 'gravit', '/grav/it/'], ['spirit', '/spirit/', '/spir/it/'], ['trilit', '/tri/lit/', '/tril/it/'], ['vizit', '/vizit/', '/viz/it/']]
    SONOTA=[['alo', '/alo/', '/al/o'], ['alte', '/alte/', '/alt/e'], ['apoge', '/apoge/', '/apog/e'], ['kaze', '/kaze/', '/kaz/e'], ['inka', 'inka', '/ink/a'], ['pere', '/pere/', '/per/e'], ['fero', 'fero', '/fer/o'], ['havaj', 'havaj', '/hav/aj'], ['kore', 'kore', '/kor/e'], ['lama', '/lama/', '/lam/a'], ['malaj', 'malaj', '/mal/aj'], ['male', 'male', '/mal/e'], ['refoj', '/re/foj/', '/ref/oj'], ['samo', 'samo', '/sam/o'], ['savoj', 'savoj', '/sav/oj'], ['sole', '/sole/', '/sol/e'], ['veto', 'veto', '/vet/o'], ['amas', '/amas/', '/am/as/'], ['iris', '/iris/', '/ir/is/'], ['regulus', 'regulus', '/regul/us/'], ['agxi', '/agxi/', '/agx/i'], ['akirant', 'akirant', '/akir/ant/'], ['radius', 'radius', '/radi/us/'], ['premis', '/premis/', '/prem/is/'], ['premi', '/premi/', '/prem/i'], ['bari', 'bari', '/bar/i'], ['markot', '/markot/', '/mark/ot/'], ['tempi', '/tempi/', '/temp/i'], ['noktu', '/noktu/', '/nokt/u'], ['vakcini', 'vakcini', '/vakcin/i'], ['nomad', '/nomad/', '/nom/ad/'], ['procesi', '/procesi/', '/proces/i'], ['statu', '/statu/', '/stat/u'], ['kolorad', 'kolorad', '/kolor/ad/'], ['devi', 'devi', '/dev/i'], ['diskont', '/diskont/', '/disk/ont/'], ['endos', 'endos', '/end/os/'], ['esperant', '/esperant/', '/esper/ant/'], ['feri', '/feri/', '/fer/i'], ['fleksi', '/fleksi/', '/fleks/i'], ['forkant', '/for/kant/', '/fork/ant/'], ['pensi', '/pensi/', '/pens/i'], ['konus', '/konus/', '/kon/us/'], ['jesu', '/jesu/', '/jes/u'], ['jxaluzi', 'jxaluzi', '/jxaluz/i'], ['konfesi', 'konfesi', '/konfes/i'], ['konsili', 'konsili', '/konsil/i'], ['legi', '/legi/', '/leg/i'], ['lekant', '/lekant/', '/lek/ant/'], ['licenci', 'licenci', '/licenc/i'], ['logxi', '/logxi/', '/logx/i'], ['lotus', '/lotus/', '/lot/us/'], ['malvolont', '/mal/volont/', '/mal/vol/ont/'], ['mankis', '/man/kis/', '/mank/is/'], ['meti', '/meti/', '/met/i'], ['minus', '/minus/', '/min/us/'], ['pasi', '/pasi/', '/pas/i'], ['patos', '/patos/', '/pat/os/'], ['revu', '/revu/', '/rev/u'], ['rabot', '/rabot/', '/rab/ot/'], ['rabi', '/rabi/', '/rab/i'], ['religi', '/religi/', '/re/lig/i'], ['remont', 'remont', '/rem/ont/'], ['sagu', '/sagu/', '/sag/u'], ['satirus', 'satirus', '/satir/us/'], ['sekci', '/sekci/', '/sekc/i'], ['sendot', '/sen/dot/', '/send/ot/'], ['sendi', '/sen/di/', '/send/i'], ['spirant', 'spirant', '/spir/ant/'], ['taksus', '/taksus/', '/taks/us/'], ['tenis', 'tenis', '/ten/is/'], ['teni', '/teni/', '/ten/i'], ['trikot', '/trikot/', '/trik/ot/'], ['vaku', 'vaku', '/vak/u'], ['vizi', '/vizi/', '/viz/i'], ['volont', '/volont/', '/vol/ont/']]
    # print(len(AN),len(ON),len(AT),len(IT),len(SONOTA))

    for an in AN:
        if an[1].endswith("/an/"):
            i2=an[1]
            i3 = re.sub(r"/an/$", "", i2)##正規表現を使わない,
            i4=i3+"/an/o"
            i5=i3+"/an/a"
            i6=i3+"/an/e"
            i7=i3+"/a/n/"
            RR[i4.replace('/', '')]=[safe_replace(i4,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
            RR[i5.replace('/', '')]=[safe_replace(i5,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
            RR[i6.replace('/', '')]=[safe_replace(i6,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
            RR[i7.replace('/', '')]=[safe_replace(i7,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]
        else:
            i2=an[1]
            i2_2 = re.sub(r"an$", "", i2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i3 = re.sub(r"an/$", "", i2_2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i4=i3+"an/o"
            i5=i3+"an/a"
            i6=i3+"an/e"
            i7=i3+"/a/n/"
            RR[i4.replace('/', '')]=[safe_replace(i4,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
            RR[i5.replace('/', '')]=[safe_replace(i5,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
            RR[i6.replace('/', '')]=[safe_replace(i6,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
            RR[i7.replace('/', '')]=[safe_replace(i7,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]

    for on in ON:
        if on[1].endswith("/on/"):
            i2=on[1]
            i3 = re.sub(r"/on/$", "", i2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i4=i3+"/on/o"
            i5=i3+"/on/a"
            i6=i3+"/on/e"
            i7=i3+"/o/n/"
            RR[i4.replace('/', '')]=[safe_replace(i4,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
            RR[i5.replace('/', '')]=[safe_replace(i5,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
            RR[i6.replace('/', '')]=[safe_replace(i6,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
            RR[i7.replace('/', '')]=[safe_replace(i7,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]
        else:
            i2=on[1]
            i2_2 = re.sub(r"on$", "", i2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i3 = re.sub(r"on/$", "", i2_2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i4=i3+"on/o"
            i5=i3+"on/a"
            i6=i3+"on/e"
            i7=i3+"/o/n/"
            RR[i4.replace('/', '')]=[safe_replace(i4,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
            RR[i5.replace('/', '')]=[safe_replace(i5,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
            RR[i6.replace('/', '')]=[safe_replace(i6,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
            RR[i7.replace('/', '')]=[safe_replace(i7,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]

    ##RRの編集(主に置換の優先順位の変更) ここでも置換の仕方の変更ができないことはないが、品詞の種類に応じて接尾辞や接頭辞を追加するところをスキップすることになってしまう。
    never_used_as_roots_only=["vin","lin","sin","min","gxin"]
    for i in never_used_as_roots_only:
        RR[i]=[i,len(i)*10000+3000]##これらについては数字の大きさはそこまで重要ではない
    # QQ[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000-3000]##漢字化しない単語は優先順位を下げる
    # conversion_format(hanzi, word, format_type)

    # RR['amas']=['<ruby>爱<rt>am</rt></ruby>as',len('amas')*10000+2500]##漢字化しない語根単体については上記で、うまく処理できているはずだが、amasoは群oと漢字化するので。
    RR['farigx'][1]=len('farigx')*10000+27500##優先順位だけ変更

    x='mond/o/n'
    RR[x.replace('/', '')]=[safe_replace(x,replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  (len(x.replace('/', ''))-1)*10000+3000]

    ##正しく語根分解・漢字変換してほしいやつ  anとenは念の為a/n/,e/n/としておく。ant,int,ontは大丈夫  空白を使うのは最終手段。  ","は絶対に使っては駄目
    y1=[['gvid/ant/o',73000],['am/as',33000],["ink/a",33000],["post/e/n",53000],["per/e",33000],["fer/o",33000],["kor/e",33000],["mal/a/j",43000],["mal/e",33000],
        ['sam/o',33000],['sav/oj',43000],['vet/o',33000],['ir/is',33000],['regul/us',63000],['akir/ant',63000],["prem/is",53000],
        ["mark/ot",53000],["kolor/ad",63000],["lot/us",43000],["mank/is",53000],["pat/os",43000],["rem/ont",53000],["satir/us",63000],["send/at",53000],["send/ot",53000],
        ["spir/ant",63000],["ten/is",43000],["trakt/at",63000],["alt/e",33000],["apog/e",43000],["dom/e/n",43000],["kaz/e/ ",43000],
        ["post/e/n",53000],["posten/ul",73000],["hav/a/j",43000],["sol/e",33000],["lam/a",33000],
        ["ref/oj",43000],["akir/ant",63000],["ordin/at",63000],["form/at",53000],["kant/at",53000],["end/os",43000],
        ["kon/us ",53000],["lek/ant",53000],["leg/at",43000],["taks/us",53000],["pi/a/n",38000]]##["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj "pi/a/n"だけ8000に
    for i in y1:
        RR[i[0].replace('/', '')]=[safe_replace(i[0],replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]]

    ##正しく語根分解・漢字変換してほしいやつ  anとenは念の為a/n/,e/n/としておく。ant,int,ontは大丈夫  空白を使うのは最終手段。  ","は絶対に使っては駄目
    y1=[['sole/o',43000],['sole/a',43000]]##["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj
    for i in y1:
        RR[i[0].replace('/', '')]=[safe_replace(i[0],replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]]

    ##on系の調節(an系は現時点で調節必要なし) 空白を使うのは最終手段。  ","は絶対に使っては駄目   "duon","okon"だけ8000に
    y1=[['du/on',38000],['tri/on',43000],["kvar/on",53000],["kvin/on",53000],["ses/on",43000],["baston",53000],["bast/o/n ",63000],["beton",43000],["bet/o/n ",53000],["burgxon",63000],["burgx/o/n ",73000],
        ["sep/on",43000],["ok/on",38000],["naux/on",53000],["dek/on",43000],["al/don",43000],["ald/o/n ",53000],["cent/on",53000],["mil/on",43000],["citron",53000],["citr/o/n ",63000],["elektr/on",73000],["elektr/o/n ",83000],
        ["sent/o/n",53000],["fanfaron",73000],["fanfar/o/n ",83000],["kanon",43000],["kan/o/n ",53000],["milion/on",73000],["milion",53000],["menton",53000],["ment/o/n ",53000],["melon",43000],
        ["mel/o/n ",53000],["lud/o/n",43000],["kupon",43000],["kup/o/n ",53000],["sens/o/n",53000]]##["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj
    for i in y1:
        RR[i[0].replace('/', '')]=[safe_replace(i[0],replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]]
        
    ##/o,/a,/eの追加
    y1=[['domen',43000],['teren',43000],["posten",53000],["apoge",43000],["tenis",43000],["re/foj",43000],["sen/dot",53000],["sen/dat",53000],
        ['patos',43000],['markot',43000],["premis",53000],["veto",43000],["savoj",43000],["kore",43000]]##["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj
    for i in y1:
        RR[(i[0]+'/a').replace('/', '')]=[safe_replace((i[0]+'/a'),replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]
        RR[(i[0]+'/e').replace('/', '')]=[safe_replace((i[0]+'/e'),replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]
        RR[(i[0]+'/o').replace('/', '')]=[safe_replace((i[0]+'/o'),replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]

    ##/o,/aの追加
    y1=[['sole',33000],['pian',38000],["taksus",53000],["legat",43000],["lekant",53000],["endos",43000],["endos",43000],
        ['kantat',53000],['ordinat',63000],["akirant",63000],["lama",33000],["kaze",33000],["alte",33000],["traktat",63000],
        ['spirant',63000],['satirus',63000],["remont",53000],["man/kis",33000],["kolorad",63000],["regulus",63000],["male",33000],
        ['pere',33000]]##["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj
    for i in y1:
        RR[(i[0]+'/a').replace('/', '')]=[safe_replace((i[0]+'/a'),replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]
        RR[(i[0]+'/o').replace('/', '')]=[safe_replace((i[0]+'/o'),replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]

    ##漢字変換してほしくないやつ
    y2=[['lian',43000]]
    for j in y2:
        RR[j[0].replace('/', '')]=[conversion_format(j[0],j[0], format_type), j[1]]
    ##以下は完全手作業
    RR['dat/um/i'.replace('/', '')]=[safe_replace('dat/um/i',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('dat/um/i'.replace('/', ''))*10000+3000]
    RR['dat/um/u'.replace('/', '')]=[safe_replace('dat/um/u',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('dat/um/u'.replace('/', ''))*10000+3000]
    #dat/um/u  dat/um/u!
    RR['tra/met/i'.replace('/', '')]=[safe_replace('tra/met/i',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('tra/met/i'.replace('/', ''))*10000+3000]
    RR['tra/met/u'.replace('/', '')]=[safe_replace('tra/met/u',replacements).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('tra/met/u'.replace('/', ''))*10000+3000]


    TT=[]
    for old,new in  RR.items():
        TT.append((old,new[0],new[1]))

    pre_replacements3= sorted(TT, key=lambda x: x[2], reverse=True)##(置換順序の数字の大きさ順にソート!)

    ##'エスペラント語根'、'置換漢字'、'place holder'の順に並べ、最終的な置換に用いる"replacements"リストを作成。
    replacements_l=[]
    for kk in range(len(pre_replacements3)):
        if len(pre_replacements3[kk][0])>1:
            replacements_l.append([pre_replacements3[kk][0],pre_replacements3[kk][1],loaded_strings[kk]])

    replacements2=[]
    if format_type == 'HTML Format':
        for old,new,place_holder in replacements_l:
            replacements2.append((old,new,place_holder))
            replacements2.append((old.upper(),new.upper(),place_holder[:-1]+'up$'))##place holderを少し変更する必要があった。
            if old[0]==' ':
                replacements2.append((old[0] + old[1].upper() + old[2:],new[0] + capitalize_according_to_condition_htmlruby(new[1:]),place_holder[:-1]+'cap$'))##new[0] + new[1].upper() + new[2:]は本当は怪しいが。。  
            else:
                replacements2.append((old.capitalize(),capitalize_according_to_condition_htmlruby(new),place_holder[:-1]+'cap$'))
    else:
        for old,new,place_holder in replacements_l:
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
        label="Download replacements_list_ruby_html_format.txt",
        data=download_data,
        file_name="replacements_list_ruby_html_format.txt",
        mime='text/plain')
    elif format_type == 'Parentheses Format':
        st.download_button(
        label="Download replacements_list_ruby_parentheses_format.txt",
        data=download_data,
        file_name="replacements_list_ruby_parentheses_format.txt",
        mime='text/plain')
