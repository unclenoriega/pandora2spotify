# pandora2spotify
Create a Spotify playlist based on Pandora "thumbprint" likes

This program reads thumbprint likes from your (or any public) Pandora profile, tries to find a matching track on Spotify, and adds the best match to a Spotify playlist.

You'll need a few things to get started:

1. A Pandora username
2. A Spotify username
3. A Spotify playlist ID
4. A Pandora auth token
5. A Spotify auth token

# Getting a Spotify Playlist ID

Simply create a playlist and navigate to its page in Spotify's web player. The ID is in the URL like so: `https://open.spotify.com/user/{username}/playlist/{playlist_id}`

# Getting a Spotify Auth Token

While you're in the Spotify web player, open your browser's developer tools, and inspect a request to api.spotify.com, looking for a request header called `authorization`. The value will start with 'Bearer' and be really long. This is the token you need.

# Getting a Pandora Auth Token

Similarly, login to pandora.com and look for a request header called `X-AuthToken`. Its value is not as long. This is your Pandora auth token.

# Putting it all together

Then just do this: `python3 pandora2spotify.py --pandora-username {pandora_username} --spotify-username {spotify_username} --playlist {playlist_id} --pandora-auth {pandora_authtoken} --spotify-auth {spotify_authtoken}`

If all goes well, your playlist will soon be filled with tracks from your Pandora likes. You will also be presented with a list of tracks that did not produce any results in the Spotify search.
