from django.db import models

# Create your models here.
class InvestopediaTerms(models.Model):
    termID       = models.AutoField(primary_key=True)
    term         = models.CharField(max_length=300)
    definition   = models.TextField()

    class Meta:
        managed = False
        db_table    = "Investopedia_Term"

#Create your models here.
class TermAndQuestion(models.Model):
    questionID = models.AutoField(primary_key=True)
    termID     = models.ForeignKey('InvestopediaTerms', models.DO_NOTHING, db_column='termID')
    question   = models.TextField()

    class Meta:
        managed = False
        db_table    = "Investopedia_Term_Question"