import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import CubicSpline
from scipy.interpolate import RegularGridInterpolator


def Values(data, user, property):
    users = []
    for dictionary in data:
        if dictionary['user'] not in users:
            users.append(dictionary['user'])

    vector = []

    if user not in users:
        for dictionary in data:
            if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] in [
                vector[i][0:3] for i, element in enumerate(vector)]:
                i = [vector[i][0:3] for i, element in enumerate(vector)].index(
                    [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
                vector[i].append(dictionary[property])
            else:
                vector.append(
                    [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water'],
                     dictionary[property]])
        for i, element in enumerate(vector):
            sub_vector = element[0:3]
            sub_vector.append(sum(element[3:]) / len(element[3:]))  # element[0:3]
            vector[i] = sub_vector
    else:
        for dictionary in data:
            if dictionary['user'] == user:
                vector.append(
                    [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water'],
                     dictionary[property]])

    vector = np.array(vector)

    # initialize 3D property and fullness
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
                    f_coffee_property_nonzero = [i for index, i in enumerate(f_coffee_property[y][z]) if
                                                 fullness[index][y][z]]
                    f_coffee[y][z] = CubicSpline(f_coffee_yz_nonzero, f_coffee_property_nonzero)
                elif sum(f_coffee_fullness[y][z]) == 1:
                    f_coffee[y][z] = lambda x: sum(f_coffee_property[y][z]) + np.array(x) * 0
                if sum(f_coffee_fullness[y][z]) > 0:
                    f_coffee_property[y][z] = list(f_coffee[y][z](f_coffee_yz[y][z]))
                    f_coffee_fullness[y][z] = [1, 1, 1, 1, 1]

        for z in range(5):
            for x in range(5):
                if sum(f_coffee_water_fullness[z][x]) > 1:
                    f_coffee_water_zx_nonzero = [i for index, i in enumerate(f_coffee_water_zx[z][x]) if
                                                 fullness[x][index][z]]
                    f_coffee_water_property_nonzero = [i for index, i in enumerate(f_coffee_water_property[z][x]) if
                                                       fullness[x][index][z]]
                    f_coffee_water[z][x] = CubicSpline(f_coffee_water_zx_nonzero, f_coffee_water_property_nonzero)
                elif sum(f_coffee_water_fullness[z][x]) == 1:
                    f_coffee_water[z][x] = lambda y: sum(f_coffee_water_property[z][x]) + np.array(y) * 0
                if sum(f_coffee_water_fullness[z][x]) > 0:
                    f_coffee_water_property[z][x] = list(f_coffee_water[z][x](f_coffee_water_zx[z][x]))
                    f_coffee_water_fullness[z][x] = [1, 1, 1, 1]

        for x in range(5):
            for y in range(4):
                if sum(f_water_fullness[x][y]) > 1:
                    f_water_xy_nonzero = [i for index, i in enumerate(f_water_xy[x][y]) if fullness[x][y][index]]
                    f_water_property_nonzero = [i for index, i in enumerate(f_water_property[x][y]) if
                                                fullness[x][y][index]]
                    f_water[x][y] = CubicSpline(f_water_xy_nonzero, f_water_property_nonzero)
                elif sum(f_water_fullness[x][y]) == 1:
                    f_water[x][y] = lambda z: sum(f_water_property[x][y]) + np.array(z) * 0
                if sum(f_water_fullness[x][y]) > 0:
                    f_water_property[x][y] = list(f_water[x][y](f_water_xy[x][y]))
                    f_water_fullness[x][y] = [1, 1, 1, 1, 1]

        for x in range(5):
            for y in range(4):
                for z in range(5):
                    if (f_coffee_fullness[y][z][x] + f_coffee_water_fullness[z][x][y] + f_water_fullness[x][y][z]):
                        property[x][y][z] = (f_coffee_property[y][z][x] + f_coffee_water_property[z][x][y] +
                                             f_water_property[x][y][z]) / (
                                                        f_coffee_fullness[y][z][x] + f_coffee_water_fullness[z][x][y] +
                                                        f_water_fullness[x][y][z])
                        fullness[x][y][z] = 1

    # Continuous grid
    x_values = np.linspace(1, 5, 121)
    y_values = np.linspace(25, 100, 121)
    z_values = np.linspace(0, 100, 121)
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

    return [values, X, Y, Z, vector, x_values, y_values, z_values]


def Graph_3D(values, X, Y, Z, vector):
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
        mode='markers', marker=dict(color='black'),
        hovertemplate='Coffee: %{x}<br>Coffee water: %{y}<br>Water: %{z}<extra></extra>')
    )

    fig.update_scenes(
        xaxis=dict(range=[0.8, 5.2], nticks=5, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)",
                   ticks='outside', title='Coffee'),
        yaxis=dict(range=[21, 104], dtick=25, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)",
                   ticks='outside', title='Coffee water'),
        zaxis=dict(range=[-5, 105], dtick=25, color="white", gridcolor="white", backgroundcolor="rgba(0, 0, 0, 0)",
                   ticks='outside', title='Water'),
    )

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#6f4e37")
    return fig


def Graph_2D_Coffee(data, user, property, Coffee):
    values, X, Y, Z, vector, x_values, y_values, z_values = Values(data, user, property)
    # Coffee = 5   # In beans, step 0.5, range [1, 5]
    values2D = np.array(values)[int(30 * (Coffee - 1)), :, :]

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
    fig2D_Coffee.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#6f4e37",
                               plot_bgcolor='rgba(0, 0, 0, 0)')
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

    return fig2D_Coffee


def Graph_2D_Coffee_water(data, user, property, Coffee_water):
    values, X, Y, Z, vector, x_values, y_values, z_values = Values(data, user, property)
    # Coffe_water = 95   # In ml, step 5, range [25, 100]
    values2D = np.array(values)[:, int(8 * (Coffee_water - 25) / 5), :]

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
    fig2D_Coffee_water.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#6f4e37",
                                     plot_bgcolor='rgba(0, 0, 0, 0)')
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

    return fig2D_Coffee_water


def Graph_2D_Water(data, user, property, Water):
    values, X, Y, Z, vector, x_values, y_values, z_values = Values(data, user, property)
    # Water = 95  # In ml, step 5, range [0, 100]
    values2D = np.array(values)[:, :, int(6 * Water / 5)]

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
    fig2D_Water.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#6f4e37",
                              plot_bgcolor='rgba(0, 0, 0, 0)')
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

    return fig2D_Water
