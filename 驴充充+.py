import requests
import time
import random  
from urllib.parse import urlencode
import sys
import base64
import json
import urllib.parse as urlparse
import os 
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

PRIVATE_PEM = '''-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCS2vUGcnNMb3OxWyUn+bRpEHA+01aV2/VqCefi8h21feQT93pu
rzsD8E7Co2Cw7Mzd/kkzy++Cib21xkF8uW6j3LKyrzVbR9MdZtEtT5IDAnjlQoOK
eNwQdBjqcdi3gKxCdgYNNHfmQS3RjRcmz2ZgEOHBqDNY4y9EWra0UxTKXQIDAQAB
AoGAeGzRLT5BSlbCupeRepyL0vRF9176y90Z/KCu5S3CKwhXNgBlB8ruTCaNj5LG
QY+N2CUkBjOf7p3hUeSH4y10ifD57uW0KuQhsCrfAP84g+W/8CxccpBx6Qd6wqbL
0tgqbYRIHmaT0H1IILVXC8o1EwpO8z9d3u5PWhfkhfsuRkkCQQDCzyaiDuhcQcPC
xxljdCUXVTI1oCmhtbiesLT3VhRyQynPFhP/SIt0JK/IM6MpEL2AY/Iy52HVSsb5
iOkaR/6zAkEAwPvGW7u78XZUhalmAYHRni5eubbrv9W/R9sdCM2lDCf2MveLT3zt
jyLE5JYSy+U14iNL5foM7Wnk+GNzU8KarwJBAIaAwjrIMjRoj8Hu95+MNIPMpfMS
l0v4jPS8KuZOv6U4rCg4JSxwKSDSp6+Bv5h932lDGJl+2jSLAaCOn+suZDMCQBTg
qBrwemqq9IXpR6HOG5FTTugkg+ijBSiO6dsz9DEWeaoV4bpdt42Oo2JfYfUw/N1U
GDfvD0r3889zYtyi5v0CQQCDLekGtoErSLeZ1DpXkUpbd5DoJLQ1BryIxsJVL+3K
9aaKVlydsziJMkWan/e84eC5ON2+uDMFwV/ueqLYOJO5
-----END RSA PRIVATE KEY-----'''
PUBLIC_PEM = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCS2vUGcnNMb3OxWyUn+bRpEHA+
01aV2/VqCefi8h21feQT93purzsD8E7Co2Cw7Mzd/kkzy++Cib21xkF8uW6j3LKy
rzVbR9MdZtEtT5IDAnjlQoOKeNwQdBjqcdi3gKxCdgYNNHfmQS3RjRcmz2ZgEOHB
qDNY4y9EWra0UxTKXQIDAQAB
-----END PUBLIC KEY-----'''

class lcc: 
    def __init__(self, phone, userid):
        self.phone = phone
        self.userid = userid
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254162e) XWEB/18151 miniProgram/wx0132aa93a8b214ae",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://h5.lvcchong.com", 
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://h5.lvcchong.com/",  
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
    
    def login(self):
        url = "https://appapi.lvcchong.com/appBaseApi/h5/accessEntrance"
        data = {
            "phone": self.phone,
            "ownerId": 0,
            "userid": self.userid,
            "time": str(int(time.time() * 1000)),
        }
        try:
            response = requests.post(url, headers=self.headers, data=data, timeout=10)
            response.raise_for_status()  # 抛出HTTP异常
            re = response.json()
            code = re.get("code")
            if code == 200 and "data" in re and "userToken" in re["data"]:
                userToken = re["data"]["userToken"]
                msg = re["message"] if "message" in re else ""
                print(f"token更新结果：{msg}")
                return userToken
            elif code == -1:
                msg = re["message"] if "message" in re else "未知原因"
                print(f"token更新失败：{msg}")    
                return None
            else:
                print(f"登录接口返回异常，code：{code}")
                return None
        except Exception as e:
            print(f"登录请求出错：{str(e)}")
            return None
    
    def sign(self, userToken):
        url = "https://appapi.lvcchong.com/appBaseApi/scoreUser/sign/userSign"
        data = {
            "sourceType": 3
        }
        self.headers["token"] = userToken
        try:
            response = requests.post(url, headers=self.headers, data=data, timeout=10)
            response.raise_for_status()
            re = response.json()
            code = re.get("code")
            if code == 200 and "data" in re and "score" in re["data"]:
                score = re["data"]["score"]
                print(f"恭喜获得{score}积分")
            elif code == -1:
                message = re["message"] if "message" in re else "未知错误"
                print(f"签到失败：{message}")
            else:
                print(f"签到接口返回异常，code：{code}")
        except Exception as e:
            print(f"签到请求出错：{str(e)}")
    
    def ls(self, userToken):
        url = "https://appapi.lvcchong.com/appBaseApi/scoreUser/task/getTaskList"
        data = {
            "sourceType": "3",
            "version": "1"
        }
        self.headers["token"] = userToken
        try:
            response = requests.post(url, headers=self.headers, data=data, timeout=10)
            response.raise_for_status()
            re = response.json()
            code = re.get("code")
            if code == 200 and "data" in re:
                if len(re["data"]) > 1 and "finishTimes" in re["data"][1]:
                    finishTimes = re["data"][1]["finishTimes"]
                    return finishTimes
                else:
                    return 0
            elif code == -1:
                message = re["message"] if "message" in re else "未知错误"
                print(f"获取广告次数失败：{message}")
                return 0
            else:
                print(f"获取广告次数接口返回异常，code：{code}")
                return 0
        except Exception as e:
            print(f"获取广告次数请求出错：{str(e)}")
            return 0
    
    def gg(self, userToken, task_num):
        """
        执行广告任务
        :param userToken: 用户令牌
        :param task_num: 当前执行的是第几次广告任务（用于日志输出）
        """
        try:
            timestamp = str(int(time.time() * 1000))
            pub = RSA.import_key(PUBLIC_PEM)
            payload = {"taskType":7,"status":1,"isApp":0,"sourceType":3}
            content_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
            cipher = PKCS1_v1_5.new(pub)
            ct_nonce = cipher.encrypt(timestamp.encode('utf-8'))
            ct_content = cipher.encrypt(content_bytes)
            nonce_b64 = base64.b64encode(ct_nonce).decode('ascii')
            content_b64 = base64.b64encode(ct_content).decode('ascii')
            nonce_url = urlparse.quote(nonce_b64)
            content_url = urlparse.quote(content_b64)
            
            url = f"https://appapi.lvcchong.com/appBaseApi/scoreUser/task/receiveTaskScore?timestamp={timestamp}&nonce={nonce_url}"
            data = {
                "content": content_url
            }
            self.headers["token"] = userToken
            response = requests.post(url, headers=self.headers, data=data, timeout=10)
            response.raise_for_status()
            re = response.json()
            code = re.get("code")
            if code == 200 and "message" in re:
                message = re["message"]
                print(f"第{task_num}次广告结果：{message}")
            elif code == -1:
                message = re["message"] if "message" in re else "未知错误"
                print(f"第{task_num}次广告任务失败：{message}")
            else:
                print(f"第{task_num}次广告接口返回异常，code：{code}")
        except Exception as e:
            print(f"第{task_num}次广告任务请求出错：{str(e)}")

if __name__ == "__main__":
    lcc_env = os.environ.get('lcc')
    if not lcc_env:
        print("请转人工执行，未检测到环境变量")
    else:
        lcc_list = lcc_env.split('@')
        for num, lcc_item in enumerate(lcc_list, start=1):
            print(f"\n=====开始执行第{num}个账号任务=====")
            phone, userid = lcc_item.split('&')
            client = lcc(phone, userid)
            userToken = client.login()
            if userToken:
                client.sign(userToken)
                finish_times = client.ls(userToken)
                print(f"账号 {phone} 已完成广告次数：{finish_times}")
                
                if finish_times >= 10:
                    print(f"\n❌ 账号 {phone} 广告次数已达到或超过10次，跳过执行")
                else:
                    loop_count = 10 - finish_times
                    if loop_count > 0:
                        for i in range(loop_count):
                            task_num = i + 1
                            print(f"\n=== 账号 {phone} 正在执行第{task_num}次广告任务 ===")
                            client.gg(userToken, task_num)
                            if i < loop_count - 1:
                                delay = random.randint(20, 35)
                                print(f"账号 {phone} 第{task_num}次广告任务完成，将延迟{delay}秒执行下一次...")
                                time.sleep(delay)
                        print(f"\n✅ 账号 {phone} 所有广告任务执行完毕！")
                    else:
                        print(f"\n❌ 账号 {phone} 无广告任务可执行")
            else:
                print(f"\n❌ 账号 {phone} 登录失败，无法继续执行后续操作")