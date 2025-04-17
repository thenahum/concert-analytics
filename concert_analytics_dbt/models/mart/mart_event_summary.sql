with event_summary as (
	select 
		event_id
		,event_date
		,event_info
		,event_url
		,event_tour_id
		,event_tour
		,venue_id
		,venue_name
		,venue_city
		,venue_state_code
		,venue_country_code
		,venue_latitude
		,venue_longitude
		,count(distinct event_set_song_id) as event_total_songs
		,count(distinct set_index) as event_total_sets
		,count(distinct case 
			when encore_flag = true then event_set_song_id 
			end 
			) as event_total_encore_songs
		,count(distinct case 
			when encore_flag = false then event_set_song_id 
			end 
			) as event_total_non_encore_songs
		,lag(event_date) over (order by event_date asc) as event_last_date	
		,lag(event_tour_id) over (order by event_date asc) as event_last_tour_id
	from 
		{{ ref('stg_setlist_history') }}
	group by 
		1,2,3,4,5,6,7,8,9,10,11,12,13
), new_tour_flag as (
	select 
		*
		,case 
			when event_tour_id <> event_last_tour_id then 1 
			when event_date - event_last_date > 90 then 1
			else 0 
		end as new_tour_flag
	from 
		event_summary
), tour_psuedo_counter as (
	select 
		*
		,sum(new_tour_flag) over (order by event_date) as tour_psuedo_counter
	from 
		new_tour_flag
)
select 
	event_id
	,event_date
	,event_info
	,event_url
	,event_tour_id
	,event_tour
	,venue_id
	,venue_name
	,venue_city
	,venue_state_code
	,venue_country_code
	,venue_latitude
	,venue_longitude
	,event_total_songs
	,event_total_sets
	,event_total_encore_songs
	,event_total_non_encore_songs
	,event_last_date
	,event_last_tour_id
	,md5('mewithoutyou'||tour_psuedo_counter) as event_tour_pseudo_id
from 
	tour_psuedo_counter