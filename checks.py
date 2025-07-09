import asyncio
from io import BytesIO
import regex as re
import requests
import datetime
from telethon import TelegramClient, events
from telethon.tl import functions
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from concurrent.futures import ThreadPoolExecutor
from config import *

client = TelegramClient(session='session', api_id=int(api_id), api_hash=api_hash, system_version="4.16.30-vxSOSYNXA")

code_regex = re.compile(r"t\.me/(CryptoBot|send|tonRocketBot|wallet|xrocket|xJetSwapBot)\?start=(CQ[A-Za-z0-9]{10}|C-[A-Za-z0-9]{10}|t_[A-Za-z0-9]{15}|mci_[A-Za-z0-9]{15}|c_[a-z0-9]{24})", re.IGNORECASE)
url_regex = re.compile(r"https:\/\/t\.me\/\+(\w{12,})")
public_regex = re.compile(r"https:\/\/t\.me\/(\w{4,})")

replace_chars = ''' @#&+()*"'…;,!№•—–·±<{>}†★‡„“”«»‚‘’‹›¡¿‽~`|√π÷×§∆\\°^%©®™✓₤$₼€₸₾₶฿₳₥₦₫₿¤₲₩₮¥₽₻₷₱₧£₨¢₠₣₢₺₵₡₹₴₯₰₪'''
translation = str.maketrans('', '', replace_chars)

executor = ThreadPoolExecutor(max_workers=5)


current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
message_content = f'ChequeCatcher enabled - {current_datetime}'

crypto_black_list = [1559501630, 1985737506, 5014831088, 6014729293, 5794061503]

global checks
global checks_count
global wallet
activated_checks = {}
checks = []
wallet = []
channels = []
captches = []
checks_count = 0


def ocr_space_sync(file: bytes, overlay=False, language='eng', scale=True, OCREngine=2):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': ocr_api_key,
        'language': language,
        'scale': scale,
        'OCREngine': OCREngine
    }
    response = requests.post(
        'https://api.ocr.space/parse/image',
        data=payload,
        files={'filename': ('image.png', file, 'image/png')}
    )
    result = response.json()
    return result.get('ParsedResults')[0].get('ParsedText').replace(" ", "")


async def ocr_space(file: bytes, overlay=False, language='eng'):
    loop = asyncio.get_running_loop()
    recognized_text = await loop.run_in_executor(
        executor, ocr_space_sync, file, overlay, language
    )
    return recognized_text


async def pay_out_wallet():
    await client.send_message('wallet', message=f'/wallet')
    await asyncio.sleep(0.1)
    messages = await client.get_messages('wallet', limit=1)
    message = messages[0].message
    lines = message.split('\n\n')
    for line in lines:
        if ':' in line:
            if 'Доступно' in line:
                data = line.split('\n')[2].split('Доступно: ')[1].split(' (')[0].split(' ')
                summ = data[0]
                curency = data[1]
            else:
                data = line.split(': ')[1].split(' (')[0].split(' ')
                summ = data[0]
                curency = data[1]
            try:
                if summ == '0':
                    continue
                result = (await client.inline_query('wallet', f'{summ}'))[0]
                if 'Создать чек' in result.title:
                    await result.click(avto_vivod_tag)
            except:
                pass
    await asyncio.sleep(3600)


async def pay_out_xrocket():
    await client.send_message('xrocket', message=f'/wallet')
    await asyncio.sleep(0.1)
    messages = await client.get_messages('xrocket', limit=1)
    message = messages[0].message
    lines = message.split('\n\n')
    for line in lines:
        if ':' in line:
            if 'Доступно' in line:
                data = line.split('\n')[2].split('Доступно: ')[1].split(' (')[0].split(' ')
                summ = data[0]
                curency = data[1]
            else:
                data = line.split(': ')[1].split(' (')[0].split(' ')
                summ = data[0]
                curency = data[1]
            try:
                if summ == '0':
                    continue
                result = (await client.inline_query('xrocket', f'{summ} {curency}'))[0]
                if 'Чек' in result.title:
                    await result.click(avto_vivod_tag)
            except:
                pass
    await asyncio.sleep(3600) 


@client.on(events.NewMessage(chats=[1985737506], pattern="⚠️ Вы не можете активировать этот чек, так как вы не являетесь подписчиком канала"))
async def handle_new_message(event):
    global wallet
    code = None
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    try:
                        check = code_regex.search(button.url)
                        if check:
                            code = check.group(2)
                    except:
                        pass
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        await client(ImportChatInviteRequest(channel.group(1)))
                    if public_channel:
                        await client(JoinChannelRequest(public_channel.group(1)))
                except:
                    pass
    except AttributeError:
        pass
    if code not in wallet:
        await client.send_message('wallet', message=f'/start {code}')
        wallet.append(code)


@client.on(events.NewMessage(chats=[1559501630], pattern="Чтобы"))
async def handle_new_message_crypto_bot(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    channel = url_regex.search(button.url)
                    if channel:
                        await client(ImportChatInviteRequest(channel.group(1)))
                except:
                    pass
    except AttributeError:
        pass
    await event.message.click(data=b'check-subscribe')


if anti_captcha:
    @client.on(events.NewMessage(chats=[1559501630], func=lambda e: e.photo))
    async def handle_photo_message(event):
        photo = await event.download_media(bytes)
        recognized_text = await ocr_space(file=photo)
        if recognized_text and recognized_text not in captches:
            await client.send_message('CryptoBot', message=recognized_text)
            await asyncio.sleep(0.1)
            message = (await client.get_messages('CryptoBot', limit=1))[0].message
            if 'Incorrect answer.' in message or 'Неверный ответ.' in message:
                await client.send_message(channel, message=f'<b>❌ Не удалось разгадать каптчу, решите ее сами.</b>', parse_mode='HTML') 
                print(f'[!] Ошибка антикаптчи > Не удалось разгадать каптчу, решите ее сами.')
                captches.append(recognized_text)
    print(f'[$] Антикаптча подключена!')


@client.on(events.NewMessage(chats=[5014831088], pattern="Для активации чека"))
async def handle_new_message_xrocket(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        await client(ImportChatInviteRequest(channel.group(1)))
                    if public_channel:
                        await client(JoinChannelRequest(public_channel.group(1)))
                except:
                    pass
    except AttributeError:
        pass
    await event.message.click(data=b'Check')


@client.on(events.NewMessage(chats=[5014831088], pattern="💰 Вы получили"))
async def handle_new_message_xrocket(event):
    try:
        row = event.message.reply_markup.rows[0]
        if row.buttons:
            first_button_text = row.buttons[0].text
            if first_button_text.startswith('Ref_'):
                ref_value = first_button_text.split('Ref_')[1]
                print(f'Text after Ref_: {ref_value}')
    except AttributeError:
        pass
    await event.message.click(data=b'Check')


@client.on(events.NewMessage(chats=[5794061503]))
async def handle_new_message_xjetswap_bot(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    try:
                        if (button.data.decode()).startswith(('showCheque_', 'activateCheque_')):
                            await event.message.click(data=button.data)
                    except:
                        pass
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        await client(ImportChatInviteRequest(channel.group(1)))
                    if public_channel:
                        await client(JoinChannelRequest(public_channel.group(1)))
                except:
                    pass
    except AttributeError:
        pass


async def filter_messages(event):
    for word in ['Вы получили', 'Вы обналичили чек на сумму:', '✅ Вы получили:', '💰 Вы получили']:
        if word in event.message.text:
            return True
    return False


async def send_log_message(log_message, check_url, channel):
    full_log_message = f'{log_message}\nСсылка на чек: {check_url}'
    await client.send_message(channel, message=full_log_message, parse_mode='HTML')


@client.on(events.MessageEdited(chats=crypto_black_list, func=filter_messages))
@client.on(events.NewMessage(chats=crypto_black_list, func=filter_messages))
async def handle_new_message_checks(event):
    try:
        bot = (await client.get_entity(event.message.peer_id.user_id)).username
    except:
        bot = (await client.get_entity(event.message.peer_id.user_id)).usernames[0].username
    code = None
    check_url = None
    summ = event.raw_text.split('\n')[0].replace('Вы получили ', '').replace('✅ Вы получили: ', '').replace('💰 Вы получили ', '').replace('Вы обналичили чек на сумму: ', '')
    if summ in activated_checks and bot in activated_checks[summ]:
        return
    if summ not in activated_checks:
        activated_checks[summ] = [bot]
    else:
        activated_checks[summ].append(bot)
    log_message = f'✅ Активирован чек на сумму <b>{summ}</b>\nБот: <b>@{bot}</b>\nВсего чеков после запуска активировано: <b>{len(activated_checks)}</b>'
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    match = code_regex.search(button.url)
                    if match:
                        code = match.group(2)

                        if code not in checks:
                            await client.send_message(match.group(1), message=f'/start {code}')
                            checks.append(code)
                            check_url = f"https://t.me/{bot}?start={code}"
                except AttributeError:
                    pass
    except AttributeError:
        pass
    await send_log_message(log_message, check_url, channel)


@client.on(events.MessageEdited(outgoing=False, chats=crypto_black_list, blacklist_chats=True))
@client.on(events.NewMessage(outgoing=False, chats=crypto_black_list, blacklist_chats=True))
async def handle_new_message_codes(event):
    global checks
    message_text = event.message.text.translate(translation)
    codes = code_regex.findall(message_text)
    if codes:
        for bot_name, code in codes:
            if code not in activated_checks or bot_name not in activated_checks[code]:
                await client.send_message(bot_name, message=f'/start {code}')
                if code not in activated_checks:
                    activated_checks[code] = [bot_name]
                else:
                    activated_checks[code].append(bot_name)
                check_url = f"https://t.me/{bot_name}?start={code}"
                log_message = f"✅ Активирован новый чек!\nБот: <b>@{bot_name}</b>\nВсего чеков после запуска активировано: <b>{len(activated_checks)}</b>"
                await send_log_message(log_message, check_url, channel)
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    match = code_regex.search(button.url)
                    if match:
                        if match.group(2) not in checks:
                            await client.send_message(match.group(1), message=f'/start {match.group(2)}')
                            checks.append(match.group(2))
                            # Отправка ссылки на чек в лог-канал
                            check_url = f"https://t.me/{match.group(1)}?start={match.group(2)}"
                            log_message = f"✅ Активирован новый чек!\nБот: <b>@{match.group(1)}</b>\nВсего чеков после запуска активировано: <b>{len(checks)}</b>"
                            await send_log_message(log_message, check_url, channel)
                except AttributeError:
                    pass
    except AttributeError:
        pass


async def main():
    try:
        await client.start()
        try:
            await client(JoinChannelRequest('blant_info'))
        except:
            pass
        if avto_vivod and avto_vivod_tag != '':
            try:
                message = await client.send_message(avto_vivod_tag, message=message_content)
                asyncio.create_task(pay_out_wallet())
                asyncio.create_task(pay_out_xrocket())
                print(f'[$] Автовывод подключен!')
            except Exception as e:
                print(f'[!] Ошибка автовывода > Не удалось отправить тестовое сообщение на тег для авто вывода. Авто вывод отключен.')
        elif avto_vivod and avto_vivod_tag == '':
            print(f'[!] Ошибка автовывода > Вы не указали тег для авто вывода.')
        print(f'[$] Ловец чеков запущен!')
        print(f'[+] По всем вопросам: @supportbot')
        await client.run_until_disconnected()
    except Exception as e:
        print(f'[!] Ошибка коннекта > {e}')


asyncio.run(main())