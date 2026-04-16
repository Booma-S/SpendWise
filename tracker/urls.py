from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.home,           name='home'),
    path('add/',                views.add_expense,    name='add_expense'),
    path('edit/<int:id>/',      views.edit_expense,   name='edit_expense'),
    path('delete/<int:id>/',    views.delete_expense, name='delete_expense'),
    path('export/csv/',         views.export_csv,     name='export_csv'),
    path('budget/set/',         views.set_budget,     name='set_budget'),
    path('clear/',              views.clear_all_expenses, name='clear_all'),
]