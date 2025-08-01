import mysql.connector
from mysql.connector import pooling
import sys
from proj_whisper.exception.exception import CustomException

class DatabaseConnection:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        pool_reset_session=True,
        host='172.29.64.1',
        user='root',
        password='Pass137920word',
        database='ml_project_db',
    )

    @staticmethod
    def get_connection():
        try:
            connection = DatabaseConnection.connection_pool.get_connection()
            if connection.is_connected():
                return connection
        except mysql.connector.Error as err:
            raise CustomException(err, sys)
