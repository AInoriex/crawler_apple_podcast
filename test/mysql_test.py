import mysql.connector

class DAO: 
    def __init__(self, user, password, host, database):
        self.cnx = mysql.connector.connect(user=user, 
                                          password=password,
                                          host=host,
                                          database=database)   
        self.cursor = self.cnx.cursor(
            buffered=True,      # 查询结果立即被获取并存入内存 内存↓效率↑
            dictionary=True     # select返回结构为字典：k字段-v数值
        )
        print("database __init__")

    # 注意，在Python中，应确保在不再需要数据库连接时及时关闭它，因此我们在析构函数中关闭它
    def __del__(self):
        self.cursor.close()
        self.cnx.close()
        print("database __del__")

    def close_connection(self):
        ''' 手动关闭数据库连接 '''
        self.cursor.close()
        self.cnx.close()
        print("database close_connection")
        
    def Select(self, table, condition=None):
        query = "SELECT * FROM {}".format(table)
        if condition is not None:
            query += " WHERE {}".format(condition)
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for row in rows:
                print(row)
        except mysql.connector.Error as err:
            print("select Error: ", err)

    def Insert(self, table, values):
        query = "INSERT INTO {} VALUES ({})".format(table, values)
        try:
            self.cursor.execute(query)
            # 执行update 或 insert操作后，需要调用commit方法才能保证修改能够生效
            self.cnx.commit()
        except mysql.connector.Error as err:
            print("insert Error: ", err)

    def Update(self, table, set_values, condition):
        query = "UPDATE {} SET {} WHERE {}".format(table, set_values, condition)
        try:
            self.cursor.execute(query)
            # 执行update 或 insert操作后，需要调用commit方法才能保证修改能够生效
            self.cnx.commit()
        except mysql.connector.Error as err:
            print("update Error: ", err)


if __name__ == "__main__":
    dao = DAO(user='root', password='123456', host='127.0.0.1', database='meta')

    # Select statement without condition
    dao.Select('common_config')
    # Insert
    dao.Insert(table="common_config", values="'test_config_key', 'test_name', 'can_be_deleted', '2024-05-24 15:52'")
    # Update
    dao.Update(table="common_config", set_values="value = 'can_be_deleted_2'", condition="config_key = 'test_config_key'")
    # Select statement with condition
    dao.Select(table="common_config", condition="config_key = 'test_config_key'")

    dao.close_connection()