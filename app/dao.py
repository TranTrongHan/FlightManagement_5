from app.models import Flight, Route, Airport

def load_route():
    return Route.query.all()

def load_specific_routes(takeoffId = None, landingairportId=None):
    if takeoffId and landingairportId:
        return Route.query.filter(Route.take_off_airport_id == takeoffId, Route.landing_airport_id == landingairportId)

def load_airport_id(airportrole =None):
    if(airportrole):
        query = Route.query.order_by('name').filter(Route.take_off_airport_id)
    else:
        query = Route.query.order_by('name').filter(Route.landing_airport_id)
    return query

def load_airport():
    return Airport.query.all()

def load_flights():
    return Flight.query.all()