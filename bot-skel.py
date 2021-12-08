	#!./.venv/bin/python

#Copyright 2021

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.
    #
    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.
    #
    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <https://www.gnu.org/licenses/>.



import discord      # base discord module
import code         # code.interact
import os           # environment variables
import inspect      # call stack inspection
import random       # dumb random number generator
import argparse


from discord.ext import commands    # Bot class and utils

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
        'debug'   : ('\033[34m', '-'),
        'info'    : ('\033[32m', '*'),
        'warning' : ('\033[33m', '?'),
        'error'   : ('\033[31m', '!'),
    }

    # internal ansi codes
    _extra_ansi = {
        'critical' : '\033[35m',
        'bold'     : '\033[1m',
        'unbold'   : '\033[2m',
        'clear'    : '\033[0m',
    }

    # get information about call site
    caller = inspect.stack()[1]

    # input sanity check
    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
            (_extra_ansi['critical'], _extra_ansi['bold'],
             caller.function, caller.lineno,
             _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return

    # print the damn message already
    print('%s%s[%s] %s:%d %s%s%s' % \
        (_extra_ansi['bold'], *dsp_sel[level],
         caller.function, caller.lineno,
         _extra_ansi['unbold'], msg, _extra_ansi['clear']))

################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################

# bot instantiation
bot = commands.Bot(command_prefix='!')

# on_ready - called after connection to server is established
@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')

# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
    # filter out our own messages
    if msg.author == bot.user:
        return

    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')

    # overriding the default on_message handler blocks commands from executing
    # manually call the bot's command processor on given message
    await bot.process_commands(msg)

#code.interact(local=dict(globals(), **locals()))

# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    # argument sanity check
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')

    await ctx.send(random.randint(1, max_val))

# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))

# play a song in voice channel
@bot.command(aliases=['play'])
async def joinvc(ctx):
    voice_channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client:
        if not voice_client.is_connected():
            await voice_channel.connect()
            voice_client.play(discord.FFmpegPCMAudio(source='file.mp3'))
    else:
        await voice_channel.connect()
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice_client.play(discord.FFmpegPCMAudio(source='file.mp3'))


# leave command

@bot.command()
async def leave(context):
        await context.voice_client.disconnect()


@commands.Cog.listener("on_voice_state_update")
async def voiceStateUpdate(self, member, before, after):
    voiceClient = discord.utils.get(self.bot.voice_clients, guild = member.guild) # Bot "voice_client"

    if voiceClient.channel != None:
      if len(voiceClient.channel.members) == 1:
        await voiceClient.disconnect()


@bot.command()
async def parse(ctx, x: int, y: int):
	parser = argparse.ArgumentParser(description="calculate X to the power of Y")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-v", "--verbose", action="store_true")
	group.add_argument("-q", "--quiet", action="store_true")
	parser.add_argument("x", type=int, help="the base")
	parser.add_argument("y", type=int, help="the exponent")
	args = parser.parse_args()
	answer = args.x**args.y

	if args.quiet:
            await ctx.send(answer)
	elif args.verbose:
            await ctx.send("{} to the power {} equals {}".format(args.x, args.y, answer))
	else:
            await ctx.send("{}^{} == {}".format(args.x, args.y, answer))

################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################

if __name__ == '__main__':
    # check that token exists in environment
    if 'BOT_TOKEN' not in os.environ:
        log_msg('save your token in the BOT_TOKEN env variable!', 'error')
        exit(-1)

    # launch bot (blocking operation)
    bot.run(os.environ['BOT_TOKEN'])
