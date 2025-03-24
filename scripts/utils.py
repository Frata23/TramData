import json
import datetime
from interactions import Embed, SlashContext

def get_model_from_id(id):
    if id > 60:
        return 302
    else:
        return 301

def load_data():
    with open("bot_entries.json", "r", encoding="utf-8") as json_file:
        output = json.load(json_file)
    
    return output["datas"]


def get_total_numbers_of_entries():
    with open("bot_entries.json", "r", encoding="utf-8") as json_file:
        output = json.load(json_file)
    
    return output["total"]




def get_models_stats():
    datas = load_data()

    models = dict()
    for i in datas:
        model=i['model']

        if model in models:
            models[model] +=1
        else:
            models[model] = 1 
        
    return models
    
def get_ids_stats():
    datas = load_data()

    ids = dict()
    for i in datas:
        id = i['id']

        if id in ids:
            ids[id] +=1
        else:
            ids[id] = 1

    sorted_data = dict(sorted(ids.items(), key=lambda item: item[1], reverse=True))
    return sorted_data

def get_lines_stats():
    datas = load_data()

    lines = dict()
    for i in datas:
        line = i['line']
        if line in lines:
            lines[line] +=1
        else:
            lines[line] = 1
    return lines

def get_personnal_stats(*author_ids : int):
    datas = load_data()
    filtered_data = []
    for i in datas:
        if int(i['user']['id']) in author_ids:
            filtered_data.append(i)

    lines = dict()
    ids = dict()
    models = dict()
    for i in filtered_data:
        line = i['line']
        id = i['id']
        model=i['model']

        if line in lines:
            lines[line] +=1
        else:
            lines[line] = 1
        
        if id in ids:
            ids[id] +=1
        else:
            ids[id] = 1

        if model in models:
            models[model] +=1
        else:
            models[model] = 1 
        

    result = {
        "total" : len(filtered_data),
        "users_fetched" : {
            "number":len(author_ids),
            "ids":author_ids,
        },
        "ids" : ids,
        "lines" : lines,
        "models" : models,
    }

    return result


def generate_empty_embed(ctx: SlashContext, title : str, description : str = "", footer_text : str = "") -> Embed:
    embed = Embed(
        title=title,
        description=description,
        color=0x3498db,
        timestamp= datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )

    footer_prefix = f"Commande lancée par {ctx.author}"
    embed.set_footer(
        text=footer_prefix+" "+footer_text,
        icon_url=ctx.author.avatar.url
    )

    return embed