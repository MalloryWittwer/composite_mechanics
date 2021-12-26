from math import tau
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

def get_modulus(e1, e2, poisson_ratio, shear_modulus, theta):
    theta = np.radians(theta)
    q_reduced = reduced_stiffness_matrix(e1, e2, poisson_ratio, shear_modulus)
    qrt = transformed_reduced_stiffness_matrix(q_reduced, theta)
    modulus = effective_modulus(qrt)
    return modulus

def get_max_stress(s1, s2, t12, theta):
    theta = np.radians(theta)
    max_stress = tsai_hill_criterion(s1, s2, t12, theta)
    return max_stress

def get_failure_mode(s1, s2, t12, theta):
    theta = np.radians(theta)
    modes = ['fibers', 'matrix', 'shear']
    ms1 = max_sigma1_criterion(s1, theta)
    ms2 = max_sigma2_criterion(s2, theta)
    mt12 = max_shear_criterion(t12, theta)
    mode = modes[np.argmin([ms1, ms2, mt12])]
    return mode

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
        plot_bgcolor="#b1eeff",
    )
    return fig

def tsai_hill_criterion(sigma1, sigma2, tau12, t):
    f_x = 1 / np.sqrt(
        np.square(
            np.cos(t)**2 / sigma1
        ) +
        np.square(
            np.sin(t)**2 / sigma2
        ) -
        np.square(
            np.sin(t) * np.cos(t) / sigma1
        ) +
        np.square(
            np.sin(t) * np.cos(t) / tau12
        )
    )
    return f_x

def max_sigma1_criterion(sigma1, t):
    f_x_1 = sigma1 / np.cos(t)**2
    return f_x_1

def max_sigma2_criterion(sigma2, t):
    f_x_2 = sigma2 / np.sin(t)**2
    return f_x_2

def max_shear_criterion(tau12, t):
    f_x_12 = tau12 / ((np.sin(t) * np.cos(t)) + 1e-9)
    return f_x_12

def ply_failure_curves(sigma1, sigma2, tau12, thetas):
    ply_failures_th = []
    ply_failures_s1 = []
    ply_failures_s2 = []
    ply_failures_t12 = []
    for t in thetas:
        ply_failures_s1.append(
            max_sigma1_criterion(sigma1, t)
        )
        ply_failures_s2.append(
            max_sigma2_criterion(sigma2, t)
        )
        ply_failures_t12.append(
            max_shear_criterion(tau12, t)
        )
        ply_failures_th.append(
            tsai_hill_criterion(sigma1, sigma2, tau12, t)
        )
    return ply_failures_s1, ply_failures_s2, ply_failures_t12, ply_failures_th

def add_vrect_to_fig(fig, x0, x1, color, annotation):
    fig.add_vrect(
        x0=np.degrees(x0), x1=np.degrees(x1), fillcolor=color, 
        opacity=0.5, layer="below", line_width=0,
        annotation_text=annotation,
        annotation_position="bottom"
    )
    return fig

def add_failure_modes(fig, thetas, pfs1, pfs2, pft12):
    colors = ['#00cff8', '#009fc7', '#50daff']
    annotations = ['fibers failure', 'matrix failure', 'shear failure']
    x0 = thetas[0]
    pad = (thetas[1] - thetas[0]) / 2
    m0 = np.argmin([pfs1[0], pfs2[0], pft12[0]])
    for t, fs1, fs2, ft12 in zip(thetas, pfs1, pfs2, pft12):
        m = np.argmin([fs1, fs2, ft12])
        if m != m0:
            x1 = t
            fig = add_vrect_to_fig(fig, x0 - pad, x1 - pad, colors[m0], annotations[m0])
            x0 = x1
        if t == thetas[-1]:
            x1 = t
            fig = add_vrect_to_fig(fig, x0 - pad, x1, colors[m0], annotations[m0])
        m0 = m
    return fig

def failure_wrapper(sigma1, sigma2, tau12):
    thetas = np.radians(np.linspace(0, 90, 40))
    pfs1, pfs2, pft12, pfth = ply_failure_curves(sigma1, sigma2, tau12, thetas)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=np.degrees(thetas), y=pfs1,
                        mode='lines',
                        name='Max \u03c3<sub>1</sub>',
                        line={ 'color': "#000000", 'dash': 'longdash' }
                        ))
    fig.add_trace(go.Scatter(x=np.degrees(thetas), y=pfs2,
                        mode='lines',
                        name='Max \u03c3<sub>2</sub>',
                        line={ 'color': "#000000", 'dash': 'dash' }
                        ))
    fig.add_trace(go.Scatter(x=np.degrees(thetas), y=pft12,
                        mode='lines',
                        name='Max \u03c4<sub>12</sub>',
                        line={ 'color': "#000000", 'dash': 'dot'}
                        ))
    fig.add_trace(go.Scatter(x=np.degrees(thetas), y=pfth,
                        mode='lines',
                        name='Tsai-Hill',
                        line={ 'color': "#000000" }
                        ))
    
    fig = add_failure_modes(fig, thetas, pfs1, pfs2, pft12)
    
    fig.update_yaxes(range=[0, 2 * max(sigma1, sigma2)])
    fig.update_xaxes(range=[0, 90], showgrid=False)
    fig.update_layout(
        xaxis_title=u"Theta (\u0398)",
        yaxis_title="Stress [MPa]",
        plot_bgcolor="#eeeeee",
    )
    return fig

if __name__ == '__main__':
    # Elastic properties
    e1 = 70
    e2 = 30
    poisson_ratio = 0.3
    shear_modulus = 20
    # fig = modulus_wrapper(e1, e2, poisson_ratio, shear_modulus)
    # fig.show()
    
    # Failure properties
    sigma1 = 110
    sigma2 = 60
    tau12 = 40
    
    fig = failure_wrapper(sigma1, sigma2, tau12)
    fig.show()
    