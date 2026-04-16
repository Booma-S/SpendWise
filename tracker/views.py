import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
import calendar

from django.db import models as db_models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Budget, Expense


# ─────────────────────────────────────────────
#  HOME / DASHBOARD
# ─────────────────────────────────────────────
def home(request):
    # --- search / category filter ---
    search     = request.GET.get('q', '').strip()
    cat_filter = request.GET.get('cat', '').strip()

    all_qs = Expense.objects.all().order_by('-date')
    filtered_qs = all_qs

    if search:
        filtered_qs = filtered_qs.filter(
            db_models.Q(title__icontains=search)
            | db_models.Q(category__icontains=search)
            | db_models.Q(description__icontains=search)
        )
    if cat_filter:
        filtered_qs = filtered_qs.filter(category=cat_filter)

    expenses     = list(filtered_qs)
    all_expenses = list(all_qs)

    now = datetime.now()

    # --- totals ---
    total = sum(e.amount for e in all_expenses)

    cur_month = now.month
    cur_year  = now.year
    monthly_total = sum(
        e.amount for e in all_expenses
        if e.date.month == cur_month and e.date.year == cur_year
    )

    prev_month = cur_month - 1 or 12
    prev_year  = cur_year if cur_month > 1 else cur_year - 1
    monthly_prev = sum(
        e.amount for e in all_expenses
        if e.date.month == prev_month and e.date.year == prev_year
    )
    # --- weekly total ---
    week_ago = now - timedelta(days=7)
    weekly_total = sum(e.amount for e in all_expenses if e.date >= week_ago.date())

    # --- monthly change ---
    if monthly_prev > 0:
        difference = monthly_total - monthly_prev
        month_change_dir = 'up' if difference >= 0 else 'down'
    else:
        difference = None
        month_change_dir = 'up'
    # average daily spend over last 30 days
    last30_total = sum(
        e.amount for e in all_expenses
        if e.date >= (now - timedelta(days=30)).date()
    )
    avg_daily = round(last30_total / 30, 2)

    # --- weekly bar-chart report (oldest → newest) ---
    weekly_report = {}
    for i in range(6, -1, -1):
        d    = (now - timedelta(days=i)).date()
        name = d.strftime('%A')
        weekly_report[name[:3]] = round(
            sum(e.amount for e in all_expenses if e.date == d), 2
        )

    # --- highest expense ---
    highest_expense = max(all_expenses, key=lambda x: x.amount) if all_expenses else None

    # --- monthly breakdown (for expandable card) ---
    monthly_data_raw = defaultdict(float)

    for e in all_expenses:
        month_name = calendar.month_abbr[e.date.month]  # Jan, Feb, Mar
        monthly_data_raw[month_name] += e.amount

        # sort months properly
    ordered_months = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]

    monthly_data = {
        m: round(monthly_data_raw[m], 2)
        for m in ordered_months
        if m in monthly_data_raw
    }

    # --- category totals (for chart + budget) ---
    cat_totals = defaultdict(float)
    for e in all_expenses:
        cat_totals[e.category] += e.amount

    # top spending category
    top_category = max(cat_totals, key=cat_totals.get) if cat_totals else '—'

    labels = list(cat_totals.keys())
    data   = [round(v, 2) for v in cat_totals.values()]

    # --- budget progress ---
    budgets     = {b.category: b.limit for b in Budget.objects.all()}
    budget_data = []
    for cat, spent in cat_totals.items():
        if cat in budgets:
            limit = budgets[cat]
            pct   = min(round((spent / limit) * 100), 100)
            budget_data.append({
                'category': cat,
                'spent':    round(spent, 2),
                'limit':    limit,
                'pct':      pct,
                'over':     spent > limit,
            })

    # --- heatmap: last 35 days ---
    heatmap     = []
    heatmap_max = 1
    for i in range(34, -1, -1):
        d       = (now - timedelta(days=i)).date()
        day_amt = round(sum(e.amount for e in all_expenses if e.date == d), 2)
        heatmap.append({'date': d.strftime('%Y-%m-%d'), 'amount': day_amt})
        if day_amt > heatmap_max:
            heatmap_max = day_amt

    # --- distinct categories for filter chips ---
    all_categories = list(
        Expense.objects.values_list('category', flat=True).distinct()
    )

    return render(request, 'home.html', {
        'expenses':         expenses,
        'total':            round(total, 2),
        'monthly_total':    round(monthly_total, 2),
        'monthly_prev':     round(monthly_prev, 2),
        'month_change_dir': month_change_dir,
        'weekly_total':     round(weekly_total, 2),
        'avg_daily':        avg_daily,
        'weekly_report':    weekly_report,
        'highest_expense':  highest_expense,
        'top_category':     top_category,
        'labels':           json.dumps(labels),
        'data':             json.dumps(data),
        'budget_data':      budget_data,
        'heatmap':          json.dumps(heatmap),
        'heatmap_max':      heatmap_max,
        'all_categories':   all_categories,
        'search':           search,
        'cat_filter':       cat_filter,
        'monthly_data': monthly_data,
        'difference': round(abs(difference), 2) if difference is not None else None,
    })


# ─────────────────────────────────────────────
#  ADD
# ─────────────────────────────────────────────
def add_expense(request):
    if request.method == 'POST':
        Expense.objects.create(
            title       = request.POST.get('title') or None,
            amount      = request.POST.get('amount'),
            category    = request.POST.get('category'),
            date        = request.POST.get('date'),
            description = request.POST.get('description') or None,
            reference   = request.POST.get('reference') or None,
        )
        return redirect('home')
    return render(request, 'add.html')


# ─────────────────────────────────────────────
#  EDIT
# ─────────────────────────────────────────────
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id)
    if request.method == 'POST':
        expense.title       = request.POST.get('title') or None
        expense.amount      = request.POST.get('amount')
        expense.category    = request.POST.get('category')
        expense.date        = request.POST.get('date')
        expense.description = request.POST.get('description') or None
        expense.reference   = request.POST.get('reference') or None
        expense.save()
        return redirect('home')
    return render(request, 'edit.html', {'expense': expense})


# ─────────────────────────────────────────────
#  DELETE
# ─────────────────────────────────────────────
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id)
    expense.delete()
    return redirect('home')


# ─────────────────────────────────────────────
#  CSV EXPORT
# ─────────────────────────────────────────────
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Category', 'Date', 'Description', 'Reference'])
    for e in Expense.objects.all().order_by('-date'):
        writer.writerow([
            e.title or '',
            e.amount,
            e.category,
            e.date,
            e.description or '',
            e.reference or '',
        ])
    return response


# ─────────────────────────────────────────────
#  SET BUDGET (POST only)
# ─────────────────────────────────────────────
def set_budget(request):
    if request.method == 'POST':
        category = request.POST.get('category', '').strip()
        limit    = request.POST.get('limit', '').strip()
        if category and limit:
            Budget.objects.update_or_create(
                category=category,
                defaults={'limit': float(limit)},
            )
    return redirect('home')

# ─────────────────────────────────────────────
#  CLEAR ALL EXPENSES 
# ─────────────────────────────────────────────

def clear_all_expenses(request):
    if request.method == "POST":
        from .models import Expense
        Expense.objects.all().delete()
    return redirect('home')