import os
import time
import random
import json
import base64
import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from urllib.parse import quote
from datetime import datetime

# ======================
# 环境变量配置
# ======================
# 变量名: lcc
# 格式: 手机号&用户ID&推送token（推送token可选）
# 多账号用 @ 分割
# 示例: 18312345678&12345678&pushplus_token@18387654321&87654321
FINISH_TIMES_FILE = "finish_times.json"
def init_finish_times_file():
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(FINISH_TIMES_FILE):
        init_data = {"last_update": today}
        with open(FINISH_TIMES_FILE, "w", encoding="utf-8") as f:
            json.dump(init_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 首次运行，自动创建文件: {FINISH_TIMES_FILE}")
        return  
    try:
        with open(FINISH_TIMES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)  
        if data.get("last_update") != today:
            reset_data = {"last_update": today}
            with open(FINISH_TIMES_FILE, "w", encoding="utf-8") as f:
                json.dump(reset_data, f, ensure_ascii=False, indent=2)
            print(f"🔄 跨天检测：当前日期 {today}，已重置所有账号的广告次数记录")
    except Exception as e:
        init_data = {"last_update": today}
        with open(FINISH_TIMES_FILE, "w", encoding="utf-8") as f:
            json.dump(init_data, f, ensure_ascii=False, indent=2)
        print(f"⚠️ 文件读取异常，重建文件：{e}")
init_finish_times_file()
PUBLIC_KEY = RSA.import_key(
    """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCS2vUGcnNMb3OxWyUn+bRpEHA+
01aV2/VqCefi8h21feQT93purzsD8E7Co2Cw7Mzd/kkzy++Cib21xkF8uW6j3LKy
rzVbR9MdZtEtT5IDAnjlQoOKeNwQdBjqcdi3gKxCdgYNNHfmQS3RjRcmz2ZgEOHB
qDNY4y9EWra0UxTKXQIDAQAB
-----END PUBLIC KEY-----"""
)
cipher = PKCS1_v1_5.new(PUBLIC_KEY)
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://h5.lvcchong.com",
    "Referer": "https://h5.lvcchong.com/",
}

log_messages = []
def log(msg: str):
    print(msg)
    log_messages.append(msg)

def pushplus(title: str, content: str, token: str):
    if not token:
        print("⚠️ 未配置推送token，跳过推送")
        return
    
    url = "https://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "txt",
    }
    try:
        r = requests.post(url, json=data, timeout=10)
        j = r.json()
        if j.get("code") == 200:
            print("✅ PushPlus 推送成功")
        else:
            print(f"❌ PushPlus 推送失败：{j.get('msg', j)}")
    except Exception as e:
        print(f"❌ PushPlus 推送异常：{e}")
def encrypt(data: str) -> str:
    ct = cipher.encrypt(data.encode())
    return quote(base64.b64encode(ct).decode())
def login(phone: str, userid: str) -> str | None:
    url = "https://appapi.lvcchong.com/appBaseApi/h5/accessEntrance"
    data = {
        "phone": phone,
        "ownerId": 0,
        "userid": userid,
        "time": int(time.time() * 1000),
    }
    r = requests.post(url, headers=BASE_HEADERS, data=data, timeout=10)
    j = r.json()
    if j.get("code") == 200:
        log("登录成功")
        return j["data"]["userToken"]
    log(f"登录失败：{j.get('message', j)}")
    return None
def sign(token: str):
    r = requests.post(
        "https://appapi.lvcchong.com/appBaseApi/scoreUser/sign/userSign",
        headers={**BASE_HEADERS, "token": token},
        data={"sourceType": 3},
        timeout=10,
    )
    j = r.json()
    if j.get("code") == 200:
        log(f"签到成功，获得 {j['data']['score']} 积分")
    else:
        log(f"签到失败：{j.get('message', j)}")
def get_ad_times(token: str) -> int:
    r = requests.post(
        "https://appapi.lvcchong.com/appBaseApi/scoreUser/task/getTaskList",
        headers={**BASE_HEADERS, "token": token},
        data={"sourceType": "3", "version": "1"},
        timeout=10,
    )
    j = r.json()
    if j.get("code") == 200 and len(j["data"]) > 1:
        return j["data"][1].get("finishTimes", 0)
    return 0
def do_ad(token: str, nth: int):
    timestamp = str(int(time.time() * 1000))
    payload = {"taskType": 7, "status": 1, "isApp": 0, "sourceType": 3}
    content = encrypt(json.dumps(payload, separators=(",", ":")))
    nonce = encrypt(timestamp)
    url = f"https://appapi.lvcchong.com/appBaseApi/scoreUser/task/receiveTaskScore?timestamp={timestamp}&nonce={nonce}"
    r = requests.post(
        url,
        headers={**BASE_HEADERS, "token": token},
        data={"content": content},
        timeout=10,
    )
    j = r.json()
    log(f"第{nth}次广告 → {j.get('message', j)}")
def read_finish_times():
    try:
        with open(FINISH_TIMES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if k != "last_update"}
    except Exception as e:
        log(f"读取完成次数文件失败：{e}")
        return {}
def update_finish_times(phone: str, times: int):
    try:
        with open(FINISH_TIMES_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    except:
        all_data = {"last_update": datetime.now().strftime("%Y-%m-%d")}
    all_data[phone] = times
    try:
        with open(FINISH_TIMES_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"更新完成次数文件失败：{e}")
def parse_account(item: str):
    parts = item.strip().split("&")
    if len(parts) < 2:
        return None, None, None
    phone = parts[0].strip()
    userid = parts[1].strip()
    push_token = parts[2].strip() if len(parts) >= 3 else None
    return phone, userid, push_token
def main():
    raw = os.getenv("lcc")
    if not raw:
        print("=" * 50)
        print("❌ 未设置环境变量 lcc")
        print("=" * 50)
        return
    log(f"🚀 驴充充任务开始执行 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    accounts = raw.split("@")
    push_tokens = set()
    finish_times = read_finish_times()
    for idx, item in enumerate(accounts, 1):
        phone, userid, push_token = parse_account(item)  
        if not phone or not userid:
            log(f"❌ 账号格式错误: {item}")
            continue
        if push_token:
            push_tokens.add(push_token) 
        log(f"\n{'='*15} 第{idx}个账号 {phone} {'='*15}")
        stored_times = finish_times.get(phone, 0)
        if stored_times >= 10:
            log(f"本地记录该账号已完成 {stored_times} 次广告，达到上限，跳过广告任务")
            token = login(phone, userid)
            if token:
                sign(token)
            continue
        token = login(phone, userid)
        if not token:
            continue
        sign(token)
        done = get_ad_times(token)
        log(f"今日已完成广告：{done} 次")
        update_finish_times(phone, done) 
        if done >= 10:
            log("今日广告已满10次，跳过")
            continue
        need = 10 - done
        log(f"还需 {need} 次")
        for i in range(1, need + 1):
            do_ad(token, i)
            update_finish_times(phone, done + i)
            if i < need:
                delay = random.randint(2, 5)
                log(f"等待 {delay}s 后继续...")
                time.sleep(delay)
        log(f"账号 {phone} 全部任务完成！")
    log(f"\n{'='*15} 任务执行完毕 {'='*15}")
    if log_messages and push_tokens:
        for token in push_tokens:
            pushplus("驴充充任务通知", "\n".join(log_messages), token)
    elif not push_tokens:
        print("⚠️ 未配置任何推送token，跳过推送")
if __name__ == "__main__":
    main()