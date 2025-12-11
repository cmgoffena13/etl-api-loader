TEST_JSON_PARSER_SIMPLE_RESPONSE = [
    {
        "id": 1,
        "name": "Product 1",
        "price": 19.99,
        "category": "Electronics",
    },
    {
        "id": 2,
        "name": "Product 2",
        "price": 29.99,
        "category": "Clothing",
    },
]

TEST_JSON_PARSER_NESTED_RESPONSE = [
    {
        "id": 1,
        "name": "Product 1",
        "price": 19.99,
        "dimensions": {
            "width": 10.5,
            "height": 20.0,
        },
        "meta": {
            "createdAt": "2024-01-01T00:00:00Z",
        },
    },
    {
        "id": 2,
        "name": "Product 2",
        "price": 29.99,
        "dimensions": {
            "width": 15.0,
            "height": 25.0,
        },
        "meta": {
            "createdAt": "2024-01-02T00:00:00Z",
        },
    },
]

TEST_JSON_PARSER_WITH_LISTS_RESPONSE = [
    {
        "id": 1,
        "name": "Product 1",
        "tags": ["electronics", "gadget", "new"],
        "images": ["image1.jpg", "image2.jpg"],
    },
    {
        "id": 2,
        "name": "Product 2",
        "tags": ["clothing", "fashion"],
        "images": ["image3.jpg"],
    },
]

TEST_JSON_PARSER_MULTIPLE_TABLES_RESPONSE = [
    {
        "id": 1,
        "name": "Product 1",
        "price": 19.99,
        "category": "Electronics",
        "reviews": [
            {
                "productId": 1,
                "reviewerName": "John Doe",
                "rating": 5,
                "comment": "Great product!",
            },
            {
                "productId": 1,
                "reviewerName": "Jane Smith",
                "rating": 4,
                "comment": "Good value",
            },
        ],
    },
    {
        "id": 2,
        "name": "Product 2",
        "price": 29.99,
        "category": "Clothing",
        "reviews": [
            {
                "productId": 2,
                "reviewerName": "Bob Wilson",
                "rating": 3,
                "comment": "Average quality",
            },
        ],
    },
]

TEST_JSON_PARSER_LIST_ROOT_RESPONSE = [
    {"id": 1, "title": "Post 1", "body": "Body of post 1"},
    {"id": 2, "title": "Post 2", "body": "Body of post 2"},
    {"id": 3, "title": "Post 3", "body": "Body of post 3"},
]

TEST_JSON_PARSER_DEEPLY_NESTED_RESPONSE = [
    {
        "invoice_id": 1,
        "invoice_date": "2024-01-01",
        "customer_name": "John Doe",
        "total_amount": 150.00,
        "invoice_line_items": [
            {
                "line_item_id": 1,
                "product_name": "Widget A",
                "quantity": 2,
                "unit_price": 50.00,
                "transactions": [
                    {
                        "txn_id": 1,
                        "txn_date": "2024-01-01T10:00:00Z",
                        "txn_amount": 50.00,
                        "payment_method": "credit_card",
                    },
                    {
                        "txn_id": 2,
                        "txn_date": "2024-01-01T11:00:00Z",
                        "txn_amount": 50.00,
                        "payment_method": "credit_card",
                    },
                ],
            },
            {
                "line_item_id": 2,
                "product_name": "Widget B",
                "quantity": 1,
                "unit_price": 50.00,
                "transactions": [
                    {
                        "txn_id": 3,
                        "txn_date": "2024-01-01T12:00:00Z",
                        "txn_amount": 50.00,
                        "payment_method": "paypal",
                    },
                ],
            },
        ],
    },
    {
        "invoice_id": 2,
        "invoice_date": "2024-01-02",
        "customer_name": "Jane Smith",
        "total_amount": 75.00,
        "invoice_line_items": [
            {
                "line_item_id": 3,
                "product_name": "Widget C",
                "quantity": 1,
                "unit_price": 75.00,
                "transactions": [
                    {
                        "txn_id": 4,
                        "txn_date": "2024-01-02T09:00:00Z",
                        "txn_amount": 75.00,
                        "payment_method": "bank_transfer",
                    },
                ],
            },
        ],
    },
]
