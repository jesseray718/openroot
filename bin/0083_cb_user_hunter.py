#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
#   CB-USERHUNTER v1.0 — Ciberbrigada OSINT Suite
#   Búsqueda de usernames en 80+ plataformas simultáneamente
#   Uso exclusivo para fines legales y educativos
# ═══════════════════════════════════════════════════════════════════════════════

import sys
import time
import os
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    os.system("pip install requests colorama --break-system-packages -q")
    import requests
    from colorama import init, Fore, Style
    init(autoreset=True)

# ── Colores ───────────────────────────────────────────────────────────────────
C  = Fore.CYAN
Y  = Fore.YELLOW
G  = Fore.GREEN
R  = Fore.RED
W  = Fore.WHITE
D  = Fore.WHITE + Style.DIM
M  = Fore.MAGENTA
B  = Style.BRIGHT
RS = Style.RESET_ALL

HEADERS_DEFAULT = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

HEADERS_API = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest",
}

# ══════════════════════════════════════════════════════════════════════════════
# BASE DE PLATAFORMAS — 80+ sitios con detección avanzada
# detect modes:
#   status_200         — solo verifica HTTP 200
#   not_contains:TEXT  — 200 y NO contiene ese texto (perfil existe)
#   contains:TEXT      — 200 y SÍ contiene ese texto (perfil existe)
#   api_json:KEY       — llama API JSON y verifica que KEY exista
#   status_200_strict  — 200 sin redirección a login
# ══════════════════════════════════════════════════════════════════════════════
PLATFORMS = [
    # ── Redes Sociales ────────────────────────────────────────────────────────
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/{}/?__a=1&__d=dis",
        "detect": "not_contains:\"user\":null",
        "headers": {**HEADERS_API, "X-IG-App-ID": "936619743392459"},
        "fallback_url": "https://www.instagram.com/{}/",
        "fallback_detect": "not_contains:Page Not Found",
    },
    {
        "name": "Twitter/X",
        "url": "https://x.com/{}",
        "detect": "not_contains:This account doesn't exist",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "TikTok",
        "url": "https://www.tiktok.com/@{}",
        "detect": "not_contains:Couldn't find this account",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "YouTube",
        "url": "https://www.youtube.com/@{}",
        "detect": "not_contains:channel/about",
        "headers": HEADERS_DEFAULT,
        "alt_detect": "contains:channelId",
    },
    {
        "name": "Facebook",
        "url": "https://www.facebook.com/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com/in/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Pinterest",
        "url": "https://www.pinterest.com/{}/",
        "detect": "not_contains:User not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Snapchat",
        "url": "https://www.snapchat.com/add/{}",
        "detect": "not_contains:Sorry, we couldn't find",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Tumblr",
        "url": "https://{}.tumblr.com",
        "detect": "not_contains:There's nothing here",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{}/about.json",
        "detect": "contains:\"name\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/json"},
    },
    {
        "name": "Twitch",
        "url": "https://www.twitch.tv/{}",
        "detect": "not_contains:Sorry. Unless you've got a time machine",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "VK",
        "url": "https://vk.com/{}",
        "detect": "not_contains:This page does not exist",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Mastodon",
        "url": "https://mastodon.social/@{}",
        "detect": "not_contains:The page you are looking for",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Threads",
        "url": "https://www.threads.net/@{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Bluesky",
        "url": "https://bsky.app/profile/{}",
        "detect": "not_contains:Profile not found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Desarrollo / Tech ─────────────────────────────────────────────────────
    {
        "name": "GitHub",
        "url": "https://api.github.com/users/{}",
        "detect": "contains:\"login\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/vnd.github.v3+json"},
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{}",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Bitbucket",
        "url": "https://bitbucket.org/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "HackerNews",
        "url": "https://hacker-news.firebaseio.com/v0/user/{}.json",
        "detect": "contains:\"id\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Dev.to",
        "url": "https://dev.to/api/users/by_username?url={}",
        "detect": "contains:\"username\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/json"},
    },
    {
        "name": "Replit",
        "url": "https://replit.com/@{}",
        "detect": "not_contains:page doesn't exist",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Kaggle",
        "url": "https://www.kaggle.com/{}",
        "detect": "not_contains:No user found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Codepen",
        "url": "https://codepen.io/{}",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Pastebin",
        "url": "https://pastebin.com/u/{}",
        "detect": "not_contains:Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "NPM",
        "url": "https://registry.npmjs.org/~{}",
        "detect": "status_200",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "PyPI",
        "url": "https://pypi.org/user/{}/",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Dockerhub",
        "url": "https://hub.docker.com/v2/users/{}",
        "detect": "contains:\"username\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/json"},
    },
    {
        "name": "StackOverflow",
        "url": "https://api.stackexchange.com/2.3/users?inname={}&site=stackoverflow",
        "detect": "contains:\"items\"",
        "headers": HEADERS_DEFAULT,
    },

    # ── Gaming ────────────────────────────────────────────────────────────────
    {
        "name": "Steam",
        "url": "https://steamcommunity.com/id/{}",
        "detect": "not_contains:The specified profile could not be found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "PSN",
        "url": "https://psnprofiles.com/{}",
        "detect": "not_contains:User Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Roblox",
        "url": "https://api.roblox.com/users/get-by-username?username={}",
        "detect": "contains:\"Id\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Chess.com",
        "url": "https://api.chess.com/pub/player/{}",
        "detect": "contains:\"username\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Minecraft",
        "url": "https://api.mojang.com/users/profiles/minecraft/{}",
        "detect": "contains:\"name\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Speedrun",
        "url": "https://www.speedrun.com/api/v1/users/{}",
        "detect": "contains:\"data\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Fortnite",
        "url": "https://fortnitetracker.com/profile/all/{}",
        "detect": "not_contains:We could not find",
        "headers": HEADERS_DEFAULT,
    },

    # ── Música / Creadores ────────────────────────────────────────────────────
    {
        "name": "SoundCloud",
        "url": "https://soundcloud.com/{}",
        "detect": "not_contains:We can't find that user",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Bandcamp",
        "url": "https://{}.bandcamp.com",
        "detect": "not_contains:Sorry, that something",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Last.fm",
        "url": "https://www.last.fm/user/{}",
        "detect": "not_contains:User not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Mixcloud",
        "url": "https://api.mixcloud.com/{}/",
        "detect": "contains:\"username\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Spotify",
        "url": "https://open.spotify.com/user/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Fotos / Diseño ────────────────────────────────────────────────────────
    {
        "name": "Flickr",
        "url": "https://www.flickr.com/people/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Behance",
        "url": "https://www.behance.net/{}",
        "detect": "not_contains:page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Dribbble",
        "url": "https://dribbble.com/{}",
        "detect": "not_contains:Whoops",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "DeviantArt",
        "url": "https://www.deviantart.com/{}",
        "detect": "not_contains:page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "ArtStation",
        "url": "https://www.artstation.com/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Foros / Comunidades ───────────────────────────────────────────────────
    {
        "name": "Quora",
        "url": "https://www.quora.com/profile/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Medium",
        "url": "https://medium.com/@{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Substack",
        "url": "https://substack.com/@{}",
        "detect": "not_contains:not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Wordpress",
        "url": "https://{}.wordpress.com",
        "detect": "not_contains:doesn't exist",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Goodreads",
        "url": "https://www.goodreads.com/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Letterboxd",
        "url": "https://letterboxd.com/{}",
        "detect": "not_contains:Sorry, we can't find",
        "headers": HEADERS_DEFAULT,
    },

    # ── Ciberseguridad ────────────────────────────────────────────────────────
    {
        "name": "HackTheBox",
        "url": "https://www.hackthebox.com/api/v4/user/profile/basic/{}",
        "detect": "contains:\"profile\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "TryHackMe",
        "url": "https://tryhackme.com/api/user/exist/{}",
        "detect": "contains:true",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "BugCrowd",
        "url": "https://bugcrowd.com/{}",
        "detect": "not_contains:The page you were looking for",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "HackerOne",
        "url": "https://hackerone.com/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Crypto / Finanzas ─────────────────────────────────────────────────────
    {
        "name": "Keybase",
        "url": "https://keybase.io/_/api/1.0/user/lookup.json?username={}",
        "detect": "contains:\"them\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "CoinMarketCap",
        "url": "https://coinmarketcap.com/community/profile/{}/",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Trabajo / Profesional ─────────────────────────────────────────────────
    {
        "name": "ProductHunt",
        "url": "https://www.producthunt.com/@{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Fiverr",
        "url": "https://www.fiverr.com/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Streaming / Video ─────────────────────────────────────────────────────
    {
        "name": "Vimeo",
        "url": "https://vimeo.com/{}",
        "detect": "not_contains:Sorry, we couldn't find",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Rumble",
        "url": "https://rumble.com/user/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Kick",
        "url": "https://kick.com/{}",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },

    # ── Otros ─────────────────────────────────────────────────────────────────
    {
        "name": "Telegram",
        "url": "https://t.me/{}",
        "detect": "not_contains:If you have Telegram",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Gravatar",
        "url": "https://en.gravatar.com/{}",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "About.me",
        "url": "https://about.me/{}",
        "detect": "not_contains:page doesn't exist",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Linktree",
        "url": "https://linktr.ee/{}",
        "detect": "not_contains:Sorry",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Patreon",
        "url": "https://www.patreon.com/{}",
        "detect": "not_contains:page you're looking for",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Ko-fi",
        "url": "https://ko-fi.com/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Strava",
        "url": "https://www.strava.com/athletes/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Cashapp",
        "url": "https://cash.app/${}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
]

# ══════════════════════════════════════════════════════════════════════════════
# BANNER
# ══════════════════════════════════════════════════════════════════════════════
def banner():
    os.system("cls" if os.name == "nt" else "clear")

    CYAN = '\033[96m'
    ORAN = '\033[38;5;208m'
    DIM  = '\033[2m\033[37m'
    BOLD = '\033[1m'
    YEL  = '\033[33m'
    RST  = '\033[0m'

    logo = [
        "              ...::::...               ",
        "              ..:::+: ....             ",
        "        .:...:::::::.  ..:....... ..   ",
        "       :+  .:::::::    ::::::::::.     ",
        "      .+. .::::::::    +::::::::++::   ",
        "    . ::.:+:.          :::       ::+:  ",
        "   .: :::+.            +:+       .+++  ",
        "   .+ .+::             +:+.    .:+++.  ",
        "    +: :+.             ++++++++++++:   ",
        "     +:.:+             +++:......:+++: ",
        "   :. :++++.           +++         ++%:",
        "    ::  .::+++:::::    +++        .++%:",
        "     .:::....::++++   .+++:.....::+++: ",
        "   ... ..:+::+::+++:. ::++++++++++:.   ",
        "     :+:. :+.:+:.:++::......  ...      ",
        "       :+: :+..++...::::.......         ",
        "         .. :+:..:+:.........           ",
    ]

    print()
    for line in logo:
        mid = len(line) // 2
        print(f"       {CYAN}{BOLD}{line[:mid]}{ORAN}{line[mid:]}{RST}")

    print(f"                          {DIM}by: Fgunther{RST}")
    print()
    print(f"  {CYAN}{BOLD}Ciber{ORAN}brigada{RST} {CYAN}OSINT Suite{RST}  {DIM}─────────────────────{RST}")
    print(f"  {BOLD}╔══════════════════════════════════════════╗{RST}")
    print(f"  {BOLD}║  👤  CB-USERHUNTER  v1.0                ║{RST}")
    print(f"  {BOLD}║  Username OSINT — 80+ plataformas       ║{RST}")
    print(f"  {BOLD}╚══════════════════════════════════════════╝{RST}")
    print(f"  {DIM}[ ciberbrigada.com ]  [ OSINT Suite ]{RST}")
    print(f"  {YEL}⚠  Solo para uso legal, ético y educativo  ⚠{RST}")
    print()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def separador(titulo=""):
    if titulo:
        pad = (58 - len(titulo)) // 2
        print(f"\n{C}{'─' * pad} {B}{titulo}{RS}{C} {'─' * pad}{RS}")
    else:
        print(f"{D}{'─' * 60}{RS}")

def ok(msg):   print(f"  {G}{B}[✓]{RS} {W}{msg}{RS}")
def warn(msg): print(f"  {Y}[!]{RS} {Y}{msg}{RS}")
def fail(msg): print(f"  {R}[✗]{RS} {D}{msg}{RS}")
def info(msg): print(f"  {C}[i]{RS} {W}{msg}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# CHECKER — verifica una plataforma con detección avanzada
# ══════════════════════════════════════════════════════════════════════════════
def check_platform(platform, username):
    url     = platform["url"].format(username)
    detect  = platform.get("detect", "status_200")
    headers = platform.get("headers", HEADERS_DEFAULT)

    try:
        r = requests.get(url, headers=headers, timeout=10,
                         allow_redirects=True)

        body = r.text.lower() if r.text else ""

        # status_200 simple
        if detect == "status_200":
            if r.status_code == 200:
                return {"name": platform["name"], "url": platform.get("display_url", url).format(username), "status": r.status_code}
            return None

        # contains:TEXT — el perfil existe si el texto está presente
        if detect.startswith("contains:"):
            needle = detect.split("contains:")[1].lower()
            if r.status_code == 200 and needle in body:
                return {"name": platform["name"], "url": platform.get("display_url", url).format(username), "status": r.status_code}
            return None

        # not_contains:TEXT — el perfil existe si el texto NO está presente
        if detect.startswith("not_contains:"):
            needle = detect.split("not_contains:")[1].lower()
            if r.status_code == 200 and needle not in body:
                # Verificar que no sea una página genérica vacía
                if len(r.text) > 200:
                    return {"name": platform["name"], "url": platform.get("display_url", url).format(username), "status": r.status_code}
            # Intentar fallback si existe
            if "fallback_url" in platform:
                fb_url    = platform["fallback_url"].format(username)
                fb_detect = platform.get("fallback_detect", "status_200")
                try:
                    r2   = requests.get(fb_url, headers=HEADERS_DEFAULT, timeout=8, allow_redirects=True)
                    body2 = r2.text.lower()
                    if fb_detect.startswith("not_contains:"):
                        needle2 = fb_detect.split("not_contains:")[1].lower()
                        if r2.status_code == 200 and needle2 not in body2 and len(r2.text) > 200:
                            return {"name": platform["name"], "url": fb_url, "status": r2.status_code}
                except Exception:
                    pass
            return None

        return None

    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════════════════════
# BÚSQUEDA PRINCIPAL — multihilo
# ══════════════════════════════════════════════════════════════════════════════
def search_username(username):
    separador(f"BUSCANDO: {username}")
    print(f"\n  {C}Analizando {len(PLATFORMS)} plataformas en paralelo...{RS}")
    print(f"  {D}Esto puede tardar 15-30 segundos{RS}\n")

    found     = []
    total     = len(PLATFORMS)
    completed = 0

    # Barra de progreso simple
    def progress(n, total):
        pct  = int(n / total * 40)
        bar  = "█" * pct + "░" * (40 - pct)
        print(f"\r  {C}[{bar}]{RS} {W}{n}/{total}{RS}", end="", flush=True)

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_platform, p, username): p for p in PLATFORMS}
        for future in as_completed(futures):
            completed += 1
            progress(completed, total)
            result = future.result()
            if result:
                found.append(result)

    print(f"\n")
    return found

# ══════════════════════════════════════════════════════════════════════════════
# MOSTRAR RESULTADOS
# ══════════════════════════════════════════════════════════════════════════════
def show_results(username, found):
    separador(f"RESULTADOS — @{username}")

    if not found:
        warn(f"Username '{username}' no encontrado en ninguna plataforma")
        return

    ok(f"Encontrado en {G}{B}{len(found)}{RS} {W}plataformas:")
    print()

    # Agrupar por categoría
    categorias = {
        "Redes Sociales":    ["Instagram","Twitter/X","TikTok","Facebook","LinkedIn","Pinterest","Snapchat","Tumblr","Reddit","Threads","Bluesky","VK","Mastodon","Clubhouse"],
        "Desarrollo / Tech": ["GitHub","GitLab","Bitbucket","HackerNews","StackOverflow","Dev.to","Replit","Kaggle","Codepen","Pastebin","NPM","PyPI","Dockerhub"],
        "Gaming":            ["Steam","Xbox","PSN","Roblox","Chess.com","Minecraft","Fortnite","Speedrun"],
        "Música / Creadores":["Spotify","SoundCloud","Bandcamp","Last.fm","Mixcloud","YouTube","Twitch","Kick","Vimeo","Dailymotion","Rumble","Patreon","Ko-fi"],
        "Fotos / Diseño":    ["Flickr","500px","Behance","Dribbble","DeviantArt","ArtStation"],
        "Ciberseguridad":    ["HackTheBox","TryHackMe","BugCrowd","HackerOne","Shodan"],
        "Crypto / Finanzas": ["Keybase","Etherscan","CoinMarketCap","BitcoinTalk","Cashapp"],
        "Trabajo":           ["AngelList","ProductHunt","Fiverr","Upwork"],
        "Comunidades":       ["Quora","Medium","Substack","Wordpress","Blogspot","WikiPedia","Goodreads","Letterboxd","Strava"],
        "Otros":             ["Telegram","Signal","Gravatar","About.me","Linktree","Carrd","OnlyFans"],
    }

    found_names = {f["name"]: f for f in found}
    printed = set()

    for cat, plats in categorias.items():
        cat_found = [found_names[p] for p in plats if p in found_names]
        if cat_found:
            print(f"  {C}{B}▸ {cat}{RS}")
            for f in cat_found:
                print(f"    {G}[✓]{RS} {W}{B}{f['name']:<18}{RS} {D}{f['url']}{RS}")
                printed.add(f["name"])
            print()

    # Cualquier resultado que no cayó en categoría
    extras = [f for f in found if f["name"] not in printed]
    if extras:
        print(f"  {C}{B}▸ Otros{RS}")
        for f in extras:
            print(f"    {G}[✓]{RS} {W}{B}{f['name']:<18}{RS} {D}{f['url']}{RS}")
        print()

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE DORKS
# ══════════════════════════════════════════════════════════════════════════════
def google_dorks(username):
    separador("GOOGLE DORKS")
    dorks = [
        (f'"{username}"',                              "Username exacto"),
        (f'"@{username}"',                             "Mención con @"),
        (f'"{username}" site:linkedin.com',            "LinkedIn"),
        (f'"{username}" site:github.com',              "GitHub"),
        (f'"{username}" filetype:pdf',                 "En PDFs"),
        (f'"{username}" email OR mail OR correo',      "Email asociado"),
        (f'"{username}" password OR contraseña OR leak',"En leaks"),
        (f'intext:"{username}" site:pastebin.com',     "Pastebin"),
        (f'"{username}" CV OR curriculum OR resume',   "Curriculums"),
        (f'"{username}" phone OR celular OR teléfono', "Teléfono asociado"),
    ]
    for dork, desc in dorks:
        encoded = urllib.parse.quote(dork)
        url = f"https://www.google.com/search?q={encoded}"
        print(f"  {C}▸ {W}{desc:<30}{RS} {D}{url[:70]}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ══════════════════════════════════════════════════════════════════════════════
def resumen_final(username, found, elapsed):
    separador("RESUMEN")
    print(f"\n  {C}{B}Target:{RS}      {W}{B}@{username}{RS}")
    print(f"  {C}{B}Plataformas:{RS} {W}{len(PLATFORMS)} analizadas{RS}")
    print(f"  {C}{B}Encontrado:{RS}  {G}{B}{len(found)}{RS} {W}perfiles{RS}")
    print(f"  {C}{B}Tiempo:{RS}      {W}{elapsed:.1f}s{RS}")
    print()
    if found:
        print(f"  {D}Perfiles encontrados:{RS}")
        for f in found:
            print(f"  {G}  ✓{RS} {W}{f['name']}{RS}")
    print(f"\n  {D}Análisis completado — Ciberbrigada OSINT Suite v1.0{RS}\n")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    banner()

    print(f"  {W}Ingresá el username a buscar (sin @) o 'salir' para terminar:{RS}\n")

    while True:
        try:
            username = input(f"  {C}▸ Username:{RS} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {Y}Saliendo... Hasta pronto.{RS}\n")
            sys.exit(0)

        if username.lower() in ("salir", "exit", "quit", "q"):
            print(f"\n  {Y}Saliendo... Hasta pronto.{RS}\n")
            sys.exit(0)

        # Limpiar @ si lo puso
        username = username.lstrip("@").strip()

        if not username or len(username) < 2:
            warn("Ingresá un username válido (mínimo 2 caracteres)")
            continue

        if not re.match(r'^[a-zA-Z0-9._\-]+$', username):
            warn("El username solo puede contener letras, números, puntos, guiones y guiones bajos")
            continue

        start   = time.time()
        found   = search_username(username)
        elapsed = time.time() - start

        show_results(username, found)
        google_dorks(username)
        resumen_final(username, found, elapsed)

        separador()
        print(f"\n  {D}¿Buscar otro username? (Enter para continuar / 'salir' para terminar){RS}")
        try:
            again = input(f"  {C}▸{RS} ").strip().lower()
            if again in ("salir", "exit", "quit", "q"):
                print(f"\n  {Y}Saliendo... Hasta pronto.{RS}\n")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {Y}Saliendo...{RS}\n")
            sys.exit(0)

        banner()

if __name__ == "__main__":
    main()
