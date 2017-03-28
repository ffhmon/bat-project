### gets a list of calls from sequences with a manual sequence classification
### matching automatical call classification (MostLikelySpecies field)
### and where only one species was found in the recording (for better statistical results)
### use full latin SpeciesName e.g. 'Eptesicus nilssonii'

use ffh;

set @Species = 'Pipistrellus pygmaeus';

set @Genus = concat('%',@Species,'%');

SELECT 
	c.ProjectName, c.SDCardName, c.SequenceName, c.CallName, c.MostLikelySpecies as AutoClassification, s.EndClass1 as ManualClassification,
	c.Duration, c.IntervalPre, c.intervalPost, c.MinFreq, c.MaxFreq, c.PeakFreq, c.CenterFreq, c.BestConfidence, c.AnyCI, c.SNR, c.numAgreeingClassifiers
FROM ffh.`2016-call-import` c left join ffh.`2016-sequence-import` s on c.SequenceName=s.SequenceName
where c.AnyCI='PASS'
and (s.EndClass1 like @Genus and s.EndClass2 = '' and s.EndClass3 ='')
and c.MostLikelySpecies like @Genus

