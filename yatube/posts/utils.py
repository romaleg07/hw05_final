from django.conf import settings
from django.core.paginator import Paginator


def PostsPaginator(posts, request):
    paginator = Paginator(posts, settings.NUMBER_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
