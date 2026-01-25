from rest_framework.pagination import PageNumberPagination


class LessonPagination(PageNumberPagination):
    page_size = 5  # Количество уроков на странице
    page_size_query_param = "page_size"
    max_page_size = 50  # Максимальное количество на странице


class CoursePagination(PageNumberPagination):
    page_size = 2  # Количество курсов на странице
    page_size_query_param = "page_size"
    max_page_size = 20  # Максимальное количество на странице
