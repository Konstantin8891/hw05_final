from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # Поля
    list_display = ('pk', 'text', 'created', 'author', 'group')
    # поиск по тексту постов
    search_fields = ('text',)
    # фильтрация по дате
    list_filter = ('created', 'group',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
