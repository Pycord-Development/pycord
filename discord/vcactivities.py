from aiohttp import ClientSession
from typing import Union, Optional
#errors

class InvalidArgument(Exception):
    """Raised when an invalid argument was entered."""
    pass

class RangeExceeded(Exception):
    """Raised when the allowed ranges for max_age and max_uses parameters were exceeded."""
    pass

class BotMissingPerms(Exception):
    """Raised when your bot does not have CREATE_INSTANT_INVITE permissions."""
    pass

class ConnectionError(Exception):
    """Raised when a general error occured while communicating with Discord API."""
    pass

defaultApplications = { 
    'youtube': '880218394199220334',
    'poker': '755827207812677713',
    'betrayal': '773336526917861400',
    'fishing': '814288819477020702',
    'chess': '832012774040141894',
    # ---
    'letter-league': '879863686565621790',
    'word-snack': '879863976006127627',
    'sketch-heads': '902271654783242291',
    'spellcast': '852509694341283871',
    'awkword': '879863881349087252',
    'checkers': '832013003968348200',
    'blazing-8s': '832025144389533716',
    'land-io': '903769130790969345',
    'putt-party': '945737671223947305',
    'bobble-league': '947957217959759964',
}


class AsyncObject(object):
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass

class DiscordTogether(AsyncObject):
    """
    Controls invite generations.
    
    Parameters
    ----------
    token: str
        The token used by your bot.
    debug: :class:`bool` 
        (default = False) Debug mode toggle
    
    Methods
    -------
    create_link(voiceChannelID : int, option : str, *, max_age : Optional[int], max_uses : Optional[int])
    Attributes
    -------
    default_choices
        Gives all the default application choices that you have as a list
    """

    default_choices = list(defaultApplications.keys())

    async def __init__(self, token: str, *, debug: Optional[bool] = False):
        """
        Controls invite generations.
        Parameters
        ----------
        token: str
            The token used by your bot.
        debug: Optional[:class:`bool`]
            Debug mode toggle, used to identify error code in case of invalid invite links.
            Default value is false.
        
        Methods
        -------
        create_link(voiceChannelID : int, option : str, *, max_age : Optional[int], max_uses : Optional[int])
            Creates a invite link
        """
        
        self._session = ClientSession()

        if isinstance(token, str):
            self.token = token
        else:
            raise TypeError(f"'token' parameter MUST be of type string, not a {type(token).__name__!r} type.")
        
        if isinstance(debug, bool):
            self.debug = debug
        else:
            self.debug = False
            print('\033[93m'+"[WARN] (discord-together) Debug parameter did not receive a bool object. Reverting to Debug = False."+'\033[0m') 
        
    async def close(self):
        await self._session.close()
    
    async def create_link(self, voiceChannelID: Union[int,str], option: Union[int,str], *, max_age: Optional[int] = 0, max_uses: Optional[int] = 0) -> str:
        """
        Generates an invite link to a VC with the Discord Party VC Feature.
        Parameters
        ----------
        voiceChannelID: Union[:class:`str`, :class:`int`]
            ID of the voice channel to create the activity for
        option: Union[:class:`str`, :class:`int`]
            A option amongst the predefined choices (DiscordTogether.default_choices) or a custom ID
        max_age: Optional[:class:`int`]
            Optional duration in seconds after which the invite expires. 
            Value has to be between 0 (Unlimited) and 604800 (7 days), default is 86400 (24 hrs).
        max_uses: Optional[:class:`int`]
            Optional maximum number of times this invite can be used.
            Value has to be between 0 to 100, default is 0 (Unlimited).
        
        Returns
        ----------
        :class:`str`
            Contains the discord invite link which, upon clicked, starts the custom activity in the VC. 
        """
        
        # Type checks
        if not isinstance(voiceChannelID, (str,int)):
            raise TypeError(f"'voiceChannelID' argument MUST be of type string or integer, not a {type(voiceChannelID).__name__!r} type.")
        if not isinstance(option, (str,int)):
            raise TypeError(f"'option' argument MUST be of type string or integer, not a {type(option).__name__!r} type.")
        
        # Max Range checks
        if not 0 <= max_age <= 604800:
            raise RangeExceeded(f'max_age argument value should be an integer between 0 and 604800')
        if not 0 <= max_uses <= 100:
            raise RangeExceeded(f'max_uses argument value should be an integer between 0 and 100')

        # Pre Defined Application ID
        if option and (str(option).lower().replace(" ", "") in defaultApplications.keys()):   

            data = {
                'max_age': max_age,
                'max_uses': max_uses,
                'target_application_id': defaultApplications[str(option).lower().replace(" ","")],
                'target_type': 2,
                'temporary': False,
                'validate': None
            }
            
            async with self._session.post(f"https://discord.com/api/v10/channels/{voiceChannelID}/invites",
                    json=data, 
                    headers = {
                        'Authorization': f'Bot {self.token}',
                        'Content-Type': 'application/json'
                    }) as resp:
                resp_code = resp.status
                result = await resp.json()

            if self.debug:
                print('\033[95m'+'\033[1m'+'[DEBUG] (discord-together) Response Output:\n'+'\033[0m'+'HTTP RESPONSE CODE: '+str(resp_code)+'\n'+str(result))
            
            if resp_code == 429:
                raise ConnectionError('You are being rate limited, see Rate Limits (https://discord.com/developers/docs/topics/rate-limits).')
            elif resp_code == 401:
                raise ConnectionError('The Authorization header was missing or invalid. Verify if the token you entered inside the constructor is correct.')
            elif result['code'] == 10003 or (result['code'] == 50035 and 'channel_id' in result['errors']):
                raise InvalidArgument(f'Voice Channel ID {str(voiceChannelID)!r} is invalid.')
            elif result['code'] == 50013:
                raise BotMissingPerms('Missing CREATE_INSTANT_INVITE permissions for that voice channel.')
            elif result['code'] == 130000:
                raise ConnectionError('API Resource is currently overloaded. Try again a little later.')
            
            return f"https://discord.gg/{result['code']}"



        # User Defined Application ID
        elif option and (str(option).replace(" ", "") not in defaultApplications.keys()) and str(option).replace(" ","").isnumeric():
            
            data = {
                'max_age': max_age,
                'max_uses': max_uses,
                'target_application_id': str(option).replace(" ", ""),
                'target_type': 2,
                'temporary': False,
                'validate': None
            }

            async with self._session.post(f"https://discord.com/api/v10/channels/{voiceChannelID}/invites",
                    json=data, 
                    headers = {
                        'Authorization': f'Bot {self.token}',
                        'Content-Type': 'application/json'
                    }) as resp:
                resp_code = resp.status
                result = await resp.json()

            if self.debug:
                print('\033[95m'+'\033[1m'+'[DEBUG] (discord-together) Response Output:\n'+'\033[0m'+'HTTP RESPONSE CODE: '+str(resp_code)+'\n'+str(result))
            
            if resp_code == 429:
                raise ConnectionError('You are being rate limited, see Rate Limits (https://discord.com/developers/docs/topics/rate-limits).')
            elif resp_code == 401:
                raise ConnectionError('The Authorization header was missing or invalid. Verify if the token you entered inside the constructor is correct.')
            elif result['code'] == 50035 and 'target_application_id' in result['errors']:
                raise InvalidArgument(str(option).replace(" ", "")+" is an invalid custom application ID.")
            elif result['code'] == 10003 or (result['code'] == 50035 and 'channel_id' in result['errors']):
                raise InvalidArgument(f'Voice Channel ID {str(voiceChannelID)!r} is invalid.')
            elif result['code'] == 50013:
                raise BotMissingPerms('Missing CREATE_INSTANT_INVITE permissions for that voice channel.')
            elif result['code'] == 130000:
                raise ConnectionError('API Resource is currently overloaded. Try again a little later.')

            return f"https://discord.gg/{result['code']}"

        else:
            raise InvalidArgument("Invalid activity option chosen. You may only choose between (\"{}\") or input a custom application ID.".format('", "'.join(defaultApplications.keys())))
