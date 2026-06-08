import streamlit as st
import sqlite3
from text2sql import text_to_sql, execute_sql
import pandas as pd

st.set_page_config(page_title="Text2SQL 查询助手", layout="wide")
st.title("📊 自然语言 SQL 查询助手")
st.markdown("输入业务问题，AI 自动生成 SQL 并返回结果")

# 初始化 session_state
if "question" not in st.session_state:
    st.session_state.question = ""

# 示例问题列表
example_questions = [
    "2024年每个月的订单总数",
    "哪个城市的用户消费总额最高？",
    "购买过'电子产品'类别的用户有多少？",
    "最近30天内，每个用户的平均订单金额",
    "支付方式为 wechat 的总交易额是多少？"
]

question = st.text_area("💬 输入你的问题", value=st.session_state.question, height=100)

col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 生成 SQL 并查询"):
        if question:
            with st.spinner("生成 SQL 中..."):
                sql = text_to_sql(question)
                st.code(sql, language='sql')
                rows, cols, err = execute_sql(sql)
                if err:
                    st.error(f"执行错误：{err}")
                else:
                    st.success(f"查询成功，共 {len(rows)} 行")
                    if rows:
                        # 修复：用 pandas 正确显示列名
                        df = pd.DataFrame(rows, columns=cols)
                        st.dataframe(df)
        else:
            st.warning("请输入问题")

with col2:
    st.subheader("📌 示例问题")
    for q in example_questions:
        if st.button(q):
            st.session_state.question = q
            st.rerun()  # 修复新版 streamlit 写法

# 显示数据库 schema（折叠）
with st.expander("📁 数据库 Schema"):
    from text2sql import get_db_schema
    schema = get_db_schema("ecommerce.db")
    st.text(schema)
