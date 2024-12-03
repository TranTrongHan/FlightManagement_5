
def view_ticket(ticket):
    ticket_quantity, total_amount = 0, 0
    if ticket:
        for c in ticket.values():
            ticket_quantity = c['quantity']
            total_amount += c['quantity'] * c['unitprice']
    return {
        'total_amount': total_amount,
        'ticket_quantity': ticket_quantity
    }
