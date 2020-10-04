import requests
import json
import discord
import praw
import random
import asyncio
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook
from discord import Webhook,RequestsWebhookAdapter
from discord.ext import commands


class Main:
    def __init__(self):
        with open('configs.json','r') as f:
            config = json.load(f)

        self.token = config['token']
        self.prefix = config['prefix']
        self.author_dc = config['author_dc']
        self.author_dc_server = config['author_dc_server']
        self.icon_url = config['icon_url']
        self.embed_colour = 10181046
        self.embed_footer_message = config['embed_footer_message']
        self.reddit_app_client_id = config['reddit_app_client_id']
        self.reddit_praw_useragent = config['reddit_praw_useragent']
        self.chrome_header = headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

        self.commands = {
            "{0}nudefrom (subredditname)".format(self.prefix):"Get's a random nsfw picture/gif from the given subreddit",
            "{0}sxyprn_get (sortbyname,categoryname)".format(self.prefix):"Get's the latest video (sortbynames latest/views/rating/orgasmic) categorynames (all/top/other)",
            "{0}sxyprn_get_random (sortbyname,categoryname)".format(self.prefix):"Get's a random video (sortbynames latest/views/rating/orgasmic) categorynames (all/top/other)",
            "{0}sxyprn_get_random_latest".format(self.prefix):"Get's random latest video from the site",
            "{0}sxyprn_get_latest".format(self.prefix):"Get's the latest video from the site",
            "{0}sxyprn_get_random_most_viewed".format(self.prefix):"Get's a random most viewed video from the site",
            "{0}sxyprn_get_most_viewed".format(self.prefix):"Get's the most viewed video from the site",
            "{0}sxyprn_get_random_most_rated".format(self.prefix):"Get's a random most rated video from the site",
            "{0}sxyprn_get_most_rated".format(self.prefix):"Get's the top rated video from the site",
            "{0}sxyprn_get_random_most_orgasmic".format(self.prefix):"Get's a random most 'orgasmic' video from the site",
            "{0}sxyprn_get_most_orgasmic".format(self.prefix):"Get's the most 'orgasmic' video from the site",
            "{0}sxyprn_get_actress_random_latest (Actress Name)".format(self.prefix):"Sends you the a random video from the actress please use full names eg: Aaron Stone",
            "{0}sxyprn_get_actress_latest (Actress Name)".format(self.prefix):"Sends you the latest video from the actress please use full names eg: Aaron Stone",
            "{0}xhamster_random".format(self.prefix):"Sends you a random video",
            "{0}xhamster_get_actress_latest_video (actress name)".format(self.prefix):"Get's the given actress latest video",
            "{0}xhamster_get_channel_latest_video (channelname)".format(self.prefix):"Get's the given channel's latest video",
            "{0}xhamster_get_category_latest_video (category)".format(self.prefix):"Get's the given category's latest video",
            "{0}xhamster_random_daily".format(self.prefix):"Sends a random daily video",
            "{0}xhamster_best_daily".format(self.prefix):"Get's the best daily video",
            "{0}xhamster_best_daily_max_duration (maxduration)".format(self.prefix):"Get's the best daily video with max duration limit",
            "{0}xhamster_best_daily_between_duration (minduration,maxduration)".format(self.prefix):"Get's the best daily video with between durations",
            "{0}xhamster_best_daily_min_duration (minduration)".format(self.prefix):"Get's the best daily video with atleast minimum duration",
            "{0}xhamster_random_weekly".format(self.prefix):"Sends a random weekly video",
            "{0}xhamster_best_weekly".format(self.prefix):"Get's the weekly daily video",
            "{0}xhamster_best_weekly_max_duration (maxduration)".format(self.prefix):"Get's the best weekly video with max duration limit",
            "{0}xhamster_best_weekly_between_duration (minduration,maxduration)".format(self.prefix):"Get's the best weekly video with between durations",
            "{0}xhamster_best_weekly_min_duration (minduration)".format(self.prefix):"Get's the best weekly video with atleast minimum duration",
            "{0}xhamster_random_monthly".format(self.prefix):"Sends a random monthly video",
            "{0}xhamster_best_monthly".format(self.prefix):"Get's the best monthly video",
            "{0}xhamster_best_monthly_max_duration (maxduration)".format(self.prefix):"Get's the best monthly video with max duration limit",
            "{0}xhamster_best_monthly_between_duration (minduration,maxduration)".format(self.prefix):"Get's the best monthly video with between durations",
            "{0}xhamster_best_monthly_min_duration (minduration)".format(self.prefix):"Get's the best monthly video with atleast minimum duration",
            "{0}xhamster_random_year (year)".format(self.prefix):"Sends a random video from the given year",
            "{0}xhamster_best_year (year)".format(self.prefix):"Get's the best video in the given year",
            "{0}xhamster_best_year_max_duration (year,maxduration)".format(self.prefix):"Get's the best video in the given year with max duration limit",
            "{0}xhamster_best_year_between_duration (year,minduration,maxduration)".format(self.prefix):"Get's the best video in the given year with between durations",
            "{0}xhamster_best_year_min_duration (year,minduration)".format(self.prefix):"Get's the best video in the given year with atleast minimum duration",
            "{0}beeg_latest".format(self.prefix):"Get's the latest video from the website beeg",
            "{0}beeg_latest_detailed".format(self.prefix):"Get's the latest video from the website beeg and the actor/acctress name and his/her current videos on the site",
            "{0}mp4togif (url)".format(self.prefix):"Convert's mp4 file from url to gif and sends it embed"
        }

        self.checkWords = ['i.imgur.com', 'gif',"redgif",'webm','jpg','jpeg','png']
        
        self.reddit = praw.Reddit(client_id=self.reddit_app_client_id,client_secret=None,user_agent=self.reddit_praw_useragent)
        self.bot = commands.Bot(command_prefix=self.prefix, self_bot=False)
        


    def Start(self):

        def mp4togif_from_url(url):
            try:
                payload = {
                    'new-image':'(binary)',
                    'new-image-url':url,
                    'upload':'Upload video!'
                }
                response = requests.post('https://s2.ezgif.com/video-to-gif',data=payload)
                generated_ezgif_link = response.url
                generated_ezgif_filename = generated_ezgif_link.split('/')[-1]

                get_token_response = requests.get(generated_ezgif_link).text
                soup = BeautifulSoup(get_token_response,'html.parser')

                token = soup.find('input',{'name':'token'})
                token = token['value']


                payload = {
                    'file':generated_ezgif_filename,
                    'token':token,
                    'start':'0',
                    'end':'7',
                    'size':'original',
                    'fps':'10',
                    'method':'ffmpeg'
                }

                convert_response = requests.post('https://s2.ezgif.com/video-to-gif/{0}?ajax=true'.format(generated_ezgif_filename),data=payload).text
            
                soup = BeautifulSoup(convert_response,'html.parser')
                gif = soup.find('a',{'m-btn-crop'})
                gif_link = gif['href']
                
                payload = {
                    'file':generated_ezgif_filename,
                    'token':token,
                    'x1':'0',
                    'y1':'0',
                    'x2':'original',
                    'y2':'original',
                    'w':'original',
                    'h':'original',
                    'method':'gifsicle'
                }

                convert_crop = requests.post('{0}?ajax=true'.format(gif_link)).text

                soup = BeautifulSoup(convert_crop,'html.parser')
                gif_valid_url = soup.find('a',{'save'})['href']
                #gif_valid_url = gif_valid_url['href'].replace('save','tmp')

                return gif_valid_url
            except:
                pass

        def get_subreddit(subreddit_name:str):
            sub = self.reddit.subreddit(subreddit_name)
            posts = [post for post in sub.hot(limit=300)]
            random_post_number = random.randint(0, 300)
            random_post = posts[random_post_number]
            return random_post
        
        def GetRedGifFullUrl(url):
            if 'redgifs.com' in url:
                response = requests.get(url,headers=self.chrome_header)
                soup = BeautifulSoup(response.content, 'html.parser')

                return soup.find('img').attrs['src']
            else:
                return url

        @self.bot.command(pass_context=True)
        async def info(ctx):
            await ctx.message.delete()
            try:
                embed_message = discord.Embed(description='**[COMMANDS]**')
                embed_message.add_field(name="Author's contact", value="[Discord Server]({0})".format(self.author_dc_server),inline=False)
                embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                embed_message.add_field(name="IMPORTANT",value="Use the commands in a NSFW text channel",inline=False)
                for key in self.commands:
                    embed_message.add_field(name=key,value=self.commands[key],inline=False)

                embed_message.set_footer(text='{0}'.format(self.embed_footer_message))
                embed_message.colour = self.embed_colour
                await ctx.send(embed=embed_message)
            except:
                pass

        @self.bot.command(pass_context=True)
        async def nudefrom(ctx,subreddit_name):
            await ctx.message.delete()

            sub = get_subreddit(subreddit_name)
            url_text = sub.url
            has_domain = any(string in url_text for string in self.checkWords)
            
            while not has_domain:
                sub = get_subreddit(subreddit_name)
                url_text = sub.url
                await asyncio.sleep(0.1)

            if sub.over_18:
                if ctx.channel.is_nsfw():                    
                        try:
                            image_full_url = GetRedGifFullUrl(url_text)
                            embed_message = discord.Embed(description='**[{0}]**'.format(sub.title))
                            embed_message.add_field(name="Author's contact", value="[Discord Server]({0})".format(self.author_dc),inline=False)
                            embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                            embed_message.set_image(url=image_full_url)
                            embed_message.set_footer(text='REQUESTED: {0}\n\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                            embed_message.colour = self.embed_colour
                            await ctx.send(embed=embed_message)
                        except:
                            pass
                            

        @self.bot.command(pass_context=True) #categorynames all/top/other #sortbynames latest/views/rating/orgasmic
        async def sxyprn_get(ctx,sortbyname,categoryname):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm={0}&fl={1}".format(sortbyname,categoryname),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[0]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[0]['data-url'],inline=False)
                    
                    vid_url = myimages[0]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    #print(myvideos)
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[0]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                    
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass


        @self.bot.command(pass_context=True) #categorynames all/top/other #sortbynames latest/views/rating/orgasmic
        async def sxyprn_get_random(ctx,sortbyname,categoryname):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm={0}&fl={1}".format(sortbyname,categoryname),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    random_index = random.randint(0,30)
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[random_index]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[random_index]['data-url'],inline=False)
                    
                    vid_url = myimages[random_index]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[random_index]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                        
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass

        @self.bot.command(pass_context=True)
        async def sxyprn_get_latest(ctx):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm=latest&fl=all",headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[0]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[0]['data-url'],inline=False)
                    vid_url = myimages[0]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[0]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                        
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass


        @self.bot.command(pass_context=True)
        async def sxyprn_get_random_latest(ctx):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm=latest&fl=all",headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    random_index = random.randint(0,30)
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[random_indexm]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[random_index]['data-url'],inline=False)
                    vid_url = myimages[random_index]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[random_index]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                        
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass

        @self.bot.command(pass_context=True)
        async def sxyprn_get_most_viewed(ctx):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm=views&fl=all",headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[0]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[0]['data-url'],inline=False)
                    vid_url = myimages[0]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[0]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                        
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass

        @self.bot.command(pass_context=True)
        async def sxyprn_get_random_most_viewed(ctx):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm=views&fl=all",headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    random_index = random.randint(0,30)
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[random_index]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[random_index]['data-url'],inline=False)
                    vid_url = myimages[random_index]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[random_index]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                        
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass

        @self.bot.command(pass_context=True)
        async def sxyprn_get_most_rated(ctx):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm=rating&fl=all",headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[0]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[0]['data-url'],inline=False)
                    vid_url = myimages[0]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[0]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                    
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass

        @self.bot.command(pass_context=True)
        async def sxyprn_get_random_most_rated(ctx):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm=rating&fl=all",headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    random_index = random.randint(0,30)
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[random_index]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[random_index]['data-url'],inline=False)
                    vid_url = myimages[random_index]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[random_index]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                    
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass


        @self.bot.command(pass_context=True)
        async def sxyprn_get_most_orgasmic(ctx):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm=orgasmic&fl=all",headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[0]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[0]['data-url'],inline=False)
                    vid_url = myimages[0]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[0]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                    
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass

        @self.bot.command(pass_context=True)
        async def sxyprn_get_random_most_orgasmic(ctx):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/blog/all/0.html?sm=orgasmic&fl=all",headers=self.chrome_header).text
                    soup = BeautifulSoup(response,"html.parser")
                    mydivs = soup.findAll("div", {"class": "sharing_toolbox"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    random_index = random.randint(0,30)
                    embed_message = discord.Embed(description='**[{0}]**'.format(mydivs[random_index]['data-title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=mydivs[random_index]['data-url'],inline=False)
                    vid_url = myimages[random_index]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[random_index]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)
                    
                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass


        @self.bot.command(pass_context=True)
        async def sxyprn_get_actress_latest(ctx,actressname):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/{0}.html".format(actressname.replace(' ','-')),headers=self.chrome_header).text

                    soup = BeautifulSoup(response,"html.parser")
                    video_datas = soup.findAll("a", {"class": "tdn post_time"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    embed_message = discord.Embed(description='**[{0}]**'.format(video_datas[0]['title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value='https://sxyprn.com{0}'.format(video_datas[0]['href']),inline=False)
                    vid_url = myimages[0]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)

                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[0]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)

                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except:
                    pass

        @self.bot.command(pass_context=True)
        async def sxyprn_get_actress_random_latest(ctx,actressname):
            await ctx.message.delete()
            if ctx.channel.is_nsfw():
                try:
                    response = requests.get("https://sxyprn.com/{0}.html".format(actressname.replace(' ','-')),headers=self.chrome_header).text

                    soup = BeautifulSoup(response,"html.parser")
                    video_datas = soup.findAll("a", {"class": "tdn post_time"})
                    myimages = soup.findAll("img",{"class": "mini_post_vid_thumb"})
                    myvideos = soup.findAll("video",{"class": "hvp_player"})
                    random_index = random.randint(0,30)
                    embed_message = discord.Embed(description='**[{0}]**'.format(video_datas[random_index]['title']))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value='https://sxyprn.com{0}'.format(video_datas[random_index]['href']),inline=False)
                    vid_url = myimages[random_index]['src'].split('//',1)[1]
                    vid_url = "https://{0}".format(vid_url)
                    
                    if len(myvideos) > 0:
                        valid_mp4_url = myvideos[random_index]['src'].split('//',1)[1]
                        valid_mp4_url = "https://{0}".format(valid_mp4_url)
                        vid_url = mp4togif_from_url(valid_mp4_url)

                    embed_message.set_image(url=vid_url)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                except :
                    pass
                
               

        @self.bot.command(pass_context=True)
        async def xhamster_random(ctx):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/',headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    random_vid_index = random.randint(0,30)
                    video_link = ref_links[random_vid_index]['href']
                    video_mp4 = ref_links[random_vid_index]['data-previewvideo']
                    gif_url = mp4togif_from_url(video_mp4)
                    video_title = preview_data[random_vid_index]['alt']
                    video_duration = durations[random_vid_index].getText()
                    
                    embed_message = discord.Embed(description='**[{0} VIDEO]**\n'.format(video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass

        @self.bot.command(pass_context=True)
        async def xhamster_get_actress_latest_video(ctx,actressname):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    valid_actress_name = actressname.replace(' ','-')
                    response = requests.get('https://xhamster.com/pornstars/{0}'.format(valid_actress_name),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[{0} LATEST VIDEO]**\n{1}'.format(actressname,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass

        @self.bot.command(pass_context=True)
        async def xhamster_get_channel_latest_video(ctx,channelname):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    valid_channel_name = channelname.replace(' ','-')
                    response = requests.get('https://xhamster.com/channels/{0}'.format(valid_channel_name),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[{0} LATEST VIDEO]**\n{1}'.format(valid_channel_name,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass

        @self.bot.command(pass_context=True)
        async def xhamster_get_category_latest_video(ctx,categoryname):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/categories/{0}'.format(categoryname),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[{0} LATEST VIDEO]**\n{1}'.format(categoryname,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            
        @self.bot.command(pass_context=True)
        async def xhamster_best_daily(ctx):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/daily',headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST DAILY VIDEO]**\n{0}'.format(top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass

        @self.bot.command(pass_context=True)
        async def xhamster_random_daily(ctx):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/daily',headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    random_vid_index = random.randint(0,30)
                    top_video_link = ref_links[random_vid_index]['href']
                    top_video_mp4 = ref_links[random_vid_index]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[random_vid_index]['alt']
                    top_video_duration = durations[random_vid_index].getText()
                    
                    embed_message = discord.Embed(description='**[RANDOM DAILY VIDEO]**\n{0}'.format(top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                await xhamster_best_daily(ctx)

        @self.bot.command(pass_context=True)
        async def xhamster_best_daily_max_duration(ctx,max_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/daily?max-duration={0}'.format(max_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST DAILY VIDEO {0}min]**\n{1}'.format(max_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
           

        @self.bot.command(pass_context=True)
        async def xhamster_best_daily_between_duration(ctx,min_duration,max_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/daily?min-duration={0}&amp;max-duration={1}'.format(min_duration,max_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST DAILY VIDEO {0}min-{1}min]**\n{2}'.format(min_duration,max_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_daily_min_duration(ctx,min_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/daily?min-duration={0}'.format(min_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST DAILY VIDEO {0}min]**\n{1}'.format(min_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass


        @self.bot.command(pass_context=True)
        async def xhamster_random_weekly(ctx):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/weekly',headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    random_vid_index = random.randint(0,30)
                    top_video_link = ref_links[random_vid_index]['href']
                    top_video_mp4 = ref_links[random_vid_index]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[random_vid_index]['alt']
                    top_video_duration = durations[random_vid_index].getText()
                    
                    embed_message = discord.Embed(description='**[RANDOM WEEKLY VIDEO]**\n{0}'.format(top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                await xhamster_random_weekly(ctx)
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_weekly(ctx):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/weekly',headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST WEEKLY VIDEO]**\n{0}'.format(top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
                    
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_weekly_max_duration(ctx,max_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/weekly?max-duration={0}'.format(max_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST WEEKLY VIDEO {0}min]**\n{1}'.format(max_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_weekly_between_duration(ctx,min_duration,max_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/weekly?min-duration={0}&amp;max-duration={1}'.format(min_duration,max_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST WEEKLY VIDEO {0}min-{1}min]**\n{2}'.format(min_duration,max_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_weekly_min_duration(ctx,min_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/weekly?min-duration={0}'.format(min_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST WEEKLY VIDEO {0}min]**\n{1}'.format(min_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_random_monthly(ctx):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/monthly',headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    random_vid_index = random.randint(0,30)
                    top_video_link = ref_links[random_vid_index]['href']
                    top_video_mp4 = ref_links[random_vid_index]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[random_vid_index]['alt']
                    top_video_duration = durations[random_vid_index].getText()
                    
                    embed_message = discord.Embed(description='**[RANDOM MONTHLY VIDEO]**\n{0}'.format(top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                await xhamster_random_monthly(ctx)

        @self.bot.command(pass_context=True)
        async def xhamster_best_monthly(ctx):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/monthly',headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST MONTHLY VIDEO]**\n{0}'.format(top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_monthly_max_duration(ctx,max_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/monthly?max-duration={0}'.format(max_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST MONTHLY VIDEO {0}min]**\n{1}'.format(max_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_monthly_between_duration(ctx,min_duration,max_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/monthly?min-duration={0}&amp;max-duration={1}'.format(min_duration,max_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST MONTHLY VIDEO {0}min-{1}min]**\n{2}'.format(min_duration,max_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_monthly_min_duration(ctx,min_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/monthly?min-duration={0}'.format(min_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST MONTHLY VIDEO {0}min]**\n{1}'.format(min_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass

        @self.bot.command(pass_context=True)
        async def xhamster_random_yearly(ctx,year):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/year-{0}'.format(year),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    random_vid_index = random.randint(0,30)
                    top_video_link = ref_links[random_vid_index]['href']
                    top_video_mp4 = ref_links[random_vid_index]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[random_vid_index]['alt']
                    top_video_duration = durations[random_vid_index].getText()
                    
                    embed_message = discord.Embed(description='**[RANDOM {0} YEAR VIDEO]**\n{1}'.format(year,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                await xhamster_random_yearly(ctx,year)
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_year(ctx,year):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/year-{0}'.format(year),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST {0} YEAR VIDEO]**\n{1}'.format(year,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_year_max_duration(ctx,year,max_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/year-{0}?max-duration={1}'.format(year,max_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST {0} YEAR VIDEO {1}min]**\n{2}'.format(year,max_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_year_between_duration(ctx,year,min_duration,max_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/year-{0}?min-duration={1}&amp;max-duration={2}'.format(year,min_duration,max_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST {0} YEAR VIDEO {1}min-{2}min]**\n{3}'.format(year,min_duration,max_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def xhamster_best_year_min_duration(ctx,year,min_duration):
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://xhamster.com/best/year-{0}?min-duration={1}'.format(year,min_duration),headers=self.chrome_header).text
                    soup = BeautifulSoup(response,'html.parser')
                    ref_links = soup.find_all('a',{'class':'video-thumb__image-container thumb-image-container'})
                    preview_data = soup.find_all('img',{'thumb-image-container__image'})
                    durations = soup.find_all('div',{'thumb-image-container__duration'})
                    top_video_link = ref_links[0]['href']
                    top_video_mp4 = ref_links[0]['data-previewvideo']
                    gif_url = mp4togif_from_url(top_video_mp4)
                    top_video_title = preview_data[0]['alt']
                    top_video_duration = durations[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEST {0} YEAR VIDEO {1}min]**\n{2}'.format(year,min_duration,top_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=top_video_link,inline=False)
                    embed_message.set_image(url=gif_url)
                    embed_message.add_field(name='DURATION',value=top_video_duration,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass

        @self.bot.command(pass_context=True)
        async def beeg_latest(ctx): #if this is not working then it is probably ratelimited
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():
                    response = requests.get('https://beeg.com',headers=self.chrome_header).text

                    soup = BeautifulSoup(response,'html.parser')
                    
                    video_ref_urls = soup.find_all('a',{'XxxThumb__content'})
                    video_data = soup.find_all('img',{'XxxThumb__img-preview'})

                    first_video_title = video_data[0]['alt']
                    first_video_thumbnail = video_data[0]['src']
                    first_video_url = 'https://beeg.com{0}'.format(video_ref_urls[0]['href'])
                    
                    embed_message = discord.Embed(description='**[BEEG LATEST VIDEO]**\n{0}'.format(first_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=first_video_url,inline=False)
                    embed_message.set_image(url=first_video_thumbnail)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass

        @self.bot.command(pass_context=True)
        async def beeg_latest_detailed(ctx): #if this is not working then it is probably ratelimited
            await ctx.message.delete()
            try:
                if ctx.channel.is_nsfw():

                    response = requests.get('https://beeg.com',headers=self.chrome_header).text

                    soup = BeautifulSoup(response,'html.parser')
                    
                    video_ref_urls = soup.find_all('a',{'XxxThumb__content'})
                    video_data = soup.find_all('img',{'XxxThumb__img-preview'})

                    first_video_title = video_data[0]['alt']
                    first_video_thumbnail = video_data[0]['src']
                    first_video_url = 'https://beeg.com{0}'.format(video_ref_urls[0]['href'])

                    response = requests.get(first_video_url,headers=self.chrome_header).text

                    soup = BeautifulSoup(response,'html.parser')

                    video_actors = soup.find_all('a',{'XxxChannelListing__title'})
                    first_video_actor = video_actors[0].getText()
                    video_actors_videos = soup.find_all('div','XxxChannelListing__videos')
                    first_video_actor_videos = video_actors_videos[0].getText()
                    
                    embed_message = discord.Embed(description='**[BEEG LATEST VIDEO]**\n{0}'.format(first_video_title))
                    embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                    embed_message.add_field(name="URL", value=first_video_url,inline=False)
                    embed_message.set_image(url=first_video_thumbnail)
                    embed_message.add_field(name="Actor/Actress name", value=first_video_actor,inline=False)
                    embed_message.add_field(name="Actor/Actress videos", value=first_video_actor_videos,inline=False)
                    embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                    embed_message.colour = self.embed_colour
                    await ctx.send(embed=embed_message)
            except:
                pass
            

        @self.bot.command(pass_context=True)
        async def mp4togif(ctx,url):
            await ctx.message.delete()
            try:
                payload = {
                    'new-image':'(binary)',
                    'new-image-url':url,
                    'upload':'Upload video!'
                }
                response = requests.post('https://s2.ezgif.com/video-to-gif',data=payload)
                generated_ezgif_link = response.url
                generated_ezgif_filename = generated_ezgif_link.split('/')[-1]

                get_token_response = requests.get(generated_ezgif_link).text
                soup = BeautifulSoup(get_token_response,'html.parser')

                token = soup.find('input',{'name':'token'})
                token = token['value']

                payload = {
                    'file':generated_ezgif_filename,
                    'token':token, #if the request is wrong then they changed the method
                    'start':'0',
                    'end':'7',
                    'size':'original',
                    'fps':'10',
                    'method':'ffmpeg'
                }
                
                convert_response = requests.post('https://s2.ezgif.com/video-to-gif/{0}?ajax=true'.format(generated_ezgif_filename),data=payload).text
            
                soup = BeautifulSoup(convert_response,'html.parser')
                gif = soup.find('a',{'m-btn-crop'})
                gif = gif['href']

                embed_message = discord.Embed(description='**[GENERATED GIF FROM MP4]**')
                embed_message.set_author(name="{0}".format(self.author_dc), icon_url="{0}".format(self.icon_url))
                embed_message.add_field(name="URL", value=gif,inline=False)
                embed_message.set_image(url=gif)
                embed_message.set_footer(text='REQUESTED: {0}\n{1}'.format(ctx.message.author.name,self.embed_footer_message))
                embed_message.colour = self.embed_colour
                await ctx.send(embed=embed_message)
            except:
                pass
            
        self.bot.run(self.token,bot=True)

if __name__ == '__main__':
    main = Main()
    main.Start()


