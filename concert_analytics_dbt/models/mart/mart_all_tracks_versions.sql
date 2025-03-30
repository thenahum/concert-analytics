with album_track_joined as (
	select 
		al.album_id as album_id
		,al.album_url as album_url
		,al.album_uri as album_uri
		,al.album_type as album_type
		,al.album_name as album_name
		,al.album_total_tracks as album_total_tracks
		,al.album_release_date_clean as album_release_date
		,al.album_image_url as album_image_url
		,almd.album_popularity as album_popularity
		,tr.track_id as track_id
		,tr.track_url as track_url
		,tr.track_uri as track_uri
		,tr.track_disk_number as track_disk_number
		,tr.track_duration_seconds as track_duration_seconds
		,tr.track_name as track_name
		,tr.track_number as track_number
		,trmd.track_popularity as track_popularity
		,trmd.track_isrc as track_irsc
	from 
		{{ ref('stg_artist_albums') }} al
	  	join {{ ref('stg_artist_albums_metadata') }} almd
	    	on al.album_id = almd.album_id
	  	join {{ ref('stg_artist_tracks') }} tr
	    	on al.album_id = tr.album_id
	  	join {{ ref('stg_artist_tracks_metadata') }} trmd
	    	on tr.track_id = trmd.track_id
)
, album_track_ranked as (
	select 
 		album_id
		,album_url
		,album_uri
		,album_type
		,album_name
		,album_total_tracks
		,album_release_date
		,album_image_url
		,album_popularity
		,track_id
		,track_url
		,track_uri
		,track_disk_number
		,track_duration_seconds
		,track_name
		,track_number
		,track_popularity
		,track_irsc
 		,ROW_NUMBER() OVER (
			PARTITION BY 
				LOWER(track_name)
			ORDER BY
		    	CASE 
			    	WHEN album_type = 'album' THEN 0 
			    	ELSE 1 
			    end
			   ,track_popularity DESC NULLS last
		) as track_version_rank
 	from 
	 	album_track_joined
)
select 
	album_id
	,album_url
	,album_uri
	,album_type
	,album_name
	,album_total_tracks
	,album_release_date
	,album_image_url
	,album_popularity
	,track_id
	,track_url
	,track_uri
	,track_disk_number
	,track_duration_seconds
	,track_name
	,track_number
	,track_popularity
	,track_irsc
	,track_version_rank
from 
	album_track_ranked