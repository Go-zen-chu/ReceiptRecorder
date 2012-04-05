# encoding: utf-8
from django.contrib import admin
from django.db import models

class Receipt(models.Model):
    # id is added automatically
    date_of_purchase = models.DateTimeField(u"購入日")
    PAYMENT_USER_CHOICES = ((1,u"慧智"),(2,u"彬"))
    payment_user = models.SmallIntegerField(u"支払人",choices=PAYMENT_USER_CHOICES,default=1)
    total_payment = models.IntegerField(u"合計金額")
    keichi_expense = models.IntegerField(u"慧智自腹の分",blank=True,default=0)
    akira_expense = models.IntegerField(u"彬自腹の分",blank=True,default=0)
    memo = models.CharField(u"メモ",max_length=140)
    
    def __unicode__(self):
        return "[%s]%s" % (self.date_of_purchase, self.memo)
    def common_payment(self):
        return self.total_payment - self.keichi_expense - self.akira_expense
    common_payment.short_description = u"割り勘の分"
    