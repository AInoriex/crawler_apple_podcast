import mysql.connector
from time import localtime, strftime
from json import dumps, loads

class PipelineVideo:
    ''' 数据结果记录表 '''
    def __init__(self, user, password, host, database):
        self.cnx = mysql.connector.connect(user=user, 
                                          password=password,
                                          host=host,
                                          database=database)   
        self.cursor = self.cnx.cursor(
            buffered=False,      # 查询结果立即被获取并存入内存 内存↓效率↑
            dictionary=True     # select返回结构为字典：k字段-v数值
        )
        self.table = "pipeline_video"
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
        status_upload = int(4) #状态：已上传云端
        now_time_string = self.get_now_time_string()
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