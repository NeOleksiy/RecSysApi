from django.db import models
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


# Create your models here.
class Similarity(models.Model):
    created = models.DateField()
    source = models.CharField(max_length=16, db_index=True)
    target = models.CharField(max_length=16)
    similarity = models.DecimalField(max_digits=8, decimal_places=7)

    class Meta:
        db_table = 'similarity'

    def __str__(self):
        return "[({} => {}) sim = {}]".format(self.source,
                                              self.target,
                                              self.similarity)


class TfIdfMatrix(models.Model):
    row_id = models.CharField(max_length=16, db_index=True)
    col_id = models.CharField(max_length=16)
    tfidf_sim = models.DecimalField(max_digits=8, decimal_places=7)

    class Meta:

        db_table = 'tf-idf-matrix'

    def __str__(self):
        return "[({} => {}) sim = {}]".format(self.row_id,
                                              self.col_id,
                                              self.tfidf_sim)
