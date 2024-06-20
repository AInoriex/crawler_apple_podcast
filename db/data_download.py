import mysql.connector
from time import localtime, strftime
from json import dumps, loads
from utils.tool import load_cfg
import mysql.connector
from mysql.connector import pooling

cfg = load_cfg("config.json")

class PipelineVideo:
    ''' 数据结果记录表 '''
    def __init__(self, user, password, host, database, port=3306, table="pipeline_video"):
        self.cnx = mysql.connector.connect(user=user, 
                                          password=password,
                                          host=host,
                                          port=port,
                                          database=database)   
        self.cursor = self.cnx.cursor(
            buffered=False,      # 查询结果立即被获取并存入内存 内存↓效率↑
            dictionary=True     # select返回结构为字典：k字段-v数值
        )
        self.table = table
        # print("PipelineVideo database __init__")

    # 注意，在Python中，应确保在不再需要数据库连接时及时关闭它，因此我们在析构函数中关闭它
    def __del__(self):
        self.cursor.close()
        self.cnx.close()
        print("PipelineVideo database __del__")

    def CloseConnection(self):
        ''' 手动关闭数据库连接 '''
        self.cursor.close()
        self.cnx.close()
        print("PipelineVideo database close_connection")

    def get_now_time_string(self):
        ''' 返回现在时间戳字符串 | 格式：2024-06-12 18:43 '''
        return strftime("%Y-%m-%d %H:%M", localtime())
        
    def Select(self, condition=None):
        query = f"SELECT * FROM {self.table}"
        if condition is not None:
            query += " WHERE {}".format(condition)
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            print(rows)
            # for row in rows:
            #     print(row)
        except mysql.connector.Error as err:
            print("PipelineVideo Select Error: ", err)
            raise err
        else:
            return rows

    def Insert(self, values):
        query = f"INSERT INTO {self.table} VALUES ({values})"
        try:
            self.cursor.execute(query)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print("PipelineVideo Insert Error: ", err)
            raise err

    def CreatePodcastRecord(self, vid:str, cloud_path:str, duration:int, link:str, info=""):
        ''' 创建播客下载上传成功记录 '''
        position_quwan = int(3) #存储位置：quwan
        type_podcast = int(4) #数据类型：播客
        status_upload = int(2) #状态：已上传云端
        now_time_string = self.get_now_time_string()
        info = str(info).strip().replace("'","''") #解决数据中存在单引号的问题
        try:
            query_result = self.Select(condition=f"vid = '{vid}'")
            query = ""
            if len(query_result) <= 0:
                # 查询为空,insert
                query = f"INSERT INTO {self.table}(`vid`, `position`, `cloud_path`, `type`, `duration`, `link`, `language`, `status`, `info`, `created_at`, `updated_at`)  \
                        VALUES('{vid}', {position_quwan}, '{cloud_path}', '{type_podcast}', '{duration}', '{link}', 'en', {status_upload}, '{info}', '{now_time_string}', '{now_time_string}')"
            else:
                # 查询存在,update
                query = f"UPDATE {self.table} SET cloud_path = '{cloud_path}', duration = '{duration}', link = '{link}', info = '{info}' WHERE vid = '{vid}'"
            self.cursor.execute(query)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print("PipelineVideo CreatePodcastRecord Error: ", err)
            raise err

    def Update(self, set_values, condition):
        query = f"UPDATE {self.table} SET {set_values} WHERE {condition}"
        try:
            self.cursor.execute(query)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print("PipelineVideo Update Error: ", err)
            raise err

class PipelineVideoV2:
    ''' 数据结果记录表 '''
    def __init__(self, user, password, host, database, port=3306, table="pipeline_video"):
        dbconfig = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }
        # 创建连接池
        self.connection_pool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,  # 连接池大小
            **dbconfig
        )
        self.table = table
        # print("PipelineVideoV2 database __init__")

    def __del__(self):
        try:
            self.connection_pool._remove_connections()
            print("Connection pool released.")
        except Exception as e:
            print(f"[Error] __del__ releasing connection pool: {e}")

    def CloseConnection(self):
        ''' 手动关闭数据库连接 '''
        try:
            self.connection_pool._remove_connections()
            print("Connection pool released.")
        except Exception as e:
            print(f"[Error] CloseConnection releasing connection pool: {e}")

    def get_now_time_string(self):
        ''' 返回现在时间戳字符串 | 格式：2024-06-12 18:43 '''
        return strftime("%Y-%m-%d %H:%M", localtime())
    
    def get_connection(self):
        ''' 获取数据库连接 '''
        return self.connection_pool.get_connection()

    def Select(self, condition=None):
        query = f"SELECT * FROM {self.table}"
        if condition is not None:
            query += " WHERE {}".format(condition)
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            print("PipelineVideoV2 Select:", rows)
            # for row in rows:
            #     print(row)
        except mysql.connector.Error as err:
            print("PipelineVideoV2 Select Error: ", err)
            raise err
        except Exception as err:
            print("PipelineVideoV2 Select Unknown Error: ", err)
            raise err
        else:
            return rows
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def Insert(self, values):
        query = f"INSERT INTO {self.table} VALUES ({values})"
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
        except mysql.connector.Error as err:
            print("PipelineVideoV2 Insert Error: ", err)
            raise err
        except Exception as err:
            print("PipelineVideoV2 Insert Unknown Error: ", err)
            raise err
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def Update(self, set_values, condition):
        query = f"UPDATE {self.table} SET {set_values} WHERE {condition}"
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
        except mysql.connector.Error as err:
            print("PipelineVideoV2 Update Error: ", err)
            raise err
        except Exception as err:
            print("PipelineVideoV2 Update Unknown Error: ", err)
            connection.rollback()
            raise err
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def CreatePodcastRecord(self, vid:str, cloud_path:str, duration:int, link:str, info=""):
        ''' 创建播客下载上传成功记录 '''
        position_quwan = int(3) #存储位置：quwan
        type_podcast = int(4) #数据类型：播客
        status_upload = int(2) #状态：已上传云端
        now_time_string = self.get_now_time_string()
        info = str(info).strip().replace("'","''") #解决数据中存在单引号的问题
        try:
            query_result = self.Select(condition=f"vid = '{vid}'")
            query = ""
            if len(query_result) <= 0:
                # 查询为空,insert
                query = f"INSERT INTO {self.table}(`vid`, `position`, `cloud_path`, `type`, `duration`, `link`, `language`, `status`, `info`, `created_at`, `updated_at`)  \
                        VALUES('{vid}', {position_quwan}, '{cloud_path}', '{type_podcast}', '{duration}', '{link}', 'en', {status_upload}, '{info}', '{now_time_string}', '{now_time_string}')"
            else:
                # 查询存在,update
                query = f"UPDATE {self.table} SET cloud_path = '{cloud_path}', duration = '{duration}', link = '{link}', info = '{info}' WHERE vid = '{vid}'"
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            print("CreatePodcastRecord committed successfully")
        except mysql.connector.Error as err:
            print("PipelineVideoV2 CreatePodcastRecord Error: ", err)
            connection.rollback()
            raise err
        except Exception as err:
            print("PipelineVideoV2 CreatePodcastRecord Unknown Error: ", err)
            connection.rollback()
            raise err
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


DB = PipelineVideoV2(
    user=cfg["db_conf"]["user"], 
    password=cfg["db_conf"]["password"], 
    host=cfg["db_conf"]["host"], 
    port=cfg["db_conf"]["port"], 
    database=cfg["db_conf"]["database"],
    table=cfg["db_conf"]["table"]
)

if __name__ == "__main__":
    # pipeline_video = PipelineVideo(user='root', password='123456', host='127.0.0.1', database='crawler') # localhost

    # Insert
    save_json = {
        "id": "Podcast_571335890_1000630309236",
        "title": "Dr. Rochelle Walensky on making health care policy under fire",
        "full_url": "https://podcasts.apple.com/us/podcast/dr-rochelle-walensky-on-making-health-care-policy-under/id571335890?i=1000630309233",
        "author": "Rochelle Walensky, Ralph Ranalli",
        "duration": 2489000,
        "categories": [
            "Education"
        ],
        "asset_url": "https://dts.podtrac.com/redirect.mp3/cdn.simplecast.com/audio/430dbfb5-1a4c-4451-9b14-8d6a00bc3634/episodes/153449d2-11df-4b2d-a4e8-c0e487007c62/audio/3d8a2e0a-1810-4f2c-8683-6caa9e490747/default_tc.mp3?aid=rss_feed&feed=8W_aZ33f"
    }
    # pipeline_video.CreatePodcastRecord(
    #     vid="Podcast_571335890_1000630309236",
    #     cloud_path="https://cos-bj-x-tmeta-1302248489.cos.ap-beijing.myqcloud.com/dev/live_train/deploy_server/temp/follow.wav",
    #     duration=200,
    #     link="https://podcasts.apple.com/us/podcast/dr-rochelle-walensky-on-making-health-care-policy-under/id571335890?i=1000630309233",
    #     info = dumps(save_json)
    # )

    # Update
    # data_download.Update(set_values="value = 'can_be_deleted_2'", condition="config_key = 'test_config_key'")

    # Select
    # pipeline_video.Select(condition="id > 0 ORDER BY id DESC LIMIT 1")

    # vid = "Podcast_571335890_1000630309235"
    # pipeline_video.Select(condition=f"vid = '{vid}'")

    # pipeline_video.CloseConnection()