
## LAST UPDATE 05/03

import streamlit as st
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
import re
import io
import base64
import array
import random


# LAST UPDATE 05/03


def validate_duration_format(duration_str):
    # Use regular expression to validate HH:MM format for duration
    return re.match(r'^([0-9]|[0-9][0-9]|[1-9][0-9][0-9]+):([0-5]\d)$', duration_str)


def get_days_of_service(bus_number, direction):
    while True:
        try:
            while True:  # Boucle interne pour gérer les jours invalides
                jours_map = {
                    "Monday": 1,
                    "Tuesday": 2,
                    "Wednesday": 3,
                    "Thursday": 4,
                    "Friday": 5,
                    "Saturday": 6,
                    "Sunday": 7
                }

                jours_selectionnes = st.multiselect(f"Quel(s) jour(s) le bus {bus_number} roule de {direction} ?", list(jours_map.keys()))
                days = []
                
                #if "Everyday" in jours_selectionnes:
                #    days = list(jours_map.keys())
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
            num_buses = st.slider("Number of buses 🚌:", min_value=1, max_value=10, value=1, step=1)

            #st.sidebar.write("Number of buses 🚌 :", num_buses)
            print("\n")
            return num_buses
        except ValueError:
            print(" Veuillez entrer un nombre valide.")

def graphicage_hlp():
    while True:
        try:
            choice = st.radio("How many cities ? 🚏", options=[2, 3], format_func=lambda x: f"{x}")
            #st.write("Choix sélectionné :", choice)
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

    st.write("<div style='font-size:30px;'><b> 🚏 Stops</b></div>", unsafe_allow_html=True)
    
    for i in range(num_villes):
        villes[f"ville_{i+1}"] = st.text_input(f"City {i+1}:")

    for i in range(num_villes):
        for j in range(i+1, num_villes):
            while True:
                try:
                    key_1 = get_unique_key(f'heure_depart_{i}_{j}')
                    horaire_depart = st.time_input(f"Travel time {villes[f'ville_{i+1}']} to {villes[f'ville_{j+1}']}: ", key=key_1, value = None)
                    st.write("Travel time :")
                    col1, col2 = st.columns(2)
                    if horaire_depart is not None:
                        heures_key = get_unique_key(f"heures_{i}_{j}")
                        minutes_key = get_unique_key(f"minutes_{i}_{j}")
                        heures = col1.number_input("Heures:", min_value=0, max_value=50, step=1, key=heures_key)
                        minutes = col2.number_input("Minutes:", min_value=0, max_value=59, step=1, key=minutes_key)
                        duree_trajet_minutes = heures * 60 + minutes
                        duree_trajet = f"{heures}:{minutes}"
                        trajet_key = f"{villes[f'ville_{i+1}']}_{villes[f'ville_{j+1}']}"
                        horaires_trajets[trajet_key] = {'depart': horaire_depart.strftime("%H:%M"), 'duree': duree_trajet}
                        break
                    else:
                        st.info(f"Departure time {villes[f'ville_{i+1}']} to {villes[f'ville_{j+1}']} has not been specified")
                        break
                except ValueError:
                    st.error("Format d'heure incorrect. Veuillez entrer une heure au format HH:MM.")

    for i in range(num_villes):
        for j in range(i+1, num_villes):
            while True:
                try:
                    horaire_depart = st.time_input(f" Departure time {villes[f'ville_{j+1}']} to {villes[f'ville_{i+1}']}: ", key=get_unique_key(f"time_input_{i}{j}"), value = None)
                    col1, col2 = st.columns(2)
                    if horaire_depart is not None:
                        heures_key = get_unique_key(f"heures_{j}_{i}")
                        minutes_key = get_unique_key(f"minutes_{j}_{i}")
                        heures = col1.number_input("Heures:", min_value=0, max_value=50, step=1, key= heures_key)
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

def get_days_of_service_all_buses():

    horaires_trajets, num_buses, num_villes, villes = horaires()
    days_of_service_villes = {}
    departs_villes = {}
    arrivees_villes = {}
    directions = [key for key, value in horaires_trajets.items()]

    colors = ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'brown']
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thirsday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
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
                    
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'brown', 'yellow', 'turquoise', 'lavender']
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
        midnight_dates = []
        
        dates_noon = []
        start_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        start_date += timedelta(days=(7 - start_date.weekday()))  # Pour obtenir le prochain lundi
        dates = [start_date + timedelta(days=i) for i in range(10)]  
        for date in dates:
            midnight_dates.append(date.replace(hour=0, minute=0, second=0, microsecond=0))
            dates_noon.append(date.replace(hour=12, minute=0, second=0, microsecond=0))
        


        if num_villes == 2:
            fig, ax = plt.subplots(figsize=(20, 15))

            third_element_arrivees = list(arrivees_villes.keys())[0][2]
            third_element_arrivees_2 = list(arrivees_villes.keys())[1][2]
            
            for key, value in arrivees_villes.items():
                if third_element_arrivees_2 in key:
                    if key[1] == 1:
                        for i in range(len(arrivees_villes[key])):
                            if departs_villes[key] != '':
                                ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                                ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                                #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                                #ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                                plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 1), colors[key[0]-1])

                                for i, time in enumerate(departs_villes[key]):
                                    ax.annotate(f"{time.strftime('%H:%M')}",
                                                (time, -1.07),
                                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                                for i, time in enumerate(arrivees_villes[key]):
                                    ax.annotate(f"{time.strftime('%H:%M')}",
                                                (time, 1.01),
                                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)

                if third_element_arrivees in key:
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
                                            textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                            for i, time in enumerate(arrivees_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                            (time, -1.07),
                                            textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
            
            for date in midnight_dates:
                ax.axvline(x=date, color='lightblue', linestyle='-', linewidth=1)
            
            plt.yticks([-1, 1], [f'{villes["ville_2"]}', f'{villes["ville_1"]}'], fontsize = 20)
            plt.xticks(dates_noon, [days_of_week[date.weekday()]  for date in dates], fontsize=20, ha='center', va='center')
            #ax.set_xlim(midnight_dates[0], dates_noon[-1])
            plt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True, colors='coral')
            for spine in ax.spines.values():
                spine.set_visible(False)

            plt.xlim(dates[0], dates[-2])

            title_color = 'navy'
            #plt.title(f"Graphicage {villes['ville_1']} - {villes['ville_2']}", y=1.1, color=title_color)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            st.image(buffer, use_column_width=True, caption='Graphicage Image')
            
            fig.set_size_inches(18, 10)
            plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.3)
            plt.savefig(f"Graphicage {villes['ville_1']} - {villes['ville_2']}.png", bbox_inches='tight')
            plt.close()

            filename = f"Graphicage {villes['ville_1']} - {villes['ville_2']}.png"  # Define the filename for the graph image
            image_bytes = buffer.getvalue()
            st.markdown(get_image_download_link(image_bytes, filename=filename), unsafe_allow_html=True)


        if num_villes == 3:
            fig, ax = plt.subplots(figsize=(20, 15))

            if list(departs_villes.values())[0] != '':
                ville_1_2 = list(departs_villes.keys())[0][2]
            else: 
                ville_1_2 = 'not a key'
            if list(departs_villes.values())[3] != '':
                ville_2_1 = list(departs_villes.keys())[3][2]
            else:
                ville_2_1 = 'not a key'
            if list(departs_villes.values())[1] != '':
                ville_1_3 = list(departs_villes.keys())[1][2]
            else:
                ville_1_3 = 'not a key'
            if list(departs_villes.values())[4] != '':
                ville_3_1 = list(departs_villes.keys())[4][2]
            else:
                ville_3_1 = 'not a key'
            if list(departs_villes.values())[2] != '':
                ville_2_3 = list(departs_villes.keys())[2][2]
            else:
                ville_2_3 = 'not a key'
            if list(departs_villes.values())[5] != '':
                ville_3_2 = list(departs_villes.keys())[5][2]
            else:
                ville_3_2 = 'not a key'

            # Afficher la première valeur des clés contenant cet élément
            for key, value in departs_villes.items():
                if ville_3_2 in key:
                    if value != '':
                        ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [0]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 0), colors[key[0]-1])
                    
                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1.02),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, 0.01),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)


                if ville_2_3 in key:
                    if value != '':
                        ax.scatter(departs_villes[key], [0]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 0), (arrivees_villes[key][i], -1), colors[key[0]-1])

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 0.02),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1.02),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)


                if ville_3_1 in key:
                    if value != '':
                        ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 1), colors[key[0]-1])
                    

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1.06),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, 1.07),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
            
                if ville_1_3 in key:
                    if value != '':
                        ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], -1), colors[key[0]-1])

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.04),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1.03),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

                if ville_2_1 in key:
                        if value != '':
                            ax.scatter(departs_villes[key], [0]*len(departs_villes[key]),  color=colors[key[0]-1])
                            #ax.plot([departs_villes[key], departs_villes[key]], [0, 1], linestyle='dotted', color='grey', alpha=0.5)
                            ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                            #ax.plot([arrivees_villes[key], arrivees_villes[key]], [0, 1], linestyle='dotted', color='grey', alpha=0.5)
                            for i in range(len(departs_villes[key])):
                                plot_arrow(ax, (departs_villes[key][i], 0), (arrivees_villes[key][i], 1), colors[key[0]-1])
                        

                            for i, time in enumerate(departs_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                            (time, -0.02),
                                    textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                            
                            for i, time in enumerate(arrivees_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                    (time, 1.06),
                                    textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

                if ville_1_2 in key:
                    if value != '':
                        ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [0]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], 0), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.03),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -0.03),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

                
            plt.xticks(dates_noon, [days_of_week[date.weekday()]  for date in dates], fontsize = 20, ha='center', va='center')
            ax.set_xlim(midnight_dates[0], dates_noon[-1])
            plt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True, colors = 'coral')
            #plt.title(f"Graphicage {villes['ville_1']} - {villes['ville_2']} - {villes['ville_3']}" , y=1.1)  # Déplacer le titre plus haut
            for spine in ax.spines.values():
                spine.set_visible(False)  # Désactiver les bords du graphique
            plt.yticks([-1, 0, 1], [f"{villes['ville_3']}", f"{villes['ville_2']}", f"{villes['ville_1']}"], fontsize=20)
            days_to_next_monday = (7 - start_date.weekday()) % 7  # Calculate days to the next Monday
            start_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
            dates = [start_date + timedelta(days=i) for i in range(8)]  # Générer jusqu'au jour 8 inclus
            for date in midnight_dates:
                ax.axvline(x=date, color='lightblue', linestyle='-', linewidth=1)  # Modifier la couleur et le style selon vos préférences
            plt.xlim(dates[0], dates[-2])
            title_color = 'navy'
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            st.image(buffer, use_column_width=True, caption='Graphicage Image')
            

            fig.set_size_inches(18*0.9, 10*0.9)
            plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.3)
            plt.savefig(f"Graphicage {villes['ville_1']} - {villes['ville_2']}.png", bbox_inches='tight')
            plt.close()

            filename = f"Graphicage {villes['ville_1']} - {villes['ville_2']} - {villes['ville_3']}.png"  # Define the filename for the graph image
            image_bytes = buffer.getvalue()
            st.markdown(get_image_download_link(image_bytes, filename=filename), unsafe_allow_html=True)





    

if __name__ == '__main__':
    get_days_of_service_all_buses()

