import sqlite3
import re
from openai import OpenAI
from optimizer import suggest_indexes   # 导入函数

# ---------- 配置 ----------
DEEPSEEK_API_KEY = "sk-DeepseekAPI"   # 替换成真实的 key
DB_PATH = "ecommerce.db"

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ---------- 1. 获取数据库 schema ----------
def get_db_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema_lines = []
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = cursor.fetchall()
        col_defs = [f"{col[1]} ({col[2]})" for col in cols]  # 列名 (类型)
        schema_lines.append(f"Table {table_name}: " + ", ".join(col_defs))
    # 获取外键关系（简单提示）
    schema_lines.append("\nForeign keys: order_items.order_id -> orders.order_id, order_items.product_id -> products.product_id, orders.user_id -> users.user_id, payments.order_id -> orders.order_id")
    conn.close()
    return "\n".join(schema_lines)

# ---------- 2. Few-shot 示例 ----------
FEW_SHOT_EXAMPLES = """
Example 1:
Question: "总共有多少用户？"
SQL: SELECT COUNT(*) FROM users;

Example 2:
Question: "2025年1月已完成订单的总金额是多少？"
SQL: SELECT SUM(total_amount) FROM orders WHERE status='completed' AND strftime('%Y-%m', order_date) = '2025-01';

Example 3:
Question: "每个商品类别的销售总量（按销量降序）"
SQL: SELECT p.category, SUM(oi.quantity) as total_sold FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.category ORDER BY total_sold DESC;

Example 4:
Question: "消费总额最高的前3名用户的名字和消费金额"
SQL: SELECT u.name, SUM(o.total_amount) as total_spent FROM users u JOIN orders o ON u.user_id = o.user_id WHERE o.status='completed' GROUP BY u.user_id ORDER BY total_spent DESC LIMIT 3;
"""

# ---------- 3. 调用 API 生成 SQL ----------
def text_to_sql(question):
    schema = get_db_schema(DB_PATH)
    prompt = f"""You are an expert SQLite assistant. Generate only SQL statement, no extra text.

Database schema:
{schema}

{FEW_SHOT_EXAMPLES}
Question: {question}
SQL:"""
    
    #print(f"{prompt}")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300
    )
    sql = response.choices[0].message.content.strip()
    # 清理 markdown 标记
    sql = re.sub(r'```sql\n?|```', '', sql).strip()
    return sql

# ---------- 4. 执行 SQL 并返回结果 ----------
def execute_sql(sql):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()
        return rows, col_names, None
    except Exception as e:
        return None, None, str(e)

# ---------- 测试 ----------
if __name__ == "__main__":
    question = input("请输入自然语言问题：")
    sql = text_to_sql(question)
    print(f"\n生成的 SQL:\n{sql}")
    rows, cols, err = execute_sql(sql)
    if err:
        print(f"执行错误：{err}")
    else:
        print(f"\n结果（共 {len(rows)} 行）：")
        print(cols)
        for row in rows[:10]:  # 只显示前10行
            print(row)
    suggestions = suggest_indexes(sql, DB_PATH)
    if suggestions:
        print("\n📌 索引优化建议：")
        for sug in suggestions:
            print(f"  {sug}")
    else:
        print("\n✅ 未发现明显的索引缺失。")
