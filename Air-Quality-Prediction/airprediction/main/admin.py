from django.contrib import admin

# Register your models here.
from .models import Dataset, Dataset1, Dataset2, Dataset3, whole_dataset


# @admin.register(Dataset, Dataset1, Dataset2, Dataset3, whole_dataset)
# class ViewAdmin(admin.ModelAdmin):
#     pass

admin.site.register(Dataset)
admin.site.register(Dataset1)
admin.site.register(Dataset2)
admin.site.register(Dataset3)
admin.site.register(whole_dataset)


# @admin.register(Dataset)
# class DatasetAdmin(admin.ModelAdmin):
#     list_display = (
#         "date",
#         "Ozone",
#         "Pm25",
#     )


# @admin.register(Dataset1)
# class Dataset1Admin(admin.ModelAdmin):
#     list_display = (
#         "date",
#         "Ozone",
#         "Pm25",
#     )


# @admin.register(Dataset2)
# class Dataset2Admin(admin.ModelAdmin):
#     list_display = (
#         "date",
#         "Ozone",
#         "Pm25",
#     )


# @admin.register(Dataset3)
# class Dataset3Admin(admin.ModelAdmin):
#     list_display = (
#         "date",
#         "Ozone",
#         "Pm25",
#     )


# @admin.register(whole_dataset)
# class whole_datasetAdmin(admin.ModelAdmin):
#     list_display = (
#         "date",
#         "Ozone",
#         "Pm25",
#     )
