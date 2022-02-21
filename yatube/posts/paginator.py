from django.core.paginator import Paginator

from yatube.settings import POST_AMOUNT


def paginator_method(request, posts):
    # показывать post_amount постов
    paginator = Paginator(posts, POST_AMOUNT)
    # извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # получаем набор записей для страницы с запрошенным номером
    return paginator.get_page(page_number)
