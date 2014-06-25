#!/bin/python

import argparse
import datetime
import legislativescorecard

def main(out_filename):
	print 'collecting legislators...'
	sc = legislativescorecard.LegislativeScorecard()	

	# sponsor/cosponsor of Surveillance State Repeal Act [hr2818-113] (+4)
	print 'checking sponsor/cosponsors of Surveillance State Repeal Act...'
	sc.cosponsored({'sponsor/cosponsor of Surveillance State Repeal Act': 4}, 'hr2818-113')	

	# sponsor/cosponsor of Senate version of USA FREEDOM [s1599-113] (+4)
	print 'checking sponsor/cosponsors of Senate version of USA FREEDOM...'
	sc.cosponsored({'sponsor/cosponsor of Senate version of USA FREEDOM': 4}, 's1599-113')

	# voted for House version of USA FREEDOM [hr3361-113](roll id: h230-2014) (-3)
	print 'checking votes on House version of USA FREEDOM...'
	sc.voted_for({'voted for House version of USA Freedom': -3}, ['h230-2014'])
	
	# sponsor/cosponsor of FISA Improvements Act [s1631-113] (-4)
	print 'checking sponsor/cosponsors of FISA Improvements Act...'
	sc.cosponsored({'sponsor/cosponsor of FISA Improvements Act': -4}, 's1631-113')

	# cosponsored House version of USA Freedom on or before 5/18/2014 (+4)
	print 'checking sponsor/cosponsors of USA FREEDOM prior to 2014-05-18...'
	cosponsorship_cutoff_date = datetime.datetime(2014, 5, 18)
	sc.cosponsored({'sponsor/cosponsor of USA FREEDOM prior to 2014-05-18': 4}, 'hr3361-113', lambda x: datetime.datetime.strptime(x['sponsored_on'], '%Y-%m-%d') <= cosponsorship_cutoff_date)	

	# Conyers-Amash Amendment amendment: [hamdt413-113] vote: [h412-2013] (vote +4)
	print 'checking votes on Conyers/Amash amendment...'
	sc.voted_for({'voted for Conyers/Amash amendment': 4}, ['h412-2013'])

	# sponsor/cosponsor of FISA Transparency & Modernization Act (Rogers/MI) [hr4291-113] (cosponsor -4)
	print 'checking sponsor/cosponsors of FISA Transparency & Modernization Act (Rogers bill)...'
	sc.cosponsored({'sponsor/cosponsor of FISA Transparency & Modernization Act': -4}, 'hr4291-113')	

	# # Reauthorizing Section 215 of the Patriot Act (vote(?) -.5)
	# print 'checking votes on USA PATRIOT section 215 reauthorization...'
	# sc.voted_for({'voted for reauthorization of USA PATRIOT section 215': -0.5}, ['s19-2011', 'h36-2011'])

	# # Voted to reauthorize FISA Amendments Act [hr5949-112] roll IDS [s236-2012, h569-2012] (vote(?) -.5)
	# print 'checking votes on reauthorization of FISA Amendments Act...'
	# sc.voted_for({'voted for reauthorization of FISA Amendments Act': -0.5}, ['s236-2012', 'h569-2012'])

	# voted for Massie-Lofgren amendment
	print 'checking votes on Massie-Lofgren amendment...'
	sc.voted_for({'voted for Massie-Lofgren amendment': 3}, ['h327-2014'])

	# # sponsor/cosponsor of FISA Court Reform Act
	# print 'checking sponsor/cosponsors of FISA Court Reform Act...'
	# sc.cosponsored({'sponsor/cosponsor of FISA Court Reform Act': 2}, 's1467-113')

	# # sponsor/cosponsor of Surveillance Transparency Act of 2013
	# print 'checking sponsor/cosponsors of Surveillance Transparency Act of 2013...'
	# sc.cosponsored({'sponsor/cosponsor of Surveillance Transparency Act of 2013': 1}, 's1452-113')

	print 'writing results...'
	f = open(out_filename, 'w')
	sc.write(f)
	f.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate legislators\'s scores based on a bunch of digital civil liberties votes/actions.')
	parser.add_argument('outfile', metavar='F', type=str, help='filename to write output to')
	args = parser.parse_args()    
	
	main(args.outfile)