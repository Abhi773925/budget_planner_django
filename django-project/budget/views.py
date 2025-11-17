from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from datetime import datetime, date, timedelta
from .models import UserProfile, Category, Budget, Transaction, FinancialTip, SavingsGoal
from .forms import (
    CustomUserCreationForm, TransactionForm, BudgetForm, CategoryForm, 
    UserProfileForm, SavingsGoalForm, DateRangeForm
)


def landing_page(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get some sample statistics or features to display
    context = {
        'features': [
            {
                'icon': '📊',
                'title': 'Track Expenses',
                'description': 'Monitor your spending habits with detailed categorization and visual reports.'
            },
            {
                'icon': '💰',
                'title': 'Budget Management',
                'description': 'Set monthly budgets for different categories and get alerts when limits are reached.'
            },
            {
                'icon': '🎯',
                'title': 'Savings Goals',
                'description': 'Set and track your financial goals with progress monitoring and tips.'
            },
            {
                'icon': '📈',
                'title': 'Financial Reports',
                'description': 'Generate comprehensive reports to analyze your financial health over time.'
            }
        ]
    }
    return render(request, 'budget/landing.html', context)


def signup_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Create user profile
                UserProfile.objects.create(user=user)
                # Create default categories
                create_default_categories(user)
                login(request, user)
                messages.success(request, f'Welcome {user.first_name}! Your account has been created successfully.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, 'There was an error creating your account. Please try again.')
                print(f"Signup error: {e}")  # For debugging
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'budget/signup.html', {'form': form})


def create_default_categories(user):
    """Create default categories for new users"""
    default_categories = [
        # Expense categories
        {'name': 'Food & Dining', 'type': 'expense', 'icon': '🍽️', 'color': '#e74c3c'},
        {'name': 'Transportation', 'type': 'expense', 'icon': '🚗', 'color': '#f39c12'},
        {'name': 'Shopping', 'type': 'expense', 'icon': '🛍️', 'color': '#9b59b6'},
        {'name': 'Entertainment', 'type': 'expense', 'icon': '🎬', 'color': '#3498db'},
        {'name': 'Bills & Utilities', 'type': 'expense', 'icon': '💡', 'color': '#e67e22'},
        {'name': 'Healthcare', 'type': 'expense', 'icon': '🏥', 'color': '#1abc9c'},
        {'name': 'Education', 'type': 'expense', 'icon': '📚', 'color': '#34495e'},
        # Income categories
        {'name': 'Salary', 'type': 'income', 'icon': '💼', 'color': '#27ae60'},
        {'name': 'Freelance', 'type': 'income', 'icon': '💻', 'color': '#2ecc71'},
        {'name': 'Investment', 'type': 'income', 'icon': '📈', 'color': '#16a085'},
    ]
    
    for cat_data in default_categories:
        Category.objects.create(
            user=user,
            name=cat_data['name'],
            category_type=cat_data['type'],
            icon=cat_data['icon'],
            color=cat_data['color']
        )


@login_required
def dashboard(request):
    """Main dashboard view with enhanced financial insights"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Current month data
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get monthly totals - current month
    monthly_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # If no current month data, get last month's data for comparison
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1
    
    if monthly_income == 0 and monthly_expenses == 0:
        # Check if there's any data at all
        total_income = Transaction.objects.filter(
            user=request.user,
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_expenses = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # If there's historical data, use last month or recent data
        if total_income > 0 or total_expenses > 0:
            # Get last month's data
            monthly_income = Transaction.objects.filter(
                user=request.user,
                transaction_type='income',
                date__month=last_month,
                date__year=last_month_year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_expenses = Transaction.objects.filter(
                user=request.user,
                transaction_type='expense',
                date__month=last_month,
                date__year=last_month_year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # If still no data, get last 30 days
            if monthly_income == 0 and monthly_expenses == 0:
                thirty_days_ago = datetime.now() - timedelta(days=30)
                
                monthly_income = Transaction.objects.filter(
                    user=request.user,
                    transaction_type='income',
                    date__gte=thirty_days_ago
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                monthly_expenses = Transaction.objects.filter(
                    user=request.user,
                    transaction_type='expense',
                    date__gte=thirty_days_ago
                ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_savings = monthly_income - monthly_expenses
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date')[:5]
    
    # Budget overview - current month budgets
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    ).select_related('category')
    
    # Savings goals
    savings_goals = SavingsGoal.objects.filter(user=request.user)[:3]
    
    # Financial tips
    financial_tips = FinancialTip.objects.filter(is_active=True)[:3]
    
    # Calculate budget alerts
    budget_alerts = []
    for budget in budgets:
        if budget.percentage_used > 80:
            budget_alerts.append({
                'category': budget.category.name,
                'percentage': budget.percentage_used,
                'is_over': budget.is_over_budget,
                'over_amount': budget.over_budget_amount
            })
    
    # Enhanced financial health metrics
    savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
    expense_ratio = (monthly_expenses / monthly_income * 100) if monthly_income > 0 else 0
    
    # Additional financial insights
    total_transaction_count = Transaction.objects.filter(user=request.user).count()
    average_monthly_expense = monthly_expenses  # Could be enhanced with historical average
    
    # Financial health status
    if monthly_income > 0:
        if savings_rate >= 20:
            financial_status = "excellent"
            financial_message = "Excellent! You're saving over 20% of your income."
            financial_tip = "Consider increasing your emergency fund or investment contributions."
        elif savings_rate >= 10:
            financial_status = "good"
            financial_message = "Good progress! Try to increase savings to 20%."
            financial_tip = "Look for areas to reduce expenses and increase savings."
        elif monthly_savings >= 0:
            financial_status = "okay"
            financial_message = "You're saving money, but aim for at least 10% of income."
            financial_tip = "Create a budget to identify potential savings opportunities."
        else:
            financial_status = "warning"
            financial_message = "You're spending more than you earn this month."
            financial_tip = "Review your expenses and consider cutting non-essential spending."
    else:
        financial_status = "no_data"
        financial_message = "Add income and expense transactions to see your financial health."
        financial_tip = "Start by recording your monthly income and tracking daily expenses."
    
    context = {
        'profile': profile,
        'monthly_income': float(monthly_income),
        'monthly_expenses': float(monthly_expenses),
        'monthly_savings': float(monthly_savings),
        'savings_rate': round(savings_rate, 1),
        'expense_ratio': round(expense_ratio, 1),
        'financial_status': financial_status,
        'financial_message': financial_message,
        'financial_tip': financial_tip,
        'total_transaction_count': total_transaction_count,
        'recent_transactions': recent_transactions,
        'budgets': budgets,
        'savings_goals': savings_goals,
        'financial_tips': financial_tips,
        'budget_alerts': budget_alerts,
        'current_month': current_month,
        'current_year': current_year,
    }
    return render(request, 'budget/dashboard.html', context)


@login_required
def transaction_list(request):
    """List all transactions with filtering"""
    transactions = Transaction.objects.filter(user=request.user)
    filter_form = DateRangeForm(request.GET, user=request.user)
    
    if filter_form.is_valid():
        if filter_form.cleaned_data['start_date']:
            transactions = transactions.filter(date__gte=filter_form.cleaned_data['start_date'])
        if filter_form.cleaned_data['end_date']:
            transactions = transactions.filter(date__lte=filter_form.cleaned_data['end_date'])
        if filter_form.cleaned_data['category']:
            transactions = transactions.filter(category=filter_form.cleaned_data['category'])
        if filter_form.cleaned_data['transaction_type']:
            transactions = transactions.filter(transaction_type=filter_form.cleaned_data['transaction_type'])
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'budget/transaction_list.html', {
        'page_obj': page_obj,
        'filter_form': filter_form,
    })


@login_required
def add_transaction(request):
    """Add new transaction"""
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'budget/add_transaction.html', {'form': form})


@login_required
def edit_transaction(request, pk):
    """Edit existing transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    return render(request, 'budget/edit_transaction.html', {
        'form': form, 'transaction': transaction
    })


@login_required
def delete_transaction(request, pk):
    """Delete transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')
    return render(request, 'budget/confirm_delete.html', {
        'object': transaction, 'type': 'transaction'
    })


@login_required
def budget_overview(request):
    """Budget overview and management"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    ).select_related('category')
    
    # Calculate total budgeted vs spent
    total_budgeted = sum(budget.amount for budget in budgets)
    total_spent = sum(budget.spent_amount for budget in budgets)
    
    context = {
        'budgets': budgets,
        'current_month': current_month,
        'current_year': current_year,
        'total_budgeted': total_budgeted,
        'total_spent': total_spent,
        'total_remaining': total_budgeted - total_spent,
    }
    return render(request, 'budget/budget_overview.html', context)


@login_required
def create_budget(request):
    """Create new budget"""
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_overview')
    else:
        form = BudgetForm(user=request.user)
    return render(request, 'budget/create_budget.html', {'form': form})


@login_required
def edit_budget(request, pk):
    """Edit existing budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_overview')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    return render(request, 'budget/edit_budget.html', {
        'form': form, 'budget': budget
    })


@login_required
def delete_budget(request, pk):
    """Delete existing budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        category_name = budget.category.name
        budget.delete()
        messages.success(request, f'Budget for "{category_name}" deleted successfully!')
        return redirect('budget_overview')
    return render(request, 'budget/confirm_delete.html', {
        'object': budget,
        'object_type': 'Budget',
        'cancel_url': 'budget_overview'
    })


@login_required
def category_list(request):
    """List and manage categories"""
    categories = Category.objects.filter(user=request.user).order_by('category_type', 'name')
    return render(request, 'budget/category_list.html', {'categories': categories})


@login_required
def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'budget/add_category.html', {'form': form})


@login_required
def edit_category(request, pk):
    """Edit existing category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'budget/edit_category.html', {
        'form': form, 'category': category
    })


@login_required
def delete_category(request, pk):
    """Delete existing category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    # Check if category is being used in transactions or budgets
    transaction_count = category.transactions.count()
    budget_count = category.budgets.count()
    
    if request.method == 'POST':
        if transaction_count > 0 or budget_count > 0:
            messages.error(request, f'Cannot delete "{category.name}" because it is being used by {transaction_count} transactions and {budget_count} budgets.')
            return redirect('category_list')
        
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('category_list')
    
    return render(request, 'budget/confirm_delete.html', {
        'object': category,
        'object_type': 'Category',
        'cancel_url': 'category_list',
        'warning_message': f'This category has {transaction_count} transactions and {budget_count} budgets.' if (transaction_count > 0 or budget_count > 0) else None
    })


@login_required
def profile_view(request):
    """User profile management"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Get user statistics
    total_transactions = Transaction.objects.filter(user=request.user).count()
    total_categories = Category.objects.filter(user=request.user).count()
    total_budgets = Budget.objects.filter(user=request.user).count()
    
    context = {
        'form': form, 
        'profile': profile,
        'total_transactions': total_transactions,
        'total_categories': total_categories,
        'total_budgets': total_budgets,
    }
    return render(request, 'budget/profile.html', context)


@login_required
def reports_view(request):
    """Financial reports and analytics"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Monthly expense breakdown by category
    expense_by_category = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__month=current_month,
        date__year=current_year
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Monthly trends (last 6 months)
    monthly_trends = []
    for i in range(6):
        month = (current_month - i - 1) % 12 + 1
        year = current_year if current_month - i > 0 else current_year - 1
        
        income = Transaction.objects.filter(
            user=request.user,
            transaction_type='income',
            date__month=month,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            date__month=month,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_trends.append({
            'month': f"{month}/{year}",
            'income': float(income),
            'expenses': float(expenses),
            'savings': float(income - expenses)
        })
    
    # Top spending categories (last 3 months)
    three_months_ago = datetime.now() - timedelta(days=90)
    top_categories = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__gte=three_months_ago
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    context = {
        'expense_by_category': expense_by_category,
        'monthly_trends': list(reversed(monthly_trends)),
        'top_categories': top_categories,
    }
    return render(request, 'budget/reports.html', context)


@login_required
def savings_goals_view(request):
    """Display and manage savings goals"""
    savings_goals = SavingsGoal.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'savings_goals': savings_goals,
    }
    return render(request, 'budget/savings_goals.html', context)


@login_required
def add_savings_goal(request):
    """Add new savings goal"""
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            savings_goal = form.save(commit=False)
            savings_goal.user = request.user
            savings_goal.save()
            messages.success(request, 'Savings goal created successfully!')
            return redirect('savings_goals')
    else:
        form = SavingsGoalForm()
    return render(request, 'budget/add_savings_goal.html', {'form': form})


@login_required
def edit_savings_goal(request, pk):
    """Edit existing savings goal"""
    savings_goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=savings_goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Savings goal updated successfully!')
            return redirect('savings_goals')
    else:
        form = SavingsGoalForm(instance=savings_goal)
    return render(request, 'budget/edit_savings_goal.html', {
        'form': form, 'savings_goal': savings_goal
    })


@login_required
def delete_savings_goal(request, pk):
    """Delete existing savings goal"""
    savings_goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal_title = savings_goal.title
        savings_goal.delete()
        messages.success(request, f'Savings goal "{goal_title}" deleted successfully!')
        return redirect('savings_goals')
    return render(request, 'budget/confirm_delete.html', {
        'object': savings_goal,
        'object_type': 'Savings Goal',
        'cancel_url': 'savings_goals'
    })


# API Views for AJAX requests
@login_required
def expense_data_api(request):
    """API endpoint for expense chart data"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    expense_data = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__month=current_month,
        date__year=current_year
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    )
    
    if not expense_data:
        return JsonResponse({
            'labels': [],
            'data': [],
            'colors': [],
        })
    
    data = {
        'labels': [item['category__name'] for item in expense_data],
        'data': [float(item['total']) for item in expense_data],
        'colors': [item['category__color'] for item in expense_data],
    }
    return JsonResponse(data)


@login_required
def budget_progress_api(request):
    """API endpoint for budget progress data"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    )
    
    data = []
    for budget in budgets:
        data.append({
            'category': budget.category.name,
            'budgeted': float(budget.amount),
            'spent': float(budget.spent_amount),
            'percentage': budget.percentage_used,
            'over_budget': budget.is_over_budget,
        })
    
    return JsonResponse({'budgets': data})
