#!/usr/bin/env python3
"""重置所有用户的密码为 '123456'"""

import bcrypt
import psycopg2

# 生成 bcrypt 哈希
password = "123456"
password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
print(f"生成的 bcrypt 哈希: {password_hash}")

# 连接数据库
dsn = "postgresql://zhiyuan:zhiyuan_dev_2026@localhost:5432/zhiyuan"
try:
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()

    # 查看当前用户列表
    cur.execute("SELECT id, phone FROM users")
    users = cur.fetchall()
    print(f"\n数据库中共有 {len(users)} 个用户:")
    for uid, phone in users:
        print(f"  - 手机号: {phone}, ID: {uid}")

    # 更新所有用户的密码
    cur.execute("UPDATE users SET password_hash = %s", (password_hash,))
    print(f"\n✅ 已重置 {cur.rowcount} 个用户的密码为 '123456'")

    conn.commit()
    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ 操作失败: {e}")
    raise
