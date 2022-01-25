from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# class TestView(TestCase):
#     def test_post_list(self):   # 'Test'로 시작하는 이름을 가진 클래스 안에 'test'로 시작하는 이름으로 함수를 정의함. => 테스트 코드를 작성할 때의 규칙!
#         self.assertEqual(2, 2)

class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_list(self):
        # 1.1 포스트 목록 페이지를 가져온다.
        response = self.client.get('/blog/')                           # 테스트를 위한 가상의 사용자(client)가 웹 브라우저에 '~~/blog/'를 입력할 때 열리는 웹 페이지의 정보를 response에 저장함.
        # 1.2 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)                    # 서버에서 요청한 페이지를 성공적으로 찾았을 때 status_code 값으로 200을 보내줌. (실패시 404)
        # 1.3 페이지 타이틀은 'Blog'이다.
        soup = BeautifulSoup(response.content, 'html.parser')          # 불러온 페이지의 내용(HTML로 구성됨)에 쉽게 접근하기 위해 BeautifulSoup으로 읽어들인 후, 파싱한 결과를 soup에 담음.
        self.assertEqual(soup.title.text, 'Blog')                      # title 요소에서 텍스트만 가져와 Blog인지 확인.
        # 1.4 내비게이션 바가 있다.
        navbar = soup.nav                                              # soup에 담긴 내용 중 nav 요소만 가져와 navbar에 저장.
        # 1.5 Blog, About Me라는 문구가 내비게이션 바에 있다.
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)                         # navbar의 텍스트 중 Blog와 About Me가 있는지 확인함.

        # 2.1 메인 영역에 게시물이 하나도 없다면
        self.assertEqual(Post.objects.count(), 0)                      # 작성된 포스트가 0개인지 확인함. 테스트가 시작되면 테스트를 위한 새 데이터베이스를 임시로 만드는데, setUp()에서 설정한 요소는 포함시킨다.(테스트를 위한 새 데이터베이스에 어떤 정보도 담아놓으라는 말이 없음) -> 테스트 데이터베이스에는 현재 포스트가 하나도 없어야 함!
        # 2.2 '아직 게시물이 없습니다'라는 문구가 보인다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)         # id가 main-area인 div 요소를 찾아 main_area에 저장함. 그리고 (데이터베이스에 저장된 Post 레코드가 없으니) 메인 영역에 '아직 게시물이 없습니다'라는 문구가 나타나는지 점검.

        # 3.1 게시물이 2개 있다면
        post_001 = Post.objects.create(                                # Post 레코드가 데이터베이스에 존재하는 상황도 테스트하기 위해 새로운 포스트를 만든다.
            title = '첫 번째 포스트입니다.',                            # 매개변수에는 Post 모델의 필드 값을 넣음.
            content = "기다렸어 어서와. 어디든 We're coming together.",
        )
        post_002 = Post.objects.create(
            title = '두 번째 포스트입니다.',
            content = '아무 걱정 하지 마, 잘 될 거야 Hello future.',
        )
        self.assertEqual(Post.objects.count(), 2)                      # 테스트 데이터베이스에 포스트 2개가 잘 생성되어 있는지 확인.

        # 3.2 포스트 목록 페이지를 새로고침했을 때
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        # 3.3 메인 영역에 포스트 2개의 타이틀이 존재한다.
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        # 3.4 '아직 게시물이 없습니다'라는 문구는 더 이상 보이지 않는다.
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)