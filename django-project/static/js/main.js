// Main JavaScript for Budget Planner

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Initialize expense chart if canvas exists
    const expenseChartCanvas = document.getElementById('expenseChart');
    if (expenseChartCanvas) {
        initializeExpenseChart();
    }

    // Initialize budget progress charts
    const budgetProgressElements = document.querySelectorAll('.budget-progress');
    if (budgetProgressElements.length > 0) {
        initializeBudgetProgress();
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Initialize expense pie chart
function initializeExpenseChart() {
    fetch('/api/expense-data/')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('expenseChart').getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: data.colors,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading expense data:', error);
            document.getElementById('expenseChart').style.display = 'none';
            document.querySelector('#expenseChart').parentNode.innerHTML = 
                '<p class="text-muted text-center">No expense data available</p>';
        });
}

// Initialize budget progress indicators
function initializeBudgetProgress() {
    fetch('/api/budget-progress/')
        .then(response => response.json())
        .then(data => {
            data.budgets.forEach(budget => {
                updateBudgetProgressBar(budget);
            });
        })
        .catch(error => {
            console.error('Error loading budget progress:', error);
        });
}

// Update individual budget progress bar
function updateBudgetProgressBar(budget) {
    const progressBar = document.querySelector(`[data-budget="${budget.category}"] .progress-bar`);
    if (progressBar) {
        progressBar.style.width = `${budget.percentage}%`;
        progressBar.setAttribute('aria-valuenow', budget.percentage);
        
        // Change color based on budget status
        progressBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');
        if (budget.over_budget) {
            progressBar.classList.add('bg-danger');
        } else if (budget.percentage > 80) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-success');
        }
        
        // Update text
        const budgetText = document.querySelector(`[data-budget="${budget.category}"] .budget-text`);
        if (budgetText) {
            budgetText.textContent = `$${budget.spent.toFixed(2)} of $${budget.budgeted.toFixed(2)}`;
        }
    }
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to show loading spinner
function showLoading(element) {
    element.innerHTML = '<div class="spinner"></div>';
}

// Utility function to hide loading spinner
function hideLoading(element, content) {
    element.innerHTML = content;
}

// AJAX form submission helper
function submitFormAjax(form, successCallback, errorCallback) {
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok');
    })
    .then(data => {
        if (successCallback) {
            successCallback(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (errorCallback) {
            errorCallback(error);
        }
    });
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const toastContainer = document.querySelector('.toast-container') || document.body;
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}