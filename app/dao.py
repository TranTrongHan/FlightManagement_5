from app.models import Flight, RouteDetails, Airport


def load_airport():
    return Airport.query.all()


def load_routesdetails(role):
    query = RouteDetails.query
    query = query.filter(RouteDetails.airport_role.__eq__(role))
    return query


def find_flight(departure=None, arrival=None):
    if departure:
        return Flight.query.filter(Flight.route_id == int(departure))
    if arrival:
        return Flight.query.filter(Flight.route_id == arrival)
