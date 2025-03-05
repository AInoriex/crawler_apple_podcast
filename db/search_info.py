import mysql.connector
from utils.logger import logger

class SearchInfo: 
    ''' 谷歌搜索记录表 '''
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

    def Close(self):
        ''' 手动关闭数据库连接 '''
        self.cursor.close()
        self.cnx.close()
        print("database close_connection")
        
    def Select(self, table, condition=None):
        query = "SELECT * FROM {}".format(table)
        res = {}
        if condition is not None:
            query += " WHERE {}".format(condition)
        try:
            self.cursor.execute(query)
            res = self.cursor.fetchall()
            # for row in rows:
            #     print(row)
        except mysql.connector.Error as err:
            logger.error(f"SELECT Error: {err}")
        finally:
            return res
            
    def Insert(self, table, values)->bool:
        query = "INSERT INTO {} VALUES ({})".format(table, values)
        try:
            self.cursor.execute(query)
            # 执行update 或 insert操作后，需要调用commit方法才能保证修改能够生效
            self.cnx.commit()
        except mysql.connector.Error as err:
            logger.error(f"INSERT Error: {err}")
            return False
        else:
            return True

    def Update(self, table, set_values, condition)->bool:
        query = "UPDATE {} SET {} WHERE {}".format(table, set_values, condition)
        try:
            self.cursor.execute(query)
            # 执行update 或 insert操作后，需要调用commit方法才能保证修改能够生效
            self.cnx.commit()
        except mysql.connector.Error as err:
            logger.error(f"UPDATE Error: {err}")
            return False
        else:
            return True


if __name__ == "__main__":
    google_search = SearchInfo(user='root', password='123456', host='127.0.0.1', database='crawler')

    # Select statement without condition
    google_search.Select('web_search_info')
    # Insert
    google_search.Insert(table="web_search_info", values="'test_config_key', 'test_name', 'can_be_deleted', '2024-05-24 15:52'")
    # Update
    google_search.Update(table="web_search_info", set_values="value = 'can_be_deleted_2'", condition="config_key = 'test_config_key'")
    # Select statement with condition
    google_search.Select(table="web_search_info", condition="config_key = 'test_config_key'")

    google_search.Close()