import datetime
from haystack import indexes
from biostar4.forum.models import SearchDoc, Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    title = indexes.CharField(model_attr='title')

    def get_model(self):
        return SearchDoc

    def prepare(self, obj):
        data = super(PostIndex, self).prepare(obj)
        data['text'] = obj.content
        return data

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        query = SearchDoc.objects.all()
        return query