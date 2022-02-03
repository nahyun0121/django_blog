from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag

# CBV방식으로 구현
class PostList(ListView):           # FBV 스타일의 index() 함수를 대체하는 PostList 클래스를 ListView 클래스를 상속하여 만듦. 'base.html'을 기본 템플릿으로 사용
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):                                                   # get_context_data 정의하여 오버라이딩
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

class PostDetail(DetailView):       # FBV 스타일의 single_post_page 함수를 대체하는 PostDetail 클래스. 'post_detail.html'을 기본 템플릿으로 사용
    model = Post

    def get_context_data(self, **kwargs):                                                   # get_context_data 정의하여 오버라이딩
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):                      # LoginRequiredMixin 클래스는 장고에서 제공하며, 로그인했을 때만 정상적으로 페이지를 보여줌.
    model = Post                                                                            # Post 모델을 사용한다고 model 변수에 선언함
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']     # Post 모델에 사용할 필드명을 리스트로 fields에 저장
    
    def test_func(self):                                                                    # 이 페이지에 접근 가능한 사용자는 최고 관리자 또는 스태프로 제한하는 함수
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):                                                             # CreateView에서 제공하는 form_valid()를 재정의하여 확장함.
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_supersuer):
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect('/blog/')

# FBV방식으로 category_page() 구현
def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)      # 포스트 중에서 카테고리가 없는 것만 가져온다.
    else:
        category = Category.objects.get(slug=slug)      # url에서 추출하여 category_page()의 인자로 받은 slug와 동일한 slug를 갖는 카테고리를 불러오는 쿼리셋을 만들어 category 변수에 저장한다.
        post_list = Post.objects.filter(category=category)      # 포스트 중에서 category와 동일한 카테고리만 가져온다.

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,                                                 # 포스트 중에서 바로 위에서 필터링한 카테고리만 가져온다.
            'categories': Category.objects.all(),                                   # 카테고리 카드를 채운다.
            'no_category_post_count': Post.objects.filter(category=None).count(),   # 미분류 포스트와 그 개수를 알려준다.
            'category': category,                                                   # 페이지 타이틀 옆에 카테고리 이름을 알려준다.
        }
    )

# FBV방식으로 tag_page() 구현
def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)                   # url에서 추출하여 tag_page()의 인자로 받은 slug와 동일한 slug를 갖는 태그를 불러오는 쿼리셋을 만들어 tag 변수에 저장한다.
    post_list = tag.post_set.all()                     # 그 태그에 연결된 포스트 전체를 post_list 변수에 저장한다.

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )


# FBV방식으로 구현
# def index(request):
#     posts = Post.objects.all().order_by('-pk')      #이 파일에서 데이터베이스에 쿼리를 날려 원하는 레코드 (pk 값의 역순으로 정렬되어) 가져오는 코드.


#     return render(
#         request,
#         'blog/base.html',
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