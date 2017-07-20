from django.shortcuts import render
from .forms import ContactForm
from .sending import send_mail

# Payment
def payment_proccess(request):
    if self.request.GET.get("eventType") == "NewSaleSuccess":
        objPOST = self.request.POST

        idsuscription = objPOST.get('subscriptionId')
        customer_fname = objPOST.get('firstName')
        customer_lname = objPOST.get('lastName')
        email = objPOST.get('consumerEmail')
        addres1 = objPOST.get('address1')
        city = objPOST.get('city')
        country = objPOST.get('country')
        zipcode = objPOST.get('postalCode')
        price = objPOST.get('billedInitialPrice')
        cardType = objPOST.get('cardType')
        referer = objPOST.get('transactionId')
        if referer == '':
            referer=None

        datehapppen = objPOST.get('timestamp')
        datestart = datetime.now().isoformat()
        dateend = objPOST.get('nextRenewalDate')
        cliusername = objPOST.get('client')

        #Buscamos el cliente
        if Client.objects.filter(cliusername=cliusername).exits():
            client = Client.objects.get(cliusername=cliusername)
            #Guardar el Purchase
            purchase = Purchase.objects.create(
                       puridsuscription=idsuscription,
                       purdate = datehapppen,
                       purstatus = True,
                       purbalance = 0,
                       purfname = customer_fname,
                       purlname = customer_lname,
                       puremail = email,
                       puraddress1 = addres1,
                       purcity = city,
                       purcountry = country,
                       purzipcode = zipcode,
                       purprice = price,
                       purcardtype = cardType,
                       purccbillreferer = referer,
                       purdatestart = datestart,
                       purdateend = dateend,
                       clicode = client)

# Static pages
def about_view(request):
    return render(request, 'dateSite/about.html')


def faq_view(request):
    return render(request, 'dateSite/faq.html')


def terms_view(request):
    return render(request, 'dateSite/terms.html')


def privacy_view(request):
    return render(request, 'dateSite/policy.html')


def securely_view(request):
    return render(request, 'dateSite/securely.html')


def contact_view(request):
    return render(request, 'dateSite/contactus.html')

def verified_view(request):
    return render(request, 'dateSite/verified.html')

def contact_form(request):
    form_class = ContactForm

    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get('contact_name')
            contact_email = request.POST.get('contact_email')
            form_content = request.POST.get('content')

        context = {
            'name': contact_name,
            'email': contact_email,
            'message': form_content,
        }

        template = 'account/email/email_contact.html'
        send_mail("Message from " + contact_name, template,
                  ['susej@rexlertech.com', 'luis@rexlertech.com'],
                  '<contact@datinglatinos.com>', context)

        return render(request, 'dateSite/contact.html', context)

    return render(request, 'dateSite/contact.html', {
        'form': form_class,
    })

def forbidden(request):
    return render(request, 'dateSite/forbidden.html')

def under_construction(request):
    return render(request, 'dateSite/under_construction.html')

def error404(request):
    return render(request, 'dateSite/404.html', status=404)
