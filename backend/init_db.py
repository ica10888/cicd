"""
Run this script once to create the 'cicd' database if it doesn't exist.
Usage: python init_db.py
"""
import configparser
import os

import pymysql

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

conn = pymysql.connect(
    host=config.get('database', 'host'),
    port=int(config.get('database', 'port')),
    user=config.get('database', 'user'),
    password=config.get('database', 'password'),
    charset='utf8mb4',
)

with conn.cursor() as cur:
    db_name = config.get('database', 'name')
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    print(f"Database '{db_name}' is ready.")

conn.close()
