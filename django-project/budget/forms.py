from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, Category, Budget, UserProfile, SavingsGoal
from datetime import datetime


class CustomUserCreationForm(UserCreationForm):
    """Extended user creation form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = None
        
        # Add specific attributes for better UX
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Choose a unique username',
            'required': True
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'your@email.com',
            'type': 'email',
            'required': True
        })
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'First Name',
            'required': True
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Last Name',
            'required': True
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a strong password',
            'required': True
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'required': True
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """User profile form"""
    class Meta:
        model = UserProfile
        fields = ['monthly_income', 'savings_goal']
        widgets = {
            'monthly_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'savings_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }


class CategoryForm(forms.ModelForm):
    """Category form"""
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '💰 (Use emoji icons)'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
        }


class TransactionForm(forms.ModelForm):
    """Transaction form"""
    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'description', 'date']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = datetime.now().date()


class BudgetForm(forms.ModelForm):
    """Budget form"""
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2030'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter categories to only expense categories for budgeting
            self.fields['category'].queryset = Category.objects.filter(
                user=user, 
                category_type='expense'
            )
        
        # Set default month and year
        if not self.instance.pk:
            current_date = datetime.now()
            self.fields['month'].initial = current_date.month
            self.fields['year'].initial = current_date.year


class SavingsGoalForm(forms.ModelForm):
    """Savings goal form"""
    class Meta:
        model = SavingsGoal
        fields = ['title', 'target_amount', 'current_amount', 'target_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'current_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class DateRangeForm(forms.Form):
    """Form for filtering by date range"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        empty_label="All Categories"
    )
    transaction_type = forms.ChoiceField(
        choices=[('', 'All Types'), ('income', 'Income'), ('expense', 'Expense')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)