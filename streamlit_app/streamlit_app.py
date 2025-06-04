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

# FRUIT_OPTIONSテーブルからFRUIT_NAMEとSEARCH_ON列を取得
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# ドロップダウンには「FRUIT_NAME」を表示
fruit_list_for_multiselect = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# 材料を選択するマルチセレクトウィジェット
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list_for_multiselect,
    default=[],
    max_selections=5
)

# 材料が選択された場合のみ処理を実行
if ingredients_list:
    
    # ▼▼▼ 修正点2: 各フルーツ名の空白を確実に取り除く、より安全な方法に変更 ▼▼▼
    ingredients_string = " ".join([fruit.strip() for fruit in ingredients_list])

    # 注文内容を先に表示
    st.write("You are about to order:", ingredients_string)

    # 選択されたフルーツごとに栄養情報を表示するループ
    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + ' Nutrition Information')
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # 送信ボタン
    submit_button = st.button("Submit Order")

    if submit_button:
        my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order) 
        values ('{ingredients_string}', '{name_on_order}')
        """
        
        # ▼▼▼ 修正点1: INSERT文の末尾にあった .collect() を削除しました ▼▼▼
        session.sql(my_insert_stmt)
        
        st.success(f'Smoothie for "{name_on_order}" with "{ingredients_string}" ordered!', icon="✅")

# 材料が選択されていない場合に表示するメッセージ
else:
    st.write("Please choose your ingredients to make a smoothie!")
