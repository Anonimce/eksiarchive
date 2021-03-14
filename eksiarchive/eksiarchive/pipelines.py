# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from eksiarchive.models import *
from sqlalchemy.orm import sessionmaker
import eksiarchive.items

class EskiArchivePipeline:
    def __init__(self):
        self.process_count = 0
        self.db = db_connect()
        
        create_table(self.db)

        self.recreate_session()

    def recreate_session(self):
        self.session = sessionmaker(bind=self.db)()

    def process_item(self, item, spider):
        self.process_count += 1

        if type(item) is eksiarchive.items.Title:
            title = Title(id=item['id'], name=item['name'])

            if not self.session.query(Title).filter(Title.id == item['id']).scalar(): #Add if title doesn't exist
                self.session.add(title)

        if type(item) is eksiarchive.items.Entry:
            entry = Entry(id=item['id'], title_id=item['title_id'], author_id=item['author_id'], likes=item['likes'], content=item['content'], date=item['date'])
            
            if not self.session.query(Author).filter(Author.id == item['author_id']).scalar(): #Add if author doesn't exist
                author = Author(id=item['author_id'], name=item['author'])
                self.session.add(author)
            
            if not self.session.query(Entry).filter(Entry.id == item['id']).scalar(): #Add if entry doesn't exist
                self.session.add(entry)
        
        if self.process_count >= 20:
            self.session.commit()
            self.session.flush()

            self.process_count = 0
            self.recreate_session()

        return item
