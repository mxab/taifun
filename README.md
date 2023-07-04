# Taifun

Typed AI Functions


## Usage

```python

from taifun import Taifun

# ... set openai api key

taifun = Taifun()

@taifun.fn()
def get_user_name() -> str:
    return "Alex"

if __name__ == "__main__":
    taifun.run("Say hello to user")

```