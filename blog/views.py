from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.core.exceptions import PermissionDenied


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
        context['comment_form'] = CommentForm
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):                      # LoginRequiredMixin 클래스는 장고에서 제공하며, 로그인했을 때만 정상적으로 페이지를 보여줌.
    model = Post                                                                            # Post 모델을 사용한다고 model 변수에 선언함
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']     # Post 모델에 사용할 필드명을 리스트로 fields에 저장
    
    def test_func(self):                                                                    # 이 페이지에 접근 가능한 사용자는 최고 관리자 또는 스태프로 제한하는 함수
        return self.request.user.is_superuser or self.request.user.is_staff

    # 방문자가 폼에 담아 보낸 유효한 정보를 사용해 포스트를 만들고, 이 포스트의 고유 경로로 보내주는(redirect) 함수. CreateView에서 제공한다.
    def form_valid(self, form):                                                             # form_valid()를 재정의하여 확장함.
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)                             # 태그 관련 작업 전에 form_valid()의 결괏값을 response라는 변수에 임시로 저장

            tags_str = self.request.POST.get('tags_str')                                    # POST 방식으로 전달된 정보 중 name='tags_str'인 input의 값을 가져와 tags_str에 저장
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')                                             # tags_str로 받은 값을 세미콜론으로 split하여 리스트 형태로 tags_list에 담음.

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)                 # get_or_create()는 Tag 모델의 인스턴스와, 그 인스턴스가 새로 생성되었는지 나타내는 bool 형태의 값을 return한다.
                    if is_tag_created:                                                      # 태그가 새로 만들어졌다면, slug가 자동으로 생기지 못했을 것이므로 (한글 태그여도) slugify()로 slug를 만들어 준다.
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)                                               # 새로 만든 포스트(self.object)의 tags 필드에 태그를 추가한다.

            return response                                                                 # 작업이 다 끝나면 새로 만든 포스트의 페이지로 이동한다.
        else:
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'                                            # 원하는 html 파일을 템플릿 파일로 설정함. (기본은 '_form.html')

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)                          # 리스트의 값들을 세미콜론으로 결합하여 하나의 문자열로 만든 후 context['tags_str_default']에 담는다.

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:      # 방문자가 로그인한 상태이며 Post 인스턴스의 author 필드와 동일한 경우에만 dispatch() 메서드가 원래 역할을 함.
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:                                                                               # 그렇지 않을 경우 권한이 없음을 나타냄.
            raise PermissionDenied

    def form_valid(self, form):                                                             # form_valid()를 재정의하여 확장함.
        response = super(PostUpdate, self).form_valid(form)                             # 태그 관련 작업 전에 form_valid()의 결괏값을 response라는 변수에 임시로 저장
        self.object.tags.clear()                                                            # self.object로 가져온 포스트의 태그를 모두 삭제한다.

        tags_str = self.request.POST.get('tags_str')                                    # POST 방식으로 전달된 정보 중 name='tags_str'인 input의 값을 가져와 tags_str에 저장
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')                                             # tags_str로 받은 값을 세미콜론으로 split하여 리스트 형태로 tags_list에 담음.

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)                 # get_or_create()는 Tag 모델의 인스턴스와, 그 인스턴스가 새로 생성되었는지 나타내는 bool 형태의 값을 return한다.
                if is_tag_created:                                                      # 태그가 새로 만들어졌다면, slug가 자동으로 생기지 못했을 것이므로 (한글 태그여도) slugify()로 slug를 만들어 준다.
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)                                               # 새로 만든 포스트(self.object)의 tags 필드에 태그를 추가한다.

        return response                                                                 # 작업이 다 끝나면 새로 만든 포스트의 페이지로 이동한다.
    

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):                                       # 웹 사이트 방문자의 요청이 GET인지 POST인지 판단하는 함수
        if request.user.is_authenticated and request.user == self.get_object().author:  # 판단하기 전 다른 사용자의 댓글 해킹 방지
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

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


# FBV방식으로 new_comment() 구현
def new_comment(request, pk):
    if request.user.is_authenticated:                   
        post = get_object_or_404(Post, pk=pk)               # 해당 pk가 없는 경우 404 오류를 발생시킨다.


        if request.method == 'POST':                        # 폼을 작성한 후 <submit> 버튼을 눌러 POST 방식으로 서버에 요청되면,
            comment_form = CommentForm(request.POST)        # 정상적으로 폼을 작성하고 POST 방식으로 서버에 요청이 들어왔다면 그 정보를 CommentForm 형태로 가져온다.
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)   # 해당 내용으로 새로운 레코드를 만들기 전, 저장은 일단 미룸
                comment.post = post                         # post 필드는 pk로 가져온 포스트로 채우고,
                comment.author = request.user               # author 필드는 로그인한 사용자 정보로 채운다.
                comment.save()                              # 이 작업이 모두 끝나면 저장한다.
                return redirect(comment.get_absolute_url())
        else:                                               # GET 방식으로 서버에 요청하게 되면, pk=숫자인 포스트 페이지로 리다이렉트 됨.
            return redirect(post.get_absolute_url())
    else:                                                   # 로그인하지 않은 경우 PermissionDenied 발생시킨다.
        raise PermissionDenied


# FBV방식으로 delete_comment() 구현
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


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