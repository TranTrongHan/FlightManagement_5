function viewTicket(id,customer,flight,route,takeoff_airport,landing_airport,
takeoff_time,landing_time,seat,fareclass,quantity,unitprice){
    event.preventDefault()

    fetch('/api/payment',{
        method:'post',
        body:JSON.stringify({
            'id' :id,
            'customer':customer,
            'flight':flight,
            'route':route,
            'takeoff_airport': takeoff_airport,
            'landing_airport' : landing_airport,
            'takeoff_time':takeoff_time,
            'landing_time':landing_time,
            'seat':seat,
            'fareclass':fareclass,
            'quantity':quantity,
            'unitprice':unitprice
        }),
        headers:{
            'Content-type':'application/json'
        }
    }).then(res => res.json()).then(data =>{
        console.info(data)
    })
}