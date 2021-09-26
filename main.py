import random
import re
import sys
from collections import defaultdict, OrderedDict
from argparse import ArgumentParser

import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import asyncio


GREEN = '\033[32m'
CLEAR = '\033[0m'
def success(*args):
    print(GREEN + '✓', *args, CLEAR)


parser = ArgumentParser('Suneel Freimuth\'s Discord bot.')
parser.add_argument('--token', type=str, help='Your bot token. Either pass it with this argument or place it in bot_token.txt.')
args = parser.parse_args()

token = args.token
if token:
    success('Bot token provided as command line argument.')
else:
    try:
        f = open('bot_token.txt')
        token = f.read().strip()
        f.close()
        success('Bot token loaded from bot_token.txt')
    except FileNotFoundError:
        print('No bot_token.txt found. Either place your bot token in a file called bot_token.txt or run with --token=<token>', file=sys.stderr)
        exit(1)


bot = commands.Bot(command_prefix="$")


# Use my help command, not discord.py's.
bot.remove_command('help')

help_texts = OrderedDict(
    help=('$help [command]', 'Display a list of commands or get help on a specific command.'),
    ping=('$ping', 'pong'),
    meow=('$meow', 'meow'),
    contributions=('$contributions', 'Count the number of times each user has sent a message in this channel and display the data as a bar graph.')
)

full_help_text = '**Commands:**\n'
for format, description in help_texts.values():
    full_help_text += f'  `{format}`: {description}\n'

@bot.command()
async def help(ctx, command=None):
    if command:
        command = command.lstrip('$')
        if command in help_texts:
            format, description = help_texts[command]
            msg = f'`{format}`: {description}'
        else:
            msg = full_help_text
    else:
        msg = full_help_text
    await ctx.send(msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


meow_pattern = re.compile(r'm[aeiou]([aeiu]|(?=[^aeiou]))')

@bot.command()
async def meow(ctx):
    history = ctx.channel.history(limit=2)
    _ = await history.next()
    # Message before the command invocation.
    msg = await history.next()
    response = meow_pattern.sub('meow', msg.content)
    await ctx.send(response)




# Unused and messy but useful.
def draw_textual_bar_graph(data: [(str, int)]) -> str:
    # Sort by descending magnitude.
    categories = map(lambda pair: pair[0], data)
    counts = map(lambda pair: pair[1], data)
    longest_cat_name = max(categories, key=len)
    longest_count = max(counts, key=lambda c: len(str(c)))

    data = sorted(data, key=lambda pair: -pair[1])
    agg = ""
    for cat, num in data:
        pad0 = ' ' * (len(longest_cat_name) - len(cat) + 1)
        pad1 = ' ' * (len(str(longest_count)) - len(str(num)) + 1)
        agg += f'{cat}{pad0}[{num}]{pad1}{"#"*num}\n'
    return '```\n' + agg + '```'

def constrain(v, min, max):
    if v < min:
        return min
    if v > max:
        return max
    return v

def draw_bar_graph(data: dict) -> 'Plot':
    descending_count = lambda pair: -pair[1]
    names, counts = zip(*sorted(data.items(), key=descending_count))

    def colorize(count):
        # The chance anyone will hit 750 out of 1000 messages is slim.
        norm = count / 750
        return tuple(constrain(v, 0.0, 1.0) for v in (
            (norm*2, 1.0, 0.0)
            if norm < 0.5
            else (1.0, 2.0 - 2*norm, 0.0)
        ))

    fig, ax = plt.subplots()
    rects = ax.barh(range(len(counts)), counts, height=0.5, align='center',
        color=[colorize(c) for c in counts])
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    plt.tight_layout()

    fig.savefig('./bar_plot.png')
    return './bar_plot.png'

@bot.command()
async def contributions(ctx):
    async with ctx.channel.typing():
        counts = defaultdict(int)
        async for message in ctx.channel.history(limit=1000):
            counts[message.author.name] += 1
        file_path = draw_bar_graph(counts)
        await ctx.send(file=discord.File(file_path))


@bot.listen()
async def on_ready():
    success('Ready!')

@bot.listen()
async def on_command_error(ctx, err):
    if type(err) == commands.CommandNotFound:
        await ctx.send(full_help_text)
    else:
        print(err, file=sys.stderr)

print('  Starting bot...')
bot.run(token)

