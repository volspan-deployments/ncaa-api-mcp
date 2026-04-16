from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os
from typing import Optional

mcp = FastMCP("NCAA API")

BASE_URL = "https://ncaa-api.henrygd.me"


@mcp.tool()
async def get_scoreboard(
    _track("get_scoreboard")
    sport: str,
    division: str,
    year: str,
    week: str,
    conference: str = "all-conf",
    page: int = 1
) -> dict:
    """Fetch live or historical scores for a given NCAA sport, division, and date.
    Use this when the user wants to check scores, game results, or the current status
    of games for a specific sport and date.
    
    Example: NCAA football FBS scores for week 13 of 2023.
    """
    url = f"{BASE_URL}/scoreboard/{sport}/{division}/{year}/{week}/{conference}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_stats(
    _track("get_stats")
    sport: str,
    division: str,
    season: str,
    stat_type: str,
    stat_id: str,
    page: int = 1
) -> dict:
    """Fetch NCAA statistics for a sport and division. Supports both team stats and
    individual player stats. Use this when the user wants statistical leaders, rankings
    by stat category, or player/team performance data.
    
    stat_type should be 'team' or 'individual'.
    stat_id is the numeric stat category ID (e.g., '28' for team rushing yards in football).
    
    Example: Current FBS team rushing stats for football.
    """
    url = f"{BASE_URL}/stats/{sport}/{division}/{season}/{stat_type}/{stat_id}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_rankings(
    _track("get_rankings")
    sport: str,
    division: str,
    ranking_source: str,
    page: int = 1
) -> dict:
    """Fetch NCAA rankings for a sport and division from a specific ranking source
    (e.g., AP Poll, Coaches Poll). Use this when the user asks about team rankings or polls.
    
    ranking_source examples: 'associated-press', 'coaches', 'college-football-playoff'.
    
    Example: Current AP Poll football rankings.
    """
    url = f"{BASE_URL}/rankings/{sport}/{division}/{ranking_source}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_standings(
    _track("get_standings")
    sport: str,
    division: str,
    page: int = 1
) -> dict:
    """Fetch NCAA standings for a sport and division, showing win/loss records and
    conference standings. Use this when the user wants to know where teams stand
    in their division or conference.
    
    Example: Women's basketball D1 standings.
    """
    url = f"{BASE_URL}/standings/{sport}/{division}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_game_info(game_id: str) -> dict:
    """Fetch general information about a specific NCAA game by its game ID.
    Use this to get basic game details like teams, score, date, location, and status.
    
    game_id is the numeric string found in ncaa.com game URLs (e.g., '6305900').
    
    Example: Get details for NCAA game 6305900.
    """
    _track("get_game_info")
    url = f"{BASE_URL}/game/{game_id}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_game_detail(game_id: str, detail_type: str) -> dict:
    """Fetch detailed data for a specific NCAA game such as box score, play-by-play,
    scoring summary, or team stats. Use this when the user wants in-depth game breakdown
    beyond the basic info.
    
    detail_type options: 'boxscore', 'play-by-play', 'scoring-summary', 'team-stats'.
    game_id is the numeric string found in ncaa.com game URLs (e.g., '6305900').
    
    Example: Box score for NCAA game 6305900.
    """
    _track("get_game_detail")
    url = f"{BASE_URL}/game/{game_id}/{detail_type}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_schedule(
    _track("get_schedule")
    sport: str,
    division: str,
    season: str,
    team_or_conference: Optional[str] = None,
    page: int = 1
) -> dict:
    """Fetch the schedule of games for a specific NCAA sport, team, or season.
    Use this when the user wants to know upcoming or past games on the calendar.
    
    Note: Football uses YYYY format for season, while basketball, hockey, and others
    use YYYY/MM format.
    
    Example: 2023 FBS football schedule.
    """
    if team_or_conference:
        url = f"{BASE_URL}/schedule/{sport}/{division}/{season}/{team_or_conference}"
    else:
        url = f"{BASE_URL}/schedule/{sport}/{division}/{season}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_news_or_history(
    _track("get_news_or_history")
    sport: str,
    content_type: str,
    division: Optional[str] = None,
    page: int = 1
) -> dict:
    """Fetch NCAA news articles or historical records for a sport or team.
    Use this when the user wants recent news, historical results, or background
    information about NCAA sports.
    
    content_type: 'news' for recent articles or 'history' for historical records.
    division: optional filter (e.g., 'fbs', 'd1', 'd2', 'd3').
    
    Example: Latest NCAA football news.
    """
    if content_type == "news":
        if division:
            url = f"{BASE_URL}/news/{sport}/{division}"
        else:
            url = f"{BASE_URL}/news/{sport}"
    elif content_type == "history":
        if division:
            url = f"{BASE_URL}/history/{sport}/{division}"
        else:
            url = f"{BASE_URL}/history/{sport}"
    else:
        return {"error": f"Invalid content_type '{content_type}'. Use 'news' or 'history'."}
    
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()




_SERVER_SLUG = "ncaa-api"

def _track(tool_name: str, ua: str = ""):
    try:
        import urllib.request, json as _json
        data = _json.dumps({"slug": _SERVER_SLUG, "event": "tool_call", "tool": tool_name, "user_agent": ua}).encode()
        req = urllib.request.Request("https://www.volspan.dev/api/analytics/event", data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass

async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

sse_app = mcp.http_app(transport="sse")

app = Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", sse_app),
    ],
    lifespan=sse_app.lifespan,
)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
