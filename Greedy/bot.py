import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0
reserved_points = []
undef = 99

# PROGRAM UTAMA 
def main(player_key):
	global map_size
	global undef
	# Membaca file eksternal
	with open(os.path.join(output_path, game_state_file), 'r') as f_in:
		state = json.load(f_in)
	map_size = state['MapDimension']

	# Mendapatkan nilai STATE dari permainan
	if state['Phase'] == 1:
		place_ships()	# Meletakkan kapal-kapal
	else:
		opponent_map = state['OpponentMap']['Cells']
		player_own = state['PlayerMap']['Owner']
		# Periksa apakah memerlukan strategi bertahan
		current_charge = player_own['Shield']['CurrentCharges']
		if (is_battleship_hit(player_own) and (current_charge>0) and is_battleship_active(player_own)) :
			defence_mode(player_own)
			return	
		for cell in opponent_map:	# Pengulangan GREEDY dengan memastikan kapal harus tenggelam
			if (cell['Damaged']):	# saat salah satu bagian dari kapal tersebut sudah DAMAGED
				x,y = is_sunk(cell['X'], cell['Y'], state)
				if (is_on_map(x,y,map_size)):
					output_shot(x,y,player_own, False)
					return
		hunting(opponent_map, player_own)	# Perintah yang dilakukan saat tidak ada DAMAGED
											# atau kapal yang DAMAGED sudah dipastikan tenggelam

def is_battleship_active(player_own):
	# I.S 	: Semua parameter terdefinisi
	# F.S 	: RETURN TRUE jika Battleship masih aktif, RETURN FALSE jika sebaliknya
	Ships = player_own['Ships']
	for ship in Ships :
		if (ship['ShipType']=="Battleship") :
			if (ship['Destroyed']) :
				return False
			else :
				return True

def is_battleship_hit(player_own):
	# I.S 	: Semua parameter terdefinisi
	# F.S 	: RETURN TRUE jika Battleship terkena HIT, RETURN FALSE jika sebaliknya
	print('Masuk is_battle_ship')
	Ships = player_own['Ships']
	for ship in Ships:
		if (ship['ShipType'] == "Battleship"):
			print('masuk battleship')
			cells = ship['Cells']
			for cell in cells:
				if (cell['Hit']) :
					return True
	return False

def defence_mode(player_own):
	# I.S 	: Semua parameter terdefinisi
	# F.S 	: Menulis perintah Shield di COMMAND.TXT
	Ships = player_own['Ships']
	for ship in Ships :
		if (ship['ShipType']=="Battleship"):
			cell = ship['Cells']
			hit = False
			i = 0
			while (i<4 and not hit):
				if (cell[i]['Hit']) :
					if (not cell[(i+1)%4]['Hit']) :
						x = cell[i+1]['X']
						y = cell[i+1]['Y']
						hit = True
					elif (not cell[(i-1)%4]['Hit']):
						x = cell[i-1]['X']
						y = cell[i-1]['Y']
						hit = True
					else :
						i += 1
				else :
					i += 1
	with open(os.path.join(output_path, command_file), 'w') as f_out:
		f_out.write('{},{},{}'.format(8, x, y))
		f_out.write('\n')
	pass

def energy_required(map_size):
	# I.S 	: Semua parameter terdefinisi
	# F.S 	: RETURN 30 jika Small Map, RETURN 40 jika Medium Map, dan RETURN 55 jika Large Map
	if (map_size == 7):
		return 30
	elif (map_size == 10):
		return 40
	else:
		return 55

def is_on_map(x,y,map_size):
	# I.S 	: Semua parameter terdefinisi
	# F.S 	: RETURN TRUE jika koordinat x,y terdefinisi di peta, RETURN FALSE jika tidak terdefinisi
	return (x>=0 and x<map_size and y>=0 and y<map_size)

def is_sunk(x,y,state):
	# I.S		: Semua parameter terdefinisi
	# F.S		: RETURN POINT(X,Y) jika terdefinisi atau RETURN UNDEF jika tidak terdefinisi
	# METODE	: Pertama, titik DAMAGED tersebut diperiksa apakah bagian atas dan bawahnya sudah DAMAGED, jika iya, maka
	#			  kapal tersebut pasti vertikal, jika tidak, diperiksa bagian kanan dan kirinya sudah DAMAGED, jika iya, maka
	#			  kapal tersebut pasti horizontal, tidak mungkin keduanya.
	#			  Selanjutnya, perintah menjalankan pencarian untuk menemukan target lokasi SHOT selanjutnya. Namun, target tersebut
	#			  bernilai UNDEF saat titik-titik DAMAGED terluar sudah dibatasi oleh titik MISSED
	global undef
	opponent_map = state['OpponentMap']['Cells']
	map_size = state['MapDimension']
	if (is_on_map(x+1,y,map_size)):
		cell1 = opponent_map[(x+1)*10+y]['Damaged']
	else:
		cell1 = False
	if (is_on_map(x-1,y,map_size)):
		cell2 = opponent_map[(x-1)*10+y]['Damaged']
	else:
		cell2 = False
	if (is_on_map(x,y+1,map_size)):
		cell3 = opponent_map[(x)*10+(y+1)]['Damaged']
	else:
		cell3 = False
	if (is_on_map(x,y-1,map_size)):
		cell4 = opponent_map[(x)*10+(y-1)]['Damaged']
	else:
		cell4 = False

	if (cell1 or cell2):
		i, j = check_horizontal(x, y, opponent_map, map_size)
		if (is_on_map(i,j,map_size)):
			return i,j
	elif (cell3 or cell4):
		i, j = check_vertical(x,y,opponent_map, map_size)
		if (is_on_map(i,j,map_size)):
			return i,j
	else:    
		i, j = check_vertical(x,y,opponent_map, map_size)
		if (is_on_map(i,j,map_size)):
			return i,j
		else:
			i, j = check_horizontal(x, y, opponent_map, map_size)
			if (is_on_map(i,j,map_size)):
				return i,j
	return undef,undef

def check_vertical(x, y, opponent_map, map_size):
	# I.S		: Semua parameter terdefinisi
	# F.S		: RETURN POINT (X,Y), jika terdefinisi dan RETURN UNDEF jika tidak terdefinisi
	# METODE	: Pertama, periksa bagian atas apakah bernilai MISSED/DAMAGED/NONE. Jika MISSED, maka dilanjutkan dengan
	#			  pencarian bagian bawah dengan memeriksa blok-blok tersebut bernilai MISSED/DAMAGED/NONE.
	#			  Kondisi :
	#			    - Jika pencarian atas MISSED dan pencarian bawah MISSED, maka RETURN UNDEF
	#				- Jika pencarian atas/bawah DAMAGED, maka lanjut ke blok-blok berikutnya, hingga ditemukan MISSED atau NONE
	#				- Jika pencarian ditemukan NONE, maka blok pertama yang ditemukan akan menjadi target SHOT berikutnya
	global undef
	j = y-1
	fail_top = False
	while (is_on_map(x, j, map_size) and not (fail_top)):
		idx = x*10+j
		if (opponent_map[idx]['Missed']):
			fail_top = True
		elif not (opponent_map[idx]['Damaged']):
			return (x,j)
		else:
			j -= 1
	if not (is_on_map(x, j, map_size)):
		fail_top=True

	j = y+1
	fail_bottom = False
	while (is_on_map(x, j, map_size) and not (fail_bottom)):
		idx = x*10+j
		if (opponent_map[idx]['Missed']):
			fail_bottom = True
		elif not (opponent_map[idx]['Damaged']):
			return (x,j)
		else:
			j += 1
	if not (is_on_map(x, j, map_size)):
		fail_bottom=True

	if (fail_top and fail_bottom):
		return undef,undef

def check_horizontal(x, y, opponent_map, map_size):
	# I.S		: Semua parameter terdefinisi
	# F.S		: RETURN POINT (X,Y), jika terdefinisi dan RETURN UNDEF jika tidak terdefinisi
	# METODE	: Pertama, periksa bagian kanan apakah bernilai MISSED/DAMAGED/NONE. Jika MISSED, maka dilanjutkan dengan
	#			  pencarian bagian kiri dengan memeriksa blok-blok tersebut bernilai MISSED/DAMAGED/NONE.
	#			  Kondisi :
	#			    - Jika pencarian kanan MISSED dan pencarian kiri MISSED, maka RETURN UNDEF
	#				- Jika pencarian kanan/kiri DAMAGED, maka lanjut ke blok-blok berikutnya, hingga ditemukan MISSED atau NONE
	#				- Jika pencarian ditemukan NONE, maka blok pertama yang ditemukan akan menjadi target SHOT berikutnya
	global undef
	i = x+1
	fail_right = False
	while (is_on_map(i, y, map_size) and not fail_right):
		idx = i*10+y
		if (opponent_map[idx]['Missed']):
			fail_right = True
		elif not (opponent_map[idx]['Damaged']):
			return (i,y)
		else:
			i += 1
	if not (is_on_map(i, y, map_size)):
		fail_right=True

	i=x-1
	fail_left = False
	while (is_on_map(i, y, map_size) and not fail_left):
		idx = i*10+y
		if (opponent_map[idx]['Missed']):
			fail_left = True
		elif not (opponent_map[idx]['Damaged']):
			return (i,y)
		else:
			i -= 1
	if not (is_on_map(i, y, map_size)):
		fail_left=True

	if (fail_right and fail_left):
		return undef,undef

def hunting(opponent_map,player_own):
	# I.S		: Semua parameter terdefinisi
	# F.S		: RETURN POINT (X,Y) jika terdefinisi, RETURN UNDEF jika tidak
	# METODE	: Pertama, energi diperiksa apakah memenuhi untuk menembak dengan RESERVED_POINTS. Jika iya, maka titik yang merupakan
	#			  anggota dari RESERVED_POINTS yang akan menjadi target SHOT selanjutnya. 
	# 			  Jika tidak maka dilakukan pencarian dengan mencari seluruh titik yang tidak DAMAGED atau MISSED dan memenuhi
	#			  (x+y%2 = 1). Selanjutnya, dari sekumpulan titik tersebut akan dipilih satu titik yang akan menjadi kandidat
	#			  target SHOT selanjutnya. Kandidat target tersebut diperiksa untuk memastikan titik tersebut tidak termasuk dalam
	#			  RESERVED_POINTS yang hanya boleh ditembak dengan menggunakan senjata CORNER SHOT. Jika iya, maka akan dilakukan pengulangan
	#			  hingga menemukan titik yang bukan anggota dari himpunan RESERVED POINTS.
	global map_size
	reserved_points = [(2,3), (map_size-3, 3)]
	energy = player_own['Energy']
	targets = []
	if (energy >= energy_required(map_size) and is_battleship_active(player_own)):
		target = choice(reserved_points)
	else :
		for cell in opponent_map:
			oddity = (cell['X']+cell['Y']) % 2
			if not (cell['Damaged'] or cell['Missed']) and oddity:
				if (is_battleship_active(player_own)) :
					if not (((cell['X'] >= 1 and cell['X'] <= 3) and (cell['Y'] >= 2 and cell['Y'] <= 4)) or ((cell['X'] >= map_size-3 and cell['X'] <= map_size-1) and (cell['Y'] >= 2 and cell['Y'] <= 4))):
						valid_cell = cell['X'], cell['Y']
						targets.append(valid_cell)
				else :
					valid_cell = cell['X'], cell['Y']
					targets.append(valid_cell)
		target = choice(targets)
	output_shot(*target, player_own, True)
	return

def output_shot(x, y, player_own, type):
# I.S		: Semua parameter terdefinisi
# F.S		: Perintah di COMMAND.TXT tertulis
# METODE	: Jika energi cukup untuk melakukan CORNER SHOT, maka gunakan CORNER SHOT dengan terlebih dahulu melakukan 
# 			  pemeriksaan syarat-syarat dalam menggunakan jenis senjata tersebut. Jika tidak maka gunakan FIRE SHOT
	energy = player_own['Energy']
	ships = player_own['Ships']
	move = 1
	if (energy >= energy_required(map_size) and type):
		for ship in ships:
			if (ship['ShipType'] == "Battleship" and not ship['Destroyed']):
				move = 5  # Cross Shot Diagonal
				break
	with open(os.path.join(output_path, command_file), 'w') as f_out:
		f_out.write('{},{},{}'.format(move, x, y))
		f_out.write('\n')
	pass

def place_ships():
# I.S		: Semua parameter terdefinisi
# F.S		: Titik-titik lokasi kapal-kapal tertulis
	ships = ['Battleship 1 3 north',
			 'Carrier 3 0 East',
			 'Cruiser 6 3 north',
			 'Destroyer 9 5 north',
			 'Submarine 4 8 East'
			 ]

	with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
		for ship in ships:
			f_out.write(ship)
			f_out.write('\n')
	return

#KONFIGURASI ENVIRONMENT
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('PlayerKey', nargs='?',
						help='Player key registered in the game')
	parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(
	), help='Directory for the current game files')
	args = parser.parse_args()
	assert (os.path.isdir(args.WorkingDirectory))
	output_path = args.WorkingDirectory
	main(args.PlayerKey)
