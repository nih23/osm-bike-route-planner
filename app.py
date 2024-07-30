from flask import Flask, render_template, request
import osmnx as ox
import networkx as nx

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plan_route', methods=['POST'])
def plan_route():
    start_location = request.form['start']
    end_location = request.form['end']

    # Convert start and end locations to tuples of floats
    try:
        start_coords = tuple(map(float, start_location.split(',')))
        end_coords = tuple(map(float, end_location.split(',')))

        # Swapping the first and second elements
        start_coords = (start_coords[1], start_coords[0])
        end_coords = (end_coords[1], end_coords[0])
    except ValueError:
        return render_template('index.html', error="Invalid coordinates format. Please try again.")

    try:
        # Download the graph
        G = ox.graph_from_point(start_coords, dist=2000, network_type='bike')

        # Get the nearest nodes to the start and end points
        orig_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
        dest_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])

        # Find the shortest path
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')

        # Get the coordinates of the route
        route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

        return render_template('index.html', route=route_coords, start=start_location, end=end_location)
    except ox._errors.InsufficientResponseError:
        return render_template('index.html', error="No data available for the selected points. Please try again with different points.")
    except Exception as e:
        return render_template('index.html', error=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
