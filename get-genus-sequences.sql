### gets a full list of sequences for a certain bat genus
### use latin GenusName without species e.g. 'Eptesicus'

use ffh;

set @GenusName = 'Pipistrellus';

set @Species = concat('%',@GenusName,'%');

SELECT 
	s.ProjectName, s.SDCardName, s.SequenceName,
	s.EndClass1, s.EndClass2, s.EndClass3,
	s.recDate, s.recTime, s.recDuration, s.temperature, s.GPSLongitude, s.GPSLatitude 
FROM ffh.`2016-sequence-import` s 
WHERE 
	(s.EndClass1 like @Species
	or s.EndClass2 like @Species
	or s.EndClass3 like @Species)
