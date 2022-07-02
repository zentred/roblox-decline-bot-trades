import requests, time, threading, ctypes, json

config = json.load(open('config.json','r'))
cookie = config['cookie']

declineUsers = None
declinedTrades = 0
totalTrades = 0
botTrades = 0

userId = requests.get('https://www.roblox.com/mobileapi/userinfo', cookies={'.ROBLOSECURITY': cookie}).json()['UserID']
req = requests.Session()
req.cookies['.ROBLOSECURITY'] = cookie

def title():
    while True:
        ctypes.windll.kernel32.SetConsoleTitleW(f'Total Trades: {totalTrades} | Bot Trades: {botTrades} | Declined Trades: {declinedTrades}')
        time.sleep(1)

threading.Thread(target=title).start()

def getUsers():
    global declineUsers
    botUsers = requests.get('https://raw.githubusercontent.com/67571303/declinelist/d0c43a1579e20de59807793df6f471090c88445e/manuallist').json()
    declineUsers = [i[0] for i in botUsers]

def getTrades():
    global totalTrades, botTrades
    cursor = ''
    toDecline = []
    while cursor != None:
        trades = req.get(f'https://trades.roblox.com/v1/trades/inbound?cursor={cursor}&limit=50&sortOrder=Desc').json()
        if 'data' in trades:
            totalTrades += len(trades['data'])
            toDecline = [trade['id'] for trade in trades['data'] if trade['user']['id'] in declineUsers]
            cursor = trades['nextPageCursor']
        elif 'TooManyRequests' in str(trades):
            time.sleep(60)
            continue
        else:
            print(trades)
            break
    botTrades += len(toDecline)
    if len(toDecline) >= 5:
        for i in range(5):
            threading.Thread(target=declineTrades, args=[toDecline[i::5]]).start()
    else:
        threading.Thread(target=declineTrades, args=[toDecline]).start()

def grabCsrf():
    return req.post('https://auth.roblox.com/v2/login').headers['X-CSRF-TOKEN']

def declineTrades(toDecline):
    global declinedTrades
    csrf = grabCsrf()
    for trade in toDecline:
        while True:
            decline = req.post(f'https://trades.roblox.com/v1/trades/{trade}/decline', headers={'X-CSRF-TOKEN': csrf}).json()
            if decline == {} or 'inactive' in str(decline):
                declinedTrades += 1
                break
            elif 'TooManyRequests' in str(decline):
                time.sleep(60)
                continue
            else:
                break
    return None

getUsers()
getTrades()
print(f'Declined {declinedTrades} trades. It may take a minute or two to actually take action')
