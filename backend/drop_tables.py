import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root',
                       password='Wwh@12345', db='cicd', charset='utf8mb4')
tables = ['app_info', 'user_info', 'django_admin_log', 'django_content_type',
          'django_session', 'auth_user_user_permissions', 'auth_user_groups',
          'auth_group_permissions', 'auth_user', 'auth_group', 'auth_permission',
          'django_migrations']
with conn.cursor() as cur:
    cur.execute('SET FOREIGN_KEY_CHECKS=0;')
    for t in tables:
        cur.execute('DROP TABLE IF EXISTS `%s`;' % t)
        print('Dropped:', t)
    cur.execute('SET FOREIGN_KEY_CHECKS=1;')
    conn.commit()
print('Done.')
conn.close()
