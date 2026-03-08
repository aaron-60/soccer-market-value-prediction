"""
Generate a model.bim (Tabular Object Model JSON) file for the Soccer Market Value
Prediction Power BI semantic model.

This script constructs the complete TOM JSON from the TMDL definitions, producing a
valid model.bim that can be imported into Power BI Desktop or Analysis Services.

Usage:
    python src/generate_model_bim.py
"""

import json
import os
import sys


def build_model_bim() -> dict:
    """Build the complete model.bim structure as a Python dictionary."""

    # ──────────────────────────────────────────────────────────────
    # Helper: default summarizeBy based on data type
    # ──────────────────────────────────────────────────────────────
    def _summarize(data_type: str, is_key: bool = False) -> str:
        if is_key:
            return "none"
        if data_type in ("int64", "decimal", "double"):
            return "sum"
        return "none"

    # ──────────────────────────────────────────────────────────────
    # Table 1: Players
    # ──────────────────────────────────────────────────────────────
    players_table = {
        "name": "Players",
        "description": "Main fact table - 31K players with demographics and market values",
        "lineageTag": "d6ae10a3-9de5-40e6-b683-3e384916f1a5",
        "columns": [
            {
                "name": "player_id",
                "dataType": "int64",
                "sourceColumn": "player_id",
                "summarizeBy": "none",
                "lineageTag": "761625c0-8f81-4708-a098-d28efc79ad73"
            },
            {
                "name": "player_name",
                "dataType": "string",
                "sourceColumn": "player_name",
                "summarizeBy": "none",
                "lineageTag": "af1f921e-1657-4ffd-80ed-ff61ab6e225a"
            },
            {
                "name": "position",
                "dataType": "string",
                "sourceColumn": "position",
                "summarizeBy": "none",
                "lineageTag": "7a293319-399f-4d2b-9d28-1a9984eac362"
            },
            {
                "name": "sub_position",
                "dataType": "string",
                "sourceColumn": "sub_position",
                "summarizeBy": "none",
                "lineageTag": "8c7c1729-eab5-4537-b254-1b216eda4519"
            },
            {
                "name": "nationality",
                "dataType": "string",
                "sourceColumn": "nationality",
                "dataCategory": "Country",
                "summarizeBy": "none",
                "lineageTag": "8ce614a5-6e54-476a-a6e7-dee85df1746f"
            },
            {
                "name": "date_of_birth",
                "dataType": "dateTime",
                "sourceColumn": "date_of_birth",
                "summarizeBy": "none",
                "lineageTag": "ddcb8940-cfb2-4846-8512-321595dab82e"
            },
            {
                "name": "age",
                "dataType": "int64",
                "sourceColumn": "age",
                "summarizeBy": "sum",
                "lineageTag": "44dac26a-75bb-43a5-9d39-8f16a0fab543"
            },
            {
                "name": "current_club_id",
                "dataType": "int64",
                "sourceColumn": "current_club_id",
                "summarizeBy": "none",
                "lineageTag": "23b74e93-fdac-410a-8efe-e689484c4dd2"
            },
            {
                "name": "current_club_name",
                "dataType": "string",
                "sourceColumn": "current_club_name",
                "summarizeBy": "none",
                "lineageTag": "0cae8d2b-781a-4c21-96a1-750121b2ee17"
            },
            {
                "name": "league_id",
                "dataType": "string",
                "sourceColumn": "league_id",
                "summarizeBy": "none",
                "lineageTag": "e789d49a-2714-43f6-a58d-1d8f8f7bed86"
            },
            {
                "name": "market_value",
                "dataType": "decimal",
                "sourceColumn": "market_value",
                "formatString": "\u20ac#,##0",
                "displayFolder": "Values",
                "summarizeBy": "sum",
                "lineageTag": "9fba2258-81d4-4896-8785-9b9934d5d1a1"
            },
            {
                "name": "peak_market_value",
                "dataType": "decimal",
                "sourceColumn": "peak_market_value",
                "formatString": "\u20ac#,##0",
                "displayFolder": "Values",
                "summarizeBy": "sum",
                "lineageTag": "c91404fc-c32a-493d-a886-13075a8e59dc"
            },
            {
                "name": "league_tier",
                "dataType": "string",
                "sourceColumn": "league_tier",
                "summarizeBy": "none",
                "lineageTag": "01336086-0a41-4882-b4e0-6198c7f3bc66"
            },
            {
                "name": "age_group",
                "dataType": "string",
                "sourceColumn": "age_group",
                "summarizeBy": "none",
                "lineageTag": "495d704b-5131-4bb4-a27b-0dc37ddb2541"
            }
        ],
        "measures": [
            {
                "name": "Total Players",
                "expression": "COUNTROWS(Players)",
                "formatString": "#,##0",
                "displayFolder": "KPIs",
                "lineageTag": "d8c95c4b-14e6-4685-ae33-b8412744eb97"
            },
            {
                "name": "Total Market Value",
                "expression": "SUM(Players[market_value])",
                "formatString": "\u20ac#,##0,,\"M\"",
                "displayFolder": "KPIs",
                "lineageTag": "8e7b2a6d-e77d-4306-9b32-1d1649b560b5"
            },
            {
                "name": "Avg Market Value",
                "expression": "AVERAGE(Players[market_value])",
                "formatString": "\u20ac#,##0",
                "displayFolder": "KPIs",
                "lineageTag": "b449fc30-8f7d-4dff-a73e-c8107e844472"
            },
            {
                "name": "Avg Age",
                "expression": "AVERAGE(Players[age])",
                "formatString": "0.0",
                "displayFolder": "KPIs",
                "lineageTag": "6f0a3067-1960-446f-b4d4-4a8cc272f651"
            },
            {
                "name": "Player Count by Country",
                "expression": "COUNTROWS(Players)",
                "formatString": "#,##0",
                "displayFolder": "Map",
                "lineageTag": "a57e4a7a-1583-4f12-b563-9dcc0afbbdf3"
            },
            {
                "name": "Total Value by Country",
                "expression": "SUM(Players[market_value])",
                "formatString": "\u20ac#,##0,,\"M\"",
                "displayFolder": "Map",
                "lineageTag": "e511ec6b-92ca-4ec8-96cd-32f5cb017f30"
            },
            {
                "name": "Top Player Value",
                "expression": "MAX(Players[market_value])",
                "formatString": "\u20ac#,##0",
                "displayFolder": "KPIs",
                "lineageTag": "44ef739b-0720-4a25-baef-8c6fe1217caa"
            },
            {
                "name": "Forwards Count",
                "expression": "CALCULATE(COUNTROWS(Players), Players[position] = \"Attack\")",
                "formatString": "#,##0",
                "displayFolder": "Position Breakdown",
                "lineageTag": "dae0621b-25a6-4532-8c8e-fddcfbc879f7"
            },
            {
                "name": "Midfielders Count",
                "expression": "CALCULATE(COUNTROWS(Players), Players[position] = \"Midfield\")",
                "formatString": "#,##0",
                "displayFolder": "Position Breakdown",
                "lineageTag": "b90b82fb-e4ec-42eb-93ed-70d734bb0e45"
            },
            {
                "name": "Defenders Count",
                "expression": "CALCULATE(COUNTROWS(Players), Players[position] = \"Defense\")",
                "formatString": "#,##0",
                "displayFolder": "Position Breakdown",
                "lineageTag": "a3148dfc-9c1d-4c58-a84c-af712aed8eea"
            },
            {
                "name": "Goalkeepers Count",
                "expression": "CALCULATE(COUNTROWS(Players), Players[position] = \"Goalkeeper\")",
                "formatString": "#,##0",
                "displayFolder": "Position Breakdown",
                "lineageTag": "8b6f404b-e764-4c1f-b4c8-e2c22335ffc8"
            }
        ],
        "hierarchies": [
            {
                "name": "Position Hierarchy",
                "lineageTag": "606ccd6c-8e5e-4ecd-ba07-a7a96df0ae1a",
                "levels": [
                    {
                        "name": "Position",
                        "ordinal": 0,
                        "column": "position",
                        "lineageTag": "4e75cc8d-405f-41c4-a99c-6f6a6e83a00a"
                    },
                    {
                        "name": "Sub Position",
                        "ordinal": 1,
                        "column": "sub_position",
                        "lineageTag": "6fb477ba-dadd-497b-b925-83ad4b65b286"
                    }
                ]
            },
            {
                "name": "Age Hierarchy",
                "lineageTag": "ca69a065-2858-409a-bf91-396cc473841a",
                "levels": [
                    {
                        "name": "Age Group",
                        "ordinal": 0,
                        "column": "age_group",
                        "lineageTag": "51465329-5724-43a9-b1de-16f621302db0"
                    },
                    {
                        "name": "Age",
                        "ordinal": 1,
                        "column": "age",
                        "lineageTag": "1eaa2cfc-b3d1-4f61-8d66-03f7725d8aef"
                    }
                ]
            }
        ],
        "partitions": [
            {
                "name": "Players",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": [
                        "let",
                        "    Source = Csv.Document(File.Contents(\"C:\\\\Users\\\\aaron\\\\Desktop\\\\soccer-market-value-prediction\\\\data\\\\processed\\\\powerbi\\\\players.csv\"), [Delimiter=\",\", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.None]),",
                        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                        "    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{\"player_id\", Int64.Type}, {\"player_name\", type text}, {\"position\", type text}, {\"sub_position\", type text}, {\"nationality\", type text}, {\"date_of_birth\", type datetime}, {\"age\", Int64.Type}, {\"current_club_id\", Int64.Type}, {\"current_club_name\", type text}, {\"league_id\", type text}, {\"market_value\", type number}, {\"peak_market_value\", type number}, {\"league_tier\", type text}, {\"age_group\", type text}})",
                        "in",
                        "    ChangedTypes"
                    ]
                }
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # Table 2: Player Stats
    # ──────────────────────────────────────────────────────────────
    player_stats_table = {
        "name": "Player Stats",
        "description": "Career performance statistics",
        "lineageTag": "399cf6a3-bd18-4399-94c9-e2c7c8ec834f",
        "columns": [
            {
                "name": "player_id",
                "dataType": "int64",
                "sourceColumn": "player_id",
                "summarizeBy": "none",
                "lineageTag": "27a56235-f37e-4509-bdae-6fec2cbcf43d"
            },
            {
                "name": "total_appearances",
                "dataType": "int64",
                "sourceColumn": "total_appearances",
                "summarizeBy": "sum",
                "lineageTag": "5eb92ccc-cbce-4d31-af49-fd75e54995ff"
            },
            {
                "name": "total_goals",
                "dataType": "int64",
                "sourceColumn": "total_goals",
                "summarizeBy": "sum",
                "lineageTag": "dd0bc987-1279-4694-afe4-8c4e45f26627"
            },
            {
                "name": "total_assists",
                "dataType": "int64",
                "sourceColumn": "total_assists",
                "summarizeBy": "sum",
                "lineageTag": "5f75df12-830d-4ceb-9a08-b1ab61df0da8"
            },
            {
                "name": "total_minutes",
                "dataType": "int64",
                "sourceColumn": "total_minutes",
                "summarizeBy": "sum",
                "lineageTag": "d4bb6d10-e445-49ea-8d9e-ca802b515d6a"
            },
            {
                "name": "total_yellow_cards",
                "dataType": "int64",
                "sourceColumn": "total_yellow_cards",
                "summarizeBy": "sum",
                "lineageTag": "1a964ed0-dc71-4438-98f9-6ff3e2681e32"
            },
            {
                "name": "total_red_cards",
                "dataType": "int64",
                "sourceColumn": "total_red_cards",
                "summarizeBy": "sum",
                "lineageTag": "d80357f3-c1c9-4a60-b007-c46e79004cb1"
            },
            {
                "name": "goals_per_90",
                "dataType": "decimal",
                "sourceColumn": "goals_per_90",
                "summarizeBy": "sum",
                "lineageTag": "52372180-de9c-4cba-b45d-419153c5fc56"
            },
            {
                "name": "assists_per_90",
                "dataType": "decimal",
                "sourceColumn": "assists_per_90",
                "summarizeBy": "sum",
                "lineageTag": "906b2378-953e-4320-8d21-004e3a6ad881"
            }
        ],
        "measures": [
            {
                "name": "Total Goals",
                "expression": "SUM('Player Stats'[total_goals])",
                "formatString": "#,##0",
                "displayFolder": "Performance",
                "lineageTag": "c4d84efc-ce93-4c24-a35b-8d5081ca97ef"
            },
            {
                "name": "Total Assists",
                "expression": "SUM('Player Stats'[total_assists])",
                "formatString": "#,##0",
                "displayFolder": "Performance",
                "lineageTag": "dabc4c6f-3774-4ed7-a03c-1af4ee5668bf"
            },
            {
                "name": "Total Appearances",
                "expression": "SUM('Player Stats'[total_appearances])",
                "formatString": "#,##0",
                "displayFolder": "Performance",
                "lineageTag": "719e63cd-ec27-4031-9f6e-d588e7221def"
            },
            {
                "name": "Avg Goals per 90",
                "expression": "AVERAGE('Player Stats'[goals_per_90])",
                "formatString": "0.00",
                "displayFolder": "Performance",
                "lineageTag": "a0022cb6-a568-49df-9f9c-0146a88e5b46"
            }
        ],
        "partitions": [
            {
                "name": "Player Stats",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": [
                        "let",
                        "    Source = Csv.Document(File.Contents(\"C:\\\\Users\\\\aaron\\\\Desktop\\\\soccer-market-value-prediction\\\\data\\\\processed\\\\powerbi\\\\player_stats.csv\"), [Delimiter=\",\", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),",
                        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                        "    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{\"player_id\", Int64.Type}, {\"total_appearances\", Int64.Type}, {\"total_goals\", Int64.Type}, {\"total_assists\", Int64.Type}, {\"total_minutes\", Int64.Type}, {\"total_yellow_cards\", Int64.Type}, {\"total_red_cards\", Int64.Type}, {\"goals_per_90\", type number}, {\"assists_per_90\", type number}})",
                        "in",
                        "    ChangedTypes"
                    ]
                }
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # Table 3: Clubs
    # ──────────────────────────────────────────────────────────────
    clubs_table = {
        "name": "Clubs",
        "description": "Club dimension table",
        "lineageTag": "2b529414-fec7-4fa4-a74c-7b157a13ce7f",
        "columns": [
            {
                "name": "club_id",
                "dataType": "int64",
                "sourceColumn": "club_id",
                "summarizeBy": "none",
                "lineageTag": "f098c1f0-7b54-4de2-aa84-b41de4db6cc1"
            },
            {
                "name": "club_name",
                "dataType": "string",
                "sourceColumn": "club_name",
                "summarizeBy": "none",
                "lineageTag": "0cca539f-10c5-4912-961d-79e65602faa4"
            },
            {
                "name": "league_id",
                "dataType": "string",
                "sourceColumn": "league_id",
                "summarizeBy": "none",
                "lineageTag": "a4128870-79a9-4eae-85d1-8d92d86782e5"
            },
            {
                "name": "club_total_value",
                "dataType": "decimal",
                "sourceColumn": "club_total_value",
                "summarizeBy": "sum",
                "lineageTag": "8f9ddf2c-ac05-4cb6-b10b-c57ca383c36d"
            },
            {
                "name": "squad_size",
                "dataType": "int64",
                "sourceColumn": "squad_size",
                "summarizeBy": "sum",
                "lineageTag": "4e23d11c-517d-4a06-908c-6e97cb66f22f"
            },
            {
                "name": "club_avg_age",
                "dataType": "decimal",
                "sourceColumn": "club_avg_age",
                "summarizeBy": "sum",
                "lineageTag": "899f7597-d0dc-4c3b-abc9-e55dd0b40c96"
            },
            {
                "name": "stadium_name",
                "dataType": "string",
                "sourceColumn": "stadium_name",
                "summarizeBy": "none",
                "lineageTag": "803f2080-3b8f-4234-b8f7-c8f8ff1f1363"
            },
            {
                "name": "stadium_seats",
                "dataType": "int64",
                "sourceColumn": "stadium_seats",
                "summarizeBy": "sum",
                "lineageTag": "38e9dd66-fb95-4631-9cba-363d99882020"
            }
        ],
        "measures": [
            {
                "name": "Market Value by Club",
                "expression": "CALCULATE(SUM(Players[market_value]))",
                "formatString": "\u20ac#,##0,,\"M\"",
                "displayFolder": "Club Analysis",
                "lineageTag": "630e5434-afaa-4c15-b894-2fc48b6fcf29"
            },
            {
                "name": "Squad Size",
                "expression": "CALCULATE(COUNTROWS(Players))",
                "formatString": "#,##0",
                "displayFolder": "Club Analysis",
                "lineageTag": "41edbdb8-abfd-45d8-8549-ae9b7ab6dd96"
            }
        ],
        "partitions": [
            {
                "name": "Clubs",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": [
                        "let",
                        "    Source = Csv.Document(File.Contents(\"C:\\\\Users\\\\aaron\\\\Desktop\\\\soccer-market-value-prediction\\\\data\\\\processed\\\\powerbi\\\\clubs.csv\"), [Delimiter=\",\", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),",
                        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                        "    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{\"club_id\", Int64.Type}, {\"club_name\", type text}, {\"league_id\", type text}, {\"club_total_value\", type number}, {\"squad_size\", Int64.Type}, {\"club_avg_age\", type number}, {\"stadium_name\", type text}, {\"stadium_seats\", Int64.Type}})",
                        "in",
                        "    ChangedTypes"
                    ]
                }
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # Table 4: Leagues
    # ──────────────────────────────────────────────────────────────
    leagues_table = {
        "name": "Leagues",
        "description": "League/competition dimension table",
        "lineageTag": "6cdfa6d4-9286-4365-b32d-dfd9f71cc685",
        "columns": [
            {
                "name": "league_id",
                "dataType": "string",
                "sourceColumn": "league_id",
                "summarizeBy": "none",
                "lineageTag": "2a49aaef-0aa2-47bc-aa26-b22c5253c8d6"
            },
            {
                "name": "league_name",
                "dataType": "string",
                "sourceColumn": "league_name",
                "summarizeBy": "none",
                "lineageTag": "ed5632eb-7fbc-4fa0-a69e-c2b7d0daf39d"
            },
            {
                "name": "country_name",
                "dataType": "string",
                "sourceColumn": "country_name",
                "summarizeBy": "none",
                "lineageTag": "37197ced-2a68-426f-8922-3fe770ed6628"
            },
            {
                "name": "competition_type",
                "dataType": "string",
                "sourceColumn": "competition_type",
                "summarizeBy": "none",
                "lineageTag": "1610de9c-ad84-473e-a392-cfa2ff2e541f"
            }
        ],
        "partitions": [
            {
                "name": "Leagues",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": [
                        "let",
                        "    Source = Csv.Document(File.Contents(\"C:\\\\Users\\\\aaron\\\\Desktop\\\\soccer-market-value-prediction\\\\data\\\\processed\\\\powerbi\\\\leagues.csv\"), [Delimiter=\",\", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),",
                        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                        "    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{\"league_id\", type text}, {\"league_name\", type text}, {\"country_name\", type text}, {\"competition_type\", type text}})",
                        "in",
                        "    ChangedTypes"
                    ]
                }
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # Table 5: Predictions
    # ──────────────────────────────────────────────────────────────
    predictions_table = {
        "name": "Predictions",
        "description": "ML model predictions vs actual values",
        "lineageTag": "a8c8d9ff-18f3-4854-8dd1-0b87e710e345",
        "columns": [
            {
                "name": "player_name",
                "dataType": "string",
                "sourceColumn": "player_name",
                "summarizeBy": "none",
                "lineageTag": "69f81e99-ffe4-4201-ac2b-f01301901c1d"
            },
            {
                "name": "age",
                "dataType": "int64",
                "sourceColumn": "age",
                "summarizeBy": "sum",
                "lineageTag": "88aa102e-3307-43f1-b77c-8fbc633a57a9"
            },
            {
                "name": "position_group",
                "dataType": "string",
                "sourceColumn": "position_group",
                "summarizeBy": "none",
                "lineageTag": "ae4b7fa7-afb5-4d89-82d4-84608cd5ae79"
            },
            {
                "name": "current_club_name",
                "dataType": "string",
                "sourceColumn": "current_club_name",
                "summarizeBy": "none",
                "lineageTag": "1e850fd1-2ddd-40f8-b9cd-68841c897437"
            },
            {
                "name": "market_value",
                "dataType": "decimal",
                "sourceColumn": "market_value",
                "formatString": "\u20ac#,##0",
                "summarizeBy": "sum",
                "lineageTag": "f4930b66-14ab-4c25-b366-f0b1ea0e1f86"
            },
            {
                "name": "predicted",
                "dataType": "decimal",
                "sourceColumn": "predicted",
                "formatString": "\u20ac#,##0",
                "summarizeBy": "sum",
                "lineageTag": "8aaf11a8-4beb-4e60-b399-c488e13d94aa"
            },
            {
                "name": "error",
                "dataType": "decimal",
                "sourceColumn": "error",
                "formatString": "\u20ac#,##0",
                "summarizeBy": "sum",
                "lineageTag": "28883f3b-da32-43a0-99db-4e72ae571a7a"
            },
            {
                "name": "error_pct",
                "dataType": "decimal",
                "sourceColumn": "error_pct",
                "formatString": "0.00%",
                "summarizeBy": "sum",
                "lineageTag": "047f5db6-050d-4488-af17-4e7c039d0302"
            }
        ],
        "measures": [
            {
                "name": "Prediction Accuracy",
                "expression": "1 - AVERAGEX(Predictions, ABS(Predictions[error_pct]))",
                "formatString": "0.0%",
                "displayFolder": "ML Predictions",
                "lineageTag": "e145cf92-96ca-4b2d-bd09-d206b7c1d95d"
            },
            {
                "name": "Avg Prediction Error",
                "expression": "AVERAGE(Predictions[error_pct])",
                "formatString": "0.00%",
                "displayFolder": "ML Predictions",
                "lineageTag": "324646ef-cb7e-448e-aad3-86fef3b4e61b"
            },
            {
                "name": "Total Predicted Value",
                "expression": "SUM(Predictions[predicted])",
                "formatString": "\u20ac#,##0,,\"M\"",
                "displayFolder": "ML Predictions",
                "lineageTag": "de22b52a-56ca-4b04-9432-9a5d20ce244b"
            }
        ],
        "partitions": [
            {
                "name": "Predictions",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": [
                        "let",
                        "    Source = Csv.Document(File.Contents(\"C:\\\\Users\\\\aaron\\\\Desktop\\\\soccer-market-value-prediction\\\\data\\\\processed\\\\powerbi\\\\predictions.csv\"), [Delimiter=\",\", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),",
                        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
                        "    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{\"player_name\", type text}, {\"age\", Int64.Type}, {\"position_group\", type text}, {\"current_club_name\", type text}, {\"market_value\", type number}, {\"predicted\", type number}, {\"error\", type number}, {\"error_pct\", type number}})",
                        "in",
                        "    ChangedTypes"
                    ]
                }
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # Table 6: Country Summary (calculated table)
    # ──────────────────────────────────────────────────────────────
    country_summary_table = {
        "name": "Country Summary",
        "lineageTag": "1f39f781-317c-4c76-ab14-4e8b95686a8b",
        "columns": [
            {
                "name": "nationality",
                "dataType": "string",
                "sourceColumn": "Players[nationality]",
                "dataCategory": "Country",
                "isNameInferred": True,
                "summarizeBy": "none",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Player Count",
                "dataType": "int64",
                "sourceColumn": "[Player Count]",
                "formatString": "#,##0",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Total Market Value",
                "dataType": "decimal",
                "sourceColumn": "[Total Market Value]",
                "formatString": "\u20ac#,##0",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Avg Market Value",
                "dataType": "decimal",
                "sourceColumn": "[Avg Market Value]",
                "formatString": "\u20ac#,##0",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Top Player Value",
                "dataType": "decimal",
                "sourceColumn": "[Top Player Value]",
                "formatString": "\u20ac#,##0",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            }
        ],
        "partitions": [
            {
                "name": "Country Summary",
                "mode": "import",
                "source": {
                    "type": "calculated",
                    "expression": "SUMMARIZE(Players, Players[nationality], \"Player Count\", COUNTROWS(Players), \"Total Market Value\", SUM(Players[market_value]), \"Avg Market Value\", AVERAGE(Players[market_value]), \"Top Player Value\", MAX(Players[market_value]))"
                }
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # Table 7: Top Players (calculated table)
    # ──────────────────────────────────────────────────────────────
    top_players_table = {
        "name": "Top Players",
        "lineageTag": "f0be153a-61ba-46a0-a14d-4bd56246ce30",
        "columns": [
            {
                "name": "Player Name",
                "dataType": "string",
                "sourceColumn": "[Player Name]",
                "isNameInferred": True,
                "summarizeBy": "none",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Club",
                "dataType": "string",
                "sourceColumn": "[Club]",
                "isNameInferred": True,
                "summarizeBy": "none",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Age",
                "dataType": "int64",
                "sourceColumn": "[Age]",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Position",
                "dataType": "string",
                "sourceColumn": "[Position]",
                "isNameInferred": True,
                "summarizeBy": "none",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Sub Position",
                "dataType": "string",
                "sourceColumn": "[Sub Position]",
                "isNameInferred": True,
                "summarizeBy": "none",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Nationality",
                "dataType": "string",
                "sourceColumn": "[Nationality]",
                "dataCategory": "Country",
                "isNameInferred": True,
                "summarizeBy": "none",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Market Value",
                "dataType": "decimal",
                "sourceColumn": "[Market Value]",
                "formatString": "\u20ac#,##0",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Peak Market Value",
                "dataType": "decimal",
                "sourceColumn": "[Peak Market Value]",
                "formatString": "\u20ac#,##0",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            }
        ],
        "partitions": [
            {
                "name": "Top Players",
                "mode": "import",
                "source": {
                    "type": "calculated",
                    "expression": "TOPN(50, SELECTCOLUMNS(Players, \"Player Name\", Players[player_name], \"Club\", Players[current_club_name], \"Age\", Players[age], \"Position\", Players[position], \"Sub Position\", Players[sub_position], \"Nationality\", Players[nationality], \"Market Value\", Players[market_value], \"Peak Market Value\", Players[peak_market_value]), [Market Value], DESC)"
                }
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # Table 8: Club Value Summary (calculated table)
    # ──────────────────────────────────────────────────────────────
    club_value_summary_table = {
        "name": "Club Value Summary",
        "lineageTag": "3bb4b7b5-e87c-42ba-9274-c91ee30e7c68",
        "columns": [
            {
                "name": "current_club_name",
                "dataType": "string",
                "sourceColumn": "Players[current_club_name]",
                "isNameInferred": True,
                "summarizeBy": "none",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Total Value",
                "dataType": "decimal",
                "sourceColumn": "[Total Value]",
                "formatString": "\u20ac#,##0,,\"M\"",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Player Count",
                "dataType": "int64",
                "sourceColumn": "[Player Count]",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            },
            {
                "name": "Avg Player Value",
                "dataType": "decimal",
                "sourceColumn": "[Avg Player Value]",
                "formatString": "\u20ac#,##0",
                "isNameInferred": True,
                "summarizeBy": "sum",
                "annotations": [
                    {
                        "name": "SummarizationSetBy",
                        "value": "Automatic"
                    }
                ]
            }
        ],
        "partitions": [
            {
                "name": "Club Value Summary",
                "mode": "import",
                "source": {
                    "type": "calculated",
                    "expression": "TOPN(20, SUMMARIZE(Players, Players[current_club_name], \"Total Value\", SUM(Players[market_value]), \"Player Count\", COUNTROWS(Players), \"Avg Player Value\", AVERAGE(Players[market_value])), [Total Value], DESC)"
                }
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # Relationships
    # ──────────────────────────────────────────────────────────────
    relationships = [
        {
            "name": "Players_current_club_id_Clubs_club_id",
            "fromTable": "Players",
            "fromColumn": "current_club_id",
            "toTable": "Clubs",
            "toColumn": "club_id",
            "crossFilteringBehavior": "bothDirections"
        },
        {
            "name": "Players_league_id_Leagues_league_id",
            "fromTable": "Players",
            "fromColumn": "league_id",
            "toTable": "Leagues",
            "toColumn": "league_id",
            "crossFilteringBehavior": "bothDirections"
        },
        {
            "name": "Player Stats_player_id_Players_player_id",
            "fromTable": "Player Stats",
            "fromColumn": "player_id",
            "toTable": "Players",
            "toColumn": "player_id",
            "crossFilteringBehavior": "bothDirections"
        }
    ]

    # ──────────────────────────────────────────────────────────────
    # Cultures
    # ──────────────────────────────────────────────────────────────
    cultures = [
        {
            "name": "en-US",
            "linguisticMetadata": {
                "content": {
                    "Version": "1.0.0",
                    "Language": "en-US"
                },
                "contentType": "json"
            }
        }
    ]

    # ──────────────────────────────────────────────────────────────
    # Annotations (model-level)
    # ──────────────────────────────────────────────────────────────
    annotations = [
        {
            "name": "__PBI_TimeIntelligenceEnabled",
            "value": "1"
        },
        {
            "name": "PBI_ProTooling",
            "value": "[\"MCP-PBIModeling\"]"
        }
    ]

    # ──────────────────────────────────────────────────────────────
    # Assemble the full model.bim
    # ──────────────────────────────────────────────────────────────
    model_bim = {
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-CA",
            "tables": [
                players_table,
                player_stats_table,
                clubs_table,
                leagues_table,
                predictions_table,
                country_summary_table,
                top_players_table,
                club_value_summary_table
            ],
            "relationships": relationships,
            "cultures": cultures,
            "annotations": annotations
        }
    }

    return model_bim


def write_model_bim(model_bim: dict, output_path: str) -> None:
    """Write the model.bim dictionary to a JSON file with proper formatting."""

    # Ensure the euro sign is written as the actual character, not as \u20ac
    json_str = json.dumps(model_bim, indent=2, ensure_ascii=False)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_str)

    print(f"model.bim written to: {output_path}")
    print(f"File size: {os.path.getsize(output_path):,} bytes")


def main():
    output_path = os.path.join(
        r"C:\Users\aaron\Desktop\soccer-market-value-prediction",
        "pbip_project",
        "SoccerDashboard.SemanticModel",
        "model.bim"
    )

    print("Building model.bim from embedded definitions...")
    model_bim = build_model_bim()

    # Quick validation
    tables = model_bim["model"]["tables"]
    relationships = model_bim["model"]["relationships"]
    total_columns = sum(len(t.get("columns", [])) for t in tables)
    total_measures = sum(len(t.get("measures", [])) for t in tables)
    total_hierarchies = sum(len(t.get("hierarchies", [])) for t in tables)

    print(f"  Tables:        {len(tables)}")
    print(f"  Columns:       {total_columns}")
    print(f"  Measures:      {total_measures}")
    print(f"  Hierarchies:   {total_hierarchies}")
    print(f"  Relationships: {len(relationships)}")

    write_model_bim(model_bim, output_path)
    print("Done.")


if __name__ == "__main__":
    main()
