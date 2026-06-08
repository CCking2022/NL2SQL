# NL2SQL
NL2SQL 是一个基于大语言模型的自然语言 SQL 查询助手。用户输入中文业务问题，系统自动生成准确的 SQLite 查询语句，执行并返回结果。项目创新地集成了智能优化器模块（optimizer.py），可自动检测缺失索引并给出 CREATE INDEX 建议，帮助提升数据库查询性能。  技术栈：Python, SQLite, DeepSeek API (OpenAI SDK), Streamlit, Faker 亮点：Few-shot Prompt 工程 · 多表 JOIN/聚合/排序支持 · 索引性能分析 · 端到端 Web 界面
