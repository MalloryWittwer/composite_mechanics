from math import tau
import plotly.graph_objects as go
import numpy as np

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
    f_x_1 = sigma1 / (np.cos(t)**2 + 1e-9)
    return f_x_1

def max_sigma2_criterion(sigma2, t):
    f_x_2 = sigma2 / (np.sin(t)**2 + 1e-9)
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

def add_vrect_to_fig(fig, x0, x1, color):#, annotation):
    fig.add_vrect(
        x0=np.degrees(x0), x1=np.degrees(x1), fillcolor=color, 
        opacity=0.5, layer="below", line_width=0,
        # annotation_text=annotation,
        # annotation_position="bottom"
    )
    return fig

def add_failure_modes(fig, thetas, pfs1, pfs2, pft12):
    colors = ['#f7f7f7', '#f7f7f7', '#fcfcfc']
    # annotations = ['longitudinal strength limiting', 'transverse strength limiting', 'shear strength limiting']
    x0 = thetas[0]
    pad = (thetas[1] - thetas[0]) / 2
    m0 = np.argmin([pfs1[0], pfs2[0], pft12[0]])
    for t, fs1, fs2, ft12 in zip(thetas, pfs1, pfs2, pft12):
        m = np.argmin([fs1, fs2, ft12])
        if m != m0:
            x1 = t
            fig = add_vrect_to_fig(fig, x0 - pad, x1 - pad, colors[m0])#, annotations[m0])
            x0 = x1
        if t == thetas[-1]:
            x1 = t
            fig = add_vrect_to_fig(fig, x0 - pad, x1, colors[m0])#, annotations[m0])
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
    fig = failure_wrapper(110, 60, 40)
    fig.show()
    