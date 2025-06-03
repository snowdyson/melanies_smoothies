# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# アプリのタイトルと説明
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    (Choose up to 5 ingredients, though this limit is not currently enforced.)
    """
)

# NEW: スムージーの名前を入力するテキストボックス
name_on_order = st.text_input('Name on Smoothie:')
if name_on_order: # 名前が入力された場合のみ、確認のために表示
    st.write('The name on your Smoothie will be:', name_on_order)

# 現在のSnowflakeセッションを取得
cnx = st.connection("snowflake")
session = cnx.session()

# --- ▼▼▼ データ取得部分を修正 ▼▼▼ ---
# FRUIT_OPTIONSテーブルからFRUIT_NAMEとSEARCH_ON列を取得
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# SnowparkデータフレームをPandasデータフレームに変換
pd_df = my_dataframe.to_pandas()
# マルチセレクトウィジェット用のリストを作成
fruit_list_for_multiselect = [row["FRUIT_NAME"] for row in my_dataframe.collect()]
# --- ▲▲▲ データ取得部分の修正ここまで ▲▲▲ ---


# 材料を選択するマルチセレクトウィジェット
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list_for_multiselect,
    default=[],
    max_selections=5
)

# 材料が選択された場合のみ処理を実行
if ingredients_list:
    ingredients_string = ''

    # 選択されたフルーツごとに処理をループ
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        
        # --- ▼▼▼ forループ内を修正 ▼▼▼ ---
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # pd_dfから、FRUIT_NAMEに一致する行を探し、SEARCH_ON列の値を取得
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.') # デバッグ用の表示
        
        # API呼び出しに、取得したsearch_on変数を使用
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        
        # データを表示
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        # --- ▲▲▲ forループ内の修正ここまで ▲▲▲ ---

    # forループの外で、注文情報を一度だけ表示
    ingredients_string = ingredients_string.strip()
    st.write("You are about to order:", ingredients_string)

    # 送信ボタン
    submit_button = st.button("Submit Order")

    if submit_button:
        my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order) 
        values ('{ingredients_string}', '{name_on_order}')
        """
        
        session.sql(my_insert_stmt).collect()
        st.success(f'Smoothie for "{name_on_order}" with "{ingredients_string}" ordered!', icon="✅")

# 材料が選択されていない場合に表示するメッセージ
else:
    st.write("Please choose your ingredients to make a smoothie!")
