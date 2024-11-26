from app.config.database import get_db
from bson import ObjectId
from datetime import datetime

def create_new_reservation(data, current_user):
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(current_user)})
    if not user:
        return {"status": "error", "message": "User not found"}, 404

    # Check if the requested time is during church service
    if is_service_time(data['date'], data['startTime'], data['endTime'], data['location']):
        return {
            "status": "error",
            "message": "Não é possível reservar o templo durante os horários de culto:\n" +
                      "- Terças-feiras das 21:00 às 23:00\n" +
                      "- Sábados das 19:00 às 22:00\n" +
                      "- Domingos das 07:00 às 13:00"
        }, 400

    # Check for conflicts
    existing = check_reservation_conflict(data)
    if existing:
        conflict_user = db.users.find_one({"_id": ObjectId(existing['user_id'])})
        conflict_user_name = conflict_user.get('name', existing['user_id']) if conflict_user else existing['user_id']
        
        return {
            "status": "error",
            "message": "Conflito de horário detectado",
            "conflict": {
                "date": existing['date'],
                "startTime": existing['startTime'],
                "endTime": existing['endTime'],
                "location": existing['location'],
                "description": existing['description'],
                "responsible": existing['responsible'],
                "user": conflict_user_name,
                "email": conflict_user.get('email', '')
            }
        }, 409

    new_reservation = {
        "user_id": current_user,
        "date": data['date'],
        "startTime": data['startTime'],
        "endTime": data['endTime'],
        "location": data['location'],
        "description": data['description'],
        "responsible": user['name'],  # Use the authenticated user's name
        "email": data.get('email', user.get('email', '')),  # Use provided email or user's email as fallback
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        result = db.rooms.insert_one(new_reservation)
        new_reservation['_id'] = str(result.inserted_id)
        return {
            "status": "success",
            "message": "Reserva criada com sucesso",
            "reservation": new_reservation
        }, 201
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao criar reserva: {str(e)}"
        }, 500

def check_reservation_conflict(data):
    db = get_db()
    return db.rooms.find_one({
        "date": data['date'],
        "location": data['location'],
        "$or": [
            {
                "startTime": {"$lt": data['endTime']},
                "endTime": {"$gt": data['startTime']}
            },
            {
                "startTime": data['startTime'],
                "endTime": data['endTime']
            }
        ]
    })

def get_reservations_by_date(date):
    db = get_db()
    try:
        reservations = list(db.rooms.find({"date": date}))
        for reservation in reservations:
            reservation['_id'] = str(reservation['_id'])
            user = db.users.find_one({"_id": ObjectId(reservation['user_id'])})
            if user:
                reservation['user_name'] = user.get('name', '')
                reservation['user_email'] = user.get('email', '')
        return {"status": "success", "reservations": reservations}, 200
    except Exception as e:
        return {"status": "error", "message": f"Error fetching reservations: {str(e)}"}, 500

def get_date_range_reservations(start_date_str, end_date_str):
    try:
        print(f"[SERVICE] Getting reservations for date range: {start_date_str} to {end_date_str}")
        
        # Get database connection
        db = get_db()
        print(f"[SERVICE] Connected to database: {db.name}")
        
        # Print all collections in the database
        print(f"[SERVICE] Available collections: {db.list_collection_names()}")
        
        # Print a sample document from the rooms collection
        sample_doc = db.rooms.find_one()
        print(f"[SERVICE] Sample reservation document: {sample_doc}")
        
        # Build the query
        query = {
            'date': {
                '$gte': start_date_str,
                '$lte': end_date_str
            }
        }
        print(f"[SERVICE] Executing query: {query}")
        
        # Execute query on the rooms collection
        reservations = list(db.rooms.find(query).sort('date', 1))
        print(f"[SERVICE] Found {len(reservations)} reservations")
        
        if len(reservations) == 0:
            # If no results, let's check what dates are actually in the database
            distinct_dates = db.rooms.distinct('date')
            print(f"[SERVICE] Available dates in database: {distinct_dates}")
        
        # Convert ObjectId to string for JSON serialization
        for reservation in reservations:
            reservation['_id'] = str(reservation['_id'])
            if 'user_id' in reservation:
                # Get user info
                user = db.users.find_one({'_id': ObjectId(reservation['user_id'])})
                if user:
                    reservation['user_email'] = user.get('email', '')
        
        result = {"status": "success", "reservations": reservations}
        print(f"[SERVICE] Returning result: {result}")
        return result, 200
        
    except Exception as e:
        error_msg = f"[SERVICE] Error in get_date_range_reservations: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}, 500

def update_reservation_by_id(id, data):
    try:
        db = get_db()
        reservation = db.rooms.find_one({"_id": ObjectId(id)})
        if not reservation:
            return {"status": "error", "message": "Reservation not found"}, 404

        # Check for conflicts with other reservations
        conflict = db.rooms.find_one({
            "_id": {"$ne": ObjectId(id)},
            "date": data['date'],
            "location": data['location'],
            "$or": [
                {
                    "startTime": {"$lt": data['endTime']},
                    "endTime": {"$gt": data['startTime']}
                },
                {
                    "startTime": data['startTime'],
                    "endTime": data['endTime']
                }
            ]
        })

        if conflict:
            conflict_user = db.users.find_one({"_id": ObjectId(conflict['user_id'])})
            return {
                "status": "error",
                "message": "Conflito de horário detectado",
                "conflict": {
                    "date": conflict['date'],
                    "startTime": conflict['startTime'],
                    "endTime": conflict['endTime'],
                    "location": conflict['location'],
                    "description": conflict['description'],
                    "responsible": conflict['responsible'],
                    "user": conflict_user.get('name', '') if conflict_user else '',
                    "email": conflict_user.get('email', '') if conflict_user else ''
                }
            }, 409

        # Check if the requested time is during church service
        if is_service_time(data['date'], data['startTime'], data['endTime'], data['location']):
            return {
                "status": "error",
                "message": "Não é possível reservar o templo durante os horários de culto:\n" +
                          "- Terças-feiras das 21:00 às 23:00\n" +
                          "- Sábados das 19:00 às 22:00\n" +
                          "- Domingos das 07:00 às 13:00"
            }, 400

        update_data = {
            **data,
            "updated_at": datetime.utcnow()
        }

        db.rooms.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )

        updated_reservation = db.rooms.find_one({"_id": ObjectId(id)})
        updated_reservation['_id'] = str(updated_reservation['_id'])
        
        return {
            "status": "success",
            "message": "Reserva atualizada com sucesso",
            "reservation": updated_reservation
        }, 200

    except Exception as e:
        return {"status": "error", "message": f"Error updating reservation: {str(e)}"}, 500

def delete_reservation_by_id(id):
    try:
        db = get_db()
        result = db.rooms.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return {"status": "error", "message": "Reservation not found"}, 404
        return {"status": "success", "message": "Reserva excluída com sucesso"}, 200
    except Exception as e:
        return {"status": "error", "message": f"Error deleting reservation: {str(e)}"}, 500

def get_user_reservations(user_id):
    """Get all reservations for a specific user."""
    db = get_db()
    try:
        reservations = list(db.rooms.find({"user_id": user_id}))
        for reservation in reservations:
            reservation['_id'] = str(reservation['_id'])
        return {"status": "success", "reservations": reservations}, 200
    except Exception as e:
        print(f"Error getting user reservations: {str(e)}")
        return {"status": "error", "message": "Failed to fetch reservations"}, 500

def get_all_reservations():
    """Get all reservations in the system."""
    db = get_db()
    try:
        reservations = list(db.rooms.find())
        for reservation in reservations:
            reservation['_id'] = str(reservation['_id'])
            if 'user_id' in reservation:
                # Get user details
                user = db.users.find_one({"_id": ObjectId(reservation['user_id'])})
                if user:
                    reservation['user_name'] = user.get('name', 'Unknown')
                    reservation['user_email'] = user.get('email', 'Unknown')
        
        return {"status": "success", "reservations": reservations}, 200
    except Exception as e:
        print(f"Error getting all reservations: {str(e)}")
        return {"status": "error", "message": "Failed to fetch reservations"}, 500

def is_service_time(date_str, start_time, end_time, location):
    """Check if the requested time slot conflicts with church service times."""
    if location.lower() != 'templo':
        return False

    # Convert date string to datetime object to get day of week
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_week = date.weekday()  # Monday is 0, Sunday is 6
        
        # Convert time strings to comparable format (assuming HH:mm format)
        start = datetime.strptime(start_time, '%H:%M').time()
        end = datetime.strptime(end_time, '%H:%M').time()
        
        # Define blocked time slots
        blocked_slots = {
            1: [('21:00', '23:00')],  # Tuesday
            5: [('19:00', '22:00')],  # Saturday
            6: [('07:00', '13:00')]   # Sunday
        }
        
        if day_of_week in blocked_slots:
            for blocked_start, blocked_end in blocked_slots[day_of_week]:
                blocked_start_time = datetime.strptime(blocked_start, '%H:%M').time()
                blocked_end_time = datetime.strptime(blocked_end, '%H:%M').time()
                
                # Check if there's any overlap with blocked time
                if (start < blocked_end_time and end > blocked_start_time):
                    return True
                    
        return False
    except ValueError as e:
        print(f"Error parsing date/time: {str(e)}")
        return False
