```markdown
# 📊 NL2SQL 自然语言查询助手

基于大语言模型（LLM）的自然语言转 SQL 查询工具，支持通过中文问题自动生成 SQL 并执行，同时提供索引优化建议。帮助非技术用户零代码获取数据库分析结果，适用于数据科学、商业智能等场景。

## ✨ 主要特性

- **自然语言转 SQL**：输入中文业务问题，自动生成准确的 SQLite 查询语句。
- **即时执行与展示**：自动执行生成的 SQL，返回表格结果。
- **智能索引建议**：分析生成的 SQL，自动检测缺失的数据库索引，给出 `CREATE INDEX` 优化建议（`optimizer.py`）。
- **交互式 Web 界面**：基于 Streamlit 构建，提供友好的 UI，支持示例问题快速体验。
- **上下文增强**：内置 Few-shot 示例和数据库 Schema 描述，提升复杂查询准确率。

## 🛠️ 技术栈

| 组件            | 技术选型                                      |
| --------------- | --------------------------------------------- |
| 数据库          | SQLite（轻量级，零配置）                      |
| 后端语言        | Python 3.9+                                   |
| 大模型 API      | DeepSeek API（兼容 OpenAI SDK）               |
| Web 界面        | Streamlit                                     |
| 数据生成        | Faker + Pandas                                |
| SQL 优化分析    | 正则匹配 + SQLite 系统表（`PRAGMA index_list`）|

## 📁 项目结构

```
NL2SQL/
├── ecommerce.db           # 生成的 SQLite 数据库（自动生成）
├── generate_data.py       # 模拟电商数据生成脚本
├── text2sql.py            # 核心模块：Schema 获取、LLM 调用、SQL 执行
├── optimizer.py           # SQL 优化分析模块：缺失索引检测
├── app.py                 # Streamlit Web 应用
├── requirements.txt       # Python 依赖列表
└── README.md              # 项目说明文档
```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/CCking2022/NL2SQL.git
cd NL2SQL
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

`requirements.txt` 内容：

```
openai
pandas
streamlit
faker
sqlparse
```

### 3. 生成模拟数据

运行数据生成脚本，创建包含 5 张表（用户、商品、订单、订单明细、支付记录）的 SQLite 数据库：

```bash
python generate_data.py
```

成功后将生成 `ecommerce.db` 文件。

### 4. 配置 API Key

本项目默认使用 **DeepSeek API**（新用户赠送 500 万 tokens）。  
在 `text2sql.py` 中替换你的 API Key：

```python
DEEPSEEK_API_KEY = "sk-DeepSeekAPI"
```

> 也可选择本地 Ollama 方案（见文末附录）。

### 5. 命令行体验

```bash
python text2sql.py
```

输入问题（如“每个商品类别的销售总量”）即可看到生成的 SQL 和查询结果，以及索引优化建议。

### 6. 启动 Web 界面

```bash
streamlit run app.py
```

浏览器打开 `http://localhost:8501`，在输入框中输入自然语言问题，点击按钮即可获取 SQL 和结果。

## 📝 使用示例

**自然语言问题**：

> “查询每个用户的订单总金额，并按金额从高到低排序，只显示前10名。”

**生成的 SQL**：

```sql
SELECT u.name, SUM(o.total_amount) AS total_spent
FROM users u
JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id
ORDER BY total_spent DESC
LIMIT 10;
```

**输出结果**（前 3 行）：

| name   | total_spent |
|--------|-------------|
| 刘敏   | 434958.52   |
| 吴淑华 | 378594.58   |
| 谷玉华 | 359229.00   |

**优化建议**（若缺失索引）：

```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```

## 🔍 优化器模块 (`optimizer.py`) 的作用

`optimizer.py` 是项目的智能查询优化顾问，主要功能：

1. **解析 SQL 语句**：通过正则匹配提取 `JOIN`、`WHERE`、`ORDER BY` 中涉及的列名和表名。
2. **检查现有索引**：连接 SQLite 数据库，查询系统表 `PRAGMA index_list` 和 `PRAGMA index_info`，判断关键列是否已有索引。
3. **生成索引建议**：对缺失索引的列输出 `CREATE INDEX` 语句，帮助提升查询性能。
4. **无侵入集成**：在 `text2sql.py` 主流程中自动调用，建议信息打印在控制台或显示在 Web 界面中。

> 通过这个模块，项目展示了数据工程师在性能调优方面的最佳实践——不仅会写 SQL，还懂得如何让它跑得更快。

## 🧪 测试环境

- 操作系统：Windows 10 / macOS / Linux
- Python 版本：3.9+
- 数据库：SQLite 3

## 📌 未来改进方向

- 支持更多 SQL 方言（PostgreSQL、MySQL）
- 增加查询缓存机制，减少重复 API 调用
- 增强优化器检测规则（如检测 `SELECT *`、缺少 WHERE 的全表扫描）
- 引入更强大的本地开源模型（如 Qwen-Coder）实现完全离线运行

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来改进项目。

## 📄 许可证

MIT License

---

## 附录：使用本地 Ollama 替代 API（免费、离线）

1. 安装 [Ollama](https://ollama.com/) 并拉取代码模型：

   ```bash
   ollama pull qwen2.5-coder:7b
   ```

2. 修改 `text2sql.py` 中的 `text_to_sql` 函数，将 API 调用替换为本地请求：

   ```python
   import requests

   def text_to_sql(question):
       # 省略 schema 和 prompt 构造部分...
       response = requests.post('http://localhost:11434/api/generate',
                                json={'model': 'qwen2.5-coder:7b', 'prompt': prompt, 'stream': False})
       sql = response.json()['response'].strip()
       return sql
   ```

其余代码保持不变，无需 API Key 即可运行。
```
