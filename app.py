import discord
import os  
import threading
import gradio as gr
import requests
import json
import random
import time
import re
from discord import Embed, Color
from discord.ext import commands
# a
from gradio_client import Client
from PIL import Image
#from ratelimiter import RateLimiter

import asyncio
import concurrent.futures
import multiprocessing

import shutil # for doing image movement magic

#import tempfile
#import glob

import uuid
import glob

#todo
# experiment with animeGANv2
#✅ tasks for concurrent coroutines (now jobs)
# ratelimits

# enlarge each of 4 images?
# Error: [Errno 104] Connection reset by peer?

# clean up old threads
# safety for on_reaction_add?
# could use one channel, use threads to organize it. Otherwise may be too split and harder to keep track of
# lock generation after ~120s, can change
# restructure using slash commands? generate -> deepfloydif -> prompt -> thread -> combined -> upscale -> thread

GRADIOTEST_TOKEN = os.getenv('HF_TOKEN')
DISCORD_TOKEN = os.environ.get("GRADIOTEST_TOKEN", None)

df = Client("huggingface-projects/IF", GRADIOTEST_TOKEN)
jojogan = Client("akhaliq/JoJoGAN", GRADIOTEST_TOKEN)
falconclient = Client("HuggingFaceH4/falcon-chat", GRADIOTEST_TOKEN)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

#---------------------------------------------------------------------------------------------------------------------------------------------
@bot.command()
async def info(ctx):
    current_directory = os.getcwd()
    temp_directory = tempfile.gettempdir()
    await ctx.reply(f"current_directory={current_directory}\n temp_directory={temp_directory}")
#---------------------------------------------------------------------------------------------------------------------------------------------
@bot.event
async def on_ready():
    print('Logged on as', bot.user)
    bot.log_channel = bot.get_channel(1100458786826747945) # 1100458786826747945 = bot-test, 1107006391547342910 = lunarbot server  
#--------------------------------------------------------------------------------------------------------------------------------------------- 
@bot.command()
async def commands(ctx):
    try:
        if await safetychecks(ctx):    
            await ctx.reply(f"Use !deepfloydif [prompt], !jojo !spidey or !sketch. Have fun! 🤗💖")
    except Exception as e:
        print(f"Error: unable to help :( {e}")   
#---------------------------------------------------------------------------------------------------------------------------------------------   
async def safetychecks(ctx): 
    failure_emoji = '<:disagree:1098628957521313892>' 
    try:
        if ctx.author.bot:
            print(f"Error: The bot is not allowed to use its own commands.")
            await ctx.message.add_reaction(failure_emoji)
            return False
    
        #✅✅ check if the bot is offline 
        offline_bot_role_id = 1103676632667017266
        bot_member = ctx.guild.get_member(bot.user.id)
        if any(role.id == offline_bot_role_id for role in bot_member.roles):
            print(f"Error: {ctx.author} The bot is offline or under maintenance. (Remove the offline-bot role to bring it online)") 
            thread = await ctx.message.create_thread(name=f'Offline Error')
            await thread.send(f"Error: {ctx.author.mention} The bot is offline or under maintenance. (Remove the offline-bot role to bring it online)")
            await ctx.message.add_reaction(failure_emoji)
            return False
    
        #✅✅ check if the command is in the allowed channel(s)
        bot_test = 1100458786826747945
        deepfloydif_channel = 1113182673859518514
        jojo_channel = 1114217739473649764
        sketch_channel = 1114218145343877180
        spidey_channel = 1114218191594471514
        falcon_channel = 1116089829147557999
        
        channel_ids = [bot_test, deepfloydif_channel, jojo_channel, spidey_channel, sketch_channel, falcon_channel]
        if ctx.channel.id not in channel_ids: 
            print(f"{ctx.author}, commands are not permitted in {ctx.channel}")
            thread = await ctx.message.create_thread(name=f'Channel Error')
            await thread.send(f"Error: {ctx.author.mention} commands are not permitted in {ctx.channel}")
            await ctx.message.add_reaction(failure_emoji)
            return False            
            
        #✅✅ check if the user has the required role(s)   
        guild_id = 879548962464493619
        verified_role_id = 900063512829755413  # @verified = 900063512829755413,  HF = 897376942817419265, fellows = 963431900825919498
        huggingfolks_role_id = 897376942817419265
        fellows_role_id = 963431900825919498
        contentcreator_role_id = 928589475968323636
        betatester_role_id = 1113511652990668893
        
        allowed_role_ids = [huggingfolks_role_id, fellows_role_id, contentcreator_role_id, betatester_role_id]
        guild = bot.get_guild(guild_id)
        user_roles = ctx.author.roles
        has_allowed_role = any(role.id in allowed_role_ids for role in user_roles)
        if not has_allowed_role:
            print(f"Error: {ctx.author} does not have any of the required roles to use that command.")
            thread = await ctx.message.create_thread(name=f'Perms Error')
            await thread.send(f"Error: {ctx.author.mention} does not have any of the required roles to use that command.")
            await ctx.message.add_reaction(failure_emoji)
            return False
            
    
        return True

    # ping lunarflu if any safety check ever fails
    except Exception as e:
        print(f"Error: safetychecks failed somewhere, command will not continue, {e}")
        await ctx.message.reply(f"❌ <@811235357663297546> SC failed somewhere ❌ {e}") # this will always ping, as long as the bot has access to the channel
        await ctx.message.add_reaction(failure_emoji)
#---------------------------------------------------------------------------------------------------------------------------------------------- 
@bot.command()
async def deepfloydifdemo(ctx):
    try:
        thread = await ctx.message.create_thread(name=f'{ctx.author} Demo Thread')
        await thread.send(f'{ctx.author.mention} Here is a demo for the !deepfloydif command!')
        await asyncio.sleep(0.5)
        await thread.send(f'https://cdn.discordapp.com/attachments/932563860597121054/1113483403258499142/image.png')
    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.add_reaction('<:disagree:1098628957521313892>')
#---------------------------------------------------------------------------------------------------------------------------------------------- 
@bot.command()
async def jojodemo(ctx):
    try:
        thread = await ctx.message.create_thread(name=f'JoJo Demo {ctx.author} ')
        await thread.send(f'{ctx.author.mention} Here is a demo for the !jojo command!')
        await asyncio.sleep(0.5)
        await thread.send(f'https://cdn.discordapp.com/attachments/932563860597121054/1114220616199966810/image.png')
        await thread.edit(archived=True)        
    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.add_reaction('<:disagree:1098628957521313892>')
        await thread.edit(archived=True)        
#---------------------------------------------------------------------------------------------------------------------------------------------- 
@bot.command()
async def sketchdemo(ctx):
    try:
        thread = await ctx.message.create_thread(name=f'Sketch Demo {ctx.author} ')
        await thread.send(f'{ctx.author.mention} Here is a demo for the !sketch command!')
        await asyncio.sleep(0.5)
        await thread.send(f'https://cdn.discordapp.com/attachments/932563860597121054/1114220716498370641/image.png')
        await thread.edit(archived=True)        
    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.add_reaction('<:disagree:1098628957521313892>')
        await thread.edit(archived=True)        
#---------------------------------------------------------------------------------------------------------------------------------------------- 
@bot.command()
async def spideydemo(ctx):
    try:
        thread = await ctx.message.create_thread(name=f'Spidey Demo {ctx.author} ')
        await thread.send(f'{ctx.author.mention} Here is a demo for the !spidey command!')
        await asyncio.sleep(0.5)
        await thread.send(f'https://cdn.discordapp.com/attachments/932563860597121054/1114220798085959690/image.png')
        await thread.edit(archived=True)
    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.add_reaction('<:disagree:1098628957521313892>')
        await thread.edit(archived=True)        
#----------------------------------------------------------------------------------------------------------------------------------------------         
# jojo ✅
@bot.command()
async def jojo(ctx):
    # img + face    ✅
    # img + no face ✅
    # no image      ✅
    # no generation ✅
    # responsive?   ✅
    # ratelimits?   ❌
    # safety checks?✅
    # bot no crash  ✅
    try:  
        if await safetychecks(ctx): #✅
            if ctx.channel.id == 1114217739473649764:
                await ctx.message.add_reaction('<a:loading:1114111677990981692>') 
                thread = await ctx.message.create_thread(name=f'Jojo | {ctx.author}', auto_archive_duration=60)         
                if ctx.message.attachments:
                    await thread.send(f'{ctx.author.mention} Generating images in thread, can take ~1 minute...yare yare, daze ...')  
                    attachment = ctx.message.attachments[0]
                    style = 'JoJo'
                    #im = jojogan.predict(attachment.url, style)
                    im = await asyncio.get_running_loop().run_in_executor(None, jojogan.predict, attachment.url, style)
                    #await ctx.message.reply(f'Here is the {style} version of it', file=discord.File(im))
                    await thread.send(f'{ctx.author.mention} Here is the {style} version of it', file=discord.File(im))
    
                    #testing animated
                    # <a:hugging_spin:1102656012621713488>
                    await ctx.message.add_reaction('<:agree:1098629085955113011>') # ✅   
                    await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
                    await thread.edit(archived=True)
                else: # no image
                    await thread.send(f"{ctx.author.mention} No attachments to be found...Can't animify dat! Try sending me an image 😉")
                    await ctx.message.add_reaction('<:disagree:1098628957521313892>') # ❌
                    await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
                    await thread.edit(archived=True)
    except Exception as e: # no generation / img + no face
        await fullqueue(e, thread)  
        print(f"Error: {e}")
        await thread.send(f"{ctx.author.mention} Error: {e}")
        await ctx.message.add_reaction('<:disagree:1098628957521313892>') # ❌
        await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
        await thread.edit(archived=True)
    
   
#---------------------------------------------------------------------------------------------------------------------------------------------- 
# Spider-Verse ✅
@bot.command()
async def spidey(ctx):
    try:
        if await safetychecks(ctx): #✅ 
            if ctx.channel.id == 1114218191594471514:
                await ctx.message.add_reaction('<a:loading:1114111677990981692>') 
                thread = await ctx.message.create_thread(name=f'Spider-verse | {ctx.author}', auto_archive_duration=60)         
                if ctx.message.attachments:
                    await thread.send(f'{ctx.author.mention} Generating images in thread, can take ~1 minute...')  
                    attachment = ctx.message.attachments[0]
                    style = 'Spider-Verse'
                    im = await asyncio.get_running_loop().run_in_executor(None, jojogan.predict, attachment.url, style)
                    await thread.send(f'{ctx.author.mention} Here is the {style} version of it', file=discord.File(im))
                    await ctx.message.add_reaction('<:agree:1098629085955113011>') # img + face    
                    await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user) 
                    await thread.edit(archived=True)                
                else: # no image
                    await thread.send(f"{ctx.author.mention} No attachments to be found...Can't animify dat! Try sending me an image 😉")
                    await ctx.message.add_reaction('<:disagree:1098628957521313892>')  
                    await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
                    await thread.edit(archived=True)                
    except Exception as e: # no generation / img + no face
        await fullqueue(e, thread)       
        print(f"Error: {e}")
        await thread.send(f"{ctx.author.mention} Error: {e}")
        await ctx.message.add_reaction('<:disagree:1098628957521313892>') 
        await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
        await thread.edit(archived=True)        
#---------------------------------------------------------------------------------------------------------------------------------------------- 
# sketch ✅
@bot.command()
async def sketch(ctx):
    try:    
        if await safetychecks(ctx): #✅
            if ctx.channel.id == 1114218145343877180:
                await ctx.message.add_reaction('<a:loading:1114111677990981692>') 
                thread = await ctx.message.create_thread(name=f'Sketch | {ctx.author}', auto_archive_duration=60)         
                if ctx.message.attachments:
                    await thread.send(f'{ctx.author.mention} Generating images in thread, can take ~1 minute...')  
                    attachment = ctx.message.attachments[0]
                    #style = 'sketch'
                    im = await asyncio.get_running_loop().run_in_executor(None, jojogan.predict, attachment.url, 'sketch')
                    await thread.send(f'{ctx.author.mention} Here is the sketch version of it', file=discord.File(im))
                    await ctx.message.add_reaction('<:agree:1098629085955113011>') # img + face 
                    await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user) 
                    await thread.edit(archived=True)                
                else: # no image
                    await thread.send(f"{ctx.author.mention} No attachments to be found...Can't animify dat! Try sending me an image 😉")
                    await ctx.message.add_reaction('<:disagree:1098628957521313892>') 
                    await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
                    await thread.edit(archived=True)                
    except Exception as e: # no generation / img + no face
        await fullqueue(e, thread)  
        print(f"Error: {e}")
        await thread.send(f"{ctx.author.mention} Error: {e}")
        await ctx.message.add_reaction('<:disagree:1098628957521313892>') 
        await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
        await thread.edit(archived=True)        
#----------------------------------------------------------------------------------------------------------------------------------------------
async def fullqueue(e, thread):
    error_message = str(e)
    if "Error: Expecting value: line 1 column 1 (char 0)" in error_message:
        await thread.send("Queue is full! Please try again.")
    elif "Error: Queue is full! Please try again." in error_message:
        await thread.send("Queue is full! Please try again.")
    # raised when the space we depend on needs to build after some inactivity (~10h)
    elif "local variable 'stage_1_results' referenced before assignment" in error_message:
        await thread.send("Space is building! Please try again after a few minutes.")    

#----------------------------------------------------------------------------------------------------------------------------------------------  


# deepfloydif stage 1 generation ✅
def inference(prompt):
    negative_prompt = ''
    seed = random.randint(0, 1000)
    #seed = 1
    number_of_images = 4
    guidance_scale = 7
    custom_timesteps_1 = 'smart50'
    number_of_inference_steps = 50
    
    stage_1_results, stage_1_param_path, stage_1_result_path = df.predict(
        prompt, negative_prompt, seed, number_of_images, guidance_scale, custom_timesteps_1, number_of_inference_steps, api_name='/generate64')
    
    return [stage_1_results, stage_1_param_path, stage_1_result_path]
#---------------------------------------------------------------------------------------------------------------------------------------------- 
# deepfloydif stage 2 upscaling ✅
def inference2(index, stage_1_result_path):
    selected_index_for_stage_2 = index
    seed_2 = 0
    guidance_scale_2 = 4
    custom_timesteps_2 = 'smart50'
    number_of_inference_steps_2 = 50
    result_path = df.predict(stage_1_result_path, selected_index_for_stage_2, seed_2, 
                             guidance_scale_2, custom_timesteps_2, number_of_inference_steps_2, api_name='/upscale256')
    
    return result_path    
#----------------------------------------------------------------------------------------------------------------------------------------------  
# ✅
async def react1234(reaction_emojis, combined_image_dfif):
    for emoji in reaction_emojis:
        await combined_image_dfif.add_reaction(emoji)  
#----------------------------------------------------------------------------------------------------------------------------------------------  
# Stage 1 ✅
@bot.command()
async def deepfloydif(ctx, *, prompt: str):
    thread = None
    try:
        try:
            if await safetychecks(ctx): #✅
                if ctx.channel.id == 1113182673859518514:
                    await ctx.message.add_reaction('<a:loading:1114111677990981692>') 
                    dfif_command_message_id = ctx.message.id # we will use this in some magic later on
                    thread = await ctx.message.create_thread(name=f'DeepfloydIF | {prompt}', auto_archive_duration=60) # could also just use prompt, no deepfloydif
                    # create thread -> send new message inside thread + combined_image -> add reactions -> dfif2
        
                    #current_time = int(time.time())
                    #random.seed(current_time)
        
                    negative_prompt = ''
                    seed = random.randint(0, 1000)
                    #seed = 1
                    number_of_images = 4
                    guidance_scale = 7
                    custom_timesteps_1 = 'smart50'
                    number_of_inference_steps = 50
                    api_name = '/generate64'
                    await thread.send(f'{ctx.author.mention}Generating images in thread, can take ~1 minute...')
            
        except Exception as e:
            print(f"Error: {e}")
            if thread is None:
                thread = await ctx.message.create_thread(name=f'DFIF1 Error')  
            await thread.send(f"{ctx.author.mention} Error before stage 1 generation, {e}. If error code: 50035, upscale can still work.")
            await fullqueue(e, thread)  
            await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
            await ctx.message.add_reaction('<:disagree:1098628957521313892>')
            await thread.edit(archived=True)            
        #generation✅-------------------------------------------------------
        try:
            #stage_1_results, stage_1_param_path, stage_1_result_path = df.predict(
            #    prompt, negative_prompt, seed, number_of_images, guidance_scale, custom_timesteps_1, number_of_inference_steps, api_name='/generate64')

            # run blocking function in executor
            await thread.send(f'✅running blocking function in executor')  
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, inference, prompt)
            await thread.send(f'{ctx.author.mention}after executor')
            await thread.send(f'✅run_in_executor ran successfully')            
            stage_1_results = result[0]
            stage_1_result_path = result[2]
            
            partialpath = stage_1_result_path[5:] #magic for later
            
        except Exception as e:
            print(f"Error: {e}")
            if thread is None:
                thread = await ctx.message.create_thread(name=f'Generation Error')
            await thread.send(f"{ctx.author.mention} Error during stage 1 generation, {e}")
            await fullqueue(e, thread)  
            await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
            await ctx.message.add_reaction('<:disagree:1098628957521313892>')
            await thread.edit(archived=True)            
        #posting images✅----------------------------------------------------------------    
        try:
            await thread.send(f'✅combining images...') 
            #old, see: https://huggingface.co/spaces/DeepFloyd/IF/commit/fb79844b1d0b013a28ac435a36f804d8030fba50
            #png_files = [f for f in os.listdir(stage_1_results) if f.endswith('.png')] 
            png_files = list(glob.glob(f"{stage_1_results}/**/*.png"))

            if png_files:
                first_png = png_files[0]
                second_png = png_files[1]
                third_png = png_files[2]
                fourth_png = png_files[3]
    
                first_png_path = os.path.join(stage_1_results, first_png)
                second_png_path = os.path.join(stage_1_results, second_png)
                third_png_path = os.path.join(stage_1_results, third_png)
                fourth_png_path = os.path.join(stage_1_results, fourth_png)
    
                img1 = Image.open(first_png_path)
                img2 = Image.open(second_png_path)
                img3 = Image.open(third_png_path)
                img4 = Image.open(fourth_png_path)
    
                combined_image = Image.new('RGB', (img1.width * 2, img1.height * 2))
    
                combined_image.paste(img1, (0, 0))
                combined_image.paste(img2, (img1.width, 0))
                combined_image.paste(img3, (0, img1.height))
                combined_image.paste(img4, (img1.width, img1.height))
    
                combined_image_path = os.path.join(stage_1_results, f'{partialpath}{dfif_command_message_id}.png')
                combined_image.save(combined_image_path)   

            with open(combined_image_path, 'rb') as f:
                combined_image_dfif = await thread.send(f'{ctx.author.mention}React with the image number you want to upscale!', file=discord.File(
                    f, f'{partialpath}{dfif_command_message_id}.png')) # named something like: tmpgtv4qjix1111269940599738479.png 

            await thread.send(f'✅reacting with 1234...') 
            emoji_list = ['↖️', '↗️', '↙️', '↘️']
            await react1234(emoji_list, combined_image_dfif)
            
            ''' individual images
            if png_files:
                for i, png_file in enumerate(png_files):
                    png_file_path = os.path.join(stage_1_results, png_file)
                    img = Image.open(png_file_path)
                    image_path = os.path.join(stage_1_results, f'{i+1}{partialpath}.png')
                    img.save(image_path)
                    with open(image_path, 'rb') as f:
                        await thread.send(f'{ctx.author.mention}Image {i+1}', file=discord.File(f, f'{i+1}{partialpath}.png'))
                    await asyncio.sleep(1)             
            
            '''
            
        except Exception as e:
            print(f"Error: {e}")
            if thread is None:
                thread = await ctx.message.create_thread(name=f'Posting Error')
            await thread.send(f"{ctx.author.mention} Encountered error while posting combined image in thread, {e}")
            await fullqueue(e, thread)  
            await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
            await ctx.message.add_reaction('<:disagree:1098628957521313892>')
            await thread.edit(archived=True)            
    #deepfloydif try/except
    except Exception as e:
        print(f"Error: {e}")
        if thread is None:
            thread = await ctx.message.create_thread(name=f'deepfloydif Error')
        await thread.send(f"{ctx.author.mention} Overall error with deepfloydif, {e}")
        await fullqueue(e, thread)  
        await ctx.message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
        await ctx.message.add_reaction('<:disagree:1098628957521313892>')
        await thread.edit(archived=True)
#----------------------------------------------------------------------------------------------------------------------------
# Stage 2 ✅
async def dfif2(index: int, stage_1_result_path, thread, dfif_command_message_id): # add safetychecks
    try:
        number = index + 1
        if number == 1:
            position = "top left"
        elif number == 2:
            position = "top right"
        elif number == 3:
            position = "bottom left"
        elif number == 4:
            position = "bottom right" 
        await thread.send(f"Upscaling the {position} image...")  
        
        # run blocking function in executor
        loop = asyncio.get_running_loop()
        result_path = await loop.run_in_executor(None, inference2, index, stage_1_result_path)

        #await thread.send(f"✅upscale done")          
        with open(result_path, 'rb') as f:
            await thread.send(f'Here is the upscaled image! :) ', file=discord.File(f, 'result.png'))
            
        parent_channel = thread.parent
        dfif_command_message = await parent_channel.fetch_message(dfif_command_message_id)
        await dfif_command_message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
        await dfif_command_message.add_reaction('<:agree:1098629085955113011>')
        await thread.edit(archived=True)

    except Exception as e:
        print(f"Error: {e}")
        parent_channel = thread.parent
        dfif_command_message = await parent_channel.fetch_message(dfif_command_message_id)
        await dfif_command_message.remove_reaction('<a:loading:1114111677990981692>', bot.user)
        await dfif_command_message.add_reaction('<:disagree:1098628957521313892>')  
        await thread.send(f"Error during stage 2 upscaling, {e}") 
        await fullqueue(e, thread) 
        await thread.edit(archived=True)
#----------------------------------------------------------------------------------------------------------------------------
# react detector for stage 2 ✅
@bot.event
async def on_reaction_add(reaction, user):    # ctx = await bot.get_context(reaction.message)? could try later, might simplify
    try:
        #ctx = await bot.get_context(reaction.message)
        # safety checks first ✅

        
        if not user.bot: 
            thread = reaction.message.channel
            threadparentid = thread.parent.id
            if threadparentid == 1113182673859518514: # testing-the-bot, should be whatever the deepfloydif channel is
                # 811235357663297546 =  lunarflu
                if reaction.message.attachments:
                    if user.id == reaction.message.mentions[0].id:  #  if user.id == reaction.message.mentions[0].id:           
                        # magic begins
                        #await reaction.message.channel.send("✅reaction detected")
                        attachment = reaction.message.attachments[0]
                        image_name = attachment.filename # named something like: tmpgtv4qjix1111269940599738479.png
                        # remove .png first
                        partialpathmessageid = image_name[:-4] # should be tmpgtv4qjix1111269940599738479 
                        # extract partialpath, messageid
                        partialpath = partialpathmessageid[:11] # tmpgtv4qjix
                        messageid = partialpathmessageid[11:] # 1111269940599738479
                        # add /tmp/ to partialpath, save as new variable
                        fullpath = "/tmp/" + partialpath # should be /tmp/tmpgtv4qjix
                        #await reaction.message.channel.send(f"✅fullpath extracted, {fullpath}")        
                        emoji = reaction.emoji
                        
                        if emoji == "↖️":
                            index = 0
                        elif emoji == "↗️":
                            index = 1
                        elif emoji == "↙️":
                            index = 2
                        elif emoji == "↘️":
                            index = 3 
                            
                        #await reaction.message.channel.send(f"✅index extracted, {index}")         
                        index = index
                        stage_1_result_path = fullpath
                        thread = reaction.message.channel
                        dfif_command_message_id = messageid
                        ctx = await bot.get_context(reaction.message)
                        #await reaction.message.channel.send(f"✅calling dfif2")  
                        await dfif2(index, stage_1_result_path, thread, dfif_command_message_id)

    except Exception as e:
        print(f"Error: {e} (known error, does not cause issues, fix later)")


#---------------------------------------------------------------------------------------------------------------------------- 
chathistory = None


falcon_chats = []
falcon_threads = []

@bot.command()
async def falconprivate(ctx):
    try:
        global falcon_chats
        if ctx.channel.id == 1116089829147557999: # #falcon
            if ctx.author.id not in falcon_chats: # create a new one
                thread = await ctx.message.create_thread(name=f'{ctx.author}')
                falcon_chats = [ctx.author.id] + falcon_chats
                await thread.send(f"Thread created")

            elif ctx.author.id in falcon_chats:
                await ctx.reply(f"{ctx.author.mention}, you already have an existing conversation! ")

        if ctx.channel.name == ctx.author:
            await ctx.reply(f"inside thread")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.reply(f"{e} cc <@811235357663297546> (falconprivate error)")           

@bot.command()
async def falcon(ctx, *, prompt: str):
    try:
        if await safetychecks(ctx): 
            if ctx.channel.id == 1116089829147557999:
                global chathistory
                
                if chathistory is not None: # This handles all subsequent discussions/prompts to the chatbot/model
                    instructions = "The following is a conversation between a highly knowledgeable and intelligent AI assistant, called Falcon, and a human user, called User. In the following interactions, User and Falcon will converse in natural language, and Falcon will answer User's questions. Falcon was built to be respectful, polite and inclusive. Falcon was built by the Technology Innovation Institute in Abu Dhabi. Falcon will never decline to answer a question, and always attempts to give an answer that User would be satisfied with. It knows a lot, and always tells the truth. The conversation begins."
                    job = falconclient.submit(prompt, chathistory, instructions, 0.8, 0.9, fn_index=1)  # This is not blocking
                    while job.done() == False: 
                        status = job.status() 
                    else:
                        file_paths = job.outputs()
                        full_generation = file_paths[-1]
                        chathistory = full_generation # we store this and pass it in the loop
                    with open(full_generation, 'r') as file:
                        data = json.load(file)
                        output_text = data[-1][-1] # we output this as the bot
                    print(output_text)
                    await ctx.reply(f"{output_text}")
                
                if chathistory == None: # This handles the start of a conversation/chathistory file with the model
                    chathistory = falconclient.predict( 
                            fn_index=5
                    ) 
                    instructions = "The following is a conversation between a highly knowledgeable and intelligent AI assistant, called Falcon, and a human user, called User. In the following interactions, User and Falcon will converse in natural language, and Falcon will answer User's questions. Falcon was built to be respectful, polite and inclusive. Falcon was built by the Technology Innovation Institute in Abu Dhabi. Falcon will never decline to answer a question, and always attempts to give an answer that User would be satisfied with. It knows a lot, and always tells the truth. The conversation begins."
                    job = falconclient.submit(prompt, chathistory, instructions, 0.8, 0.9, fn_index=1)  # This is not blocking
                    while job.done() == False: 
                        status = job.status() 
                    else:
                        file_paths = job.outputs()
                        full_generation = file_paths[-1]
                        chathistory = full_generation # we store this and pass it in the loop
                    with open(full_generation, 'r') as file:
                        data = json.load(file)
                        output_text = data[-1][-1] # we output this as the bot
                    await ctx.reply(f"{output_text}")                 

    except Exception as e:
        print(f"Error: {e}")
        await ctx.reply(f"{e} cc <@811235357663297546> (falcon error)")
#---------------------------------------------------------------------------------------------------------------------------- 
'''
@bot.event 
async def on_message(message):
    try:    
        if message.channel.id == 1116089829147557999:



    except Exception as e:
        print(f"Error: {e}")
        await ctx.reply(f"{e} cc <@811235357663297546> (falcon error)")    

'''
#---------------------------------------------------------------------------------------------------------------------------- 


        
        
def run_bot():
    bot.run(DISCORD_TOKEN)

threading.Thread(target=run_bot).start()

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
#demo.queue(concurrency_count=10)
demo.queue(concurrency_count=20)
demo.launch()
