# Organizer
 Discord bot that sends message at specific time which users can react to.

## Requirements
 - [Python 3.8.6](https://www.python.org/downloads/release/python-386/)
 - [Discord.py](https://github.com/Rapptz/discord.py/)
 - [Discord.py Menus](https://github.com/Rapptz/discord-ext-menus)

## Setup
 1. Install Python 3.8.6
 2. Clone this repository.
 3. Go to the repository destination and execute `pip install -r requirements.txt`
 4. Rename `config_example.json` to `config.json` and set important variables.
 ```
 {
    "token": "", <- Token here
    "prefix": "", <- Prefix here (Not needed for much | Defaults to `o!`)
    "time": {"hour": 0, "minute": 0, "second": 0},
    "channel_id": 0, <- The ID where the bot should send the message
    "title": "", <- The event title
    "description": "" <- The event description
}
```

 5. Run the `bot.py`

## Issues
 If you encounter any bugs create an issue and I'll try to resolve the porblem.

## Limitations
 - Only works for one guild.
 - Need to account for different timezones.

 Note: These limitations can be solved but I'm lazy to do so. Might solve them in future commits.

## Contribution
 If you want to improve the bot feel free to make a pull request!

## Lincense
 [GNU GPLv3](LICENSE)