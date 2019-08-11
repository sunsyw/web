from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    # 默认返回 2条记录
    page_size = 2
    # 开启 page_size
    page_size_query_param = 'page_size'

    # max_page_size = 20