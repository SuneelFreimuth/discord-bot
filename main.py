import random
from collections import defaultdict
from discord.ext import commands
from discord import File as DiscFile
import matplotlib.pyplot as plt

bot = commands.Bot(command_prefix="$")


# Use my help command, not discord.py's.
bot.remove_command('help')

help_texts = {
    'help': ('$help [command]', 'Display this help message or get help on a specific command.'),
    'ping': ('$ping', 'pong'),
    'insult': ('$insult', 'Self-explanatory.'),
    'contributions': ('$contributions', 'Count the number of times each user has sent a message in this channel and represent the data as a histogram.')
}

full_help_text = '**Commands:**\n'
for format, description in help_texts.values():
    full_help_text += f'  `{format}`: {description}\n'

@bot.command()
async def help(ctx, command=None):
    if command:
        command = command.lstrip('$')
        if command in help_texts:
            msg = f'`${command}`: {help_texts[command]}'
        else:
            msg = full_help_text
    else:
        msg = full_help_text
    await ctx.send(msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


f = open('adjectives.txt')
adjectives = [l.strip() for l in f.readlines()]
f.close()

f = open('animals.txt')
animals = [l.strip().lower() for l in f.readlines()]
f.close()

@bot.command()
async def insult(ctx):
    adj, animal = random.choice(adjectives), random.choice(animals)
    await ctx.send(f'Shut the fuck up, you {adj} {animal}')


def draw_text_bar_graph(data: [(str, int)]) -> str:
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

def draw_bar_graph(data: dict) -> 'Plot':
    names, counts = [], []
    # Sort by count, descending.
    for name, count in sorted(data.items(), key=lambda pair: -pair[1]):
        names.append(name)
        counts.append(count)
    fig, ax = plt.subplots()
    rects = ax.bar(names, counts, width=0.2)
    # Annotate bars with labels manually.
    for rect, count in zip(rects, counts):
        ax.text(
            rect.get_x() + rect.get_width()/2,
            rect.get_height() + 1,
            str(count),
            ha='center'
        )
    fig.savefig('./bar_plot.png')
    return './bar_plot.png'


@bot.command()
async def contributions(ctx):
    counts = defaultdict(int)
    async for message in ctx.channel.history(limit=1000):
        counts[message.author.name] += 1
    file_path = draw_bar_graph(counts)
    await ctx.send(file=DiscFile(file_path))


@bot.listen
async def on_ready():
    print('Ready!')

f = open('bot_token.txt')
token = f.read().strip()
f.close()
bot.run(token)
