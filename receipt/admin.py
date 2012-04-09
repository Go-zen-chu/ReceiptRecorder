# encoding: utf-8
from ReceiptRecorder.receipt.models import Receipt, Shop
from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import HttpResponse
from django.utils.functional import update_wrapper
from django.views.generic.simple import direct_to_template
from django.db.models import Sum

class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("date_of_purchase","total_payment","memo","payment_user","common_payment","keichi_expense","akira_expense","shop")
    # 以下、日付の詳細なフィルター
    # list_filter = ["date_of_purchase"]
    date_hierarchy = "date_of_purchase"
    
    def show_home_page(self, request):
        return HttpResponse(u'''Hello, receipt!<br><ul>
            <li><a href="/admin/receipt/receipt/">レシート確認画面</a></li><br>
            <li><a href="/admin/receipt/receipt/add/">レシート追加画面</a></li><br>
            <li><a href="/admin/receipt/receipt/monthly_summary/">月別合計</a></li><br>
            <li><a href="/admin/receipt/shop/monthly_summary/">店別合計</a></li><br>
            <li><a href="/admin/">管理サイト</a></li><br>''')

    def compute_summary_of_month(self, request):
        first_date = Receipt.objects.all().order_by("date_of_purchase")[0].date_of_purchase
        last_date = Receipt.objects.all().order_by("-date_of_purchase")[0].date_of_purchase
        year = first_date.year
        month = first_date.month
        result = []
        while True:
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
    
    def get_urls(self):
        urls = super(ReceiptAdmin,self).get_urls()
        my_urls = patterns('',
                    (r'^home_page/$', self.admin_site.admin_view(self.show_home_page)), # home_page
                    (r'^monthly_summary/$', self.admin_site.admin_view(self.compute_summary_of_month)),
        )
        return my_urls + urls
    
# Receiptクラスをadminサイトに反映させる
admin.site.register(Receipt, ReceiptAdmin)


class ShopAdmin(admin.ModelAdmin):
    # 各店舗の合計を計算し、表示する
    def compute_summary_of_store(self, request):
        first_date = Receipt.objects.all().order_by("date_of_purchase")[0].date_of_purchase
        last_date = Receipt.objects.all().order_by("-date_of_purchase")[0].date_of_purchase
        year = first_date.year
        month = first_date.month
        date_list = []
        shop_list = []
        total_payment_list = []
        while True:
            for receipt in Receipt.objects.filter(date_of_purchase__year=year,
                                                date_of_purchase__month=month).select_related(depth=1).values("shop__name").annotate(total=Sum("total_payment")):
                shop_list.append(receipt["shop__name"])
                total_payment_list.append(receipt["total"])
                
            date_list.append((year,month))
            
            if last_date.year == year and last_date.month == month:
                break
            else:
                month += 1
            
            if month == 13:
                month = 1
                year += 1
                
        context = { 'title': u"店舗別支払い", 'date_list': date_list, 'shop_list': shop_list,
                     'total_payment_list': total_payment_list, }
        return direct_to_template(request, "shops_monthly_reports.html", context)

    # adminサイトにホームページや月別合計のページを登録するのに使う
    def get_urls(self):
        urls = super(ShopAdmin,self).get_urls()
        my_urls = patterns('',
                    (r'^monthly_summary/$', self.admin_site.admin_view(self.compute_summary_of_store)),
        )
        return my_urls + urls

admin.site.register(Shop,ShopAdmin)
