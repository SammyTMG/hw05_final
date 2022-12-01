from django.shortcuts import render

NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500


def page_not_found(request, exception):
    return render(request,
                  'core/404.html',
                  {'path': request.path},
                  status=NOT_FOUND)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def server_error(request):
    return render(request, "core/500.html", status=INTERNAL_SERVER_ERROR)
