import pymysql, hashlib

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root',
                       password='Wwh@12345', db='cicd', charset='utf8mb4')
with conn.cursor() as cur:
    for t in ['app_info', 'user_info', 'role_info', 'app_permission']:
        cur.execute('SHOW COLUMNS FROM `%s`;' % t)
        print('[%s]' % t)
        for col in cur.fetchall():
            print('  %-20s %s' % (col[0], col[1]))
        print()

    # Re-insert admin user
    pwd = hashlib.md5('admin'.encode()).hexdigest()
    cur.execute("""
        INSERT IGNORE INTO user_info (username, password, email, role, is_active, deleted, create_time, update_time)
        VALUES ('admin', %s, '', 'admin', 1, 0, NOW(), NOW())
    """, (pwd,))
    conn.commit()
    print('Admin user ready.')

conn.close()
