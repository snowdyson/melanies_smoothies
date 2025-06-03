# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col # import文を上部に移動

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

# FRUIT_OPTIONSテーブルからFRUIT_NAME列を取得し、リストに変換
fruit_options_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list_for_multiselect = [row["FRUIT_NAME"] for row in fruit_options_df.collect()]

# 材料を選択するマルチセレクトウィジェット
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list_for_multiselect,
    default=[],
    max_selections=5  # <-- この行を追加して、選択を5つに制限します
)

# 材料が選択された場合のみ処理を実行
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
    ingredients_string = ingredients_string.strip()

    st.write("You are about to order:", ingredients_string)

    # 送信ボタン
    submit_button = st.button("Submit Order")

    if submit_button:
        # 現時点では、ORDERSテーブルにはingredients列しかないため、name_on_orderはDBに保存していません。
        # 表示メッセージに含めることで、UXを向上させています。
        my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order) 
        values ('{ingredients_string}', '{name_on_order}')
        """
        
        session.sql(my_insert_stmt).collect()
        # 成功メッセージにオーダー名を含める
        st.success(f'Smoothie for "{name_on_order}" with "{ingredients_string}" ordered!', icon="✅")
else:
    # 材料が選択されていない場合に表示するメッセージ
    st.write("Please choose your ingredients to make a smoothie!")


# New section to display smoothiefroot nutrition information
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# この行をコメントアウト（または削除）
# st.text(smoothiefroot_response.json())

# この行を新しく追加
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)



