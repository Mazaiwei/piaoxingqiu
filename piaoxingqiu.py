# -*- coding: utf-8 -*-
# @Time:      2024/07/02 10:57
# @Author:     马再炜
# @File:       piaoxingqiu.py

import requests
from fake_useragent import UserAgent
import datetime


class PXQ:
    def __init__(self):
        # 输入自己的token
        self.token = '这里要打开网页开发者工具找到你自己的token'
        # 演唱会项目id，必填
        self.show_id = '665708481d06bc0001627d83'
        # 指定场次id，不指定则默认从第一场开始遍历
        self.session_id = '665708656a025300012ae72a'
        # 购票数量，一定要看购票须知，不要超过上限
        self.buy_count = 1
        # 指定观演人，观演人序号从0开始，人数需与票数保持一致
        self.audience_idx = [0]
        # audience_idx = [0]
        # 门票类型，不确定则可以不填，让系统自行判断。快递送票:EXPRESS,电子票:E_TICKET/ID_CARD,现场取票:VENUE,电子票或现场取票:VENUE_E,目前只发现这四种，如有新发现可补充
        self.deliver_method = ''
        self.seat_plan_id = ''
        self.session_id_exclude = []  # 被排除掉的场次
        self.price: int = 0
        self.seatPlanName = ''
        self.threadsLists = []
        # 判断是否对应价位有票数,默认是无
        self.flag = False
        # 设置抢票开始时间
        self.startTime = datetime.datetime(2024, 7, 3, 2, 0, 0)
        self.user_agent = UserAgent()

    # 根据项目id获取所有场次和在售状态
    def get_sessions(self, useragent):
        headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'User-Agent': useragent,
            'Content-Type': 'application/json'
        }
        url = "https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v3/show/" + self.show_id + "/sessions_dynamic_data"
        response = requests.get(url=url, headers=headers).json()
        if response["statusCode"] == 200:
            # 获取场次的id
            # print(response)
            return response["data"]["sessionVOs"]
        else:
            print("get_sessions异常:" + str(response))
        return None

    # 根据场次id获取座位信息
    def get_seat_plans(self, useragent) -> list:
        headers = {
            'User-Agent': useragent,
            'Content-Type': 'application/json'
        }
        url = "https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v3/show/" + self.show_id + "/show_session/" + self.session_id + "/seat_plans_static_data"
        response = requests.get(url=url, headers=headers).json()
        if response["statusCode"] == 200:
            # 查看票价的id
            # print(response)
            return response["data"]["seatPlans"]
        else:
            raise Exception("get_seat_plans异常:" + str(response))

    # 获取座位余票
    def get_seat_count(self, useragent) -> list:
        headers = {
            'User-Agent': useragent,
            'Content-Type': 'application/json'
        }
        url = "https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v3/show/" + self.show_id + "/show_session/" + self.session_id + "/seat_plans_dynamic_data"
        response = requests.get(url=url, headers=headers).json()
        if response["statusCode"] == 200:
            return response["data"]["seatPlans"]
        else:
            raise Exception("get_seat_count异常:" + str(response))

    # 获取门票类型（快递送票EXPRESS,电子票E_TICKET,现场取票VENUE,电子票或现场取票VENUE_E）
    def get_deliver_method(self, useragent, qty: int) -> str:
        headers = {
            'User-Agent': useragent,
            'Content-Type': 'application/json',
            'access-token': self.token
        }
        data = {
            "items": [
                {
                    "skus": [
                        {
                            "seatPlanId": self.seat_plan_id,  # 644fcf080f4f4e0001f1519d
                            "sessionId": self.session_id,  # 644fcb7dca916100017dda3d
                            "showId": self.show_id,  # 644fcb2aca916100017dcfef
                            "skuId": self.seat_plan_id,
                            "skuType": "SINGLE",
                            "ticketPrice": self.price,  # 388
                            "qty": qty  # 2
                        }
                    ],
                    "spu": {
                        "id": self.show_id,
                        "spuType": "SINGLE"
                    }
                }
            ]
        }
        url = "https://m.piaoxingqiu.com/cyy_gatewayapi/trade/buyer/order/v3/pre_order"
        response = requests.post(url=url, headers=headers, json=data).json()
        if response["statusCode"] == 200:
            # 这里的print可以去掉
            # print(response["data"]["supportDeliveries"][0])
            return response["data"]["supportDeliveries"][0]["name"]
        else:
            raise Exception("获取门票类型异常:" + str(response))

    # 获取观演人信息
    # def get_audiences() -> list | None:
    def get_audiences(self, useragent):
        headers = {
            'User-Agent': useragent,
            'Content-Type': 'application/json',
            'access-token': self.token
        }
        url = "https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/user_audiences"
        response = requests.get(url=url, headers=headers).json()
        if response["statusCode"] == 200:
            # 可以获取观影人的信息查看是否正确
            return response["data"]
        else:
            print("get_audiences异常:" + str(response))
        return None

    # 获取收货地址
    # def get_address() -> dict | None:
    def get_address(self, useragent):
        headers = {
            'User-Agent': useragent,
            'Content-Type': 'application/json',
            'access-token': self.token
        }
        url = "https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/user/addresses/default"
        response = requests.get(url=url, headers=headers).json()
        if response["statusCode"] == 200:
            return response["data"]
        else:
            print("get_address异常:" + str(response))
        return None

    # 获取快递费
    def get_express_fee(self, useragent, qty: int, location_city_id: str) -> dict:
        headers = {
            'User-Agent': useragent,
            'Content-Type': 'application/json',
            'access-token': self.token
        }
        data = {
            "items": [
                {
                    "skus": [
                        {
                            "seatPlanId": self.seat_plan_id,  # 644fcf080f4f4e0001f1519d
                            "sessionId": self.session_id,  # 644fcb7dca916100017dda3d
                            "showId": self.show_id,  # 644fcb2aca916100017dcfef
                            "skuId": self.seat_plan_id,
                            "skuType": "SINGLE",
                            "ticketPrice": self.price,  # 388
                            "qty": qty,  # 2
                            "deliverMethod": "EXPRESS"
                        }
                    ],
                    "spu": {
                        "id": self.show_id,
                        "spuType": "SINGLE"
                    }
                }
            ],
            "locationCityId": location_city_id  # 460102
        }
        url = "https://m.piaoxingqiu.com/cyy_gatewayapi/trade/buyer/order/v3/price_items"
        response = requests.post(url=url, headers=headers, json=data).json()
        if response["statusCode"] == 200:
            return response["data"][0]
        else:
            raise Exception("获取快递费异常:" + str(response))

    # 提交订单（快递送票EXPRESS,电子票E_TICKET/ID_Card,现场取票VENUE,电子票或现场取票VENUE_E）
    def create_order(self, useragent, qty: int, express_fee: int,
                     receiver, cellphone, address_id, detail_address, location_city_id, audience_ids: list):
        headers = {
            'User-Agent': useragent,
            'Content-Type': 'application/json',
            'access-token': self.token
        }
        if self.deliver_method == "EXPRESS":
            data = {
                "priceItemParam": [
                    {
                        "applyTickets": [],
                        "priceItemName": "票款总额",
                        "priceItemVal": self.price * qty,
                        "priceItemType": "TICKET_FEE",
                        "priceItemSpecies": "SEAT_PLAN",
                        "direction": "INCREASE",
                        "priceDisplay": "￥" + str(self.price * qty)
                    },
                    {
                        "applyTickets": [],
                        "priceItemName": "快递费",
                        "priceItemVal": express_fee,
                        "priceItemId": self.show_id,
                        "priceItemSpecies": "SEAT_PLAN",
                        "priceItemType": "EXPRESS_FEE",
                        "direction": "INCREASE",
                        "priceDisplay": "￥" + str(express_fee)
                    }
                ],
                "items": [
                    {
                        "skus": [
                            {
                                "seatPlanId": self.seat_plan_id,
                                "sessionId": self.session_id,
                                "showId": self.show_id,
                                "skuId": self.seat_plan_id,
                                "skuType": "SINGLE",
                                "ticketPrice": self.price,
                                "qty": qty,
                                "deliverMethod": self.deliver_method
                            }
                        ],
                        "spu": {
                            "id": self.show_id,
                            "spuType": "SINGLE"
                        }
                    }
                ],
                "contactParam": {
                    "receiver": receiver,  # 张三
                    "cellphone": cellphone  # 13812345678
                },

                "one2oneAudiences": [{"audienceId": i, "sessionId": self.session_id} for i in audience_ids],
                "addressParam": {
                    "address": detail_address,  # 星巴克咖啡门口
                    "district": location_city_id[4:],
                    "city": location_city_id[2:4],
                    "province": location_city_id[0:2],
                    "addressId": address_id
                }
            }
        elif self.deliver_method == "ID_CARD":
            data = {
                "priceItemParam": [
                    {
                        "applyTickets": [],
                        "priceItemName": "票款总额",
                        "priceItemVal": self.price * qty,
                        "priceItemType": "TICKET_FEE",
                        "priceItemSpecies": "SEAT_PLAN",
                        "direction": "INCREASE",
                        "priceDisplay": "￥" + str(self.price * qty),
                    }
                ],
                "items": [
                    {
                        "skus": [
                            {
                                "seatPlanId": self.seat_plan_id,
                                "sessionId": self.session_id,
                                "showId": self.show_id,
                                "skuId": self.seat_plan_id,
                                "skuType": "SINGLE",
                                "ticketPrice": self.price,
                                "qty": qty,
                                "deliverMethod": self.deliver_method,
                            }
                        ],
                        "spu": {"id": self.show_id, "spuType": "SINGLE"},
                    }
                ],
                "one2oneAudiences": [
                    {"audienceId": i, "sessionId": self.session_id} for i in audience_ids
                ],
                "many2OneAudience": {
                    "audienceId": audience_ids[0],
                    "sessionIds": [self.session_id],
                },
            }
        # 电子票已解决
        elif self.deliver_method == "E_TICKET":
            data = {
                "priceItemParam": [
                    {
                        "applyTickets": [],
                        "priceItemName": "票款总额",
                        "priceItemVal": self.price * qty,
                        "priceItemType": "TICKET_FEE",
                        "priceItemSpecies": "SEAT_PLAN",
                        "direction": "INCREASE",
                        "priceDisplay": "￥" + str(self.price * qty)
                    }
                ],
                "items": [
                    {
                        "skus": [
                            {
                                "seatPlanId": self.seat_plan_id,
                                "sessionId": self.session_id,
                                "showId": self.show_id,
                                "skuId": self.seat_plan_id,
                                "skuType": "SINGLE",
                                "ticketPrice": self.price,
                                "qty": qty,
                                "deliverMethod": self.deliver_method
                            }
                        ],
                        "spu": {
                            "id": self.show_id,
                            "spuType": "SINGLE"
                        }
                    }
                ],
                "many2OneAudience": {
                    "audienceId": audience_ids[0],
                    "sessionIds": [
                        self.session_id
                    ]
                }
            }
        elif self.deliver_method == "VENUE":
            data = {
                "priceItemParam": [
                    {
                        "applyTickets": [],
                        "priceItemName": "票款总额",
                        "priceItemVal": self.price * qty,
                        "priceItemType": "TICKET_FEE",
                        "priceItemSpecies": "SEAT_PLAN",
                        "direction": "INCREASE",
                        "priceDisplay": "￥" + str(self.price * qty)
                    }
                ],
                "items": [
                    {
                        "skus": [
                            {
                                "seatPlanId": self.seat_plan_id,
                                "sessionId": self.session_id,
                                "showId": self.show_id,
                                "skuId": self.seat_plan_id,
                                "skuType": "SINGLE",
                                "ticketPrice": self.price,
                                "qty": qty,
                                "deliverMethod": self.deliver_method
                            }
                        ],
                        "spu": {
                            "id": self.show_id,
                            "spuType": "SINGLE"
                        }
                    }
                ],
                "one2oneAudiences": [{"audienceId": i, "sessionId": self.session_id} for i in audience_ids]
            }
        elif self.deliver_method == "VENUE_E":
            data = {
                "priceItemParam": [
                    {
                        "applyTickets": [],
                        "priceItemName": "票款总额",
                        "priceItemVal": self.price * qty,
                        "priceItemType": "TICKET_FEE",
                        "priceItemSpecies": "SEAT_PLAN",
                        "direction": "INCREASE",
                        "priceDisplay": "￥" + str(self.price * qty)
                    }
                ],
                "items": [
                    {
                        "skus": [
                            {
                                "seatPlanId": self.seat_plan_id,
                                "sessionId": self.session_id,
                                "showId": self.show_id,
                                "skuId": self.seat_plan_id,
                                "skuType": "SINGLE",
                                "ticketPrice": self.price,
                                "qty": qty,
                                "deliverMethod": self.deliver_method
                            }
                        ],
                        "spu": {
                            "id": self.show_id,
                            "spuType": "SINGLE"
                        }
                    }
                ]
            }
        else:
            raise Exception("不支持的deliver_method:" + str(self.deliver_method))

        url = "https://m.piaoxingqiu.com/cyy_gatewayapi/trade/buyer/order/v3/create_order"
        response = requests.post(url=url, headers=headers, json=data).json()
        if response["statusCode"] == 200:
            print("下单成功！请尽快支付！")
        else:
            raise Exception("下单异常:" + str(response))

    # 主函数
    def main(self):
        # 创建随机的useragent
        useragent = self.user_agent.random
        while True:
            try:
                # 获取座位余票信息，默认从最低价开始
                seat_plans = self.get_seat_plans(useragent)
                # print(seat_plans)
                seat_count = self.get_seat_count(useragent)
                # print(seat_count)

                # 获取想要购买的票价id,这里记得输入正确且对应的票价id，不然一直循环
                self.seat_plan_id = '66571097c305df0001686d7'

                # 提取出对应的票价
                for temp in seat_plans:
                    if temp["seatPlanId"] == self.seat_plan_id:
                        self.price = temp["originalPrice"]
                        self.seatPlanName = temp["seatPlanName"]
                        break

                # 判断对应的票价id是否有剩余票数
                for i in seat_count:
                    if i["seatPlanId"] == self.seat_plan_id:
                        if i["canBuyCount"] > 0:
                            self.flag = True
                            # print(f'{self.seatPlanName}该价位剩余数量：可满足您的购买需求')
                            break
                        else:
                            self.flag = False
                            # print(f'{self.seatPlanName}无剩余！')
                            break

                if self.flag:
                    print(f'{self.seatPlanName}该价位剩余数量：可满足您的购买需求')
                    print('正在努力抢购中……')
                else:
                    print(f'{self.seatPlanName}票价无剩余！,将继续为你刷新抢购')
                    continue

                if not self.deliver_method:
                    self.deliver_method = self.get_deliver_method(useragent, self.buy_count)
                print("演唱票类型:" + self.deliver_method)

                if self.deliver_method == "VENUE_E":
                    self.create_order(useragent, self.buy_count, 0, None, None, None, None, None, [])
                else:
                    # 获取观演人信息
                    audiences = self.get_audiences(useragent)
                    if len(self.audience_idx) == 0:
                        self.audience_idx = range(self.buy_count)
                    audience_ids = [audiences[i]["id"] for i in self.audience_idx]

                    if self.deliver_method == "EXPRESS":
                        # 获取默认收货地址
                        address = self.get_address(useragent)
                        address_id = address["addressId"]  # 地址id
                        location_city_id = address["locationId"]  # 460102
                        receiver = address["username"]  # 收件人
                        cellphone = address["cellphone"]  # 电话
                        detail_address = address["detailAddress"]  # 详细地址

                        # 获取快递费用
                        express_fee = self.get_express_fee(useragent, self.buy_count, location_city_id)

                        self.create_order(useragent, self.buy_count, express_fee["priceItemVal"], receiver,
                                          cellphone, address_id, detail_address, location_city_id, audience_ids)
                    elif self.deliver_method == "VENUE" or self.deliver_method == "E_TICKET" or self.deliver_method == "ID_CARD":
                        self.create_order(useragent, self.buy_count, 0, None, None, None, None, None, audience_ids)
                    else:
                        print("不支持的deliver_method:" + self.deliver_method)
                break
            except Exception as e:
                print(e)


if __name__ == '__main__':
    # 创建对象
    pxq = PXQ()
    while True:
        now = datetime.datetime.now()
        # 判断当前时间与设置的开抢时间，并进行倒计时，当当前时间大于开抢时间直接开抢
        if now < pxq.startTime:
            print(f"{int(pxq.startTime.timestamp()-now.timestamp())}秒后开抢", end="\r")
        else:
            pxq.main()
            break

