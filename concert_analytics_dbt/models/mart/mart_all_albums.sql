select 
	al.artist_name_hint as artist_name_hint
	,al.album_id as album_id
	,al.album_url as album_url
	,al.album_uri as album_uri
	,al.album_type as album_type
	,al.album_name as album_name
	,al.album_total_tracks as album_total_tracks
	,al.album_release_date_clean as album_release_date
	,al.album_image_url as album_image_url
	,almd.album_popularity as album_popularity
from 
	{{ ref('stg_artist_albums') }} al
  	join {{ ref('stg_artist_albums_metadata') }} almd
    	on al.album_id = almd.album_id