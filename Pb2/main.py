import requests , os , psutil , sys , jwt , pickle , json , binascii , time , urllib3 , base64 , datetime , re , socket , threading , ssl , pytz , aiohttp
from protobuf_decoder.protobuf_decoder import Parser
from xC4 import * ; from xHeaders import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Pb2 import DEcwHisPErMsG_pb2 , MajoRLoGinrEs_pb2 , PorTs_pb2 , MajoRLoGinrEq_pb2 , sQ_pb2 , Team_msg_pb2
from cfonts import render, say


#EMOTES BY DEKA X CODEX
# FIXED BY Duy Khanh


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  
online_writer = None
whisper_writer = None
spam_room = False
spammer_uid = None
spam_chat_id = None
spam_uid = None
Spy = False
Chat_Leave = False
#------------------------------------------#
 
####################################

#Clan-info-by-clan-id
def Get_clan_info(clan_id):
    try:
        url = f"https://get-clan-info.vercel.app/get_clan_info?clan_id={clan_id}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            msg = f""" 
[11EAFD][b][c]
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
▶▶▶▶GUILD DETAILS◀◀◀◀
Achievements: {data['achievements']}\n\n
Balance : {fix_num(data['balance'])}\n\n
Clan Name : {data['clan_name']}\n\n
Expire Time : {fix_num(data['guild_details']['expire_time'])}\n\n
Members Online : {fix_num(data['guild_details']['members_online'])}\n\n
Regional : {data['guild_details']['regional']}\n\n
Reward Time : {fix_num(data['guild_details']['reward_time'])}\n\n
Total Members : {fix_num(data['guild_details']['total_members'])}\n\n
ID : {fix_num(data['id'])}\n\n
Last Active : {fix_num(data['last_active'])}\n\n
Level : {fix_num(data['level'])}\n\n
Rank : {fix_num(data['rank'])}\n\n
Region : {data['region']}\n\n
Score : {fix_num(data['score'])}\n\n
Timestamp1 : {fix_num(data['timestamp1'])}\n\n
Timestamp2 : {fix_num(data['timestamp2'])}\n\n
Welcome Message: {data['welcome_message']}\n\n
XP: {fix_num(data['xp'])}\n\n
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
[FFB300][b][c]MADE BY DEKA
            """
            return msg
        else:
            msg = """
[11EAFD][b][c]
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
Failed to get info, please try again later!!

°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
[FFB300][b][c]MADE BY DEKA
            """
            return msg
    except:
        pass
#GET INFO BY PLAYER ID
def get_player_info(player_id):
    url = f"https://like2.vercel.app/player-info?uid={player_id}&server={server2}&key={key2}"
    response = requests.get(url)
    print(response)    
    if response.status_code == 200:
        try:
            r = response.json()
            return {
                "Account Booyah Pass": f"{r.get('booyah_pass_level', 'N/A')}",
                "Account Create": f"{r.get('createAt', 'N/A')}",
                "Account Level": f"{r.get('level', 'N/A')}",
                "Account Likes": f" {r.get('likes', 'N/A')}",
                "Name": f"{r.get('nickname', 'N/A')}",
                "UID": f" {r.get('accountId', 'N/A')}",
                "Account Region": f"{r.get('region', 'N/A')}",
                }
        except ValueError as e:
            pass
            return {
                "error": "Invalid JSON response"
            }
    else:
        pass
        return {
            "error": f"Failed to fetch data: {response.status_code}"
        }
#CHAT WITH AI
def talk_with_ai(question):
    url = f"https://gemini-api-api-v2.vercel.app/prince/api/v1/ask?key=prince&ask={question}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        msg = data["message"]["content"]
        return msg
    else:
        return "An error occurred while connecting to the server."
#SPAM REQUESTS
def spam_requests(player_id):
    # This URL now correctly points to the Flask app you provided
    url = f"https://like2.vercel.app/send_requests?uid={player_id}&server={server2}&key={key2}"
    try:
        res = requests.get(url, timeout=20) # Added a timeout
        if res.status_code == 200:
            data = res.json()
            # Return a more descriptive message based on the API's JSON response
            return f"API Status: Success [{data.get('success_count', 0)}] Failed [{data.get('failed_count', 0)}]"
        else:
            # Return the error status from the API
            return f"API Error: Status {res.status_code}"
    except requests.exceptions.RequestException as e:
        # Handle cases where the API isn't running or is unreachable
        print(f"Could not connect to spam API: {e}")
        return "Failed to connect to spam API."
####################################

# ** NEW INFO FUNCTION using the new API **
def newinfo(uid):
    # Base URL without parameters
    url = "https://like2.vercel.app/player-info"
    # Parameters dictionary - this is the robust way to do it
    params = {
        'uid': uid,
        'server': server2,  # Hardcoded to bd as requested
        'key': key2
    }
    try:
        # Pass the parameters to requests.get()
        response = requests.get(url, params=params, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # Check if the expected data structure is in the response
            if "basicInfo" in data:
                return {"status": "ok", "data": data}
            else:
                # The API returned 200, but the data is not what we expect (e.g., error message in JSON)
                return {"status": "error", "message": data.get("error", "Invalid ID or data not found.")}
        else:
            # The API returned an error status code (e.g., 404, 500)
            try:
                # Try to get a specific error message from the API's response
                error_msg = response.json().get('error', f"API returned status {response.status_code}")
                return {"status": "error", "message": error_msg}
            except ValueError:
                # If the error response is not JSON
                return {"status": "error", "message": f"API returned status {response.status_code}"}

    except requests.exceptions.RequestException as e:
        # Handle network errors (e.g., timeout, no connection)
        return {"status": "error", "message": f"Network error: {str(e)}"}
    except ValueError: 
        # Handle cases where the response is not valid JSON
        return {"status": "error", "message": "Invalid JSON response from API."}

	
#ADDING-100-LIKES-IN-24H
def send_likes(uid):
    try:
        likes_api_response = requests.get(
             f"https://yourlikeapi/like?uid={uid}&server_name={server2}&x-vercel-set-bypass-cookie=true&x-vercel-protection-bypass={BYPASS_TOKEN}",
             timeout=15
             )
      
      
        if likes_api_response.status_code != 200:
            return f"""
[C][B][FF0000]━━━━━
[FFFFFF]Like API Error!
Status Code: {likes_api_response.status_code}
Please check if the uid is correct.
━━━━━
"""

        api_json_response = likes_api_response.json()

        player_name = api_json_response.get('PlayerNickname', 'Unknown')
        likes_before = api_json_response.get('LikesbeforeCommand', 0)
        likes_after = api_json_response.get('LikesafterCommand', 0)
        likes_added = api_json_response.get('LikesGivenByAPI', 0)
        status = api_json_response.get('status', 0)

        if status == 1 and likes_added > 0:
            # ✅ Success
            return f"""
[C][B][11EAFD]‎━━━━━━━━━━━━
[FFFFFF]Likes Status:

[00FF00]Likes Sent Successfully!

[FFFFFF]Player Name : [00FF00]{player_name}  
[FFFFFF]Likes Added : [00FF00]{likes_added}  
[FFFFFF]Likes Before : [00FF00]{likes_before}  
[FFFFFF]Likes After : [00FF00]{likes_after}  
[C][B][11EAFD]‎━━━━━━━━━━━━
[C][B][FFB300]Subscribe: [FFFFFF]SPIDEERIO YT [00FF00]!!
"""
        elif status == 2 or likes_before == likes_after:
            # 🚫 Already claimed / Maxed
            return f"""
[C][B][FF0000]━━━━━━━━━━━━

[FFFFFF]No Likes Sent!

[FF0000]You have already taken likes with this UID.
Try again after 24 hours.

[FFFFFF]Player Name : [FF0000]{player_name}  
[FFFFFF]Likes Before : [FF0000]{likes_before}  
[FFFFFF]Likes After : [FF0000]{likes_after}  
[C][B][FF0000]━━━━━━━━━━━━
"""
        else:
            # ❓ Unexpected case
            return f"""
[C][B][FF0000]━━━━━━━━━━━━
[FFFFFF]Unexpected Response!
Something went wrong.

Please try again or contact support.
━━━━━━━━━━━━
"""

    except requests.exceptions.RequestException:
        return """
[C][B][FF0000]━━━━━
[FFFFFF]Like API Connection Failed!
Is the API server (app.py) running?
━━━━━
"""
    except Exception as e:
        return f"""
[C][B][FF0000]━━━━━
[FFFFFF]An unexpected error occurred:
[FF0000]{str(e)}
━━━━━
"""
####################################
#CHECK ACCOUNT IS BANNED

Hr = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB51"}

# ---- Random Colores ----
def get_random_color():
    colors = [
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]",
        "[A52A2A]", "[800080]", "[000000]", "[808080]", "[C0C0C0]", "[FFC0CB]", "[FFD700]", "[ADD8E6]",
        "[90EE90]", "[D2691E]", "[DC143C]", "[00CED1]", "[9400D3]", "[F08080]", "[20B2AA]", "[FF1493]",
        "[7CFC00]", "[B22222]", "[FF4500]", "[DAA520]", "[00BFFF]", "[00FF7F]", "[4682B4]", "[6495ED]",
        "[5F9EA0]", "[DDA0DD]", "[E6E6FA]", "[B0C4DE]", "[556B2F]", "[8FBC8F]", "[2E8B57]", "[3CB371]",
        "[6B8E23]", "[808000]", "[B8860B]", "[CD5C5C]", "[8B0000]", "[FF6347]", "[FF8C00]", "[BDB76B]",
        "[9932CC]", "[8A2BE2]", "[4B0082]", "[6A5ACD]", "[7B68EE]", "[4169E1]", "[1E90FF]", "[191970]",
        "[00008B]", "[000080]", "[008080]", "[008B8B]", "[B0E0E6]", "[AFEEEE]", "[E0FFFF]", "[F5F5DC]",
        "[FAEBD7]"
    ]
    return random.choice(colors)

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload
    
async def GeNeRaTeAccEss(uid , password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": (await Ua()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"}
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=Hr, data=data) as response:
            if response.status != 200: return "Failed to get access token"
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return (open_id, access_token) if open_id and access_token else (None, None)

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.118.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return  await encrypted_proto(string)

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization']= f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto
    
async def decode_team_packet(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = sQ_pb2.recieved_chat()
    proto.ParseFromString(packet)
    return proto
    
async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9: headers = '0000000'
    elif uid_length == 8: headers = '00000000'
    elif uid_length == 10: headers = '000000'
    elif uid_length == 7: headers = '000000000'
    else: print('Unexpected length') ; headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"
     
async def cHTypE(H):
    if not H: return 'Squid'
    elif H == 1: return 'CLan'
    elif H == 2: return 'PrivaTe'
    
async def SEndMsG(H , message , Uid , chat_id , key , iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid': msg_packet = await xSEndMsgsQ(message , chat_id , key , iv)
    elif TypE == 'CLan': msg_packet = await xSEndMsg(message , 1 , chat_id , chat_id , key , iv)
    elif TypE == 'PrivaTe': msg_packet = await xSEndMsg(message , 2 , Uid , Uid , key , iv)
    return msg_packet

async def SEndPacKeT(OnLinE , ChaT , TypE , PacKeT):
    if TypE == 'ChaT' and ChaT: whisper_writer.write(PacKeT) ; await whisper_writer.drain()
    elif TypE == 'OnLine': online_writer.write(PacKeT) ; await online_writer.drain()
    else: return 'UnsoPorTed TypE ! >> ErrrroR (:():)' 
           
async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer , spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , XX , uid , Spy,data2, Chat_Leave
    while True:
        try:
            reader , writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            online_writer.write(bytes_payload)
            await online_writer.drain()
            while True:
                data2 = await reader.read(9999)
                if not data2: break
                
                if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                    try:
                        print(data2.hex()[10:])
                        packet = await DeCode_PackEt(data2.hex()[10:])
                        print(packet)
                        packet = json.loads(packet)
                        OwNer_UiD , CHaT_CoDe , SQuAD_CoDe = await GeTSQDaTa(packet)

                        JoinCHaT = await AutH_Chat(3 , OwNer_UiD , CHaT_CoDe, key,iv)
                        await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , JoinCHaT)


                        message = f'[B][C]Tất Cả Tránh Ra [00ffd4]Duy Khanh[FFFFFF]Đã Vào [00ff00] Quỳ Xuống!\n[FFFFFF]× Tiktok: [00ffb3]@dekadev0\n[FFFFFF]× Tel[c]egr[c]am: [00ffb3]@dekadevz\n[FFFFFF]× Facebook: [00ffb3]Duy Khanh\n\nDuy Khanh:\n[C0C0C0]Mọi Người Th[c]uê Bot Team 5-6 - Bot Emotes Bật Hành Động Sú[c]n[c]g 7 Ai Cũng Nhìn Thấy Được IB TikTok. '
                        P = await SEndMsG(0 , message , OwNer_UiD , OwNer_UiD , key , iv)
                        await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)

                    except:
                        if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                            try:
                                print(data2.hex()[10:])
                                packet = await DeCode_PackEt(data2.hex()[10:])
                                print(packet)
                                packet = json.loads(packet)
                                OwNer_UiD , CHaT_CoDe , SQuAD_CoDe = await GeTSQDaTa(packet)

                                JoinCHaT = await AutH_Chat(3 , OwNer_UiD , CHaT_CoDe, key,iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , JoinCHaT)


                                message = f'[B][C]Tất Cả Tránh Ra [00ffd4]Duy Khanh[FFFFFF]Đã Vào [00ff00] Quỳ Xuống!\n[FFFFFF]× Tiktok: [00ffb3]@dekadev0\n[FFFFFF]× Tel[c]egr[c]am: [00ffb3]@dekadevz\n[FFFFFF]× Facebook: [00ffb3]Duy Khanh\n\nDuy Khanh:\n[C0C0C0]Mọi Người Th[c]uê Bot Team 5-6 - Bot Emotes Bật Hành Động Sú[c]n[c]g 7 Ai Cũng Nhìn Thấy Được IB TikTok\n\n{get_random_color()}- Commands : @a {xMsGFixinG('player_uid')} {xMsGFixinG('909000001')}\n\n[00FF00]Dev : @{xMsGFixinG('Spideerio')}'
                                P = await SEndMsG(0 , message , OwNer_UiD , OwNer_UiD , key , iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)
                            except:
                                pass

            online_writer.close() ; await online_writer.wait_closed() ; online_writer = None

        except Exception as e: print(f"- ErroR With {ip}:{port} - {e}") ; online_writer = None
        await asyncio.sleep(reconnect_delay)
                            
async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region , reconnect_delay=0.5):
    print(region, 'TCP CHAT')

    global spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , online_writer , chat_id , XX , uid , Spy,data2, Chat_Leave
    while True:
        try:
            reader , writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            whisper_writer.write(bytes_payload)
            await whisper_writer.drain()
            ready_event.set()
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                print('\n - TarGeT BoT in CLan ! ')
                print(f' - Clan Uid > {clan_id}')
                print(f' - BoT ConnEcTed WiTh CLan ChaT SuccEssFuLy ! ')
                pK = await AuthClan(clan_id , clan_compiled_data , key , iv)
                if whisper_writer: whisper_writer.write(pK) ; await whisper_writer.drain()
            while True:
                data = await reader.read(9999)
                if not data: break
                
                if data.hex().startswith("120000"):

                    msg = await DeCode_PackEt(data.hex()[10:])
                    chatdata = json.loads(msg)
                    try:
                        response = await DecodeWhisperMessage(data.hex()[10:])
                        uid = response.Data.uid
                        chat_id = response.Data.Chat_ID
                        XX = response.Data.chat_type
                        inPuTMsG = response.Data.msg.lower()
                    except:
                        response = None


                    if response:
                        if inPuTMsG.startswith(("/5")):
                            try:
                                dd = chatdata['5']['data']['16']
                                print('msg in private')
                                message = f"[B][C][00ff00]\n\n『 ACTIVE 』\n\n[00ffb3]Chấp Nhận Nhanh\n\n"
                                P = await SEndMsG(response.Data.chat_type , message , uid , chat_id , key , iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)
                                PAc = await OpEnSq(key , iv,region)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , PAc)
                                C = await cHSq(5, uid ,key, iv,region)
                                await asyncio.sleep(0.5)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , C)
                                V = await SEnd_InV(5 , uid , key , iv,region)
                                await asyncio.sleep(0.5)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , V)
                                E = await ExiT(None , key , iv)
                                await asyncio.sleep(3)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , E)
                            except:
                                print('msg in squad')

                    if response:
                        if inPuTMsG.startswith(("/6")):
                            try:
                                dd = chatdata['5']['data']['16']
                                print('msg in private')
                                message = f"[B][C][00ff00]\n\n『 ACTIVE 』   [00ffb3]Chấp Nhận Nhanh!\n\n"
                                P = await SEndMsG(response.Data.chat_type , message , uid , chat_id , key , iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)
                                PAc = await OpEnSq(key , iv,region)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , PAc)
                                C = await cHSq(5, uid ,key, iv,region)
                                await asyncio.sleep(0.5)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , C)
                                V = await SEnd_InV(5 , uid , key , iv,region)
                                await asyncio.sleep(0.5)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , V)
                                E = await ExiT(None , key , iv)
                                await asyncio.sleep(3)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , E)
                            except:
                                print('msg in squad')


                        if inPuTMsG.startswith('/x/'):
                            CodE = inPuTMsG.split('/x/')[1]
                            try:
                                dd = chatdata['5']['data']['16']
                                print('msg in private')
                                EM = await GenJoinSquadsPacket(CodE , key , iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , EM)


                            except:
                                print('msg in squad')



                if "1200" in data.hex()[0:4]:
                
                    json_result = get_available_room(data.hex()[10:])
                    #logging.info(data.hex())
                    parsed_data = json.loads(json_result)
                    try:
                        uid = parsed_data["5"]["data"]["1"]["data"]
                    except KeyError:
                        logging.warning("Warning: '1' key is missing in parsed_data, skipping...")
                        uid = None  # Set a default value
                    if "8" in parsed_data["5"]["data"] and "data" in parsed_data["5"]["data"]["8"]:
                        uexmojiii = parsed_data["5"]["data"]["8"]["data"]
                        if uexmojiii == "DefaultMessageWithKey":
                            pass
                        else:
                            clients.send(
                                self.GenResponsMsg(
                                f"""[FF0000][c]━━━━━━━━━━━━━━━━━━━━[/c]

[FFD700][b][c]Xin Chào! Mình Là DEKA BOT[/b]

[FFFFFF][c]Dùng Lệnh Bên Dưới Để Xem Danh Sách Lệnh:  

[32CD32][b][c]/🤔help[/b]

[FF0000][c]━━━━━━━━━━━━━━━━━━━━[/c]

[FFD700][b][c]Chúc Bạn Chơi Game Vui Vẻ[/b]

[1E90FF][b][c]CẢM ƠN BẠN ĐÃ ỦNG HỘ[/b]
[1E90FF][c]TELE: @dekadevz[/c]

[FFD700][b][c]Developer: DEKA[/b]

[FF0000][c]━━━━━━━━━━━━━━━━━━━━[/c]""",uid
                                )
                            )
                    else:
                        pass  


                    
                


                if "1200" in data.hex()[0:4] and b"/admin" in data:
                    try:
                        i = re.split("/admin", str(data))[1]
                        if "***" in i:
                            i = i.replace("***", "106")
                        sid = str(i).split("(\\x")[0]
                        json_result = get_available_room(data.hex()[10:])
                        
                        parsed_data = json.loads(json_result)
                        uid = parsed_data["5"]["data"]["1"]["data"]
                        clients.send(
                            self.GenResponsMsg(
                                f"""[C][B][FF0000]╔══════════╗
[FFFFFF]SINH NĂM 2009
[FFFFFF]Sống ở Lâm Đồng
[FFFFFF]SKILL: JAVA-PYTHON
[FF0000]╠══════════╣
[FFD700]OWNER : [FFFFFF]DEKA 
[FFD700]TL : [FFFFFF]@dekadevz 
[FFD700]TÊN  : [FFFFFF] Nguyễn Duy Khánh
[FF0000]╚══════════╝
[FFD700]✨ Developer —͟͞͞ </> DEKA  ⚡""", uid
                            )
                        )
                    except Exception as e:
                        logging.error(f"Error processing /admin command: {e}. Restarting.")
                        restart_program()
                




                        if inPuTMsG.strip().startswith('/vip'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    message = f"[B][C]{get_random_color()}Vui lòng nhập ít nhất 1 UID!\nVí dụ: /vip 123456789 987654321"
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uids = [int(x) for x in parts[1:6]]

                                default_emotes = [
                                    909049010, 909051003, 909033002, 909041005, 909038010,
                                    909039011, 909040010, 909000081, 909000085, 909000063,
                                    909000075, 909033001, 909000090, 909000068, 909000098,
                                    909035007, 909037011, 909038012, 909035012, 909042008,
                                    909035007, 909045001
                                ]

                                msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Bắt đầu chạy emote cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = f"[B][C]{get_random_color()}→ Đang gửi emote cho UID {target_uid}"
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(6)

                                        done_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã Hoàn Tất Emote Cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã Hoàn Tất Emote Cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"loi")
                                # file bố code remake con cặc

                        if inPuTMsG.strip().startswith('/co'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    message = f"[B][C]{get_random_color()}Vui lòng nhập ít nhất 1 UID!\nVí dụ: /co 123456789 987654321"
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uids = [int(x) for x in parts[1:6]]

                                default_emotes = [
                                    909000021, 909000020, 909000015, 909000011, 909000012,
                                    909000043, 909000037, 909000025, 909000008, 909000022
                                    
                                ]

                                msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Bắt đầu chạy emote cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Bắt đầu chạy emote cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(4,75)

                                        done_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã Hoàn Tất Emote Cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã Hoàn Tất Emote Cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"loi")
                                # file bố code remake con cặc

                        if inPuTMsG.strip().startswith('/hai'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    message = f"[B][C]{get_random_color()}Vui lòng nhập ít nhất 1 UID!\nVí dụ: /hai 123456789 987654321"
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uids = [int(x) for x in parts[1:6]]

                                default_emotes = [
                                    909040001, 909050011, 909051005, 909000006, 909034009,                                    
                                    909051002, 909038005, 909033009, 909000035, 909048014
                                    
                                ]

                                msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Bắt đầu chạy emote cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = f"[B][C]{get_random_color()}→ Đang gửi emote cho UID {target_uid}"
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(5)

                                        done_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã Hoàn Tất Emote Cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã Hoàn Tất Emote Cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"loi")
                                # file bố code remake con cặc

                        if inPuTMsG.strip().startswith('/ngau'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    message = f"[00ff00]Vui lòng nhập ít nhất 1 UID!\nVí dụ: /ngau 123456789 987654321"
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uids = [int(x) for x in parts[1:6]]

                                default_emotes = [
                                    909046015, 909050009, 909043002, 909041002, 909041001,
                                    909000072, 909000073, 909000069, 909000067, 909046016,
                                    909000145, 909000129, 909000121, 909000124, 909000089,
                                    
                                ]

                                msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Bắt đầu chạy emote cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = f"[B][C]{get_random_color()}→ Đang gửi emote cho UID {target_uid}"
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(4)

                                        done_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã Hoàn Tất Emote Cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã Hoàn Tất Emote Cho 1 UID...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"loi")
                                # file bố code remake con cặc

                        if inPuTMsG.strip().startswith('/l'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    message = f"[B][C]{get_random_color()}Vui lòng nhập ít nhất 1 UID!\nVí dụ: /l 123456789"
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uids = [int(x) for x in parts[1:6]]

                                default_emotes = [
                                    909049010, 909051003, 909033002, 909041005, 909038010,
                                    909039011, 909040010, 909000081, 909000085, 909000063,
                                    909000075, 909033001, 909000090, 909000068, 909000098,
                                    909035007, 909037011, 909038012, 909035012, 909042008,
                                    909035007, 909045001
                                ]

                                msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Bắt đầu chạy hành động LV7...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = f"[B][C]{get_random_color()}→ Đang gửi hành động LV7 cho UID {target_uid}"
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        # Tạo list riêng cho từng UID và shuffle để mỗi người KHÁC NHAU
                                        emo_list = default_emotes.copy()
                                        random.shuffle(emo_list)

                                        for emo_id in emo_list:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(4)

                                        done_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Hoàn Tất Gửi Hành Động LV7...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print("loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| Đã xong hành động LV7...[ffffff]Tele[c]gr[c]am: [00fffb]@dekadevz"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print("loi")

                        if inPuTMsG.strip().startswith('/ftg'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 3:
                                    msg = f"[B][C]{get_random_color()}Sai cú pháp!\nVí dụ:\n/ftg 123 ak47\n/ftg 111 222 333 mp40\n/ftg all scar\n/ftg 111 ak47 222 mp40 333 m60"
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                gun_emotes = {
                                    "ak47": 909000063,
                                    "scar": 909000068,
                                    "mp40": 909000075,
                                    "m1014": 909000081,
                                    "cgk": 909042008,
                                    "famas": 909000079,
                                    "ump": 909000098,
                                    "p90": 909049010,
                                    "mp40v2": 909040010,
                                    "m1014v2": 909039011,
                                    "m4a1": 909000085,
                                    "m1887": 909035007,
                                    "lv100": 909042007,
                                    "thonson": 909038010,
                                    "g18": 909038012,
                                    "an94": 909035012,
                                    "xm8": 909000085,
                                    "m60": 909051003,
                                    "parafal": 909045001
                                }

                                args = parts[1:]

                                uid_gun_pairs = []

                                # TH1: /ftg all tensung
                                if args[0].lower() == "all" and len(args) == 2:
                                    gun = args[1].lower()
                                    if gun not in gun_emotes:
                                        msg = f"[B][C]Tên súng không hợp lệ!\nHợp lệ: {', '.join(gun_emotes.keys())}"
                                        P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                        continue

                                    all_json = get_available_room(data.hex()[10:])
                                    all_players = json.loads(all_json)["5"]["data"].keys()
                                    for pl in all_players:
                                        uid_gun_pairs.append((int(pl), gun_emotes[gun]))

                                # TH2: /ftg uid1 uid2 uid3 tensung
                                elif args[-1].lower() in gun_emotes and all(a.isdigit() for a in args[:-1]):
                                    gun = args[-1].lower()
                                    emo = gun_emotes[gun]
                                    for u in args[:-1]:
                                        uid_gun_pairs.append((int(u), emo))

                                # TH3: /ftg uid1 gun1 uid2 gun2 uid3 gun3 ...
                                else:
                                    if len(args) % 2 != 0:
                                        msg = f"[B][C]Thiếu tham số! Phải dạng: UID súng UID súng..."
                                        P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                        continue

                                    for i in range(0, len(args), 2):
                                        uid = args[i]
                                        gun = args[i+1].lower()
                                        if not uid.isdigit() or gun not in gun_emotes:
                                            msg = f"[B][C]Sai format hoặc tên súng sai!"
                                            P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                            continue
                                        uid_gun_pairs.append((int(uid), gun_emotes[gun]))

                                start_msg = f"[B][C]{get_random_color()}→ Bắt đầu bật hành động cho {len(uid_gun_pairs)} UID"
                                S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                async def run_emote(t_uid, emo):
                                    try:
                                        H = await Emote_k(t_uid, emo, key, iv, region)
                                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                        await asyncio.sleep(0.5)
                                    except:
                                        pass

                                tasks = [asyncio.create_task(run_emote(u, e)) for u, e in uid_gun_pairs]
                                await asyncio.gather(*tasks)

                                done_msg = f"[B][C][00ff00]Hoàn tất action cho {len(uid_gun_pairs)} UID!"
                                D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)

                            except Exception as e:
                                print("loi ftg")


                        if inPuTMsG.startswith('/solo'):
                            leave = await ExiT(uid,key,iv)
                            await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , leave)

                        if inPuTMsG.strip().startswith('/s'):
                            EM = await FS(key , iv)
                            await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , EM)

                        if inPuTMsG.strip().startswith('!e'):

                            try:
                                dd = chatdata['5']['data']['16']
                                print('msg in private')
                                message = f"[B][C]{get_random_color()}\n\nLệnh Chỉ Được Dùng Trong Đội! \n\n"
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                            except:
                                print('msg in squad')

                                parts = inPuTMsG.strip().split()
                                print(response.Data.chat_type, uid, chat_id)
                                message = f'[B][C]{get_random_color()}\nACITVE TarGeT -> {xMsGFixinG(uid)}\n'

                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)

                                uid2 = uid3 = uid4 = uid5 = None
                                s = False

                                try:
                                    uid = int(parts[1])
                                    uid2 = int(parts[2])
                                    uid3 = int(parts[3])
                                    uid4 = int(parts[4])
                                    uid5 = int(parts[5])
                                    idT = int(parts[5])

                                except ValueError as ve:
                                    print("ValueError:", ve)
                                    s = True

                                except Exception:
                                    idT = len(parts) - 1
                                    idT = int(parts[idT])
                                    print(idT)
                                    print(uid)

                                if not s:
                                    try:
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                        H = await Emote_k(uid, idT, key, iv,region)
                                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)

                                        if uid2:
                                            H = await Emote_k(uid2, idT, key, iv,region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                        if uid3:
                                            H = await Emote_k(uid3, idT, key, iv,region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                        if uid4:
                                            H = await Emote_k(uid4, idT, key, iv,region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                        if uid5:
                                            H = await Emote_k(uid5, idT, key, iv,region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                        

                                    except Exception as e:
                                        pass


                        if inPuTMsG in ("/help"):
                            uid = response.Data.uid
                            chat_id = response.Data.Chat_ID
                            message = '[B][C][00ff00]Xin chào [00ff00]đây [00ff00] là [00ff00]danh sách lệnh\n[FFFFFF]× T[c]e[c]am 5-6\n => [00ffb3]/5\n[FFFFFF] => [00ffb3]/6\n\n[FFFFFF]× Bot Vào Đội\n=> [00ffb3]/x/ (teamcode)\n\n[FFFFFF]× full hành động lv7\n=> [00ffb3]/vip (uid)\n\n[FFFFFF]× full hành động cổ\n=> [00ffb3]/co (uid)\n\n[FFFFFF]× full hành động hài\n=> [00ffb3]/hai (uid)\n\n[FFFFFF]× full hành động ngầu\n=> [00ffb3]/ngau (uid)\n\n[FFFFFF]× random full hành động lv7\n => [00ffb3]/l (uid)\n\n[FFFFFF]× Bật hành động lv7 theo tên\n=> [00ffb3]/ftg (uid) (tensung)\n[00ffb3]Lưu Ý:\n[C0C0C0]Admin: @dekadevz                         '
                            P = await SEndMsG(response.Data.chat_type , message , uid , chat_id , key , iv)
                            await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)
                        response = None
                            
            whisper_writer.close() ; await whisper_writer.wait_closed() ; whisper_writer = None
                    
                    	
                    	
        except Exception as e: print(f"ErroR {ip}:{port} - {e}") ; whisper_writer = None
        await asyncio.sleep(reconnect_delay)

async def MaiiiinE():
    Uid , Pw = '4294804728','E01BEAC3490523AF192BBCB774EBC55E11EE11372228ADE92E790DC2F9F1A079'
    

    open_id , access_token = await GeNeRaTeAccEss(Uid , Pw)
    if not open_id or not access_token: print("ErroR - InvaLid AccounT") ; return None
    
    PyL = await EncRypTMajoRLoGin(open_id , access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE: print("TarGeT AccounT => BannEd / NoT ReGisTeReD ! ") ; return None
    
    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    print(UrL)
    region = MajoRLoGinauTh.region

    ToKen = MajoRLoGinauTh.token
    TarGeT = MajoRLoGinauTh.account_uid
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp
    
    LoGinDaTa = await GetLoginData(UrL , PyL , ToKen)
    if not LoGinDaTa: print("ErroR - GeTinG PorTs From LoGin DaTa !") ; return None
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
    OnLineiP , OnLineporT = OnLinePorTs.split(":")
    ChaTiP , ChaTporT = ChaTPorTs.split(":")
    acc_name = LoGinDaTaUncRypTinG.AccountName
    #print(acc_name)
    print(ToKen)
    equie_emote(ToKen,UrL)
    AutHToKen = await xAuThSTarTuP(int(TarGeT) , ToKen , int(timestamp) , key , iv)
    ready_event = asyncio.Event()
    
    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT , AutHToKen , key , iv , LoGinDaTaUncRypTinG , ready_event ,region))
     
    await ready_event.wait()
    await asyncio.sleep(1)
    task2 = asyncio.create_task(TcPOnLine(OnLineiP , OnLineporT , key , iv , AutHToKen))
    os.system('clear')
    print('')
    #print(' - ReGioN => {region}'.format(region))
    print(f"[ 𝘿𝙀𝙆𝘼 ] [ Online! Đã Khoá Mọi Truy Cập ] {TarGeT} | Name Acc : {acc_name}")
    print(f"[ 𝘿𝙀𝙆𝘼 ] [ Sau 14 Ngày Acc Của Mày Sẽ Trở Thành Của Tao ]")    
    print(f"[ 𝘿𝙀𝙆𝘼 ] [ </> 𝘿𝙪𝙮 𝙆𝙝𝙖𝙣𝙝 𝘽𝙤̂́ 𝘾𝙪̉𝙖 𝙁𝙧𝙚𝙚 𝙁𝙞𝙧𝙚 </> ]")    
    print(f"[ 𝘿𝙀𝙆𝘼 ] </> Trạng Thái | [=] | Hoạt Động Tốt")    
    await asyncio.gather(task1 , task2)
    
async def StarTinG():
    while True:
        try: await asyncio.wait_for(MaiiiinE() , timeout = 7 * 60 * 60)
        except asyncio.TimeoutError: print("Token ExpiRed ! , ResTartinG")
        except Exception as e: print(f"ErroR TcP - {e} => ResTarTinG ...")

if __name__ == '__main__':
    asyncio.run(StarTinG())