from conftest import posts_list

def test_posts_index(client):
    response = client.get("/posts")
    assert response.status_code == 200
    assert "Последние посты" in response.text

def test_posts_index_template(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/posts')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'posts.html'
        assert context['title'] == 'Посты'
        assert len(context['posts']) == 1

def test_post_template(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/posts/0')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'post.html'
        assert 'post' in context
        assert context['title'] == context['post']['title']

def test_post_content_display(client, posts_list):
    post = posts_list[0]
    response = client.get('/posts/0')
    assert post['title'] in response.text
    assert post['text'] in response.text
    assert post['author'] in response.text
    assert post['image_id'] in response.text

def test_post_date_format(client, posts_list):
    post = posts_list[0]
    response = client.get('/posts/0')
    expected_date = post['date'].strftime('%d.%m.%Y %H:%M')
    assert expected_date in response.text

def test_post_comments_display(client, posts_list):
    post = posts_list[0]
    response = client.get('/posts/0')
    for comment in post['comments']:
        assert comment['author'] in response.text
        assert comment['text'] in response.text

def test_post_comment_replies_display(client, posts_list):
    post = posts_list[0]
    response = client.get('/posts/0')
    for comment in post['comments']:
        if 'replies' in comment:
            for reply in comment['replies']:
                assert reply['author'] in response.text
                assert reply['text'] in response.text

def test_nonexistent_post_returns_404(client):
    response = client.get('/posts/999')
    assert response.status_code == 404

def test_post_image_display(client, posts_list):
    post = posts_list[0]
    response = client.get('/posts/0')
    assert f'static/images/{post["image_id"]}' in response.text

def test_comment_form_exists(client):
    response = client.get('/posts/0')
    assert 'Оставьте комментарий' in response.text
    assert 'textarea' in response.text
    assert 'Отправить' in response.text

def test_avatar_images_exist_in_comments(client):
    response = client.get('/posts/0')
    assert 'avatar.jpg' in response.text
    assert 'rounded-circle comment-image' in response.text

def test_post_content_justified(client):
    response = client.get('/posts/0')
    assert 'text-align: justify' in response.text

def test_all_posts_displayed_on_index(client, posts_list):
    response = client.get('/posts')
    posts = posts_list
    for post in posts:
        assert post['title'] in response.text

def test_post_metadata_display(client, posts_list):
    post = posts_list[0]
    response = client.get('/posts/0')
    assert f'{post["author"]}, {post["date"].strftime("%d.%m.%Y %H:%M")}' in response.text

def test_error_handler_404(client):
    """Проверка кастомной обработки 404 ошибки"""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert '404 Not Found' in response.text