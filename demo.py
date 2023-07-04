from taifun import Taifun

import urllib.parse as urlparse

import httpx

import rich

from rich.prompt import Prompt


taifun = Taifun()


@taifun.fn()
def get_location() -> str:
    """
    Get the user's location

    returns: the user's location like a Ciry and State, e.g. San Francisco, CA
    """
    location = Prompt.ask("What is your location?")

    return location



@taifun.fn()
def get_lang_lat(location: str) -> dict:
    """
    Get the latitude and longitude of a location

    Parameters
    ----------
    location (str): the user's location like a Ciry and State, e.g. San Francisco, CA

    """

    response = httpx.get(
        f"https://nominatim.openstreetmap.org/search/{urlparse.quote(location)}",
        params={
            "format": "json",
        },
    )
    response.raise_for_status()
    data = response.json()
    lat = data[0]["lat"]
    lng = data[0]["lon"]

    return {"latitute": lat, "longitude": lng}


def get_current_weather(lon: float, lat: float):
    """Get the current weather in a given longitude and latitude

    Parameters
    ----------
    lon (float): longitude of the location
    lat (float): latitude of the location

    Returns:
        dict: a dictionary of the current weather

    """

    response = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data


if __name__ == "__main__":

    result = taifun.run("Should I wear sunglasses?")

    rich.print(result)
