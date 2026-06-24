from __future__ import annotations

from update_artificial_analysis import CellSnapshot, HeaderSnapshot, extract_table


def test_action_only_column_is_dropped_without_header_name() -> None:
    headers: list[HeaderSnapshot] = [{"text": "Model"}, {"text": "Unrelated Header"}]
    rows: list[list[CellSnapshot]] = [
        [
            {"text": "Claude", "linkText": "", "hasLink": False, "imageAlts": []},
            {
                "text": "Model Providers",
                "linkText": "Model Providers",
                "hasLink": True,
                "imageAlts": [],
            },
        ],
        [
            {"text": "Gemini", "linkText": "", "hasLink": False, "imageAlts": []},
            {
                "text": "Model Providers",
                "linkText": "Model Providers",
                "hasLink": True,
                "imageAlts": [],
            },
        ],
    ]

    display_headers, extracted_rows = extract_table({"headers": headers, "rows": rows})

    assert display_headers == ["Model"]
    assert extracted_rows == [["Claude"], ["Gemini"]]


def test_extra_cell_without_header_raises_instead_of_truncating() -> None:
    headers: list[HeaderSnapshot] = [{"text": "Model"}, {"text": "Creator"}]
    rows: list[list[CellSnapshot]] = [
        [
            {"text": "Claude", "linkText": "", "hasLink": False, "imageAlts": []},
            {"text": "Anthropic", "linkText": "", "hasLink": False, "imageAlts": []},
            {"text": "Extra", "linkText": "", "hasLink": False, "imageAlts": []},
        ]
    ]

    try:
        extract_table({"headers": headers, "rows": rows})
    except ValueError as exc:
        assert str(exc) == "Expected 2 raw columns per row; mismatches: row 1: 3"
    else:
        raise AssertionError("expected extract_table to reject unheadered cells")


def test_cell_text_preferred_over_duplicate_image_alt() -> None:
    display_headers, rows = extract_table(
        {
            "headers": [{"text": "Creator"}],
            "rows": [
                [
                    {
                        "text": "Anthropic",
                        "linkText": "",
                        "hasLink": False,
                        "imageAlts": ["Anthropic"],
                    }
                ]
            ],
        }
    )

    assert display_headers == ["Creator"]
    assert rows == [["Anthropic"]]


def test_image_alt_fallback_when_text_empty() -> None:
    display_headers, rows = extract_table(
        {
            "headers": [{"text": "Provider"}],
            "rows": [
                [
                    {
                        "text": "",
                        "linkText": "",
                        "hasLink": False,
                        "imageAlts": ["Provider X"],
                    }
                ]
            ],
        }
    )

    assert display_headers == ["Provider"]
    assert rows == [["Provider X"]]
