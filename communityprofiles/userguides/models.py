from django.db import models

# Create your models here.
class StayInTouchUser(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s -- %s"%(self.name, self.email)


class AboutPost(models.Model):
    post_title = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='icons', null=True, blank=True)
    description = models.TextField(blank=True)
    topics = models.ForeignKey('AboutTopic', blank=True)
    display_order = models.IntegerField()

    @property
    def get_Text(self):
        if len(self.description) > 400:
           return self.description[:400]+' ...'
        else:
           return self.description
    def __unicode__(self):
        return self.post_title

class AboutTopic(models.Model):
    title = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    display_order = models.IntegerField()

    @property
    def get_Post(self):
        return AboutPost.objects.filter(topics__pk = self.pk).order_by("display_order")

    def __unicode__(self):
        return self.title

class faq(models.Model):
    question = models.CharField(max_length=200,unique=True)
    answer = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    display_order = models.IntegerField()

    def __unicode__(self):
        return self.question

