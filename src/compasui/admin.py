from django.contrib import admin
from .models import CompasJob, Label, SingleBinaryJob, BasicParameter, AdvancedParameter


# Register your models here.

@admin.register(CompasJob)
class CompasJobAdmin(admin.ModelAdmin):
    pass


@admin.register(AdvancedParameter)
class AdvancedParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(BasicParameter)
class BasicParameterAdmin(admin.ModelAdmin):
    pass

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    pass


@admin.register(SingleBinaryJob)
class SingleBinaryJobAdmin(admin.ModelAdmin):
    pass
