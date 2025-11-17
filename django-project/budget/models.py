from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import datetime


class UserProfile(models.Model):
    """Extended user profile for budget planning"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    monthly_income = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    savings_goal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def current_month_expenses(self):
        """Calculate total expenses for current month"""
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        return self.user.transactions.filter(
            date__month=current_month,
            date__year=current_year,
            transaction_type='expense'
        ).aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def current_month_income(self):
        """Calculate total income for current month"""
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        return self.user.transactions.filter(
            date__month=current_month,
            date__year=current_year,
            transaction_type='income'
        ).aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def current_savings(self):
        """Calculate current savings (income - expenses)"""
        return self.current_month_income - self.current_month_expenses


class Category(models.Model):
    """Expense and income categories"""
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, default='💰')  # Emoji icon
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ['name', 'user', 'category_type']

    def __str__(self):
        return f"{self.name} ({self.category_type})"

    @property
    def current_month_total(self):
        """Total amount for this category in current month"""
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        return self.transactions.filter(
            date__month=current_month,
            date__year=current_year
        ).aggregate(total=models.Sum('amount'))['total'] or 0


class Budget(models.Model):
    """Monthly budget for different categories"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    month = models.PositiveIntegerField()  # 1-12
    year = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'category', 'month', 'year']

    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.month}/{self.year})"

    @property
    def spent_amount(self):
        """Amount spent in this category for the budget period"""
        return self.category.transactions.filter(
            date__month=self.month,
            date__year=self.year,
            user=self.user,
            transaction_type='expense'
        ).aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def remaining_amount(self):
        """Remaining budget amount"""
        return self.amount - self.spent_amount

    @property
    def percentage_used(self):
        """Percentage of budget used"""
        if self.amount == 0:
            return 0
        return min((self.spent_amount / self.amount) * 100, 100)

    @property
    def is_over_budget(self):
        """Check if spending exceeds budget"""
        return self.spent_amount > self.amount

    @property
    def over_budget_amount(self):
        """Amount over budget (positive if over, 0 if under)"""
        if self.is_over_budget:
            return self.spent_amount - self.amount
        return 0


class Transaction(models.Model):
    """Income and expense transactions"""
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} - ${self.amount} ({self.date})"

    def save(self, *args, **kwargs):
        # Ensure transaction_type matches category type
        self.transaction_type = self.category.category_type
        super().save(*args, **kwargs)


class FinancialTip(models.Model):
    """Financial tips and recommendations"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title

    def get_priority_color(self):
        """Get Bootstrap color class for priority"""
        colors = {
            'low': 'info',
            'medium': 'warning', 
            'high': 'danger'
        }
        return colors.get(self.priority, 'secondary')


class SavingsGoal(models.Model):
    """User's savings goals"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    title = models.CharField(max_length=200)
    target_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    current_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    target_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - ${self.target_amount}"

    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.target_amount == 0:
            return 0
        return min((self.current_amount / self.target_amount) * 100, 100)

    @property
    def is_completed(self):
        """Check if goal is completed"""
        return self.current_amount >= self.target_amount

    @property
    def days_remaining(self):
        """Days remaining to reach target date"""
        today = datetime.date.today()
        if self.target_date <= today:
            return 0
        return (self.target_date - today).days
