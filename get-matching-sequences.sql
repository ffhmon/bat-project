### gets a list of sequences for which manual sequence classification
### matches automatical call classification (MostLikelySpecies field)
### use full latin SpeciesName e.g. 'Eptesicus nilssonii'

use ffh;

set @SpeciesName = 'Pipistrellus pygmaeus';
set @Species = concat('%',@SpeciesName,'%');

SELECT 
	#s.ProjectName, s.SDCardName, 
	s.SequenceName, @SpeciesName as ManualClassification, 
	count(c.SequenceName) as '#MatchingAutoClassifiedCalls'
	#s.recDate, s.recTime, s.recDuration, s.temperature, s.GPSLongitude, s.GPSLatitude
FROM ffh.`2016-call-import` c 
LEFT JOIN ffh.`2016-sequence-import` s ON c.SequenceName=s.SequenceName
WHERE c.AnyCI='PASS'
	and (s.EndClass1 like @Species
	or s.EndClass2 like @Species
	or s.EndClass3 like @Species)
	and c.MostLikelySpecies like @Species
GROUP BY s.SequenceName
