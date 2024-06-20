import mysql.connector
from mysql.connector import pooling

# 配置数据库连接信息
dbconfig = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "crawler"
}

# 创建连接池
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,  # 连接池大小
    **dbconfig
)

if __name__ == "__main__":
    # 获取连接
    connection = connection_pool.get_connection()

    try:
        cursor = connection.cursor()

        # 执行查询
        cursor.execute("SELECT * FROM pipeline_video")

        # 获取查询结果
        results = cursor.fetchall()

        for row in results:
            print(row)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if connection.is_connected():
            cursor.close()
            connection.close()