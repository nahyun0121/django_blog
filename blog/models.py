from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()


    created_at = models.DateTimeField(auto_now_add=True)       #처음 레코드가 생성될 때 현재 시각이 자동으로 저장됨
    updated_at = models.DateTimeField(auto_now=True)           #다시 저장할 때마다 그 시각이 저장됨
    #author: 추후 작성 예정


    def __str__(self):
        return f'[{self.pk}]{self.title}'   #pk: 각 레코드에 대한 고유값. 첫 번째 포스트는 pk값이 1, 두 번째 포스트는 pk값이 2..