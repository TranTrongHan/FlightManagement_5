function pay(){
     if (confirm('Ban muon thanh toan khong') == true){
        fetch('/api/payment',{
            method:'post',
        }).then(res => res.json()).then(data =>{
            if (data.code == 200){
                window.location.href = data.redirect_url;
            }else {
                alert('Có lỗi xảy ra trong quá trình thanh toán. Đang chuyển về trang đặt vé...');
                window.location.href = data.redirect_url;  // Chuyển hướng đến trang đặt vé
            }
        }).catch(err => console.error(err))
     }
}

function view_ticket_info(flightid,customerid,fareclassid,quantity,plane){
    fetch('/api/create_ticket_info',{
        method:'post',
        body:JSON.stringify({
            'flightid':flightid,
            'customerid':customerid,
            'fareclassid':fareclassid,
            'quantity':quantity,
            'plane':plane
        }),
        headers:{
            'Content-Type':'application/json'
        }
    })
}

