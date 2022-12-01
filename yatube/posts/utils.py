from django.core.paginator import Paginator
from .constants import PER_PAGE as yatube_PER_PAGE


def page_numbers(queryset, request):
    paginator = Paginator(queryset, yatube_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
