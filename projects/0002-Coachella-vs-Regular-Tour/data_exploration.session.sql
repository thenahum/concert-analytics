-- with coachella_dates(artist_name_hint,coachella_weekend,coachella_start_date,coachella_end_date) as (
--     values 
--         ('Turnstile','Weekend 1','2022-04-16'::date,'2022-04-18'::date)
--         ,('BillieEilish','Weekend 1','2022-04-16'::date,'2022-04-18'::date)
--         ,('JapaneseBreakfast','Weekend 1','2022-04-16'::date,'2022-04-18'::date)
--         ,('TameImpala','Weekend 1','2019-04-12'::Date, '2019-04-14'::date)
--         ,('Turnstile','Weekend 2','2022-04-23'::Date, '2022-04-25'::date)
--         ,('BillieEilish','Weekend 2','2022-04-23'::Date, '2022-04-25'::date)
--         ,('JapaneseBreakfast','Weekend 2','2022-04-23'::Date, '2022-04-25'::date)
--         ,('TameImpala','Weekend 2','2019-04-19'::date, '2019-04-21'::Date)
-- )
-- , analysis_dates as (
--     select 
--         artist_name_hint
--         ,min(coachella_start_date) as first_coachella_date
--         ,max(coachella_end_date) as last_coachella_date
--         ,min(coachella_start_date) - 365 as reporting_start_date
--         ,max(coachella_end_date) + 365 as reporting_end_date
--     from 
--         coachella_dates
--     group by 
--         1
-- )
-- , coachella_sets_cte as (
--     select 
--         msh.artist_name_hint	
--         ,msh.event_set_song_id	
--         ,msh.event_id	
--         ,msh.event_date	
--         ,msh.event_info	
--         ,msh.event_url	
--         ,msh.event_tour_id	
--         ,msh.event_tour	
--         ,msh.venue_id	
--         ,msh.venue_name	
--         ,case when cd.artist_name_hint is not null then TRUE else FALSE end as is_coachella
--         ,cd.coachella_weekend as coachella_weekend
--         ,case when ad.first_coachella_date > msh.event_date then  ad.first_coachella_date - msh.event_date end as days_before_first_coachella_date
--         ,case when ad.last_coachella_date < msh.event_date then msh.event_date - ad.last_coachella_date end as days_after_last_coachella_date
--     from 
--         analytics_mart.mart_setlist_history as msh
--         join analysis_dates as ad 
--             on msh.artist_name_hint = ad.artist_name_hint
--             and msh.event_date between ad.reporting_start_date and ad.reporting_end_date 
--         left join coachella_dates as cd 
--             on msh.artist_name_hint = cd.artist_name_hint
--             and msh.event_date between cd.coachella_start_date and cd.coachella_end_date
--     where TRUE
-- )
-- select
--     *
-- from 
--     coachella_sets_cte
-- ;

select *  
from 
    analytics_mart.mart_track_setlist_similarity_scores
where 
    artist_name_hint='JapaneseBreakfast'
;