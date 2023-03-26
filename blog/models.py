from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.utils.text import slugify
from django.conf import settings
from django.dispatch import receiver
from users.models import Account

# Create your models here.

def upload_location(instance, filename):
    file_path = 'blog/{author_id}/{title}-{filename}'.format(
        author_id=str(instance.author.id), title=str(instance.title), filename=filename
    )
    return file_path


class BlogPost(models.Model):
    title           = models.CharField(max_length=50, null=False, blank=False)
    body            = models.TextField(max_length=5000, null=False, blank=False)
    image           = models.ImageField(upload_to=upload_location, null=False, blank=False)
    date_published  = models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated   = models.DateTimeField(auto_now=True, verbose_name="date updated")
    author          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug            = models.SlugField(blank=True, unique=True)
    category        = models.CharField(max_length=255, default='coding')
    likes           = models.ManyToManyField(Account, related_name='blog_posts')

    def __str__(self):
        return self.title

class Comment(models.Model):
    blogpost = models.ForeignKey(BlogPost, related_name= "comment", on_delete=models.CASCADE)
    body = models.TextField()
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body
    

@receiver(post_delete, sender=BlogPost)
def submission_delete(sender, instance, **Kwargs):
    instance.image.delete(False)

def pre_save_blog_post_receiver(sender, instance, *args, **Kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.author.username + "-" + instance.title)

pre_save.connect(pre_save_blog_post_receiver, sender=BlogPost)
