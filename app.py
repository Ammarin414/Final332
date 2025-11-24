from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json

app = Flask(__name__)
# เปิด CORS ให้ S3 สามารถเรียก API นี้ได้
CORS(app) 

# ===============================================
# !! สำคัญ !!
# แก้ไขข้อมูลการเชื่อมต่อ RDS ของคุณที่นี่
# (ในโลกจริง ควรอ่านค่าเหล่านี้จาก Environment Variables)
# ===============================================
db_config = {
    'host': 'YOUR_RDS_ENDPOINT_HERE', # เช่น todo-database.xxxxx.us-east-1.rds.amazonaws.com
    'user': 'admin',                 # Master username ของคุณ
    'password': 'YOUR_RDS_PASSWORD_HERE',
    'database': 'tododb',             # ชื่อ Database ที่คุณสร้าง (อาจต้องสร้างเองก่อน)
    'ssl_disabled': True
}
# ===============================================

def create_db_connection():
    """สร้างการเชื่อมต่อ Database"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def create_table_if_not_exists():
    """สร้างตาราง todos ถ้ายังไม่มี"""
    conn = create_db_connection()
    if conn is None:
        return
        
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text VARCHAR(255) NOT NULL,
                completed BOOLEAN DEFAULT FALSE
                )CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
        """)
        conn.commit()
        print("Table 'todos' checked/created successfully.")
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/todos', methods=['GET'])
def get_todos():
    """GET /todos - ดึง To-Do List ทั้งหมด"""
    conn = create_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection error'}), 500
        
    try:
        cursor = conn.cursor(dictionary=True) # คืนค่าเป็น Dict
        cursor.execute("SELECT * FROM todos")
        todos = cursor.fetchall()
        # แปลง boolean (0/1) เป็น True/False
        for todo in todos:
            todo['completed'] = bool(todo['completed'])
        return jsonify(todos)
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/todos', methods=['POST'])
def add_todo():
    """POST /todos - เพิ่ม To-Do ใหม่"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'message': 'Missing "text" in request body'}), 400

    # สร้าง ID (ใน Lambda เราใช้ uuid, ที่นี่ใช้ text + hash กันง่ายๆ)
    import hashlib
    item_id = hashlib.md5(data['text'].encode()).hexdigest()

    item = {
        'id': item_id,
        'text': data['text'],
        'completed': False
    }

    conn = create_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection error'}), 500
        
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (id, text, completed) VALUES (%s, %s, %s)", 
                       (item['id'], item['text'], item['completed']))
        conn.commit()
        return jsonify(item), 201
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/todos', methods=['PUT'])
def update_todo():
    """PUT /todos - อัปเดต To-Do (เช่น ติ๊กถูก)"""
    data = request.get_json()
    if 'id' not in data or 'completed' not in data:
        return jsonify({'message': 'Missing "id" or "completed" in body'}), 400

    item_id = data['id']
    completed = bool(data['completed'])

    conn = create_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection error'}), 500
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("UPDATE todos SET completed = %s WHERE id = %s", (completed, item_id))
        conn.commit()
        
        # ดึงข้อมูลที่อัปเดตแล้วกลับไป
        cursor.execute("SELECT * FROM todos WHERE id = %s", (item_id,))
        updated_item = cursor.fetchone()
        if updated_item:
            updated_item['completed'] = bool(updated_item['completed'])
            return jsonify(updated_item), 200
        else:
            return jsonify({'message': 'Item not found'}), 404
            
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/todos', methods=['DELETE'])
def delete_todo():
    """DELETE /todos - ลบ To-Do"""
    data = request.get_json()
    if 'id' not in data:
        return jsonify({'message': 'Missing "id" in body'}), 400

    item_id = data['id']
    conn = create_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection error'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = %s", (item_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'message': 'Item not found'}), 404
            
        return jsonify({'message': f'Todo {item_id} deleted'}), 200
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    create_table_if_not_exists()
    # รันเซิร์ฟเวอร์ ให้เข้าถึงได้จากภายนอก (0.0.0.0) ที่ Port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)



