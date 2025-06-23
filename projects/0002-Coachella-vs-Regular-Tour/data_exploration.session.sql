with coachella_sets_cte as (
    select 
        * 
        ,case 
            when
                artist_name_hint <> 'TameImpala' 
                and (event_date between '2022-04-16' and '2022-04-18'
                or event_date between '2022-04-23' and '2022-04-25')
            then TRUE
            when artist_name_hint = 'TameImpala'
            and (event_date between '2019-04-12' and '2019-04-14'
                or event_date between '2019-04-19' and '2019-04-21')
            then TRUE
            else FALSE
        end as is_coachella
    from 
        analytics_mart.mart_setlist_history 
    where TRUE
        and ( 
            (artist_name_hint <> 'TameImpala' 
                and event_date between '2021-04-16' and '2023-04-25')
            OR (artist_name_hint = 'TameImpala'
                and event_date between '2018-04-12' and '2020-04-22')
            )
        and artist_name_hint in ('Turnstile','TameImpala','BillieEilish','JapanseBreakfast')
)
select
    artist_name_hint
    ,is_coachella
    ,count(1)
from 
    coachella_sets_cte
group by 
    1,2
limit 10
;

