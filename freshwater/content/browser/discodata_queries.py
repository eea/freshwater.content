""" fetch data from discodata """

SW_PRIORITY_SUBSTANCE_EU27_2022 = """
select
LOWER(CONCAT('EU27', '-', '3rd', '-', REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(title, ' - ', '-'), ' + ', '-'), ' ', '-'), '_', '-'), '(', ''), ')', ''), ',', ''))) as 'id',
title,
count(*) as 'number_of_appearances',
count(distinct surfaceWaterBodyCategory) as 'number_of_categories',
count(distinct countryCode) as 'number_of_countries',
'3rd' as 'management_plan',
'SWPrioritySubstance' as 'chemical_type',
'EU27' as 'country'
from (SELECT 'chemical' as '@type',
'Chemical' as 'type_title',
SUBSTRING(REPLACE(swPrioritySubstanceCode, ' - ', '#'), CHARINDEX('#', REPLACE(swPrioritySubstanceCode, ' - ', '#'))+1, LEN(REPLACE(swPrioritySubstanceCode, ' - ', '#'))) as 'title',
surfaceWaterBodyCategory,
countryCode
from [WISE_WFD].[v2r1].[SWB_SurfaceWaterBody_SWPrioritySubstance]
where swPrioritySubstanceCausingFailure = 'YES'
and countryGroup = 'EU27'
and cYear = 2022) as "asd"
group by title
order by number_of_appearances desc
"""

SW_PRIORITY_SUBSTANCE_COUNTRIES_2022 = """
select 
LOWER(CONCAT(countryCode, '-', '3rd', '-', REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(title, ' - ', '-'), ' + ', '-'), ' ', '-'), '_', '-'), '(', ''), ')', ''), ',', ''))) as 'id',
title,
count(*) as 'number_of_appearances', 
count(distinct surfaceWaterBodyCategory) as 'number_of_categories', 
count(distinct countryCode) as 'number_of_countries',
'3rd' as 'management_plan',
'SWPrioritySubstance' as 'chemical_type',
countryCode as 'country'
from (SELECT 'chemical' as '@type', 
'Chemical' as 'type_title',
SUBSTRING(REPLACE(swPrioritySubstanceCode, ' - ', '#'), CHARINDEX('#', REPLACE(swPrioritySubstanceCode, ' - ', '#'))+1, LEN(REPLACE(swPrioritySubstanceCode, ' - ', '#'))) as 'title',
surfaceWaterBodyCategory,
countryCode
from [WISE_WFD].[v2r1].[SWB_SurfaceWaterBody_SWPrioritySubstance]
where swPrioritySubstanceCausingFailure = 'YES'
and cYear = 2022) as "asd"
group by title, countryCode
order by number_of_appearances desc
"""

SW_RBSP_POLLUTANT_COUNTRIES_2022 = """
select 
LOWER(CONCAT(countryCode, '-', '3rd', '-', REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(title, ' - ', '-'), ' + ', '-'), ' ', '-'), '_', '-'), '(', ''), ')', ''), ',', ''))) as 'id',
title,
count(*) as 'number_of_appearances', 
count(distinct surfaceWaterBodyCategory) as 'number_of_categories', 
count(distinct countryCode) as 'number_of_countries',
'3rd' as 'management_plan',
'swFailingRBSP' as 'chemical_type',
countryCode as 'country'
from (SELECT 'chemical' as '@type', 
'Chemical' as 'type_title',
SUBSTRING(REPLACE(swFailingRBSP, ' - ', '#'), CHARINDEX('#', REPLACE(swFailingRBSP, ' - ', '#'))+1, LEN(REPLACE(swFailingRBSP, ' - ', '#'))) as 'title',
surfaceWaterBodyCategory,
countryCode
from [WISE_WFD].[v2r1].[SWB_SurfaceWaterBody_FailingRBSP]
where cYear = 2022
and swFailingRBSP != '') as "asd"
group by title, countryCode
order by number_of_appearances desc
"""

SW_RBSP_POLLUTANT_EU27_2022 = """
select 
LOWER(CONCAT('EU27', '-', '3rd', '-', REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(title, ' - ', '-'), ' + ', '-'), ' ', '-'), '_', '-'), '(', ''), ')', ''), ',', ''))) as 'id',
title,
count(*) as 'number_of_appearances', 
count(distinct surfaceWaterBodyCategory) as 'number_of_categories', 
count(distinct countryCode) as 'number_of_countries',
'3rd' as 'management_plan',
'swFailingRBSP' as 'chemical_type',
'EU27' as 'country'
from (SELECT 'chemical' as '@type', 
'Chemical' as 'type_title',
SUBSTRING(REPLACE(swFailingRBSP, ' - ', '#'), CHARINDEX('#', REPLACE(swFailingRBSP, ' - ', '#'))+1, LEN(REPLACE(swFailingRBSP, ' - ', '#'))) as 'title',
surfaceWaterBodyCategory,
countryCode
from [WISE_WFD].[v2r1].[SWB_SurfaceWaterBody_FailingRBSP]
where countryGroup = 'EU27'
and swFailingRBSP != ''
and cYear = 2022) as "asd"
group by title
order by number_of_appearances desc
"""

GW_POLLUTANT_COUNTRIES_2022 = """
select 
LOWER(CONCAT(countryCode, '-', '3rd', '-', REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(title, ' - ', '-'), ' + ', '-'), ' ', '-'), '_', '-'), '(', ''), ')', ''), ',', ''))) as 'id',
title,
ROUND(sum(cArea), 0) as 'number_of_area',
count(*) as 'number_of_appearances', 
count(distinct countryCode) as 'number_of_countries',
'3rd' as 'management_plan',
'GWPollutant' as 'chemical_type',
countryCode as 'country'
from (SELECT cArea, 'chemical' as '@type', 
'Chemical' as 'type_title',
SUBSTRING(REPLACE(gwPollutantCode, ' - ', '#'), CHARINDEX('#', REPLACE(gwPollutantCode, ' - ', '#'))+1, LEN(REPLACE(gwPollutantCode, ' - ', '#'))) as 'title',
countryCode
from [WISE_WFD].[v2r1].[GWB_GroundWaterBody_GWPollutant]
where gwPollutantCausingFailure = 'YES'
and cYear = 2022) as "asd"
group by title, countryCode
order by number_of_area desc
"""

GW_POLLUTANT_EU27_2022 = """
select 
LOWER(CONCAT('EU27', '-', '3rd', '-', REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(title, ' - ', '-'), ' + ', '-'), ' ', '-'), '_', '-'), '(', ''), ')', ''), ',', ''))) as 'id',
title,
ROUND(sum(cArea), 0) as 'number_of_area',
count(*) as 'number_of_appearances', 
count(distinct countryCode) as 'number_of_countries',
'3rd' as 'management_plan',
'GWPollutant' as 'chemical_type',
'EU27' as 'country'
from (SELECT cArea, 'chemical' as '@type', 
'Chemical' as 'type_title',
SUBSTRING(REPLACE(gwPollutantCode, ' - ', '#'), CHARINDEX('#', REPLACE(gwPollutantCode, ' - ', '#'))+1, LEN(REPLACE(gwPollutantCode, ' - ', '#'))) as 'title',
countryCode
from [WISE_WFD].[v2r1].[GWB_GroundWaterBody_GWPollutant]
where gwPollutantCausingFailure = 'YES'
and countryGroup='EU27'
and cYear = 2022) as "asd"
group by title
order by number_of_area desc
"""
