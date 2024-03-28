import websockets
from bs4 import BeautifulSoup
import discord


async def handler(websocket):
    try:
        moves = []
        async for message in websocket:
            if message.startswith("|pm"):
                response = message.split("|")[4][5:]
                parsed_moves = parse_html(response)
                return parsed_moves
            else:
                print("Received unexpected message:", message)

        return moves
    except Exception as e:
        print("Error handling PS! message:", e)
        return None


async def request_data(command: str):
    try:
        async with websockets.connect("ws://sim.smogon.com:8000/showdown/websocket") as websocket:
            print("PS! connection established")
            await websocket.send("|/" + command)
            return await handler(websocket)
    except Exception as e:
        print("Error during PS! connection:", e)
        return None


def parse_html(response: str) -> list[str]:
    try:
        soup = BeautifulSoup(response, features="html.parser")
        move_tags = soup.find_all('a')

        moves = []
        for tag in move_tags:
            move_name = tag.get_text(strip=True)
            moves.append(move_name)

        print("Parsed moves:", moves)
        return moves
    except Exception as e:
        print("Error parsing HTML:", e)
        return []


async def search_moves(pokemon_list):
    results = {}

    for pokemon in pokemon_list:
        moves = await request_data(f"nms {pokemon}, all")
        results[pokemon] = moves

    print(results)
    return results


async def format_embed(results):
    embed = discord.Embed(title="Move Search Results", color=discord.Color.lighter_gray())
    for pokemon, moves in results.items():
        if moves:
            moves_str = ', '.join(moves)
            embed.add_field(name=pokemon, value=moves_str, inline=False)
        else:
            embed.add_field(name=pokemon, value="No moves found", inline=False)
    return embed
