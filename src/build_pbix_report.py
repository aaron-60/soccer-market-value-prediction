"""
Build Power BI report visuals into the PBIX file.
Modifies the Report/Layout JSON inside the PBIX zip to add interactive visuals.
"""
import json, zipfile, shutil, os, uuid

SRC_PBIX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_pbix", "original.pbix")
OUT_PBIX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_pbix", "soccer-market-value-prediction-dashboard.pbix")

def uid():
    return uuid.uuid4().hex[:20]

def jstr(obj):
    return json.dumps(obj, separators=(",", ":"))

# ---------------------------------------------------------------------------
# Visual builder helpers
# ---------------------------------------------------------------------------

def make_textbox(name, x, y, w, h, text, font_size="20pt", bold=True, color="#FFFFFF"):
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": text,
                                "textStyle": {
                                    "fontFamily": "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif",
                                    "fontSize": font_size,
                                    "bold": bold,
                                    "color": color
                                }
                            }]
                        }]
                    }
                }]
            },
            "vcObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            }
        }
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": jstr(config), "filters": "[]", "tabOrder": 0}


def make_card(name, x, y, w, h, table, measure, tab_order=0):
    alias = table[0].lower()
    query_ref = f"{table}.{measure}"
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": tab_order}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {"Values": [{"queryRef": query_ref, "active": True}]},
            "prpiorities": [{"Values": [query_ref]}],
            "objects": {
                "labels": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#4FC3F7'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "20D"}}}
                }}],
                "categoryLabels": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#8B95A5'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                }}]
            },
            "vcObjects": {
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}],
                "border": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}},
                    "radius": {"expr": {"Literal": {"Value": "8D"}}}
                }}],
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            }
        }
    }
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": [{"Name": alias, "Entity": table, "Type": 0}],
                    "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": alias}}, "Property": measure}, "Name": query_ref}]
                },
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": [0]}]},
                    "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
                    "Version": 1
                }
            }
        }]
    }
    dt = {
        "projectionOrdering": {"Values": [0]},
        "projectionActiveItems": {"Values": [{"queryRef": query_ref, "active": True}]},
        "queryMetadata": {"Select": [{"Restatement": measure, "Name": query_ref, "Type": 1}]}
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": jstr(config), "filters": "[]",
            "query": jstr(query), "dataTransforms": jstr(dt), "tabOrder": tab_order}


def make_map(name, x, y, w, h, tab_order=0):
    # Data point color selectors for league_tier
    def tier_selector(tier_value):
        return {"data": [{"scopeId": {"Comparison": {
            "ComparisonKind": 0,
            "Left": {"Column": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "league_tier"}},
            "Right": {"Literal": {"Value": f"'{tier_value}'"}}
        }}}]}

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": tab_order}}],
        "singleVisual": {
            "visualType": "map",
            "projections": {
                "Category": [{"queryRef": "Players.nationality", "active": True}],
                "Color": [{"queryRef": "Players.league_tier", "active": True}],
                "Size": [{"queryRef": "Players.Player Count by Country", "active": True}],
                "Tooltips": [{"queryRef": "Players.Total Value by Country", "active": True}]
            },
            "prpiorities": [
                {"Category": ["Players.nationality"]},
                {"Color": ["Players.league_tier"]},
                {"Size": ["Players.Player Count by Country"]},
                {"Tooltips": ["Players.Total Value by Country"]}
            ],
            "objects": {
                "bubbles": [{"properties": {
                    "scaleSizeMax": {"expr": {"Literal": {"Value": "55D"}}}
                }}],
                "legend": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "position": {"expr": {"Literal": {"Value": "'TopRight'"}}},
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}}
                }}],
                "dataPoint": [
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1B3A6B'"}}}}}},
                     "selector": tier_selector("Top 5")},
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#4FC3F7'"}}}}}},
                     "selector": tier_selector("Other")}
                ],
                "categoryLabels": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "8D"}}}
                }}]
            },
            "vcObjects": {
                "title": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Count of Player Count by Nationality'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
                }}],
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}],
                "border": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}]
            }
        }
    }
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": [{"Name": "p", "Entity": "Players", "Type": 0}],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "nationality"}, "Name": "Players.nationality"},
                        {"Column": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "league_tier"}, "Name": "Players.league_tier"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "Player Count by Country"}, "Name": "Players.Player Count by Country"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "Total Value by Country"}, "Name": "Players.Total Value by Country"}
                    ]
                },
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3]}]},
                    "DataReduction": {"DataVolume": 4, "Primary": {"Top": {"Count": 1000}}},
                    "Version": 1
                }
            }
        }]
    }
    dt = {
        "projectionOrdering": {"Category": [0], "Color": [1], "Size": [2], "Tooltips": [3]},
        "projectionActiveItems": {
            "Category": [{"queryRef": "Players.nationality", "active": True}],
            "Color": [{"queryRef": "Players.league_tier", "active": True}],
            "Size": [{"queryRef": "Players.Player Count by Country", "active": True}],
            "Tooltips": [{"queryRef": "Players.Total Value by Country", "active": True}]
        },
        "queryMetadata": {
            "Select": [
                {"Restatement": "nationality", "Name": "Players.nationality", "Type": 6},
                {"Restatement": "league_tier", "Name": "Players.league_tier", "Type": 6},
                {"Restatement": "Player Count by Country", "Name": "Players.Player Count by Country", "Type": 1},
                {"Restatement": "Total Value by Country", "Name": "Players.Total Value by Country", "Type": 1}
            ]
        }
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": jstr(config), "filters": "[]",
            "query": jstr(query), "dataTransforms": jstr(dt), "tabOrder": tab_order}


def make_bar_chart(name, x, y, w, h, tab_order=0):
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": tab_order}}],
        "singleVisual": {
            "visualType": "clusteredBarChart",
            "projections": {
                "Category": [{"queryRef": "Club Value Summary.current_club_name", "active": True}],
                "Y": [{"queryRef": "Club Value Summary.Total Value", "active": True}]
            },
            "prpiorities": [
                {"Category": ["Club Value Summary.current_club_name"]},
                {"Y": ["Club Value Summary.Total Value"]}
            ],
            "objects": {
                "dataPoint": [{"properties": {
                    "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#4FC3F7'"}}}}}
                }}],
                "categoryAxis": [{"properties": {
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#8B95A5'"}}}}}
                }}],
                "valueAxis": [{"properties": {
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#8B95A5'"}}}}},
                    "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}]
            },
            "vcObjects": {
                "title": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Market Value by Club'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
                }}],
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}],
                "border": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}]
            }
        }
    }
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": [{"Name": "c", "Entity": "Club Value Summary", "Type": 0}],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "current_club_name"}, "Name": "Club Value Summary.current_club_name"},
                        {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Total Value"}, "Name": "Club Value Summary.Total Value"}
                    ],
                    "OrderBy": [{"Direction": 2, "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Total Value"}}}]
                },
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": [0, 1]}]},
                    "DataReduction": {"DataVolume": 4, "Primary": {"Top": {"Count": 20}}},
                    "Version": 1
                }
            }
        }]
    }
    dt = {
        "projectionOrdering": {"Category": [0], "Y": [1]},
        "projectionActiveItems": {
            "Category": [{"queryRef": "Club Value Summary.current_club_name", "active": True}],
            "Y": [{"queryRef": "Club Value Summary.Total Value", "active": True}]
        },
        "queryMetadata": {
            "Select": [
                {"Restatement": "Club", "Name": "Club Value Summary.current_club_name", "Type": 6},
                {"Restatement": "Total Value", "Name": "Club Value Summary.Total Value", "Type": 1}
            ]
        }
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": jstr(config), "filters": "[]",
            "query": jstr(query), "dataTransforms": jstr(dt), "tabOrder": tab_order}


def make_table(name, x, y, w, h, tab_order=0):
    cols = [
        ("Player Name", "String"), ("Club", "String"), ("Age", "Int64"),
        ("Position", "String"), ("Nationality", "String"),
        ("Market Value", "Decimal"), ("Peak Market Value", "Decimal")
    ]
    projections = [{"queryRef": f"Top Players.{c[0]}", "active": True} for c in cols]
    select = []
    for i, (col_name, _) in enumerate(cols):
        select.append({
            "Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": col_name},
            "Name": f"Top Players.{col_name}"
        })

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": tab_order}}],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {"Values": projections},
            "prpiorities": [{"Values": [f"Top Players.{c[0]}" for c in cols]}],
            "objects": {
                "grid": [{"properties": {
                    "gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                    "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}},
                    "gridHorizontalColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}],
                "columnHeaders": [{"properties": {
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#4FC3F7'"}}}}},
                    "backColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E2738'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}}
                }}],
                "values": [{"properties": {
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}},
                    "backColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}}
                }}]
            },
            "vcObjects": {
                "title": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Top 50 Most Valuable Players'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
                }}],
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}],
                "border": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}]
            }
        }
    }
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": "Top Players", "Type": 0}],
                    "Select": select,
                    "OrderBy": [{"Direction": 2, "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": "Market Value"}}}]
                },
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": list(range(len(cols)))}]},
                    "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 500}}},
                    "Version": 1
                }
            }
        }]
    }
    dt = {
        "projectionOrdering": {"Values": list(range(len(cols)))},
        "projectionActiveItems": {"Values": [{"queryRef": f"Top Players.{c[0]}", "active": True} for c in cols]},
        "queryMetadata": {
            "Select": [{"Restatement": c[0], "Name": f"Top Players.{c[0]}", "Type": 6} for c in cols]
        }
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": jstr(config), "filters": "[]",
            "query": jstr(query), "dataTransforms": jstr(dt), "tabOrder": tab_order}


def make_donut(name, x, y, w, h, tab_order=0):
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": tab_order}}],
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {
                "Category": [{"queryRef": "Players.position", "active": True}],
                "Y": [{"queryRef": "Players.Total Players", "active": True}]
            },
            "prpiorities": [
                {"Category": ["Players.position"]},
                {"Y": ["Players.Total Players"]}
            ],
            "objects": {
                "legend": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#8B95A5'"}}}}}
                }}]
            },
            "vcObjects": {
                "title": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Position Distribution'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
                }}],
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}],
                "border": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}]
            }
        }
    }
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": [{"Name": "p", "Entity": "Players", "Type": 0}],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "position"}, "Name": "Players.position"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "Total Players"}, "Name": "Players.Total Players"}
                    ]
                },
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": [0, 1]}]},
                    "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
                    "Version": 1
                }
            }
        }]
    }
    dt = {
        "projectionOrdering": {"Category": [0], "Y": [1]},
        "projectionActiveItems": {
            "Category": [{"queryRef": "Players.position", "active": True}],
            "Y": [{"queryRef": "Players.Total Players", "active": True}]
        },
        "queryMetadata": {
            "Select": [
                {"Restatement": "Position", "Name": "Players.position", "Type": 6},
                {"Restatement": "Total Players", "Name": "Players.Total Players", "Type": 1}
            ]
        }
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": jstr(config), "filters": "[]",
            "query": jstr(query), "dataTransforms": jstr(dt), "tabOrder": tab_order}


def make_slicer(name, x, y, w, h, table, column, tab_order=0):
    alias = table[0].lower()
    query_ref = f"{table}.{column}"
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": tab_order}}],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {"Values": [{"queryRef": query_ref, "active": True}]},
            "prpiorities": [{"Values": [query_ref]}],
            "objects": {
                "data": [{"properties": {
                    "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}
                }}],
                "selection": [{"properties": {
                    "selectAllCheckboxEnabled": {"expr": {"Literal": {"Value": "true"}}},
                    "singleSelect": {"expr": {"Literal": {"Value": "false"}}}
                }}],
                "items": [{"properties": {
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}},
                    "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}}
                }}],
                "header": [{"properties": {
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#4FC3F7'"}}}}}
                }}]
            },
            "vcObjects": {
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}],
                "border": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}],
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            }
        }
    }
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": [{"Name": alias, "Entity": table, "Type": 0}],
                    "Select": [{"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": column}, "Name": query_ref}]
                },
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": [0]}]},
                    "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
                    "Version": 1
                }
            }
        }]
    }
    dt = {
        "projectionOrdering": {"Values": [0]},
        "projectionActiveItems": {"Values": [{"queryRef": query_ref, "active": True}]},
        "queryMetadata": {"Select": [{"Restatement": column, "Name": query_ref, "Type": 6}]}
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": jstr(config), "filters": "[]",
            "query": jstr(query), "dataTransforms": jstr(dt), "tabOrder": tab_order}


def make_scatter(name, x, y, w, h, tab_order=0):
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": tab_order}}],
        "singleVisual": {
            "visualType": "scatterChart",
            "projections": {
                "X": [{"queryRef": "Predictions.market_value", "active": True}],
                "Y": [{"queryRef": "Predictions.predicted", "active": True}],
                "Category": [{"queryRef": "Predictions.player_name", "active": True}]
            },
            "prpiorities": [
                {"X": ["Predictions.market_value"]},
                {"Y": ["Predictions.predicted"]},
                {"Category": ["Predictions.player_name"]}
            ],
            "objects": {
                "dataPoint": [{"properties": {
                    "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#4FC3F7'"}}}}}
                }}],
                "categoryAxis": [{"properties": {
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#8B95A5'"}}}}},
                    "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}],
                "valueAxis": [{"properties": {
                    "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#8B95A5'"}}}}},
                    "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}]
            },
            "vcObjects": {
                "title": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Actual vs Predicted Market Value'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E0E0E0'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
                }}],
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1F2E'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }}],
                "border": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2D3548'"}}}}}
                }}]
            }
        }
    }
    query = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": [{"Name": "pr", "Entity": "Predictions", "Type": 0}],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "pr"}}, "Property": "player_name"}, "Name": "Predictions.player_name"},
                        {"Column": {"Expression": {"SourceRef": {"Source": "pr"}}, "Property": "market_value"}, "Name": "Predictions.market_value"},
                        {"Column": {"Expression": {"SourceRef": {"Source": "pr"}}, "Property": "predicted"}, "Name": "Predictions.predicted"}
                    ]
                },
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": [0, 1, 2]}]},
                    "DataReduction": {"DataVolume": 4, "Primary": {"Top": {"Count": 5000}}},
                    "Version": 1
                }
            }
        }]
    }
    dt = {
        "projectionOrdering": {"X": [1], "Y": [2], "Category": [0]},
        "projectionActiveItems": {
            "X": [{"queryRef": "Predictions.market_value", "active": True}],
            "Y": [{"queryRef": "Predictions.predicted", "active": True}],
            "Category": [{"queryRef": "Predictions.player_name", "active": True}]
        },
        "queryMetadata": {
            "Select": [
                {"Restatement": "Player", "Name": "Predictions.player_name", "Type": 6},
                {"Restatement": "Actual Value", "Name": "Predictions.market_value", "Type": 1},
                {"Restatement": "Predicted Value", "Name": "Predictions.predicted", "Type": 1}
            ]
        }
    }
    return {"x": x, "y": y, "z": 0, "width": w, "height": h,
            "config": jstr(config), "filters": "[]",
            "query": jstr(query), "dataTransforms": jstr(dt), "tabOrder": tab_order}


# ---------------------------------------------------------------------------
# Build full layout
# ---------------------------------------------------------------------------

def build_layout():
    # Read original layout
    with zipfile.ZipFile(SRC_PBIX, "r") as z:
        raw = z.read("Report/Layout").decode("utf-16-le")
        if raw.startswith("\ufeff"):
            raw = raw[1:]
        layout = json.loads(raw)

    # Page config with dark background
    page_config = {
        "version": "5.69",
        "themeCollection": {
            "baseTheme": {"name": "CY25SU12", "version": {"visual": "2.5.0", "report": "3.1.0", "page": "2.3.0"}, "type": 2}
        },
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "settings": {
            "useNewFilterPaneExperience": True,
            "allowChangeFilterTypes": True,
            "useStylableVisualContainerHeader": True,
            "queryLimitOption": 6,
            "useEnhancedTooltips": True,
            "exportDataMode": 1,
            "useDefaultAggregateDisplayName": True
        },
        "objects": {
            "section": [{"properties": {
                "verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}},
                "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#0E1117'"}}}}}
            }}]
        }
    }

    section_config = {
        "objects": {
            "background": [{"properties": {
                "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#0E1117'"}}}}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}],
            "wallpaper": [{"properties": {
                "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#0E1117'"}}}}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}]
        }
    }

    # Build visual containers
    visuals = []

    # Title
    visuals.append(make_textbox(uid(), 20, 8, 620, 42,
                                "Football Player Market Value Analysis", "20pt", True, "#FFFFFF"))

    # KPI Cards - top right
    visuals.append(make_card(uid(), 700, 8, 135, 65, "Players", "Total Players", 1))
    visuals.append(make_card(uid(), 845, 8, 175, 65, "Players", "Total Market Value", 2))
    visuals.append(make_card(uid(), 1030, 8, 115, 65, "Players", "Avg Age", 3))
    visuals.append(make_card(uid(), 1155, 8, 115, 65, "Players", "Top Player Value", 4))

    # Slicers - below title
    visuals.append(make_slicer(uid(), 20, 55, 180, 40, "Players", "position", 5))
    visuals.append(make_slicer(uid(), 210, 55, 180, 40, "Players", "league_tier", 6))
    visuals.append(make_slicer(uid(), 400, 55, 180, 40, "Players", "age_group", 7))

    # Map - main visual
    visuals.append(make_map(uid(), 10, 100, 750, 300, 8))

    # Donut - position distribution
    visuals.append(make_donut(uid(), 770, 100, 250, 300, 9))

    # Scatter - predictions
    visuals.append(make_scatter(uid(), 1030, 100, 240, 300, 10))

    # Bar chart - club values
    visuals.append(make_bar_chart(uid(), 10, 410, 500, 305, 11))

    # Table - top players
    visuals.append(make_table(uid(), 520, 410, 750, 305, 12))

    # Update page
    layout["sections"][0]["visualContainers"] = visuals
    layout["sections"][0]["config"] = jstr(section_config)
    layout["sections"][0]["displayName"] = "Market Value Analysis"
    layout["config"] = jstr(page_config)

    return layout


def write_pbix(layout):
    # Create new PBIX by copying original and replacing Layout
    shutil.copy2(SRC_PBIX, OUT_PBIX)

    layout_bytes = json.dumps(layout, separators=(",", ":")).encode("utf-16-le")

    # Replace Layout in the ZIP
    import tempfile
    tmp = OUT_PBIX + ".tmp"
    with zipfile.ZipFile(SRC_PBIX, "r") as zin:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "Report/Layout":
                    zout.writestr(item, layout_bytes)
                else:
                    zout.writestr(item, zin.read(item.filename))
    os.replace(tmp, OUT_PBIX)
    print(f"Created: {OUT_PBIX}")
    print(f"Size: {os.path.getsize(OUT_PBIX):,} bytes")


if __name__ == "__main__":
    layout = build_layout()
    write_pbix(layout)
    print("Done! Open the new PBIX file in Power BI Desktop.")
