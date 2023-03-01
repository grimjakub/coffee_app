import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import CubicSpline
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt


def vytvor_graf(data, user, property):

    users = []
    for dictionary in data:
        if dictionary['user'] not in users:
            users.append(dictionary['user'])

    vector = []

    if user not in users:
        for dictionary in data:
            if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] in [vector[i][0:3] for i, element in enumerate(vector)]:
                i = [vector[i][0:3] for i, element in enumerate(vector)].index([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
                vector[i].append(dictionary[property])
            else:
                vector.append([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water'], dictionary[property]])
        for i, element in enumerate(vector):
            sub_vector = element[0:3]
            sub_vector.append(sum(element[3:]) / len(element[3:]))  # element[0:3]
            vector[i] = sub_vector
    else:
        for dictionary in data:
            if dictionary['user'] == user:
                vector.append([dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water'], dictionary[property]])

    vector = np.array(vector)
    # print(vector)
    # print(vector.sort())

    xs = np.arange(-1.5, 9.6, 0.1)
    fig, ax = plt.subplots(figsize=(6.5, 4))

    # initilize 3D property and fullness
    property = [[list(np.zeros(5)) for _ in range(4)] for _ in range(5)]
    fullness = [[list(np.zeros(5)) for _ in range(4)] for _ in range(5)]

    # fill in the known data
    for i in vector:
        property[int(i[0] - 1)][int(i[1] / 25 - 1)][int(i[2] / 25)] = i[3]
        fullness[int(i[0] - 1)][int(i[1] / 25 - 1)][int(i[2] / 25)] = 1

    for cycles in range(3):
        # initialize all projections
        f_coffee = [[[] for _ in range(5)] for _ in range(4)]
        f_coffee_yz = [[[1, 2, 3, 4, 5] for _ in range(5)] for _ in range(4)]
        f_coffee_property = [[[] for _ in range(5)] for _ in range(4)]
        f_coffee_fullness = [[[] for _ in range(5)] for _ in range(4)]

        f_coffee_water = [[[] for _ in range(5)] for _ in range(5)]
        f_coffee_water_zx = [[[25, 50, 75, 100] for _ in range(5)] for _ in range(5)]
        f_coffee_water_property = [[[] for _ in range(5)] for _ in range(5)]
        f_coffee_water_fullness = [[[] for _ in range(5)] for _ in range(5)]

        f_water = [[[] for _ in range(4)] for _ in range(5)]
        f_water_xy = [[[0, 25, 50, 75, 100] for _ in range(4)] for _ in range(5)]
        f_water_property = [[[] for _ in range(4)] for _ in range(5)]
        f_water_fullness = [[[] for _ in range(4)] for _ in range(5)]

        # fill in the projections from property and fullness
        for x in range(5):
            for y in range(4):
                for z in range(5):
                    f_coffee_property[y][z].append(property[x][y][z])
                    f_coffee_fullness[y][z].append(fullness[x][y][z])
                    f_coffee_water_property[z][x].append(property[x][y][z])
                    f_coffee_water_fullness[z][x].append(fullness[x][y][z])
                    f_water_property[x][y].append(property[x][y][z])
                    f_water_fullness[x][y].append(fullness[x][y][z])

        for y in range(4):
            for z in range(5):
                if sum(f_coffee_fullness[y][z]) > 1:
                    f_coffee_yz_nonzero = [i for index, i in enumerate(f_coffee_yz[y][z]) if fullness[index][y][z]]
                    f_coffee_property_nonzero = [i for index, i in enumerate(f_coffee_property[y][z]) if fullness[index][y][z]]
                    f_coffee[y][z] = CubicSpline(f_coffee_yz_nonzero, f_coffee_property_nonzero)
                    ax.plot(xs, f_coffee[y][z](xs))
                elif sum(f_coffee_fullness[y][z]) == 1:
                    f_coffee[y][z] = lambda x: sum(f_coffee_property[y][z]) + np.array(x) * 0
                    ax.plot(xs, f_coffee[y][z](xs))
                if sum(f_coffee_fullness[y][z]) > 0:
                    f_coffee_property[y][z] = list(f_coffee[y][z](f_coffee_yz[y][z]))
                    f_coffee_fullness[y][z] = [1, 1, 1, 1, 1]

        for z in range(5):
            for x in range(5):
                if sum(f_coffee_water_fullness[z][x]) > 1:
                    f_coffee_water_zx_nonzero = [i for index, i in enumerate(f_coffee_water_zx[z][x]) if fullness[x][index][z]]
                    f_coffee_water_property_nonzero = [i for index, i in enumerate(f_coffee_water_property[z][x]) if fullness[x][index][z]]
                    f_coffee_water[z][x] = CubicSpline(f_coffee_water_zx_nonzero, f_coffee_water_property_nonzero)
                    ax.plot(xs, f_coffee_water[z][x](xs))
                elif sum(f_coffee_water_fullness[z][x]) == 1:
                    f_coffee_water[z][x] = lambda y: sum(f_coffee_water_property[z][x]) + np.array(y) * 0
                    ax.plot(xs, f_coffee_water[z][x](xs))
                if sum(f_coffee_water_fullness[z][x]) > 0:
                    f_coffee_water_property[z][x] = list(f_coffee_water[z][x](f_coffee_water_zx[z][x]))
                    f_coffee_water_fullness[z][x] = [1, 1, 1, 1]

        for x in range(5):
            for y in range(4):
                if sum(f_water_fullness[x][y]) > 1:
                    f_water_xy_nonzero = [i for index, i in enumerate(f_water_xy[x][y]) if fullness[x][y][index]]
                    f_water_property_nonzero = [i for index, i in enumerate(f_water_property[x][y]) if fullness[x][y][index]]
                    f_water[x][y] = CubicSpline(f_water_xy_nonzero, f_water_property_nonzero)
                    ax.plot(xs, f_water[x][y](xs))
                elif sum(f_water_fullness[x][y]) == 1:
                    f_water[x][y] = lambda z: sum(f_water_property[x][y]) + np.array(z) * 0
                    ax.plot(xs, f_water[x][y](xs))
                if sum(f_water_fullness[x][y]) > 0:
                    f_water_property[x][y] = list(f_water[x][y](f_water_xy[x][y]))
                    f_water_fullness[x][y] = [1, 1, 1, 1, 1]

        for x in range(5):
            for y in range(4):
                for z in range(5):
                    if (f_coffee_fullness[y][z][x] + f_coffee_water_fullness[z][x][y] + f_water_fullness[x][y][z]):
                        property[x][y][z] = (f_coffee_property[y][z][x] + f_coffee_water_property[z][x][y] + f_water_property[x][y][z]) / (f_coffee_fullness[y][z][x] + f_coffee_water_fullness[z][x][y] + f_water_fullness[x][y][z])
                        fullness[x][y][z] = 1

    # plt.show()

    # Continuous grid
    x_values = np.linspace(1, 5, 10)
    y_values = np.linspace(25, 100, 10)
    z_values = np.linspace(0, 100, 10)
    X, Y, Z = np.meshgrid(x_values, y_values, z_values)

    # Create mgrid
    X = np.transpose(X, [1, 0, 2])
    Y = np.transpose(Y, [1, 0, 2])
    Z = np.transpose(Z, [1, 0, 2])

    # Grid
    x = np.linspace(1, 5, 5)
    y = np.linspace(25, 100, 4)
    z = np.linspace(0, 100, 5)
    V = property
    fn = RegularGridInterpolator((x, y, z), V)
    values = fn((X, Y, Z))

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
            )
        )

    fig.add_trace(go.Scatter3d(
        x=[i[0] for i in vector], y=[i[1] for i in vector], z=[i[2] for i in vector],
        mode='markers', marker=dict(color='black'), hovertemplate='Coffee: %{x}<br>Coffee water: %{y}<br>Water: %{z}<extra></extra>')
    )

    fig.update_scenes(
        xaxis=dict(range=[0.8, 5.2], nticks=5, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)", ticks='outside', title='Coffee'),
        yaxis=dict(range=[21, 104], dtick=25, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)", ticks='outside', title='Coffee water'),
        zaxis=dict(range=[-5, 105], dtick=25, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)", ticks='outside', title='Water'),
    )

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#6f4e37")

    return fig