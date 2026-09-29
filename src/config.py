DATA_PATH = "data/transactions.csv"

# Left side = column name in the DLD file. Right side = the name we use.
COLUMN_MAP = {
    "transaction_id": "transaction_id",
    "instance_date": "date",
    "area_name_en": "area",
    "actual_worth": "price",
    "procedure_area": "size_sqm",
    "trans_group_en": "trans_group",
    "property_type_en": "property_type",
}