select 
	cast(album_id as varchar) as album_id
	,cast(album_popularity as int) as album_popularity
from 
	{{ source('raw', 'artist_albums_metadata') }}