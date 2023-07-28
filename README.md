# Taifun - Typed AI Functions

A simple framework for creating typed AI functions.

It inspects the function's docstring and parameters to create functions for OpenAI's API.

Then takes a task and loops through the conversational flow until the task is complete.


## Usage

### Just functions to pass to OpenAI

```python

taifun = Taifun()


@taifun.fn()
def weather_forcast(location: str) -> str:
    """
    Get the weather forcast for a given location

    Parameters
    ----------
    location (str): the location to get the weather forcast for

    """

    # random weather
    weather = random.choice(["sunny", "rainy", "cloudy", "snowy"])

    return f"The weather in {location} is {weather}"


messages = [
    {
        "role": "user",
        "content": "Is it rainingy in berlin today?",
    },
]

# export functions as json schema dict for openai
functions = taifun.functions_as_dict()


result = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    functions=functions,
    function_call="auto",
)
response_message = result["choices"][0]["message"]

print(f"assistant: {response_message['content']}")

function_call = response_message.get("function_call")

messages.append(response_message)
if function_call is not None:
    # handle the function call
    function_response = taifun.handle_function_call(function_call)

    # responed with the function response
    print(f"function response: {function_response}")
    messages.append(
        {
            "role": "function",
            "name": function_call["name"],
            "content": function_response,
        }
    )

    result2 = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    response_message2 = result2["choices"][0]["message"]
    print(f"assistant: {response_message2['content']}")

```

```python

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


class Coordinates(BaseModel):
    latitude: float = Field(
        ..., title="Latitude", description="The latitude of a location"
    )
    longitude: float = Field(
        ..., title="Longitude", description="The longitude of a location"
    )


@taifun.fn()
def get_current_weather(coordinates: Coordinates):
    """Get the current weather in a given longitude and latitude

    Parameters
    ----------
    coordinates (Coordinates): the latitude and longitude of a location

    Returns:
        dict: a dictionary of the current weather

    """

    response = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": coordinates.latitude,
            "longitude": coordinates.longitude,
            "current_weather": True,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data


if __name__ == "__main__":
    openai.api_key_path = os.path.expanduser("~") + "/.openai_api_key"
    runner = TaifunConversationRunner(taifun)
    result = runner.run("Will I need an umbrella today?")

    rich.print(result)



```
