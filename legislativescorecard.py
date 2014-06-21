import unicodecsv
import argparse
import datetime
from sunlight import congress

class LegislativeScorecard(object):
	""" Helper class to assemble legislative scorecards """
	
	FIELDS_TO_COLLECT = ['title','first_name','last_name','party','state','district','twitter_id','youtube_id','facebook_id']

	def __init__(self):
		super(LegislativeScorecard, self).__init__()
		
		self.representatives = []
		self.senators = []   
		self.scores = {}

		self.legislator_metadata = {}

		# grab bioguides
		for (varname, chamber) in ((self.senators, 'senate'), (self.representatives, 'house')):
			i = 0
			while True:
				new_reps = congress.legislators(chamber=chamber, fields=','.join(['bioguide_id',] + LegislativeScorecard.FIELDS_TO_COLLECT), page=i)
				if new_reps is None:
					break
				for nr in new_reps:
					bioguide = nr['bioguide_id']
					varname.append(bioguide)

					self.legislator_metadata[bioguide] = {}
					for k in LegislativeScorecard.FIELDS_TO_COLLECT:
						self.legislator_metadata[bioguide][k] = nr.get(k)

				i = i + 1
		
		self.reset_scores()

	def reset_scores(self):
		# initialize scores dict
		self.scores = {}
		for legislator in self.representatives + self.senators:
			self.scores[legislator] = {} 
		
	def _get_adjustment_desc(self, score_adjustment):
		return score_adjustment.items()[0]
		
	def voted_aye(self, score_adjustment, roll_ids):
		""" Checks for aye votes on one or more roll call votes """
		(adjustment_desc, adjustment) = self._get_adjustment_desc(score_adjustment)
		
		for roll_id in roll_ids:
			votes = congress.votes(roll_id=roll_id, fields='voters')	
			
			for legislator in self.scores:
				score = 0							
				if votes[0]['voters'].get(legislator, {'vote': 'not present in data'})['vote'].lower().strip() == 'yea':
					score = adjustment
				self.scores[legislator]['%s (%s%s)' % (adjustment_desc, (adjustment > 0) and '+' or '', adjustment)] = score		


	def cosponsored(self, score_adjustment, bill_id, cosponsorship_test=lambda x: True):
		""" Tests whether each legislator sponsored or cosponsored a bill, with optional test """
		(adjustment_desc, adjustment) = self._get_adjustment_desc(score_adjustment)

		bill = congress.bills(bill_id=bill_id, fields='cosponsor_ids,sponsor_id')[0]
		cosponsors = congress.bills(bill_id=bill_id, fields='cosponsors')
		valid_sponsor_cosponsor_ids = [bill['sponsor_id']]
		
		for cs in cosponsors[0]['cosponsors']:
			if cosponsorship_test(cs):
				valid_sponsor_cosponsor_ids.append(cs['legislator']['bioguide_id'])
		
		for legislator in self.scores:
			score = 0
			if legislator in valid_sponsor_cosponsor_ids:
				score = adjustment
			self.scores[legislator]['%s (%s%s)' % (adjustment_desc, (adjustment > 0) and '+' or '', adjustment)] = score		
		

	def write(self, out_f):
		writer = unicodecsv.writer(out_f)
		
		# figure out what we've actually recorded here
		fields_to_emit = {}
		for l in self.scores:
			for k in self.scores[l]:
				fields_to_emit[k] = True
		fields_to_emit = sorted(fields_to_emit.keys())

		writer.writerow(['bioguide_id'] + fields_to_emit + ['total'] + LegislativeScorecard.FIELDS_TO_COLLECT)

		# tabulate data
		for bioguide_id in sorted(self.scores):
			out_row = [bioguide_id]
			total = 0
			for field in fields_to_emit:
				value = self.scores[bioguide_id].get(field, 0)
				out_row.append(value)
				total = total + value

			out_row.append(total)
			
			for field in LegislativeScorecard.FIELDS_TO_COLLECT:
				out_row.append(self.legislator_metadata[bioguide_id][field])

			writer.writerow(out_row)


