from datetime import datetime

import requests
from user_agents import parse

from app.core.config import GEO_DETAILS_API
from app.core.logging import AppLogger
from app.utils.cache_service import CacheService

logger = AppLogger(name="kafka").get_logger()

now = datetime.now()
formatted = now.strftime("%Y-%m-%d %H:%M:%S")


def get_geo_data(ip_address: str):
    geo_data_details = CacheService.get_geo_ip_address(ip_address)
    if not geo_data_details:
        try:
            url = GEO_DETAILS_API.format(ip=ip_address)
            response = requests.get(url=url, timeout=2, verify=False)
            data = response.json()
            geo_data_details = {
                "country": data.get("country"),
                "city": data.get("city"),
                "region": data.get("region"),
                "location": data.get("loc"),
                "timezone": data.get("timezone"),
            }
            CacheService.set_geo_ip_address(ip_address, geo_data_details)
        except Exception as e:
            logger.exception(f"Error fetching geo data : {e}")
            return {}
    return geo_data_details


def get_device(user_agent):
    user_agent_details = CacheService.get_user_agent(user_agent)
    if not user_agent_details:
        user_agent_parsed = parse(user_agent)
        if user_agent_parsed.is_mobile:
            device_type = "Mobile"
        elif user_agent_parsed.is_tablet:
            device_type = "Tablet"
        elif user_agent_parsed.is_pc:
            device_type = "PC/Desktop"
        elif user_agent_parsed.is_bot:
            device_type = "Bot/Crawler"
        else:
            device_type = "Unknown"
        user_agent_details = {
            "device_type": device_type,
            "browser": user_agent_parsed.browser.family,
            "os": user_agent_parsed.os.family,
            "raw_user_agent": user_agent,
        }
        CacheService.set_user_agent(user_agent, mapping=user_agent_details)
    return user_agent_details
