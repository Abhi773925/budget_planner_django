from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='budget/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # Main app URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    
    path('budget/', views.budget_overview, name='budget_overview'),
    path('budget/create/', views.create_budget, name='create_budget'),
    path('budget/edit/<int:pk>/', views.edit_budget, name='edit_budget'),
    path('budget/delete/<int:pk>/', views.delete_budget, name='delete_budget'),
    
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    
    path('profile/', views.profile_view, name='profile'),
    path('reports/', views.reports_view, name='reports_view'),
    
    path('savings-goals/', views.savings_goals_view, name='savings_goals'),
    path('savings-goals/add/', views.add_savings_goal, name='add_savings_goal'),
    path('savings-goals/edit/<int:pk>/', views.edit_savings_goal, name='edit_savings_goal'),
    path('savings-goals/delete/<int:pk>/', views.delete_savings_goal, name='delete_savings_goal'),
    
    # AJAX URLs for dynamic content
    path('api/expense-data/', views.expense_data_api, name='expense_data_api'),
    path('api/budget-progress/', views.budget_progress_api, name='budget_progress_api'),
]