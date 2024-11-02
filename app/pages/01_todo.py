import streamlit as st  # type: ignore
import mysql.connector # type: ignore
import os
import time
from tools.simple_auth import check_password
if not check_password():
    st.stop()

# MySQLデータベースの設定
DB_HOST = "db"  # Dockerのホスト名
DB_USER = "root"
DB_PASSWORD = os.environ.get("MYSQL_ROOT_PASSWORD")
DB_NAME = "tasks_db"

def get_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    return conn

# MySQLデータベースの初期化
def init_db():
    try:
        conn = get_connection()
    except Exception as e:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
        )
    c = conn.cursor()
    c.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    c.execute(f"USE {DB_NAME}")
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            estimated_time INT NOT NULL,
            elapsed_time INT NOT NULL DEFAULT 0,
            is_running BOOLEAN NOT NULL DEFAULT 0,
            start_time DOUBLE,
            sort_order INT DEFAULT 0
        )
    ''')
    conn.commit()
    c.close()
    conn.close()

# タスクの追加
def add_task(name, estimated_time):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COALESCE(MAX(sort_order), 0) + 1 FROM tasks')
    next_sort_order = c.fetchone()[0]
    c.execute('INSERT INTO tasks (name, estimated_time, sort_order) VALUES (%s, %s, %s)', (name, estimated_time, next_sort_order))
    conn.commit()
    c.close()
    conn.close()

# タスクの読み込み
def load_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM tasks ORDER BY sort_order')
    tasks = c.fetchall()
    c.close()
    conn.close()
    return tasks

# タスクの更新
def update_task(task_id, elapsed_time=None, is_running=None, start_time=None, sort_order=None):
    conn = get_connection()
    c = conn.cursor()
    if elapsed_time is not None:
        c.execute('UPDATE tasks SET elapsed_time = %s WHERE id = %s', (elapsed_time, task_id))
    if is_running is not None:
        c.execute('UPDATE tasks SET is_running = %s WHERE id = %s', (is_running, task_id))
    if start_time is not None:
        c.execute('UPDATE tasks SET start_time = %s WHERE id = %s', (start_time, task_id))
    if sort_order is not None and sort_order >= 0:
        c.execute('SELECT sort_order FROM tasks WHERE id = %s', (task_id,))
        current_sort_order = c.fetchone()[0]
        if current_sort_order < sort_order:
            c.execute('UPDATE tasks SET sort_order = sort_order - 1 WHERE sort_order > %s AND sort_order <= %s', (current_sort_order, sort_order))
        elif current_sort_order > sort_order:
            c.execute('UPDATE tasks SET sort_order = sort_order + 1 WHERE sort_order >= %s AND sort_order < %s', (sort_order, current_sort_order))
        c.execute('UPDATE tasks SET sort_order = %s WHERE id = %s', (sort_order, task_id))
    conn.commit()
    c.close()
    conn.close()

# タスクの削除
def delete_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT sort_order FROM tasks WHERE id = %s', (task_id,))
    sort_order = c.fetchone()[0]
    c.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    c.execute('UPDATE tasks SET sort_order = sort_order - 1 WHERE sort_order > %s', (sort_order,))
    conn.commit()
    c.close()
    conn.close()

# タイマーを更新するための関数
def update_timer():
    tasks = load_tasks()
    for task in tasks:
        task_id, _, _, elapsed_time, is_running, start_time, _ = task
        if is_running:
            current_time = time.time()
            new_elapsed_time = elapsed_time + int(current_time - start_time)
            update_task(task_id, elapsed_time=new_elapsed_time, start_time=current_time)

# アプリケーションの初期化
init_db()
st.title("TODO Management System")


# タスクの追加
with st.expander("Add Task Form", expanded=True):
    with st.form("add_task_form", border=False):
        task_name = st.text_input("Task Name")
        estimated_time = st.number_input("Estimated Time (minutes)", min_value=1, step=1)
        add_task_button = st.form_submit_button("Add Task", use_container_width=True)
        if add_task_button:
            add_task(task_name, estimated_time)
            st.success(f"Task '{task_name}' added successfully!")

# タスクの表示
tasks = load_tasks()
for i, task in enumerate(tasks):
    task_id, name, estimated_time, elapsed_time, is_running, start_time, sort_order = task
    if is_running:
        container = st.container(border=True)
    else:
        container = st.expander(f"{name}", expanded=True)
    with container:
        if is_running:
            st.write(f"#### {name} (Running😎)")
        cols = st.columns([1,1,1,3])
        with cols[0]:
            st.write(f"Order: {i+1}({sort_order})")
        with cols[1]:
            st.write(f"ETA: **{estimated_time} min**")
        with cols[2]:
            st.write(f"ET: **{(elapsed_time // 60):02d}:{(elapsed_time % 60):02d}**")
        with cols[3]:
            # タイマーの制御
            if is_running:
                elapsed_time = elapsed_time + int(time.time() - start_time)
                if st.button(f"Stop", key=f"stop_{task_id}", use_container_width=True, type="primary"):
                    update_task(task_id, is_running=0, elapsed_time=elapsed_time)
                    st.rerun()
            else:
                if st.button(f"Start", key=f"start_{task_id}", use_container_width=True, type="primary"):
                    update_task(task_id, is_running=1, start_time=time.time())
                    st.rerun()
        cols = st.columns(4)
        with cols[0]:
            if st.button(f"Move Up", key=f"move_up_{task_id}", use_container_width=True, disabled=i==0):
                update_task(task_id, sort_order=i-1)
                st.rerun()
        with cols[1]:
            if st.button(f"Move Down", key=f"move_down_{task_id}", use_container_width=True, disabled=i==(len(tasks)-1)):
                update_task(task_id, sort_order=i+1)
                st.rerun()
        with cols[2]:
            if st.button(f"Reset", key=f"reset_{task_id}", use_container_width=True):
                update_task(task_id, elapsed_time=0, is_running=0)
                st.rerun()
        with cols[3]:
            if st.button(f"Delete Task", key=f"delete_{task_id}", use_container_width=True):
                delete_task(task_id)
                st.success(f"Task '{name}' deleted successfully!")
                st.rerun()

# タイマーの定期更新
if any(task[4] for task in tasks):  # いずれかのタスクが実行中かどうか
    update_timer()
    time.sleep(1)
    st.rerun()