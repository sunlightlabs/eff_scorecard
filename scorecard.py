import unicodecsv
import argparse
import datetime
from sunlight import congress

class Scorecard(object):
	""" Helper class to assemble legislative scorecards """
	
	FIELDS_TO_COLLECT = ['title','first_name','last_name','party','state','district','twitter_id','youtube_id','facebook_id']

	def __init__(self):
		super(Scorecard, self).__init__()
		
		self.representatives = []
		self.senators = []   
		self.scores = {}

		self.legislator_metadata = {}

		# grab bioguides
		for (varname, chamber) in ((self.senators, 'senate'), (self.representatives, 'house')):
			i = 0
			while True:
				new_reps = congress.legislators(chamber=chamber, fields=','.join(['bioguide_id',] + Scorecard.FIELDS_TO_COLLECT), page=i)
				if new_reps is None:
					break
				for nr in new_reps:
					bioguide = nr['bioguide_id']
					varname.append(bioguide)

					self.legislator_metadata[bioguide] = {}
					for k in Scorecard.FIELDS_TO_COLLECT:
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
				print votes[0]['voters'].get(legislator, {'vote': 'not present in data'})['vote']
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

		writer.writerow(['bioguide_id'] + fields_to_emit + ['total'] + Scorecard.FIELDS_TO_COLLECT)

		# tabulate data
		for bioguide_id in sorted(self.scores):
			out_row = [bioguide_id]
			total = 0
			for field in fields_to_emit:
				value = self.scores[bioguide_id].get(field, 0)
				out_row.append(value)
				total = total + value

			out_row.append(total)
			
			for field in Scorecard.FIELDS_TO_COLLECT:
				out_row.append(self.legislator_metadata[bioguide_id][field])

			writer.writerow(out_row)


def main(out_filename):
	print 'collecting legislators...'
	sc = Scorecard()	

	# sponsor/cosponsor of Surveillance State Repeal Act [hr2818-113] (+4)
	print 'checking sponsor/cosponsors of Surveillance State Repeal Act...'
	sc.cosponsored({'sponsor/cosponsor of Surveillance State Repeal Act': 4}, 'hr2818-113')	

	# sponsor/cosponsor of Senate version of USA FREEDOM [s1599-113] (+4)
	print 'checking sponsor/cosponsors of Senate version of USA FREEDOM...'
	sc.cosponsored({'sponsor/cosponsor of Senate version of USA FREEDOM': 4}, 's1599-113')

	# voted for House version of USA FREEDOM [hr3361-113](roll id: h230-2014) (-3)
	print 'checking votes on House version of USA FREEDOM...'
	sc.voted_aye({'voted for House version of USA Freedom': -3}, ['h230-2014'])
	
	# sponsor/cosponsor of FISA Improvements Act [s1631-113] (-4)
	print 'checking sponsor/cosponsors of FISA Improvements Act...'
	sc.cosponsored({'sponsor/cosponsor of FISA Improvements Act': -4}, 's1631-113')

	# cosponsored House version of USA Freedom on or before 5/18/2014 (+3)
	print 'checking sponsor/cosponsors of USA FREEDOM prior to 2014-05-18...'
	cosponsorship_cutoff_date = datetime.datetime(2014, 5, 18)
	sc.cosponsored({'sponsor/cosponsor of USA FREEDOM prior to 2014-05-18': 3}, 'hr3361-113', lambda x: datetime.datetime.strptime(x['sponsored_on'], '%Y-%m-%d') <= cosponsorship_cutoff_date)	

	# Conyers-Amash Amendment amendment: [hamdt413-113] vote: [h412-2013] (vote +4)
	print 'checking votes on Conyers/Amash amendment...'
	sc.voted_aye({'voted for Conyers/Amash amendment': 4}, ['h412-2013'])

	# sponsor/cosponsor of FISA Transparency & Modernization Act (Rogers/MI) [hr4291-113] (cosponsor -4)
	print 'checking sponsor/cosponsors of FISA Transparency & Modernization Act (Rogers bill)...'
	sc.cosponsored({'sponsor/cosponsor of FISA Transparency & Modernization Act': -4}, 'hr4291-113')	

	# Reauthorizing Section 215 of the Patriot Act (vote(?) -.5)
	print 'checking votes on USA PATRIOT section 215 reauthorization...'
	sc.voted_aye({'voted for reauthorization of USA PATRIOT section 215': -0.5}, ['s19-2011', 'h36-2011'])

	# Voted to reauthorize FISA Amendments Act [hr5949-112] roll IDS [s236-2012, h569-2012] (vote(?) -.5)
	print 'checking votes on reauthorization of FISA Amendments Act...'
	sc.voted_aye({'voted for reauthorization of FISA Amendments Act': -0.5}, ['s236-2012', 'h569-2012'])

	# voted for Massie-Lofgren amendment
	# print 'checking votes on Massie-Lofgren amendment...'
	# sc.voted_aye({'voted for Massie-Lofgren amendment': 0.5}, ['h327-2014'])

	print 'writing results...'
	f = open(out_filename, 'w')
	sc.write(f)
	f.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate legislators\'s scores based on a bunch of digital civil liberties votes/actions.')
	parser.add_argument('outfile', metavar='F', type=str, help='filename to write output to')
	args = parser.parse_args()    
	
	main(args.outfile)