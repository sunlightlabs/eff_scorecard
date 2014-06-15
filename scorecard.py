import unicodecsv
import argparse
from sunlight import congress

def main(outfile):

    representatives = []
    senators = []   
    scores = {}

    legislator_metadata = {}

    fields_to_collect = ['title','first_name','last_name','party','state','district','twitter_id','youtube_id','facebook_id']

    # grab bioguides
    print 'Collecting legislators...'
    for (varname, chamber) in ((senators, 'senate'), (representatives, 'house')):
        i = 0
        while True:
            new_reps = congress.legislators(chamber=chamber, fields=','.join(['bioguide_id',] + fields_to_collect), page=i)
            if new_reps is None:
                break
            for nr in new_reps:
                bioguide = nr.get('bioguide_id')
                varname.append(bioguide)

                legislator_metadata[bioguide] = {}
                for k in fields_to_collect:
                    legislator_metadata[bioguide][k] = nr.get(k)

            i = i + 1
    
    # initialize scores dict
    for legislator in representatives + senators:
        scores[legislator] = {} 


    # sponsor/cosponsor of Surveillance State Repeal Act [hr2818-113] (+4)
    print 'checking sponsor/cosponsors of Surveillance State Repeal Act...'
    bill = congress.bills(bill_id='hr2818-113', fields='cosponsor_ids,sponsor_id')[0]
    sponsor_and_cosponsors_ids = bill.get('cosponsor_ids') + [bill.get('sponsor_id')]
    
    for legislator in scores:
        score = 0
        if legislator in sponsor_and_cosponsors_ids:
            score = 4
        scores[legislator]['sponsor/cosponsor of Surveillance State Repeal Act (+4)'] = score


    # sponsor/cosponsor of Senate version of USA FREEDOM [s1599-113] (+4)
    print 'checking sponsor/cosponsors of Senate version of USA FREEDOM...'
    bill = congress.bills(bill_id='s1599-113', fields='cosponsor_ids,sponsor_id')[0]
    sponsor_and_cosponsors_ids = bill.get('cosponsor_ids') + [bill.get('sponsor_id')]
    
    for legislator in scores:
        score = 0
        if legislator in sponsor_and_cosponsors_ids:
            score = 4
        scores[legislator]['sponsor/cosponsor of Senate version of USA FREEDOM (+4)'] = score


    # voted for House version of USA FREEDOM [hr3361-113] (-3)
    print 'checking votes on House version of USA FREEDOM...'
    votes = congress.votes(bill_id='hr3361-113', fields='voters')
    for legislator in scores:
        score = 0        
        if votes[0]['voters'].get('legislator', {}).get('vote') == 'Aye':
            score = -3
        scores[legislator]['voted for House version of USA Freedom (-3)'] = score

    
    # sponsor/cosponsor of FISA Improvements Act [s1631-113] (-4)
    print 'checking sponsor/cosponsors of FISA Improvements Act...'
    bill = congress.bills(bill_id='s1631-113', fields='cosponsor_ids,sponsor_id')[0]
    sponsor_and_cosponsors_ids = bill.get('cosponsor_ids') + [bill.get('sponsor_id')]
    
    for legislator in scores:
        score = 0
        if legislator in sponsor_and_cosponsors_ids:
            score = -4
        scores[legislator]['sponsor/cosponsor of FISA Improvements Act (-4)'] = score


    # cosponsored House version of USA Freedom on or before 5/18/2014 (+3)
    # TODO: resolve bug related to sponsorships field not coming back
    # sponsorships = congress.bills(bill_id='hr3361-113', fields='sponsorships')


    # Conyers-Amash Amendment amendment: [hamdt413-113] vote: [h412-2013] (vote +4)
    print 'checking votes on Conyers/Amash amendment...'
    votes = congress.votes(roll_id='h412-2013', fields='voters')
    for legislator in scores:
        score = 0
        if votes[0]['voters'].get('legislator', {}).get('vote') == 'Aye':
            score = 4
        scores[legislator]['voted for Conyers/Amash amendment (+4)'] = score


    # sponsor/cosponsor of FISA Transparency & Modernization Act (Rogers/MI) [hr4291-113] (cosponsor -4)
    print 'checking sponsor/cosponsors of FISA Transparency & Modernization Act (Rogers bill)...'
    bill = congress.bills(bill_id='hr4291-113', fields='cosponsor_ids,sponsor_id')[0]
    sponsor_and_cosponsors_ids = bill.get('cosponsor_ids') + [bill.get('sponsor_id')]
    
    for legislator in scores:
        score = 0
        if legislator in sponsor_and_cosponsors_ids:
            score = -4
        scores[legislator]['sponsor/cosponsor of FISA Transparency & Modernization Act (-4)'] = score



    # Reauthorizing Section 215 of the Patriot Act (vote(?) -.5)
    # TODO: figure out which vote(s) are relevant
    

    # Voted to reauthorize FISA Amendments Act [hr5949-112] roll IDS [s236-2012, h569-2012] (vote(?) -.5)
    print 'checking votes on reauthorization of FISA Amendments Act...'
    for roll_id in ('s236-2012', 'h569-2012'):
        votes = congress.votes(roll_id=roll_id, fields='voters')
        for legislator in scores:
            score = 0
            if votes[0]['voters'].get('legislator', {}).get('vote') == 'Aye':
                score = -3
            scores[legislator]['voted for reauthorization of FISA Amendments Act (-0.5)'] = score

    print 'Writing file...'
    f = open(outfile, 'w')
    writer = unicodecsv.writer(f)
    
    # figure out what we've actually recorded here
    fields_to_emit = {}
    for l in scores:
        for k in scores[l]:
            fields_to_emit[k] = True
    fields_to_emit = sorted(fields_to_emit.keys())

    writer.writerow(['bioguide_id'] + fields_to_emit + ['total'] + fields_to_collect)

    # tabulate data
    for bioguide_id in scores:
        out_row = [bioguide_id]
        total = 0
        for field in fields_to_emit:
            value = scores[bioguide_id].get(field, 0)
            out_row.append(value)
            total = total + value

        out_row.append(total)
        
        for field in fields_to_collect:
            out_row.append(legislator_metadata[bioguide_id][field])

        writer.writerow(out_row)

    f.close()

    print 'Done.'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate legislators\'s scores based on a bunch of digital civil liberties votes/actions.')
    parser.add_argument('outfile', metavar='F', type=str, help='filename to write output to')
    args = parser.parse_args()    
    main(args.outfile)