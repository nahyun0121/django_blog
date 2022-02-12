from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
       #exclude = ('post', 'author', 'created_at', 'modified_at', ) 와 바로 위의 코드는 동일한 코드