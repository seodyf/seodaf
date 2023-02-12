import time
import random

print('Use our GB changer to change pack sizes. Limit: 100GB\n')
print('Your IP Address is visible When you using this Raspberry DDoS attack service\n Use our Proxy services or TOR or Both to stay hidden\n')
print('Only PORTS allowed are: (443, 80, 8080, (9050 is a tor port that you can use) )\n')
print('We take No responsibility For your actions. And we dont condone it')
print('\n')

Proxy_IP = ['172.0.56.7', '192.0.67.8', '192.0.9.78.6', '24.34.192.7', '192.89.0.45', '192.890.78.8', '192.179.89.9', '78.56.789.8', '192.67.178.9', '23.45.678.0', '127.0.0.1', '192.0.89.0', '192.0.78.34.2', '178.4.54.67', '87.67.5.43']
IP = input('Enter IP Address: ')
PORT = input('Enter attacker Port: ')
Many = input('How many packs do you want to send: ')
GB = int(input('How many GB do you want one pack to be(Limit:100GB): '))
if GB > 100:
    print('Over 100 GB not supported.')
    time.sleep(100)
    quit()
if PORT == '443' or PORT == '8080' or PORT == '80' or PORT == '9050':
    Proxy = input('Do you Want to use proxychains(Y/N) : ')
    TOR = input('Do you want to use the Free Tor Services(Y/N): ')
    if Proxy == 'y' and TOR == 'y':
        TCP = [1, 2, 3]
        TCP_CONNECTION = random.choice(TCP)
        packs = 1
        print(f'Starting DDoS attack on PORT:{PORT}...')
        time.sleep(5)
        print('TCP Connection...')
        time.sleep(5)
        if TCP_CONNECTION == 1 or TCP_CONNECTION == 2:
            print(f'Attacking {IP}:{PORT}...')
            time.sleep(5)
            for pack_ddos in range(int(Many)):
                Proxy_IP_Random = random.choice(Proxy_IP)
                print(f'Sending packs: {packs}.. GB: {GB} \n Proxy: {Proxy_IP_Random}\n Using TOR')
                packs += 1
        else:
            print('TCP Connection failed. We could not provide a Three way handshake with the server.')

    elif Proxy == 'n' and TOR == 'n':
        TCP = [1, 2, 3]
        TCP_CONNECTION = random.choice(TCP)
        packs = 1
        print(f'Starting DDoS attack on PORT:{PORT}...')
        time.sleep(5)
        print('TCP Connection...')
        time.sleep(5)
        if TCP_CONNECTION == 1 or TCP_CONNECTION == 2:
            print(f'Attacking {IP}:{PORT}...')
            time.sleep(5)
            for pack_sending in range(int(Many)):
                print(f'Sending packs: {packs}.. GB: {GB} ')
                packs += 1

    elif Proxy == 'n' and TOR == 'y':
        TCP = [1, 2, 3]
        TCP_CONNECTION = random.choice(TCP)
        packs = 1
        print(f'Starting DDoS attack on PORT:{PORT}...')
        time.sleep(5)
        print('TCP Connection...')
        time.sleep(5)
        if TCP_CONNECTION == 1 or TCP_CONNECTION == 2:
            print(f'Attacking {IP}:{PORT}...')
            time.sleep(5)
            for pack_sending in range(int(Many)):
                Proxy_IP_Random = random.choice(Proxy_IP)
                print(f'Sending packs: {packs}.. GB: {GB} \n Using TOR')
                packs += 1
    else:
        TCP = [1, 2, 3]
        TCP_CONNECTION = random.choice(TCP)
        packs = 1
        print(f'Starting DDoS attack on PORT:{PORT}...')
        time.sleep(5)
        print('TCP Connection...')
        time.sleep(5)
        if TCP_CONNECTION == 1 or TCP_CONNECTION == 2:
            print(f'Attacking {IP}:{PORT}...')
            time.sleep(5)
            for pack_ddos in range(int(Many)):
                Proxy_IP_Random = random.choice(Proxy_IP)
                print(f'Sending packs: {packs}.. GB: {GB} \n Proxy: {Proxy_IP_Random}')
                packs += 1






else:
    print('Invalid Port')

print('Done')
time.sleep(100)