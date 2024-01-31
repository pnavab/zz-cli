import os
import sqlite3
import sys

db_file = "zz.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS zz (id INTEGER PRIMARY KEY, alias TEXT NOT NULL UNIQUE, directory TEXT NOT NULL)")
conn.commit()

def get_directory_from_alias(alias):
  cursor.execute("SELECT directory FROM zz WHERE alias = ?", (alias, ))
  info = cursor.fetchone()
  if info is not None and len(info) > 0:
    return info[0]
  return None

def add_entry(alias, directory):
  try:
    cursor.execute("INSERT INTO zz (alias, directory) VALUES (?, ?)", (alias, directory))
    conn.commit()
    return True
  except Exception as e:
    return False


def get_all():
  cursor.execute("SELECT * FROM zz")
  rows = cursor.fetchall()
  return rows