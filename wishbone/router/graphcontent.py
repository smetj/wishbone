#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  graphcontent.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import json

GRAPHCONTENT = """
<!doctype html>
<html>
<head>
    <title>Network | Custom Groups</title>

  <style type="text/css">
    #mynetwork {
      width: 100px;
      height: 100px;
      border: 0px solid lightgray;
    }
  </style>

    <script type="text/javascript" src="http://visjs.org/dist/vis.js"></script>
    <link href="http://visjs.org/dist/vis.css" rel="stylesheet" type="text/css"/>
    <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css">
</head>

<body>

<div id="mynetwork"></div>

<script type="text/javascript">
  // create an array with nodes
  var nodes = %s;

  // create an array with edges
  var edges = %s;

  // create a network
  var container = document.getElementById('mynetwork');
  var data = {
    nodes: nodes,
    edges: edges
  };

//    var options = {
//        "height":  window.innerHeight,
//        "width":  window.innerWidth,
//        "edges": {
//            "smooth": {
//              "forceDirection": "none"
//            }
//        }
//    };
var options = {
  "height":  window.innerHeight,
  "width":  window.innerWidth,
}
  var network = new vis.Network(container, data, options);
</script>

</body>
</html>

"""


class VisJSData():

    def __init__(self, ignore_logging=False, ingore_metrics=False):

        self.id = 0
        self.nodes = {}
        self.edges = []

    def addModule(self, instance_name, module_name, description):

        if ".input." in module_name or ".output." in module_name:
            shape = "square"
            color = {
                "border": 'red',
                "background": '#D2E5FF',
                "highlight": {
                    "border": '#2B7CE9',
                    "background": '#D2E5FF'
                },
                "hover": {
                    "border": '#2B7CE9',
                    "background": '#D2E5FF'
                }
            }
        else:
            shape = "dot"
            color = {
                "border": '#2B7CE9',
                "background": '#D2E5FF',
                "highlight": {
                    "border": '#2B7CE9',
                    "background": '#D2E5FF'
                },
                "hover": {
                    "border": '#2B7CE9',
                    "background": '#D2E5FF'
                }
            }

        if instance_name not in list(self.nodes.keys()):
            self.nodes[instance_name] = {"id": self.id,
                                         "label": instance_name,
                                         "shape": shape,
                                         "size": 20,
                                         "color": color,
                                         "title": "Module: %s</br>Description: %s" % (module_name, description),
                                         "shadow": True,
                                         "font.size": 20
                                         }
            self.id += 1

    def addQueue(self, module, name):

        if "%s.%s" % (module, name) not in list(self.nodes.keys()):
            self.nodes["%s.%s" % (module, name)] = {"id": self.id,
                                                    "label": name,
                                                    "shape": "dot",
                                                    "size": 5,
                                                    "title": "Queue: %s.%s" % (module, name),
                                                    "shadow": True,
                                                    "font.size": 20
                                                    }
            self.edges.append({"from": self.nodes[module]["id"],
                               "to": self.nodes["%s.%s" % (module, name)]["id"],
                               "dashes": True})
            self.id += 1

    def addEdge(self, f, t):

        self.edges.append({"from": self.nodes[f]["id"],
                           "to": self.nodes[t]["id"],
                           "arrows": "to"
                           }
                          )

    def dumpString(self):

        nodes = json.dumps(list(self.nodes.values()))
        edges = json.dumps(self.edges)
        return (nodes, edges)
