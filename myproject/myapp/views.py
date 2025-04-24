from django.shortcuts import render, redirect
from Directory import Directory  # Use relative import
from Authenticator import Authenticator  # Import the Authenticator class
from Member import Member, President, BillingStaff
from Calendar import Calendar
import datetime
from emailer import Emailer

def directory_view(request):
    results = None
    success = None
    if request.method == 'POST':
        directory = Directory()
        if request.POST.get('submittype') == 'View Full Directory':
            results = directory.getAll(request.session.get('member_id'))
            return render(request, 'myapp/directory.html', {'results': results})
        elif request.POST.get('submittype') == 'Search':
            attribute = request.POST.get('attribute')
            value = request.POST.get('value')
            results = directory.searchAttr(request.session.get('member_id'), attribute, value)
            if results == -1:
                return render(request, 'myapp/directory.html', {'Error': 'Invalid input. Try again.'})
            else:
                return render(request, 'myapp/directory.html', {'results': results})
        elif request.POST.get('submittype') == 'Create Member':
            mem = President()
            ret = mem.createMember(request.POST.get('fname'), request.POST.get('lname'), request.POST.get('email'),
                             request.POST.get('phonenum'), request.POST.get('dropdown-option'), request.POST.get('password'))
            if ret == 0:
                return render(request, 'myapp/directory.html', {'Success': 'Member created!'})
            else:
                return render(request, 'myapp/directory.html', {'Error': 'Invalid Input'})
        elif request.POST.get('submittype') == 'Deactivate Member':
            mem = President()
            ret = mem.deactivateMember(request.POST.get('memid'))
            if ret == 0:
                return render(request, 'myapp/directory.html', {'Success': 'Member deactivated!'})
            elif ret == -2:
                return render(request, 'myapp/directory.html', {'Error': 'You cannot deactivate the President or Billing Staff accounts.'})
            else:
                return render(request, 'myapp/directory.html', {'Error': 'Invalid Input'})

        elif request.POST.get('submittype') == 'Update Member':
            mem = President()
            ret = mem.updateInformation(request.POST.get('member_id'), request.POST.get('attribute'), request.POST.get('value'))
            if ret == 0:
                return render(request, 'myapp/directory.html', {'Success': 'Member updated!'})
            else:
                return render(request, 'myapp/directory.html', {'Error': 'Invalid Input'})

    return render(request, 'myapp/directory.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        auth = Authenticator()
        id, firstname, lastname = auth.login(username, password)
        print(id) #print debug
        if id != False:
            request.session['member_id'] = id
            request.session['firstname'] = firstname
            request.session['lastname'] = lastname
            return redirect('directory')  # Redirect to the search page on successful login
        else:
            return render(request, 'myapp/login.html', {'error': 'Invalid credentials. Please try again'})
    request.session['scheduler_stage'] = None
    return render(request, 'myapp/login.html')

def logout_view(request):
    if request.method == 'POST':
        request.session['member_id'] = None
        return redirect('login')
    request.session['scheduler_stage'] = None
    return render(request, 'myapp/logout.html')

def billing_view(request):
    bill = None
    success = None
    if request.method == 'POST':
        if request.POST.get('submittype') == 'Get Bill':
            if request.session.get('member_id') == 1 or request.session.get('member_id') == 2:
                if request.session.get('member_id') == 1:
                    mem = President()
                else:
                    mem = BillingStaff()
                bill = mem.getFullBill(request.POST.get('mem_id'))
            else:
                mem = Member(request.session.get('member_id'))
                bill = mem.getBill()
            if not bill:
                return render(request, 'myapp/billing.html', {'Error': 'Invalid Input. Try Again.'})
            else:
                return render(request, 'myapp/billing.html', {'bill': bill})
        if request.POST.get('submittype') == 'Create Charge':
            if request.session.get('member_id') == 1:
                mem = President()
            else:
                mem = BillingStaff()
            ret = mem.addEventFee(request.POST.get('amount'), request.POST.get('desc'), request.POST.get('mem_id'))
            if ret == -1:
                return render(request, 'myapp/billing.html', {'Error': 'Invalid Member ID. Try Again.'})
            if ret == False:
                return render(request, 'myapp/billing.html', {'Error': 'Invalid Input. Try Again.'})
            else:
                return render(request, 'myapp/billing.html', {'Success': 'Charge Added'})
        if request.POST.get('submittype') == 'Modify Charge':
            mem = BillingStaff()
            ret = mem.modifyBill(request.POST.get('charge_id'), request.POST.get('attribute'), request.POST.get('value'))
            if ret == False:
                return render(request, 'myapp/billing.html', {'Error': 'Invalid Input. Try Again.'})
            else:
                return render(request, 'myapp/billing.html', {'Success': 'Charge Modified!'})
        if request.POST.get('submittype') == 'Delete Charge':
            mem = BillingStaff()
            ret = mem.deleteCharge(request.POST.get('charge_id'))
            if ret == False:
                return render(request, 'myapp/billing.html', {'Error': 'Invalid Input. Try Again.'})
            else:
                return render(request, 'myapp/billing.html', {'Success': 'Charge Deleted!'})
        if request.POST.get('submittype') == 'Retrieve Current Billing Scheme':
            mem = BillingStaff()
            billing_scheme = mem.getBillingScheme()
            return render(request, 'myapp/billing.html', {'billing_scheme': billing_scheme})
        if request.POST.get('submittype') == 'Modify Billing Scheme':
            mem = BillingStaff()
            if request.POST.get('chargetype') == 'guestfee':
                ret = mem.modifyGuestFee(request.POST.get('value'))
            elif request.POST.get('chargetype') == 'annualfee':
                ret = mem.modifyAnnualFee(request.POST.get('value'))
            billing_scheme = mem.getBillingScheme()
            if ret == False:
                return render(request, 'myapp/billing.html', {'Error': 'Invalid Input. Try Again.'})
            else:
                return render(request, 'myapp/billing.html', {'Success': 'Billing Scheme Modified!', 'billing_scheme': billing_scheme})
        if request.POST.get('submittype') == 'Pay Your Bill':
            mem = Member(request.session.get('member_id'))
            ret = mem.payBill(request.POST.get('year'))
            if ret == False:
                return render(request, 'myapp/billing.html', {'Error': 'Invalid Year. Try Again.'})
            else:
                return render(request, 'myapp/billing.html', {'Success': 'Bill Paid'})


    return render(request, 'myapp/billing.html')

def scheduler_view(request):
    results = None
    res_results = None
    attendees = None
    success = None
    cal = Calendar()
    dir = Directory()
    courts = list(range(1, 13))  # Courts 1 to 12
    hours = list(range(6, 21))  # Hours 6 AM to 8 PM
    minutes = ["00", "30"]  # 15-minute intervals

    if request.method == 'POST':
        submittype = request.POST.get('submittype')
        if submittype == 'Reset Process':
            request.session['day'] = None
            request.session['scheduler_stage'] = None
            request.session['num_guests'] = None
            request.session['update_type'] = None
            request.session['res_id'] = None
        elif submittype == 'Select Day':
            request.session['day'] = request.POST.get('day')
            request.session['scheduler_stage'] = 'Type'  # Move to the next stage
            results = cal.RetrieveDay(request.POST.get('day'))
        elif submittype == 'Select Type':
            request.session['type'] = request.POST.get('type')
            request.session['scheduler_stage'] = 'Guests'  # Move to the next stage
            results = cal.RetrieveDay(request.session['day'])
        elif submittype == 'Designate Guests':
            request.session['num_guests'] = request.POST.get('guests')
            request.session['scheduler_stage'] = 'Reserve'  # Move to the next stage
            results = cal.RetrieveDay(request.session['day'])
        elif submittype == 'Reserve':
            start = request.POST.get('start').split(":")
            end = request.POST.get('end').split(":")
            court = request.POST.get('court')
            if request.session.get('type') == 'singles':
                mem = Member(request.session.get('member_id'))
                if request.session.get('num_guests') == '1':  # 1 guest pass, 1 member
                    members = []
                    guests = [request.POST.get('guest1')]
                else:  # 0 guest passes, 2 members
                    mem2 = request.POST.get('member2').split(" ")
                    try:
                        members = [dir.nameLookup(mem2[0], mem2[1])]
                    except IndexError:
                        return render(request, 'myapp/scheduler.html', {'Error': 'Invalid member name. Try again.'})
                    guests = []
                ret = mem.createReservation(
                    request.session.get('type'),
                    request.session.get('day'),
                    datetime.time(int(start[0]), int(start[1])),
                    datetime.time(int(end[0]), int(end[1])),
                    court,
                    members,
                    guests,
                )
            elif request.session.get('type') == 'doubles':
                mem = Member(request.session.get('member_id'))
                match request.session.get('num_guests'):
                    case '1':  # 1 guest pass, 3 members
                        mem2 = request.POST.get('member2').split(" ")
                        mem3 = request.POST.get('member3').split(" ")
                        try:
                            members = [dir.nameLookup(mem2[0], mem2[1]), dir.nameLookup(mem3[0], mem3[1])]
                        except IndexError:
                            return render(request, 'myapp/scheduler.html', {'Error': 'Invalid input. Try again.'})

                        guests = [request.POST.get('guest1')]
                    case '2':  # 2 guest passes, 2 members
                        mem2 = request.POST.get('member2').split(" ")
                        try:
                            members = [dir.nameLookup(mem2[0], mem2[1])]
                        except:
                            return render(request, 'myapp/scheduler.html', {'Error': 'Invalid member name. Try again.'})
                        guests = [request.POST.get('guest1'), request.POST.get('guest2')]
                    case '3':  # 3 guest passes, 1 member
                        members = []
                        guests = [request.POST.get('guest1'), request.POST.get('guest2'), request.POST.get('guest3')]
                    case '0':  # 0 guest passes, 4 members
                        mem2 = request.POST.get('member2').split(" ")
                        mem3 = request.POST.get('member3').split(" ")
                        mem4 = request.POST.get('member4').split(" ")
                        try:
                            members = [
                                dir.nameLookup(mem2[0], mem2[1]),
                                dir.nameLookup(mem3[0], mem3[1]),
                                dir.nameLookup(mem4[0], mem4[1]),
                            ]
                        except IndexError:
                            return render(request, 'myapp/scheduler.html', {'Error': 'Invalid member name. Try again.'})
                        guests = []
                ret = mem.createReservation(
                    request.session.get('type'),
                    request.session.get('day'),
                    datetime.time(int(start[0]), int(start[1])),
                    datetime.time(int(end[0]), int(end[1])),
                    court,
                    members,
                    guests,
                )
            request.session['scheduler_stage'] = None  # Reset stage
            success = True
            if ret == 1:
                return render(request, 'myapp/scheduler.html', {'Error':'Your reservation overlaps with a reservation on this court.'})
            elif ret == 2:
                return render(request, 'myapp/scheduler.html', {'Error':'Your reservation overlaps with another reservation you have scheduled.'})
            elif ret == 3:
                return render(request, 'myapp/scheduler.html', {'Error':'You have another scheduled reservation beginning less than 60 minutes following this one.'})
            elif ret == 4:
                return render(request, 'myapp/scheduler.html', {'Error':'You have another scheduled reservation ending less than 60 minutes before this one.'})
            elif ret == 6:
                return render(request, 'myapp/scheduler.html', {'Error':'You do not have enough guest passes.'})
            elif ret == 7:
                return render(request, 'myapp/scheduler.html', {'Error':'You have reached the maximum number of reservations in a 7 day period.'})
            elif ret == 9:
                return render(request, 'myapp/scheduler.html', {'Error':'Your reservation does not occupy a valid time slot.'})
            elif ret == 10:
                return render(request, 'myapp/scheduler.html', {'Error':'Another member on your reservation has an overlapping reservation.'})
            elif ret == 11:
                return render(request, 'myapp/scheduler.html', {'Error':'Invalid member name. Try again.'})
            elif ret == 12:
                return render(request, 'myapp/scheduler.html', {'Error':'Invalid guest name. Try again.'})
            elif ret == False:
                return render(request, 'myapp/scheduler.html', {'Error':'Invalid input. Try again.'})
            else:
                return render(request, 'myapp/scheduler.html', {'Success': 'Reservation Created!'})
        elif submittype == 'Lookup Reservation':
            res_results = cal.lookupReservation(request.POST.get('res_id'))
            if res_results == -1:
                return render(request, 'myapp/scheduler.html', {'Error':'Invalid input. Try again.'})
            elif res_results:
                request.session['res_id'] = request.POST.get('res_id')
                request.session['update_type'] = res_results[0][4]
                attendees = cal.getAttendees(request.POST.get('res_id'))
            else:
                return render(request, 'myapp/scheduler.html', {'Error':'Reservation does not exist.'})
        elif submittype == 'Delete Reservation':
            mem = request.session.get('member_id')
            if mem == 1:
                mem = President()
            else:
                mem = Member(mem)
            ret = mem.deleteReservation(request.POST.get('res_id'))
            if ret == 1:
                return render(request, 'myapp/scheduler.html', {'Success': 'Reservation deleted!'})
            elif ret == -2:
                return render(request, 'myapp/scheduler.html', {'Error': 'You do not own this reservation.'})
            elif ret == 0:
                return render(request, 'myapp/scheduler.html', {'Error': 'Invalid Input. Try Again'})
        elif submittype == 'Update Reservation':
            mem = Member(request.session.get('member_id'))
            if request.session.get('update_type') == 'singles':
                players = []
                players.append(request.POST.get('player1'))
            elif request.session.get('update_type') == 'doubles':
                players = []
                players.append(request.POST.get('player1'))
                players.append(request.POST.get('player2'))
                players.append(request.POST.get('player3'))
            ret = mem.updateReservation(int(request.session.get('res_id')),players)
            res_results = cal.lookupReservation(request.session.get('res_id'))
            attendees = cal.getAttendees(request.session.get('res_id'))
            if ret == 1:
                return render(request, 'myapp/scheduler.html', {'Success': 'Reservation Updated!'})
            elif ret == -1:
                return render(request, 'myapp/scheduler.html', {'Error': 'You do not have enough guest passes!'})
            elif ret == -2:
                return render(request, 'myapp/scheduler.html', {'Error': 'You do not own this reservation.'})
            elif ret == 0:
                return render(request, 'myapp/scheduler.html', {'Error': 'Invalid Input. Try Again'})


    processed_results = []
    if results:
        for res in results:
            start_hour, start_minute = map(int, res[2].strftime("%H:%M").split(":"))
            end_hour, end_minute = map(int, res[3].strftime("%H:%M").split(":"))
            dur = 0
            processed_results.append({
                'court': res[1],
                'start_hour': start_hour,
                'start_minute': start_minute,
                'end_hour': end_hour,
                'end_minute': end_minute,
                'reservation_id': res[0],
                'type': res[5],
                'dur' : dur
            })

    # Create a time grid with reservation IDs for each court and time slot
    time_grid = []
    for hour in hours:
        for minute in minutes:
            if hour == 20 and minute != "00":
                break
            row = {'time': f"{hour:02}:{minute}", 'courts': []}
            for court in courts:
                reservation_id = None
                dur = None
                typ = None
                for court_data in processed_results:
                    if court_data['court'] == court:
                        current_time = hour * 60 + int(minute)
                        start_time = court_data['start_hour'] * 60 + court_data['start_minute']
                        end_time = court_data['end_hour'] * 60 + court_data['end_minute']
                        if start_time == current_time:
                            reservation_id = court_data['reservation_id']
                            dur = (end_time - start_time)/30
                            typ = court_data['type']
                        #if start_time <= current_time <= end_time:
                        #    reservation_id = court_data['reservation_id']
                        #    break
                row['courts'].append({'court': court, 'reservation_id': reservation_id, 'duration' : dur, 'type' : typ})
            time_grid.append(row)

    context = {
        'results': results,
        'res_results': res_results,
        'attendees': attendees,
        'success': success,
        'courts': courts,
        'hours': hours,
        'minutes': minutes,
        'time_grid': time_grid,
    }
    return render(request, 'myapp/scheduler.html', context)

def sort_results_by_court(results):
    if results is None:
        return {}
    sorted_results = {}
    for res in results:
        court_num = res[1]
        if court_num not in sorted_results:
            sorted_results[court_num] = []
        sorted_results[court_num].append(res)
    return sorted_results

def account_view(request):
    result = None
    if request.method == 'POST':
        if request.POST.get('submittype') == 'Fetch Information':
            mem = Member(request.session.get('member_id'))
            result = mem.getInformation()
            return render(request, 'myapp/account.html', {'result': result})
        if request.POST.get('submittype') == 'Change First Name':
            mem = Member(request.session.get('member_id'))
            ret = mem.updateInformation('firstname', request.POST.get('value'))
            result = mem.getInformation()
            if ret == 0:
                return render(request, 'myapp/account.html', {'Success': 'Information Updated!', 'result' : result})
            else:
                return render(request, 'myapp/account.html', {'Error': 'Invalid input. Try Again.', 'result' : result})
        if request.POST.get('submittype') == 'Change Last Name':
            mem = Member(request.session.get('member_id'))
            ret = mem.updateInformation('lastname', request.POST.get('value'))
            result = mem.getInformation()
            if ret == 0:
                return render(request, 'myapp/account.html', {'Success': 'Information Updated!', 'result': result})
            else:
                return render(request, 'myapp/account.html', {'Error': 'Invalid input. Try Again.', 'result': result})
        if request.POST.get('submittype') == 'Change Email':
            mem = Member(request.session.get('member_id'))
            ret = mem.updateInformation('email', request.POST.get('value'))
            result = mem.getInformation()
            if ret == 0:
                return render(request, 'myapp/account.html', {'Success': 'Information Updated!', 'result' : result})
            else:
                return render(request, 'myapp/account.html', {'Error': 'Invalid input. Try Again.', 'result' : result})
        if request.POST.get('submittype') == 'Change Phone Number':
            mem = Member(request.session.get('member_id'))
            ret = mem.updateInformation('phonenum', request.POST.get('value'))
            result = mem.getInformation()
            if ret == 0:
                return render(request, 'myapp/account.html', {'Success': 'Information Updated!', 'result' : result})
            else:
                return render(request, 'myapp/account.html', {'Error': 'Invalid input. Try Again.', 'result' : result})
        if request.POST.get('submittype') == 'Change Opt-In':
            mem = Member(request.session.get('member_id'))
            ret = mem.updateInformation('optin', request.POST.get('optin'))
            result = mem.getInformation()
            if ret == 0:
                return render(request, 'myapp/account.html', {'Success': 'Information Updated!', 'result' : result})
            else:
                return render(request, 'myapp/account.html', {'Error': 'Invalid input. Try Again.', 'result' : result})
        if request.POST.get('submittype') == 'Change Password':
            mem = Member(request.session.get('member_id'))
            password = request.POST.get('pass')
            confirm_password = request.POST.get('pass_verify')
            if password != confirm_password:
                return render(request, 'myapp/account.html', {'Error': 'Passwords do not match. Try again.'})
            ret = mem.updateInformation('password', request.POST.get('pass'))
            result = mem.getInformation()
            if ret == 0:
                return render(request, 'myapp/account.html', {'Success': 'Information Updated!', 'result' : result})
            else:
                return render(request, 'myapp/account.html', {'Error': 'Invalid input. Try Again.', 'result' : result})
        if request.POST.get('submittype') == 'Send Email':
            dir = Directory()
            emails = dir.getEmails()
            email_success = []
            em = Emailer()
            for email in emails:
                try:
                    em.connect()
                    em.sendEmail(request.POST.get('emailbody'), request.POST.get('subject'), email[0])
                    email_success.append(email[0])
                except:
                    pass
            return render(request, 'myapp/account.html', {'Success': 'Announcement sent!'})

    return render(request, 'myapp/account.html')