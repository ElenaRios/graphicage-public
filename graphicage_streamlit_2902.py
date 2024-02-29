import streamlit as st
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
import re
import io
import base64
import array



'''
next step : 
inverser ville 1 et ville2
ajouter option ville 3

'''


def validate_duration_format(duration_str):
    # Use regular expression to validate HH:MM format for duration
    return re.match(r'^([0-9]|[0-9][0-9]|[1-9][0-9][0-9]+):([0-5]\d)$', duration_str)


def get_days_of_service(bus_number, direction):
    while True:
        try:
            while True:  # Boucle interne pour gérer les jours invalides
                jours_map = {
                    "Lundi": 1,
                    "Mardi": 2,
                    "Mercredi": 3,
                    "Jeudi": 4,
                    "Vendredi": 5,
                    "Samedi": 6,
                    "Dimanche": 7
                }
                jours_selectionnes = st.multiselect(f"Quel(s) jour(s) le bus {bus_number} roule de {direction} ?", list(jours_map.keys()))
                days = []
                for jour in jours_selectionnes:
                    days.append(jours_map[jour])
                days = array.array('I', [jours_map[jour] for jour in jours_selectionnes])
                days_list = list(days) 
                if not days:  # Check if the input is empty
                    days_list = []
                    break

                if any(int(day) > 7 for day in days_list):
                    print("Veuillez entrer des jours valides (de 1 à 7). \n\n")                
                
                else:
                    days_list = [int(day) for day in days_list if int(day) in range(1, 8)]  # Modified to accept days 1 to 7
                    break  # Sort de la boucle interne si l'entrée est valide
            break  # Sort de la boucle principale si l'entrée est valide
        except ValueError:
            print("Veuillez entrer des jours valides séparés par des virgules. \n\n")

    return days_list

def plot_arrow(ax, start, end, color):
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=color))


def number_buses():
    while True:
        try:
            num_buses = st.slider("Entrez le nombre de bus :", min_value=1, max_value=10, value=1, step=1)

            st.write("Nombre de bus :", num_buses)
            print("\n")
            return num_buses
        except ValueError:
            print(" Veuillez entrer un nombre valide.")

def graphicage_hlp():
    while True:
        try:
            choice = st.radio("Graphique avec 2 ou 3 villes ?", options=[2, 3])
            st.write("Choix sélectionné :", choice)
            if choice == 2:
                num_villes = 2
                return num_villes
            elif choice == 3:
                num_villes = 3
                return num_villes
            else:
                raise ValueError  # Raise an exception if the response is neither 'y' nor 'n'
        except ValueError:
            print("Veuillez entrer '2' ou '3'. ")
            print("\n")

widget_counter = 0

def get_unique_key(name):
    return f"{name}_{hash(name)}"

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{bin_file}">{file_label}</a>'
    return href

def get_image_download_link(buffer, filename):
    """Generate a download link for the image."""
    buffer_str = base64.b64encode(buffer).decode()
    href = f'<a href="data:image/png;base64,{buffer_str}" download="{filename}">Download Image</a>'
    return href

            
def horaires():
    num_villes = graphicage_hlp()
    num_buses = number_buses()

    villes = {}
    horaires_trajets = {}

    st.write("Insérez les villes dans l'ordre")
    for i in range(num_villes):
        villes[f"ville_{i+1}"] = st.text_input(f"Ville {i+1}:")

    for i in range(num_villes):
        for j in range(i+1, num_villes):
            while True:
                try:
                    key_1 = get_unique_key(f'heure_depart_{i}_{j}')
                    horaire_depart = st.time_input(f"Horaire de départ de {villes[f'ville_{i+1}']} à {villes[f'ville_{j+1}']}: ", key=key_1)
                    st.write("Durée du trajet :")
                    col1, col2 = st.columns(2)
                    if horaire_depart is not None:
                        heures_key = get_unique_key(f"heures_{i}_{j}")
                        minutes_key = get_unique_key(f"minutes_{i}_{j}")
                        heures = col1.number_input("Heures:", min_value=0, max_value=40, step=1, key=heures_key)
                        minutes = col2.number_input("Minutes:", min_value=0, max_value=59, step=1, key=minutes_key)
                        duree_trajet_minutes = heures * 60 + minutes
                        duree_trajet = f"{heures}:{minutes}"
                        trajet_key = f"{villes[f'ville_{i+1}']}_{villes[f'ville_{j+1}']}"
                        horaires_trajets[trajet_key] = {'depart': horaire_depart.strftime("%H:%M"), 'duree': duree_trajet}
                        break
                    else:
                        st.info(f"L'horaire de départ pour {villes[f'ville_{i+1}']} à {villes[f'ville_{j+1}']} n'a pas été spécifié.")
                        break
                except ValueError:
                    st.error("Format d'heure incorrect. Veuillez entrer une heure au format HH:MM.")

    for i in range(num_villes):
        for j in range(i+1, num_villes):
            while True:
                try:
                    horaire_depart = st.time_input(f" Horaire de départ de {villes[f'ville_{j+1}']} à {villes[f'ville_{i+1}']}: ")
                    col1, col2 = st.columns(2)
                    if horaire_depart is not None:
                        heures_key = get_unique_key(f"heures_{j}_{i}")
                        minutes_key = get_unique_key(f"minutes_{j}_{i}")
                        heures = col1.number_input("Heures:", min_value=0, max_value=40, step=1, key= heures_key)
                        minutes = col2.number_input("Minutes:", min_value=00, max_value=59, step=1, key= minutes_key)
                        if minutes < 10:
                            minutes = '0' + str(minutes)
                        if horaire_depart:
                            if duree_trajet:
                                trajet_key_inverse = f"{villes[f'ville_{j+1}']}_{villes[f'ville_{i+1}']}"
                                horaires_trajets[trajet_key_inverse] = {'depart': horaire_depart, 'duree': duree_trajet}
                                break
                            else:
                                st.error("Format de durée de trajet incorrect. Veuillez entrer une durée au format HH:MM.")
                        else:
                            st.error("Format d'heure de départ incorrect. Veuillez entrer une heure au format HH:MM.")
                    else:
                        trajet_key_inverse = f"{villes[f'ville_{j+1}']}_{villes[f'ville_{i+1}']}"
                        horaires_trajets[trajet_key_inverse] = {'depart': '', 'duree': ''}
                        st.warning(f"Les horaires ne seront pas enregistrés pour {villes[f'ville_{i+1}']} à {villes[f'ville_{j+1}']} car l'horaire de départ est vide.")
                        break
                except ValueError:
                    st.error("Format d'heure incorrect. Veuillez entrer une heure au format HH:MM.")


    return horaires_trajets, num_buses, num_villes, villes



def plot_graphicage_and_table_2_cities(arrivees_villes, departs_villes, villes, horaires_trajets, num_buses, days_of_services):
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'brown']
    days_of_week = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche', 'Lundi']
    midnight_dates = []
    
    dates_noon = []
    start_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    start_date += timedelta(days=(7 - start_date.weekday()))  # Pour obtenir le prochain lundi
    dates = [start_date + timedelta(days=i) for i in range(8)]  # Générer jusqu'au jour 8 inclus
    
    for date in dates:
        midnight_dates.append(date.replace(hour=0, minute=0, second=0, microsecond=0))
        dates_noon.append(date.replace(hour=12, minute=0, second=0, microsecond=0))
    
    fig, ax = plt.subplots(figsize=(20, 15))

    third_element_arrivees = list(arrivees_villes.keys())[0][2]
    third_element_arrivees_2 = list(arrivees_villes.keys())[1][2]
    
    for key, value in arrivees_villes.items():
        if third_element_arrivees in key:
            if key[1] == 1:
                for i in range(len(arrivees_villes[key])):
                    if departs_villes[key] != '':
                        ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 1), colors[key[0]-1])
                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1.07),
                                        textcoords="offset points", xytext=(0, 5), ha='center', fontsize=6)
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.01),
                                        textcoords="offset points", xytext=(0, 5), ha='center', fontsize=6)

        if third_element_arrivees_2 in key:
            for i in range(len(arrivees_villes[key])):
                if departs_villes[key] != '':
                    ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                    ax.plot([arrivees_villes[key], arrivees_villes[key]], [1, -1], linestyle='dotted', color='grey', alpha=0.5)
                    ax.plot([departs_villes[key], departs_villes[key]], [1, -1], linestyle='dotted', color='grey', alpha=0.5)

                    plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], -1), colors[key[0]-1])
                    for i, time in enumerate(departs_villes[key]):
                        ax.annotate(f"{time.strftime('%H:%M')}",
                                    (time, 1.03),
                                    textcoords="offset points", xytext=(0, 5), ha='center', fontsize=6)
                    for i, time in enumerate(arrivees_villes[key]):
                        ax.annotate(f"{time.strftime('%H:%M')}",
                                    (time, -1.07),
                                    textcoords="offset points", xytext=(0, 5), ha='center', fontsize=6)
    
    for date in midnight_dates:
        ax.axvline(x=date, color='lightblue', linestyle='-', linewidth=1)
    
    plt.yticks([-1, 1], [f'{villes["ville_1"]}', f'{villes["ville_2"]}'])
    plt.xticks(dates_noon, [days_of_week[date.weekday()]  for date in dates], fontsize=14, ha='center', va='center')
    ax.set_xlim(midnight_dates[0], dates_noon[-1])
    plt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True, colors='coral')

    for spine in ax.spines.values():
        spine.set_visible(False)

    title_color = 'navy'
    plt.title(f"Graphicage {villes['ville_1']} - {villes['ville_2']}", y=1.1, color=title_color)

    # Tableau
    table = [['' for _ in range(len(horaires_trajets) + 1)] for _ in range(num_buses + 1)]
    table_colors = [['black' for _ in range(len(horaires_trajets) + 1)] for _ in range(num_buses + 1)]
    headers = list(horaires_trajets.keys())
    table[0][1:] = headers
    for i in range(num_buses):
        table[i + 1][0] = f'Bus {i + 1}'
        for j, key in enumerate(headers):
            table[i + 1][j + 1] = days_of_services.get((i + 1, key), '')
            table_colors[i + 1][j + 1] = colors[i]
    cell_width = 4
    cell_height = 4
    table = plt.table(cellText=table, cellLoc='center', loc='lower right', bbox=[[1.1, 0.5, cell_width, cell_height] for _ in range(num_buses + 1) for _ in range(len(horaires_trajets) + 1)], edges='closed') 
    table.auto_set_font_size(False)  
    table.set_fontsize(18)  

    fig.set_size_inches(18*0.9, 10*0.9)
    plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.3)
    plt.savefig(f"Graphicage {villes['ville_1']} - {villes['ville_2']}.png", bbox_inches='tight')
    plt.close()
    return fig, table
    

def get_days_of_service_all_buses():

    horaires_trajets, num_buses, num_villes, villes = horaires()
    days_of_service_villes = {}
    departs_villes = {}
    arrivees_villes = {}
    directions = [key for key, value in horaires_trajets.items()]

    colors = ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'brown']
    days_of_week = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche', 'Lundi']
    midnight_dates = []
    
    dates_noon = []
    start_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    start_date += timedelta(days=(7 - start_date.weekday()))  # Pour obtenir le prochain lundi
    dates = [start_date + timedelta(days=i) for i in range(8)]  # Générer jusqu'au jour 8 inclus
    
    for date in dates:
        midnight_dates.append(date.replace(hour=0, minute=0, second=0, microsecond=0))
        dates_noon.append(date.replace(hour=12, minute=0, second=0, microsecond=0))
    
    
    days_of_services = {}
    for i in range(num_buses):
        for key, value in horaires_trajets.items():
            if value['depart'] == '':
                days_of_services[(i+1, key)] = ''
            else:
                days_of_services[(i+1, key)] = get_days_of_service(i+1, key)
    days_of_service_villes = {}
    
    for i in range(num_buses):
        for j in range(num_villes):
            for direction in directions:

                days_of_service_villes[(i+1, j+1, direction)] = days_of_services[(i+1, direction)] 
                departs_villes[(i+1, j+1, direction)] = [date for k, date in enumerate(dates) if (k + 1) in days_of_service_villes[(i+1, j+1, direction)]] if days_of_service_villes[(i+1, j+1, direction)] else ''
                arrivees_villes[(i+1, j+1, direction)] = [date for k, date in enumerate(dates) if (k + 1) in days_of_service_villes[(i+1, j+1, direction)]] if days_of_service_villes[(i+1, j+1, direction)] else ''
    
    for key, value in horaires_trajets.items():
        for k, v in departs_villes.items():
            if key == k[2]:
                if value['depart'] != '':
                    try:
                        heure_depart, minutes_depart = map(int, value['depart'].split(':'))
                    except AttributeError:
                        heure_depart = value['depart'].hour
                        minutes_depart = value['depart'].minute               
                    for i in range(len(departs_villes[k])):
                        departs_villes[k][i] = departs_villes[k][i].replace(hour=heure_depart, minute=minutes_depart)

    
    # Remplacer les heures et les minutes de tous les éléments de la clé du dictionnaire 'departs_villes'
    # par celles du dictionnaire 'horaire_trajets'
    for key, value in horaires_trajets.items():
        for k, v in departs_villes.items():
            if key == k[2]:
                if value['depart'] != '':
                    try:
                        heure_depart, minutes_depart = map(int, value['depart'].split(':'))
                    except AttributeError:
                        heure_depart = value['depart'].hour
                        minutes_depart = value['depart'].minute               

    for key, value in horaires_trajets.items():
        for k, v in departs_villes.items():
            if key == k[2]:
                if value['depart'] != '':
                    try:
                        heure_duree, minutes_duree = map(int, value['duree'].split(':'))
                    except AttributeError:
                        heure_duree= value['duree'].hour
                        minutes_duree = value['duree'].minute               

                for i in range(len(arrivees_villes[k])):
                    arrivees_villes[k][i] = departs_villes[k][i] + timedelta(hours=heure_duree, minutes=minutes_duree)
    
    
    
    #fig, table = plot_graphicage_and_table_2_cities(arrivees_villes, departs_villes, villes, horaires_trajets, num_buses, days_of_services)
    #plot_graphicage_and_table_2_cities(arrivees_villes, departs_villes, villes, horaires_trajets, num_buses, days_of_services)
    #st.pyplot(fig)
    #st.pyplot(table)
                    
    if st.button("Submit"):
                    
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'brown']
        days_of_week = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche', 'Lundi']
        midnight_dates = []
        
        dates_noon = []
        start_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        start_date += timedelta(days=(7 - start_date.weekday()))  # Pour obtenir le prochain lundi
        dates = [start_date + timedelta(days=i) for i in range(8)]  # Générer jusqu'au jour 8 inclus
        
        for date in dates:
            midnight_dates.append(date.replace(hour=0, minute=0, second=0, microsecond=0))
            dates_noon.append(date.replace(hour=12, minute=0, second=0, microsecond=0))
        
        fig, ax = plt.subplots(figsize=(20, 15))

        third_element_arrivees = list(arrivees_villes.keys())[0][2]
        third_element_arrivees_2 = list(arrivees_villes.keys())[1][2]
        
        for key, value in arrivees_villes.items():
            if third_element_arrivees in key:
                if key[1] == 1:
                    for i in range(len(arrivees_villes[key])):
                        if departs_villes[key] != '':
                            ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                            ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                            ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                            ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                            plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 1), colors[key[0]-1])

                            for i, time in enumerate(departs_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                            (time, -1.07),
                                            textcoords="offset points", xytext=(0, 5), ha='center', fontsize=6)
                            for i, time in enumerate(arrivees_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                            (time, 1.01),
                                            textcoords="offset points", xytext=(0, 5), ha='center', fontsize=6)

            if third_element_arrivees_2 in key:
                for i in range(len(arrivees_villes[key])):
                    if departs_villes[key] != '':
                        ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        ax.plot([arrivees_villes[key], arrivees_villes[key]], [1, -1], linestyle='dotted', color='grey', alpha=0.5)
                        ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], -1), colors[key[0]-1])
                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.03),
                                        textcoords="offset points", xytext=(0, 5), ha='center', fontsize=6)
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1.07),
                                        textcoords="offset points", xytext=(0, 5), ha='center', fontsize=6)
        
        for date in midnight_dates:
            ax.axvline(x=date, color='lightblue', linestyle='-', linewidth=1)
        
        plt.yticks([-1, 1], [f'{villes["ville_1"]}', f'{villes["ville_2"]}'])
        plt.xticks(dates_noon, [days_of_week[date.weekday()]  for date in dates], fontsize=14, ha='center', va='center')
        ax.set_xlim(midnight_dates[0], dates_noon[-1])
        plt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True, colors='coral')
        for spine in ax.spines.values():
            spine.set_visible(False)

        title_color = 'navy'
        plt.title(f"Graphicage {villes['ville_1']} - {villes['ville_2']}", y=1.1, color=title_color)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        st.image(buffer, use_column_width=True, caption='Graphicage Image')
        

        fig.set_size_inches(18*0.9, 10*0.9)
        plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.3)
        plt.savefig(f"Graphicage {villes['ville_1']} - {villes['ville_2']}.png", bbox_inches='tight')
        plt.close()

        filename = f"Graphicage {villes['ville_1']} - {villes['ville_2']}.png"  # Define the filename for the graph image
        image_bytes = buffer.getvalue()
        st.markdown(get_image_download_link(image_bytes, filename=filename), unsafe_allow_html=True)

    

if __name__ == '__main__':
    get_days_of_service_all_buses()

    

