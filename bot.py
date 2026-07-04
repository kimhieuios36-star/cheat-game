import requests , os , psutil , sys , jwt , pickle , json , binascii , time , urllib3 , base64 , datetime , re , socket , threading , ssl , pytz , aiohttp
from protobuf_decoder.protobuf_decoder import Parser
from xC4 import * ; from xHeaders import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Pb2 import DEcwHisPErMsG_pb2 , MajoRLoGinrEs_pb2 , PorTs_pb2 , MajoRLoGinrEq_pb2 , sQ_pb2 , Team_msg_pb2
from cfonts import render, say
from flask import Flask, jsonify, request
import asyncio
import signal
import sys

import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

VIP_FILE = "vip_users.json"
ACTIVE_USERS_FILE = "active_users.json"

ADMIN_UIDS = ["4393628657"]  # <-- ĐỔI UID ADMIN

START_TIME = time.time()

    
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

# VariabLes dyli 
#------------------------------------------#
online_writer = None
whisper_writer = None
spam_room = False
spammer_uid = None
spam_chat_id = None
spam_uid = None
Spy = False
Chat_Leave = False
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None
spam_request_running = False
spam_request_task = None
evo_fast_spam_running = False
evo_fast_spam_task = None
evo_custom_spam_running = False
evo_custom_spam_task = None
lag_running = False
lag_task = None
#------------------------------------------#
 
####################################

# ===================== CORE =====================
async def handle_message(inPuTMsG, uid, chat_id, key, iv, chat_type):
    uid = str(uid)

    # ===== /rs =====
    if inPuTMsG == "/rs":
        if uid not in ADMIN_UIDS:
            await safe_send_message(chat_type, "❌ Không có quyền", uid, chat_id, key, iv)
            return
        await safe_send_message(chat_type, "♻️ Bot đang khởi động lại...", uid, chat_id, key, iv)
        await asyncio.sleep(1)
        restart_bot()

    # ===== /cpu =====
    if inPuTMsG == "/cpu":
        if uid not in ADMIN_UIDS:
            return
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        msg = (
            "[B][C][00FF00]📊 VPS STATUS\n\n"
            f"CPU: {cpu}%\n"
            f"RAM: {ram.used//1024//1024}MB / {ram.total//1024//1024}MB"
        )
        await safe_send_message(chat_type, msg, uid, chat_id, key, iv)
        return

    # ===== /uptime =====
    if inPuTMsG == "/uptime":
        uptime = format_time(time.time() - START_TIME)
        await safe_send_message(chat_type, f"⏱ Bot đã chạy: {uptime}", uid, chat_id, key, iv)
        return

    # ===== /status =====
    if inPuTMsG == "/status":
        msg = (
            "✅ BOT ĐANG HOẠT ĐỘNG\n"
            f"Uptime: {format_time(time.time() - START_TIME)}\n"
            f"CPU: {psutil.cpu_percent()}%"
        )
        await safe_send_message(chat_type, msg, uid, chat_id, key, iv)
        return

    # ===== /regcode =====
    if inPuTMsG.startswith("/regcode"):
        if uid not in ADMIN_UIDS:
            return
        parts = inPuTMsG.split()
        if len(parts) != 3:
            await safe_send_message(chat_type, "/regcode <code> <ngày>", uid, chat_id, key, iv)
            return

        code = parts[1]
        days = int(parts[2])
        vip = load_json(VIP_FILE)

        vip[code] = {
            "used": False,
            "expire": now_ts() + days * 86400,
            "uid": ""
        }

        save_json(VIP_FILE, vip)
        await safe_send_message(chat_type, f"✅ Tạo code {code} ({days} ngày)", uid, chat_id, key, iv)
        return

    # ===== /code =====
    if inPuTMsG.startswith("/code"):
        parts = inPuTMsG.split()
        vip = load_json(VIP_FILE)
        users = load_json(ACTIVE_USERS_FILE)

        if len(parts) != 2:
            return

        code = parts[1]
        if code not in vip:
            await safe_send_message(chat_type, "❌ Code không tồn tại", uid, chat_id, key, iv)
            return

        if vip[code]["used"]:
            await safe_send_message(chat_type, "❌ Code đã dùng", uid, chat_id, key, iv)
            return

        if now_ts() > vip[code]["expire"]:
            del vip[code]
            save_json(VIP_FILE, vip)
            await safe_send_message(chat_type, "❌ Code hết hạn", uid, chat_id, key, iv)
            return

        vip[code]["used"] = True
        vip[code]["uid"] = uid
        users[uid] = code

        save_json(VIP_FILE, vip)
        save_json(ACTIVE_USERS_FILE, users)

        await safe_send_message(chat_type, "✅ Kích hoạt VIP thành công", uid, chat_id, key, iv)
        return

    # ===== /xoacode =====
    if inPuTMsG.startswith("/xoacode"):
        if uid not in ADMIN_UIDS:
            return

        vip = load_json(VIP_FILE)
        users = load_json(ACTIVE_USERS_FILE)

        parts = inPuTMsG.split()
        if parts[1] == "all":
            vip.clear()
            users.clear()
        else:
            code = parts[1]
            if code in vip:
                u = vip[code].get("uid")
                if u in users:
                    del users[u]
                del vip[code]

        save_json(VIP_FILE, vip)
        save_json(ACTIVE_USERS_FILE, users)
        await safe_send_message(chat_type, "✅ Đã xoá code", uid, chat_id, key, iv)
        return

    # ===== CHECK VIP =====
    users = load_json(ACTIVE_USERS_FILE)
    if uid not in users:
        await safe_send_message(chat_type, NO_VIP_MSG, uid, chat_id, key, iv)
        return

#Clan-info-by-clan-id
def Get_clan_info(clan_id):
    try:
        url = f"https://get-clan-info.vercel.app/get_clan_info?clan_id={clan_id}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            msg = f""" 
[11EAFD][b][c]
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
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
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
[FFB300][b][c]MADE BY DEKA
            """
            return msg
        else:
            msg = """
[11EAFD][b][c]
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
Failed to get info, please try again later!!

°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
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

# Badge values for s1 to s8 commands - using your exact values
BADGE_VALUES = {
    "s1": 1048576,    # Your first badge
    "s2": 32768,      # Your second badge  
    "s3": 2048,       # Your third badge
    "s4": 64,         # Your fourth badge
    "s5": 262144     # Your seventh badge
}

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

# Helper functions for ghost join
def dec_to_hex(decimal):
    """Convert decimal to hex string"""
    hex_str = hex(decimal)[2:]
    return hex_str.upper() if len(hex_str) % 2 == 0 else '0' + hex_str.upper()

async def encrypt_packet(packet_hex, key, iv):
    """Encrypt packet using AES CBC"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    packet_bytes = bytes.fromhex(packet_hex)
    padded_packet = pad(packet_bytes, AES.block_size)
    encrypted = cipher.encrypt(padded_packet)
    return encrypted.hex()

async def nmnmmmmn(packet_hex, key, iv):
    """Wrapper for encrypt_packet"""
    return await encrypt_packet(packet_hex, key, iv)

async def ghost_join_packet(player_id, secret_code, key, iv):
    """Create ghost join packet"""
    try:
        # Create a simple packet structure for joining
        # This is a basic implementation - adjust based on your needs
        packet_data = f"01{dec_to_hex(len(secret_code))}{secret_code.encode().hex()}"
        
        # Encrypt the packet
        encrypted_packet = await encrypt_packet(packet_data, key, iv)
        
        # Create header
        header_length = len(encrypted_packet) // 2
        header_length_hex = dec_to_hex(header_length)
        
        # Build final packet based on header length
        if len(header_length_hex) == 2:
            final_packet = "0515000000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 3:
            final_packet = "051500000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 4:
            final_packet = "05150000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 5:
            final_packet = "0515000" + header_length_hex + encrypted_packet
        else:
            final_packet = "0515000000" + header_length_hex + encrypted_packet
            
        return bytes.fromhex(final_packet)
        
    except Exception as e:
        print(f"Error creating ghost join packet: {e}")
        return None

async def xSEndMsgsQ(Msg , id , K , V):
    fields = {1: id , 2: id , 4: Msg , 5: 1756580149, 7: 2, 8: 904990072, 9: {1: "xBe4!sTo - C4", 2: await xBunnEr(), 4: 330, 5: 827001005, 8: "xBe4!sTo - C4", 10: 1, 11: 1, 13: {1: 2}, 14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}}, 10: "VN", 13: {2: 2, 3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)     
    
async def xSEndMsg(Msg , Tp , Tp2 , id , K , V):
    feilds = {1: id , 2: Tp2 , 3: Tp, 4: Msg, 5: 13708513937, 7: 2, 9: {1: "xBesTo - C4", 2: int(await xBunnEr()), 3: 901048018, 4: 330, 5: 827001006, 8: "xBesTo - C4", 10: 1, 11: 1, 13: {1: 2}, 14: {1: 12484827014, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}, 12: 0}, 10: "VN", 13: {3: 1}}
    Pk = (await CrEaTe_ProTo(feilds)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)


async def safe_send_message(chat_type, message, target_uid, chat_id, key, iv, max_retries=3):
    """Safely send message with retry mechanism"""
    for attempt in range(max_retries):
        try:
            P = await SEndMsG(chat_type, message, target_uid, chat_id, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
            print(f"Message sent successfully on attempt {attempt + 1}")
            return True
        except Exception as e:
            print(f"Failed to send message (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)  # Wait before retry
    return False

async def lag_team_loop(team_code, key, iv, region):
    """Rapid join/leave loop to create lag"""
    global lag_running
    count = 0
    
    while lag_running:
        try:
            # Join the team
            join_packet = await GenJoinSquadsPacket(team_code, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            
            # Very short delay before leaving
            await asyncio.sleep(0.01)  # 10 milliseconds
            
            # Leave the team
            leave_packet = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
            
            count += 1
            print(f"Lag cycle #{count} completed for team: {team_code}")
            
            # Short delay before next cycle
            await asyncio.sleep(0.01)  # 10 milliseconds between cycles
            
        except Exception as e:
            print(f"Error in lag loop: {e}")
            # Continue the loop even if there's an error
            await asyncio.sleep(0.1)

async def request_join_with_badge(target_uid, badge_value, key, iv, region):
    """Send join request with specific badge - converted from your old TCP"""
    fields = {
        1: 33,
        2: {
            1: int(target_uid),
            2: region.upper(),
            3: 1,
            4: 1,
            5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]),
            6: "iG:[C][B][FF0000] KRISHNA",
            7: 330,
            8: 1000,
            10: region.upper(),
            11: bytes([49, 97, 99, 52, 98, 56, 48, 101, 99, 102, 48, 52, 55, 56,
                       97, 52, 52, 50, 48, 51, 98, 102, 56, 102, 97, 99, 54, 49, 50, 48, 102, 53]),
            12: 1,
            13: int(target_uid),
            14: {
                1: 2203434355,
                2: 8,
                3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
            },
            16: 1,
            17: 1,
            18: 312,
            19: 46,
            23: bytes([16, 1, 24, 1]),
            24: int(await xBunnEr()),
            26: "",
            28: "",
            31: {
                1: 1,
                2: badge_value  # Dynamic badge value
            },
            32: badge_value,    # Dynamic badge value
            34: {
                1: int(target_uid),
                2: 8,
                3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])
            }
        },
        10: "en",
        13: {
            2: 1,
            3: 1
        }
    }
    
    packet = (await CrEaTe_ProTo(fields)).hex()
    
    if region.lower() == "ind":
        packet_type = '0514'
    elif region.lower() == "bd":
        packet_type = "0519"
    else:
        packet_type = "0515"
        
    return await GeneRaTePk(packet, packet_type, key, iv)    


async def leave_squad(key, iv, region):
    """Leave squad - converted from your old TCP leave_s()"""
    fields = {
        1: 7,
        2: {
            1: 12480598706  # Your exact value from old TCP
        }
    }
    
    packet = (await CrEaTe_ProTo(fields)).hex()
    
    if region.lower() == "ind":
        packet_type = '0514'
    elif region.lower() == "bd":
        packet_type = "0519"
    else:
        packet_type = "0515"
        
    return await GeneRaTePk(packet, packet_type, key, iv)    

async def reset_bot_state(key, iv, region):
    """Reset bot to solo mode before spam - Critical step from your old TCP"""
    try:
        # Leave any current squad (using your exact leave_s function)
        leave_packet = await leave_squad(key, iv, region)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
        await asyncio.sleep(0.5)
        
        print("✅ Bot state reset - left squad")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting bot: {e}")
        return False    
 
async def handle_badge_command(cmd, inPuTMsG, uid, chat_id, key, iv, region, chat_type):
    """Handle individual badge commands"""
    parts = inPuTMsG.strip().split()
    if len(parts) < 2:
        error_msg = f"[B][C][FF0000]❌ Usage: /{cmd} (uid)\nExample: /{cmd} 123456789\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)
        return
    
    target_uid = parts[1]
    badge_value = BADGE_VALUES.get(cmd, 1048576)
    
    if not target_uid.isdigit():
        error_msg = f"[B][C][FF0000]❌ Please write a valid player ID!\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)
        return
    
    # Send initial message
    initial_msg = f"[B][C][1E90FF]🌀 Request received! Preparing to spam {target_uid}...\n"
    await safe_send_message(chat_type, initial_msg, uid, chat_id, key, iv)
    
    try:
        # Reset bot state
        await reset_bot_state(key, iv, region)
        
        # Create and send join packets
        join_packet = await request_join_with_badge(target_uid, badge_value, key, iv, region)
        spam_count = 50
        
        for i in range(spam_count):
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            print(f"✅ Đang Spam Lệnh /{cmd} yêu cầu#{i+1} với tích: {badge_value}")
            await asyncio.sleep(0.1)
        
        success_msg = f"[B][C][FFFFFF]Thành Công Spam Mời+Tích\n"
        await safe_send_message(chat_type, success_msg, uid, chat_id, key, iv)
        
        # Cleanup
        await asyncio.sleep(1)
        await reset_bot_state(key, iv, region)
        
    except Exception as e:
        error_msg = f"[B][C][FF0000]❌ Error in /{cmd}: {str(e)}\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)

async def spam_request_loop(target_uid, key, iv, region):
    """Spam request function that creates group and sends join requests in loop - FASTER VERSION"""
    global spam_request_running
    count = 0
    max_requests = 40
    
    while spam_request_running and count < max_requests:
        try:
            PAc = await OpEnSq(key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
            await asyncio.sleep(0.1)  # Reduced delay
            
            V = await SEnd_InV(5, int(target_uid), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
            
            E = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
            
            count += 1
            print(f"Sent request #{count} to {target_uid}")
            
            await asyncio.sleep(0.1)  
            
        except Exception as e:
            print(f"Error in spam_request_loop for uid {target_uid}: {e}")
            await asyncio.sleep(0.1)        

async def SEnd_InV_with_Cosmetics(Nu, Uid, K, V, region):
    """Simple version - just add field 5 with basic cosmetics"""
    region = "ind"
    fields = {
        1: 2, 
        2: {
            1: int(Uid), 
            2: region, 
            4: int(Nu),
            # Simply add field 5 with basic cosmetics
            5: {
                1: "BOT",                    # Name
                2: int(await xBunnEr()),     # Avatar
                5: random.choice([1048576, 32768, 2048]),  # Random badge
            }
        }
    }

    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
        
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)   


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
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
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
    
def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def now_ts():
    return int(time.time())

def restart_bot():
    print("Restarting bot...")
    time.sleep(1)
    os._exit(0)

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s"


           
async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer , spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , XX , uid , Spy,data2, Chat_Leave, fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task, spam_request_running, spam_request_task, evo_fast_spam_running, evo_fast_spam_task, evo_custom_spam_running, evo_custom_spam_task, lag_running, lag_task
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


                        message = f"""[B][C]Tất Cả Tránh Ra [00ffd4] Bố ANH CODE [FFFFFF]Đã Vào [00ff00] Quỳ Xuống!

[FFFFFF]× Tiktok: [00ffb3]@anhcodeclick
[FFFFFF]× Tel[c]egr[c]am: [00ffb3]@anhcodeclick
[FFFFFF]× Facebook: [00ffb3]ANH CODE

ANH CODE:
[C0C0C0]Mọi Người Th[c]uê Bot Team 5-6 - Bot Emotes Bật Hành Động Sú[c]n[c]g 7 Ai Cũng Nhìn Thấy Được IB TikTok"""
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


                                message = f"""[B][C]Tất Cả Tránh Ra [00ffd4] Bố ANH CODE[FFFFFF]Đã Vào [00ff00] Quỳ Xuống!

[FFFFFF]× Tiktok: [00ffb3]@anhcodeclick
[FFFFFF]× Tel[c]egr[c]am: [00ffb3]@anhcodeclick
[FFFFFF]× Facebook: [00ffb3]ANH CODE

ANH CODE:
[C0C0C0]Mọi Người Th[c]uê Bot Team 5-6 - Bot Emotes Bật Hành Động Sú[c]n[c]g 7 Ai Cũng Nhìn Thấy Được IB TikTok"""
                                P = await SEndMsG(0 , message , OwNer_UiD , OwNer_UiD , key , iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)
                            except:
                                pass

            online_writer.close() ; await online_writer.wait_closed() ; online_writer = None

        except Exception as e: print(f"- ErroR With {ip}:{port} - {e}") ; online_writer = None
        await asyncio.sleep(reconnect_delay)
                            
async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region , reconnect_delay=0.5):
    print(region, 'TCP CHAT')

    global spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , online_writer , chat_id , XX , uid , Spy,data2, Chat_Leave, fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task, spam_request_running, spam_request_task, evo_fast_spam_running, evo_fast_spam_task, evo_custom_spam_running, evo_custom_spam_task, lag_running, lag_task
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
                        
                        # Debug print to see what we're receiving
                        print(f"Received message: {inPuTMsG} from UID: {uid} in chat type: {XX}")
                        # ===================== MESSAGE =====================
                        NO_VIP_MSG = (
    "[C][B][FF0000]ANH CODE\n\n"
    "[C][B][C0C0C0]Tài khoản chưa được cấp quyền sử dụng bot\n"
    "Liên hệ Admin\n\n"
    "[11EAFD]Telegram: @anhcodeclick"
)
                        
                    except:
                        response = None
					
                    if response:
                        if inPuTMsG.startswith(("5")):
                            # Process /5 command in any chat type
                            initial_message = f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Create Squad: [00ffb3]5\n\n[C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Đã Tạo Thành Công Team 5 Free Fire. Vui Lòng Chấp Nhận L[c]ờ[c]i M[c]ời Bot Gửi Tới!"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            # Fast squad creation and invite
                            PAc = await OpEnSq(key, iv, region)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                            
                            C = await cHSq(5, uid, key, iv, region)
                            await asyncio.sleep(0.3)  # Reduced delay
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                            
                            V = await SEnd_InV(5, uid, key, iv, region)
                            await asyncio.sleep(0.3)  # Reduced delay
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                            
                            E = await ExiT(None, key, iv)
                            await asyncio.sleep(3.5)  # Reduced from 3 seconds
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                            
                            # SUCCESS MESSAGE
                            success_message = f"[B][C][00FF00]✅ SUCCESS! Đã Gửi Lời Mời Tới: [00ffb3]{uid}!\nVui Lòng Chấp Nhận Lời Mời\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)




                        if inPuTMsG.startswith('/x/'):
                            CodE = inPuTMsG.split('/x/')[1]
                            try:
                                dd = chatdata['5']['data']['16']
                                print('msg in private')
                                EM = await GenJoinSquadsPacket(CodE , key , iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , EM)


                            except:
                                print('msg in squad')

                        if inPuTMsG.startswith('cut'):
                            leave = await ExiT(uid,key,iv)
                            await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , leave)

                        if inPuTMsG.strip().startswith('post'):
                            EM = await FS(key , iv)
                            await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , EM)

                        if inPuTMsG.strip() == "giabot":
                            # Process /giabot command in any chat type
                            giabot_message = """[C][B][00ffb3]Giá [00ff00]Bot:

[C][B][FFFFFF]10k = 1 day

[C][B][FFFFFF]40k = 1 tuần

[C][B][FFFFFF]100k = 1 tháng

[C][B][FFFFFF]200k = 3 tháng

[C][B][FFFFFF]300k = 5 tháng

[C][B]Nếu Có Nhu Cầu Thuê Bot Vui Lòng Ib [ffffff]Tele[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7"""
                            await safe_send_message(response.Data.chat_type, giabot_message, uid, chat_id, key, iv)

                        if inPuTMsG.strip() == "admin":
                            # Process /admin command in any chat type
                            admin_message = """[B][C][9B30FF]
⚡ THÔNG TIN DEV 乂 ADMIN

[00E5FF]✘ DEV
[FFFFFF]=> 👑 [FFD700]ANH CODE

[FFD700]✘ NĂM SINH
[FFFFFF]=> [00FF7F]2008

[FF4DFF]✘ THÔNG TIN MXH
[FFFFFF]=> 📬 Tele     : [00FFAA]@anhcodeclick
[9B30FF]━━━━━━━━━━━━━━━━━━━━

[00E5FF]✘ THÔNG TIN KHÁC
[FFFFFF]=> 🛡️ [FFD700]tôi là ANH CODE

[FFD700]✘ SỞ THÍCH
[FFFFFF]=> [00FF7F]ăn vật hoặc bánh

[FF4DFF]✘ ĐANG ĐỘC THÂN
[FFFFFF]=> 🎵 lập Trình : [00FFAA]Python
[FFFFFF]=> 📬 chạy bot     : [00FFAA]vps window
[FFFFFF]=> 📘 phiên bản   : [00FF7F]python 3.10.1"""
                            await safe_send_message(response.Data.chat_type, admin_message, uid, chat_id, key, iv)

                        if inPuTMsG.strip().startswith('atk '):
                            print('Processing lag command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f"[B][C][FF0000]❌ ERROR! Usage: atk (team_code)\nExample: atk ABC123\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                team_code = parts[1]
                                
                                # Stop any existing lag task
                                if lag_task and not lag_task.done():
                                    lag_running = False
                                    lag_task.cancel()
                                    await asyncio.sleep(0.1)
                                
                                # Start new lag task
                                lag_running = True
                                lag_task = asyncio.create_task(lag_team_loop(team_code, key, iv, region))
                                
                                # SUCCESS MESSAGE
                                success_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]|  Đang Spam Lag\n[ffffff]Nhóm Bị Spam: [00ffb3]{team_code}\n[ffffff]Te[c]le[c]gram: [00fffb]@anhcodeclick"
                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)

                        # STOP LAG COMMAND
                        if inPuTMsG.strip() == 'satk':
                            if lag_task and not lag_task.done():
                                lag_running = False
                                lag_task.cancel()
                                success_msg = f"[B][C][00FF00]✅ SUCCESS! Dừng Spam Thành Công!\n"
                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                            else:
                                error_msg = f"[B][C][FF0000]❌ ERROR! No active lag attack to stop!\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)


                        if inPuTMsG.strip().startswith('siv'):
                            print('Processing spam request in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f"[B][C][FF0000]❌ ERROR! Sai: /spm_inv (uid)\nVí Dụ: siv 123456789\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                try:
                                    target_uid = parts[1]
                                    
                                    # Stop any existing spam request
                                    if spam_request_task and not spam_request_task.done():
                                        spam_request_running = False
                                        spam_request_task.cancel()
                                        await asyncio.sleep(0.5)
                                    
                                    # Start new spam request
                                    spam_request_running = True
                                    spam_request_task = asyncio.create_task(spam_request_loop(target_uid, key, iv, region))
                                    
                                    # SUCCESS MESSAGE
                                    success_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]|Bắt Đầu Spam\n[00ffb3]Uid Bị Spam: [FFFFFF]{target_uid}"
                                    await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                        
                                except Exception as e:
                                    error_msg = f"[B][C][FF0000]❌ ERROR! {str(e)}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # Stop spam request command - works in all chat types
                        if inPuTMsG.strip() == 'ssiv':
                            if spam_request_task and not spam_request_task.done():
                                spam_request_running = False
                                spam_request_task.cancel()
                                success_msg = f"[B][C][00FF00]✅ SUCCESS! Thành Công!\n"
                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                            else:
                                error_msg = f"[B][C][FF0000]❌ ERROR! Lỗi!\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)



                        if inPuTMsG.strip().startswith('s1'):
                            await handle_badge_command('s1', inPuTMsG, uid, chat_id, key, iv, region, response.Data.chat_type)
    
                        if inPuTMsG.strip().startswith('s2'):
                            await handle_badge_command('s2', inPuTMsG, uid, chat_id, key, iv, region, response.Data.chat_type)

                        if inPuTMsG.strip().startswith('s3'):
                            await handle_badge_command('s3', inPuTMsG, uid, chat_id, key, iv, region, response.Data.chat_type)

                        if inPuTMsG.strip().startswith('s4'):
                            await handle_badge_command('s4', inPuTMsG, uid, chat_id, key, iv, region, response.Data.chat_type)

                        if inPuTMsG.strip().startswith('s5'):
                            await handle_badge_command('s5', inPuTMsG, uid, chat_id, key, iv, region, response.Data.chat_type)

                        if inPuTMsG.strip().startswith('s6'):
                            await handle_badge_command('s6', inPuTMsG, uid, chat_id, key, iv, region, response.Data.chat_type)

                        if inPuTMsG.strip().startswith('s7'):
                            await handle_badge_command('s7', inPuTMsG, uid, chat_id, key, iv, region, response.Data.chat_type)

                        if inPuTMsG.strip().startswith('s8'):
                            await handle_badge_command('s8', inPuTMsG, uid, chat_id, key, iv, region, response.Data.chat_type)

                        if inPuTMsG.strip().startswith('msg'):
                            try:
                                print("[msg] Nhảy vào lệnh msg (join team + spam team chat)")
                        
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 4:
                                    msg = (
                                        "[B][C][FF0000]Thiếu tham số!\n\n"
                                        "[FFFFFF]Cú pháp đúng:\n"
                                        "[00FF00]msg [teamcode] [nội_dung] [số_lần]\n"
                                        "[FFFFFF]VD: msg 123456 QuangHau 10"
                                    )
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue
                        
                                team_code = parts[1].strip()
                        
                                try:
                                    repeat_count = int(parts[-1])
                                except ValueError:
                                    msg = "[B][C][FF0000]1-100!"
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue
                        
                                msg_text = "[B][C] ".join(parts[2:-1]).strip()
                                if not msg_text:
                                    msg_text = (
                                        "[B][C]Tất Cả Tránh Ra [00ffd4]ANH CODE[FFFFFF]Đã Đá "
                                        "[00ff00]Live!\n\n"
                                        "[FFFFFF]× Tiktok: [00ffb3]@anhcodeclick\n"
                                        "[FFFFFF]× Telegram: [00ffb3]@anhcodeclick\n"
                                        "[FFFFFF]× Facebook: [00ffb3]ANH CODEy\n\n"
                                        "ANH CODE:\n"
                                        "[C0C0C0]Mọi Người Thuê Bot Team 5-6 - Bot Emotes "
                                        "Bật Hành Động Súng 7 Ai Cũng Nhìn Thấy Được IB TikTok."
                                    )
                        
                                repeat_count = max(1, min(repeat_count, 100))
                        
                                print(f"[msg] team_code={team_code}, repeat={repeat_count}, msg={msg_text!r}")
                        
                                start_msg = (
                                    f"[B][C][00FF00]『 SPAM TEAM 』[FFFFFF]Join team "
                                    f"[00FF00]{team_code} [FFFFFF]và gửi "
                                    f"[00FF00]{repeat_count} [FFFFFF]tin nhắn..."
                                )
                                P = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        
                                try:
                                    join_packet = await GenJoinSquadsPacket(team_code, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
                                    await asyncio.sleep(1.0)
                                except Exception as e:
                                    print(f"[msg] Lỗi join teamcode: {e}")
                                    continue
                        
                                sent = 0
                                for i in range(repeat_count):
                                    try:
                                        color = get_random_color()
                                        text = f"[B][C]{color}{msg_text}"
                                        P_team = await SEndMsG(0, text, uid, uid, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P_team)
                                        sent += 1
                                        await asyncio.sleep(0.08)
                                    except Exception as e:
                                        print(f"[msg] Lỗi gửi team chat lần {i+1}: {e}")
                                        break
                        
                                try:
                                    E = await ExiT(None, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                                    print("[msg] Đã out team sau khi spam.")
                                except Exception as e:
                                    print(f"[msg] Lỗi out team: {e}")
                        
                                done_msg = (
                                    f"[B][C][00FF00]『 HOÀN TẤT 』[FFFFFF]Đã gửi "
                                    f"[00FF00]{sent}[FFFFFF]/[00FF00]{repeat_count} "
                                    f"[FFFFFF]tin nhắn và out team thành công!"
                                )
                                P = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        
                            except Exception as e:
                                print("[ERROR msg]", e)



# ===== XỬ LÝ CHAT MESSAGE =====
                        if inPuTMsG and inPuTMsG.strip().startswith(('/start', 'hello', 'hi' , 'menu' , '/menu' , 'bot' , 'ê' , 'start' , 'ơi' , 'oi' , 'on' , 'help' , 'alo' , 'lo' , 'chat' , 'deka' , 'dekadev' , 'dekadevz')):
                            try:
                                # uid đã có sẵn giống Code2
                                # uid = response.Data.uid  (nếu bạn lấy uid kiểu này)

                                welcome_msg = (
                                    "[FF0000][c]━━━━━━━━━━━━━━━━━━━━[/c]\n\n"
                                    "[C][B][FFFFFF]Dùng Lệnh Bên Dưới Để Hiện Danh Sách Lệnh:\n\n"
                                    "[C][B][32CD32]help[/b]\n\n"
                                    "[C][B][00ffb3]ANH CODE:[/b]\n"
                                    "[C][B][C0C0C0]Th[c]uê Bot I[c]B [c]Te[c]le[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7[/b]\n\n"
                                    "[FF0000][c]━━━━━━━━━━━━━━━━━━━━[/c]"
                                )

                                P = await SEndMsG(
                                    response.Data.chat_type,
                                    welcome_msg,
                                    uid,
                                    chat_id,
                                    key,
                                    iv
                                )
                                await SEndPacKeT(
                                    whisper_writer,
                                    online_writer,
                                    'ChaT',
                                    P
                                )

                            except Exception as e:
                                print("welcome msg err:", e)

                                                   
                        if inPuTMsG.strip().startswith('ftg'):
                            parts = inPuTMsG.strip().split()
                        
                            if len(parts) < 4 or len(parts) % 2 != 0:
                                msg = (
                                    "[B][C][ff0000]Sai cú pháp!\n\n"
                                    "[ffffff]Ví Dụ:\n"
                                    "[00ff00]ftg [teamcode] [tensung1] [uid1] [tensung2] [uid2] ..."
                                )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                continue
                        
                            teamcode = parts[1]

                            emote_presets = {
                                "mp40v2": 909040010,
                                "mp40": 909000075,
                                "ak47": 909000063,
                                "m1887": 909035007,
                                "xm8": 909000085,
                                "famas": 909000090,
                                "ump": 909000098,
                                "parafal": 909045001,
                                "m1014": 909000081,
                                "m1014v2": 909039011,
                                "p90": 909049010,
                                "scar": 909000068,
                                "m4a1": 909039011,
                                "woodpecker": 909042008,
                                "thompson": 909038010,
                                "uzi": 909038009,
                                "m60": 909051003,
                                "groza": 909041005,
                                "vector": 909037011,
                                "mp5": 909033002,
                                "g18": 909038012
                            }

                            pair_list = []
                            for i in range(2, len(parts), 2):
                                try:
                                    gun_name = parts[i].lower()
                                    uid_target = int(parts[i + 1])
                                    pair_list.append((gun_name, uid_target))
                                except Exception as e:
                                    print("Lỗi khi đọc cặp:", e)
                                    continue
                        
                            if not pair_list:
                                msg = "[B][C][ff0000]Không có cặp hợp lệ!\n\n[ffffff]Ví Dụ:\n[00ff00]ftg [teamcode] [tensung] [uid] ..."
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                continue

                            message = (
                                f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Hành Động LV7 Theo Tên\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đang tiến hành vào đội và bật hành động lv7 để phong bạt!"
                            )
                            P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                            try:
                                EM = await GenJoinSquadsPacket(teamcode, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                                print(f"Đã join teamcode {teamcode}")
                            except Exception as e:
                                print("Join teamcode error:", e)
                                continue
                        
                            await asyncio.sleep(0.5)

                            async def activate_gun_for_uid(gun_name, target_uid):
                                try:
                                    idT = emote_presets.get(gun_name)
                                    if idT is None:
                                        try:
                                            idT = int(gun_name)
                                        except:
                                            print(f"Preset '{gun_name}' không hợp lệ!")
                                            return
                        
                                    print(f"→ Bật {gun_name} ({idT}) cho UID {target_uid}")
                                    H = await Emote_k(target_uid, idT, key, iv, region)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                    await asyncio.sleep(0.3)
                                except Exception as e:
                                    print(f"Lỗi khi bật {gun_name} cho UID {target_uid}: {e}")
                        
                            tasks = [asyncio.create_task(activate_gun_for_uid(namegun, target_uid)) for namegun, target_uid in pair_list]
                            await asyncio.gather(*tasks)

                            done_msg = f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Hành Động LV7 Theo Tên\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật hành động lv7 để phong bạt và sẽ rời đội ngay!"
                            P = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            
                            await asyncio.sleep(0.6)
                             
                            try:
                                E = await ExiT(None, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                                print("Đã out khỏi squad.")
                            except Exception as e:
                                print("Exit error:", e)
                                
                        
                        if inPuTMsG.strip().startswith('vip'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    msg = (
                                         "[B][C][ff0000]Sai cú pháp!\n\n"
                                         "[ffffff]Ví Dụ:\n"
                                         "[00ff00]vip [uid1] [uid2] ..."
                                    )
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

                                msg = f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Súng 7\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đang tiến hành bật full súng 7 để phong bạt!"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Đang gửi emote cho UID {target_uid}\n            [ffffff]Te[c]le[c]gram: [00fffb]@anhcodeclick"
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(5)

                                        done_msg = f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Súng 7\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật full hành động lv7 để phong bạt"
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C]{get_random_color()}🎉 Hoàn tất toàn bộ emote cho {len(target_uids)} UID!"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"loi")
                                # file bố code remake con cặc

                        if inPuTMsG.strip().startswith('rd'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 3:
                                    msg = (
                                        "[B][C][ff0000]Sai cú pháp!\n\n"
                                        "[ffffff]Ví Dụ:\n"
                                        "[00ff00]rd [teamcode] [uid1] [uid2] ..."
                                    )
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                teamcode = parts[1]
                                target_uids = [int(x) for x in parts[2:7]]   # tối đa 5 UID

                                full_emotes = [
                                    909049010, 909051003, 909033002, 909041005, 909038010,
                                    909039011, 909040010, 909000081, 909000085, 909000063,
                                    909000075, 909033001, 909000090, 909000068, 909000098,
                                    909035007, 909037011, 909038012, 909035012, 909042008,
                                    909035007, 909045001
                                ]

                                msg = (
                                    f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Súng 7\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã join nhóm thành công đang tiến hành bật full súng 7 để phong bạt!"
                                 )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                try:
                                    EM = await GenJoinSquadsPacket(teamcode, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                                except Exception as e:
                                    print("Join teamcode error:", e)
                                    continue

                                await asyncio.sleep(0.6)

                                async def emote_for_uid(uid_target):
                                    try:
                                        start_msg = (
                                            f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Bật 22 Emote Cho UID: {uid_target}\n"
                                            "[ffffff]Tele[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7"
                                        )
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in full_emotes:
                                            H = await Emote_k(uid_target, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(5)

                                        done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Súng 7\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật full hành động lv7 để phong bạt và sẽ rời đội ngay!"
                                        )
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print("Lỗi emote_for_uid:", e)

                                # chạy tối đa 5 uid song song
                                tasks = [asyncio.create_task(emote_for_uid(t)) for t in target_uids]
                                await asyncio.gather(*tasks)

                                await asyncio.sleep(2)
                                try:
                                    E = await ExiT(None, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                                except Exception as e:
                                    print("Exit error:", e)

                            except Exception as e:
                                print("Lỗi tổng rd:", e)

                        if inPuTMsG.strip().startswith('ngau2'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 3:
                                    msg = (
                                        "[B][C][ff0000]Sai cú pháp!\n\n"
                                        "[ffffff]Ví Dụ:\n"
                                        "[00ff00]ngau2 [teamcode] [uid1] [uid2] ..."
                                    )
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                teamcode = parts[1]
                                target_uids = [int(x) for x in parts[2:7]]   # tối đa 5 UID

                                full_emotes = [
                                    909046015, 909050009, 909043002, 909041002, 909041001,
                                    909000072, 909000073, 909000069, 909000067, 909046016,
                                    909000145, 909000129, 909000121, 909000124, 909000089,
                                ]

                                msg = (
                                    f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Ngầu\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã join nhóm thành công đang tiến hành bật full súng 7 để phong bạt!"
                                 )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                try:
                                    EM = await GenJoinSquadsPacket(teamcode, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                                except Exception as e:
                                    print("Join teamcode error:", e)
                                    continue

                                await asyncio.sleep(0.6)

                                async def emote_for_uid(uid_target):
                                    try:
                                        start_msg = (
                                            f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Bật 22 Emote Cho UID: {uid_target}\n"
                                            "[ffffff]Tele[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7"
                                        )
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in full_emotes:
                                            H = await Emote_k(uid_target, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(5)

                                        done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Ngầu\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật full hành động ngầu để phong bạt và sẽ rời đội ngay!"
                                        )
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print("Lỗi emote_for_uid:", e)

                                # chạy tối đa 5 uid song song
                                tasks = [asyncio.create_task(emote_for_uid(t)) for t in target_uids]
                                await asyncio.gather(*tasks)

                                await asyncio.sleep(2)
                                try:
                                    E = await ExiT(None, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                                except Exception as e:
                                    print("Exit error:", e)

                            except Exception as e:
                                print("Lỗi tổng ngau2:", e)

                        if inPuTMsG.strip().startswith('hai2'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 3:
                                    msg = (
                                        "[B][C][ff0000]Sai cú pháp!\n\n"
                                        "[ffffff]Ví Dụ:\n"
                                        "[00ff00]hai2 [teamcode] [uid1] [uid2] ..."
                                    )
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                teamcode = parts[1]
                                target_uids = [int(x) for x in parts[2:7]]   # tối đa 5 UID

                                full_emotes = [
                                    909051004, 909051005, 909051006, 909051007, 909051008,
                                    909051009, 909051010, 909051011, 909051012, 909051013,
                                    909051014, 909051015, 909051016
                                ]

                                msg = (
                                    f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Hài\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã join nhóm thành công đang tiến hành bật full súng 7 để phong bạt!"
                                 )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                try:
                                    EM = await GenJoinSquadsPacket(teamcode, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                                except Exception as e:
                                    print("Join teamcode error:", e)
                                    continue

                                await asyncio.sleep(0.6)

                                async def emote_for_uid(uid_target):
                                    try:
                                        start_msg = (
                                            f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Bật 22 Emote Cho UID: {uid_target}\n"
                                            "[ffffff]Tele[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7"
                                        )
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in full_emotes:
                                            H = await Emote_k(uid_target, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(5)

                                        done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Hài\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật full hành động hài để phong bạt và sẽ rời đội ngay!"
                                        )
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print("Lỗi emote_for_uid:", e)

                                # chạy tối đa 5 uid song song
                                tasks = [asyncio.create_task(emote_for_uid(t)) for t in target_uids]
                                await asyncio.gather(*tasks)

                                await asyncio.sleep(2)
                                try:
                                    E = await ExiT(None, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                                except Exception as e:
                                    print("Exit error:", e)

                            except Exception as e:
                                print("Lỗi tổng hai2:", e)

                        if inPuTMsG.strip().startswith('co2'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 3:
                                    msg = (
                                        "[B][C][ff0000]Sai cú pháp!\n\n"
                                        "[ffffff]Ví Dụ:\n"
                                        "[00ff00]co2 [teamcode] [uid1] [uid2] ..."
                                    )
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                teamcode = parts[1]
                                target_uids = [int(x) for x in parts[2:7]]   # tối đa 5 UID

                                full_emotes = [
                                    909000020, 909000021, 909000027, 909000008, 909000011,
                                    909000012, 909042007, 909000040
                                ]

                                msg = (
                                    f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Cổ\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã join nhóm thành công đang tiến hành bật full cổ để phong bạt!"
                                 )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                try:
                                    EM = await GenJoinSquadsPacket(teamcode, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                                except Exception as e:
                                    print("Join teamcode error:", e)
                                    continue

                                await asyncio.sleep(0.6)

                                async def emote_for_uid(uid_target):
                                    try:
                                        start_msg = (
                                            f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Bật 8 Emote Cho UID: {uid_target}\n"
                                            "[ffffff]Te[c]le[c]gram: [00fffb]@anhcodeclick"
                                        )
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in full_emotes:
                                            H = await Emote_k(uid_target, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(5)

                                        done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Cổ\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật full hành động cổ để phong bạt và sẽ rời đội ngay!"
                                        )
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print("Lỗi emote_for_uid:", e)

                                # chạy tối đa 5 uid song song
                                tasks = [asyncio.create_task(emote_for_uid(t)) for t in target_uids]
                                await asyncio.gather(*tasks)

                                await asyncio.sleep(2)
                                try:
                                    E = await ExiT(None, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                                except Exception as e:
                                    print("Exit error:", e)

                            except Exception as e:
                                print("Lỗi tổng co2:", e)


                        if inPuTMsG.strip().startswith('wf'):
                            try:
                                parts = inPuTMsG.strip().split()

                                if len(parts) < 3:
                                    msg = (
                                        "[B][C][ff0000]Sai cú pháp!\n\n"
                                        "[ffffff]Ví dụ:\n"
                                        "[00ff00]wf [teamcode] [uid1] [uid2] [uid3] ..."
                                    )
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                teamcode = parts[1]
                                target_uids = [int(x) for x in parts[2:7]]  # Tối đa 5 UID

                                full_emotes = [
                                    909051003, 909049010, 909033002, 909039011, 909000081,
                                    909000085, 909000063, 909040010, 909000075, 909033001,
                                    909000090, 909000068, 909000098, 909035007, 909037011,
                                    909038012, 909045001, 909041005, 909038010
                                ]

                                msg = (
                                    f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Random Full Súng 7\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã join nhóm thành công đang tiến hành bật random full súng 7 để phong bạt!"
                                )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                # Join TeamCode (giống hệt /ftg)
                                try:
                                    EM = await GenJoinSquadsPacket(teamcode, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                                    print("Đã join vào teamcode", teamcode)
                                except Exception as e:
                                    print("WF join error:", e)
                                    continue

                                await asyncio.sleep(0.6)

                                # Random emote cho từng UID (giống /l)
                                async def random_run(uid_target):
                                    import random
                                    emo_list = full_emotes[:]  
                                    random.shuffle(emo_list)

                                    start = (
                                        f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Đang Random: [00ffb3]{teamcode}\n"
                                        "[ffffff]Mỗi UID = danh sách random khác nhau!\n"
                                        "[ffffff]Tele[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7"
                                    )
                                    S = await SEndMsG(response.Data.chat_type, start, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                    for emo in emo_list:
                                        H = await Emote_k(uid_target, emo, key, iv, region)
                                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                        await asyncio.sleep(5)

                                        done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Random Full Súng 7\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật random full hành động lv7 để phong bạt và  sẽ rời đội ngay!"
                                        )
                                    D = await SEndMsG(response.Data.chat_type, done, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)

                                tasks = [asyncio.create_task(random_run(tu)) for tu in target_uids]
                                await asyncio.gather(*tasks)

                                # Out squad
                                await asyncio.sleep(0.6)
                                try:
                                    E = await ExiT(None, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                                    print("WF: Bot đã thoát squad.")
                                except:
                                    pass

                            except Exception as e:
                                print("WF cmd error:", e)
                                

                        if inPuTMsG.strip().startswith('l'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    msg = (
                                         "[B][C][ff0000]Sai cú pháp!\n\n"
                                         "[ffffff]Ví Dụ:\n"
                                         "[00ff00]l [uid1] [uid2] ..."
                                )
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                else:
                                    target_uids = [int(x) for x in parts[1:6]]
                                    full_emotes = [
                                        909051003, 909049010, 909033002, 909039011, 909000081,
                                    909000085, 909000063, 909040010, 909000075, 909033001,
                                    909000090, 909000068, 909000098, 909035007, 909037011,
                                    909038012, 909045001, 909041005, 909038010
                                    ]
                                    msg = (
                                    f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Random Full Súng 7\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đang tiến hành bật random full súng 7 để phong bạt!"
                                 )
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    async def run_all(uidt):
                                        import random
                                        emo_list = full_emotes[:] 
                                        random.shuffle(emo_list)
                                        for emo in emo_list:
                                            H = await Emote_k(uidt, emo, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(5)
                                    tasks = [asyncio.create_task(run_all(t)) for t in target_uids]
                                    await asyncio.gather(*tasks)
                                    done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Random Full Súng 7\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật random full hành động lv7 để phong bạt!"
                                        )
                                    F = await SEndMsG(response.Data.chat_type, done, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)
                            except Exception as e:
                                print('l cmd err', e)
                        if inPuTMsG.strip().startswith('hai'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    msg = (
                                         "[B][C][ff0000]Sai cú pháp!\n\n"
                                         "[ffffff]Ví Dụ:\n"
                                         "[00ff00]hai [uid1] [uid2] ..."
                                )
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uids = [int(x) for x in parts[1:6]]

                                default_emotes = [
                                    909051004, 909051005, 909051006, 909051007, 909051008,
                                    909051009, 909051010, 909051011, 909051012, 909051013,
                                    909051014, 909051015, 909051016
                                ]

                                msg = (
                                f"[B][C][FFFFFF]Xin Chào!/n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Hài\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đang tiến hành bật full hành động hài để phong bạt!"
                            )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = (
                                f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Đang Bật Full Emote Hài\n"
                                "[ffffff]Tele[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7"
                            )
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(3)

                                        done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Cổ\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật full hành động cổ để phong bạt!"
                                        )
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C]{get_random_color()}🎉 Hoàn tất toàn bộ emote cho {len(target_uids)} UID!"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"loi")

                        if inPuTMsG.strip().startswith('ngau'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    msg = (
                                         "[B][C][ff0000]Sai cú pháp!\n\n"
                                         "[ffffff]Ví Dụ:\n"
                                         "[00ff00]ngau [uid1] [uid2] ..."
                                )
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uids = [int(x) for x in parts[1:6]]

                                default_emotes = [
                                    909046015, 909050009, 909043002, 909041002, 909041001,
                                    909000072, 909000073, 909000069, 909000067, 909046016,
                                    909000145, 909000129, 909000121, 909000124, 909000089,
                                    
                                ]

                                msg = (
                                f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Ngầu\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đang tiến hành bật full hành động ngầu để phong bạt!"
                            )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = (
                                f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Đang Bật Full Emote Ngầu\n"
                                "[ffffff]Tele[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7"
                            )
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(4)

                                        done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Ngầu\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật full hành động ngầu để phong bạt!"
                                        )
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C]{get_random_color()}🎉 Hoàn tất toàn bộ emote cho {len(target_uids)} UID!"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"loi")
                                # file bố code remake con cặc



                        if inPuTMsG.strip().startswith('e'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 3:
                                    msg = (
                                         "[B][C][ff0000]Sai cú pháp!\n\n"
                                         "[ffffff]Ví Dụ:\n"
                                         "[00ff00]e [tensung] [uid1] [tensung] [uid2] ..."
                                )
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

                                # TH1: /fe all tensung
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

                                # TH2: /e uid1 uid2 uid3 tensung
                                elif args[-1].lower() in gun_emotes and all(a.isdigit() for a in args[:-1]):
                                    gun = args[-1].lower()
                                    emo = gun_emotes[gun]
                                    for u in args[:-1]:
                                        uid_gun_pairs.append((int(u), emo))

                                # TH3: /e uid1 gun1 uid2 gun2 uid3 gun3 ...
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

                                start_msg = f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Hành Động LV7 Theo Tên\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đang tiến hành bật hành động lv7 để phong bạt!"
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

                                done_msg = f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Hành Động LV7 Theo Tên\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật hành động lv7 để phong bạt!"
                                D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)

                            except Exception as e:
                                print("loi e")

                                
                                
                                
                                
                                
                        if inPuTMsG.strip().startswith('co'):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    msg = (
                                         "[B][C][ff0000]Sai cú pháp!\n\n"
                                         "[ffffff]Ví Dụ:\n"
                                         "[00ff00]co [uid1] [uid2] ..."
                                )
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uids = [int(x) for x in parts[1:6]]

                                default_emotes = [
                                    909000020, 909000021, 909000027, 909000008, 909000011,
                                    909000012, 909042007, 909000040
                                ]

                                msg = (
                                f"[B][C][FFFFFF]Xin Chào!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Cổ\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đang tiến hành bật full hành động cổ để phong bạt!"
                            )
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        start_msg = (
                                f"[B][C][00ff00]『 ACTIVE 』[ffffff]| → Đang Bật Full Emote Cổ\n"
                                "[ffffff]Tele[c]gr[c]am: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7"
                            )
                                        S = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', S)

                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(3)

                                        done_msg = (
                                            f"[B][C][FFFFFF]Thành Công!\n[FFFFFF]Thể Loại Lệnh: [00ffb3]Full Hành Động Cổ\n\n[FFFFFF]Ti[c]kT[c]ok Admin: [C][B][007AFF]@[C][B][339BFF]q[C][B][66BBFF]u[C][B][99DFFF]a[C][B][CCF5FF]n[C][B][E0FAFF]g[C][B][F0FDFF]hau8th7\n[C0C0C0]Bot đã bật full hành động cổ để phong bạt!"
                                        )
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"loi")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C]{get_random_color()}🎉 Hoàn tất toàn bộ emote cho {len(target_uids)} UID!"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"loi")

                                if inPuTMsG.strip().lower() in ("help", "/help", "menu", "/menu", "commands"):
                                 print(f"Help command detected from UID: {uid} in chat type: {response.Data.chat_type}")

                                # ───── LẤY TÊN NGƯỜI CHƠI ─────
                                try:
                                    cdanhdev = chatdata['5']['data']['9']['data']['1']['data']
                                except Exception:
                                    cdanhdev = "User"

                                # ───── HEADER / CHÀO NGƯỜI CHƠI ─────
                                header = f"""[C][B]{get_random_color()}XIN CHÀO {cdanhdev}
[FFFFFF]Chào mừng bạn đến với BOT"""
                                await safe_send_message(
                                    response.Data.chat_type,
                                    header,
                                    uid,
                                    chat_id,
                                    key,
                                    iv
                                )
                                await asyncio.sleep(0.2)
    
                            # Advanced Commands
                            advanced_commands = """[B][C][00FFA6]Troll Lag+Dừng Lag
[00FF00] [FFFFFF]🗿atk [code]
[00FF00] [FFFFFF]🗿satk

[00FFA6]Spam Mời+Dừng Spam
[00FF00] [FFFFFF]🗿siv [uid]
[00FF00] [FFFFFF]🗿ssiv

[00FFA6]Team 5+Mời 1 Người Vào Team 5
[00FF00] [FFFFFF]🗿5
[00FF00] [FFFFFF]🗿inv [uid]

[00FFA6]Sau Đây Là Các Lệnh Lặt Vặt

[00FFA6]Hiện Thông Tin Admin
[00FF00] [FFFFFF]🗿admin

[00FFA6]Hiện Giá Th[c]uê Bot
[00FF00] [FFFFFF]🗿giabot

[00FFA6]Bot Vào Đội+Rời Đội
[00FF00]/[FFFFFF]🗿x/[code]
[00FF00] [FFFFFF]🗿cut"""
    
                            await safe_send_message(response.Data.chat_type, advanced_commands, uid, chat_id, key, iv)
                            await asyncio.sleep(0.2)
    
                            # Evolution Emote Commands
                            evo_commands = """[B][C]
[F0FDFF]Sau Đây Là Lệnh Hành Động Trong Đội

[00FFA6]Full Hành Động Hài
[00FF00] [FFFFFF]🗿hai [uid]

[00FFA6]Full Hành Động Cổ
[00FF00] [FFFFFF]🗿co [uid]

[00FFA6]Full Súng 7
[00FF00] [FFFFFF]🗿vip [uid]

[00FFA6]Full Hành Động Ngầu
[00FF00] [FFFFFF]🗿ngau [uid]

[00FFA6]Random Full Lv7
[00FF00] [FFFFFF]🗿l [uid]

[00FFA6]Bật 1 Hành Động Lv7 Theo Tên
[00FF00] [FFFFFF]🗿e [TENSUNG] [UID]"""
    
                            await safe_send_message(response.Data.chat_type, evo_commands, uid, chat_id, key, iv)
                            await asyncio.sleep(0.2)

                            # Evolution Emote Commands
                            code_commands = """[B][C]
[F0FDFF]Sau Đây Là Lệnh Hành Động Bằng Code

[00FFA6]Full Hành Động Hài
[00FF00] [FFFFFF]🗿hai2 [code] [uid]

[00FFA6]Full Hành Động Ngầu
[00FF00] [FFFFFF]🗿ngau2 [code] [uid]

[00FFA6]Full Hành Động Cổ
[00FF00] [FFFFFF]🗿co2 [code] [uid]

[00FFA6]Full Súng 7
[00FF00] [FFFFFF]🗿rd [code] [uid]

[00FFA6]Random Full Lv7
[00FF00] [FFFFFF]🗿wf [code] [uid]

[00FFA6]Bật 1 Hành Động Lv7 Theo Tên
[00FF00] [FFFFFF]🗿ftg [code] [TENSUNG] [UID] [FFFFFF]@anhcodeclick"""

                            await safe_send_message(response.Data.chat_type, code_commands, uid, chat_id, key, iv)
                            await asyncio.sleep(0.2)
                        
                           # Badges command 
                            badge_commands = """[B][C]
[F0FDFF]Sau Đây Là Các Lệnh Spam Yêu Cầu Vào Đội+Tích

[FFFFFF]Tích Nhà Sáng Tạo
[00FF00] [FFFFFF]🗿s1 [uid]

[00FFA6]Tích V v2
[00FF00] [FFFFFF]🗿s2 [uid]

[00FFA6]Tích Nhà Điều Hành
[00FF00] [FFFFFF]🗿s3 [uid]

[00FFA6]Tích V v1
[00FF00] [FFFFFF]🗿s4 [uid]

[00FFA6]Tích Tuyển Thủ
[00FF00] [FFFFFF]🗿s5 [uid]

[00FFA6]Random
[00FF00] [FFFFFF]🗿s6 [uid] [FFFFFF]@anhcodeclick"""

                            await safe_send_message(response.Data.chat_type, badge_commands, uid, chat_id, key, iv)
                            await asyncio.sleep(0.2)                       


                        response = None
                            
            whisper_writer.close() ; await whisper_writer.wait_closed() ; whisper_writer = None
                    
                        
                        
        except Exception as e: print(f"ErroR {ip}:{port} - {e}") ; whisper_writer = None
        await asyncio.sleep(reconnect_delay)

async def MaiiiinE():
    Uid , Pw = '4357649878','21145AE32E59B88F27CF97AE6E0F0D3200AA49214D621A41472C8B9103E827C9'
    

    open_id , access_token = await GeNeRaTeAccEss(Uid , Pw)
    if not open_id or not access_token: print("ErroR - InvaLid AccounT") ; return None
    
    PyL = await EncRypTMajoRLoGin(open_id , access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE: print("TarGeT AccounT => BannEd / NoT ReGisTeReD ! ") ; return None
    
    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    # In the MaiiiinE function, find and comment out these print statements:
    os.system('clear')
    print("🔄 Bắt đầu thiết lập kết nối TCP...")
    print("📡 Đang kết nối đến máy chủ Free Fire...")
    print("🌐 Đã thiết lập kết nối máy chủ")

    region = MajoRLoGinauTh.region

    ToKen = MajoRLoGinauTh.token
    print("🔐 Xác thực thành công")
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
    
    equie_emote(ToKen,UrL)
    AutHToKen = await xAuThSTarTuP(int(TarGeT) , ToKen , int(timestamp) , key , iv)
    ready_event = asyncio.Event()
    
    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT , AutHToKen , key , iv , LoGinDaTaUncRypTinG , ready_event ,region))
    task2 = asyncio.create_task(TcPOnLine(OnLineiP , OnLineporT , key , iv , AutHToKen))  

    os.system('cls')
    print("Đang Khởi Chạy Bot...")
    print("┌────────────────────────────────────┐")
    print("│ █████████████░░░░░░░░░░░░░░░░░░ │")
    print("└────────────────────────────────────┘")
    time.sleep(0.5)
    os.system('cls')
    print("Đang kết nối đến máy chủ Free Fire...")
    print("┌────────────────────────────────────┐")
    print("│ ██████████████████████░░░░░░░░░░░░ │")
    print("└────────────────────────────────────┘")
    time.sleep(0.5)
    os.system('cls')

    print("🤖 DEKA BOT - ONLINE")
    print("┌────────────────────────────────────┐")
    print("│ ██████████████████████████████████ │")
    print("└────────────────────────────────────┘")
    print(f"🔹 UID: {TarGeT}")
    print(f"🔹 Name: {acc_name}")
    print(f"🔹 Status: 🟢 READY")
    print("")
    print("💡 Dùng /help Để Hiện Danh Sách Lệnh")
    await asyncio.gather(task1, task2)
    time.sleep(0.5)
    os.system('cls')
    await ready_event.wait()
    await asyncio.sleep(1)

    os.system('cls')
    print(render('DEKA', colors=['white', 'green'], align='center'))
    print('')
    print("🤖 THEROSHANF BOT - ONLINE")
    print(f"🔹 UID: {TarGeT}")
    print(f"🔹 Name: {acc_name}")
    print(f"🔹 Status: 🟢 READY")
    


def handle_keyboard_interrupt(signum, frame):
    """Clean handling for Ctrl+C"""
    print("\n\n🛑 Bot Đang Off...")
    print("👋 Cảm Ơn Vì Đã Tin Tưởng")
    sys.exit(0)
    
async def StarTinG():
    while True:
        try:
            await asyncio.wait_for(MaiiiinE() , timeout = 7 * 60 * 60)
        except KeyboardInterrupt:
            print("\n\n🛑 Bot Đã Off Bởi Người Dùng")
            print("👋 Cảm Ơn Vì Đã Tin Tưởng!")
            break
        except asyncio.TimeoutError: print("Token ExpiRed ! , ResTartinG")
        except Exception as e: print(f"ErroR TcP - {e} => ResTarTinG ...")

if __name__ == '__main__':
    asyncio.run(StarTinG())