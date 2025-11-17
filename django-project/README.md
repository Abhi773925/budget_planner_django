# Django Budget Planner

An interactive budget planner application built with Django that allows users to create monthly budgets, track expenses, and visualize their spending habits with financial health suggestions.

## Features

### 📊 Dashboard
- Real-time budget overview with spending vs. budget comparisons
- Visual charts showing expense distribution by category
- Quick stats on total income, expenses, and savings
- Recent transactions overview

### 💰 Budget Management
- Create and manage monthly budgets by category
- Set spending limits for different expense categories
- Track budget performance with visual indicators
- Budget vs. actual spending analysis

### 📝 Transaction Tracking
- Add income and expense transactions
- Categorize transactions with custom icons and colors
- Search and filter transactions by date, category, and amount
- Bulk transaction management

### 📈 Financial Reporting
- Monthly and yearly spending reports
- Category-wise expense breakdown
- Income vs. expense trends
- Savings goal tracking progress

### 🎯 Savings Goals
- Set and track multiple savings goals
- Visual progress indicators
- Target date and amount tracking
- Automatic progress calculations

### 💡 Financial Tips
- Personalized financial advice
- Budget optimization suggestions
- Spending habit insights
- Financial health recommendations

## Technology Stack

- **Backend**: Django 5.2.4
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5.1.3, Chart.js
- **Icons**: Font Awesome 6.0.0
- **Styling**: Custom CSS with responsive design

## Installation & Setup

1. **Navigate to project directory**:
   ```bash
   cd c:\Users\91773\OneDrive\Desktop\django-project
   ```

2. **Install dependencies** (if needed):
   ```bash
   pip install django
   ```

3. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create sample data** (optional):
   ```bash
   python manage.py create_sample_data
   ```

5. **Start development server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the application**:
   Open your browser and go to `http://127.0.0.1:8000/`

## Demo Account

Use these credentials to explore the application with pre-loaded sample data:

- **Username**: `demo`
- **Password**: `demo123`

Or create a new account by clicking "Sign Up" on the login page.

## Application Structure

### Models
- **UserProfile**: Extended user information with income and savings goals
- **Category**: Income/expense categories with icons and colors
- **Transaction**: Financial transactions (income/expenses)
- **Budget**: Monthly spending limits by category
- **SavingsGoal**: Savings targets with progress tracking
- **FinancialTip**: Financial advice and recommendations

### Key Features

#### Dashboard (`/dashboard/`)
- Overview of current month's budget performance
- Interactive charts powered by Chart.js
- Quick access to recent transactions
- Financial health indicators

#### Transactions (`/transactions/`)
- Add, edit, and delete transactions
- Filter by date range, category, and type
- Pagination for large transaction lists
- CSV export functionality

#### Budgets (`/budgets/`)
- Set monthly spending limits
- Visual budget vs. actual comparisons
- Category-wise budget management
- Budget performance analytics

#### Reports (`/reports/`)
- Monthly and yearly financial reports
- Category-wise spending analysis
- Income vs. expense trends
- Downloadable report summaries

#### Savings Goals (`/savings-goals/`)
- Create and track multiple savings goals
- Progress visualization
- Target date management
- Achievement tracking

## API Endpoints

The application includes AJAX endpoints for dynamic updates:

- `/api/category-expenses/`: Monthly expenses by category
- `/api/monthly-trends/`: Income vs. expense trends
- `/api/budget-performance/`: Budget vs. actual spending data

## Responsive Design

The application is fully responsive and works well on:
- Desktop computers
- Tablets
- Mobile phones

## Security Features

- User authentication and authorization
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password handling

## Customization

### Adding Categories
- Custom icons using emoji or Font Awesome
- Color coding for visual organization
- Income vs. expense classification

### Financial Tips
- Customizable advice system
- Priority-based tip display
- Contextual recommendations

### Reports
- Flexible date range filtering
- Multiple visualization options
- Export capabilities

## Sample Data

The `create_sample_data` management command creates:
- Demo user account
- 10 expense/income categories
- 3 months of transaction history
- Current month budgets
- Sample savings goals
- Financial tips and advice

## Development Notes

### Key Files
- `budget/models.py`: Database models and relationships
- `budget/views.py`: Business logic and request handling
- `budget/forms.py`: Form definitions and validation
- `templates/`: HTML templates with Bootstrap styling
- `static/`: CSS, JavaScript, and asset files

### Database
- Uses Django ORM with SQLite for development
- Easily configurable for PostgreSQL/MySQL in production
- Includes proper foreign key relationships and constraints

### Frontend
- Bootstrap 5 for responsive UI components
- Chart.js for interactive data visualization
- Custom CSS for application-specific styling
- JavaScript for dynamic interactions

## Future Enhancements

- **Mobile App**: React Native or Flutter mobile application
- **Bank Integration**: Connect to bank APIs for automatic transaction import
- **Investment Tracking**: Portfolio management and investment tracking
- **Bill Reminders**: Automatic bill payment reminders
- **Multi-Currency**: Support for multiple currencies
- **Collaborative Budgets**: Shared budgets for families/couples
- **Advanced Reports**: More detailed financial analytics
- **Export Options**: PDF reports and CSV exports

## Support

The application includes comprehensive error handling and user-friendly interfaces. For issues or feature requests, check the Django development server logs for debugging information.

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Framework**: Django 5.2.4