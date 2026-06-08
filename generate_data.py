import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('zh_CN')  # 中文数据

# 连接数据库（如果不存在会自动创建）
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# 1. 删除旧表（可选）
cursor.executescript('''
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS payments;
''')

# 2. 创建表
cursor.executescript('''
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    city TEXT,
    register_date TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    order_date TEXT,
    total_amount REAL,
    status TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    subtotal REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    payment_method TEXT,
    amount REAL,
    pay_time TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
''')

# 3. 生成用户 (200人)
users = []
for i in range(1, 201):
    age = random.randint(18, 70)
    city = random.choice(['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安'])
    register_date = fake.date_between(start_date='-2y', end_date='today')
    users.append((i, fake.name(), age, city, register_date))
cursor.executemany('INSERT INTO users VALUES (?,?,?,?,?)', users)

# 4. 生成商品 (50种)
categories = ['电子产品', '服装', '家居用品', '图书', '美妆', '食品', '运动器材']
products = []
for i in range(1, 51):
    name = fake.word() + fake.random_element(elements=['手机', '电脑', 'T恤', '沙发', '小说', '口红', '饼干'])
    category = random.choice(categories)
    price = round(random.uniform(20, 5000), 2)
    products.append((i, name, category, price))
cursor.executemany('INSERT INTO products VALUES (?,?,?,?)', products)

# 5. 生成订单 (3000单)
orders = []
order_items = []
payments = []
order_id = 1
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 3, 31)

for _ in range(3000):
    user_id = random.randint(1, 200)
    order_date = fake.date_between(start_date=start_date, end_date=end_date)
    status = random.choices(['completed', 'cancelled'], weights=[0.9, 0.1])[0]
    total_amount = 0.0
    orders.append((order_id, user_id, order_date, 0, status))  # total_amount 先占位
    # 每个订单包含 1~5 种商品
    num_items = random.randint(1, 5)
    item_list = []
    for _ in range(num_items):
        product_id = random.randint(1, 50)
        quantity = random.randint(1, 3)
        # 查询商品价格
        cursor.execute('SELECT price FROM products WHERE product_id=?', (product_id,))
        price = cursor.fetchone()[0]
        subtotal = round(price * quantity, 2)
        total_amount += subtotal
        order_items.append((order_id, product_id, quantity, subtotal))
    # 更新订单总金额
    total_amount = round(total_amount, 2)
    orders[-1] = (order_id, user_id, order_date, total_amount, status)
    
    # 已完成订单才生成支付记录
    if status == 'completed':
        payment_method = random.choice(['alipay', 'wechat', 'credit_card'])
        pay_time = fake.date_time_between(start_date=order_date, end_date=order_date + timedelta(days=2))
        payments.append((order_id, payment_method, total_amount, pay_time))
    
    order_id += 1

# 插入订单表
cursor.executemany('INSERT INTO orders VALUES (?,?,?,?,?)', orders)
# 插入订单明细表
cursor.executemany('INSERT INTO order_items (order_id, product_id, quantity, subtotal) VALUES (?,?,?,?)', order_items)
# 插入支付表
cursor.executemany('INSERT INTO payments (order_id, payment_method, amount, pay_time) VALUES (?,?,?,?)', payments)

conn.commit()
conn.close()
print("数据库生成完成！共生成 200 个用户，3000 条订单记录。")
