[1mdiff --git a/.idea/FlightManagement_5.iml b/.idea/FlightManagement_5.iml[m
[1mindex b6731d8..efe646f 100644[m
[1m--- a/.idea/FlightManagement_5.iml[m
[1m+++ b/.idea/FlightManagement_5.iml[m
[36m@@ -4,7 +4,7 @@[m
     <content url="file://$MODULE_DIR$">[m
       <excludeFolder url="file://$MODULE_DIR$/.venv" />[m
     </content>[m
[31m-    <orderEntry type="jdk" jdkName="Python 3.13" jdkType="Python SDK" />[m
[32m+[m[32m    <orderEntry type="jdk" jdkName="Python 3.13 (FlightManagement_5)" jdkType="Python SDK" />[m
     <orderEntry type="sourceFolder" forTests="false" />[m
   </component>[m
 </module>[m
\ No newline at end of file[m
[1mdiff --git a/.idea/misc.xml b/.idea/misc.xml[m
[1mindex 1d3ce46..b4afc79 100644[m
[1m--- a/.idea/misc.xml[m
[1m+++ b/.idea/misc.xml[m
[36m@@ -3,5 +3,5 @@[m
   <component name="Black">[m
     <option name="sdkName" value="Python 3.13" />[m
   </component>[m
[31m-  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.13" project-jdk-type="Python SDK" />[m
[32m+[m[32m  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.13 (FlightManagement_5)" project-jdk-type="Python SDK" />[m
 </project>[m
\ No newline at end of file[m
[1mdiff --git a/app/index.py b/app/index.py[m
[1mindex f4e3d1e..1c5e510 100644[m
[1m--- a/app/index.py[m
[1m+++ b/app/index.py[m
[36m@@ -282,9 +282,7 @@[m [mdef payment_comfirm_page():[m
         "price":fareclass_price[m
     }[m
     session['ticket_info'] = ticket_info[m
[31m-    print(session.get('ticket_info').get('customername'))[m
     seats = utils.get_seat_by_quantity(quantity=quantity, flightid=flight_id)[m
[31m-[m
     return render_template('payment.html', seats=seats, quantity=quantity, price=fareclass_price,[m
                                cus_name=customer_name,[m
                                fareclass_name=fareclass_name, plane_name=plane_name)[m
[1mdiff --git a/app/utils.py b/app/utils.py[m
[1mindex e7d477f..6e709ac 100644[m
[1m--- a/app/utils.py[m
[1m+++ b/app/utils.py[m
[36m@@ -1,4 +1,3 @@[m
[31m-[m
 from random import choice[m
 from flask_mail import Message[m
 from flask import session[m
[36m@@ -11,25 +10,28 @@[m [mfrom app.models import Ticket, Flight, Customer, Seat, FareClass, Plane, Route[m
 [m
 def get_seat_by_quantity(quantity,flightid):[m
     if quantity:[m
[31m-[m
         selected_seats = [][m
         seatinfo = {}[m
[31m-        for _ in range(quantity):[m
[32m+[m[32m        for index  in range(quantity):[m
             seats = Seat.query.filter(Seat.status == False, Seat.flight_id == flightid).all()[m
             if seats:[m
                 rand_seat = choice(seats)[m
                 rand_seat.status = True[m
[32m+[m[32m                print(f"Chỉ số hiện tại: {index}")[m
[32m+[m[32m                print(f"Chỗ ngồi hiện tại: {rand_seat.name}")[m
[32m+[m[32m                print(rand_seat.status)[m
[32m+[m[32m                selected_seats.append(rand_seat)[m
                 seatinfo[int(rand_seat.id)]={[m
                     "id":int(rand_seat.id),[m
                     "name":str(rand_seat.name),[m
                     "flightid":int(rand_seat.flight_id)[m
                 }[m
[31m-                selected_seats.append(rand_seat)[m
[32m+[m[32m                db.session.commit()[m
[32m+[m
             elif not seats:[m
                 return selected_seats[m
[31m-            session['seats'] = seatinfo[m
[31m-            return selected_seats[m
[31m-            db.session.commit()[m
[32m+[m[32m        session['seats'] = seatinfo[m
[32m+[m[32m        return selected_seats[m
 [m
 [m
 def add_ticket(ticket_info):[m
[1mdiff --git a/requirements.txt b/requirements.txt[m
[1mindex 8ec6cc2..23e4544 100644[m
Binary files a/requirements.txt and b/requirements.txt differ
