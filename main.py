from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import sqlite3
app = FastAPI()


class Address(BaseModel):
    """Address model

    Raises:
        ValueError: will fail on latitude mismatch
        ValueError: will fail on longitude mismatch

    Returns:
        _type_: Model
    """
    id: int
    name: str
    street: str
    city: str
    state: str
    zip: str
    lat: float
    lon: float

    @validator('lat')
    def check_lat(cls, v):
        """Validates latitude value

        Args:
            v (_type_): latitude

        Returns:
            _type_: latitude
        """
        if v < -90 or v > 90:
            raise ValueError('latitude must be between -90 and 90')
        return v

    @validator('lon')
    def check_lon(cls, v):
        """Validates longitude value

        Args:
            v (_type_): longitude

        Returns:
            longitude
             
        """
        if v < -180 or v > 180:
            raise ValueError('longitude must be between -180 and 180')
        return v

        
    @validator('zip')
    def check_zip(cls, v):
        if not v.isnumeric():
            raise ValueError('Invalid zipcode')
        return v

def get_db_connection():
    """creates database connections

    Returns:
        connection
    """
    conn = sqlite3.connect('address.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
async def startup():
    """Create database on startup if does not exist
    """
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.get("/addresses")
async def get_addresses():
    """Gets all address stored in the database

    Returns:
        _type_: [dict]
    """
    conn = get_db_connection()
    addresses = conn.execute('SELECT * FROM addresses').fetchall()
    conn.close()
    return [dict(address) for address in addresses]

@app.get("/addresses/{address_id}")
async def get_address(address_id: int):
    """Gets specific address based on id

    Args:
        address_id (int)

    Raises:
        HTTPException

    Returns:
        _type_: dict
    """
    conn = get_db_connection()
    address = conn.execute('SELECT * FROM addresses WHERE id = ?', (address_id,)).fetchone()
    conn.close()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return dict(address)

@app.post("/addresses")
async def create_address(address: Address):
    """Creates address after validation

    Args:
        address (Address)

    Returns:
        _type_: int
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO addresses (name, street, city, state, zip, lat, lon)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (address.name, address.street, address.city, address.state, address.zip, address.lat, address.lon))
    conn.commit()
    conn.close()
    return {"id": cursor.lastrowid}

@app.put("/addresses/{address_id}")
async def update_address(address_id: int, address: Address):
    """update a address based on address id

    Args:
        address_id (int)
        address (Address)

    Returns:
        _type_: dict
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE addresses
        SET name = ?, street = ?, city = ?, state = ?, zip = ?, lat = ?, lon = ?
        WHERE id = ?
    ''', (address.name, address.street, address.city, address.state, address.zip, address.lat, address.lon, address_id))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Address updated successfully"}

@app.delete("/addresses/{address_id}")
async def delete_address(address_id: int):
    """Deletes a specific address from record

    Args:
        address_id (int)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM addresses WHERE id = ?', (address_id,))
    conn.commit()
    conn.close()
    return {"message": "Address deleted successfully"}
