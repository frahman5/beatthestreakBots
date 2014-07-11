from selectfunctions import todaysTopPBatters
from datetime import datetime

players = todaysTopPBatters(p=2, today=datetime.today(), filt={'minERA':2.5})
print players
