import uuid
from django.shortcuts import render,redirect,HttpResponse
from utils.pay import AliPay
from app01 import models


def index(request):
    goods_list = models.Goods.objects.all()
    return render(request,'index.html',{'goods_list':goods_list})


def buy(request, gid):
    """
    去购买并支付
    :param request:
    :param gid:
    :return:
    """
    obj = models.Goods.objects.get(pk=gid)

    # 生成订单（未支付）
    no = str(uuid.uuid4())
    models.Order.objects.create(no=no, goods_id=obj.id)

    # 根据
    #   APPID
    #   支付宝网关
    #   公钥和私钥
    # 生成要跳转的地址
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info

    alipay = AliPay(
        appid = "2016092600597674",
        app_notify_url="http://120.78.181.188:8888/check_order/", # POST,发送支付状态信息
        return_url="http://120.78.181.188:8888/show/",  # GET,将用户浏览器地址重定向回原网站
        app_private_key_path="keys/app_private_2048.txt",
        alipay_public_key_path="keys/alipay_public_2048.txt",
        debug=True,  # 默认True测试环境、False正式环境
    )

    query_params = alipay.direct_pay(
        subject=obj.name,  # 商品简单描述
        out_trade_no=no,  # 商户订单号
        total_amount=obj.price,  # 交易金额(单位: 元 保留俩位小数)
    )

    pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)

    return redirect(pay_url)


def check_order(request):
    """
    POST请求，支付宝通知支付信息，我们修改订单状态
    :param request:
    :return:
    """
    if request.method == 'POST':
        alipay = AliPay(
            appid="2016092600597674",
            app_notify_url="http://120.78.181.188:8888/check_order/",  # POST,发送支付状态信息
            return_url="http://120.78.181.188:8888/show/",  # GET,将用户浏览器地址重定向回原网站
            app_private_key_path="keys/app_private_2048.txt",
            alipay_public_key_path="keys/alipay_public_2048.txt",
            debug=True,  # 默认True测试环境、False正式环境
        )

        from urllib.parse import parse_qs
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)

        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]
        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        if status:
            # 支付成功，获取订单号将订单状态更新
            out_trade_no = post_dict['out_trade_no']
            models.Order.objects.filter(no=out_trade_no).update(status=2)
            return HttpResponse('success')
        else:
            return HttpResponse('支持失败')
    else:
        return HttpResponse('只支持POST请求')


def show(request):
    """
    回到我们页面
    :param request:
    :return:
    """

    if request.method == "GET":
        alipay = AliPay(
            appid="2016092600597674",
            app_notify_url="http://120.78.181.188:8888/check_order/",  # POST,发送支付状态信息
            return_url="http://120.78.181.188:8888/show/",  # GET,将用户浏览器地址重定向回原网站
            app_private_key_path="keys/app_private_2048.txt",
            alipay_public_key_path="keys/alipay_public_2048.txt",
            debug=True,  # 默认True测试环境、False正式环境
        )
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = alipay.verify(params, sign)
        if status:
            return HttpResponse('支付成功')
        else:
            return HttpResponse('失败')
    else:
        return HttpResponse('只支持GET请求')


def order_list(request):
    """
    查看所有订单状态
    :param request:
    :return:
    """
    orders = models.Order.objects.all()
    return render(request,'order_list.html',{'orders':orders})
