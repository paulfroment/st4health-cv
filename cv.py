import streamlit as st
import plotly.graph_objects as go
import json
import numpy as np
from sklearn.cluster import KMeans

st.set_page_config(layout="wide")  # use full width for the app

# Define the points as (Health, Computer science, Experience)
points = {
    "DFGSM": (10, 1, 5),
    "DFASM": (10, 1, 9),
    "Programmation": (1, 10, 2),
    "Cloud": (1, 8, 6),
    "MOA": (3, 6, 5),
    "PIR": (6, 4, 6)
}

# Map axes: x = Health, y = Experience, z = Computer science.
x_vals, y_vals, z_vals, labels, hovertexts = [], [], [], [], []
for label, (health, cs, exp) in points.items():
    x_vals.append(health)
    y_vals.append(exp)
    z_vals.append(cs)
    labels.append(label)
    # Remove coordinate details and add additional info.
    hovertexts.append(f"<b>{label}</b><br>Additional details: An essential skill for this role.")

# Create a 3D scatter plot.
fig = go.Figure(data=go.Scatter3d(
    x=x_vals,
    y=y_vals,
    z=z_vals,
    mode='markers+text',
    marker=dict(color='cyan', size=12),
    text=labels,
    textposition='top center',
    textfont=dict(color='white'),
    hovertext=hovertexts,
    hoverinfo='text',
    showlegend=False
))

# Set the initial camera view.
initial_eye = dict(x=0.05, y=-2.5, z=0.5)
fig.update_layout(
    scene=dict(
        xaxis=dict(title='Health', range=[0, 10],
                   backgroundcolor='black', color='white', gridcolor='grey'),
        yaxis=dict(title='Experience', range=[0, 10],
                   backgroundcolor='black', color='white', gridcolor='grey'),
        zaxis=dict(title='Computer science', range=[0, 10],
                   backgroundcolor='black', color='white', gridcolor='grey'),
        aspectmode='cube'
    ),
    scene_camera=dict(eye=initial_eye),
    paper_bgcolor='black',
    plot_bgcolor='black'
)

# Precompute k-means clustering with k=2.
points_array = np.array(list(zip(x_vals, y_vals, z_vals)))
kmeans = KMeans(n_clusters=2, random_state=0).fit(points_array)
cluster_labels = kmeans.labels_.tolist()
centroids = kmeans.cluster_centers_.tolist()

# Determine centroid names based on highest computer science and health grades.
cs_values = [centroid[2] for centroid in centroids]
health_values = [centroid[0] for centroid in centroids]
cs_idx = int(np.argmax(cs_values))
health_idx = int(np.argmax(health_values))
if cs_idx == health_idx:
    other_idx = 1 - cs_idx
    centroid_names = {cs_idx: "AI", other_idx: "Medecine"}
else:
    centroid_names = {cs_idx: "AI", health_idx: "Medecine"}

# Create hover texts for centroids.
centroid_hover_texts = []
for i in range(len(centroids)):
    if centroid_names[i] == "AI":
        centroid_hover_texts.append("This centroid is <b>AI</b> because it has the highest Computer Science grade. It represents skills geared towards innovative tech solutions.")
    elif centroid_names[i] == "Medecine":
        centroid_hover_texts.append("This centroid is <b>Medecine</b> because it has the highest Health grade. It represents skills focused on medical expertise.")
    else:
        centroid_hover_texts.append("")

# Convert objects to JSON strings for embedding.
fig_json = fig.to_json()
cluster_labels_json = json.dumps(cluster_labels)
centroids_json = json.dumps(centroids)
centroid_names_json = json.dumps(centroid_names)
centroid_hover_texts_json = json.dumps(centroid_hover_texts)
initial_eye_json = json.dumps(initial_eye)

# Animation parameters.
steps = 720
zoom_factor = 0.2

html_string = f"""
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
            background-color: black;
            color: white;
        }}
        #plotly-div {{
            width: 100vw;
            height: 100vh;
        }}
        #rotate-button {{
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 100;
            padding: 10px 20px;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <button id="rotate-button">Run k mean clustering</button>
    <div id="plotly-div"></div>
    <script>
        var fig = {fig_json};
        // Prevent full manual rotation by intercepting mouse events.
        document.getElementById('plotly-div').onmousedown = function(e) {{
            e.preventDefault();
        }};
        Plotly.newPlot('plotly-div', fig.data, fig.layout);
        
        // Precomputed clustering data.
        var clusterLabels = {cluster_labels_json};
        var centroids = {centroids_json};
        var centroidNames = {centroid_names_json};
        var centroidHoverTexts = {centroid_hover_texts_json};
        // Define color mapping: AI -> blue, Medecine -> red.
        var clusterColorMap = {{"AI": "blue", "Medecine": "red"}};
        
        var clusteringApplied = false;
        var initial_eye = {initial_eye_json};
        var radius = Math.sqrt(initial_eye.x * initial_eye.x + initial_eye.y * initial_eye.y);
        var initial_angle = Math.atan2(initial_eye.y, initial_eye.x);
        var steps = {steps};
        var zoom_factor = {zoom_factor};

        document.getElementById("rotate-button").addEventListener("click", function() {{
            if (!clusteringApplied) {{
                // Update marker colors based on cluster labels.
                var newMarkerColors = clusterLabels.map(function(lbl) {{
                    var cname = centroidNames[lbl] || centroidNames[String(lbl)];
                    return clusterColorMap[cname];
                }});
                Plotly.restyle('plotly-div', {{'marker.color': [newMarkerColors]}}, [0]);
                
                // Draw lines from centroids to each point.
                var x_vals = fig.data[0].x;
                var y_vals = fig.data[0].y;
                var z_vals = fig.data[0].z;
                var lineTraces = [];
                for (var i = 0; i < clusterLabels.length; i++) {{
                    var cl = clusterLabels[i];
                    var cname = centroidNames[cl] || centroidNames[String(cl)];
                    var color = clusterColorMap[cname];
                    var trace = {{
                        type: 'scatter3d',
                        mode: 'lines',
                        x: [centroids[cl][0], x_vals[i]],
                        y: [centroids[cl][1], y_vals[i]],
                        z: [centroids[cl][2], z_vals[i]],
                        line: {{color: color, width: 2}},
                        hoverinfo: 'skip',
                        showlegend: false
                    }};
                    lineTraces.push(trace);
                }}
                Plotly.addTraces('plotly-div', lineTraces);
                
                // Add centroids as markers with hover texts.
                var centroidTrace = {{
                    type: 'scatter3d',
                    mode: 'markers+text',
                    x: [centroids[0][0], centroids[1][0]],
                    y: [centroids[0][1], centroids[1][1]],
                    z: [centroids[0][2], centroids[1][2]],
                    marker: {{
                        color: [clusterColorMap[centroidNames["0"]], clusterColorMap[centroidNames["1"]]],
                        size: 16,
                        symbol: 'diamond'
                    }},
                    text: [centroidNames["0"], centroidNames["1"]],
                    textposition: 'top center',
                    textfont: {{color: 'white'}},
                    hovertext: centroidHoverTexts,
                    hoverinfo: 'text',
                    showlegend: false
                }};
                Plotly.addTraces('plotly-div', centroidTrace);
                
                clusteringApplied = true;
            }}
            // Run rotation animation.
            var step = 0;
            function animate() {{
                if (step <= steps) {{
                    var angle = initial_angle + (2 * Math.PI * step / steps);
                    var new_radius = radius * (1 - zoom_factor * (1 - Math.cos(2 * Math.PI * step / steps)) / 2);
                    var new_eye = {{
                        x: new_radius * Math.cos(angle),
                        y: new_radius * Math.sin(angle),
                        z: initial_eye.z
                    }};
                    Plotly.relayout('plotly-div', 'scene.camera.eye', new_eye);
                    step++;
                    requestAnimationFrame(animate);
                }} else {{
                    Plotly.relayout('plotly-div', 'scene.camera.eye', initial_eye);
                }}
            }}
            animate();
        }});
    </script>
</body>
</html>
"""

st.components.v1.html(html_string, height=800)