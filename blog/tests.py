from telnetlib import LOGOUT
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

# class TestView(TestCase):
#     def test_post_list(self):   # 'Test'로 시작하는 이름을 가진 클래스 안에 'test'로 시작하는 이름으로 함수를 정의함. => 테스트 코드를 작성할 때의 규칙!
#         self.assertEqual(2, 2)

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_kancho = User.objects.create_user(username='kancho', password='somepassword')         # 사용자 생성(이름, 패스워드까지 설정)
        self.user_jamna = User.objects.create_user(username='jamna', password='somepassword')
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