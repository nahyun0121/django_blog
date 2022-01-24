from django.db import models
import os


class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()


    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)     # upload_to에 이미지를 저장할 폴더의 경로 규칙 지정함. 연도 폴더, 월 폴더, 일 폴더까지 내려간 위치에 이미지 저장함. 'blank=True':해당 필드는 필수 항목 X.
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)       #처음 레코드가 생성될 때 현재 시각이 자동으로 저장됨
    updated_at = models.DateTimeField(auto_now=True)           #다시 저장할 때마다 그 시각이 저장됨
    #author: 추후 작성 예정


    def __str__(self):
        return f'[{self.pk}]{self.title}'   #pk: 각 레코드에 대한 고유값. 첫 번째 포스트는 pk값이 1, 두 번째 포스트는 pk값이 2..

    
    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]