from telnetlib import LOGOUT
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment

# class TestView(TestCase):
#     def test_post_list(self):   # 'Test'로 시작하는 이름을 가진 클래스 안에 'test'로 시작하는 이름으로 함수를 정의함. => 테스트 코드를 작성할 때의 규칙!
#         self.assertEqual(2, 2)

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_kancho = User.objects.create_user(username='kancho', password='somepassword')         # 사용자 생성(이름, 패스워드까지 설정)
        self.user_jamna = User.objects.create_user(username='jamna', password='somepassword')
        self.user_kancho.is_staff = True                                                                # 사용자 '칸쵸'는 스태프!
        self.user_kancho.save()
        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_daily = Category.objects.create(name='daily', slug='daily')
        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')


        # 3.1 게시물이 3개 있다면
        self.post_001 = Post.objects.create(                           # Post 레코드가 데이터베이스에 존재하는 상황도 테스트하기 위해 새로운 포스트를 만든다.
            title = '첫 번째 포스트입니다.',                            # 매개변수에는 Post 모델의 필드 값을 넣음.
            content = "기다렸어 어서와. 어디든 We're coming together.",
            category = self.category_programming,
            author = self.user_kancho
        )
        self.post_001.tags.add(self.tag_hello)                         # 이미 만들어진 첫 번째 포스트에 태그를 추가함.(ManyToManyField는 여러 개의 레코드를 연결할 수 있기 때문.)

        self.post_002 = Post.objects.create(
            title = '두 번째 포스트입니다.',
            content = '아무 걱정 하지 마, 잘 될 거야 Hello future.',
            category = self.category_daily,
            author = self.user_jamna
        )
        # 세 번째 게시물은 카테고리가 없다.
        self.post_003 = Post.objects.create(
            title = '세 번째 포스트입니다.',
            content = '너를 만나 같이 더 빛나.',
            author = self.user_kancho
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

        # 잠나가 첫 번째 게시물에 댓글을 남긴다.
        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_jamna,
            content='NCT DREAM - Hello Future'
        )


    def category_card_test(self, soup):
            categories_card = soup.find('div', id='categories-card')
            self.assertIn('Categories', categories_card.text)
            self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
            self.assertIn(f'{self.category_daily.name} ({self.category_daily.post_set.count()})', categories_card.text)
            self.assertIn(f'미분류 (1)', categories_card.text)


    def navbar_test(self, soup):                                       # 내비게이션 바를 점검하는 함수
        # 내비게이션 바가 있다.
        navbar = soup.nav                                              # soup에 담긴 내용 중 nav 요소만 가져와 navbar에 저장.
        # Blog, About me라는 문구가 내비게이션 바에 있다.
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)                         # navbar의 텍스트 중 Blog와 About Me가 있는지 확인함.

        logo_btn = navbar.find('a', text='NA NA LAND')                 # 'NA NA LAND' 버튼 점검 코드. 'NA NA LAND'라는 문구를 가진 a 요소를 찾아 logo_btn 변수에 담는다.
        self.assertEqual(logo_btn.attrs['href'], '/')                  # a 요소에서 href 속성을 찾아 값이 '/'인지 확인.

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')


    def test_post_list(self):
        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)                           # 포스트 3개가 잘 있는지 확인

        response = self.client.get('/blog/')                                # 테스트를 위한 가상의 사용자(client)가 웹 브라우저에 '~~/blog/'를 입력할 때 열리는 웹 페이지의 정보를 response에 저장함.
        self.assertEqual(response.status_code, 200)                         # 서버에서 요청한 페이지를 성공적으로 찾았을 때 status_code 값으로 200을 보내줌. (실패시 404)
        soup = BeautifulSoup(response.content, 'html.parser')               # 불러운 페이지의 내용(HTML로 구성됨)에 쉽게 접근하기 위해 BeautifulSoup으로 읽어들인 후, 파싱한 결과를 soup에 담음.

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id = 'main-area')                      # id가 main-area인 div 요소를 찾아 main_area에 저장.
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)           # 데이터베이스에 저장된 Post 레코드가 3개 있으므로 메인 영역에 '아직 게시물이 없습니다'가 안 나타나는지 점검.

        # id가 post-1인 div 요소룰 main_area에서 찾아 post_001_card에 담은 후, 그 안에 첫 번째 게시물의 제목, 카테고리 이름, 알맞은 태그 이름이 잘 있는지 확인.
        post_001_card = main_area.find('div', id = 'post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id = 'post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id = 'post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        # 메인 영역에서 작성자명으로 kancho와 jamna가 나온다. 작성자명은 대문자로 표기된다.
        self.assertIn(self.user_jamna.username.upper(), main_area.text)
        self.assertIn(self.user_kancho.username.upper(), main_area.text)


        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id = 'main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)


    def test_post_detail(self):
        
        # 1.2 미리 만들어둔 첫 번째 포스트의 url은 '/blog/1/'이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200).
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2 포스트 목록 페이지와 똑같은 내비게이션 바와 카테고리 카드가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)
        # 2.3. 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)
        # 2.4. 첫 번째 포스트의 제목이 포스트 영역에 있고, 포스트의 카테고리 이름인 'programming'이 post_area에 들어 있다.
        main_area = soup.find('div', id='main-area')                                    
        post_area = main_area.find('div', id='post-area')                                   # 메인 영역에서 포스트 영역만 불러옴.
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)
        # 2.5. 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다.
        self.assertIn(self.user_kancho.username.upper(), post_area.text)
        # 2.6. 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)
        # 2.7. 첫 번째 포스트의 태그(tag)가 포스트 영역에 있다.
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
        # 2.8 첫 번째 포스트의 댓글 작성자(jamna)와 댓글 내용이 포스트 영역에 있다.
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)


    def test_category_page(self):
        # 카테고리 programming 페이지의 고유 URL로 접근하면 정상적으로 작동한다.
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # beautifulsoup4로 HTML를 다루기 쉽게 파싱한 후, 내비게이션 바와 카테고리 카드가 잘 구성되어 있는지 확인한다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 페이지 상단에 카테고리 뱃지가 잘 나타나는지 확인한다.(이 페이지에서는 <h2> 태그를 한 번만 쓰므로 <h2>에 카테고리 이름이 있는지 확인)
        self.assertIn(self.category_programming.name, soup.h2.text)

        # 메인 영역에서 카테고리 programming이 있는지 확인하고, 이 카테고리에 해당하는 포스트만 노출되어 있는지 확인한다.
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)


    def test_tag_page(self):
        # setUp() 함수에서 만든 태그 중 name 필드가 'hello'인 페이지의 고유 URL로 접근하면 정상 작동 확인 및 HTML 파싱하기
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    
    def test_create_post(self):
        # 로그인하지 않으면 status code가 200이면 안 된다!
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 jamna가 로그인을 하여 포스트 생성을 하지 못 한다.
        self.client.login(username='jamna', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 kancho로 로그인을 한다.
        self.client.login(username='kancho', password='somepassword')

        # /blog/create_post/라는 URL로 방문자가 접근하면 포스트 작성 페이지가 정상적으로 열리는지 확인 후 HTML 파싱한다.
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        # 포스트 작성 페이지의 main_area에 id='id_tags_str'인 input이 존재하는지 확인한다.
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        # self.client.post()를 이용하여 첫 번째 인수인 해당 경로로 두 번째 인수인 딕셔너리 정보를 POST 방식으로 보낸다.
        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': "Post Form 페이지를 만듭시다.",
                'tags_str': 'new tag; 한글 태그, python'
            }
        )
        
        # 새로 만들어진 포스트를 합친 4개의 포스트가 잘 만들어졌는지 확인 후, 가장 최신 포스트의 제목과 작성자가 똑바른지 확인한다.
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'kancho')

        # 가장 최신 포스트에 태그가 3개인 것을 확인하고, 새로운 두 태그를 데이터베이스에 등록한 후 태그의 종류가 총 5개가 되었는지 확인한다.
        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)


    # 세 번째 포스트를 수정하는 함수
    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인 하지 않은 경우 접근 불가능
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만 작성자가 아닌 경우(jamna)도 접근 불가능
        self.assertNotEqual(self.post_003.author, self.user_jamna)
        self.client.login(
            username = self.user_jamna.username,
            password = 'somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자(kancho)가 접근하는 경우 수정 페이지가 제대로 열리고 HTML 파싱하여 soup에 저장한다.
        self.client.login(
            username = self.post_003.author.username,
            password = 'somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        # 메인 영역에 id_tags_str이라는 id를 가진 input이 있는지 확인하고 input에 self.post_003의 태그가 들어 있는지 확인한다.
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'])

        # 제대로 'Edit Post'가 나오면, title, content, category, tags_str 값을 수정한 다음 Post 방식으로 update_post_url에 날린다.
        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다.',
                'content': '아름다운 시간만 쌓자.',
                'category': self.category_daily.pk,
                'tags_str': '파이썬 공부; 한글 태그, some tag'
            },
            follow = True
        )
        # 4가지가 잘 바뀌었는지 다시 확인해본다.
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('아름다운 시간만 쌓자.', main_area.text)
        self.assertIn(self.category_daily.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text) 
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)   

    
    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)                       # setUp()에 이미 댓글이 하나 있는 상태
        self.assertEqual(self.post_001.comment_set.count(), 1)             # 이 댓글은 첫 번째 포스트에 달려 있다.

        # 로그인하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Join NANALAND and leave a comment!', comment_area.text)
        self.assertFalse(comment_area.find('form', id='comment-form'))     # 로그인하지 않은 상태이므로 id가 comment-form인 form요소 존재 X

        # 로그인한 상태
        self.client.login(username='kancho', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Join NANALAND and leave a comment!', comment_area.text)

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content'))    # 로그인한 상태이므로 댓글 폼이 보이고, 그 안에 textarea도 있다.
        response = self.client.post(
            self.post_001.get_absolute_url() + 'new_comment/',
            {
                'content': "칸쵸의 댓글입니다.",
            },
            follow=True                                                    # POST로 보내는 경우 서버에서 처리한 후 리다이렉트되는데, 이때 따라가도록 하는 역할
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 2)                       # 댓글이 하나 더 추가됐으므로 전체 댓글 개수는 2개이다.
        self.assertEqual(self.post_001.comment_set.count(), 2)             # 이제 첫 번째 포스트에 댓글이 2개이다.

        new_comment = Comment.objects.last()

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title, soup.title.text)             # 웹 브라우저의 타이틀로 새로 만든 댓글이 달린 포스트의 타이틀이 나타난다.

        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('kancho', new_comment_div.text)
        self.assertIn('칸쵸의 댓글입니다.', new_comment_div.text)





