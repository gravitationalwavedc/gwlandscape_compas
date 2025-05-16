from django.contrib import admin
from .models import Keyword, CompasPublication, CompasModel, CompasDatasetModel


# Register your models here.


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    pass


@admin.register(CompasPublication)
class CompasPublicationAdmin(admin.ModelAdmin):
    pass


@admin.register(CompasModel)
class CompasModelAdmin(admin.ModelAdmin):
    pass


@admin.register(CompasDatasetModel)
class CompasDatasetAdmin(admin.ModelAdmin):
    pass
