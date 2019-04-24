from django.shortcuts import render, redirect
from django.views.generic import View

from .forms import ClientForm
from .models import Conso_eur, Conso_watt


class ClientFormView(View):
    def get(self, request):
        return render(request, 'dashboard/accueil.html')

    def post(self, request):
        form = ClientForm(request.POST)

        if form.is_valid():
            client_id = form.cleaned_data['client']
            return redirect('dashboard:results', client_id=client_id)

def results(request, client_id):
    conso_euro = []
    conso_watt = []
    annual_costs = [0, 0]
    is_elec_heating = True
    dysfunction_detected = False

    conso_excessive = []

    """Recherche d'une consommation excessive en plein hiver"""
    for cw in Conso_watt.objects.filter(janvier__in=(range(900,1800)), id=client_id):
        conso_excessive.append(cw)

    if len(conso_excessive) == 0:
        is_elec_heating = False

    """Récupération de toutes les consommations en euro du client de l'année 2016"""
    ce16 = Conso_eur.objects.get(id=client_id, year=2016)

    total_2016 = ce16.janvier + ce16.fevrier + ce16.mars + ce16.avril + ce16.mai + ce16.juin + ce16.juillet + ce16.aout + ce16.septembre + ce16.octobre + ce16.novembre + ce16.decembre

    """Récupération de toutes les consommations en euro du client de l'année 2017"""
    for elt in Conso_eur.objects.filter(year=2017):
        if int(elt.client_id) == int(client_id):
            ce17 = elt

    total_2017 = ce17.janvier + ce17.fevrier + ce17.mars + ce17.avril + ce17.mai + ce17.juin + ce17.juillet + ce17.aout + ce17.septembre + ce17.octobre + ce17.novembre + ce17.decembre

    """Restriction à 2 chiffres après la virgule maximum"""
    total_2016 = float("%.2f" % total_2016)
    total_2017 = float("%.2f" % total_2017)

    annual_costs = [total_2016, total_2017]

    """Comparaison des totaux des deux années pour y trouver une grande différence ou non"""
    if is_very_different(total_2016, total_2017):
        dysfunction_detected = True

    """Récupération des données pour le graphique"""
    for cwatt in Conso_watt.objects.filter(year=2017):
        if int(cwatt.client_id) == int(client_id):
            conso_watt=[cwatt.janvier, cwatt.fevrier, cwatt.mars, cwatt.avril, cwatt.mai, cwatt.juin, cwatt.juillet, cwatt.aout, cwatt.septembre, cwatt.octobre, cwatt.novembre, cwatt.decembre]

    context = {
        "conso_euro": conso_euro,
        "conso_watt": conso_watt,
        "annual_costs": annual_costs,
        "is_elec_heating": is_elec_heating,
        "dysfunction_detected": dysfunction_detected,
    }
    return render(request, 'dashboard/results.html', context)

def is_very_different(val_2016, val_2017):

    if (val_2016 - val_2017 >= 400) or (val_2017 - val_2016 >= 400):
        return True
    else:
        return False
