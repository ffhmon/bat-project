### gets a list of calls from sequences with a manual sequence classification on genus level only ("spec.")
### matching automatical call classification (MostLikelySpecies field) on a species with the genus
### use latin Genus only e.g. 'Eptesicus'

use ffh;

set @Genus = 'Pipistrellus';
set @SequenceGenus = concat('%',@Genus,' spec.%');
set @SelectedGenus = concat(@Genus,' spec.');
set @CallGenus = concat('%',@Genus,'%');

SELECT 
	c.ProjectName, c.SDCardName, c.SequenceName, c.CallName, c.MostLikelySpecies as AutoClassification, @SelectedGenus as ManualClassification,
	c.Duration, c.IntervalPre, c.intervalPost, c.MinFreq, c.MaxFreq, c.PeakFreq, c.CenterFreq, c.BestConfidence, c.AnyCI, c.SNR, c.numAgreeingClassifiers
FROM ffh.`2016-call-import` c left join ffh.`2016-sequence-import` s on c.SequenceName=s.SequenceName
where c.AnyCI='PASS'
and (s.EndClass1 like @SequenceGenus or s.EndClass2 like @SequenceGenus or s.EndClass3 like @SequenceGenus)
