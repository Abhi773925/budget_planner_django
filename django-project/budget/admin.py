from django.contrib import admin
from .models import UserProfile, Category, Budget, Transaction, FinancialTip, SavingsGoal


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'monthly_income', 'savings_goal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'user', 'icon', 'color']
    list_filter = ['category_type', 'created_at']
    search_fields = ['name', 'user__username']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'month', 'year', 'percentage_used']
    list_filter = ['month', 'year', 'category__category_type']
    search_fields = ['user__username', 'category__name']
    
    def percentage_used(self, obj):
        return f"{obj.percentage_used:.1f}%"
    percentage_used.short_description = 'Used %'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'description', 'category', 'amount', 'transaction_type', 'date']
    list_filter = ['transaction_type', 'category', 'date']
    search_fields = ['description', 'user__username', 'category__name']
    date_hierarchy = 'date'


@admin.register(FinancialTip)
class FinancialTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'is_active', 'created_at']
    list_filter = ['priority', 'is_active']
    search_fields = ['title', 'content']


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'target_amount', 'current_amount', 'progress_percentage', 'target_date']
    list_filter = ['target_date', 'created_at']
    search_fields = ['title', 'user__username']
    
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage:.1f}%"
    progress_percentage.short_description = 'Progress %'
