"""
Build Power BI Project (PBIP) report definition with dashboard visuals.
Creates report.json and page/visual JSON files in the PBIR enhanced format.
"""
import json, os, uuid

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pbip_project", "SoccerDashboard.Report", "definition")

def uid():
    return str(uuid.uuid4())

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    print(f"  Created: {os.path.relpath(path, BASE)}")

# ---------------------------------------------------------------------------
# Shared helpers for visual config
# ---------------------------------------------------------------------------

def col_ref(alias, prop):
    return {"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop}}

def measure_ref(alias, prop):
    return {"Measure": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop}}

def source_entity(alias, entity):
    return {"Name": alias, "Entity": entity, "Type": 0}

def lit(val):
    return {"expr": {"Literal": {"Value": val}}}

def solid_color(color):
    return {"solid": {"color": lit(f"'{color}'")}}

# Dark theme colors
BG = "#0E1117"
CARD_BG = "#1A1F2E"
BORDER = "#2D3548"
TEXT = "#E0E0E0"
MUTED = "#8B95A5"
ACCENT = "#4FC3F7"
ACCENT2 = "#81C784"
ACCENT3 = "#FFB74D"

# ---------------------------------------------------------------------------
# Visual builders
# ---------------------------------------------------------------------------

def make_card_visual(name, x, y, w, h, table, measure_name, label_color=ACCENT):
    alias = table[0].lower()
    qref = f"{table}.{measure_name}"
    return {
        "name": name,
        "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{"field": measure_ref(alias, measure_name), "queryRef": qref, "active": True}]
                    }
                },
                "sortDefinition": None
            },
            "objects": {
                "labels": [{"properties": {
                    "color": solid_color(label_color),
                    "fontSize": lit("22D")
                }}],
                "categoryLabels": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color(MUTED),
                    "fontSize": lit("10D")
                }}]
            },
            "visualContainerObjects": {
                "background": [{"properties": {
                    "color": solid_color(CARD_BG),
                    "transparency": lit("0D")
                }}],
                "border": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color(BORDER),
                    "radius": lit("8D")
                }}],
                "title": [{"properties": {"show": lit("false")}}]
            },
            "drillFilterOtherVisuals": True
        },
        "filters": [],
        "fromEntities": [source_entity(alias, table)]
    }


def make_map_visual(name, x, y, w, h):
    return {
        "name": name,
        "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "map",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{"field": col_ref("p", "nationality"), "queryRef": "Players.nationality", "active": True}]
                    },
                    "Size": {
                        "projections": [{"field": measure_ref("p", "Player Count by Country"), "queryRef": "Players.Player Count by Country", "active": True}]
                    },
                    "Tooltips": {
                        "projections": [{"field": measure_ref("p", "Total Value by Country"), "queryRef": "Players.Total Value by Country", "active": True}]
                    }
                },
                "sortDefinition": None
            },
            "objects": {
                "bubbles": [{"properties": {
                    "fill": solid_color(ACCENT),
                    "scaleSizeMax": lit("55D")
                }}],
                "categoryLabels": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color("#FFFFFF"),
                    "fontSize": lit("8D")
                }}]
            },
            "visualContainerObjects": {
                "title": [{"properties": {
                    "show": lit("true"),
                    "text": lit("'Player Distribution by Nationality'"),
                    "fontColor": solid_color(TEXT),
                    "fontSize": lit("13D")
                }}],
                "background": [{"properties": {
                    "color": solid_color(CARD_BG),
                    "transparency": lit("0D")
                }}],
                "border": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color(BORDER)
                }}]
            },
            "drillFilterOtherVisuals": True
        },
        "filters": [],
        "fromEntities": [source_entity("p", "Players")]
    }


def make_bar_chart(name, x, y, w, h):
    return {
        "name": name,
        "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{"field": col_ref("c", "current_club_name"), "queryRef": "Club Value Summary.current_club_name", "active": True}]
                    },
                    "Y": {
                        "projections": [{"field": col_ref("c", "Total Value"), "queryRef": "Club Value Summary.Total Value", "active": True}]
                    }
                },
                "sortDefinition": {
                    "sort": [{"field": col_ref("c", "Total Value"), "direction": "Descending"}]
                }
            },
            "objects": {
                "dataPoint": [{"properties": {"fill": solid_color(ACCENT)}}],
                "categoryAxis": [{"properties": {"labelColor": solid_color(MUTED)}}],
                "valueAxis": [{"properties": {
                    "labelColor": solid_color(MUTED),
                    "gridlineColor": solid_color(BORDER)
                }}]
            },
            "visualContainerObjects": {
                "title": [{"properties": {
                    "show": lit("true"),
                    "text": lit("'Market Value by Club (Top 20)'"),
                    "fontColor": solid_color(TEXT),
                    "fontSize": lit("13D")
                }}],
                "background": [{"properties": {
                    "color": solid_color(CARD_BG),
                    "transparency": lit("0D")
                }}],
                "border": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color(BORDER)
                }}]
            },
            "drillFilterOtherVisuals": True
        },
        "filters": [],
        "fromEntities": [source_entity("c", "Club Value Summary")]
    }


def make_table_visual(name, x, y, w, h):
    cols = ["Player Name", "Club", "Age", "Position", "Nationality", "Market Value", "Peak Market Value"]
    projections = []
    for col in cols:
        projections.append({
            "field": col_ref("t", col),
            "queryRef": f"Top Players.{col}",
            "active": True
        })
    return {
        "name": name,
        "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": projections}
                },
                "sortDefinition": {
                    "sort": [{"field": col_ref("t", "Market Value"), "direction": "Descending"}]
                }
            },
            "objects": {
                "grid": [{"properties": {
                    "gridVertical": lit("false"),
                    "gridHorizontal": lit("true"),
                    "gridHorizontalColor": solid_color(BORDER)
                }}],
                "columnHeaders": [{"properties": {
                    "fontColor": solid_color(ACCENT),
                    "backColor": solid_color("#1E2738"),
                    "fontSize": lit("9D")
                }}],
                "values": [{"properties": {
                    "fontColor": solid_color(TEXT),
                    "backColor": solid_color(CARD_BG),
                    "fontSize": lit("9D")
                }}]
            },
            "visualContainerObjects": {
                "title": [{"properties": {
                    "show": lit("true"),
                    "text": lit("'Most Valuable Players'"),
                    "fontColor": solid_color(TEXT),
                    "fontSize": lit("13D")
                }}],
                "background": [{"properties": {
                    "color": solid_color(CARD_BG),
                    "transparency": lit("0D")
                }}],
                "border": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color(BORDER)
                }}]
            },
            "drillFilterOtherVisuals": True
        },
        "filters": [],
        "fromEntities": [source_entity("t", "Top Players")]
    }


def make_donut(name, x, y, w, h):
    return {
        "name": name,
        "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "donutChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{"field": col_ref("p", "position"), "queryRef": "Players.position", "active": True}]
                    },
                    "Y": {
                        "projections": [{"field": measure_ref("p", "Total Players"), "queryRef": "Players.Total Players", "active": True}]
                    }
                },
                "sortDefinition": None
            },
            "objects": {
                "legend": [{"properties": {
                    "show": lit("true"),
                    "labelColor": solid_color(TEXT)
                }}]
            },
            "visualContainerObjects": {
                "title": [{"properties": {
                    "show": lit("true"),
                    "text": lit("'Position Distribution'"),
                    "fontColor": solid_color(TEXT),
                    "fontSize": lit("13D")
                }}],
                "background": [{"properties": {
                    "color": solid_color(CARD_BG),
                    "transparency": lit("0D")
                }}],
                "border": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color(BORDER)
                }}]
            },
            "drillFilterOtherVisuals": True
        },
        "filters": [],
        "fromEntities": [source_entity("p", "Players")]
    }


def make_scatter(name, x, y, w, h):
    return {
        "name": name,
        "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "scatterChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{"field": col_ref("pr", "player_name"), "queryRef": "Predictions.player_name", "active": True}]
                    },
                    "X": {
                        "projections": [{"field": col_ref("pr", "market_value"), "queryRef": "Predictions.market_value", "active": True}]
                    },
                    "Y": {
                        "projections": [{"field": col_ref("pr", "predicted"), "queryRef": "Predictions.predicted", "active": True}]
                    }
                },
                "sortDefinition": None
            },
            "objects": {
                "dataPoint": [{"properties": {"fill": solid_color(ACCENT)}}],
                "categoryAxis": [{"properties": {
                    "labelColor": solid_color(MUTED),
                    "gridlineColor": solid_color(BORDER)
                }}],
                "valueAxis": [{"properties": {
                    "labelColor": solid_color(MUTED),
                    "gridlineColor": solid_color(BORDER)
                }}]
            },
            "visualContainerObjects": {
                "title": [{"properties": {
                    "show": lit("true"),
                    "text": lit("'Actual vs Predicted Market Value'"),
                    "fontColor": solid_color(TEXT),
                    "fontSize": lit("13D")
                }}],
                "background": [{"properties": {
                    "color": solid_color(CARD_BG),
                    "transparency": lit("0D")
                }}],
                "border": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color(BORDER)
                }}]
            },
            "drillFilterOtherVisuals": True
        },
        "filters": [],
        "fromEntities": [source_entity("pr", "Predictions")]
    }


def make_slicer(name, x, y, w, h, table, column):
    alias = table[0].lower()
    return {
        "name": name,
        "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{"field": col_ref(alias, column), "queryRef": f"{table}.{column}", "active": True}]
                    }
                },
                "sortDefinition": None
            },
            "objects": {
                "data": [{"properties": {"mode": lit("'Dropdown'")}}],
                "selection": [{"properties": {
                    "selectAllCheckboxEnabled": lit("true"),
                    "singleSelect": lit("false")
                }}],
                "items": [{"properties": {
                    "fontColor": solid_color(TEXT),
                    "background": solid_color(CARD_BG)
                }}],
                "header": [{"properties": {
                    "fontColor": solid_color(ACCENT)
                }}]
            },
            "visualContainerObjects": {
                "background": [{"properties": {
                    "color": solid_color(CARD_BG),
                    "transparency": lit("0D")
                }}],
                "border": [{"properties": {
                    "show": lit("true"),
                    "color": solid_color(BORDER)
                }}],
                "title": [{"properties": {"show": lit("false")}}]
            },
            "drillFilterOtherVisuals": True
        },
        "filters": [],
        "fromEntities": [source_entity(alias, table)]
    }


def make_textbox(name, x, y, w, h, text, font_size="20pt"):
    return {
        "name": name,
        "position": {"x": x, "y": y, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{"properties": {
                    "paragraphs": [{
                        "textRuns": [{
                            "value": text,
                            "textStyle": {
                                "fontFamily": "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif",
                                "fontSize": font_size,
                                "bold": True,
                                "color": "#FFFFFF"
                            }
                        }]
                    }]
                }}]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": lit("false")}}]
            },
            "drillFilterOtherVisuals": True
        },
        "filters": []
    }


# ---------------------------------------------------------------------------
# Build report definition
# ---------------------------------------------------------------------------

def build_report():
    page_name = uid()

    # Report-level config
    report = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "CY25SU12",
                "reportVersionAtImport": "5.69",
                "type": "SharedResources"
            }
        },
        "defaultDrillFilterOtherVisuals": True,
        "linguisticSchemaSyncVersion": 2,
        "settings": {
            "useNewFilterPaneExperience": True,
            "allowChangeFilterTypes": True,
            "useStylableVisualContainerHeader": True,
            "queryLimitOption": 6,
            "useEnhancedTooltips": True,
            "exportDataMode": 1
        }
    }

    # Page config
    page = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json",
        "name": page_name,
        "displayName": "Market Value Dashboard",
        "displayOption": "FitToPage",
        "width": 1280,
        "height": 720,
        "objects": {
            "background": [{"properties": {
                "color": solid_color(BG),
                "transparency": lit("0D")
            }}],
            "wallpaper": [{"properties": {
                "color": solid_color(BG),
                "transparency": lit("0D")
            }}],
            "outspace": [{"properties": {
                "color": solid_color(BG)
            }}]
        },
        "filters": []
    }

    # Build all visuals
    visuals = {}

    # Row 1: Title + KPI cards (y=5, h=55)
    visuals["title"] = make_textbox(uid(), 15, 5, 550, 48, "Football Player Market Value Analysis")
    visuals["card_players"] = make_card_visual(uid(), 700, 5, 135, 55, "Players", "Total Players", ACCENT)
    visuals["card_value"] = make_card_visual(uid(), 845, 5, 175, 55, "Players", "Total Market Value", ACCENT2)
    visuals["card_top"] = make_card_visual(uid(), 1030, 5, 120, 55, "Players", "Top Player Value", ACCENT3)
    visuals["card_accuracy"] = make_card_visual(uid(), 1160, 5, 110, 55, "Predictions", "Prediction Accuracy", "#CE93D8")

    # Row 2: Slicers (y=65, h=30)
    visuals["slicer_pos"] = make_slicer(uid(), 15, 65, 200, 32, "Players", "position")
    visuals["slicer_tier"] = make_slicer(uid(), 225, 65, 200, 32, "Players", "league_tier")
    visuals["slicer_age"] = make_slicer(uid(), 435, 65, 200, 32, "Players", "age_group")

    # Row 3: Map + Bar + Donut (y=102, h=295)
    visuals["map"] = make_map_visual(uid(), 15, 102, 590, 295)
    visuals["bar"] = make_bar_chart(uid(), 615, 102, 400, 295)
    visuals["donut"] = make_donut(uid(), 1025, 102, 245, 295)

    # Row 4: Table + Scatter (y=405, h=305)
    visuals["table"] = make_table_visual(uid(), 15, 405, 645, 305)
    visuals["scatter"] = make_scatter(uid(), 670, 405, 600, 305)

    return report, page, visuals


def main():
    print("Building PBIP report definition...")

    report, page, visuals = build_report()

    # Write report.json
    write_json(os.path.join(BASE, "report.json"), report)

    # Write pages
    pages_dir = os.path.join(BASE, "pages")
    page_dir = os.path.join(pages_dir, page["name"])
    write_json(os.path.join(page_dir, "page.json"), page)

    # Write visuals
    for vname, vdef in visuals.items():
        visual_dir = os.path.join(page_dir, "visuals", vdef["name"])
        write_json(os.path.join(visual_dir, "visual.json"), vdef)

    print(f"\nDone! Created {len(visuals)} visuals on 1 page.")
    print(f"Open: pbip_project/SoccerDashboard.pbip in Power BI Desktop")


if __name__ == "__main__":
    main()
