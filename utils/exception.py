class MyCustomException(Exception):
    ''' 自定义异常 '''
    def __init__(self, message):
        self.message = message
 
    def __str__(self):
        return f"MyCustomException: {self.message}"

class MagicApiException(Exception):
    ''' MagicServer异常 '''
    def __init__(self, message):
        self.message = message
 
    def __str__(self):
        return f"MagicApiException: {self.message}"