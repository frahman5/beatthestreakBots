import datetime
import unittest

from beatthestreakBots.selectfunctions import todaysTopPBatters
class TestBot(unittest.TestCase):

    def test_todaysTopPBatters(self):
        # Test only works on Jul 10th, 2014. Need to change
        # answers for other dates

        ## Get the top 10 and 20 playres on July 10th, by batting average
        top10 = [
                  ('Troy', 'Tulowitzki', 'col'),
                  ('Jose', 'Altuve', 'hou'), 
                  ('Matt', 'Adams', 'stl'),
                  ('Adrian', 'Beltre', 'tex'),
                  ('Victor', 'Martinez', 'det'),
                  ('Jonathan', 'Lucroy', 'mil'),
                  ('Michael', 'Brantley', 'cle'),
                  ('Lonnie', 'Chisenhall', 'cle'),
                  ('Robinson', 'Cano', 'sea'),
                  ('Casey', 'McGehee', 'mia')
                ]
        top11_20 = [
                     ('Andrew', 'McCutchen', 'pit'),
                     ('Justin', 'Morneau', 'col'),
                     ('Paul', 'Goldschmidt', 'ari'),
                     ('Miguel', 'Cabrera', 'det'),
                     ('Yasiel', 'Puig', 'lad'), 
                     ('Scooter', 'Gennett', 'mil'),
                     ('Adam', 'Jones', 'bal'),
                     ('Ian', 'Kinsler', 'det'),
                     ('Kurt', 'Suzuki', 'min'),
                     ('Alex', 'Rios', 'tex')
                   ]
        top20 = [player for player in top10]
        top20.extend(top11_20)

        ## Sort out players by opposing pitcher ERA and whether or not they're starting today
        Troy, Jose, Matt, Adrian, Victor, Jonathan, Michael, Lonnie, Robinson, Casey = top10
        Andrew, Justin, Paul, Miguel, Yasiel, Scooter, Adam, Ian, Kurt, Alex = top11_20
        for player in (Troy, Jose, Casey): # not starting on July 10, 2014
            top10.remove(player)
        top10_3 = top10
        
        for player in (Troy, Jose, Casey, Justin, Paul): # not starting on July 10, 2014
            top20.remove(player)
        for player in (Matt, Yasiel, Adam, Kurt): # pitchers have ERA below 4
            top20.remove(player)
        top20_4 = top20

        ## Run tests
        today = datetime.datetime.today().date()
        import pdb
        pdb.set_trace()
        self.assertEqual( todaysTopPBatters( p=10, 
                                            today=today, 
                                            filt={'minEra':3.0}), 
                          top10_3 )
        self.assertEqual( todaysTopPBatters( p=20,
                                            today=today,
                                            filt={'minERA':4.0}),
                          top20_4)