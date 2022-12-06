from urllib.request import urlopen
from bs4 import BeautifulSoup

# Import data manipulation modules
import pandas as pd
import numpy as np
# Import data visualization modules
import matplotlib as mpl
import matplotlib.pyplot as plt


team_colors = {'ARI':'#97233f', 'ATL':'#a71930', 'BAL':'#241773', 'BUF':'#00338d', 'CAR':'#0085ca', 'CHI':'#0b162a', 'CIN':'#fb4f14', 'CLE':'#311d00', 'DAL':'#041e42', 'DEN':'#002244', 'DET':'#0076b6', 'GNB':'#203731', 'HOU':'#03202f', 'IND':'#002c5f', 'JAX':'#006778', 'KAN':'#e31837', 'LAC':'#002a5e','LAR':'#003594', 'LVR':'#003594', 'MIA':'#008e97', 'MIN':'#4f2683', 'NWE':'#002244', 'NOR':'#d3bc8d', 'NYG':'#0b2265', 'NYJ':'#125740', 'OAK':'#000000', 'PHI':'#004c54', 'PIT':'#ffb612', 'SFO':'#aa0000', 'SEA':'#002244', 'TAM':'#d50a0a', 'TEN':'#0c2340', 'WAS':'#773141'}

url = 'https://www.pro-football-reference.com/years/2022/scrimmage.htm'

html = urlopen(url)
stats_page = BeautifulSoup(html, 'html.parser')

column_headers = stats_page.findAll('tr')[1]
column_headers = [i.getText() for i in column_headers.findAll('th')]

# print(column_headers)


# Collect table rows
rows = stats_page.findAll('tr')[2:]

plr_stats = []
for i in range(len(rows)):
  plr_stats.append([col.getText() for col in rows[i].findAll('td')])

# print(plr_stats[0])

data = pd.DataFrame(plr_stats, columns=column_headers[1:])

# print(data.head())
# print(data.columns)



new_columns = data.columns.values
new_columns[8] = 'ReYds'
new_columns[10] = 'ReTD'
new_columns[11] = 'Re1D'
new_columns[12] = 'ReLng'
new_columns[13] = 'Re/G'
new_columns[14] = 'ReY/G'
new_columns[18] = 'RuYds'
new_columns[19] = 'RuTD'
new_columns[20] = 'Ru1D'
new_columns[21] = 'RuLng'
new_columns[23] = 'RuY/G'

# print(data.columns)

categories = ['G', 'Touch', 'YScm', 'RRTD', 'Fmb']

data_radar = data[['Player', 'Tm'] + categories]
data_radar.fillna(0)
data_radar.replace(np.nan, 0)




for i in categories:
    data_radar[i] = pd.to_numeric(data[i])

data_radar["FP"] = (data_radar["YScm"] / 10) + (data_radar["RRTD"] * 6) - (data_radar["Fmb"] * 2)
print(data_radar.head())

# print(data_radar.dtypes)

data_radar_filtered = data_radar[data_radar['YScm'] > 500]
# print(data_radar_filtered)

for i in categories:
    data_radar_filtered[i + '_Rank'] = data_radar_filtered[i].rank(pct=True)

data_radar_filtered['Fmb_Rank'] = 1 - data_radar_filtered['Fmb_Rank']
# print(data_radar_filtered.head())


# General plot parameters
mpl.rcParams['font.family'] = 'Avenir'
mpl.rcParams['font.size'] = 16
mpl.rcParams['axes.linewidth'] = 0
mpl.rcParams['xtick.major.pad'] = 15


# Calculate angles for radar chart
offset = np.pi/6
angles = np.linspace(0, 2*np.pi, len(categories) + 1) + offset

def create_radar_chart(ax, angles, player_data, color='blue'):
    
    # Plot data and fill with team color
    ax.plot(angles, np.append(player_data[-(len(angles)-1):], 
            player_data[-(len(angles)-1)]), color=color, linewidth=2)
    ax.fill(angles, np.append(player_data[-(len(angles)-1):], 
            player_data[-(len(angles)-1)]), color=color, alpha=0.2)
    
    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    
    # Remove radial labels
    ax.set_yticklabels([])

    # Add player name
    ax.text(np.pi/2, 1.7, player_data[0], ha='center', va='center', 
            size=18, color=color)
    
    # Use white grid
    ax.grid(color='white', linewidth=1.5)

    # Set axis limits
    ax.set(xlim=(0, 2*np.pi), ylim=(0, 1))

    return ax

    # Function to get QB data
def get_plr_data(data, team):
  return np.asarray(data[data['Tm'] == team])[0]


  # Create figure
fig = plt.figure(figsize=(8, 8), facecolor='white')
# Add subplots
ax1 = fig.add_subplot(221, projection='polar', facecolor='#ededed')
ax2 = fig.add_subplot(222, projection='polar', facecolor='#ededed')
ax3 = fig.add_subplot(223, projection='polar', facecolor='#ededed')
ax4 = fig.add_subplot(224, projection='polar', facecolor='#ededed')
# Adjust space between subplots
plt.subplots_adjust(hspace=0.8, wspace=0.5)
# Get QB data
cin_data = get_plr_data(data_radar_filtered, 'CIN')
mia_data = get_plr_data(data_radar_filtered, 'MIA')
lac_data = get_plr_data(data_radar_filtered, 'LAC')
gnb_data = get_plr_data(data_radar_filtered, 'GNB')
# Plot QB data
ax1 = create_radar_chart(ax1, angles, cin_data, team_colors['CIN'])
ax2 = create_radar_chart(ax2, angles, mia_data, team_colors['MIA'])
ax3 = create_radar_chart(ax3, angles, lac_data, team_colors['LAC'])
ax4 = create_radar_chart(ax4, angles, gnb_data, team_colors['GNB'])
plt.show()