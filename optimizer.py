import re

def suggest_indexes(sql, db_path):
    """解析 SQL 中 WHERE/JOIN 的列，推荐创建索引"""
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 提取可能的列名（简单正则）
    pattern = r'(\w+)\.(\w+)|JOIN (\w+) ON \3\.(\w+)\s*=\s*\w+\.(\w+)'
    columns = set()
    # JOIN 列
    joins = re.findall(r'JOIN (\w+) ON \1\.(\w+)\s*=\s*\w+\.(\w+)', sql, re.IGNORECASE)
    for tbl, col1, col2 in joins:
        columns.add((tbl, col1))
        # 另一个表的列需要从上下文解析，简化处理
    # WHERE 列
    wheres = re.findall(r'WHERE (\w+)\.(\w+)\s*=', sql, re.IGNORECASE)
    for tbl, col in wheres:
        columns.add((tbl, col))
    
    suggestions = []
    for tbl, col in columns:
        # 检查是否已有索引
        cursor.execute(f"PRAGMA index_list({tbl})")
        indexes = cursor.fetchall()
        has_index = False
        for idx in indexes:
            cursor.execute(f"PRAGMA index_info({idx[1]})")
            if any(col == info[2] for info in cursor.fetchall()):
                has_index = True
                break
        if not has_index:
            suggestions.append(f"CREATE INDEX idx_{tbl}_{col} ON {tbl}({col});")
    conn.close()
    return suggestions

# 在 text2sql.py 中调用该函数并打印
