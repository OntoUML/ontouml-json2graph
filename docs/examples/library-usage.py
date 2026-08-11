"""Run the canonical ontouml-json2graph library example."""

from json2graph.library import decode_json_project, save_graph_file

graph = decode_json_project("minimal-project.json")
save_graph_file(graph, "minimal-project.ttl", "ttl")
