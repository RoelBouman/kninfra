from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import Group
import kn.subscriptions.entities as subscr_Es
import kn.leden.entities as Es
from django.http import Http404
from django.core.mail import EmailMessage

@login_required
def event_detail(request, name):
        event = subscr_Es.event_by_name(name)
        if event is None:
                raise Http404
        subscription = event.get_subscription_of(request.user)
	if subscription:
		if subscription.debit > 0:
			request.user.push_message((
				"Je bent al aangemeld, maar moet nog wel %s"+
				" euro betalen.") % subscription.debit)
		else:
			request.user.push_message("Je bent aangemeld en je"+\
						" betaling is verwerkt!")
	elif request.method == 'POST' and event.is_open:
                notes = request.POST['notes']
		subscription = subscr_Es.Subscription({
                        'event': event._id,
                        'user': request.user._id,
                        'userNotes': notes,
                        'debit': event.cost})
		subscription.save()
		full_owner_address = '%s <%s>' % (
				event.owner.humanName,
				event.owner.primary_email)
		email = EmailMessage(
				"Aanmelding %s" % event.humanName,
				 event.mailBody % {
					'firstName': request.user.first_name,
                                        'notes': notes},
				'Karpe Noktem Activiteiten <root@karpenoktem.nl>',
				[request.user.primary_email],
				[event.owner.primary_email],
				headers={
					'Cc': full_owner_address,
					'Reply-To': full_owner_address})
		email.send()
		request.user.push_message(
				"Je bent aangemeld en moet "+\
					"nu %s euro betalen" % event.cost)
	try:
		request.user.groups.get(name=event.owner)
		# An exception would have been triggered,
		# if we weren't in the group as specified by owner
		subscrlist = EventSubscription.objects.filter(event=event)
		subscrcount_debit = subscrlist.exclude(debit=0).count()
	except Group.DoesNotExist:
		subscrlist = None
		subscrcount_debit = None
	return render_to_response('subscriptions/event_detail.html',
			{'object': event,
			 'user': request.user,
			 'subscrlist': subscrlist,
			 'subscrcount_debit': subscrcount_debit,
			 'subscription': subscription},
			context_instance=RequestContext(request))
