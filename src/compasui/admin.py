from django.contrib import admin
from .models import CompasJob, DataParameter, Label, SearchParameter, Data, Search, SingleBinaryJob


# Register your models here.


class InlineDataAdmin(admin.TabularInline):
    model = Data


class InlineSearchAdmin(admin.TabularInline):
    model = Search


class InlineDataParameterAdmin(admin.TabularInline):
    model = DataParameter


class InlineSearchParameterAdmin(admin.TabularInline):
    model = SearchParameter


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    fields = ['job', 'data_source', 'source_dataset']
    inlines = (InlineDataParameterAdmin,)


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    fields = ['job']
    inlines = (InlineSearchParameterAdmin,)


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    fields = ['name', 'description']


@admin.register(CompasJob)
class CompasJobAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'private', 'job_controller_id', 'labels']
    filter_horizontal = ('labels',)
    readonly_fields = ('creation_time', 'last_updated')
    inlines = (
        InlineDataAdmin,
        InlineSearchAdmin,
        InlineDataParameterAdmin,
        InlineSearchParameterAdmin
    )


@admin.register(SingleBinaryJob)
class SingleBinaryJobAdmin(admin.ModelAdmin):
    pass
