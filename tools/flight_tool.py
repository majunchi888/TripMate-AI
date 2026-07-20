import os
import re
import requests
import certifi
import airportsdata
import pycountry
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "JFK")

BASE_URL = "https://api.aviationstack.com/v1/flights"

AIRPORTS = airportsdata.load("IATA")


COUNTRY_ALIASES = {
    "usa": "US",
    "u.s.a": "US",
    "u.s.": "US",
    "america": "US",
    "united states": "US",
    "uk": "GB",
    "u.k.": "GB",
    "britain": "GB",
    "england": "GB",
    "uae": "AE",
    "dubai": "AE",
    "south korea": "KR",
    "korea": "KR",
    "russia": "RU",
    "vietnam": "VN",
    "bangladesh": "BD",
    "india": "IN",
    "japan": "JP",
    "china": "CN",
    "singapore": "SG",
    "malaysia": "MY",
    "thailand": "TH",
    "indonesia": "ID",
    "nepal": "NP",
    "qatar": "QA",
    "saudi arabia": "SA",
    "turkey": "TR",
    "canada": "CA",
    "australia": "AU",
    "germany": "DE",
    "france": "FR",
    "italy": "IT",
    "spain": "ES",
}


# Preferred main airport for country-level search
COUNTRY_MAIN_AIRPORT = {
    "BD": "DAC",
    "IN": "DEL",
    "JP": "NRT",
    "US": "JFK",
    "GB": "LHR",
    "AE": "DXB",
    "SG": "SIN",
    "MY": "KUL",
    "TH": "BKK",
    "ID": "CGK",
    "CN": "PEK",
    "KR": "ICN",
    "NP": "KTM",
    "QA": "DOH",
    "SA": "JED",
    "TR": "IST",
    "CA": "YYZ",
    "AU": "SYD",
    "DE": "FRA",
    "FR": "CDG",
    "IT": "FCO",
    "ES": "MAD",
}




CITY_MAIN_AIRPORT = {
        # China
    "beijing": "PEK",
    "shanghai": "PVG",
    "guangzhou": "CAN",
    "shenzhen": "SZX",
    "chengdu": "TFU",
    "hangzhou": "HGH",
    "xian": "XIY",
    "wuhan": "WUH",
    "nanjing": "NKG",
    "qingdao": "TAO",
    "xiamen": "XMN",
    "dhaka": "DAC",
    "delhi": "DEL",
    "new delhi": "DEL",
    "mumbai": "BOM",
    "kolkata": "CCU",
    "chennai": "MAA",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "tokyo": "NRT",
    "osaka": "KIX",
    "kyoto": "KIX",
    "new york": "JFK",
    "london": "LHR",
    "dubai": "DXB",
    "singapore": "SIN",
    "kuala lumpur": "KUL",
    "bangkok": "BKK",
    "doha": "DOH",
    "istanbul": "IST",
    "toronto": "YYZ",
    "sydney": "SYD",
    "paris": "CDG",
    "rome": "FCO",
    "madrid": "MAD",
    "frankfurt": "FRA",
}

# 清洗输入文本
def clean_text(text: str) -> str:
    text = text.lower().strip()
    # 保留英文、数字、中文、空格
    text = re.sub(r"[^\w\s\u4e00-\u9fa5]", " ", text)

    # 合并多个空格
    text = re.sub(r"\s+", " ", text)
    stop_words = ["flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"]

    words = [
        w for w in text.split()
        if w.strip()
        and w not in stop_words
    ]

    return " ".join(words).strip()


# ① 自定义别名COUNTRY_ALIASES
# ② pycountry全球库
# ③ 长文本搜索国家名
# ④ 再查别名 失败  返回None
def country_name_to_code(text:str):
    text = clean_text(text)

    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]
    
    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass

    # 检查长文本中的国家名
    for country in pycountry.countries:
        if country.name.lower() in text:
            return country.alpha_2
    
    for alias, code in COUNTRY_ALIASES.items():
        if alias.lower() in text:
            return code

    return None


def airport_country_matches(airport: dict, country_code: str) -> bool:
    """
    判断机场是否属于指定国家

    支持两种机场国家字段格式：
    1. ISO国家代码，例如 "JP"
    2. 国家英文名称，例如 "Japan"

    参数:
        airport: airportsdata中的机场信息字典
        country_code: ISO 3166-1 alpha-2 国家代码

    返回:
        匹配返回 True，否则返回 False
    """

    # 获取机场所属国家信息，并统一格式
    # 不同机场数据源中，country字段可能是"JP"或者"Japan"
    airport_country = str(airport.get("country", "")).upper().strip()
    # 第一种情况：机场数据直接使用ISO国家代码
    # 例如：机场国家为"JP"，查询国家代码也是"JP"
    if airport_country == country_code:
        return True
    
    try:
        # 根据ISO国家代码获取标准国家名称
        # 例如："JP" -> "Japan"
        country = pycountry.countries.get(alpha = country_code)
        # 第二种情况：机场数据使用国家英文名称
        # 例如："Japan" -> "Japan"
        if country and airport_country == country.name.lower():
            return True
    except Exception:
        pass

    return False    

def get_best_airport_for_country(country_code: str):
    """
    根据国家代码选择一个最佳代表机场

    优先使用预设的主要机场；
    如果没有预设，则从全球机场数据库中筛选并评分。

    参数:
        country_code: ISO国家代码，例如 "JP"

    返回:
        最佳机场IATA代码，例如 "NRT"
        如果没有找到机场，返回 None
    """    
    # 优先使用预先配置的国家主要机场
    # 例如：JP -> NRT，US -> JFK
    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)

    if preferred and preferred in AIRPORTS:
        return preferred    
    
    candidates = []
    # 遍历全球机场数据库，寻找属于该国家的机场
    for iata, airport in AIRPORTS.items():
        if not iata:
            continue

        if airport_country_matches(airport, country_code): # type: ignore
            name = str(airport.get("name", "")).lower()
            city = str(airport.get("city", "")).lower()

            score = 0

            if "international" in name:
                score += 50
            if "intl" in name:
                score += 40
            if "capital" in name:
                score += 20
            if city:
                score += 5

            candidates.append((score, iata))

    if not candidates:
        return None
    # 按评分从高到低排序
    candidates.sort(reverse=True)
    # 返回评分最高的机场IATA代码    
    return candidates[0][1]    



def resolve_location_to_iata(location: str):
    """
    Converts country/city/airport/IATA into IATA code.

    Examples:
    Bangladesh -> DAC
    Japan -> NRT
    Dhaka -> DAC
    Tokyo -> NRT
    DAC -> DAC
    """

    if not location:
        return None

    raw_location = location.strip()

    # Direct IATA code
    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)

    if not location_clean:
        return None

    # City preferred airport
    if location_clean in CITY_MAIN_AIRPORT:
        return CITY_MAIN_AIRPORT[location_clean]

    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
        if airport:
            return airport

    # Exact city match from airport database
    city_matches = []

    for iata, airport in AIRPORTS.items():
        city = str(airport.get("city", "")).lower().strip()
        name = str(airport.get("name", "")).lower().strip()

        score = 0

        if city == location_clean:
            score += 100
        elif location_clean in city:
            score += 70

        if location_clean in name:
            score += 50

        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]

    return None

def find_location_mentions(query: str):
    """
    Finds country or city names inside a natural language query.
    """    

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", q):  #re.search() 用于：在整个字符串中查找是否存在符合正则的内容。re.escape(alias)把正则特殊字符转义。\b单词边界。比如：alias = "china"，\bchina\b
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"\b{re.escape(name)}\b", q):
            mentions.append(name)

    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORT:
        if re.search(rf"\b{re.escape(city)}\b", q):
            mentions.append(city)

    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions


def parse_route(query: str):
    """
    把用户自然语言解析成出发机场（dep_iata）和到达机场（arr_iata）
    Returns:
    dep_iata, arr_iata

    Can return:
    None, None  -> global live flights
    DAC, NRT    -> filtered route
    DAC, None   -> all flights from DAC
    None, NRT   -> all flights to NRT
    """

    q = query.strip()
    q_lower = q.lower()

    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]

    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # Direct IATA code route: DAC to NRT。 IATA 三字码解析
    codes = re.findall(r"\b[A-Z]{3}\b", q)

    if len(codes) >= 2:
        dep = codes[0].upper()
        arr = codes[1].upper()
        return dep, arr

    # Pattern: from X to Y
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        origin_text = match.group(1)
        dest_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: to Y from X
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dest_text = match.group(1)
        origin_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: flights from X
    match = re.search(r"\bfrom\s+(.+?)(?:[.!?]|$)", q_lower)
    
    if match:
        origin_text = match.group(1)
        dep_iata = resolve_location_to_iata(origin_text)
    
        # 尝试从全文再找一个不同的地点作为目的地
        mentions = find_location_mentions(q)
    
        arr_iata = None
        for m in mentions:
            code = resolve_location_to_iata(m)
            if code and code != dep_iata:
                arr_iata = code
                break
    
        return dep_iata, arr_iata
    
    # Pattern: flights to X
    match = re.search(r"\bto\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        dest_text = match.group(1)
        arr_iata = resolve_location_to_iata(dest_text)
        return None, arr_iata

    # Fallback: find country/city mentions
    mentions = find_location_mentions(q)

    if len(mentions) >= 2:
        dep_iata = resolve_location_to_iata(mentions[0])
        arr_iata = resolve_location_to_iata(mentions[1])
        return dep_iata, arr_iata

    if len(mentions) == 1:
        arr_iata = resolve_location_to_iata(mentions[0])
        return DEFAULT_ORIGIN_IATA, arr_iata

    return None, None


# 把 AviationStack API 返回的航班 JSON 数据格式化成易读的文本。
# flight = {
#     "airline": {
#         "name": "Japan Airlines"
#     },
#     "flight": {
#         "iata": "JL22"
#     },
#     "flight_status": "scheduled",

#     "departure": {
#         "airport": "Narita International Airport",
#         "iata": "NRT",
#         "terminal": "2",
#         "gate": "61",
#         "scheduled": "2026-07-19T09:30:00+09:00",
#         "delay": 20
#     },

#     "arrival": {
#         "airport": "Beijing Capital International Airport",
#         "iata": "PEK",
#         "terminal": "3",
#         "gate": "E12",
#         "scheduled": "2026-07-19T12:40:00+08:00",
#         "delay": None
#     }
# }
def format_flight(flight: dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
                Airline: {airline}
                Flight: {flight_number}
                Status: {status}
                
                Departure:
                - Airport: {dep_airport}
                - IATA: {dep_iata}
                - Terminal: {dep_terminal}
                - Gate: {dep_gate}
                - Scheduled: {dep_scheduled}
                - Delay: {dep_delay_text}
                
                Arrival:
                - Airport: {arr_airport}
                - IATA: {arr_iata}
                - Terminal: {arr_terminal}
                - Gate: {arr_gate}
                - Scheduled: {arr_scheduled}
                - Delay: {arr_delay_text}
            """.strip()


def search_flights(query: str, limit: int = 10):
    """
    整个 Flight Tool 的入口函数。

    接收用户问题 → 解析航线 → 调用 AviationStack API → 格式化结果 → 返回给 Agent。
    """
    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(query)
    print(dep_iata)
    print(arr_iata)

    # 构造 AviationStack API 请求参数
    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        # 调用 AviationStack 获取实时航班数据
        response = requests.get(BASE_URL, params=params, timeout=50)
        # 随后 Requests 自动拼接 URL，会自动变成：
        # https://api.aviationstack.com/v1/flights?
        # access_key=xxxx
        # &dep_iata=PEK
        # &arr_iata=NRT
        # &limit=10

        #得到 response.status_code   # 状态码，例如200
            # response.headers       # 响应头
            # response.text          # 返回的文本
            # response.json()        # 把文本解析成Python对象
        data = response.json() #把服务器返回的 JSON 字符串转换成 Python 对象（通常是字典 dict）
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed: {e}"
    except ValueError:
        return "Flight API returned invalid JSON."

    if "error" in data:
        error = data["error"]
        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    flight_data = data.get("data", [])

    if not flight_data:
        route_text = ""

        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"

        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )

    route_info = "Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Live flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Live flights to {arr_iata}"

    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]

    return f"{route_info}\n\n" + "\n\n---\n\n".join(formatted_flights)


if __name__ == "__main__":
    print(search_flights("Plan a 7 days Japan trip from Bangladesh"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info"))    