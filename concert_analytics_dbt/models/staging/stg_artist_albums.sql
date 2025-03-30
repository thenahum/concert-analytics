select 
	album_id as album_id
	,album_url as album_url
	,album_uri as album_uri
	,album_type as album_type
	,album_name as album_name
	,cast(album_total_tracks as int) as album_total_tracks
	,case album_release_date_precision 
  		when 'day' then to_date(album_release_date, 'YYYY-MM-DD')
  		when 'month' then to_date(album_release_date || '-01', 'YYYY-MM-DD')
  		when 'year' then to_date(album_release_date || '-01-01', 'YYYY-MM-DD')
	end as album_release_date_clean
	,album_image_url as album_image_url
from 
	{{ source('raw', 'artist_albums') }}
