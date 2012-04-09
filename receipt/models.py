# encoding: utf-8
from datetime import datetime
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models

class Shop(models.Model):
    name = models.CharField(u'店名', max_length=128)
    def __unicode__(self):
        return "%s" % (self.name)


class Receipt(models.Model):
    # id is added automatically
    date_of_purchase = models.DateTimeField(u"購入日", default=datetime.now)
    PAYMENT_USER_CHOICES = ((1, u"慧智"), (2, u"彬"))
    payment_user = models.SmallIntegerField(u"支払人", choices=PAYMENT_USER_CHOICES, default=1)
    total_payment = models.IntegerField(u"合計金額")
    keichi_expense = models.IntegerField(u"慧智自腹の分", blank=True, default=0)
    akira_expense = models.IntegerField(u"彬自腹の分", blank=True, default=0)
    memo = models.CharField(u"メモ", max_length=140, blank=True)
    shop = models.ForeignKey(Shop, default=1, verbose_name=u"店名")
    
    def __unicode__(self):
        return "[%s]%s" % (self.date_of_purchase, self.memo)
    def common_payment(self):
        return self.total_payment - self.keichi_expense - self.akira_expense
    common_payment.short_description = u"割り勘の分"
    def clean(self):
        if self.total_payment < 0:
            raise ValidationError('合計金額は0以上の値を入力してください。')
        if self.keichi_expense < 0:
            raise ValidationError('慧智自腹分は0以上の値を入力してください。')
        if self.akira_expense < 0:
            raise ValidationError('彬自腹分は0以上の値を入力してください。')
        if self.total_payment < self.keichi_expense + self.akira_expense:
            raise ValidationError('自腹分の合計が合計金額を超えています。')
