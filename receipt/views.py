# encoding: utf-8
from ReceiptRecorder.receipt.models import Receipt
from django.contrib import admin
from django.http import HttpResponse
from django.template import Context, loader
from django.views.generic.simple import direct_to_template

def show_home_page(request):
    return HttpResponse(u'''Hello, receipt!<br><ul>
        <li><a href="/admin/receipt/receipt/">レシート確認画面</a></li><br>
        <li><a href="/admin/receipt/receipt/add/">レシート追加画面</a></li><br>
        <li><a href="/admin/monthly_summary/">月別合計</a></li><br>
        <li><a href="/admin/">管理サイト</a></li><br>''')


def compute_summary_of_month(request):
    first_date = Receipt.objects.all().order_by("date_of_purchase")[0].date_of_purchase
    last_date = Receipt.objects.all().order_by("-date_of_purchase")[0].date_of_purchase
    year = first_date.year
    month = first_date.month
    result = []
    while True:
        # 実際にお店で支払った金額の合計
#        keichi_total_payment = 0
#        akira_total_payment = 0
        # 一ヶ月で使った値段の合計
        total_payment = 0
        # 互いに対して払わなければならない値段の合計
        keichi_to_akira = 0
        akira_to_keichi = 0
        # 二人が使ったお金の合計
        common_total_payment = 0
        # 各自が一ヶ月で自腹を切る値段の合計
        keichi_total_expense = 0
        akira_total_expense = 0
        
        for receipt in Receipt.objects.filter(date_of_purchase__year=year,date_of_purchase__month=month):
            total_payment += receipt.total_payment
            # 一つのレシートにおいて二人で払うべき料金
            common_payment = (receipt.total_payment - receipt.keichi_expense - receipt.akira_expense)
            common_total_payment += common_payment
            if receipt.payment_user == 1:   # Keichi
                akira_to_keichi += common_payment/2 + receipt.akira_expense
            elif receipt.payment_user == 2: # Akira
                keichi_to_akira += common_payment/2 + receipt.keichi_expense
            keichi_total_expense += receipt.keichi_expense
            akira_total_expense += receipt.akira_expense
        
        result.append(((year,month), total_payment, akira_to_keichi, keichi_to_akira, akira_to_keichi - keichi_to_akira,
                       common_total_payment, common_total_payment/2 + keichi_total_expense, common_total_payment/2 + akira_total_expense,))
        
        if last_date.year == year and last_date.month == month:
            break
        else:
            month += 1
        
        if month == 13:
            month = 1
            year += 1
            
    context = { 'title': u"月別合計", 'result':result }
    return direct_to_template(request, "monthly_reports.html", context)



