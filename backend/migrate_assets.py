import sqlite3
import os
from pathlib import Path

# 获取数据库路径
app_data = os.getenv("APPDATA")
if app_data:
    DB_PATH = Path(app_data) / "life-canvas-os" / "life_canvas.db"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = Path(os.getenv("APP_DATA_DIR", BASE_DIR))
    DB_PATH = DATA_DIR / "life_canvas.db"

def migrate():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}, skipping migration.")
        return

    print(f"Starting migration on {DB_PATH}...")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    try:
        # 1. 为 asset_categories 添加 is_system 字段
        print("Checking asset_categories table...")
        cursor.execute("PRAGMA table_info(asset_categories)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "is_system" not in columns:
            print("Adding is_system column to asset_categories...")
            cursor.execute("ALTER TABLE asset_categories ADD COLUMN is_system BOOLEAN DEFAULT 0")
            
            # 标记默认的八个分类
            default_names = ["现金", "活期/储蓄", "投资理财", "固定资产", "应收款", "负债", "保险/公积金/养老金", "其他"]
            placeholders = ','.join(['?'] * len(default_names))
            cursor.execute(f"UPDATE asset_categories SET is_system = 1 WHERE name IN ({placeholders})", default_names)
            print("Marked default categories as system categories.")
        else:
            print("is_system column already exists.")

        # 2. 为 asset_items 添加 config 字段
        print("Checking asset_items table...")
        cursor.execute("PRAGMA table_info(asset_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "config" not in columns:
            print("Adding config column to asset_items...")
            cursor.execute("ALTER TABLE asset_items ADD COLUMN config JSON")
        else:
            print("config column already exists.")

        conn.commit()
        print("Migration completed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
