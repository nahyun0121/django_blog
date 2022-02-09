from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)                               # unique=True: 고유하다는 뜻. 동일한 name을 갖는 카테고리를 또 만들수 없음.
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)          # SlugField: 사람이 읽을 수 있는 텍스트로 고유 URL을 만들고 싶을 때 주로 사용.(한글 지원 X. 그래서 allow_unicode=True 씀)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:                                                                       # Category 모델의 메타 설정에서 verbose_name_plural로 복수형을 직접 지정함.
        verbose_name_plural = 'Categories'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)                               # unique=True: 고유하다는 뜻. 동일한 name을 갖는 카테고리를 또 만들수 없음.
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)          # SlugField: 사람이 읽을 수 있는 텍스트로 고유 URL을 만들고 싶을 때 주로 사용.(한글 지원 X. 그래서 allow_unicode=True 씀)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'


class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)     # upload_to에 이미지를 저장할 폴더의 경로 규칙 지정함. 연도 폴더, 월 폴더, 일 폴더까지 내려간 위치에 이미지 저장함. 'blank=True':해당 필드는 필수 항목 X.
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)                              # 처음 레코드가 생성될 때 현재 시각이 자동으로 저장됨
    updated_at = models.DateTimeField(auto_now=True)                                  # 다시 저장할 때마다 그 시각이 저장됨
    
    #author = models.ForeignKey(User, on_delete=models.CASCADE)                        # ForeignKey로 author 필드 구현. 한 포스트의 작성자가 데이터베이스에서 삭제되었을 때 그 포스트도 같이 삭제된다.
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)                        # 한 포스트의 작성자가 데이터베이스에서 삭제되었을 때 작성자명을 빈 칸으로 두겠다.(작성한 글은 남김)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)                                    # ManyToManyField는 기본적으로 null=True가 설정돼 있다.


    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'                            # pk: 각 레코드에 대한 고유값. 첫 번째 포스트는 pk값이 1, 두 번째 포스트는 pk값이 2..

    
    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):                                                   # Post 레코드의 content 필드에 저장돼 있는 텍스트를 마크다운 문법을 적용해 HTML로 변환함
        return markdown(self.content)