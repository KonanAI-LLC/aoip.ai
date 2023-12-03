class DBConnector:
    pass
    # __instance = None
    #
    # @staticmethod
    # def getInstance():
    #     if DBConnector.__instance == None:
    #         DBConnector()
    #     return DBConnector.__instance
    #
    # def __init__(self):
    #     if DBConnector.__instance != None:
    #         raise Exception("This class is a singleton!")
    #     else:
    #         DBConnector.__instance = self
    #         self.cnx = mysql.connector.connect(
    #                 user='root',
    #                 password='mysql1234',
    #                 host='localhost',
    #                 database='voip_rest',
    #                 auth_plugin='mysql_native_password'
    #                 )
    #
    # def get_connection(self):
    #     return self.cnx