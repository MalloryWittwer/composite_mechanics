from math import tau
import plotly.graph_objects as go
import numpy as np

def get_modulus(e1, e2, poisson_ratio, shear_modulus, theta):
    theta = np.radians(theta)
    q_reduced = reduced_stiffness_matrix(e1, e2, poisson_ratio, shear_modulus)
    qrt = transformed_reduced_stiffness_matrix(q_reduced, theta)
    modulus = effective_modulus(qrt)
    return modulus

def reduced_stiffness_matrix(e1, e2, poisson_ratio, shear_modulus):
    q11 = e1 / (1 - poisson_ratio**2)
    q12 = poisson_ratio * e2 / (1 - poisson_ratio**2)
    q21 = q12
    q22 = e2 / (1 - poisson_ratio**2)
    q66 = shear_modulus
    q_reduced = np.array([
        [q11, q12, 0],
        [q21, q22, 0],
        [0, 0, q66]
    ])
    return q_reduced

def transformed_reduced_stiffness_matrix(q_reduced, theta):
    q11 = q_reduced[0, 0]
    q12 = q_reduced[0, 1]
    q22 = q_reduced[1, 1]
    q66 = q_reduced[2, 2]
    
    qb11 = q11 * np.cos(theta)**4 + q22 * np.sin(theta)**4 + 2 * (q12 + 2 * q66) * np.sin(theta)**2 * np.cos(theta)**2
    qb22 = q11 * np.sin(theta)**4 + q22 * np.cos(theta)**4 + 2 * (q12 + 2 * q66) * np.sin(theta)**2 * np.cos(theta)**2
    qb66 = (q11 + q22 - 2* q12 - 2 * q66) * np.sin(theta)**2 * np.cos(theta)**2 + q66 * (np.sin(theta)**4 + np.cos(theta)**4)
    qb12 = (q11 + q22 - 4 * q66) * np.sin(theta)**2 * np.cos(theta)**2 + q12 * (np.sin(theta)**4 + np.cos(theta)**4)
    qb21 = qb12
    qb16 = (q11 - q12 - 2 * q66) * np.cos(theta)**3 * np.sin(theta) - (q22 - q12 - 2 * q66) * np.cos(theta) * np.sin(theta)**3
    qb61 = qb16
    qb26 = (q11 - q12 - 2 * q66) * np.cos(theta) * np.sin(theta)**3 - (q22 - q12 - 2 * q66) * np.cos(theta)**3 * np.sin(theta)
    qb62 = qb26
    
    q_reduced_transformed = np.array([
        [qb11, qb12, qb16],
        [qb21, qb22, qb26],
        [qb61, qb62, qb66]
    ])
    
    return q_reduced_transformed

def ply_modulus_curve(q_reduced, thetas):
    ply_modulus = []
    for t in thetas:
        qrt = transformed_reduced_stiffness_matrix(q_reduced, t)
        e_x = effective_modulus(qrt)
        ply_modulus.append(e_x)
    return ply_modulus

def effective_modulus(qrt):
    a11 = qrt[0, 0]
    a22 = qrt[1, 1]
    a12 = qrt[0, 1]
    h = 1
    e_x = (a11 * a22 - a12**2) / (h * a22)
    return e_x

def modulus_wrapper(e1, e2, poisson_ratio, shear_modulus):
    q_reduced = reduced_stiffness_matrix(e1, e2, poisson_ratio, shear_modulus)
    thetas = np.radians(np.linspace(0, 90, 40))
    pms = ply_modulus_curve(q_reduced, thetas)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.degrees(thetas), y=pms,
                        mode='lines',
                        name='modulus',
                        line={ 'color': "#333333" }
                        ))
    fig.update_xaxes(range=[0, 90], showgrid=False)
    fig.update_layout(
        xaxis_title=u"Theta (\u0398)",
        yaxis_title="Modulus [GPa]",
        plot_bgcolor="#f7f7f7",
    )
    return fig

if __name__ == '__main__':
    fig = modulus_wrapper(70, 30, 0.3, 20)
    fig.show()
    