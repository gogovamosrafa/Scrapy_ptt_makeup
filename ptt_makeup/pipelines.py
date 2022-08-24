# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3


class PttMakeupPipeline:
    def process_item(self, item, spider):
        # Define insert statement
        self.cur.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?)",
                         (
                             str(item['title']),
                             str(item['date'].strftime('%Y-%m-%d %H:%M:%S')),
                             str(item['article']),
                             str(item['comment']),
                             str(item['url'])
                         ))
        # Execute insert of data into database
        self.con.commit()
        return item

    def __init__(self):

        # Creating connection to database
        self.create_conn()

        # calling method to create table
        self.create_table()

    # create connection method to create database
    # or use database to store scraped data
    def create_conn(self):

        # connecting to database.
        self.con = sqlite3.connect("ptt_makeup.db")

        # collecting reference to cursor of connection
        self.cur = self.con.cursor()

    def create_table(self):

        # Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS data(
            title TEXT,
            date TEXT,
            article TEXT,
            comment TEXT,
            url TEXT
        )
        """)
