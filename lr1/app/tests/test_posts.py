def test_posts_index(client):
    response = client.get("/posts")
    assert response.status_code == 200
    assert "Последние посты" in response.text

def test_posts_index_template(client, captured_templates, mocker, posts_list):
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )

        _ = client.get('/posts')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'posts.html'
        assert context['title'] == 'Посты'
        assert len(context['posts']) == 1

def test_post_page_template(client, captured_templates, mocker, posts_list):
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )

        response = client.get('/posts/0')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'post.html'

def test_post_page_context_data(client, captured_templates, mocker, posts_list):
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )

        response = client.get('/posts/0')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]

        assert 'title' in context
        assert 'post' in context
        assert context['title'] == posts_list[0]['title']
        assert context['post'] == posts_list[0]

def test_post_page_title_display(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert posts_list[0]['title'] in response.text

def test_post_page_author_display(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert posts_list[0]['author'] in response.text

def test_post_page_text_display(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert posts_list[0]['text'] in response.text

def test_post_page_image_display(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert posts_list[0]['image_id'] in response.text

def test_post_page_date_format(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200

    assert "10.03.2025 в 14:30" in response.text

def test_post_page_comment_form(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Оставьте комментарий" in response.text
    assert '<textarea' in response.text
    assert 'Отправить' in response.text

def test_post_page_comments_display(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Петров Петр" in response.text
    assert "Отличный пост!" in response.text

def test_post_page_replies_display(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Сидоров Сидор" in response.text
    assert "Согласен!" in response.text

def test_post_page_no_comments_message(client, mocker, posts_list_no_comments):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list_no_comments,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Пока нет комментариев" in response.text

def test_post_page_comments_count(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Комментарии (1)" in response.text

def test_post_page_navigation_links(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert 'href="/"' in response.text or 'href="/index"' in response.text
    assert 'href="/posts"' in response.text
    assert 'href="/about"' in response.text

def test_post_invalid_index_404(client, mocker):
    mocker.patch(
        "app.posts_list",
        return_value=[],
        autospec=True
    )

    response = client.get('/posts/99')
    assert response.status_code == 404

def test_post_negative_index_404(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/-1')
    assert response.status_code == 404

def test_post_page_sidebar_present(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "О блоге" in response.text
    assert "Навигация" in response.text

def test_post_page_footer_present(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Гудяков Олег Артёмович" in response.text
    assert "ИВТ-б-о-23" in response.text
