import telebot
import os
import requests
import re

KEY = os.getenv('KEY')
DEC = int(os.getenv('DEC'))
DEC_ACC = 2
URL_API = os.getenv('URL_API')

bot = telebot.TeleBot(KEY)

@bot.message_handler(commands= ["start"])
def start(message):
    bot.reply_to(message, f"*Welcome {message.from_user.first_name}!*👋"
        "\n\nI am 🤖*WaxCoinsBot* and I can show you the current prices of coins of the WAX ecosystem, check your acccount status and "
        "calculate the value of 'X' amount of coins in WAX and USD 📊"
        "\n\nTo understand how I work, please press /help"
        "\n\n*WAX address for donations:* [ddgra.wam](https://wax.bloks.io/wallet/transfer) ❤️", parse_mode='MARKDOWN')

@bot.message_handler(commands= ["help"])
def help(message):
    bot.reply_to(message, "Hi👋, how are you? to make your queries please use the following commands✅:"
        "\n\n/acc - To check your CPU, RAM and NET status"
        '\n/calc - To check the price of "X" amount of coins'
        "\n/coinp - To check the price of any coin"
        "\n/parp - To check the price of a pair"
        '\n\n<b>WAX address for donations:</b> <a href="https://wax.bloks.io/wallet/transfer"><b>ddgra.wam</b></a> ❤️', parse_mode='HTML')

#Account status
@bot.message_handler(commands=['acc'])
def acc(message):
    send = {}
    chat_id = message.chat.id
    try:
        if message.text[4] == '@':
            raise Exception("Bot 'at' sign")
        text = message.text[5:]
        if text:
            send['account_name'] = text
            response = requests.post(URL_API + '/get_account', json=send)
            if response.status_code == 200:
                data = response.json()
                account = data['account_name']
                if 'core_liquid_balance' in data:
                    account_balance = round(float(data['core_liquid_balance'].split(' ')[0]), DEC_ACC)
                else:
                    account_balance = 0
                ram_used = data['ram_usage']
                ram_max = data['ram_quota']
                ram_por = round(100*ram_used/ram_max, DEC_ACC)
                ram_ava = round(100 - ram_por, DEC_ACC)
                if ram_ava < 0:
                    ram_ava = 0
                cpu_used = data['cpu_limit']['used']
                cpu_max = data['cpu_limit']['max']
                cpu_por = round(100*cpu_used/cpu_max, DEC_ACC)
                cpu_ava = round(100 - cpu_por, DEC_ACC)
                cpu_stk = round(float(data['total_resources']['cpu_weight'].split(' ')[0]), DEC_ACC)
                if cpu_ava < 0:
                    cpu_ava = 0
                net_used = data['net_limit']['used']
                net_max = data['net_limit']['max']
                net_por = round(100*net_used/net_max, DEC_ACC)
                net_ava = round(100 - net_por, DEC_ACC)
                net_stk = round(float(data['total_resources']['net_weight'].split(' ')[0]), DEC_ACC)
                if net_por < 0:
                    net_por = 0
                total_balance = round(account_balance + cpu_stk + net_stk, DEC_ACC)
                bot.send_message(chat_id,f"*🙍‍♂️Account: {account}\n💰Available balance: {account_balance} WAX\n💰Total balance: {total_balance} WAX*"
                    f"\n\n*🖥CPU*\n- Status: {cpu_por}%\n- Available: {cpu_ava}%\n*💰Staked: {cpu_stk} WAX*"
                    f"\n\n*📶NET*\n- Status: {net_por}%\n- Available: {net_ava}%\n*💰Staked: {net_stk} WAX*"
                    f"\n\n*💾RAM*\n- Status: {ram_por}%\n- Available: {ram_ava}%",parse_mode='MARKDOWN')
            else:
                bot.reply_to(message,"*‼️This account doesn't exist*", parse_mode='MARKDOWN')
        else:
            bot.send_message(chat_id,'*‼️Command format:*\n\n/acc account.wam\n\nIf you need help press /help.', parse_mode='MARKDOWN')
    except:
        bot.send_message(chat_id,'*‼️Command format:*\n\n/acc account.wam\n\nIf you need help press /help.', parse_mode='MARKDOWN')

#Pair prices
@bot.message_handler(commands= ["parp"])
def parp(message):
    try:
        if message.text[5] == '@':
            raise Exception("Bot 'at' sign")
        texto = re.search("^[a-zA-Z0-9]+/[a-zA-Z0-9]+$", message.text[6:])
        if texto:
            texto = texto.group()
            quote_token, base_token = texto.split('/')
            quote_token, base_token = quote_token.upper(), base_token.upper()
            price = None
            response_alcor = requests.get('https://wax.alcor.exchange/api/markets')
            response_coingecko = requests.get('https://api.coingecko.com/api/v3/coins/wax')
            data = response_alcor.json()
            waxusd = response_coingecko.json()['market_data']['current_price']['usd']
            for par in data:
                if par['base_token']['symbol']['name'] == base_token and par['quote_token']['symbol']['name'] == quote_token:
                    price = round(par['last_price'],DEC)
                    break
            if price != None:
                if base_token == 'WAX':
                    priceusd = round(price*waxusd,DEC)
                else:
                    for par in data:
                        if par['base_token']['symbol']['name'] == 'WAX' and par['quote_token']['symbol']['name'] == quote_token:
                            priceusd = par['last_price']
                            break
                    priceusd = round(priceusd*waxusd,DEC)

                bot.reply_to(message,f"*💎Pair: {quote_token}/{base_token}*"
                    f"\n\n🟡Precio actual: {price} {base_token}"
                    f"\n💰Precio USD: ${priceusd}", parse_mode='MARKDOWN')
            else:
                bot.reply_to(message,"Sorry, I couldn't find the pair you were looking for😢"
                    "\n\nIf you need help press /help.")
        else:
            bot.reply_to(message,"*‼️Command format*\n\n/parp TLM/WAX\n/parp AETHER/WAX\n\nIf you need help press /help.", parse_mode='MARKDOWN')
    except:
        bot.reply_to(message,"*‼️Command format*\n\n/parp TLM/WAX\n/parp AETHER/WAX\n\nIf you need help press /help.", parse_mode='MARKDOWN')

#Coin amount calculation
@bot.message_handler(commands= ["calc"])
def calc(message):
    try:
        if message.text[5] == '@':
            raise Exception("Bot 'at' sign")
        texto = re.search("^[0-9]+\.*[0-9]* [a-zA-Z0-9]+$", message.text[6:])
        if texto:
            texto = texto.group()
            cantidad, token = texto.split(' ')
            cantidad, token = float(cantidad), token.upper()
            response_alcor = requests.get('https://wax.alcor.exchange/api/markets')
            response_coingecko = requests.get('https://api.coingecko.com/api/v3/coins/wax')
            data = response_alcor.json()
            waxusd = response_coingecko.json()['market_data']['current_price']['usd']
            price = None
            if token == 'WAX':
                price = 1
            else:
                for par in data:
                    if par['base_token']['symbol']['name'] == 'WAX' and par['quote_token']['symbol']['name'] == token:
                        price = par['last_price']
                        break
            if price != None:
                pricewax = round(price*cantidad,DEC)
                priceusd = round(pricewax*waxusd,DEC)
                bot.reply_to(message,f"*💎Coin: {token}*"
                    f"\n👌Quantity: {cantidad}"
                    f"\n\n🟡Price WAX: {pricewax} WAX"
                    f"\n\n💰Price USD: ${priceusd}", parse_mode='MARKDOWN')
            else:
                bot.reply_to(message,"Sorry, I couldn't find the coin you were looking for😢"
                    "\n\nIf you need help press /help.")
        else:
            bot.reply_to(message,"*‼️Command format*\n\n/calc 15 AETHER\n/calc 10 TLM\n\nIf you need help press /help.", parse_mode='MARKDOWN')
    except:
        bot.reply_to(message,"*‼️Command format*\n\n/calc 15 AETHER\n/calc 10 TLM\n\nIf you need help press /help.", parse_mode='MARKDOWN')

#Coin prices
@bot.message_handler(commands= ["coinp"])
def coinp(message):
    try:
        if message.text[6] == '@':
            raise Exception("Bot 'at' sign")
        coin = re.search("^[a-zA-Z0-9]+$", message.text[7:])
        if coin:
            coin = coin.group().upper()
            price = None
            response_alcor = requests.get('https://wax.alcor.exchange/api/markets')
            response_coingecko = requests.get('https://api.coingecko.com/api/v3/coins/wax')
            data = response_alcor.json()
            waxusd = round(response_coingecko.json()['market_data']['current_price']['usd'],DEC)
            if coin == 'WAX':
                bot.reply_to(message,f"*💎Coin: {coin}*\
                \n\n💰Price USD: ${waxusd}", parse_mode='MARKDOWN')
            else:
                for par in data:
                    if par['base_token']['symbol']['name'] == 'WAX' and par['quote_token']['symbol']['name'] == coin:
                        price = round(par['last_price'],DEC)
                        break
                if price != None:
                    priceusd = round(price*waxusd,DEC)
                    bot.reply_to(message,f"*💎Coin: {coin}*"
                        f"\n\n🟡Price WAX: {price} WAX"
                        f"\n\n💰Price USD: ${priceusd}", parse_mode='MARKDOWN')
                else:
                    bot.reply_to(message,"Sorry, I couldn't find the coin you were looking for😢"
                        "\n\nIf you need help press /help.")
        else:
            bot.reply_to(message,"*‼️Command format*\n\n/coinp AETHER\n/coinp TLM\n\nIf you need help press /help.", parse_mode='MARKDOWN')
    except:
        bot.reply_to(message,"*‼️Command format*\n\n/coinp AETHER\n/coinp TLM\n\nIf you need help press /help.", parse_mode='MARKDOWN')