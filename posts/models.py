from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-pub_date"]

    def was_important(self):
        return self.title != "*"
