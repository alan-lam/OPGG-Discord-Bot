import discord, requests, bs4, re
from tabulate import tabulate
from markupsafe import escape

SUMMONER_URL = 'https://na.op.gg/summoner/userName='

client = discord.Client()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# https://stackoverflow.com/questions/44862112/how-can-i-send-an-embed-via-my-discord-bot-w-python

@client.event
async def on_message(message):
    if message.author == client.user:
        return
        
    if message.content.startswith('~help'):
        embed = discord.Embed(title='Available Commands', color = 0x00ff00)
        embed.add_field(name='~ladder [summoner name]', value='Displays ladder rank (% of all players in NA)', inline=False)
        embed.add_field(name='~rank [summoner name]', value='Displays ranked info (tier, lp, win/loss ratio, winrate %, series progress, league name)', inline=False)
        embed.add_field(name='~champions [summoner name]', value='Displays most champions played in current season', inline=False)
        embed.add_field(name='~playedwith [summoner name]', value='Displays summoners most recently played with and winrates with them', inline=False)
        await message.channel.send(embed=embed)
        
    elif message.content.startswith('~ladder'):
        summonerName = escape(' '.join(message.content.split()[1:]))
        soup = getRequest(SUMMONER_URL + summonerName)
        messageToSend = '```' + soup.select('.LadderRank a')[0].getText() + '```'
        embed = discord.Embed(title=summonerName, color = 0x00ff00)
        embed.add_field(name="Ladder Info", value=messageToSend)
        await message.channel.send(embed=embed)
        
    elif message.content.startswith('~rank'):
        summonerName = escape(' '.join(message.content.split()[1:]))
        soup = getRequest(SUMMONER_URL + summonerName)
        rankedInfo = soup.select('.TierRankInfo')[0]
        messageToSend = []
        for child in rankedInfo.stripped_strings:
            if child == '/':
                continue
            messageToSend.append(child)
            if child == 'Series In Progress':
                promos = soup.select('.SeriesResults i')
                promoStatus = []
                for item in promos:
                    if '__spSite-154' in item.get('class'):
                        promoStatus.append('L')
                    if '__spSite-156' in item.get('class'):
                        promoStatus.append('W')
                messageToSend.append(' '.join(promoStatus))
        messageToSend = '```' + '\n'.join(messageToSend) + '```'
        embed = discord.Embed(title=summonerName, color = 0x00ff00)
        embed.add_field(name="Ranked Info", value=messageToSend)
        await message.channel.send(embed=embed)
        
    elif message.content.startswith('~champions'):
        summonerName = escape(' '.join(message.content.split()[1:]))
        soup = getRequest(SUMMONER_URL + summonerName)
        championsPlayed = soup.select('.overview-stats--all')[0]
        messageToSend = []
        row = []
        kdaTotal = []
        kdaAvg = []
        i = 0
        for child in championsPlayed.stripped_strings:
            if child == '/' or child == 'KDA' or child == 'Show More + Past Seasons':
                continue
            if i % 8 == 1:
                row.append(child[3:]) # skip CS text at beginning
            # handle KDA formatting (total KDA on top, average KDA on bottom)
            elif i % 8 == 2:
                kdaTotal.append(child)
            elif i % 8 == 3 or i % 8 == 4 or i % 8 == 5:
                kdaAvg.append(child)
                if i % 8 == 5:
                    kdaTotal.append('/'.join(kdaAvg))
                    row.append('\n'.join(kdaTotal))
                    kdaTotal = []
                    kdaAvg = []
            elif i % 8 == 7:
                row.append(re.compile('\d+').search(child).group(0)) # skip played text at end
            else:
                row.append(child)
            if len(row) == 5:
                messageToSend.append(row)
                row = []
            i += 1
        messageToSend = '```' + tabulate(messageToSend, headers=['Champion', 'CS (/min)', 'KDA', 'Win Ratio', 'Games']) + '```'
        embed = discord.Embed(title=summonerName, color = 0x00ff00)
        embed.add_field(name="Champions Played (Season 2020)", value=messageToSend)
        await message.channel.send(embed=embed)
        
    elif message.content.startswith('~playedwith'):
        summonerName = escape(' '.join(message.content.split()[1:]))
        soup = getRequest(SUMMONER_URL + summonerName)
        playedWith = soup.select('.SummonersMostGameTable')[0]
        messageToSend = []
        row = []
        for child in playedWith.stripped_strings:
            row.append(child)
            if len(row) == 5:
                messageToSend.append(row)
                row = []
        messageToSend = '```' + tabulate(messageToSend, headers='firstrow') + '```'
        embed = discord.Embed(title=summonerName, color = 0x00ff00)
        embed.add_field(name="Recently Played With (Recent 10 Games)", value=messageToSend)
        await message.channel.send(embed=embed)
        
def getRequest(url):
    res = requests.get(url)
    res.raise_for_status()
    return bs4.BeautifulSoup(res.text, 'html.parser')
    
client.run('Njk4NzEwNjEzNTI5OTg1MDY1.XpKUCQ.PN3hVBFXYsQZ_HMgdXZuuxPTGnQ')