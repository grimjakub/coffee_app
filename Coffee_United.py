import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import RegularGridInterpolator


def Values(db_data, user, prop):
	users = []
	for dictionary in db_data:
		if dictionary['user'] not in users:
			users.append(dictionary['user'])

	# Calculate unique occurrences:
	unique = []
	if user in users:
		for dictionary in db_data:
			if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] not in unique and dictionary['user'] == user:
				unique.append([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
	else:
		for dictionary in db_data:
			if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] not in unique:
				unique.append([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])

	vector = [[] for _ in users]
	for dictionary in db_data:
		if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] in [vector[users.index(dictionary['user'])][i][0:3] for i, _ in enumerate(vector[users.index(dictionary['user'])])]:
			i = [vector[users.index(dictionary['user'])][i][0:3] for i, _ in enumerate(vector[users.index(dictionary['user'])])].index([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
			vector[users.index(dictionary['user'])][i].append(dictionary[prop])
		else:
			vector[users.index(dictionary['user'])].append([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water'], dictionary[prop]])
	for p, _ in enumerate(users):
		for i, element in enumerate(vector[p]):
			sub_vector = element[0:3]
			sub_vector.append(sum(element[3:]) / len(element[3:]))
			vector[p][i] = sub_vector

	victor = []
	for p, _ in enumerate(users):
		for i, element in enumerate(vector[p]):
			if element[0:3] in [i[0:3] for i in victor]:
				index = [i[0:3] for i in victor].index(element[0:3])
				victor[index].append(element[3])
			else:
				victor.append(element.copy())

	for i, element in enumerate(victor):
		sub_vector = element[0:3]
		sub_vector.extend([sum(element[3:]) / len(element[3:]), len(element[3:])])
		victor[i] = sub_vector

	if user in users:
		for vec in vector[users.index(user)]:
			vec.append(1)
		vector = vector[users.index(user)]
	else:
		vector = victor

	# initilize 3D property and fullness
	property_0 = [[[0, 0, 0, 0, 0] for _ in range(4)] for _ in range(5)]
	fullness = [[[0, 0, 0, 0, 0] for _ in range(4)] for _ in range(5)]

	# fill in the known data
	for i in vector:
		property_0[int(i[0] - 1)][int(i[1] / 25 - 1)][int(i[2] / 25)] = i[3]
		fullness[int(i[0] - 1)][int(i[1] / 25 - 1)][int(i[2] / 25)] = i[4]

	prop = property_0.copy()
	for x_0 in range(5):
		for y_0 in range(4):
			for z_0 in range(5):
				if property_0[x_0][y_0][z_0] == 0:
					prop[x_0][y_0][z_0] = sum([fullness[x][y][z] * property_0[x][y][z] / ((x - x_0) ** 2 + (y - y_0) ** 2 + (z - z_0) ** 2) if (x != x_0 or y != y_0 or z != z_0) else 0 for x in range(5) for y in range(4) for z in range(5)]) / sum([fullness[x][y][z] / ((x - x_0) ** 2 + (y - y_0) ** 2 + (z - z_0) ** 2) if (x != x_0 or y != y_0 or z != z_0) else 0 for x in range(5) for y in range(4) for z in range(5)])

	# Continuous grid
	x_values = np.linspace(1, 5, 13)
	y_values = np.linspace(25, 100, 13)
	z_values = np.linspace(0, 100, 13)
	X, Y, Z = np.meshgrid(x_values, y_values, z_values)

	# Create mgrid
	X = np.transpose(X, [1, 0, 2])
	Y = np.transpose(Y, [1, 0, 2])
	Z = np.transpose(Z, [1, 0, 2])

	# Grid
	x = np.linspace(1, 5, 5)
	y = np.linspace(25, 100, 4)
	z = np.linspace(0, 100, 5)
	V = prop
	fn = RegularGridInterpolator((x, y, z), V)
	values = fn((X, Y, Z))

	return [values, X, Y, Z, vector, x_values, y_values, z_values]


def Unique(db_data, user):
	users = []
	for dictionary in db_data:
		if dictionary['user'] not in users:
			users.append(dictionary['user'])

	unique = []
	if user in users:
		for dictionary in db_data:
			if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] not in unique and dictionary['user'] == user:
				unique.append([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
	else:
		for dictionary in db_data:
			if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] not in unique:
				unique.append([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
	return len(unique)


def Graph_3D(db_data, user, prop):
	values, X, Y, Z, vector, x_values, y_values, z_values = Values(db_data, user, prop)
	fig = go.Figure()
	for i in np.linspace(0, 40, 11):
		fig.add_trace(
			go.Isosurface(
				x=X.flatten(),
				y=Y.flatten(),
				z=Z.flatten(),
				value=values.flatten(),
				isomin=i / 10 + 1,
				opacity=i / 80,
				caps=dict(x_show=False, y_show=False, z_show=False),
				cmin=1,
				cmax=5,
				colorscale='blackbody',
				hoverinfo='skip',
				colorbar_tickfont_color='white',
			)
		)

	if len(vector) < 100:
		fig.add_trace(go.Scatter3d(
			x=[i[0] for i in vector], y=[i[1] for i in vector], z=[i[2] for i in vector],
			mode='markers', marker=dict(color='black'), hovertemplate='Coffee: %{x}<br>Coffee water: %{y}<br>Water: %{z}<extra></extra>')
		)

	fig.update_scenes(
		xaxis=dict(range=[0.8, 5.2], nticks=5, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)", ticks='outside', title='Coffee'),
		yaxis=dict(range=[21, 104], dtick=25, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)", ticks='outside', title='Coffee water'),
		zaxis=dict(range=[-5, 105], dtick=25, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)", ticks='outside', title='Water'),
	)

	fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#6f4e37", scene_camera_eye=dict(x=1.5, y=1.5, z=1))
	return fig


def Graph_2D_Coffee(db_data, user, prop):
	values, X, Y, Z, vector, x_values, y_values, z_values = Values(db_data, user, prop)
	fig2D_Coffee_list = []
	for coffee in [1, 2, 3, 4, 5]:
		values2D = np.array(values)[int(3 * (coffee - 1)), :, :]
		fig2D_Coffee = go.Figure()
		fig2D_Coffee.add_trace(go.Contour(
			x=y_values,
			y=z_values,
			z=values2D,
			colorscale='blackbody',
			contours=dict(start=1, end=5, size=0.1),
			contours_coloring='heatmap',
			colorbar_tickfont_color='white',
		)
		)
		fig2D_Coffee.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#6f4e37", plot_bgcolor='rgba(0, 0, 0, 0)')
		fig2D_Coffee.update_xaxes(
			range=[25, 100],
			constrain='domain',
			color='white',
			ticks='outside',
			title='Coffee water'
		)
		fig2D_Coffee.update_yaxes(
			range=[0, 100],
			scaleanchor="x",
			scaleratio=75 / 100,
			color='white',
			ticks='outside',
			title='Water'
		)
		fig2D_Coffee_list.append(fig2D_Coffee)
	return fig2D_Coffee_list


def Graph_2D_Coffee_water(db_data, user, prop):
	values, X, Y, Z, vector, x_values, y_values, z_values = Values(db_data, user, prop)
	fig2D_Coffee_water_list = []
	for coffee_water in [25, 50, 75, 100]:
		values2D = np.array(values)[:, int(4 * (coffee_water / 25 - 1)), :]
		fig2D_Coffee_water = go.Figure()
		fig2D_Coffee_water.add_trace(go.Contour(
			x=z_values,
			y=x_values,
			z=values2D,
			colorscale='blackbody',
			contours=dict(start=1, end=5, size=0.1),
			contours_coloring='heatmap',
			colorbar_tickfont_color='white',
		)
		)
		fig2D_Coffee_water.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#6f4e37", plot_bgcolor='rgba(0, 0, 0, 0)')
		fig2D_Coffee_water.update_xaxes(
			range=[0, 100],
			constrain='domain',
			color='white',
			ticks='outside',
			title='Water'
		)
		fig2D_Coffee_water.update_yaxes(
			range=[1, 5],
			scaleanchor="x",
			scaleratio=100 / 4,
			color='white',
			ticks='outside',
			title='Coffee'
		)
		fig2D_Coffee_water_list.append(fig2D_Coffee_water)
	return fig2D_Coffee_water_list


def Graph_2D_Water(db_data, user, prop):
	values, X, Y, Z, vector, x_values, y_values, z_values = Values(db_data, user, prop)
	fig2D_Water_list = []
	for water in [0, 25, 50, 75, 100]:
		values2D = np.array(values)[:, :, int(3 * water / 25)]
		fig2D_Water = go.Figure()
		fig2D_Water.add_trace(go.Contour(
			x=x_values,
			y=y_values,
			z=values2D,
			colorscale='blackbody',
			contours=dict(start=1, end=5, size=0.1),
			contours_coloring='heatmap',
			colorbar_tickfont_color='white',
		)
		)
		fig2D_Water.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#6f4e37", plot_bgcolor='rgba(0, 0, 0, 0)')
		fig2D_Water.update_xaxes(
			range=[1, 5],
			constrain='domain',
			color='white',
			ticks='outside',
			title='Coffee'
		)
		fig2D_Water.update_yaxes(
			range=[25, 100],
			scaleanchor="x",
			scaleratio=4 / 75,
			color='white',
			ticks='outside',
			title='Coffee water'
		)
		fig2D_Water_list.append(fig2D_Water)
	return fig2D_Water_list


def Statistics(db_data):
	output = {}
	for proper in ['acidity', 'bitterness', 'strong', 'taste']:
		users = []
		for dictionary in db_data:
			if dictionary['user'] not in users:
				users.append(dictionary['user'])

		vector = [[] for _ in users]
		for dictionary in db_data:
			if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] in [vector[users.index(dictionary['user'])][i][0:3] for i, _ in enumerate(vector[users.index(dictionary['user'])])]:
				i = [vector[users.index(dictionary['user'])][i][0:3] for i, _ in enumerate(vector[users.index(dictionary['user'])])].index([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
				vector[users.index(dictionary['user'])][i].append(dictionary[proper])
			else:
				vector[users.index(dictionary['user'])].append([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water'], dictionary[proper]])
		for p, _ in enumerate(users):
			for i, element in enumerate(vector[p]):
				sub_vector = element[0:3]
				sub_vector.append(sum(element[3:]) / len(element[3:]))
				vector[p][i] = sub_vector

		victor = []
		for p, _ in enumerate(users):
			for i, element in enumerate(vector[p]):
				if element[0:3] in [i[0:3] for i in victor]:
					index = [i[0:3] for i in victor].index(element[0:3])
					victor[index].append(element[3])
				else:
					victor.append(element.copy())

		for i, element in enumerate(victor):
			sub_vector = element[0:3]
			sub_vector.extend([sum(element[3:]) / len(element[3:]), len(element[3:])])
			victor[i] = sub_vector

		vector = victor

		# initilize 3D property and fullness
		property_0 = [[[0, 0, 0, 0, 0] for _ in range(4)] for _ in range(5)]
		fullness = [[[0, 0, 0, 0, 0] for _ in range(4)] for _ in range(5)]

		# fill in the known data
		for i in vector:
			property_0[int(i[0] - 1)][int(i[1] / 25 - 1)][int(i[2] / 25)] = i[3]
			fullness[int(i[0] - 1)][int(i[1] / 25 - 1)][int(i[2] / 25)] = i[4]

		prop = property_0.copy()
		for x_0 in range(5):
			for y_0 in range(4):
				for z_0 in range(5):
					if property_0[x_0][y_0][z_0] == 0:
						prop[x_0][y_0][z_0] = sum([fullness[x][y][z] * property_0[x][y][z] / ((x - x_0) ** 2 + (y - y_0) ** 2 + (z - z_0) ** 2) if (x != x_0 or y != y_0 or z != z_0) else 0 for x in range(5) for y in range(4) for z in range(5)]) / sum([fullness[x][y][z] / ((x - x_0) ** 2 + (y - y_0) ** 2 + (z - z_0) ** 2) if (x != x_0 or y != y_0 or z != z_0) else 0 for x in range(5) for y in range(4) for z in range(5)])

		# Continuous grid
		x_values = np.linspace(1, 5, 13)
		y_values = np.linspace(25, 100, 13)
		z_values = np.linspace(0, 100, 13)
		X, Y, Z = np.meshgrid(x_values, y_values, z_values)

		# Create mgrid
		X = np.transpose(X, [1, 0, 2])
		Y = np.transpose(Y, [1, 0, 2])
		Z = np.transpose(Z, [1, 0, 2])

		# Grid
		x = np.linspace(1, 5, 5)
		y = np.linspace(25, 100, 4)
		z = np.linspace(0, 100, 5)
		V = prop
		fn = RegularGridInterpolator((x, y, z), V)
		values = fn((X, Y, Z))

		tuples = list(zip(*np.where(values == np.amax(values))))
		neighbourhood = np.sum([
			[values[tup[0] + 1][tup[1]][tup[2]] if tup[0] != 12 else values[tup[0] - 1][tup[1]][tup[2]] for tup in tuples],
			[values[tup[0]][tup[1] + 1][tup[2]] if tup[1] != 12 else values[tup[0]][tup[1] - 1][tup[2]] for tup in tuples],
			[values[tup[0]][tup[1]][tup[2] + 1] if tup[2] != 12 else values[tup[0]][tup[1]][tup[2] - 1] for tup in tuples],
			[values[tup[0] - 1][tup[1]][tup[2]] if tup[0] != 0 else values[tup[0] + 1][tup[1]][tup[2]] for tup in tuples],
			[values[tup[0]][tup[1] - 1][tup[2]] if tup[1] != 0 else values[tup[0]][tup[1] + 1][tup[2]] for tup in tuples],
			[values[tup[0]][tup[1]][tup[2] - 1] if tup[2] != 0 else values[tup[0]][tup[1]][tup[2] + 1] for tup in tuples]], axis=0)
		maximum = tuples[np.where(neighbourhood == max(neighbourhood))[0][0]]
		output[proper + '_max'] = [[round(2 * (maximum[0] / 3 + 1)) / 2, 5 * round(((maximum[1] / 4 + 1) * 25) / 5), 5 * round(25 * maximum[2] / 15), round(np.amax(values), 1)]]

		tuples = list(zip(*np.where(values == np.amin(values))))
		neighbourhood = np.sum([
			[values[tup[0] + 1][tup[1]][tup[2]] if tup[0] != 12 else values[tup[0] - 1][tup[1]][tup[2]] for tup in tuples],
			[values[tup[0]][tup[1] + 1][tup[2]] if tup[1] != 12 else values[tup[0]][tup[1] - 1][tup[2]] for tup in tuples],
			[values[tup[0]][tup[1]][tup[2] + 1] if tup[2] != 12 else values[tup[0]][tup[1]][tup[2] - 1] for tup in tuples],
			[values[tup[0] - 1][tup[1]][tup[2]] if tup[0] != 0 else values[tup[0] + 1][tup[1]][tup[2]] for tup in tuples],
			[values[tup[0]][tup[1] - 1][tup[2]] if tup[1] != 0 else values[tup[0]][tup[1] + 1][tup[2]] for tup in tuples],
			[values[tup[0]][tup[1]][tup[2] - 1] if tup[2] != 0 else values[tup[0]][tup[1]][tup[2] + 1] for tup in tuples]], axis=0)
		minimum = tuples[np.where(neighbourhood == min(neighbourhood))[0][0]]
		output[proper + '_min'] = [[round(2 * (minimum[0] / 3 + 1)) / 2, 5 * round(((minimum[1] / 4 + 1) * 25) / 5), 5 * round(25 * minimum[2] / 15), round(np.amin(values), 1)]]
	return output
