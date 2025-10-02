import sqlite3



class AstraChart:
    def __init__(self):
        self.conn =None

    def init_database(self,db_path:str):
        self.conn = sqlite3.connect(db_path)
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM ASTRA_CHAT
        """)
        c = cursor.fetchall()
        print(c)
        cursor.close()


if __name__ == '__main__':
    astra_chart = AstraChart()
    # astra_chart.init_database()
