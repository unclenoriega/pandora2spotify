#!/usr/bin/python3
import requests
from urllib.parse import quote
import re
import argparse

debug = False

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--pandora-username', help='Pandora username', required=True)
parser.add_argument('-v', '--spotify-username', help='Spotify username', required=True)
parser.add_argument('-p', '--playlist', help='Spotify playlist to use', required=True)
parser.add_argument('-a', '--pandora-auth', help='Pandora auth token', required=True)
parser.add_argument('-b', '--spotify-auth', help='Spotify auth token', required=True)
parser.add_argument('-d', '--debug', help='Display additional information', type=bool, default=False)
args = parser.parse_args()

pandora_authtoken = args.pandora_auth
pandora_username = args.pandora_username
pandora_csrftoken = '0123456789abcdef' # Pandora currently does not check this, so it is just made up
spotify_authtoken = args.spotify_auth
spotify_playlist_id = args.playlist
spotify_user_id = args.spotify_username

def getPandoraList(username, authtoken, csrftoken):
	r = requests.post('https://www.pandora.com/api/v1/station/getFeedback', '{pageSize: 100, startIndex: 0, webname: "'+username+'"}', cookies={'csrftoken':csrftoken}, headers={'X-CsrfToken':csrftoken,'Content-type':'application/json','X-AuthToken':authtoken})
	if r.status_code != 200:
			print('Error!', r.text)
			quit()
	json = r.json()

	total_songs = json['total']
	song_list = []
	song_count = 0
	startIndex = 0

	while (song_count < total_songs) and (len(json['feedback']) != 0):
		for i in json['feedback']:
			song_list.append({'title':i['songTitle'],'artist':i['artistName'], 'album':i['albumTitle']})
			if debug:
				print('adding song ' + i['songTitle'] + ' by ' + i['artistName'])
			song_count = song_count + 1
			if debug:
				print(song_count)
		startIndex = startIndex + 100
		if debug:
			print('Getting next page with startIndex ' + str(startIndex))
		r = requests.post('https://www.pandora.com/api/v1/station/getFeedback', '{pageSize: 100, startIndex: '+str(startIndex)+', webname: "'+username+'"}', cookies={'csrftoken':csrftoken}, headers={'X-CsrfToken':csrftoken,'Content-type':'application/json','X-AuthToken':authtoken})
		if r.status_code != 200:
			quit("Error!\n" + r.text)
		json = r.json()
	print('Found', len(song_list), 'tracks.')
	return song_list

def getSpotifySongUris(search_list, authtoken):
	uri_list = []
	missed_list = []
	for s in search_list:
		search_string = 'track:' + quote(re.sub(r'\(.*\)', '', s['title']) )+ '+artist:' + quote(re.sub(r'\(.*\)', '', s['artist'].replace('&',',')))
		r = requests.get('https://api.spotify.com/v1/search?type=track&q='+search_string+'&best_match=true&limit=1&market=from_token', headers={'authorization':authtoken})
		j = r.json()
		if len(j['best_match']['items']) > 0:
			uri_list.append(j['best_match']['items'][0]['uri'])
		else:
			missed_list.append('"{}" by {} from {}'.format(s['title'], s['artist'], s['album']))
			if debug:
				print('Search failed for: ' + search_string)
	print('Matched', len(uri_list), 'tracks.')
	return uri_list, missed_list

def addToPlaylist(uri_list, authtoken, user_id, playlist_id):
	added_tracks = 0
	while len(uri_list) > 100:
		uris = {"uris": uri_list[:100]}
		print('Adding 100 tracks to playlist')
		r = requests.post('https://api.spotify.com/v1/users/'+user_id+'/playlists/'+playlist_id+'/tracks', headers={'authorization':authtoken, 'Content-type':'application/json'}, json=uris)
		if r.status_code != 201:
			print('Error adding tracks')
			if debug:
				print(uris)
		else:
			added_tracks = added_tracks + 100
		uri_list = uri_list[100:]
	uris = {"uris": uri_list}
	r = requests.post('https://api.spotify.com/v1/users/'+user_id+'/playlists/'+playlist_id+'/tracks', headers={'authorization':authtoken, 'Content-type':'application/json'}, json=uris)
	if r.status_code != 201:
			print('Error adding tracks')
			if debug:
				print(uris)
	else:
		added_tracks = added_tracks + len(uri_list)
	print('Added', added_tracks, 'tracks.')
	#return playlist_url

pandora_list = getPandoraList(pandora_username, pandora_authtoken, pandora_csrftoken)
(spotify_list, missed_tracks) = getSpotifySongUris(pandora_list, spotify_authtoken)

addToPlaylist(spotify_list, spotify_authtoken, spotify_user_id, spotify_playlist_id)
print('Finished creating playlist.')
print('Unmatched tracks:')
for t in missed_tracks:
	print(t)
