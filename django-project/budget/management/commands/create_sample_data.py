from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from budget.models import UserProfile, Category, Transaction, Budget, FinancialTip, SavingsGoal
from decimal import Decimal
from datetime import date, datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample data for the budget planner'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create or get demo user
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'is_active': True,
            }
        )
        
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(f'Created demo user: demo/demo123')
        
        # Create or update user profile
        profile, created = UserProfile.objects.get_or_create(
            user=demo_user,
            defaults={
                'monthly_income': Decimal('5000.00'),
                'savings_goal': Decimal('1000.00'),
            }
        )
        
        # Create sample categories if they don't exist
        categories_data = [
            # Income categories
            {'name': 'Salary', 'type': 'income', 'icon': '💼', 'color': '#28a745'},
            {'name': 'Freelance', 'type': 'income', 'icon': '💻', 'color': '#17a2b8'},
            {'name': 'Investment Returns', 'type': 'income', 'icon': '📈', 'color': '#20c997'},
            
            # Expense categories
            {'name': 'Food & Dining', 'type': 'expense', 'icon': '🍽️', 'color': '#dc3545'},
            {'name': 'Transportation', 'type': 'expense', 'icon': '🚗', 'color': '#fd7e14'},
            {'name': 'Shopping', 'type': 'expense', 'icon': '🛍️', 'color': '#6f42c1'},
            {'name': 'Entertainment', 'type': 'expense', 'icon': '🎬', 'color': '#007bff'},
            {'name': 'Bills & Utilities', 'type': 'expense', 'icon': '💡', 'color': '#ffc107'},
            {'name': 'Healthcare', 'type': 'expense', 'icon': '🏥', 'color': '#198754'},
            {'name': 'Education', 'type': 'expense', 'icon': '📚', 'color': '#6c757d'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                user=demo_user,
                name=cat_data['name'],
                category_type=cat_data['type'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {cat_data["name"]}')
        
        # Create sample transactions
        current_date = date.today()
        start_date = current_date - timedelta(days=90)  # Last 3 months
        
        # Sample transaction data
        sample_transactions = [
            # Income transactions
            ('Salary', 'income', 4500, 'Monthly salary'),
            ('Freelance', 'income', 800, 'Website development project'),
            ('Investment Returns', 'income', 150, 'Dividend payment'),
            
            # Expense transactions
            ('Food & Dining', 'expense', 450, 'Groceries and restaurants'),
            ('Transportation', 'expense', 200, 'Gas and public transport'),
            ('Shopping', 'expense', 300, 'Clothing and accessories'),
            ('Entertainment', 'expense', 180, 'Movies and games'),
            ('Bills & Utilities', 'expense', 350, 'Electricity, water, internet'),
            ('Healthcare', 'expense', 120, 'Doctor visit and medicines'),
            ('Education', 'expense', 100, 'Online courses'),
        ]
        
        # Create transactions for the last 3 months
        for month_offset in range(3):
            transaction_date = current_date.replace(day=15) - timedelta(days=30 * month_offset)
            
            for cat_name, trans_type, base_amount, description in sample_transactions:
                if cat_name in categories:
                    # Add some variation to amounts
                    amount_variation = random.uniform(0.8, 1.2)
                    amount = Decimal(str(round(base_amount * amount_variation, 2)))
                    
                    transaction, created = Transaction.objects.get_or_create(
                        user=demo_user,
                        category=categories[cat_name],
                        date=transaction_date,
                        description=f"{description} - {transaction_date.strftime('%b %Y')}",
                        defaults={
                            'amount': amount,
                            'transaction_type': trans_type,
                        }
                    )
                    if created:
                        self.stdout.write(f'Created transaction: {description} - ${amount}')
        
        # Create sample budgets for current month
        current_month = current_date.month
        current_year = current_date.year
        
        budget_data = [
            ('Food & Dining', 500),
            ('Transportation', 250),
            ('Shopping', 200),
            ('Entertainment', 150),
            ('Bills & Utilities', 400),
            ('Healthcare', 150),
            ('Education', 100),
        ]
        
        for cat_name, budget_amount in budget_data:
            if cat_name in categories:
                budget, created = Budget.objects.get_or_create(
                    user=demo_user,
                    category=categories[cat_name],
                    month=current_month,
                    year=current_year,
                    defaults={'amount': Decimal(str(budget_amount))}
                )
                if created:
                    self.stdout.write(f'Created budget: {cat_name} - ${budget_amount}')
        
        # Create sample savings goals
        savings_goals_data = [
            {
                'title': 'Emergency Fund',
                'target_amount': Decimal('10000.00'),
                'current_amount': Decimal('3500.00'),
                'target_date': current_date + timedelta(days=365),
            },
            {
                'title': 'Vacation Fund',
                'target_amount': Decimal('2500.00'),
                'current_amount': Decimal('800.00'),
                'target_date': current_date + timedelta(days=180),
            },
            {
                'title': 'New Laptop',
                'target_amount': Decimal('1500.00'),
                'current_amount': Decimal('600.00'),
                'target_date': current_date + timedelta(days=120),
            },
        ]
        
        for goal_data in savings_goals_data:
            goal, created = SavingsGoal.objects.get_or_create(
                user=demo_user,
                title=goal_data['title'],
                defaults=goal_data
            )
            if created:
                self.stdout.write(f'Created savings goal: {goal_data["title"]}')
        
        # Create sample financial tips
        tips_data = [
            {
                'title': '50/30/20 Budget Rule',
                'content': 'Allocate 50% of your income to needs, 30% to wants, and 20% to savings and debt repayment.',
                'priority': 'high',
            },
            {
                'title': 'Track Your Expenses Daily',
                'content': 'Make it a habit to record all your expenses daily. This helps you stay aware of your spending patterns.',
                'priority': 'medium',
            },
            {
                'title': 'Build an Emergency Fund',
                'content': 'Aim to save 3-6 months of living expenses for unexpected situations like job loss or medical emergencies.',
                'priority': 'high',
            },
            {
                'title': 'Review and Adjust Monthly',
                'content': 'Review your budget monthly and make adjustments based on your actual spending patterns.',
                'priority': 'medium',
            },
            {
                'title': 'Automate Your Savings',
                'content': 'Set up automatic transfers to your savings account to ensure consistent saving habits.',
                'priority': 'low',
            },
        ]
        
        for tip_data in tips_data:
            tip, created = FinancialTip.objects.get_or_create(
                title=tip_data['title'],
                defaults=tip_data
            )
            if created:
                self.stdout.write(f'Created financial tip: {tip_data["title"]}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('You can now login with:')
        self.stdout.write('  Username: demo')
        self.stdout.write('  Password: demo123')
        self.stdout.write('  Or create a new account at /signup/')