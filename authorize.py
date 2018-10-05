import urllib.request
import webbrowser

print(f'\n\nPlease open https://glass.twitch.tv/console/apps/create in your browser.')
print(f'Authorize Twitch Developer. On the Twitch dev dashboard go to "Apps > Register Your Application" and make a new application.')
print(f'In "Manage Application," set the Redirect URL to "http://localhost" and find the Client ID.')

client_id = input("\nPlease enter Client ID: ").rstrip()

url = f'https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=http://localhost&scope=user:edit+channel:moderate+chat:edit+chat:read+whispers:read+whispers:edit'

webbrowser.open(url, new=2)

print(f'''\nLog in and authorize the App you've made. You'll be redirected to a blank page.''')
print(f'''\nYour token is the string between the equals sign (=) and the ampersand (&). Copy and paste into config.py.''')
