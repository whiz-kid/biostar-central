import sys, os, warnings
import click
from django.conf import settings

from whoosh import searching
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser


SCHEMA = Schema(title=TEXT(stored=True), pid=ID(stored=True), content=TEXT(stored=True))

__PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

sys.path.append(os.getcwd())
sys.path.append(__PATH)

from biostar4.forum.models import Post

def rebuild_index():
    idx = create_in(settings.WHOOSH_INDEX, SCHEMA)
    writer = idx.writer()
    for post in Post.objects.all():
        print ("*** adding: {}".format(post.title))
        writer.add_document(title=post.title, pid=str(post.pid), content=post.text)

    writer.commit()

def do_search(query, idx=None):
    idx = idx or open_dir(settings.WHOOSH_INDEX)
    with idx.searcher() as searcher:
        query = QueryParser("content", idx.schema).parse(query)
        result = searcher.search(query, limit=20)
        items = []
        print("search runtime: {:.2f} ms".format(result.runtime*1000))
        #print (dir(result))
        for row in result:
            row.items() # Needs this to to materialize lazy hits.
            items.append(row)

    return result, items

@click.command()
@click.option('--similar', type=str, default=False,
              help='Similar to document id' )
@click.option('--query', type=str, default=False,
              help='Queries the database')
@click.option('--rebuild', is_flag=True, default=False, help='Rebuilds the search database')
def main(query, rebuild, similar):

    import django
    django.setup()

    if rebuild:
        rebuild_index()

    if query:
        res, hits = do_search(query)
        for hit in hits:
            print (hit.items())

    if similar:
        idx = open_dir(settings.WHOOSH_INDEX)
        searcher = idx.searcher()
        docnum = searcher.document_number(pid=similar)
        #print (dir(searcher))

        r = searcher.more_like(docnum, fieldname='content')

        print("Documents like", searcher.stored_fields(docnum)['title'])
        for hit in r:
            print(hit["title"])



if __name__ == '__main__':
    main()
