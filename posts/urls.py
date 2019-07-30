from django.urls import path

from . import views

app_name = "posts"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.HistoryView.as_view(), name="history"),
    path("create/", views.CreateView.as_view(), name="create"),
    path("analytics/", views.analytics, name="analytics"),
    path("delete/<int:pk>/", views.DeleteView.as_view(), name="delete"),
    # path("analytics/", views.LineChartJSONView.as_view(), name="analytics"),
    path("analytics/testchart/json", views.LineChartJSONView.as_view(), name="analyticstestchartjson"),
]
