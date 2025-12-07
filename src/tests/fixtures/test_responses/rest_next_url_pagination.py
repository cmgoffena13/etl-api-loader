TEST_REST_NEXT_URL_PAGINATION_PAGE_1_RESPONSE = {
    "count": 5,
    "next_url": "https://api.example.com/items?page=2",
    "results": [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
        {"id": 3, "name": "Item 3"},
        {"id": 4, "name": "Item 4"},
        {"id": 5, "name": "Item 5"},
    ],
}

TEST_REST_NEXT_URL_PAGINATION_PAGE_2_RESPONSE = {
    "count": 5,
    "next_url": "https://api.example.com/items?page=3",
    "results": [
        {"id": 6, "name": "Item 6"},
        {"id": 7, "name": "Item 7"},
        {"id": 8, "name": "Item 8"},
        {"id": 9, "name": "Item 9"},
        {"id": 10, "name": "Item 10"},
    ],
}

TEST_REST_NEXT_URL_PAGINATION_PAGE_3_RESPONSE = {
    "count": 2,
    "next_url": None,
    "results": [
        {"id": 11, "name": "Item 11"},
        {"id": 12, "name": "Item 12"},
    ],
}
