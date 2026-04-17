from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',                    views.home,           name='home'),
    path('add/',                views.add_expense,    name='add_expense'),
    path('edit/<int:id>/',      views.edit_expense,   name='edit_expense'),
    path('delete/<int:id>/',    views.delete_expense, name='delete_expense'),
    path('export/csv/',         views.export_csv,     name='export_csv'),
    path('budget/set/',         views.set_budget,     name='set_budget'),
    path('clear/',              views.clear_all_expenses, name='clear_all'),
      path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Forgot password (Django built-in)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]