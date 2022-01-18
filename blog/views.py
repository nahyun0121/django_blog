# from django.shortcuts import render
from django.views.generic import ListView, DetailView 
from .models import Post

# CBV방식으로 구현
class PostList(ListView):           # FBV 스타일의 index() 함수를 대체하는 PostList 클래스를 ListView 클래스를 상속하여 만듦. 'post_list.html'을 기본 템플릿으로 사용
    model = Post
    ordering = '-pk'

class PostDetail(DetailView):       # FBV 스타일의 single_post_page 함수를 대체하는 PostDetail 클래스. 'post_detail.html'을 기본 템플릿으로 사용
    model = Post


# FBV방식으로 구현
# def index(request):
#     posts = Post.objects.all().order_by('-pk')      #이 파일에서 데이터베이스에 쿼리를 날려 원하는 레코드 (pk 값의 역순으로 정렬되어) 가져오는 코드.


#     return render(
#         request,
#         'blog/post_list.html',
#         {
#             'posts': posts,
#         }
#     )

# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)      # Post.objects.get(): 괄호 안의 조건을 만족하는 Post 레코드를 가져오라

#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'post': post,
#         }
#     )