from interactions import Client, Intents, SlashContext, OptionType, SlashCommandChoice, Embed, listen, slash_command, \
    slash_option, Button, ButtonStyle, ActionRow
from dotenv import load_dotenv
from interactions.ext.paginators import Paginator

from logger import logger
import logger as loggerClass
import utils as utils
import datetime
import json
import os

load_dotenv()

if os.getenv('MODE')=="test":
    api_key = os.getenv('TOKEN_TEST')
elif os.getenv('MODE')=="run":
    api_key = os.getenv('TOKEN')

LOG_FILE = os.path.abspath(os.path.join(os.getcwd(), "bot_entries.json"))

bot = Client(intents=Intents.DEFAULT)

@listen()  
async def on_ready():
    logger.info("Bot is running")
    print("Ready and running")
    print(f"This bot is owned by {bot.owner}")

@listen()
async def on_connect():
    logger.info("Bot is connected")
    print("Bot connected")


@listen()
async def on_disconnect():
    logger.info("Bot is disconnected")
    print("Bot disconnected")


@slash_command(name="test", description="Commande simple pour voir si le bot repond")
async def test(ctx):
    loggerClass.log_command(ctx, f"Command 'test' executed")
    await ctx.send("Pour vous servir !")

# Create a slash command
@slash_command(name="add_entry", description="Permet d'ajouter un voyage en tram à la base de donnée")
@slash_option(
        name="numero",
        description="Numero de tram",
        required=True,
        opt_type=OptionType.INTEGER
    )
@slash_option(
        name="ligne",
        description="Ligne empruntée",
        required=True,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="A", value="A"),
            SlashCommandChoice(name="B", value="B")
        ]
    )
@slash_option(
        name="livery",
        description="Livery",
        required=False,
        opt_type=OptionType.STRING
    )
@slash_option(
        name="remarque",
        description="Controlleur/problème sur la ligne",
        required=False,
        opt_type=OptionType.STRING
    )
async def add_entry(ctx: SlashContext, numero : int, ligne, livery : str = "", remarque : str = "") -> None:
    loggerClass.log_command(ctx, f"Command 'add_entry' executed ({numero},{ligne},{livery},{remarque})")

    if not (30 <= numero <= 83):
        await ctx.send(f"❌ Le numero du tram doit être entre **30 et 83**. (Tu as inscrit: {numero})", ephemeral=True)
        return

    with open("bot_entries.json", "r", encoding="utf-8") as json_file:
        datas = json.load(json_file) 
    
    now_time = datetime.datetime.now()

    user_info = {
        "id": str(ctx.author.id),
        "username": ctx.author.username,  # Corrected this line
        "nick": ctx.author.nick if ctx.author.nick else None,
        "_guild_id": str(ctx.guild.id) if ctx.guild else None,
    }

    datas["total"] += 1
    datas["datas"] += [{
        "timestamp" : {
            "day" : now_time.strftime("%d"),
            "mounth" : now_time.strftime("%m"),
            "year" : now_time.strftime("%y"),
            "hour" : now_time.strftime("%H"),
            "minute" : now_time.strftime("%M"),
            "second" : now_time.strftime("%S")
        },
        "id": numero,
        "line": ligne,
        "model": utils.get_model_from_id(numero),
        "livery": livery,
        "remarque": remarque,
        "user" : user_info
    }]

    with open("bot_entries.json", "w", encoding="utf-8") as json_file:
        json.dump(datas, json_file, ensure_ascii=False, indent=4)

    await ctx.send(f"Voyage en tram numero {numero} sur la ligne {ligne} ajouté")


@slash_command(name="stats", description="Obtenez des stats sur les trams")
@slash_option(
        name="type",
        description="Type de stats",
        required=True,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Model", value="models"),
            SlashCommandChoice(name="Numeros", value="ids"),
            SlashCommandChoice(name="Lignes", value="lines"),
            SlashCommandChoice(name="Me", value="me"),
        ]
    )
async def stats(ctx: SlashContext, type : str) -> None:
    loggerClass.log_command(ctx, f"Command 'stats' executed ({type})")

    total = utils.get_total_numbers_of_entries()
    if total == 0:
        error_embed = utils.generate_empty_embed(ctx, "Aucune données", "Le bot ne possède aucune donnée à traiter. Ajouter des entrés (`/add_entry`) pour commencer a collecter des statistiques")
        await ctx.send(embed=error_embed)
        return

    res = f"**Total de voyage** : {total}"
    if type == "models":
        stats = utils.get_models_stats()
        for key, val in stats.items():
            res += f"\n**{key}** : {val} ({round(val/total*100,2)}%)"

        stat_embed = utils.generate_empty_embed(ctx, "Modèle de tram", "Statistiques sur les modèles de trams empruntés")
        stat_embed.add_field("Statistiques", res)

    elif type == "ids":
        stats = utils.get_ids_stats()

        #Le code suivant creer les lignes d'information, les regroupe par paquet de 'chunk_size', ici 10, puis genere autnat de pages que nécessaire dans le paginateur
        lines = []
        for key, val in stats.items():
            line = f"**{key}** : {val} ({round(val / total * 100, 2)}%)"
            lines.append(line)

        chunk_size = 10
        chunks = ["\n".join(lines[i:i + chunk_size]) for i in range(0, len(lines), chunk_size)]

        embeds = []
        page_number = 0
        for chunk in chunks:
            page_number += 1
            stat_embed = utils.generate_empty_embed(ctx, "Numéro de tram", "Statistiques sur les numéros de trams empruntés", f"\nPage {page_number}/{len(chunks)}")
            stat_embed.add_field("Statistiques", chunk)
            embeds.append(stat_embed)
        paginator = Paginator.create_from_embeds(bot, *embeds)

        await paginator.send(ctx)
        return

    elif type == "lines":
        stats = utils.get_lines_stats()
        for key, val in stats.items():
            res += f"\n**{key}** : {val} ({round(val/total*100,2)}%)"
        
        stat_embed = utils.generate_empty_embed(ctx, "Lignes de tram", "Statistiques sur les lignes de trams empruntés")
        stat_embed.add_field("Statistiques", res)
    elif type == "me":
        stats = utils.get_personnal_stats(ctx.author_id)
        total = stats['total']
        nb_user = stats['users_fetched']['number']
        ids = stats['ids']
        lines = stats['lines']
        models = stats['models']
        
        if total == 0:
            error_embed = utils.generate_empty_embed(ctx, "Aucune données", "Le bot ne possède aucune donnée à traiter. Ajouter des entrés (`/add_entry`) pour commencer a collecter des statistiques")
            await ctx.send(embed=error_embed)
            return

        res = f"**Total** : {total}"
        if nb_user > 1:
            res += f"\n**Nombre d'utilisateur** : {nb_user}"
            res += "\n**User** :\n"
            for i in stats['users_fetched']['ids']:
                res += f"{await ctx.bot.fetch_user(int(i))} "

        res_lines=""
        res_models=""
        for key, val in models.items():
            res_models += f"\n**{key}** : {val} ({round(val / total * 100, 2)}%)"
        for key, val in lines.items():
            res_lines += f"\n**{key}** : {val} ({round(val/total *100, 2)}%)"


        #Le code suivant creer les lignes d'information, les regroupe par paquet de 'chunk_size', ici 10, puis genere autnat de pages que nécessaire dans le paginateur
        nums_lines = []
        for key, val in ids.items():
            line = f"**{key}** : {val} ({round(val / total * 100, 2)}%)"
            nums_lines.append(line)

        chunk_size = 10
        chunks = ["\n".join(nums_lines[i:i + chunk_size]) for i in range(0, len(nums_lines), chunk_size)]

        embeds = []
        page_number = 0
        for chunk in chunks:
            page_number += 1
            stat_embed = utils.generate_empty_embed(ctx, "Statistiques personnelles",
                                                    "Vos statistiques",
                                                    f"\nPage {page_number}/{len(chunks)}")
            stat_embed.add_field("Statistiques", res)
            stat_embed.add_field("Modèles", res_models)
            stat_embed.add_field("Lines", res_lines)
            stat_embed.add_field("Numéros", chunk)
            embeds.append(stat_embed)

        paginator = Paginator.create_from_embeds(bot, *embeds)

        await paginator.send(ctx)
        return
    await ctx.send(embed=stat_embed)
    

@slash_command(name="about", description="A propos")
async def about(ctx: SlashContext) -> None:
    loggerClass.log_command(ctx, f"Command 'embed' executed")

    embed = utils.generate_empty_embed(ctx, "A propos", "Bienvenue sur TramData, votre compilateur de donnée de voyage en tram préféré !", "\nCe serait étrange d'en avoir un autre en tête tho")
    embed.add_field("Repository", "[TramData](https://github.com/Frata23/TramData)")

    await ctx.send(embed=embed)


bot.start(api_key)

# https://interactions-py.github.io/interactions.py/Guides/03%20Creating%20Commands/
# TODO edit an input / remove an input / ajout arrets / ajout climatisation / ajout arret selon la ligne avec les choices / ajout dir / ajout dir selon la ligne avec les choices