import sqlite3

from AstraConfig import AstraConfig


class AstraChart:
    def __init__(self):
        self.conn =None
        self.init_database(AstraConfig.get("AstraChart").get("db_path"))
    def init_database(self,db_path:str):
        self.conn = sqlite3.connect(db_path)
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM ASTRA_CHAT
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

if __name__ == '__main__':
    astra_chart = AstraChart()
