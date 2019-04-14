from django.db import models

# Create your models here.


class Goods(models.Model):
    name = models.CharField(max_length=32)
    price = models.FloatField()


class Order(models.Model):
    no = models.CharField(max_length=64)
    goods = models.ForeignKey(to='Goods', on_delete=models.CASCADE)
    status_choices = (
        (1,'未支付'),
        (2,'已支付'),
    )
    status = models.IntegerField(choices=status_choices,default=1)