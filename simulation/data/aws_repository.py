# from helper.DBConnector import DBConnector


class AwsRepository:
    pass

    # def __init__(self):
    #     self.db_connector = DBConnector.getInstance()
    #
    # def add_user(self, name, email):
    #     cnx = self.db_connector.get_connection()
    #     cursor = cnx.cursor()
    #     query = "INSERT INTO users (name, email) VALUES (%s, %s)"
    #     cursor.execute(query, (name, email))
    #     cnx.commit()
    #     cursor.close()