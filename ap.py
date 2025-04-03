from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
import pandas as pd
import numpy as np

app = FastAPI()

# ✅ Load JSON data
df = pd.read_json('b1.json')

# ✅ Drop 'Unnamed' columns automatically
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# ✅ Replace NaN and Inf at load time
df.replace([np.nan, np.inf, -np.inf], None, inplace=True)

@app.get("/")
async def root():
    return {"message": "Welcome to the OEE Data API!"}

@app.get("/records")
async def get_all_records(last_id: int = Query(0, description="Fetch new records after this ID")):
    """
    ✅ This endpoint will return only new records where Id > last_id
    ✅ PowerApps will call /records?last_id=<latest_id_it_has>
    ✅ No duplicate records will be returned
    """
    # 🔹 Fetch only records where Id is greater than last_id
    new_data = df[df["Id"] > last_id]

    # 🔹 Convert to JSON format
    cleaned_data = jsonable_encoder(new_data.to_dict(orient="records"))

    return cleaned_data



# @app.get('/total')
# async def get_total_data():
#   clean_data=jsonable_encoder(df.to_dict(orient="total")) 
#   return clean_data

# @app.get("/record/{record_id}")
# async def get_record(record_id: int):
#     record = df[df['Id'] == record_id]

#     if record.empty:
#         raise HTTPException(status_code=404, detail="Record not found")

#     # Clean record before returning
#     cleaned_data = jsonable_encoder(record.to_dict(orient="records")[0])
#     return cleaned_data

# @app.get("/records/shift/{shift_desc}")
# async def get_records_by_shift(shift_desc: str):
#     filtered = df[df['ShiftDesc'].str.lower() == shift_desc.lower()]

#     if filtered.empty:
#         raise HTTPException(status_code=404, detail="No records found for this shift description")

#     cleaned_data = jsonable_encoder(filtered.to_dict(orient="records"))
#     return cleaned_data

# @app.get("/records/oee/{min_oee}")
# async def get_records_by_oee(min_oee: float):
#     filtered = df[df['OEE'] >= min_oee]

#     if filtered.empty:
#         raise HTTPException(status_code=404, detail="No records found with OEE above threshold")

#     cleaned_data = jsonable_encoder(filtered.to_dict(orient="records"))
#     return cleaned_data

# @app.get("/records/{num_records}")
# async def get_records_by_number(num_records: int):
#     if num_records <= 0:
#         raise HTTPException(status_code=400, detail="Number of records must be greater than zero.")

#     # Limit records to the number requested
#     limited_data = df.head(num_records)

#     # If user asks more records than available
#     if limited_data.empty:
#         raise HTTPException(status_code=404, detail=f"No records found for limit {num_records}.")

#     cleaned_data = jsonable_encoder(limited_data.to_dict(orient="records"))
#     return cleaned_data